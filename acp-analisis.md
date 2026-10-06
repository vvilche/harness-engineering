# ACP — Viabilidad para agentes CONECTA

**Pregunta:** ¿conviene exponer los agentes CONECTA como servidores ACP?
**Fecha:** 6 octubre 2026
**Base:** paper arXiv 2609.00006v1 (sección 13.3, Observación 11, Recomendación 13) + verificación en fuentes públicas.

════════════════════════════════════════════════════════
1. QUÉ ES ACP, EN UNA FRASE
════════════════════════════════════════════════════════

**ACP (Agent Client Protocol)** es un protocolo JSON-RPC 2.0 con mensajes delimitados por salto de
línea sobre stdio, que estandariza el borde **cliente ↔ agente**. Es, en palabras oficiales, *el LSP
de los agentes de código*: sin él, cada editor necesita una integración propia para cada agente; con
él, un agente que habla ACP funciona con todo editor que hable ACP.

Led por Zed (agentclientprotocol.com). **No confundir con el ACP de IBM** (Agent Communication
Protocol), que ya fue absorbido al track A2A. Son cosas distintas con la misma sigla.

Modelo de confianza, y esto es lo importante para CONECTA: **el cliente es dueño del entorno.** El
agente pide; el cliente concede. El sistema de archivos, las terminales y las aprobaciones de permiso
los posee el cliente. El agente corre como subproceso controlado.

Autenticación: soporta OAuth (AuthMethods anunciados en el handshake).

════════════════════════════════════════════════════════
2. LOS TRES ROLES ARQUITECTÓNICOS (hallazgo del paper)
════════════════════════════════════════════════════════

El paper documenta que ACP pasó de un relato de dos roles a tres en un trimestre. Esto es el núcleo
de la oportunidad:

**Rol 1 — Editor ↔ agente (servidor hacia afuera).**
El rol de diseño original. Zed, JetBrains y otros IDEs manejan un agente local como manejarían un
language server. **6 de 11 sistemas del corpus lo publican**: Mistral Vibe, OpenCode, Hermes,
OpenClaw, OpenHands, Gemini CLI.

**Rol 2 — Agente-como-backend (host hacia adentro). NEW.**
El rol que nadie ocupaba en abril de 2026. Un harness hospeda a un harness rival como motor
intercambiable:
- OpenHands corre Claude Code, Codex o Gemini CLI como backends ACP intercambiables dentro de una
  conversación de OpenHands (`ACPAgent` delega su `step()` a un servidor ACP externo)
- Hermes consume un agente ACP como **transporte de modelo** (el CLI de GitHub Copilot como backend
  de chat)
- El meta-harness Omnigent maneja su flota de adaptadores así

Traducción: el protocolo que se diseñó para editores terminó siendo **la interfaz para hospedar
agentes**.

**Rol 3 — Malla cross-vendor (A2A), sin adopción.**
A2A sigue siendo solo de Gemini CLI. Defendible, no probado a escala. **No es la apuesta.**

════════════════════════════════════════════════════════
3. RECOMENDACIÓN LITERAL DEL PAPER (Rec. 13)
════════════════════════════════════════════════════════

> **Publica un servidor ACP:** ya no es solo integración con editores — hace que tu harness sea
> consumible por hosts y meta-orquestadores. **Mantén tus propios sub-agentes in-process.**
> Para main-agent ↔ sub-agent NO adoptes ni ACP ni A2A: las primitivas in-process son lo que usan
> los sistemas de producción (8 de 9), y hasta las excepciones cross-process (Pi con JSONL, el swarm
> de Hermes sobre SQLite) evitan los protocolos estándar para ese rol.

Un servidor ACP compra **tres audiencias de una vez**: IDEs (Zed, JetBrains), harnesses anfitriones,
y meta-orquestadores.

════════════════════════════════════════════════════════
4. SUPERFICIE DEL PROTOCOLO (verificado en fuentes públicas)
════════════════════════════════════════════════════════

Transporte canónico: JSON-RPC 2.0 delimitado por salto de línea, UTF-8, sobre stdio del subproceso.
Transporte-agnóstico (hay implementaciones que lo pasan a WebSocket o TCP sin tocar el protocolo).

**Cliente → Agente** (lo que hay que implementar en el servidor):

| Método | Propósito |
|---|---|
| `initialize` | Handshake; intercambia capacidades y versión de protocolo |
| `authenticate` / `logout` | Dispara un flujo de autenticación anunciado por el agente |
| `session/new` | Crea una conversación (requiere `cwd` absoluto) |
| `session/load` | Restaura una sesión y **reproduce su historial** como notificaciones |
| `session/resume` | Restaura sin reproducir |
| `session/list` / `session/close` / `session/delete` | Ciclo de vida de sesiones |
| `session/prompt` | Envía un mensaje de usuario; resuelve al terminar el turno |
| `session/cancel` (notificación) | Interrumpe el turno en vuelo |
| `session/set_mode` | Cambia modo de permiso (default / acceptEdits / plan / auto / dontAsk / bypassPermissions) |
| `session/set_model` / `session/set_config_option` | Cambia modelo o config genérica |
| `session/fork` (inestable) | Bifurca la sesión en el punto actual |

**Agente → Cliente** (lo que el cliente debe manejar; el agente expone):

| Método | Propósito |
|---|---|
| `session/update` (notificación) | Salida en streaming: chunks de texto/pensamiento, tool calls y sus actualizaciones, plan, cambios de modo/config, comandos disponibles, uso y costo |
| `session/request_permission` | Pide al usuario aprobar una tool call; el usuario elige entre opciones ofrecidas |
| `fs/read_text_file`, `fs/write_text_file` | El agente lee/escribe vía la vista de archivos del cliente (incluye buffers sin guardar del editor) |
| `terminal/create`, `terminal/output`, `terminal/wait_for_exit`, `terminal/kill`, `terminal/release` | El agente corre comandos en terminales administradas por el cliente |
| `elicitation/create`, `elicitation/complete` (inestable) | El agente pide entrada estructurada por formulario |

Escape hatches: `extMethod(method, params)` y `extNotification(method, params)` — requests y
notificaciones arbitrarias en ambos sentidos.

**El `stopReason` del `session/prompt`** es el contrato de cierre del turno:
`end_turn` / `max_tokens` / `max_turn_requests` / `refusal` / `cancelled`.

**Modelo de confianza (crítico para el caso industrial):** el agente **no** toca el disco directo.
Pide por `fs/read_text_file` y `fs/write_text_file`; pide permiso por `session/request_permission`;
pide terminal por `terminal/create`. **El cliente decide qué concede.** Esto invierte el modelo de
los agentes actuales, que ejecutan con los permisos del usuario que los invoca.

════════════════════════════════════════════════════════
5. QUÉ GANARÍA CONECTA — Y QUÉ NO
════════════════════════════════════════════════════════

**Ganaría (real):**

1. **Integración sin trabajo por cliente.** Un agente CONECTA que habla ACP se consume desde Cursor,
   Zed, JetBrains o cualquier frontend ACP sin integración custom. Hoy cada cliente nuevo es
   desarrollo propio.

2. **Modelo de permisos alineado con OT.** El patrón del protocolo —el agente pide, el cliente
   concede, con UI de aprobación explícita— es exactamente el comportamiento que exige IEC 62443 y
   lo que exige un cliente eléctrico que no va a dejar que un LLM escriba en su SCADA sin revisión.
   **No hay que inventarlo: viene en el protocolo.**

3. **Auditoría nativa.** `session/update` con `tool_call` y `tool_call_update` deja traza estructurada
   de cada acción, con estado. Eso es evidencia para el cliente y para el regulador.

4. **Encaja en la jugada de posicionamiento.** El paper concluye que la capa que captura valor es la
   que **integra y gobierna**, no la que ejecuta. Un servidor ACP pone a CONECTA exactamente en esa
   capa: el agente de CONECTA se vuelve el componente que otros orquestan, en vez del producto que
   compite por la atención del operador.

5. **Sesiones compartidas y fork.** `session/load`/`resume`/`fork` permiten que un supervisor vea la
   sesión de un técnico, la retome o la ramifique. Caso real: turno de noche retoma lo que dejó el
   turno de día con el historial completo.

**NO ganaría / cautelas (honestas):**

1. **No es un estándar maduro de mercado.** El paper lo documenta en 6 de 11 sistemas, todos de
   código. El ecosistema industrial no lo conoce. La adopción sería **apuesta**, no aprovechamiento
   de infraestructura existente. Verificar cada trimestre cómo evoluciona.

2. **ACP no reemplaza la integración con el mundo OT.** ACP estandariza el borde
   editor↔agente, no cómo el agente lee un RTU. Lo de abajo (OPC-UA, Modbus, MQTT, UNS) sigue siendo
   trabajo propio. ACP es la puerta de entrada, no el motor.

3. **No adoptarlo para los sub-agentes.** Recomendación explícita del paper: los sub-agentes van
   in-process. Usar ACP solo en el borde hacia afuera.

4. **Riesgo de sobre-ingeniería.** Igual que con todo el resto del paper: empezar por el piso. Si
   ningún cliente lo va a consumir, el servidor ACP es código muerto. Implementarlo **cuando exista
   al menos un consumidor concreto** (un cliente, o un meta-orquestador que lo pida).

**Veredicto:** vale una **prueba de concepto acotada**, no una inversión. El costo de implementación
es bajo (el protocolo es JSON-RPC sobre stdio, y hay SDKs en TypeScript, Go y Python). El valor es
estratégico: posiciona los agentes CONECTA como componentes integrables en vez de productos aislados,
y el modelo de permisos del protocolo coincide con la exigencia de seguridad del cliente eléctrico.
Hacerlo cuando haya un consumidor concreto a la vista, medir la adopción del protocolo cada trimestre,
y no tocar los sub-agentes.

════════════════════════════════════════════════════════
6. SI SE HACE: SECUENCIA MÍNIMA
════════════════════════════════════════════════════════

1. **Fase 1 — Passthrough.** Servidor ACP mínimo sobre stdio que implemente `initialize`,
   `session/new`, `session/prompt` y `session/update`. Sin `fs/*`, sin `terminal/*`, sin permisos.
   Validar con el cliente de ejemplo del SDK oficial contra el agente.
2. **Fase 2 — Permisos.** Implementar `session/request_permission` y anunciar capacidades de
   `fs/read_text_file` / `fs/write_text_file` solo si el agente realmente necesita leer archivos.
   Declarar las ausencias en `initialize` (el protocolo espera que el cliente aprenda del handshake
   qué NO se implementó).
3. **Fase 3 — Sesiones.** `session/load` con replay de historial, `session/resume`, `session/list`.
   El sustrato de sesión es lo que hace útil el protocolo para turnos y supervisión.
4. **Medir adopción antes de Fase 4** (fork, elicitation, set_model).

════════════════════════════════════════════════════════
FUENTES
════════════════════════════════════════════════════════

- Paper: Barbaste, Darrigol, Vu, Wiltberger. *Harness Engineering: Anatomy, Architecture, and
  Evolution of Coding Agents.* arXiv:2609.00006v1, 15 julio 2026. Sección 13.3 (protocolos
  inter-agente), Observación 11, Recomendación 13, Tabla 14.
- Especificación ACP: https://agentclientprotocol.com/protocol/v1 y /schema
- Comparativa MCP / ACP / A2A y modelo de confianza: documentación pública del protocolo
- Implementaciones de referencia verificadas: `@agentclientprotocol/sdk` (TypeScript, incluye
  cliente de ejemplo), `@zed-industries/agent-client-protocol`, adaptador `claude-agent-acp`,
  paquetes Go comunitarios que implementan el lado servidor (`AgentHandler` + `Session`)
