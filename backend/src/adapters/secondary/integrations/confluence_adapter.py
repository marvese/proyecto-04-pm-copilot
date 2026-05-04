from __future__ import annotations

import re
from typing import Any, Optional

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ....domain.ports.confluence_port import ConfluencePort


# ---------------------------------------------------------------------------
# Markdown → Confluence Storage Format (extracted from scripts/confluence_client.py)
# ---------------------------------------------------------------------------

def _escape_cdata(text: str) -> str:
    return text.replace("]]>", "]]]]><![CDATA[>")


def _inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*\n]+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_storage(md: str) -> str:
    """Convert Markdown to Confluence Storage Format (XHTML)."""
    result: list[str] = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    in_table = False
    table_rows: list[str] = []
    list_items: list[str] = []

    def flush_list() -> None:
        if list_items:
            inner = "\n".join(f"<li>{item}</li>" for item in list_items)
            result.append(f"<ul>\n{inner}\n</ul>")
            list_items.clear()

    def flush_table() -> None:
        nonlocal in_table
        if not table_rows:
            return
        parts = ["<table><tbody>"]
        header_done = False
        for row in table_rows:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if all(re.match(r"^[-: ]+$", c) for c in cells if c):
                continue
            tag = "th" if not header_done else "td"
            parts.append(
                "<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>"
            )
            header_done = True
        parts.append("</tbody></table>")
        result.append("".join(parts))
        table_rows.clear()
        in_table = False

    for line in md.splitlines():
        if line.startswith("```"):
            if in_code:
                content = _escape_cdata("\n".join(code_lines))
                lang_attr = (
                    f'<ac:parameter ac:name="language">{code_lang}</ac:parameter>'
                    if code_lang else ""
                )
                result.append(
                    f'<ac:structured-macro ac:name="code" ac:schema-version="1">'
                    f"{lang_attr}"
                    f"<ac:plain-text-body><![CDATA[{content}]]></ac:plain-text-body>"
                    f"</ac:structured-macro>"
                )
                in_code = False
                code_lang = ""
                code_lines.clear()
            else:
                flush_list()
                flush_table()
                in_code = True
                code_lang = line[3:].strip()
            continue

        if in_code:
            code_lines.append(line)
            continue

        if line.strip().startswith("|") and "|" in line:
            flush_list()
            in_table = True
            table_rows.append(line)
            continue
        if in_table:
            flush_table()

        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            flush_list()
            lvl = len(m.group(1))
            result.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            continue

        if re.match(r"^[-*_]{3,}\s*$", line):
            flush_list()
            result.append("<hr/>")
            continue

        m = re.match(r"^[-*]\s+(.*)", line)
        if m:
            list_items.append(_inline(m.group(1)))
            continue

        if not line.strip():
            flush_list()
            result.append("")
            continue

        result.append(f"<p>{_inline(line)}</p>")

    flush_list()
    flush_table()
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

def _confluence_retry(fn):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    )(fn)


class ConfluenceAdapter(ConfluencePort):
    """Implements ConfluencePort using the Confluence REST API v1 (Cloud)."""

    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._auth = (email, api_token)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=f"{self._base_url}/wiki/rest/api/",
            auth=self._auth,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=30.0,
        )

    @_confluence_retry
    async def get_page(self, page_id: str) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.get(
                f"content/{page_id}",
                params={"expand": "body.storage,version"},
            )
            resp.raise_for_status()
            return resp.json()

    @_confluence_retry
    async def create_page(
        self,
        space_key: str,
        title: str,
        content: str,
        parent_id: Optional[str] = None,
    ) -> str:
        body: dict[str, Any] = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {"storage": {"value": content, "representation": "storage"}},
        }
        if parent_id:
            body["ancestors"] = [{"id": parent_id}]
        async with self._client() as client:
            resp = await client.post("content", json=body)
            resp.raise_for_status()
            return resp.json()["id"]

    @_confluence_retry
    async def update_page(
        self, page_id: str, title: str, content: str, version: int
    ) -> None:
        body = {
            "type": "page",
            "title": title,
            "version": {"number": version + 1},
            "body": {"storage": {"value": content, "representation": "storage"}},
        }
        async with self._client() as client:
            resp = await client.put(f"content/{page_id}", json=body)
            resp.raise_for_status()

    @_confluence_retry
    async def list_pages(
        self, space_key: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get(
                "content",
                params={"spaceKey": space_key, "type": "page", "limit": limit},
            )
            resp.raise_for_status()
            return resp.json().get("results", [])

    @_confluence_retry
    async def get_page_content(self, page_id: str) -> str:
        async with self._client() as client:
            resp = await client.get(
                f"content/{page_id}",
                params={"expand": "body.storage"},
            )
            resp.raise_for_status()
            return resp.json()["body"]["storage"]["value"]

    async def health_check(self) -> bool:
        try:
            async with self._client() as client:
                resp = await client.get("space", params={"limit": 1}, timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False
