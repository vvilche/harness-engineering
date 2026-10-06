# Anexo de propuesta — Arquitectura de agentes industriales

**Base:** Barbaste, Darrigol, Vu, Wiltberger. *Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents.* arXiv:2609.00006v1, julio 2026.

---

## 1. Lo que la industria ya validó (y por qué esto importa para su planta)

Auditamos para usted el estado del arte real, no el de las presentaciones de proveedores. Sobre
**~4 millones de líneas de código fuente** de **12 sistemas de producción** —los cuatro agentes de
los proveedores frontera (Anthropic, OpenAI, Google, Mistral) más ocho de código abierto— el estudio
encuentra dos ausencias que se mantuvieron incluso al triplicar el corpus y re-auditar a los 3 meses:

**Ninguno de los 12 usa un framework de agentes.** Cero importan LangChain, LangGraph, AutoGen,
CrewAI, LlamaIndex, Pydantic AI, Genkit, Google ADK ni Semantic Kernel. Gemini CLI no usa ni los de
Google. Todos los bucles están escritos a mano.

**Ninguno usa búsqueda vectorial sobre código.** Cero. La recuperación es determinística: ripgrep,
tree-sitter, glob, sistema de archivos.

**Por qué le conviene esto.** La razón no es preferencia de estilo, es operativa: cuando un agente
modifica activos reales, las fallas de las abstracciones —prompt corrompido en silencio, caché
opaca, esquemas incompatibles entre versiones— cuestan más de lo que ahorran. La debuggabilidad le
gana a la reutilización.

**Aplicado a su operación:** un agente que consulta el tag real en el RTU o en la fuente de datos no
necesita un índice vectorial. Necesita leer la fuente. Cualquier capa intermedia entre la medición y
la decisión es una fuente de error nueva, y una copia que compite con el original. La recuperación
semántica se reserva para donde el documento **es** la fuente: normativa, cartas del Coordinador,
procedimientos.

---

## 2. Los siete subsistemas que todo agente debe resolver

Esta es la anatomía mínima verificada. Todo sistema del estudio toma posición en los siete, incluso
cuando la posición es *no tenerlo*.

| # | Subsistema | Qué decide | En su operación |
|---|---|---|---|
| 1 | **Bucle del agente** | Alterna razonamiento con acción; cuándo se detiene y cómo se recupera de fallas | Cuántas veces puede reintentar un agente que no logra leer el dato |
| 2 | **Integración con el modelo** | Qué proveedor, cómo se arma el prompt, caché, costo por token | Qué modelo por tarea; cuánto cuesta cada consulta |
| 3 | **Herramientas y acciones** | Qué puede hacer el agente y con qué | Leer medición, leer estado de interruptor, escribir en historial, NUNCA operar |
| 4 | **Memoria y contexto** | Qué recuerda entre turnos y entre sesiones | Si el turno de noche ve lo que hizo el de día |
| 5 | **Seguridad y permisos** | Qué corre sin preguntar, qué pregunta, qué está prohibido | El punto que decide si esto es desplegable o no |
| 6 | **Orquestación** | Cómo se coordinan varios agentes | Un agente por especialidad, o uno solo |
| 7 | **Extensibilidad** | Cómo se agrega capacidad sin tocar el núcleo | Cómo su equipo agrega una regla sin que intervenga el proveedor |

**Dato que ordena las prioridades:** el piso es bajo —un agente de ~100 líneas alcanza resultados en
el mismo rango que sistemas tres órdenes de magnitud más grandes— pero **lo que separa el piso de
producción no es completar la tarea**: es seguridad, recuperación, manejo de costo y extensibilidad.
En un sistema del estudio, 3 de cada 5 líneas de código no son el agente: son sus interfaces.

Usted no necesita el agente más sofisticado. Necesita el que **no se equivoque cuando no debe**.

---

## 3. Patrones que se repiten en los 12 sistemas, aplicados a su planta

De los 29 patrones catalogados, estos son los directamente aplicables a automatización y monitoreo
industrial.

| Patrón | Qué resuelve | En su planta |
|---|---|---|
| **Policy-as-Code** | Reglas de seguridad como archivo de configuración auditable, no código enterrado | Lista de acciones prohibidas en archivo revisable por su equipo de ciberseguridad |
| **Piso bajo el modo sin restricciones** | Incluso con permisos amplios, hay comandos que nunca se ejecutan | El agente no puede mandar un `rm`, un formateo ni un comando destructivo, aunque se le pida |
| **Deferred Loading** | Solo se cargan las herramientas relevantes al prompt | El agente de mantenimiento no arrastra la capacidad de operar la planta |
| **JIT Context Files** | Documentación jerárquica que se carga cuando hace falta | El procedimiento del área se carga solo al entrar a esa área |
| **Threshold Compaction** | Resumen incremental del historial sin perder decisiones tempranas | Un turno de 8 horas no pierde la hipótesis inicial |
| **Reflection Loop** | Autocorrección con feedback de verificación | El agente revisa el dato antes de reportarlo |
| **Outer Verification Loop** | Un guard valida que el trabajo esté completo antes de aceptar el cierre | No se cierra una ronda sin evidencia de verificación |
| **Untrusted-Content Delimiting** | Todo dato externo se marca como no confiable | Un manual o correo no puede dar instrucciones al agente |
| **Syntax-Aware Permissioning** | El comando se analiza antes de autorizarse | Se autorizan `git status`, no `git push`, sin pedir permiso cada vez |
| **Turn-Level Checkpoint** | Punto de retorno por paso, con reversión | Si el agente se equivoca, se vuelve al estado anterior |
| **Session-Tree Version Control** | Historial ramificable y retomable | Se puede reabrir la sesión de una falla y seguir desde ahí |
| **Client/Server** | El motor no está en la pantalla; cualquier interfaz es un cliente | El mismo agente en sala de control, tablet de terreno y reporte |

---

## 4. Seguridad: donde se decide si el sistema es desplegable

Los 12 sistemas ordenan su seguridad por el contexto de despliegue, no por tamaño. Dos recetas, y la
suya es la segunda.

**Herramienta con usuario de confianza** → tres modos de aprobación (solo-lectura / interactivo /
sin restricciones) con patrones de permiso por alcance.

**Entorno crítico, compartido o automatizado — su caso:**
1. **Aislamiento a nivel de sistema operativo** para lo que ejecuta
2. **Reglas de seguridad como archivo de política**, versionado y auditable
3. **Piso que sobrevive al modo sin restricciones**, con el interruptor bloqueado en tiempo de carga
   para que contenido inyectado no pueda activarlo en caliente
4. **Contenido externo como dato, nunca como instrucción**
5. **Trazas de auditoría por agente**, independientes del registro del proceso

**Principio que se repite en todos:** el agente **pide**, el sistema **concede**. El agente no toca
directamente el activo; solicita y queda registro de quién autorizó.

---

## 5. Cómo se ve esto en una propuesta CONECTA

Tres capacidades entregables, apoyadas en lo anterior:

**a) Agentes de campo con permisos verificables.**
Agente que lee medición, estado y documentación; propone; y no puede escribir en el sistema de
control. La lista de lo prohibido está en un archivo que su equipo revisa. Trazabilidad por acción.

**b) Memoria operacional entre turnos.**
Turno de noche retoma el trabajo del turno de día con el contexto completo, sin repetir diagnóstico.
La compactación preserva las decisiones iniciales, no solo las recientes.

**c) Integración sin dependencia del proveedor.**
El agente se expone por un protocolo estándar (ACP) que permite consumirlo desde el entorno que usted
ya usa —editor, IDE o su propia interfaz— sin desarrollo a medida por cada cliente, y con el modelo
de permisos del protocolo alineado con el suyo.

**Lo que NO proponemos, y por qué:**
- **No proponemos un framework de agentes.** Los 12 sistemas auditados no usan ninguno. Agregan
  capas que ocultan el prompt y el registro de lo que hizo el agente, justo lo que usted necesita ver.
- **No proponemos búsqueda semántica sobre datos de planta.** Una copia indexada de su medición nace
  desactualizada y compite con la fuente. Se consulta la fuente.
- **No proponemos multi-agente en la primera etapa.** Los sistemas multi-agente consumen ~15 veces más
  tokens que una conversación simple, y la mayoría de las tareas operativas no son paralelizables.

---

## 6. Cómo empezar, en el orden correcto

1. **Un agente, una herramienta, un límite.** Leer + reportar. Sin escritura, sin orquestación.
2. **Correr y medir.** Qué falla. Las fallas observadas definen qué se agrega — no la lista de deseos.
3. **Agregar seguridad antes de capacidad.** Política como código + piso que sobrevive al modo libre.
4. **Agregar memoria** cuando el trabajo pase de una sesión de un turno.
5. **Exponer el protocolo de integración** cuando haya un consumidor concreto.

Cada paso se justifica con una falla medida, no con una capacidad disponible.

---

*Fuente única de las afirmaciones técnicas de este anexo: arXiv:2609.00006v1 (julio 2026), estudio de
código fuente de 12 harnesses de producción. Las cifras de adopción citadas (ej. 9 de 12 usan skills,
8 de 12 usan MCP) están fechadas a julio de 2026: el estudio advierte que las afirmaciones de
inventario caducan en semanas, mientras las estructurales —anatomía y ausencias— se han mantenido.*
