from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class UpdateTaskCommand:
    task_id: uuid.UUID
    updates: dict[str, Any]
