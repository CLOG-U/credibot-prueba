# CrediBot v2 — Plan completo de desarrollo

**Repositorio:** CLOG-U/credibot-prueba  
**Rama de trabajo:** main  
**Fecha:** 12 de julio de 2026  
**Duración recomendada:** 8 semanas  
**Metodología:** 4 sprints de 2 semanas  
**Documento fuente:** contexto aplicacion/creditbot_requisitos_y_arquitectura_v2.md  
**Estado:** Listo para planificación del equipo

---

## 1. Objetivo

Evolucionar CrediBot v1 hacia un MVP v2 de precalificación de crédito por WhatsApp que combine:

- Máquina de estados determinista.
- Conversación natural con GPT.
- Tools conectadas a Supabase.
- RAG sobre políticas y preguntas frecuentes.
- Perfiles crediticios ficticios con cédula, score, historial y deuda.
- Reglas de elegibilidad y cálculo independientes del LLM.
- Derivación permanente a un asesor.
- Panel administrativo y auditoría.
- Redis para la sesión activa.
- Meta WhatsApp Cloud API como canal principal.
- Docker, GitHub Actions y Google Cloud Run.

La versión final debe ser una demostración académica realista, no un sistema financiero de producción. No se usarán datos personales reales.

---

## 2. Resultado esperado

Al terminar el plan, un usuario podrá:

1. Iniciar una conversación por WhatsApp o el simulador.
2. Recibir el aviso de precalificación y privacidad.
3. Otorgar consentimiento.
4. Ingresar una cédula ecuatoriana ficticia.
5. Ser validado contra un perfil ficticio de Supabase.
6. Consultar políticas mediante RAG.
7. Entregar ingreso, empleo, gastos, plazo y destino.
8. Recibir una precalificación calculada por reglas deterministas.
9. Solicitar o recibir derivación a un asesor.
10. Dejar trazabilidad de mensajes, tools, decisiones y resultados.
11. Ser visible en el dashboard administrativo.

---

## 3. Alcance

### 3.1 Incluido en el MVP

- Flujo híbrido: estados + GPT + tools + RAG.
- Validación de cédula ecuatoriana con módulo 10.
- Perfiles ficticios con score 1–999, mora, deuda e historial.
- Elegibilidad y monto máximo por reglas deterministas.
- Consentimiento y aviso de precalificación.
- Auditoría de cada tool.
- RAG de políticas, tasas, requisitos, plazos y FAQs.
- Simulador local.
- Meta WhatsApp Cloud API.
- Twilio como respaldo.
- Idempotencia del webhook.
- Redis con recuperación desde Supabase.
- Dashboard ampliado y protegido.
- Docker, GitHub Actions y Cloud Run.
- Logs estructurados y métricas.
- Pruebas unitarias, integración y end-to-end.
- Backlog, sprints, diagramas, retrospectivas y demo.

### 3.2 Fuera del MVP

- Buró de crédito real.
- Cédulas reales.
- Aprobación o desembolso de dinero.
- Firma electrónica.
- OCR, selfie o KYC biométrico.
- Aplicación móvil.
- Fine-tuning.
- Despliegue multicloud.
- Autonomía del LLM para cambiar estados o reglas.

### 3.3 Recortes permitidos por falta de tiempo

1. Redis solo para estado y contador de fallos.
2. RAG con OpenAI SDK y pgvector, sin LangChain.
3. Dashboard limitado a solicitudes, handoff y auditoría.
4. Twilio como canal de demo si Meta se retrasa.
5. Plantillas Meta documentadas si su aprobación externa no llega a tiempo.

No se pueden recortar: reglas deterministas, tools, RAG, auditoría, consentimiento, pruebas, CI/CD y entregables académicos.

---

## 4. Principios técnicos

1. GPT conversa, pero no decide elegibilidad ni montos.
2. Toda decisión crediticia sale de domain/credit_rules.py.
3. Toda cifra presentada al usuario debe provenir de una tool.
4. Supabase es la fuente de verdad.
5. Redis es una capa de sesión recuperable.
6. El webhook debe ser idempotente.
7. Toda consulta de perfil deja auditoría.
8. La opción de asesor está disponible en cualquier estado.
9. Ningún secreto se guarda en Git.
10. Cada historia incluye pruebas y documentación.
11. Todos los perfiles y cédulas son ficticios.
12. El sistema siempre indica que es una precalificación.

---

## 5. Arquitectura objetivo

~~~mermaid
flowchart LR
    U[Usuario] --> W[Meta WhatsApp o simulador]
    W --> API[FastAPI]
    API --> IDEM[Idempotencia]
    IDEM --> SM[State Manager]
    SM <--> REDIS[Redis]
    SM <--> DB[(Supabase)]
    SM --> AG[Agente GPT]
    AG --> TOOLS[Tool Registry]
    TOOLS --> RULES[Reglas crediticias]
    TOOLS --> DB
    TOOLS --> RAG[RAG Retriever]
    RAG --> VEC[(pgvector)]
    SM --> HO[Handoff]
    DB --> DASH[Streamlit]
    API --> LOG[Logs y métricas]
~~~

| Componente | Responsabilidad |
|---|---|
| State Manager | Autorizar transiciones y determinar el dato requerido |
| Agente GPT | Comprender intención, redactar e invocar tools permitidas |
| Tool Registry | Validar argumentos y ejecutar acciones auditables |
| Credit Rules | Calcular elegibilidad, monto, tasa, cuota y resultado |
| RAG Retriever | Recuperar fragmentos y fuentes de las políticas |
| Supabase | Persistencia principal |
| Redis | Sesión, fallos y contexto corto |
| WhatsApp Provider | Normalizar Meta y Twilio |
| Dashboard | Supervisión administrativa |
| CI/CD | Probar, construir y desplegar |

---

## 6. Organización del equipo

Asignar nombres antes del Sprint 1.

| Rol | Responsabilidades |
|---|---|
| Product Owner | Prioridad, criterios y aceptación |
| Scrum Master | Ceremonias, riesgos y evidencia |
| Backend/Domain | Esquema, repositorios, estados, reglas y tools |
| AI/RAG | Prompts, orquestador, recuperación y evaluación |
| Cloud/WhatsApp | Meta, Redis, Docker, Actions y Cloud Run |
| Dashboard/QA | Streamlit, pruebas, documentación y demo |

Una persona puede cubrir varios roles, pero cada historia tendrá un responsable único.

### Ceremonias

- Planning al inicio de cada sprint.
- Daily de 10–15 minutos.
- Refinamiento a mitad de sprint.
- Review con demostración.
- Retrospectiva con acciones medibles.
- Evidencia en docs/sprints/sprint-N.md.

---

## 7. Cronograma

### Preparación — 2 a 3 días

- Confirmar responsables.
- Validar reglas, tasas y categorías.
- Crear GitHub Project.
- Cargar el backlog.
- Crear ADR de arquitectura.
- Acordar Definition of Ready y Definition of Done.
- Configurar secretos y ambientes.

### Sprint 1 — Semanas 1 y 2: datos, dominio y flujo

Entregables:

- Migraciones v2.
- Seed de 20–50 perfiles ficticios.
- Validador de cédula.
- Reglas de elegibilidad, monto y cuota.
- Estados v2 y consentimiento.
- Auditoría e idempotencia base.
- Pruebas del dominio.

Criterio de salida: el simulador completa el flujo v2 sin GPT.

### Sprint 2 — Semanas 3 y 4: tools, GPT y RAG

Entregables:

- Contratos y registro de tools.
- Orquestador GPT.
- Guardrails y control de costo.
- Documentos e índice RAG.
- Evaluaciones de tools y RAG.
- Fallback determinista.

Criterio de salida: el simulador usa tools reales, responde con fuentes y no inventa score o monto.

### Sprint 3 — Semanas 5 y 6: WhatsApp, Redis, dashboard y seguridad

Entregables:

- Interfaz de proveedor WhatsApp.
- Meta Cloud API y respaldo Twilio.
- Redis y recuperación desde Supabase.
- Idempotencia completa.
- Dashboard v2.
- Autenticación administrativa.
- Enmascaramiento y logs.

Criterio de salida: una conversación de staging funciona por WhatsApp y aparece en el dashboard.

### Sprint 4 — Semanas 7 y 8: DevOps, calidad y presentación

Entregables:

- Dockerfile.
- GitHub Actions.
- Cloud Run.
- Pruebas integradas y de rendimiento.
- Diagramas y documentación.
- Runbook y rollback.
- Guion y ensayo de demo.
- Retrospectiva final.

Criterio de salida: un commit aprobado pasa CI, se despliega y permite demostrar el recorrido completo.

---

## 8. Backlog ejecutable

Escala de esfuerzo: 1, 2, 3, 5 y 8 puntos.  
Prioridad: P0 obligatorio, P1 importante, P2 mejora.

### EPIC-00 — Gobierno y estabilización

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| GOV-01 | Aprobar requisitos y reglas crediticias | P0 | 2 |
| GOV-02 | Asignar roles y responsables | P0 | 1 |
| GOV-03 | Crear GitHub Project y cargar backlog | P0 | 3 |
| GOV-04 | Corregir documentación desactualizada de v1 | P1 | 2 |
| GOV-05 | Registrar decisiones en docs/adr | P0 | 3 |
| GOV-06 | Definir convenciones de commits y revisión | P0 | 1 |
| GOV-07 | Fijar versiones de Python y dependencias | P1 | 2 |
| GOV-08 | Mantener una línea base de tests | P0 | 2 |

### EPIC-01 — Datos y migraciones

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| DATA-01 | Crear migraciones SQL versionadas | P0 | 3 |
| DATA-02 | Ampliar users con cédula y consentimiento | P0 | 3 |
| DATA-03 | Crear credit_profiles | P0 | 3 |
| DATA-04 | Crear credit_history | P0 | 3 |
| DATA-05 | Ampliar credit_requests con campos v2 | P0 | 5 |
| DATA-06 | Crear tool_audit_logs | P0 | 3 |
| DATA-07 | Crear inbound_events con ID único | P0 | 3 |
| DATA-08 | Crear rag_documents y rag_chunks con pgvector | P0 | 5 |
| DATA-09 | Añadir índices y restricciones | P0 | 3 |
| DATA-10 | Crear seed idempotente de 20–50 perfiles | P0 | 5 |
| DATA-11 | Documentar migración y rollback | P0 | 2 |
| DATA-12 | Revisar RLS y service role | P1 | 3 |

### EPIC-02 — Dominio crediticio

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| DOM-01 | Implementar módulo 10 de cédula | P0 | 3 |
| DOM-02 | Categorizar score 1–999 | P0 | 2 |
| DOM-03 | Implementar mora, lista negra y sin historial | P0 | 3 |
| DOM-04 | Calcular capacidad considerando deuda y gastos | P0 | 5 |
| DOM-05 | Calcular cuota con sistema francés | P0 | 3 |
| DOM-06 | Calcular monto máximo por categoría | P0 | 5 |
| DOM-07 | Calcular preaprobado, observado y no_cumple | P0 | 3 |
| DOM-08 | Crear tabla de decisión y casos límite | P0 | 5 |
| DOM-09 | Versionar y documentar reglas ficticias | P0 | 2 |

### EPIC-03 — Flujo y estado

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| FLOW-01 | Definir estados y transiciones v2 | P0 | 3 |
| FLOW-02 | Añadir consentimiento antes de cédula | P0 | 3 |
| FLOW-03 | Añadir verificación de cédula e identidad | P0 | 5 |
| FLOW-04 | Evaluar elegibilidad antes del monto | P0 | 5 |
| FLOW-05 | Recopilar empleo, gastos, plazo y destino | P0 | 5 |
| FLOW-06 | Mantener asesor disponible en todo estado | P0 | 3 |
| FLOW-07 | Persistir fallos de validación | P0 | 3 |
| FLOW-08 | Recuperar conversación después de reinicio | P0 | 5 |
| FLOW-09 | Probar aislamiento entre usuarios | P0 | 3 |

### EPIC-04 — Tools y auditoría

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| TOOL-01 | Definir contrato y errores comunes | P0 | 3 |
| TOOL-02 | Crear validar_cedula | P0 | 2 |
| TOOL-03 | Crear consultar_perfil_crediticio | P0 | 3 |
| TOOL-04 | Crear verificar_identidad | P0 | 3 |
| TOOL-05 | Crear calcular_monto_maximo | P0 | 5 |
| TOOL-06 | Adaptar registrar_solicitud y registrar_mensaje | P0 | 3 |
| TOOL-07 | Adaptar derivar_a_asesor | P0 | 2 |
| TOOL-08 | Crear obtener_politica_credito | P0 | 3 |
| TOOL-09 | Auditar argumentos enmascarados, resultado y latencia | P0 | 5 |
| TOOL-10 | Limitar tools permitidas según estado | P0 | 3 |
| TOOL-11 | Crear pruebas por tool | P0 | 5 |

### EPIC-05 — Agente GPT

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| AI-01 | Crear abstracción de proveedor LLM | P0 | 3 |
| AI-02 | Definir prompt y reglas de no invención | P0 | 3 |
| AI-03 | Construir contexto mínimo por estado | P0 | 5 |
| AI-04 | Implementar tool calling limitado | P0 | 8 |
| AI-05 | Validar salidas estructuradas | P0 | 5 |
| AI-06 | Rechazar montos/scores ajenos a tools | P0 | 5 |
| AI-07 | Responder dudas y regresar al estado | P0 | 5 |
| AI-08 | Añadir timeout y reintentos controlados | P1 | 3 |
| AI-09 | Crear fallback determinista | P0 | 5 |
| AI-10 | Limitar tokens y costo | P0 | 3 |
| AI-11 | Probar con proveedor LLM simulado | P0 | 5 |

### EPIC-06 — RAG

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| RAG-01 | Redactar políticas ficticias de 3–5 páginas | P0 | 5 |
| RAG-02 | Crear FAQs, glosario y catálogo | P0 | 3 |
| RAG-03 | Crear carga, chunking y embeddings | P0 | 5 |
| RAG-04 | Implementar búsqueda con metadata y umbral | P0 | 5 |
| RAG-05 | Devolver fuente con cada resultado | P0 | 3 |
| RAG-06 | Rechazar respuesta sin evidencia | P0 | 3 |
| RAG-07 | Crear 20–30 preguntas de evaluación | P0 | 5 |
| RAG-08 | Medir recuperación y ausencia de invención | P0 | 5 |
| RAG-09 | Cachear consultas frecuentes si es necesario | P2 | 3 |

### EPIC-07 — Redis y sesión

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| SES-01 | Crear interfaz SessionStore | P0 | 3 |
| SES-02 | Implementar Redis con TTL | P0 | 5 |
| SES-03 | Guardar estado, IDs, fallos y contexto | P0 | 3 |
| SES-04 | Sincronizar transiciones con Supabase | P0 | 5 |
| SES-05 | Recuperar ante cache miss | P0 | 5 |
| SES-06 | Continuar si Redis falla | P1 | 5 |
| SES-07 | Probar concurrencia y expiración | P0 | 5 |

### EPIC-08 — WhatsApp

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| WA-01 | Crear interfaz WhatsAppProvider | P0 | 3 |
| WA-02 | Adaptar Twilio a la interfaz | P1 | 3 |
| WA-03 | Implementar verificación GET de Meta | P0 | 3 |
| WA-04 | Normalizar webhook Meta | P0 | 5 |
| WA-05 | Validar autenticidad de Meta | P0 | 3 |
| WA-06 | Enviar texto por Meta | P0 | 5 |
| WA-07 | Implementar idempotencia por message_id | P0 | 5 |
| WA-08 | Preparar procesamiento desacoplado si se necesita | P1 | 5 |
| WA-09 | Preparar plantillas transaccionales | P0 | 3 |
| WA-10 | Probar payloads, errores y reintentos | P0 | 5 |
| WA-11 | Documentar Meta y fallback Twilio | P0 | 3 |

### EPIC-09 — Dashboard y seguridad

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| ADM-01 | Proteger endpoints /admin | P0 | 5 |
| ADM-02 | Mantener service role solo en backend | P0 | 3 |
| ADM-03 | Aplicar mínimo privilegio y RLS | P0 | 5 |
| ADM-04 | Mostrar score, categoría y resultado | P0 | 3 |
| ADM-05 | Mostrar historial resumido | P0 | 3 |
| ADM-06 | Mostrar auditoría de tools | P0 | 5 |
| ADM-07 | Mostrar embudo y handoff | P1 | 5 |
| ADM-08 | Enmascarar cédula y teléfono | P0 | 3 |
| ADM-09 | Registrar cierre de casos | P1 | 3 |
| ADM-10 | Probar autorización y filtros | P0 | 5 |

### EPIC-10 — DevOps y observabilidad

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| OPS-01 | Crear Dockerfile no-root y .dockerignore | P0 | 3 |
| OPS-02 | Crear health y readiness | P0 | 2 |
| OPS-03 | Crear workflow de lint y tests | P0 | 5 |
| OPS-04 | Construir imagen en CI | P0 | 3 |
| OPS-05 | Configurar autenticación GitHub–GCP | P0 | 5 |
| OPS-06 | Desplegar staging en Cloud Run | P0 | 5 |
| OPS-07 | Desplegar demo con aprobación | P0 | 5 |
| OPS-08 | Usar GCP Secret Manager | P0 | 3 |
| OPS-09 | Emitir logs JSON con IDs y latencia | P0 | 5 |
| OPS-10 | Añadir correlation_id y enmascaramiento | P0 | 3 |
| OPS-11 | Medir p95, errores, tokens y costo | P0 | 5 |
| OPS-12 | Crear alertas mínimas | P1 | 3 |
| OPS-13 | Documentar rollback | P0 | 2 |

### EPIC-11 — Calidad y entregables

| ID | Tarea | Prioridad | Puntos |
|---|---|---:|---:|
| QA-01 | Mantener los tests de v1 | P0 | 3 |
| QA-02 | Cubrir dominio, tools y estados | P0 | 8 |
| QA-03 | Integrar con Supabase de prueba | P0 | 5 |
| QA-04 | Crear E2E del simulador | P0 | 5 |
| QA-05 | Crear E2E de WhatsApp staging | P0 | 5 |
| QA-06 | Probar duplicados, reinicios y caídas | P0 | 8 |
| QA-07 | Medir p95 menor de 8 segundos | P0 | 5 |
| QA-08 | Crear diagramas Mermaid | P0 | 5 |
| QA-09 | Documentar sprints y retrospectivas | P0 | 5 |
| QA-10 | Actualizar README y declaración de IA | P0 | 3 |
| QA-11 | Crear runbook | P0 | 3 |
| QA-12 | Preparar guion y datos de demo | P0 | 5 |
| QA-13 | Ejecutar ensayo general | P0 | 5 |

---

## 9. Ruta crítica

~~~mermaid
flowchart LR
    A[Requisitos aprobados] --> B[Migraciones y seed]
    B --> C[Reglas de dominio]
    C --> D[Estados v2]
    D --> E[Tools]
    E --> F[Agente GPT]
    B --> G[Índice RAG]
    G --> F
    F --> H[Meta y Redis]
    H --> I[Dashboard y seguridad]
    I --> J[Cloud Run]
    J --> K[E2E y demo]
~~~

El dashboard, la documentación y DevOps pueden avanzar en paralelo una vez que los contratos de datos estén definidos.

---

## 10. Contratos mínimos

### 10.1 Tools

Cada tool debe:

- Recibir un esquema validado.
- Devolver un objeto estructurado.
- Incluir success, data, error_code y trace_id.
- Aplicar timeout.
- Registrar auditoría.
- Enmascarar datos sensibles.
- Ser idempotente cuando escriba.
- Tener pruebas de éxito y error.

### 10.2 Estado

Cada transición registra:

- Estado anterior.
- Evento.
- Estado siguiente.
- Datos validados.
- Tool ejecutada.
- Timestamp.
- conversation_id.

GPT no puede escribir el estado directamente.

### 10.3 Resultado crediticio

Debe persistir:

- Score y categoría.
- Flags de riesgo.
- Ingreso, gastos y deuda.
- Capacidad de pago.
- Monto sugerido.
- Tasa, plazo y cuota.
- Resultado.
- Motivos.
- Versión de las reglas.

---

## 11. Estrategia de pruebas

| Nivel | Alcance | Bloquea entrega |
|---|---|---|
| Unitario | Cédula, reglas, estados y parsers | Sí |
| Contrato | Tools y proveedores | Sí |
| Integración | Supabase, Redis y RAG | Sí |
| API | Health, simulador, admin y webhook | Sí |
| IA | Guardrails, tools y fallback | Sí |
| E2E | Flujo del simulador | Sí |
| E2E WhatsApp | Entrada, respuesta y persistencia | Sí |
| Rendimiento | p95 y concurrencia | Sí |
| Seguridad | Auth, secretos, duplicados y PII | Sí |

Casos obligatorios:

- Cédula inválida e inexistente.
- Identidad no coincidente.
- Excelente sin mora.
- Aceptable con deuda.
- Regular o sin historial.
- Alto riesgo o mora.
- Usuario solicita asesor.
- Tres entradas inválidas.
- Mensaje duplicado.
- Redis caído.
- Supabase temporalmente no disponible.
- OpenAI timeout.
- Pregunta RAG sin evidencia.
- Dos usuarios concurrentes.

---

## 12. CI/CD

### Pull Request

1. Revisar formato y lint.
2. Detectar secretos.
3. Instalar dependencias fijadas.
4. Ejecutar tests.
5. Construir Docker.
6. Bloquear si algo falla.

### main

1. Ejecutar validaciones.
2. Construir imagen identificada por SHA.
3. Publicar imagen.
4. Desplegar Cloud Run.
5. Ejecutar smoke tests.
6. Conservar la revisión anterior para rollback.

Las migraciones destructivas nunca se ejecutarán automáticamente.

---

## 13. Variables y secretos

- APP_ENV
- APP_PUBLIC_URL
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY
- REDIS_URL
- OPENAI_API_KEY
- OPENAI_MODEL
- OPENAI_MAX_TOKENS
- OPENAI_TIMEOUT_SECONDS
- META_VERIFY_TOKEN
- META_ACCESS_TOKEN
- META_PHONE_NUMBER_ID
- META_APP_SECRET
- WHATSAPP_PROVIDER
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_WHATSAPP_FROM
- ADMIN_DASHBOARD_PASSWORD
- LOG_LEVEL

Reglas:

- .env.example no contiene valores sensibles.
- Staging y demo usan secretos distintos.
- No imprimir tokens ni cédulas completas.
- Rotar secretos expuestos.

---

## 14. Observabilidad y presupuesto

Métricas:

- Mensajes recibidos y respondidos.
- Duplicados descartados.
- Conversaciones por estado.
- Solicitudes por resultado.
- Handoffs.
- Latencia total y por tool.
- Errores por proveedor.
- Tokens y costo.
- Consultas RAG sin evidencia.

Objetivos:

- p95 menor de 8 segundos.
- Cero mezcla entre usuarios.
- Cero score o monto inventado.
- Presupuesto OpenAI cercano o inferior a USD 10.

Controles:

- Modelo económico configurable.
- Contexto corto.
- Límite de iteraciones y tokens.
- Pocos fragmentos RAG.
- LLM simulado en CI.
- Registro del costo estimado.

---

## 15. Seguridad

- Consentimiento antes de cédula.
- Aviso de precalificación.
- Datos exclusivamente ficticios.
- Cédula enmascarada.
- HTTPS.
- Validación del webhook.
- Idempotencia.
- Autenticación administrativa.
- Service role solo en backend.
- Mínimo privilegio y RLS.
- Auditoría.
- Sanitización de entradas.
- Validación backend de respuestas de IA.
- Sin secretos en commits.

---

## 16. Definition of Ready

Una historia entra al sprint si:

- Tiene objetivo claro.
- Tiene criterios verificables.
- Identifica dependencias.
- Está estimada.
- Tiene responsable.
- Define datos de prueba.
- No depende de una decisión abierta.

## 17. Definition of Done

Una historia termina cuando:

- Está integrada.
- Fue revisada.
- Pasa lint y tests.
- Incluye pruebas nuevas.
- No expone secretos ni datos reales.
- Actualiza documentación.
- Incluye manejo de errores y logs.
- Funciona en staging cuando aplica.
- Cumple criterios de aceptación.
- El Product Owner la acepta.

---

## 18. Criterios de aceptación del MVP

### Funcionales

- [ ] Inicio por Meta o simulador.
- [ ] Aviso y consentimiento.
- [ ] Validación módulo 10.
- [ ] Perfil y score desde Supabase.
- [ ] Elegibilidad sin depender de GPT.
- [ ] Monto y cuota desde tools.
- [ ] GPT no inventa datos.
- [ ] RAG responde con evidencia.
- [ ] Asesor disponible siempre.
- [ ] Duplicados descartados.
- [ ] Sesiones aisladas.
- [ ] Persistencia y auditoría.
- [ ] Dashboard protegido.

### No funcionales

- [ ] p95 menor de 8 segundos.
- [ ] Secretos fuera del repositorio.
- [ ] Datos enmascarados.
- [ ] Fallback de OpenAI.
- [ ] Recuperación de Redis.
- [ ] Docker reproducible.
- [ ] CI funcional.
- [ ] Cloud Run accesible.
- [ ] Rollback probado.

### Académicos

- [ ] Backlog priorizado.
- [ ] Cuatro sprints documentados.
- [ ] Planning, review y retrospectiva.
- [ ] Story mapping actualizado.
- [ ] Diagramas Mermaid.
- [ ] Declaración de uso de IA.
- [ ] README y guía.
- [ ] Demo ensayada.
- [ ] Retrospectiva final.

---

## 19. Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Meta se retrasa | Media | Alto | Empezar pronto y conservar Twilio |
| GPT inventa datos | Media | Alto | Tools y validación backend |
| Reglas no aprobadas | Media | Alto | Cerrar GOV-01 primero |
| Redis complica el MVP | Media | Medio | Interfaz y fallback Supabase |
| RAG irrelevante | Media | Medio | Evaluación y umbral |
| Duplicados | Alta | Alto | inbound_events único |
| Service role expuesta | Baja | Alto | Backend-only, auth y RLS |
| Dependencias cambian | Media | Medio | Versiones fijadas |
| Presupuesto agotado | Media | Medio | Mocks y límites |
| Trabajo simultáneo sin orden | Alta | Alto | Respetar ruta crítica |
| Documentación tardía | Alta | Medio | Incluirla en Done |
| Demo depende de terceros | Media | Alto | Simulador de respaldo |

---

## 20. Release y rollback

Release candidate cuando:

- Todos los P0 estén terminados.
- No existan defectos críticos.
- Tests y smoke tests pasen.
- Migraciones estén aplicadas.
- El flujo completo esté ensayado.
- Exista seed limpio.
- Secretos y presupuesto estén revisados.

Rollback:

- Conservar revisión anterior de Cloud Run.
- Evitar migraciones destructivas.
- Regenerar datos mediante seed.
- Poder volver a Twilio.
- Poder desactivar GPT.
- Documentar pasos en docs/runbook.md.

---

## 21. Guion mínimo de demo

1. Mostrar pipeline y arquitectura.
2. Abrir dashboard.
3. Iniciar perfil excelente.
4. Aceptar consentimiento.
5. Validar cédula ficticia.
6. Mostrar tool y auditoría.
7. Hacer una pregunta RAG.
8. Completar datos.
9. Mostrar cálculo determinista.
10. Mostrar solicitud en dashboard.
11. Ejecutar perfil regular o con mora.
12. Mostrar handoff.
13. Explicar seguridad, costos y límites.
14. Presentar sprints y retrospectiva.

Perfiles de respaldo:

- Excelente sin mora.
- Aceptable con deuda.
- Regular/sin historial.
- Alto riesgo/mora.
- Cédula inexistente.

---

## 22. Primeras acciones

1. Aprobar reglas y alcance.
2. Asignar responsables.
3. Crear GitHub Project.
4. Registrar ADR.
5. Estabilizar dependencias y tests.
6. Crear migraciones.
7. Crear esquema y seed.
8. Implementar dominio.
9. Implementar flujo determinista.
10. Congelar contratos de tools.
11. Iniciar Meta y GCP en paralelo.
12. Revisar Sprint 1 antes de incorporar GPT.

---

## 23. Seguimiento

Estados sugeridos:

- Backlog.
- Ready.
- In progress.
- In review.
- Blocked.
- Done.

Campos sugeridos:

- Epic.
- Sprint.
- Prioridad.
- Puntos.
- Responsable.
- Dependencia.
- Riesgo.
- Evidencia.

Indicadores por sprint:

- Puntos comprometidos y completados.
- Historias P0 terminadas.
- Defectos.
- Cobertura crítica.
- Tiempo de ciclo.
- Bloqueos.
- Costo de IA.
- Riesgos actualizados.

---

## 24. Checklist de inicio

- [ ] Reglas y tasas aprobadas.
- [ ] Responsables asignados.
- [ ] Supabase staging disponible.
- [ ] Meta test o Twilio disponible.
- [ ] Proyecto GCP configurado.
- [ ] API key OpenAI con límite.
- [ ] Redis seleccionado.
- [ ] Backlog cargado.
- [ ] Sprint 1 planificado.
- [ ] Definition of Done aceptada.

Cuando este checklist esté completo, CrediBot v2 puede entrar formalmente en ejecución.
