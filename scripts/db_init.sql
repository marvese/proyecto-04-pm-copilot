-- =============================================================
-- PM Copilot — DDL completo
-- Ejecutar con: make db-init
-- Compatible con PostgreSQL 16+ (gen_random_uuid() nativo)
-- =============================================================

-- Extensiones
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- búsqueda full-text en title/description

-- =============================================================
-- ENUMS como dominios (CHECK más portables que CREATE TYPE)
-- =============================================================

-- Usamos VARCHAR + CHECK para evitar migraciones cuando se añaden valores
-- (CREATE TYPE requiere ALTER TYPE para añadir nuevos valores)

-- =============================================================
-- projects
-- =============================================================
CREATE TABLE IF NOT EXISTS projects (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name                 TEXT        NOT NULL,
    description          TEXT,
    jira_project_key     VARCHAR(32),
    confluence_space_key VARCHAR(32),
    github_repo          TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT projects_name_not_empty CHECK (trim(name) <> '')
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_projects_name
    ON projects (name);

CREATE INDEX IF NOT EXISTS idx_projects_jira_key
    ON projects (jira_project_key)
    WHERE jira_project_key IS NOT NULL;

-- =============================================================
-- sprints
-- =============================================================
CREATE TABLE IF NOT EXISTS sprints (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id       UUID        NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    name             TEXT        NOT NULL,
    goal             TEXT,
    status           VARCHAR(16) NOT NULL DEFAULT 'planned'
                         CHECK (status IN ('planned', 'active', 'completed')),
    capacity_points  INT         CHECK (capacity_points IS NULL OR capacity_points > 0),
    start_date       TIMESTAMPTZ,
    end_date         TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT sprints_dates_order CHECK (
        start_date IS NULL OR end_date IS NULL OR start_date <= end_date
    )
);

CREATE INDEX IF NOT EXISTS idx_sprints_project_id
    ON sprints (project_id);

CREATE INDEX IF NOT EXISTS idx_sprints_status
    ON sprints (status);

-- Solo puede haber un sprint activo por proyecto
CREATE UNIQUE INDEX IF NOT EXISTS uq_sprints_one_active_per_project
    ON sprints (project_id)
    WHERE status = 'active';

-- =============================================================
-- tasks
-- =============================================================
CREATE TABLE IF NOT EXISTS tasks (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id        UUID        NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    sprint_id         UUID        REFERENCES sprints (id) ON DELETE SET NULL,
    title             TEXT        NOT NULL,
    description       TEXT,
    type              VARCHAR(16) NOT NULL DEFAULT 'task'
                          CHECK (type IN ('story', 'bug', 'task', 'epic')),
    status            VARCHAR(16) NOT NULL DEFAULT 'backlog'
                          CHECK (status IN ('backlog', 'todo', 'in_progress', 'in_review', 'done')),
    priority          VARCHAR(16) NOT NULL DEFAULT 'medium'
                          CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    estimated_points  INT         CHECK (estimated_points IN (1, 2, 3, 5, 8, 13, 21)),
    actual_points     INT         CHECK (actual_points IS NULL OR actual_points > 0),
    assignee_id       UUID,
    jira_key          VARCHAR(32),
    jira_sync_status  VARCHAR(16) NOT NULL DEFAULT 'local_only'
                          CHECK (jira_sync_status IN ('pending', 'synced', 'failed', 'local_only')),
    tags              TEXT[]      NOT NULL DEFAULT '{}',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT tasks_title_not_empty CHECK (trim(title) <> '')
);

CREATE INDEX IF NOT EXISTS idx_tasks_project_id
    ON tasks (project_id);

CREATE INDEX IF NOT EXISTS idx_tasks_sprint_id
    ON tasks (sprint_id)
    WHERE sprint_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tasks_status
    ON tasks (project_id, status);

CREATE INDEX IF NOT EXISTS idx_tasks_jira_key
    ON tasks (jira_key)
    WHERE jira_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tasks_jira_sync_status
    ON tasks (project_id, jira_sync_status)
    WHERE jira_sync_status = 'pending';

-- Búsqueda de texto en título y descripción
CREATE INDEX IF NOT EXISTS idx_tasks_title_trgm
    ON tasks USING GIN (title gin_trgm_ops);

-- =============================================================
-- estimations
-- =============================================================
CREATE TABLE IF NOT EXISTS estimations (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id      UUID        NOT NULL REFERENCES tasks (id) ON DELETE CASCADE,
    points       INT         NOT NULL CHECK (points IN (1, 2, 3, 5, 8, 13, 21)),
    confidence   FLOAT       NOT NULL DEFAULT 0.0
                     CHECK (confidence >= 0.0 AND confidence <= 1.0),
    reasoning    TEXT,
    model_used   VARCHAR(64),
    breakdown    JSONB,       -- {"frontend": 2, "backend": 2, "testing": 1}
    similar_tasks JSONB,      -- [{id, title, estimated, actual}]
    risks        JSONB,       -- ["riesgo 1", "riesgo 2"]
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_estimations_task_id
    ON estimations (task_id);

-- La estimación más reciente por tarea (útil para queries de "última estimación")
CREATE INDEX IF NOT EXISTS idx_estimations_task_latest
    ON estimations (task_id, created_at DESC);

-- =============================================================
-- knowledge_chunks
-- =============================================================
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id   UUID        REFERENCES projects (id) ON DELETE CASCADE,
    source       VARCHAR(32) NOT NULL
                     CHECK (source IN ('confluence', 'jira', 'github', 'conversation')),
    document_id  TEXT        NOT NULL,
    section      TEXT,
    content      TEXT        NOT NULL,
    embedding_id TEXT,                 -- ID del vector en ChromaDB
    url          TEXT,
    metadata     JSONB       NOT NULL DEFAULT '{}',
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT knowledge_chunks_content_not_empty CHECK (trim(content) <> '')
);

CREATE INDEX IF NOT EXISTS idx_knowledge_project_id
    ON knowledge_chunks (project_id)
    WHERE project_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_knowledge_source
    ON knowledge_chunks (source);

-- Deduplicación: un documento+sección no se indexa dos veces
CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_document_section
    ON knowledge_chunks (project_id, document_id, COALESCE(section, ''))
    WHERE project_id IS NOT NULL;

-- Búsqueda full-text en contenido
CREATE INDEX IF NOT EXISTS idx_knowledge_content_trgm
    ON knowledge_chunks USING GIN (content gin_trgm_ops);

-- =============================================================
-- chat_sessions  (necesario para el módulo de chat con historial)
-- =============================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID        NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_project_id
    ON chat_sessions (project_id);

-- =============================================================
-- chat_messages
-- =============================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID        NOT NULL REFERENCES chat_sessions (id) ON DELETE CASCADE,
    role       VARCHAR(16) NOT NULL CHECK (role IN ('user', 'assistant')),
    content    TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id
    ON chat_messages (session_id, created_at);

-- =============================================================
-- Función trigger: updated_at automático
-- =============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
