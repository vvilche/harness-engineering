#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera clase-multientorno-industrial.html — clase para CONECTA (registro Academia CONECTA).

Tema: el harness pesa más que el modelo, y ahora se entrena al modelo DENTRO del harness.
Enfoque: hallazgo + consecuencias comerciales y de operación industrial.
Reutiliza el CSS de clase-harness-engineering.html (misma familia visual).
Determinista: cero llamadas a modelo.

Fuentes verificadas en primaria (6 oct 2026):
- "The ultimate guide to multi-harness RL" — Adithya S Kolavi / FineEnvs. HF Space.
- FineEnvs/LFM2.5-2.6B-multiharness-RL — checkpoint, 54.2% pass@1 step 1000.
- @ClementDelangue y @NousResearch, 5 oct 2026.
- Paper de disclosure de benchmarks (2026) citado en el artículo.
"""
import re, random

SRC = "clase-harness-engineering.html"
OUT = "clase-multientorno-industrial.html"

CSS = re.search(r"<style>(.*?)</style>", open(SRC, encoding="utf-8").read(), re.S).group(1)


# ── SVG: por qué el mismo modelo rinde distinto ──────────────────────────────
SVG_HARNESS_PESO = """
<svg viewBox="0 0 880 300" role="img" aria-label="Comparación entre cuánto mueve el harness y cuánto mueve el modelo el resultado de un agente">
  <text x="440" y="22" text-anchor="middle" font-size="12.5" fill="#334155" font-family="IBM Plex Sans,sans-serif">Cuánto mueve cada cosa el resultado final (puntos porcentuales)</text>

  <text x="150" y="72" text-anchor="end" font-size="12.5" fill="#0f172a" font-family="IBM Plex Sans,sans-serif" font-weight="700">Cambiar el harness</text>
  <rect x="160" y="54" width="390" height="26" rx="4" fill="#2563eb"/>
  <text x="562" y="73" font-size="13" font-weight="700" fill="#2563eb" font-family="IBM Plex Sans,sans-serif">hasta 13 puntos</text>

  <text x="150" y="118" text-anchor="end" font-size="12.5" fill="#0f172a" font-family="IBM Plex Sans,sans-serif" font-weight="700">Cambiar el modelo</text>
  <rect x="160" y="100" width="112" height="26" rx="4" fill="#64748b"/>
  <text x="284" y="119" font-size="13" font-weight="700" fill="#64748b" font-family="IBM Plex Sans,sans-serif">2,5 a 5 puntos</text>

  <line x1="160" y1="152" x2="830" y2="152" stroke="#cbd5e1" stroke-width="1"/>

  <text x="440" y="180" text-anchor="middle" font-size="12" fill="#334155" font-family="IBM Plex Sans,sans-serif" font-weight="700">Y la misma herramienta no le sirve igual a dos modelos distintos</text>
  <g font-family="IBM Plex Sans,sans-serif" font-size="11.5">
    <rect x="160" y="200" width="120" height="34" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
    <text x="220" y="221" text-anchor="middle" fill="#0f172a">GLM-5.2</text>
    <text x="300" y="222" font-size="12" fill="#dc2626" font-weight="700">23%</text>
    <text x="350" y="222" font-size="12" fill="#94a3b8">→</text>
    <text x="375" y="222" font-size="12" fill="#16a34a" font-weight="700">52%</text>
    <text x="410" y="222" font-size="11.5" fill="#64748b">(mismo modelo, dos harness)</text>

    <text x="160" y="252" font-size="11.5" fill="#64748b">El harness que sale 2º mejor para un modelo puede salir 9º para otro:</text>
    <text x="160" y="272" font-size="11.5" fill="#64748b">no existe «el mejor harness», existe el mejor para este modelo en esta tarea.</text>
  </g>
</svg>
"""

# ── SVG: sobreajuste al harness ──────────────────────────────────────────────
SVG_SOBREAJUSTE = """
<svg viewBox="0 0 880 250" role="img" aria-label="Las tres formas en que un modelo se sobreajusta a su harness">
  <text x="440" y="22" text-anchor="middle" font-size="12.5" fill="#334155" font-family="IBM Plex Sans,sans-serif">Tres formas de sobreajustarse a la herramienta — y qué se rompe al cambiarla</text>
  <g font-family="IBM Plex Sans,sans-serif">
    <rect x="40" y="46" width="250" height="150" rx="10" fill="#fff" stroke="#334155" stroke-width="1.5"/>
    <text x="165" y="74" text-anchor="middle" font-size="13" font-weight="700" fill="#0f172a">1 · Al formato</text>
    <text x="165" y="98" text-anchor="middle" font-size="11.5" fill="#64748b">Cómo se llama la herramienta y</text>
    <text x="165" y="115" text-anchor="middle" font-size="11.5" fill="#64748b">cómo se llaman sus argumentos.</text>
    <text x="165" y="145" text-anchor="middle" font-size="11.5" fill="#dc2626" font-weight="700">Se rompe: la llamada es rechazada</text>
    <text x="165" y="163" text-anchor="middle" font-size="11.5" fill="#dc2626" font-weight="700">antes de que la herramienta corra.</text>
    <text x="165" y="185" text-anchor="middle" font-size="10.5" fill="#94a3b8">el caso más frecuente</text>

    <rect x="315" y="46" width="250" height="150" rx="10" fill="#fff" stroke="#334155" stroke-width="1.5"/>
    <text x="440" y="74" text-anchor="middle" font-size="13" font-weight="700" fill="#0f172a">2 · Al contexto</text>
    <text x="440" y="98" text-anchor="middle" font-size="11.5" fill="#64748b">Cómo la herramienta resume y</text>
    <text x="440" y="115" text-anchor="middle" font-size="11.5" fill="#64748b">ordena el historial.</text>
    <text x="440" y="145" text-anchor="middle" font-size="11.5" fill="#dc2626" font-weight="700">Se rompe: pierde el hilo de la</text>
    <text x="440" y="163" text-anchor="middle" font-size="11.5" fill="#dc2626" font-weight="700">tarea y repite trabajo hecho.</text>
    <text x="440" y="185" text-anchor="middle" font-size="10.5" fill="#94a3b8">cuesta dinero, no da error</text>

    <rect x="590" y="46" width="250" height="150" rx="10" fill="#fff" stroke="#334155" stroke-width="1.5"/>
    <text x="715" y="74" text-anchor="middle" font-size="13" font-weight="700" fill="#0f172a">3 · Al flujo de control</text>
    <text x="715" y="98" text-anchor="middle" font-size="11.5" fill="#64748b">Los reintentos y condiciones de</text>
    <text x="715" y="115" text-anchor="middle" font-size="11.5" fill="#64748b">parada con que cuenta.</text>
    <text x="715" y="145" text-anchor="middle" font-size="11.5" fill="#dc2626" font-weight="700">Se rompe: se queda dando vueltas</text>
    <text x="715" y="163" text-anchor="middle" font-size="11.5" fill="#dc2626" font-weight="700">o se detiene antes de terminar.</text>
    <text x="715" y="185" text-anchor="middle" font-size="10.5" fill="#94a3b8">el más caro de detectar</text>
  </g>
</svg>
"""

# ── SVG: el proxy de captura ─────────────────────────────────────────────────
SVG_PROXY = """
<svg viewBox="0 0 860 235" role="img" aria-label="El proxy de captura entre el harness y el modelo">
  <defs><marker id="arp" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#94a3b8"/></marker></defs>
  <g font-family="IBM Plex Sans,sans-serif">
    <rect x="30" y="60" width="170" height="76" rx="9" fill="#0f172a"/>
    <text x="115" y="90" text-anchor="middle" font-size="13" font-weight="700" fill="#f8fafc">HARNESS REAL</text>
    <text x="115" y="110" text-anchor="middle" font-size="10.5" fill="#94a3b8">Claude Code, Codex,</text>
    <text x="115" y="125" text-anchor="middle" font-size="10.5" fill="#94a3b8">Hermes, Pi, OpenCode…</text>

    <line x1="202" y1="98" x2="252" y2="98" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arp)"/>
    <text x="227" y="88" text-anchor="middle" font-size="9.5" fill="#64748b">pide</text>

    <rect x="256" y="50" width="190" height="96" rx="9" fill="#2563eb"/>
    <text x="351" y="78" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">PROXY DE CAPTURA</text>
    <text x="351" y="98" text-anchor="middle" font-size="10.5" fill="#bfdbfe">el harness cree que es la API</text>
    <text x="351" y="118" text-anchor="middle" font-size="10.5" fill="#bfdbfe">entiende los 4 dialectos</text>
    <text x="351" y="135" text-anchor="middle" font-size="10.5" fill="#fef08a">registra TODO lo que salió</text>

    <line x1="448" y1="98" x2="498" y2="98" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arp)"/>
    <text x="473" y="88" text-anchor="middle" font-size="9.5" fill="#64748b">reenvía</text>

    <rect x="502" y="60" width="150" height="76" rx="9" fill="#fff" stroke="#334155" stroke-width="1.5"/>
    <text x="577" y="90" text-anchor="middle" font-size="13" font-weight="700" fill="#0f172a">MODELO</text>
    <text x="577" y="110" text-anchor="middle" font-size="10.5" fill="#64748b">el que se entrena</text>

    <line x1="577" y1="140" x2="577" y2="176" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arp)"/>
    <text x="577" y="196" text-anchor="middle" font-size="10.5" fill="#64748b">cada llamada, registrada</text>

    <rect x="672" y="60" width="158" height="76" rx="9" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
    <text x="751" y="88" text-anchor="middle" font-size="12.5" font-weight="700" fill="#0f172a">ENTRENADOR</text>
    <text x="751" y="108" text-anchor="middle" font-size="10.5" fill="#64748b">con el registro exacto,</text>
    <text x="751" y="123" text-anchor="middle" font-size="10.5" fill="#64748b">corrige y mejora</text>
    <line x1="655" y1="98" x2="668" y2="98" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arp)"/>

    <text x="430" y="222" text-anchor="middle" font-size="11.5" fill="#64748b">Ninguna de las 10 herramientas se modificó: se las usa tal como se instalan.</text>
  </g>
</svg>
"""

# ── Quiz: enfoque industrial ─────────────────────────────────────────────────
QS = [
    dict(
        q="Un cliente prueba un agente de IA sobre sus datos de planta y le da malos resultados. Dice: «la IA no sirve para esto». ¿Cuál es la respuesta técnicamente correcta?",
        opts=[
            "Tiene razón: si no funcionó, ese modelo no sirve para el caso",
            "Está midiendo una combinación de modelo + herramienta + instrucciones; cambiar la herramienta puede mover el resultado más que cambiar el modelo",
            "Hay que comprar un modelo más grande y caro",
            "El problema es la calidad de los datos de la planta",
        ],
        ok="Está midiendo una combinación de modelo + herramienta + instrucciones; cambiar la herramienta puede mover el resultado más que cambiar el modelo",
        why="Es el hallazgo central del estudio de Hugging Face y Liquid AI: con los mismos pesos, el mismo modelo resolvió 62% de las tareas bajo una herramienta y 33% bajo otra. Y en un experimento controlado sobre SWE-bench Verified, cambiar la herramienta movió el resultado hasta 13 puntos, mientras cambiar el modelo dentro de la misma herramienta lo movió entre 2,5 y 5. La conclusión comercial es directa: antes de descartar la IA hay que descartar el ensamblaje.",
    ),
    dict(
        q="Un proveedor te muestra una nota de benchmark de su agente. ¿Qué dato falta para que la cifra signifique algo?",
        opts=[
            "El precio por token del modelo",
            "Con qué harness se midió, porque una nota describe al modelo en esa herramienta, no al modelo en general",
            "El tamaño del modelo en parámetros",
            "La cantidad de GPU que usaron",
        ],
        ok="Con qué harness se midió, porque una nota describe al modelo en esa herramienta, no al modelo en general",
        why="El artículo lo pone como advertencia central: la nota viene con harness adjunto. Las fichas de modelos ya están declarando bajo qué framework se obtuvo cada número, y el mismo modelo aparece con cifras distintas en cada uno (Claude Opus 4.5: 45,9% en un leaderboard público y 55,4% dentro de su propia herramienta). Para una propuesta técnica esto es material de due diligence: una cifra sin su harness no es comparable con nada.",
    ),
    dict(
        q="Tu agente de monitoreo de subestaciones funciona bien con la herramienta que usas hoy, pero el cliente quiere manejarlo desde su propia interfaz. ¿Qué predice el estudio?",
        opts=[
            "Que va a funcionar igual, porque el modelo es el mismo",
            "Que puede degradarse o fallar del todo: la caída medida al cambiar de herramienta llegó a 58,8 puntos, a 3,6%",
            "Que hay que reentrenar el modelo desde cero con datos del cliente",
            "Que basta con reescribir las instrucciones",
        ],
        ok="Que puede degradarse o fallar del todo: la caída medida al cambiar de herramienta llegó a 58,8 puntos, a 3,6%",
        why="El paper Orchard midió la transferencia entre herramientas: un modelo entrenado en una pasó de 60% a 3,6% en otra, con cero en un benchmark de terminal. El artículo distingue dos fallas: tasa de resolución degradada (anda pero resuelve menos) y falla catastrófica de formato (su salida deja de ser usable). El caso típico es que el modelo llama a una herramienta con el nombre que le puso su harness original y el nuevo la rechaza antes de ejecutarla. Es exactamente el riesgo de un despliegue multi-interfaz.",
    ),
    dict(
        q="Estás definiendo el alcance de un piloto de agentes para un cliente industrial. ¿Qué conviene presupuestar además del modelo?",
        opts=[
            "Nada más: el modelo es lo determinante",
            "El ajuste del ensamblaje —herramienta, herramientas expuestas, contexto y condiciones de parada— y una prueba de transferencia si va a correr en más de una interfaz",
            "Solo la capa de seguridad y permisos",
            "El hardware de GPU para reentrenar el modelo",
        ],
        ok="El ajuste del ensamblaje —herramienta, herramientas expuestas, contexto y condiciones de parada— y una prueba de transferencia si va a correr en más de una interfaz",
        why="El hallazgo mueve el esfuerzo: si la herramienta explica más varianza que el modelo, entonces el trabajo de ingeniería rinde más ahí que en cambiar de modelo. Concretamente: elegir la herramienta, curar qué herramientas expone (no envolver cada API 1 a 1), decidir la compactación de contexto y publicar los topes de vueltas y costo. Y si el agente va a correr en la interfaz del cliente además de la tuya, la prueba de transferencia deja de ser un lujo: es la diferencia entre 60% y 3,6%.",
    ),
    dict(
        q="¿Qué distingue al ajuste supervisado (imitar) del aprendizaje por refuerzo (intentar), según el experimento?",
        opts=[
            "Imitar es siempre mejor porque aprende de un modelo más grande",
            "Imitar llegó a 47,5% y el refuerzo a 54%; además el de imitación escondía una caída de 17 puntos en una de las herramientas",
            "Son equivalentes en resultado",
            "El refuerzo solo sirve para modelos de frontera",
        ],
        ok="Imitar llegó a 47,5% y el refuerzo a 54%; además el de imitación escondía una caída de 17 puntos en una de las herramientas",
        why="El modelo entrenado imitando los aciertos de uno de 27B (el suyo tiene 2,6B) se estancó en 47,5%, por debajo de las dos corridas de refuerzo. Pero el dato más útil para una propuesta es el segundo: el promedio del modelo de imitación parecía bien mientras por dentro subía en tres herramientas y caía 17 puntos en la cuarta. Es el argumento de siempre: el promedio agregado oculta el problema, hay que mirar el desglose. Y el refuerzo además bajó 31% las llamadas a herramientas, porque se premió acertar con economía.",
    ),
    dict(
        q="El modelo del experimento tiene 2.600 millones de parámetros. ¿Qué implica eso para el negocio?",
        opts=[
            "Que no sirve para tareas industriales reales: es muy chico",
            "Que un modelo abierto y chico, entrenado para el flujo de trabajo, ya compite en tareas específicas y cabe en un notebook",
            "Que hay que esperar a que salga uno más grande",
            "Que solo funciona en la nube de quien lo entrenó",
        ],
        ok="Que un modelo abierto y chico, entrenado para el flujo de trabajo, ya compite en tareas específicas y cabe en un notebook",
        why="El experimento entrenó LFM2.5-2.6B, un modelo de 2.600 millones de parámetros que corre en un equipo común, y lo llevó de 42% a 54% entrenándolo dentro de cuatro herramientas reales. Para una propuesta industrial esto cambia la conversación: on-premise sin depender de la nube del proveedor, costo predecible, y la posibilidad de adaptar el modelo al flujo del cliente en vez de adaptar el cliente al modelo. Todos los pesos, datos y scripts están publicados y son abiertos.",
    ),
    dict(
        q="El estudio documenta que al modelo se le premió el acierto y también hacer menos consultas a herramientas. ¿Por qué importa ese segundo premio en operación industrial?",
        opts=[
            "Porque reduce el costo de la API y punto",
            "Porque sin una señal para terminar, el agente sigue dando vueltas: en corridas previas, entre 35% y 58% de los pasos de entrenamiento no enseñaban nada porque todos los intentos empataban",
            "Porque las herramientas tienen un límite de uso diario",
            "Porque así el agente escribe mejores informes",
        ],
        ok="Porque sin una señal para terminar, el agente sigue dando vueltas: en corridas previas, entre 35% y 58% de los pasos de entrenamiento no enseñaban nada porque todos los intentos empataban",
        why="Es la conexión directa con el bloque 5 de la clase: la condición de salida y el control de gasto. El experimento lo vivió en carne propia: con solo premiar el acierto, nada le indicaba al modelo que debía terminar, y una fracción enorme del entrenamiento fue inútil porque todos los intentos del grupo sacaban el mismo puntaje. Un premio pequeño por resolver con menos llamadas dio señal incluso cuando todo el grupo acertaba, y el resultado fue 31% menos consultas. Es el mismo principio del bloque 5: los topes baratos son los que evitan el gasto sin techo.",
    ),
    dict(
        q="Un colega dice: «entrenemos nuestro propio modelo y listo, dejamos de depender de los proveedores». ¿Qué dice el estudio sobre eso?",
        opts=[
            "Que es trivial y debería ser el primer paso de cualquier proyecto",
            "Que entrenar en una sola herramienta produce un modelo bueno ahí y mediocre en las demás: el modelo aprende el trámite de esa herramienta, no a resolver la tarea",
            "Que es imposible para cualquier empresa",
            "Que solo sirve si tienes más de 100 GPU",
        ],
        ok="Que entrenar en una sola herramienta produce un modelo bueno ahí y mediocre en las demás: el modelo aprende el trámite de esa herramienta, no a resolver la tarea",
        why="La formulación del equipo KwaiKAT que cita el artículo: si el entrenamiento se apoya en una sola herramienta, el modelo aprende «cómo resolver la tarea bajo las convenciones de interfaz de esa herramienta en particular», no cómo resolverla. El experimento lo confirma: entrenado solo en OpenCode llegó a 58% ahí y casi no mejoró en las otras tres. Entrenado en cuatro a la vez mejoró en las cuatro (42% → 54%). Para CONECTA la lectura es de arquitectura comercial: si el agente va a vivir en la interfaz del cliente, no se entrena contra la nuestra.",
    ),
]


def render_quiz():
    # Distribucion EXACTA: 2 correctas por cada posicion, sin repetir la original.
    # Evita que adivinar una letra fija apruebe el testeo.
    objetivo = [0, 0, 1, 1, 2, 2, 3, 3]
    rng = random.Random(1013)
    rng.shuffle(objetivo)
    parts = []
    for idx, it in enumerate(QS):
        opts = list(it["opts"]); correcta = it["ok"]
        orig = opts.index(correcta)
        pos = objetivo[idx]
        if pos == orig:
            # reasignar con una posicion libre del mismo pool
            libres = [x for x in range(4) if x != orig and objetivo.count(x) < 2]
            if libres:
                pos = libres[0]
        malas = [o for o in opts if o != correcta]
        rng.shuffle(malas); itm = iter(malas)
        nuevas = [correcta if p == pos else next(itm) for p in range(4)]
        assert nuevas[pos] == correcta and len(set(nuevas)) == 4
        parts.append((it["q"], nuevas, pos, it["why"]))

    def s(x): return '"' + x.replace('\\', '\\\\').replace('"', '\\"') + '"'
    blocks = ["  {\n    q: %s,\n    opts: [\n      %s\n    ],\n    ok: %d,\n    why: %s\n  }"
              % (s(q), ",\n      ".join(s(o) for o in op), ok, s(w))
              for q, op, ok, w in parts]
    return "const QS = [\n" + ",\n".join(blocks) + "\n];", [p[2] for p in parts]

# ── SECCIONES ────────────────────────────────────────────────────────────────
SECCIONES = [
("s0", "Bloque 0 · Qué cambió", "El hallazgo: la herramienta pesa más que el modelo", f"""
<p class="lead">Durante años la conversación fue «qué modelo usar». Un trabajo publicado en octubre de 2026 mide otra cosa: el programa que envuelve al modelo explica más del resultado que el modelo mismo.</p>

<p>Hugging Face y Liquid AI entrenaron un modelo chico y abierto dentro de las herramientas de código que la gente usa de verdad —Claude Code, Codex, Hermes, Pi, OpenCode y otras cinco— sin modificar ninguna. En el camino midieron algo que ordena toda la conversación comercial del rubro.</p>

<div class="grid2">
  <div class="kpi"><div class="big">13 pts</div><div class="lab">mueve el resultado <strong>cambiar la herramienta</strong><br><em>medido en SWE-bench Verified, todo lo demás fijo</em></div></div>
  <div class="kpi"><div class="big">2,5–5 pts</div><div class="lab">mueve <strong>cambiar el modelo</strong> dentro de la misma herramienta<br><em>el modelo importa menos de lo que se supone</em></div></div>
</div>

<div class="card accent">
  <h4>Los tres datos que lo prueban</h4>
  <ul style="margin-bottom:0">
    <li><strong>Mismos pesos, dos herramientas:</strong> GLM-5.2 resolvió 23% de las tareas bajo una herramienta y 52% bajo otra.</li>
    <li><strong>El mismo modelo en dos lugares:</strong> Claude Opus 4.5 saca 45,9% en un leaderboard público y 55,4% dentro de su propia herramienta.</li>
    <li><strong>Y no hay un ganador fijo:</strong> un harness puede ser el 2º mejor de diez para un modelo y el 9º para otro. Tres modelos que están a 3 puntos entre sí en un ranking público ganan cada uno bajo una configuración distinta.</li>
  </ul>
</div>

<div class="card warn">
  <h4>La consecuencia comercial, de frente</h4>
  <p style="margin-bottom:0">Si la herramienta explica más varianza que el modelo, entonces <strong>vender «el modelo» es vender la pieza equivocada</strong>. Lo que se vende —y lo que se defiende en una licitación— es el ensamblaje: qué herramienta, qué herramientas expuestas, cómo se maneja el contexto, qué topes de gasto y qué queda registrado. Es la tesis del bloque 10 de la clase de arquitectura, ahora con números: <em>la capa que captura valor es la que integra y gobierna, no la que ejecuta.</em></p>
</div>

<div class="card blue">
  <h4>Y el dato que le sirve al cliente</h4>
  <p style="margin-bottom:0">El modelo entrenado en el experimento pesa <strong>2.600 millones de parámetros</strong> —cabe en un notebook— y quedó en 54% de acierto habiendo arrancado en 42%. No es un modelo de frontera ni una nube ajena: es un modelo abierto, adaptable al flujo del cliente y desplegable on-premise. Para una operación industrial donde los datos no salen de la planta, eso cambia la conversación entera.</p>
</div>
"""),

("s1", "Bloque 1", "Por qué el modelo se sobreajusta a su herramienta", f"""
<p class="lead">No es una anomalía: es el mecanismo. Y tiene tres formas, todas medibles.</p>

<p>El equipo KwaiKAT lo formuló con precisión: en aprendizaje por refuerzo, si el entrenamiento se apoya en una sola herramienta, el modelo <em>«a menudo aprende no “cómo resolver la tarea”, sino “cómo resolver la tarea bajo las convenciones de interfaz de esa herramienta en particular”»</em>.</p>

<div class="svgwrap">
{SVG_SOBREAJUSTE}
<div class="figcap">Las tres formas de sobreajuste y qué se rompe al cambiar de herramienta. La primera da error visible; las otras dos, no.</div>
</div>

<h3>Por qué la tercera es la más peligrosa</h3>
<p>Cuando el modelo se sobreajusta al <strong>formato</strong>, el resultado es un error: la herramienta rechaza la llamada y se ve en pantalla. Cuando se sobreajusta al <strong>contexto</strong> o al <strong>flujo de control</strong>, no hay error: el agente sigue funcionando, cobrando tokens y dando vueltas. <strong>Un agente que da vueltas sin reportar error es el peor caso en operación industrial</strong>, porque consume sin producir y no dispara alarma.</p>

<div class="card bad">
  <h4>El dato que dimensiona el riesgo</h4>
  <p style="margin-bottom:0">El paper Orchard midió qué cuesta mover un modelo fuera de la herramienta donde se lo entrenó: un modelo pasó de su herramienta nativa a <strong>3,6%</strong> —una caída de <strong>58,8 puntos</strong>— y sacó cero en un benchmark de terminal. El artículo distingue dos fallas con nombres propios: <em>tasa de resolución degradada</em> (anda pero resuelve menos) y <em>falla catastrófica de formato</em> (su salida deja de ser usable). El caso típico del segundo: el modelo llama a una herramienta con el nombre que le puso su harness original, y el nuevo harness la rechaza antes de que la herramienta llegue a ejecutarse.</p>
</div>

<div class="card accent">
  <h4>La lectura para una propuesta</h4>
  <p style="margin-bottom:0">Cuando un agente va a operar en la interfaz del cliente —su SCADA, su HMI, su portal—, <strong>el traspaso de herramienta deja de ser un detalle de implementación y pasa a ser el riesgo principal del proyecto</strong>. Y es un riesgo que se mide antes de desplegar, no después: se corre el mismo conjunto de tareas bajo las dos herramientas y se compara. Si nadie lo midió, nadie sabe qué se está entregando.</p>
</div>

<div class="src"><strong>Fuentes:</strong> "The ultimate guide to multi-harness RL" (Kolavi / FineEnvs, Hugging Face, octubre 2026); paper Orchard sobre transferencia entre harnesses; reporte KAT-Coder del equipo KwaiKAT. Todas citadas en el artículo.</div>
"""),

("s2", "Bloque 2", "Cómo se entrena un modelo dentro de la herramienta", f"""
<p class="lead">El problema técnico era simple de enunciar y difícil de resolver: el modelo vive dentro de la herramienta, y la herramienta no deja ver qué generó.</p>

<p>Entrenar por refuerzo necesita algo muy específico: los <strong>tokens exactos</strong> que el modelo produjo y su probabilidad. Sin eso, la corrección no corresponde a lo que el modelo realmente hizo. Y el harness no los expone: hacia afuera solo deja ver un ida y vuelta de peticiones.</p>

<div class="svgwrap">
{SVG_PROXY}
<div class="figcap">El proxy de captura. El harness no distingue entre hablarle al modelo o al intermediario; por eso ninguna de las 10 herramientas necesitó modificarse.</div>
</div>

<h3>La decisión de arquitectura que hace esto elegante</h3>
<p>La salida obvia era reescribir cada herramienta como un simulador. La que eligieron es la contraria: <strong>no reescribir el harness, ponerle un intermediario que él cree que es el modelo</strong>. El intermediario habla los cuatro dialectos de API que usan los agentes de código, unifica los pedidos, reenvía al motor de inferencia y anota todo.</p>

<div class="card ok">
  <h4>Por qué esto importa en términos de ingeniería</h4>
  <p style="margin-bottom:0">Es la misma lección de la clase de arquitectura en otro plano: <strong>cuando no puedes cambiar el componente, intercepta su frontera</strong>. El único punto por el que todo harness obligadamente pasa es la llamada al modelo — igual que el único punto por el que pasa toda operación en una planta es la interfaz del equipo. El proxy de captura es, funcionalmente, un hook de ciclo de vida aplicado al entrenamiento: el mismo patrón D7 del bloque 9 de la clase de arquitectura.</p>
</div>

<div class="card warn">
  <h4>Una advertencia para no sobrevender</h4>
  <p style="margin-bottom:0">Esto es <strong>frontera de investigación aplicada, no práctica de consultoría</strong>. Las corridas del experimento tomaron 46 horas de cómputo, requieren GPU de entrenamiento y un equipo que sepa de RL. Lo que sí es aplicable hoy en un proyecto industrial es la <em>consecuencia</em>, no el método: saber que el ensamblaje pesa más que el modelo, y que el traspaso entre herramientas se mide antes de desplegar.</p>
</div>

<div class="src"><strong>Fuente:</strong> sección "How the framework works" del artículo. El proxy deriva sus conversores de dialecto del gateway Polar de NVIDIA; el entrenamiento corre sobre OpenEnv, Harbor (tareas y sandboxes) y TRL.</div>
"""),

("s3", "Bloque 3", "El experimento: qué midieron y qué salió", f"""
<p class="lead">Un modelo de 2.600 millones de parámetros, 1.000 tareas, y dos formas de entrenarlo. El resultado ordena las prioridades.</p>

<div class="card accent">
  <h4>El diseño, en concreto</h4>
  <ul style="margin-bottom:0">
    <li><strong>Modelo:</strong> LFM2.5-2.6B, abierto, de 2.600 millones de parámetros.</li>
    <li><strong>Tareas:</strong> 1.000 tareas de análisis de datos construidas desde notebooks reales; 400 medianas y 600 difíciles.</li>
    <li><strong>Test:</strong> 250 tareas reservadas, sin superposición de notebook, pregunta ni instrucción.</li>
    <li><strong>Dos corridas:</strong> una entrenada solo en OpenCode, otra entrenada en cuatro herramientas a la vez (OpenCode, Claude Code, Codex y Mini-SWE-Agent), donde cada grupo de intentos usa una de las cuatro.</li>
  </ul>
</div>

<div class="svgwrap">
{SVG_HARNESS_PESO}
<div class="figcap">Los dos órdenes de magnitud del hallazgo: la herramienta mueve más que el modelo, y no existe una herramienta que gane para todos.</div>
</div>

<table>
  <tr><th style="width:30%">Qué se midió</th><th>Qué salió</th></tr>
  <tr><td><strong>Punto de partida</strong></td><td>El mismo modelo, antes de entrenar: <strong>62%</strong> bajo Mini-SWE-Agent y <strong>33%</strong> bajo Claude Code. Una nota de benchmark describe al modelo <em>en una herramienta</em>.</td></tr>
  <tr><td><strong>Entrenar en una</strong></td><td>De <strong>34% a 58%</strong> en OpenCode. Casi nada en las otras tres herramientas.</td></tr>
  <tr><td><strong>Entrenar en cuatro</strong></td><td>De <strong>42% a 54%</strong>, promedio sobre las cuatro, <strong>mejorando en todas</strong> — incluidas las tareas bajo herramientas donde no entrenó directamente.</td></tr>
  <tr><td><strong>Economía</strong></td><td>El modelo multi-herramienta hizo <strong>31% menos llamadas</strong> a herramientas en las tareas que ya resolvía.</td></tr>
  <tr><td><strong>Imitar vs. intentar</strong></td><td>Ajuste supervisado sobre los aciertos de un modelo de 27B: <strong>47,5%</strong>. Refuerzo: <strong>54%</strong>. Imitar quedó por debajo.</td></tr>
</table>

<div class="card bad">
  <h4>El detalle que hay que subrayar</h4>
  <p style="margin-bottom:0">El modelo entrenado por imitación parecía correcto en el promedio, pero <strong>por dentro subía en tres herramientas y caía 17 puntos en la cuarta</strong>. Un promedio agregado que se ve bien y esconde un desplome: es exactamente el error que la metodología de esta casa prohíbe. <em>Un «todo bien» agregado puede ocultar el bug.</em></p>
</div>

<div class="src"><strong>Fuente:</strong> capítulo "Training small models across harnesses" y "Conclusions" del artículo. Las curvas completas, los checkpoints y los scripts están publicados.</div>
"""),

("s4", "Bloque 4", "Qué significa para CONECTA", f"""
<p class="lead">Tres consecuencias operativas, y una advertencia sobre qué no prometer.</p>

<div class="grid2">
  <div class="card"><h4>1 · El esfuerzo rinde en el ensamblaje</h4><p style="margin-bottom:0">Si la herramienta explica más varianza que el modelo, la ingeniería rinde más eligiendo herramienta, curando las herramientas expuestas, decidiendo la compactación de contexto y publicando los topes de gasto — que comprando un modelo más caro. Es donde ya está el trabajo de la clase de arquitectura, ahora con respaldo empírico.</p></div>
  <div class="card"><h4>2 · El despliegue multi-interfaz es un riesgo medible</h4><p style="margin-bottom:0">Si el agente va a vivir en la interfaz del cliente, hay una prueba que hacer antes de firmar: el mismo conjunto de tareas bajo las dos herramientas. La caída medida llegó a 58,8 puntos. Es la diferencia entre entregar un sistema y entregar una demo.</p></div>
  <div class="card"><h4>3 · On-premise ya es una opción real</h4><p style="margin-bottom:0">Un modelo de 2.600 millones de parámetros, abierto, entrenado para el flujo de trabajo y desplegable en un equipo común. Para plantas donde los datos no salen del perímetro, esto deja de ser un deseo y pasa a ser una alternativa con números.</p></div>
  <div class="card"><h4>4 · Y la advertencia</h4><p style="margin-bottom:0">Entrenar modelos es <strong>frontera de investigación aplicada</strong>: 46 horas de cómputo, GPU dedicada y equipo especializado. No es lo que hay que vender hoy. Lo que se vende es el ensamblaje y la medición; el entrenamiento es la etapa siguiente, cuando el volumen lo justifique.</p></div>
</div>

<div class="card accent">
  <h4>Cómo se dice esto en una propuesta, sin tecnicismo</h4>
  <p style="margin-bottom:0">«El rendimiento de un agente de IA depende más de cómo está ensamblado que del modelo que usa: cambiar la herramienta que lo envuelve puede mover el resultado hasta 13 puntos, contra 2,5 a 5 de cambiar el modelo. Por eso nuestro trabajo se concentra en el ensamblaje —qué puede hacer el agente, qué queda registrado, qué pasa cuando se equivoca— y en medir el traspaso antes de desplegar, no en perseguir el modelo de moda.»</p>
</div>

<div class="card violet">
  <h4>Y el eslabón que cierra el argumento</h4>
  <p style="margin-bottom:0">La clase de arquitectura termina diciendo que <strong>la unidad competitiva del campo ya no es el bucle del agente, sino la superficie de ecosistema alrededor</strong>. Este trabajo es la demostración empírica de esa tesis: el valor está en el ensamblaje, no en el motor. Y el ensamblaje es exactamente lo que CONECTA hace.</p>
</div>
"""),
]


def build():
    quiz_js, posiciones = render_quiz()

    secs = "\n\n".join(
        '<section id="%s">\n  <div class="sec-num">%s</div>\n  <h2>%s</h2>\n%s\n</section>' % (a, b, c, d)
        for a, b, c, d in SECCIONES
    )

    testeo = """
<section id="testeo">
  <div class="sec-num">Demostrar aprendizaje</div>
  <h2>Testeo: 8 preguntas</h2>
  <p class="lead">Cada respuesta despliega su explicación. El objetivo no es la nota: es poder sostener el argumento frente a un cliente.</p>
  <div id="quiz"></div>
  <button id="btnCheck" onclick="checkTest()">Revisar respuestas</button>
  <button class="ghost" onclick="location.reload()" style="margin-left:10px">Reiniciar</button>
  <div id="score"></div>
</section>
"""

    fuentes = """
<section id="fuentes">
  <div class="sec-num">Referencias</div>
  <h2 >Fuentes</h2>
  <div class="card">
    <h4>Documento base</h4>
    <p style="margin-bottom:0">Kolavi, A. S. <em>The ultimate guide to multi-harness RL.</em> FineEnvs / Hugging Face, publicado en octubre de 2026 (resultados compilados al 29 de septiembre de 2026). Guía interactiva con las curvas, los datos y los scripts.<br><br>
    <a href="https://huggingface.co/spaces/AdithyaSK/multi-harness-rl">huggingface.co/spaces/AdithyaSK/multi-harness-rl</a></p>
  </div>
  <div class="card">
    <h4>Artefactos verificables</h4>
    <ul style="margin-bottom:0">
      <li><strong>El modelo entrenado:</strong> <a href="https://huggingface.co/FineEnvs/LFM2.5-2.6B-multiharness-RL">FineEnvs/LFM2.5-2.6B-multiharness-RL</a> — paso 1.000, 54,2% de acierto en cuatro herramientas. Pesos completos publicados, no un adaptador.</li>
      <li><strong>Los datos:</strong> <a href="https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-multiharness-sft">SmolDataEnvs-multiharness-sft</a> — las trayectorias de entrenamiento, una configuración por herramienta.</li>
      <li><strong>El stack:</strong> OpenEnv (interfaz), Harbor (tareas y sandboxes) y TRL (entrenador), todo abierto.</li>
      <li><strong>La infraestructura:</strong> el proxy de captura está integrado en OpenEnv; los conversores de dialecto derivan del gateway Polar de NVIDIA.</li>
    </ul>
  </div>
  <div class="card">
    <h4>Qué es y qué no es este material</h4>
    <ul style="margin-bottom:0">
      <li><strong>Es</strong> una medición publicada y reproducible: pesos, datos, entornos y scripts están abiertos y cualquiera puede re-correrlos.</li>
      <li><strong>No es</strong> una recomendación de entrenar modelos en cada proyecto. Las corridas tomaron 46 horas de cómputo y requieren equipo especializado.</li>
      <li><strong>Cuidado con citar cifras de inventario.</strong> Los números de este material están fechados a septiembre–octubre de 2026 y el rubro se mueve en semanas. El hallazgo estructural —que el ensamblaje pesa más que el modelo— es el que se sostiene.</li>
      <li><strong>Origen del dato.</strong> Este material partió de una tendencia en X del 5 de octubre de 2026. Todos los números fueron verificados contra las fuentes primarias (el artículo, la ficha del modelo y los capítulos técnicos), no contra el resumen de la plataforma social.</li>
    </ul>
  </div>
  <div class="card">
    <h4>Material relacionado de esta carpeta</h4>
    <ul style="margin-bottom:0">
      <li><code>clase-harness-engineering.html</code> — la clase base: anatomía, los 7 subsistemas y las 2 ausencias. Este material continúa su bloque 10.</li>
      <li><code>anexo-conecta.md</code> — el anexo comercial para propuestas.</li>
      <li><code>acp-analisis.md</code> — viabilidad de exponer los agentes CONECTA como servidores ACP.</li>
    </ul>
  </div>
  <div class="src" style="border-top:none;padding-top:0">Clase generada el 6 de octubre de 2026 · Academia CONECTA.</div>
</section>
"""

    html = """<!DOCTYPE html>
<html lang="es-CL">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>El mismo modelo, otra herramienta — por qué el ensamblaje pesa más</title>
<style>@@CSS@@</style>
</head>
<body>
<div class="layout">
<nav>
  <div class="brand">Academia CONECTA</div>
  <h1>El mismo modelo, otra herramienta</h1>
  <div class="sub">Por qué el ensamblaje pesa más que el modelo — y qué se midió en octubre de 2026. Continuación de <em>Cómo se construye un agente de IA</em>.</div>

  <div class="grp">El hallazgo</div>
  <a href="#s0"><span class="n">0</span>La herramienta pesa más</a>
  <a href="#s1"><span class="n">1</span>Por qué se sobreajusta</a>

  <div class="grp">El método</div>
  <a href="#s2"><span class="n">2</span>Entrenar dentro del harness</a>
  <a href="#s3"><span class="n">3</span>El experimento</a>

  <div class="grp">Cierre</div>
  <a href="#s4"><span class="n">4</span>Qué significa para CONECTA</a>
  <a href="#testeo">Demostrar aprendizaje</a>
  <a href="#fuentes">Fuentes</a>

  <a class="foot" href="clase-harness-engineering.html">← Clase base: arquitectura →</a>
  <a class="foot" href="anexo-conecta.md">Anexo comercial →</a>
</nav>

<main>

<section id="intro">
  <div class="sec-num">Academia CONECTA · clase complementaria</div>
  <h2>El mismo modelo, otra herramienta</h2>
  <p class="lead">El hallazgo que reordena la conversación comercial de los agentes: el programa que envuelve al modelo explica más del resultado que el modelo mismo. Medido, publicado y reproducible.</p>
  <div class="card accent">
    <h4>De dónde sale esto</h4>
    <p>El 5 de octubre de 2026, Hugging Face y Liquid AI publicaron un trabajo que entrena un modelo chico y abierto <strong>dentro de las herramientas de código reales</strong> —Claude Code, Codex, Hermes, Pi, OpenCode y otras cinco— sin modificar ninguna. El resultado es una medición limpia de algo que la clase de arquitectura afirmaba sin números.</p>
    <p style="margin-bottom:0">Todo está abierto: los pesos, los datos, los entornos y los scripts. Cualquiera con GPU puede re-correrlo.</p>
  </div>
  <div class="card warn">
    <h4>Cómo leer este material</h4>
    <p style="margin-bottom:0">Es una clase de <strong>consecuencias comerciales y de operación industrial</strong>, no de método. El mecanismo técnico se explica lo suficiente para entender qué se midió, pero el objetivo es otro: que puedas sostener frente a un cliente por qué el trabajo de ingeniería rinde en el ensamblaje y no en perseguir el modelo de moda. Al final hay un testeo de 8 preguntas y una sección con lo que <em>no</em> conviene prometer.</p>
  </div>
</section>

@@SECCIONES@@

@@TESTEO@@

@@FUENTES@@

</main>
</div>
<script>
@@QUIZJS@@

let html = "";
QS.forEach((item, i) => {
  html += '<div class="q" id="q' + i + '">';
  html += '<div class="qh">' + (i+1) + '. ' + item.q + '</div>';
  item.opts.forEach((o, j) => {
    html += '<label><input type="radio" name="q' + i + '" value="' + j + '">' + o + '</label>';
  });
  html += '<div class="why" id="w' + i + '"><strong>Por qué:</strong> ' + item.why + '</div>';
  html += '</div>';
});
document.getElementById("quiz").innerHTML = html;

function checkTest(){
  let score = 0, answered = 0;
  QS.forEach((item, i) => {
    const box = document.getElementById("q" + i);
    const labels = box.querySelectorAll("label");
    const sel = box.querySelector('input[name="q' + i + '"]:checked');
    labels.forEach(l => l.classList.remove("correct", "wrong"));
    if (!sel) return;
    answered++;
    labels.forEach((l, j) => {
      if (j === item.ok) l.classList.add("correct");
      if (j === parseInt(sel.value) && parseInt(sel.value) !== item.ok) l.classList.add("wrong");
    });
    if (parseInt(sel.value) === item.ok) score++;
    document.getElementById("w" + i).classList.add("show");
  });
  const pct = Math.round(100 * score / QS.length);
  let msg = "";
  if (pct === 100) msg = "Dominio completo. Puedes sostener el argumento frente a un cliente.";
  else if (pct >= 75) msg = "Base sólida. Repasa los bloques de las preguntas que fallaron.";
  else if (pct >= 50) msg = "Entendiste la idea general. Vuelve a los bloques 0, 1 y 4.";
  else msg = "Conviene releer la clase completa antes de usarla en una propuesta.";
  const s = document.getElementById("score");
  s.innerHTML = '<span class="n">' + score + ' / ' + QS.length + '</span> &nbsp;(' + pct + '%) &nbsp;— ' + msg +
                '<div style="margin-top:10px;font-size:14px;color:#94a3b8">Respondidas ' + answered + ' de ' + QS.length + '. Cada respuesta despliega su explicación arriba.</div>';
  s.classList.add("show");
  s.scrollIntoView({behavior:"smooth", block:"center"});
}
</script>
</body>
</html>
"""

    html = (html.replace("@@CSS@@", CSS)
                .replace("@@SECCIONES@@", secs)
                .replace("@@TESTEO@@", testeo)
                .replace("@@FUENTES@@", fuentes)
                .replace("@@QUIZJS@@", quiz_js))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    return posiciones


if __name__ == "__main__":
    pos = build()
    print("OK ->", OUT)
    print("posiciones correctas del quiz:", pos)
