---
title: "Changelog — PM Copilot"
parent: "00. PM Copilot — Inicio"
---
# Changelog

Todos los cambios notables de este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [Unreleased]

### Added
- **PMCP-26**: Dominio de tareas completo — `CreateTaskUseCase`, `UpdateTaskUseCase`, `UpdateTaskCommand` en `application/commands/`, `tasks_router` con 6 endpoints y DI completa (`GET/POST/GET/{id}/PATCH/DELETE/{id}` + `POST /{id}/sync-jira` con BackgroundTasks, 503 si Jira no configurado, 422 si sin `jira_project_key`); Container con `create_task_use_case`, `update_task_use_case`, `sync_jira_use_case`; repo properties devuelven puertos abstractos; 27 tests nuevos. Suite: 246 passed.

### Fixed
- **PMCP-50**: Alineación de contrato de reportes — `ReportResponse` añade `confluence_page_id` (mapeado desde la entidad `Report`); `reportService.ts`: añade `sprint_id`, elimina `format` de las requests, corrige `downloadUrl()` (era `/download/{format}`, ahora `/download`).
- **PMCP-26 code review**: bug `jira=` → `jira_port=` en `SyncJiraUseCase` (TypeError en runtime); `datetime.utcnow()` → `datetime.now(tz=timezone.utc)`; `UpdateTaskCommand` movido a `application/commands/`.
