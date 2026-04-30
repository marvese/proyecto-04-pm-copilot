# Skill: Inicio de sesión

## Cuándo ejecutar
Al inicio de cada nueva sesión de Claude Code en este proyecto.

## Pasos obligatorios antes de escribir cualquier código

1. Lee estos ficheros en orden:
   - CLAUDE.md — contexto general del proyecto
   - docs/ARCHITECTURE.md — arquitectura hexagonal y decisiones técnicas
   - docs/PROMPTS.md — biblioteca de prompts utilizados
   - CHANGELOG.md — qué se ha hecho y en qué estado está cada cosa
   - scripts/jira_descriptions_complete.json — backlog completo con 
     estimaciones, prompts y story points

2. Verifica el estado del entorno:
   - docker ps → confirma que pmcopilot-postgres y pmcopilot-chroma 
     están healthy
   - Si no están levantados: make up && make db-init

3. Identifica la tarea activa:
   - Pregunta al usuario: "¿Con qué tarea de Jira continuamos?" 
     o lee el contexto si ya lo ha indicado
   - Localiza la tarea en jira_descriptions_complete.json
   - Lee los ficheros de prompt.context antes de empezar

4. Confirma contexto al usuario con un resumen de:
   - Último cambio registrado en CHANGELOG.md
   - Tarea que se va a abordar y su prompt.context
   - Estado del entorno (Docker OK / KO)

## Al finalizar cada tarea

1. Actualiza jira_descriptions_complete.json con los valores reales:
   - session_complexity.actual_tokens (si disponible)
   - session_complexity.actual_cost_usd (si disponible)  
   - session_complexity.actual_iterations

2. Ejecuta: git add . && git commit -m "feat/fix/docs: descripción breve"

3. Pregunta al usuario si quiere:
   - Actualizar Confluence: python3 scripts/confluence_client.py
   - Actualizar Jira con métricas reales: python3 scripts/update_jira.py

4. Actualizar los promts si se ha ejecutado algún prompt relevante:
   - Registra el prompt utilizado en docs/PROMPTS.md
