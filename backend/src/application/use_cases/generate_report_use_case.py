from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from ...domain.entities.project import Sprint
from ...domain.entities.report import Report, ReportType
from ...domain.entities.task import Task, TaskPriority, TaskStatus
from ...domain.ports.llm_port import LLMPort, LLMRequest, LLMTaskType
from ...domain.ports.project_repository_port import ProjectRepositoryPort
from ...domain.ports.sprint_repository_port import SprintRepositoryPort
from ...domain.ports.task_repository_port import TaskRepositoryPort
from ..commands.generate_report_command import GenerateReportCommand

_SYSTEM = (
    "Eres un asistente experto en gestión de proyectos de software. "
    "Genera informes profesionales, concisos y orientados a datos en Markdown."
)


class GenerateReportUseCase:
    def __init__(
        self,
        llm_port: LLMPort,
        task_repo: TaskRepositoryPort,
        sprint_repo: SprintRepositoryPort,
        project_repo: ProjectRepositoryPort,
    ) -> None:
        self._llm = llm_port
        self._task_repo = task_repo
        self._sprint_repo = sprint_repo
        self._project_repo = project_repo

    async def execute(self, command: GenerateReportCommand) -> Report:
        project = await self._project_repo.get_by_id(command.project_id)
        project_name = project.name if project else str(command.project_id)

        sprint: Optional[Sprint] = None
        if command.sprint_id:
            sprint = await self._sprint_repo.get_by_id(command.sprint_id)
        else:
            sprint = await self._sprint_repo.get_active(command.project_id)

        tasks = await self._task_repo.list_by_project(command.project_id)

        if command.type == ReportType.SPRINT_STATUS:
            prompt = self._sprint_prompt(project_name, sprint, tasks)
            title = f"Sprint Summary — {sprint.name if sprint else 'Sin sprint activo'}"
        elif command.type == ReportType.PROJECT_STATUS:
            prompt = self._project_status_prompt(project_name, sprint, tasks)
            title = f"Estado del Proyecto — {project_name}"
        else:
            prompt = self._meeting_notes_prompt(project_name, command.raw_input or "")
            title = f"Notas de Reunión — {project_name}"

        try:
            response = await self._llm.complete(
                LLMRequest(
                    prompt=prompt,
                    task_type=LLMTaskType.GENERATION_LONG,
                    system=_SYSTEM,
                    max_tokens=2048,
                    temperature=0.4,
                )
            )
            content = response.content
        except Exception:
            content = self._static_fallback(command.type, project_name, sprint, tasks, command.raw_input)

        return Report(
            id=uuid.uuid4(),
            project_id=command.project_id,
            type=command.type,
            title=title,
            content=content,
            sprint_id=sprint.id if sprint else None,
        )

    # ── Prompt builders ───────────────────────────────────────────────────────

    def _sprint_prompt(self, project_name: str, sprint: Optional[Sprint], tasks: list[Task]) -> str:
        done = [t for t in tasks if t.status == TaskStatus.DONE]
        in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        blocked = [
            t for t in tasks
            if t.status == TaskStatus.IN_REVIEW
            and t.priority in (TaskPriority.HIGH, TaskPriority.CRITICAL)
        ]
        completed_pts = sum(t.actual_points or t.estimated_points or 0 for t in done)

        return f"""Genera un informe de sprint profesional en Markdown para el proyecto "{project_name}".

Sprint: {sprint.name if sprint else "Sin sprint activo"}
Tareas completadas: {len(done)} ({completed_pts} puntos)
Tareas en progreso: {len(in_progress)}
Posibles bloqueadores: {len(blocked)}
Total de tareas: {len(tasks)}
Tareas completadas: {', '.join(t.title for t in done[:5])}{'...' if len(done) > 5 else ''}

El informe DEBE incluir exactamente estas secciones en Markdown:
## Resumen Ejecutivo
## Métricas del Sprint
## Logros
## Bloqueadores y Riesgos
## Próximos Pasos

Sé conciso y profesional. Usa los datos reales proporcionados."""

    def _project_status_prompt(self, project_name: str, sprint: Optional[Sprint], tasks: list[Task]) -> str:
        done = [t for t in tasks if t.status == TaskStatus.DONE]
        total = len(tasks)
        pct = int(len(done) / total * 100) if total > 0 else 0
        remaining_pts = sum(t.estimated_points or 0 for t in tasks if t.status != TaskStatus.DONE)
        done_pts = sum(t.actual_points or t.estimated_points or 0 for t in done)

        return f"""Genera un informe de estado del proyecto en Markdown para "{project_name}".

Sprint activo: {sprint.name if sprint else "Ninguno"}
Tareas completadas: {len(done)}/{total} ({pct}%)
Puntos completados: {done_pts}
Puntos pendientes: {remaining_pts}

El informe DEBE incluir exactamente estas secciones en Markdown:
## Estado General
## Métricas de Velocidad
## Distribución de Tareas
## Riesgos Identificados
## Recomendaciones

Sé conciso y basado en los datos proporcionados."""

    def _meeting_notes_prompt(self, project_name: str, raw_notes: str) -> str:
        return f"""Transcribe y estructura las siguientes notas de reunión del proyecto "{project_name}" en Markdown profesional.

Notas originales:
---
{raw_notes}
---

El informe estructurado DEBE incluir exactamente estas secciones en Markdown:
## Resumen de la Reunión
## Puntos Tratados
## Decisiones Tomadas
## Acciones y Responsables
## Próxima Reunión

Mantén fidelidad al contenido original. Sé conciso."""

    # ── Static fallback ───────────────────────────────────────────────────────

    def _static_fallback(
        self,
        report_type: ReportType,
        project_name: str,
        sprint: Optional[Sprint],
        tasks: list[Task],
        raw_notes: Optional[str],
    ) -> str:
        date = datetime.utcnow().strftime("%Y-%m-%d")
        done = [t for t in tasks if t.status == TaskStatus.DONE]
        total = len(tasks)

        if report_type == ReportType.SPRINT_STATUS:
            completed_pts = sum(t.actual_points or t.estimated_points or 0 for t in done)
            done_list = "\n".join(f"- {t.title}" for t in done[:10]) or "- Sin tareas completadas"
            return (
                f"# Informe de Sprint — {project_name}\n"
                f"*Generado el {date}*\n\n"
                f"## Resumen Ejecutivo\nInforme automático del sprint activo.\n\n"
                f"## Métricas del Sprint\n"
                f"- **Sprint**: {sprint.name if sprint else 'N/A'}\n"
                f"- **Tareas completadas**: {len(done)}/{total}\n"
                f"- **Puntos completados**: {completed_pts}\n\n"
                f"## Logros\n{done_list}\n\n"
                f"## Bloqueadores y Riesgos\n*Revisar manualmente*\n\n"
                f"## Próximos Pasos\n*Definir en la próxima retrospectiva*\n"
            )

        if report_type == ReportType.PROJECT_STATUS:
            pct = int(len(done) / total * 100) if total > 0 else 0
            return (
                f"# Estado del Proyecto — {project_name}\n"
                f"*Generado el {date}*\n\n"
                f"## Estado General\nSprint activo: {sprint.name if sprint else 'Ninguno'}\n\n"
                f"## Métricas de Velocidad\n"
                f"- Tareas completadas: {len(done)}/{total}\n"
                f"- Progreso: {pct}%\n\n"
                f"## Distribución de Tareas\n*Ver tablero del proyecto*\n\n"
                f"## Riesgos Identificados\n*Revisar manualmente*\n\n"
                f"## Recomendaciones\n*Basarse en métricas actualizadas*\n"
            )

        # MEETING_NOTES
        summary = (raw_notes[:300] + "...") if raw_notes and len(raw_notes) > 300 else (raw_notes or "Sin notas")
        return (
            f"# Notas de Reunión — {project_name}\n"
            f"*Generado el {date}*\n\n"
            f"## Resumen de la Reunión\n{summary}\n\n"
            f"## Puntos Tratados\n*Transcribir manualmente*\n\n"
            f"## Decisiones Tomadas\n*Documentar*\n\n"
            f"## Acciones y Responsables\n*Asignar*\n\n"
            f"## Próxima Reunión\n*Pendiente*\n"
        )
