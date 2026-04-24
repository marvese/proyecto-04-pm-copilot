# ADR-004 — PWA React Primero, Flutter POC Después

**Estado**: Aceptado  
**Fecha**: 2026-04-24  
**Autor**: Marcos Vese  

---

## Contexto

PM Copilot necesita una interfaz de usuario accesible en desktop y mobile. Las opciones evaluadas son:

- **A) PWA con React** — una sola codebase web que funciona en browser y como app instalable en mobile
- **B) App nativa Flutter** — codebase multi-plataforma compilado a nativo (iOS/Android/Desktop)
- **C) App React Native** — codebase multi-plataforma con bridge nativo
- **D) Web responsive únicamente** — sin instalación ni capacidades offline

El proyecto está en fase de MVP con un solo desarrollador, timeline ajustado y necesidad de validar funcionalidades rápidamente antes de invertir en capacidades nativas.

---

## Decisión

**Fase 1 (MVP)**: PWA con React + TypeScript desplegada en Vercel.  
**Fase Futura (POC)**: Flutter como deuda técnica planificada, evaluable tras validar el producto.

---

## Razonamiento

### Por qué PWA primero

**1. Velocidad de desarrollo y reutilización de stack**  
El frontend React comparte tipos, convenciones y conocimiento de equipo con el resto del proyecto. No hay que aprender un nuevo lenguaje (Dart), framework (Flutter) ni gestionar builds nativos (Xcode, Android Studio, certificados).

**2. Deployment inmediato y sin fricción**  
Una PWA se despliega en Vercel con un `git push`. No requiere App Store review (días/semanas), certificados de distribución ni Enterprise Developer Account.

**3. Capacidades suficientes para el MVP**  
Las funcionalidades MVP (chat conversacional, dashboard, gestión de tareas) no requieren APIs nativas de dispositivo. Las PWA modernas ofrecen:
- Instalación en homescreen (Web App Manifest)
- Funcionamiento offline con Service Workers (para consultar el último estado cacheado)
- Push notifications (Web Push API)
- Acceso a cámara (para futuras features de escaneo de documentos)

**4. Menor complejidad operacional**  
Sin App Store, sin versiones binarias que gestionar, sin policy de actualizaciones. El usuario siempre accede a la versión más reciente.

**5. Audiencia objetivo**  
PMs y tech leads trabajan mayoritariamente en desktop. Una PWA instalable satisface el caso de uso mobile sin over-engineering.

### Por qué Flutter como POC posterior y no ahora

**1. Curva de aprendizaje de Dart**  
Flutter es un excelente framework, pero Dart es un lenguaje adicional que añade fricción cuando el foco debe estar en validar el producto.

**2. Capacidades nativas no requeridas en MVP**  
Las funcionalidades que justificarían Flutter (geolocalización, Bluetooth, acceso a filesystem, integraciones profundas de iOS/Android) no están en el MVP ni en el backlog próximo.

**3. Paralelismo de desarrollo innecesario**  
Mantener dos frontends en paralelo (React + Flutter) con un solo desarrollador duplicaría el esfuerzo sin añadir valor al usuario final.

**4. El momento adecuado para Flutter**  
Flutter tiene sentido cuando:
- El producto está validado y hay usuarios activos
- Se identifican funcionalidades que requieren APIs nativas
- El equipo crece para poder mantener dos codebases
- El tiempo de "time to market" de App Store deja de ser un bloqueador

---

## Plan de Migración a Flutter (Deuda Técnica Registrada)

**DT-002: Flutter POC**  
**Trigger**: cualquiera de estos eventos:
- > 50 usuarios activos mensuales en mobile
- Identificación de 3+ features que requieren APIs nativas (cámara, notificaciones push avanzadas, offline-first)
- Disponibilidad de un segundo desarrollador con experiencia Flutter/Dart

**Alcance del POC**:
- Reimplementar las 3 pantallas principales: chat, dashboard de tareas, vista de sprint
- Evaluar si las capacidades nativas aportan valor suficiente vs el coste de mantener dos codebases
- El backend REST/WebSocket no cambia — el cliente Flutter consume la misma API

**Tiempo estimado**: 2-3 semanas para el POC de evaluación.

---

## Capacidades PWA Implementadas

| Capacidad | Prioridad | Implementación |
|-----------|-----------|----------------|
| Instalable (homescreen) | P1 | Web App Manifest |
| Offline básico (last-known state) | P1 | Service Worker + Cache API |
| Push notifications | P2 | Web Push API + backend subscription |
| Sincronización en background | P2 | Background Sync API |
| Acceso a cámara (escanear docs) | P3 | MediaDevices API |

---

## Consecuencias

### Positivas
- Time to market mínimo para el frontend
- Un solo stack frontend que mantener
- Actualizaciones instantáneas sin App Store
- Despliegue automatizado y gratuito en Vercel

### Negativas / Trade-offs
- Experiencia de usuario ligeramente inferior a nativa en mobile (scroll physics, gestos nativos, integración con OS)
- Capacidades offline más limitadas que una app nativa
- Las notificaciones push en iOS tienen limitaciones hasta iOS 16.4+
- Si el producto escala mobile-first, habrá que invertir en Flutter igualmente — solo se está posponiendo la decisión

### Premisa que invalidaría esta decisión
Si los tests de usuario revelan que > 60% del uso es en mobile y los usuarios reportan friction significativa vs apps nativas, reconsiderar Flutter en v2.0.
