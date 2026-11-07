# baton 0.3 en uso real: el run `fase4a` de MSG

Análisis del primer uso real de baton 0.3. Lo escribe el chat de baton el 2026-11-07, leyendo solo lo archivado del run. Sirve de entrada para el plan de 0.4.

## Fuentes y método

- **Archivo del run:** `C:/MSG/.claude/runs/_baton-trazas/fase4a-archivo/`, copiado por el coordinador de MSG antes del cierre. Contiene:
  - `run-baton-fase4a/`: `state.json`, `decisions.md` (145 líneas), briefs, results, reviews, critics y `audit-pr/`;
  - `retro-fase4a.md`, del 31-oct;
  - `sesiones.json`;
  - `transcripts/`: 17 `.jsonl` principales y 1.147 archivos en total, con los subagentes.
- **Citas:**
  - `[dec:N]` es la línea N de `decisions.md`;
  - `[retro §N]` es la sección N de la retro del 31-oct;
  - `[state]` es `state.json`.
- **Coste:** sale de los scripts `scripts/fase4a-cost.py` y `scripts/fase4a-coordinator.py`, ejecutados sobre el archivo con `python -I`. Usan la misma fórmula que la retro:
  - Opus 4/20 USD y Sonnet 2/10 USD por millón de tokens de entrada/salida;
  - escritura de caché a 1,25× y lectura a 0,1×;
  - Fable valorado como Opus;
  - cada mensaje cuenta una sola vez, deduplicado por `message.id` entre todos los transcripts.
  
  La persona trabaja con suscripción (el implementador se paró por el límite semanal [dec:97]), así que los USD son **equivalente a precio de API**, no lo que se pagó. Con esta fórmula, la retro reproducía el coste que registró la app con un error del 1 %.
- **Tamaño de las PR:** `git diff --shortstat <baseSha> <head>` en cada repo, solo lectura.
- **Fases del run** usadas en las tablas:
  - **A:** del lanzamiento a la primera entrega, 2026-10-27T18:20Z → 2026-10-31T03:18Z;
  - **B:** los arreglos de las reviews frescas de PR, hasta 09:30Z del 31-oct;
  - **C:** el correctivo de calidad que pidió el dueño, del 31-oct 09:30Z al merge del 2026-11-07T21:19Z.

## 1. Resumen

- **El plan se entregó en 81 h y se mergeó a los 11 días.** Las 9 partes (P0–P7 y CA) se entregaron a las 80 h 58 min, con 3 PR y el snapshot verificado [state]. El dueño revisó las PR y encontró 9 defectos de diseño y estructura que ninguna de las 50 reviews había marcado [dec:77]. De ahí salió un correctivo de 7 días y 18 h, con un implementador nuevo, y el merge llegó el 2026-11-07 a las 21:19 [dec:144].
- **El 79 % del coste fue después de la primera entrega.** Del total de ~3.062 USD, 648 USD corresponden a la fase A, 71 USD a la B y 2.344 USD a la C (tabla 2.2). Mientras baton daba el plan por terminado, el trabajo de calidad apenas había empezado.
- **Lo que funcionó de 0.3:**
  - la sesión por parte;
  - la verificación del coordinador en los tres repos;
  - las pausas y la autoridad con delegación;
  - la entrega por hooks de MSG: 4 entregas o reentregas, cada una comprobada con `gh pr view`.
- **Lo que falló:**
  - una revisión centrada en el diff de cada parte, que no cubría la PR entera ni aplicaba las reglas del repo;
  - el crecimiento de la PR sin avisar: el backend pasó de 310 a 1.922 archivos (tabla 2.4);
  - gates verdes que se saltaban tests;
  - despertares y arranques poco fiables;
  - el correctivo, que se hizo fuera de baton, con briefs escritos a mano.

## 2. Cifras

### 2.1 Línea de tiempo

| Tramo | Desde → hasta (UTC) | Duración | Fuente |
|---|---|---|---|
| Propuesta y lanzamiento | 27-10 18:20 → 18:24 | 4 min | [state] `presses` |
| Partes P0–P7 y CA (fase A) | 27-10 18:27 → 31-10 03:18 | 80 h 51 min, de ellas unas 26 h esperando a la persona | [retro §2, §5] |
| Arreglos tras las reviews frescas de PR (B) | 31-10 04:30 → 07:30 | 3 h | [dec:71–75] |
| Correctivo de calidad, Q0–Q5 y cierres final y r2–r7 (C) | 31-10 09:30 → 07-11 16:30 | 7 d 7 h | [dec:77–141] |
| Arreglo de la CI y merge | 07-11 17:30 → 21:19 | 3 h 49 min | [dec:142–144] |
| **Total** | 27-10 18:20 → 07-11 21:19 | **266 h 59 min (11 d 3 h)** | |

### 2.2 Coste por papel y por fase (USD equivalentes de API)

| Papel | A | B | C | Total | % |
|---|---|---|---|---|---|
| Coordinador (chat) | 41,08 | 4,78 | 91,81 | 137,67 | 4,5 % |
| Subagentes del coordinador: reviews y auditorías | 5,70 | 12,48 | 837,60 | 855,78 | 27,9 % |
| Subagentes del coordinador: implementador en proceso y Q5 | — | — | 75,11 | 75,11 | 2,5 % |
| Subagentes del coordinador: retro y otros | — | 4,80 | 11,43 | 16,23 | 0,5 % |
| Sesiones de implementador (10) | 435,85 | 40,60 | 386,75 | 863,21 | 28,2 % |
| Subagentes de trabajo de los implementadores | 27,75 | — | 941,50 | 969,24 | 31,6 % |
| Reviewers dentro de las partes | 95,18 | 5,79 | — | 100,95 | 3,3 % |
| Critic dentro de las partes | 42,11 | 2,06 | — | 44,18 | 1,4 % |
| **Total** | **647,67** | **70,51** | **2.344,21** | **3.062,39** | |

Fuente: `scripts/fase4a-cost.py`. Cada mensaje cae en la fase de su hora. La review extra con Fable de P7 (A) está en la fila de reviews del coordinador.

- **La revisión en todas sus formas costó 1.001 USD, el 32,7 %.** Suma los reviewers y las Critic de las partes y las reviews y auditorías del coordinador. En la ronda de laboratorio de 0.3 fue un 4,5 %, y en la fase A de este run, un 21 % [retro §3].
- **El coordinador costó el 4,5 %.** En el laboratorio fue el 82 % (README de 0.3). Releer su chat sale barato frente al trabajo real de las partes.
- **El correctivo (C) costó 3,6 veces la fase A.** Su implementador repartió el trabajo en 49 subagentes Opus (941,50 USD), y el coordinador lanzó 93 subagentes de review o auditoría.

### 2.3 Eventos y límites de la app

| Medida | Valor | Fuente |
|---|---|---|
| Turnos del coordinador por origen | 76 fines de turno de sesiones, 63 avisos de subagente o tarea, 16 mensajes de otras sesiones y unos 45 mensajes escritos por la persona (19 en A y ~26 en C) | `scripts/fase4a-coordinator.py` |
| Compactaciones del coordinador | 12 (6 en A, 6 en B y C). Ninguna perdió el estado: cada evento releía `state.json` | idem; [retro §4] |
| Llamadas a `start_session` | 14: 10 sesiones arrancadas directamente y 1 por tarjeta (P5, 1 h 17 min de espera), con 3 rechazos | idem |
| Rechazos de arranque | P1, por `cwd` en un turno automático; P5, porque el turno lo abrió el mensaje de otra sesión; y una tarjeta el 05-11, con Remote Control | idem; [dec:78, 113, 118, 134] |
| Mensajes a otras sesiones | 77, de ellos 7 respondidos «queued» | idem |
| Despertares perdidos | 2 en A (P6, 59 min; P7, 48 min) [retro §4]. En C, el implementador se paró sin avisar el 03-11 y el 04-11, ~4 h 30 min sin resultado [dec:124]; y un «Q2 r3 listo» no llegó como mensaje [dec:104] | |
| Contadores de 0.3 | `messagesSinceUser` y `wakesSinceUser` en 0 al final, con `lastSentAt` desfasado: no se llevaron | [state]; [retro §4] |
| Arranques imposibles que pasaron a subagentes | Q5 [dec:113], la QA por Codex [dec:118] y la review final de 10 lotes [dec:134], porque esos turnos los abrió otra sesión | |

### 2.4 Tamaño de las PR en cada entrega (`git diff --shortstat`, solo lectura)

| Entrega | Backend | Frontend | Raíz |
|---|---|---|---|
| 1.ª, 31-10 03:18 (`a39e5005` / `778fdc7` / `a75e0123`) | 310 archivos, +26.076 / −179 | 28 | 110 |
| 2.ª, 31-10 07:30 (`c796e3ad` / `b94a536`) | 313 | 28 | — |
| 3.ª, 05-11 13:00 (`29a71262`) | 1.732, +67.623 / −10.058 | — | — |
| 4.ª, 07-11 16:30 (`ddf3b2cd` / `52620426` / `539d9dfb`) | 1.922, +72.867 / −11.150 | 154 | 99 |

El dueño preguntó el 05-11 a las 10:14 por qué había 1.600 archivos (transcript del coordinador). Ninguna fila de `decisions.md` avisa del crecimiento antes de esa pregunta.

### 2.5 Revisión

- **Fase A:**
  - 31 reviews de parte, 13 de ellas NO, y 15 Critic;
  - P7 sola acumuló 17 rondas de review y 7 de Critic [state; retro §2].
- **Revisiones frescas, de la B en adelante:**
  - 2 reviews frescas de PR, que encontraron 3 P2 y 5 P3 [dec:71];
  - una auditoría por archivo de 11 lotes sobre 1.550 archivos de backend, 92 de frontend y 97 de raíz: 0 🔴, 25 🟠 y ~110 🟡 [dec:119];
  - 6 reviews de delta del cierre final: 2 🟠 y 32 🟡 [dec:122];
  - 3 reviews del delta r2: 7 🟡 [dec:126];
  - la review final de 10 lotes sobre 1.946 archivos: 12 🟠 y 91 🟡 [dec:135];
  - la review del delta r6, sobre 632 archivos: 2 🟠 y 31 🟡 [dec:139].
- **Rondas del correctivo:**
  - 6 rondas de review para Q0 (los detectores), con rendimientos decrecientes [dec:87];
  - 3 para Q1 y 4 para Q2;
  - además Q3, Q3c, Q4 y Q5, y los cierres r2 a r7.
- **QA de navegador:** 4 rondas con otro agente (Codex) [dec:119–129]. Las rondas 1 a 3 no valieron como evidencia: la 1 se paró, la 2 corrió con el árbol en movimiento y la 3 quedó incompleta.

## 2.6 Lo que hizo la persona

- 10 pulsaciones registradas en `presses` hasta el 29-10 [state]. La retro cuenta 27 intervenciones en la fase A, contando los botones [retro §1].
- En la fase C, unos 26 mensajes escritos. Entre ellos:
  - la revisión de las PR que abrió el correctivo [dec:77];
  - tres decisiones sobre los hooks de commit [dec:79, 82, 92];
  - las expansiones de baseline [dec:81];
  - 4 aprobaciones de recrear contenedores dentro de la sesión del implementador [dec:99, 102, 105, 108];
  - despertar al implementador [dec:124];
  - una segunda revisión de la PR con 3 puntos, 2 de ellos reales [dec:133];
  - «review y reentrega» [dec:138];
  - el aviso de la CI roja [dec:142];
  - el merge [dec:144].
- **Dos delegaciones amplias:** «hasta el lunes» [state `authority.delegated`] y «aprueba la recomendada» [dec:92]. Con ellas, el coordinador tomó la mayoría de decisiones de la fase C («coordinator, within authority», [dec:121–130]).

## 3. Qué funcionó

1. **Una sesión por parte con el modelo aprobado.** Las 9 partes de A arrancaron con su fila. La tarjeta de P5 conservó el modelo y el esfuerzo de su fila [retro §4, D-60].
2. **Verificar en vez de creer el informe (D4).** Cada `done` y cada «listo» del correctivo se comprobó en los tres repos, con commits, árboles limpios y gates repetidos en el HEAD [dec:108, 110, 121, 125, 128, 130, 134, 137, 140]. El coordinador también comprobó a mano filas del inventario de las reviews [dec:135].
3. **Entrega por hooks del repo.** `task-pr.ps1`, el snapshot de submódulos y el manifiesto funcionaron en las 4 entregas, cada una verificada con `gh pr view` (heads, MERGEABLE y sin auto-merge) [dec:75, 131, 141].
4. **Autoridad y delegación:**
   - las delegaciones quedaron con las palabras literales;
   - nada se saltó una denegación de seguridad: ni el `--no-verify` reenviado ni la recreación de contenedores, que se dejaron para la persona [dec:92, 94];
   - los borrados irreversibles se escalaron [dec:125, 132];
   - el merge siempre fue de la persona.
5. **Las compactaciones no rompieron nada.** El coordinador se compactó 12 veces y siguió desde `state.json` y `decisions.md`.
6. **El coste del coordinador** se quedó bajo, un 4,5 % del total, frente al temor del laboratorio, donde era el 82 %.

## 4. Qué falló, con evidencia

| # | Fallo | Evidencia | Impacto |
|---|---|---|---|
| F1 | **La revisión por parte no aplica las reglas del repo ni cubre la PR.** El perfil declara `repos[].reviewSkills`, pero el reviewer de baton no las cargó, y ninguna review tuvo el inventario por archivo que la skill del repo hace obligatorio. Se revisaba el diff de la parte contra su aceptación, y las rondas tardías se anclaban al delta anterior | [dec:77]; [retro, añadido 31-10] | 9 defectos de diseño pasaron 17 reviews, 7 Critic y 2 reviews frescas; dio lugar a la fase C (2.344 USD) |
| F2 | **La PR creció sin avisar.** El backend pasó de 313 a 1.922 archivos: detectores nuevos, baseline y refactors de deuda anterior que tocan archivos fuera del plan [dec:101] | tabla 2.4; la pregunta del dueño el 05-11 a las 10:14 | El dueño lo descubrió solo; una PR de 1.900 archivos es difícil de revisar |
| F3 | **Gates verdes que se saltaban tests.** Los tests SQL de Identity están condicionados a una variable de entorno: en local salían como «skipped by design» (+78) y nadie los contó como no ejecutados | [dec:104 «514 + 78 skipped by design»; dec:142] | CI roja tras la 4.ª entrega y otra ronda de arreglo |
| F4 | **El correctivo, fuera del modelo de baton.** baton 0.3 no tiene «reabrir» ni partes dinámicas. Hubo ~20 briefs a mano (`brief-Q*`, `brief-cierre-*`); las rondas y los hallazgos se llevaron solo en `decisions.md`, y `state.json` siguió en `running` con `current: P7` | [state]; lista de archivos del run | Sin contadores, sin informe por bloque y sin `findings.jsonl` de la fase C |
| F5 | **El implementador corrió dentro del chat coordinador.** Fue un subagente en proceso, porque el turno no podía arrancar una sesión. La persona lo rechazó y la app lo mató a mitad de Q0 | [dec:78]; 75,11 USD en «implementador en proceso» | Trabajo a medias y un cambio de sesión |
| F6 | **Turnos que no pueden arrancar sesiones.** Les pasa a los turnos abiertos por otra sesión, por un subagente o por Remote Control. La app no deja ni proponer tarjeta con Remote Control | [dec:113, 118, 134]; coordinador 05-11 09:59; demo `orders-service` del 02-11 | Reviews y QA como subagentes del coordinador, que engordan su contexto con 63 avisos de tarea |
| F7 | **Despertares y paradas silenciosas.** Hubo 2 despertares perdidos en A. En C, un implementador se quedó parado unas 4 h 30 min sin resultado, y otro se paró por el límite semanal. Algunos «listo» solo llegaron porque la sesión mandó un mensaje | [retro §4; dec:97, 104, 124] | Horas perdidas; la persona tuvo que preguntar «¿cómo va?» |
| F8 | **Contadores, `presses` y modelo real sin mantener.** El modelo aprobado de P7 se sobrescribió en el estado | [state; retro §7 F5, F13] | Los límites de 9 no protegieron nada; la traza tuvo que salir de los transcripts |
| F9 | **El modelo de las partes de cierre.** CA y P7 se aprobaron en Sonnet e hicieron trabajo de Opus: 24 commits de lógica en P7 y 4 Critic FAIL seguidas antes de subir | [retro §7 F8; state P7 `implementer`] | P7 costó 190 USD solo en la fase A |
| F10 | **Herramienta en `@latest`.** GitNexus en `@latest` cambió el formato del índice (42 frente a 41) y dio radios CRITICAL falsos | [dec:137] | Ruido en el análisis de impacto y deuda de herramientas |
| F11 | **Requisitos humanos descubiertos tarde.** La GitHub App y el login de Claude Code, con unas 9 h de espera entre los dos | [retro §5] | Esperas largas en A |
| F12 | **Decisiones del coordinador sin comprobar convenciones.** Ordenó un detector deformante [dec:84] y una ubicación de puertos equivocada que luego señaló el dueño [dec:133] | | Rondas extra; la review fresca lo cazó en un caso |
| F13 | **Fallos de la app vistos en la demo del 02-11.** Faltó el despertar tras un `wake_when_done` confirmado; Remote Control rechazó arranques y tarjetas; la ruta con `/` se rechaza siempre en Windows | memoria `baton-0-4-backlog`; transcripts de `baton-demo` | Run parado tras P1 |

## 5. Las preguntas abiertas de 0.3

- **D-59: ¿cuenta `start_session` en la cuota de 10 mensajes?** No se puede medir con estos datos. No hubo ningún rechazo por cuota: la racha máxima sin palabra de la persona fue de 9 turnos [retro §4], y los contadores de baton no se llevaron.
- **D-60: ¿conserva la tarjeta el modelo con que se propuso?** Sí, en el único caso: P5 arrancó con opus/medium, como su fila, aunque con otro nombre de sesión [retro §4].
- **D-62: ¿qué rompe la cadena de turnos automáticos?**
  - Un turno abierto por **el mensaje de otra sesión** no puede arrancar sesiones; el texto de la app lo dice explícitamente [P5, 13:43 del 28-10].
  - Con **Remote Control**, la app no deja arrancar sesiones ni proponer tarjetas [05-11 09:59; demo 02-11].
  - **Las compactaciones no la rompen** (12 sin incidencias).
  - Los **despertares perdidos** existen, pero su causa no se puede medir. Dos de los tres casos siguieron a un turno abierto por otra sesión [retro §4].

## 6. Propuestas para 0.4, por prioridad

| # | Propuesta | Cambia | Evidencia | Cómo probarla |
|---|---|---|---|---|
| 1 | **La revisión aplica las reglas del repo y prueba que las aplicó:** <ul><li>el reviewer carga siempre `repos[].reviewSkills` de los repos de la parte y abre con un inventario por archivo (`N_alcance = N_revisados`, un dato concreto por fila);</li><li>el coordinador rechaza una review sin inventario o con números que no cuadran, y comprueba filas al azar;</li><li>no se revisa solo el delta: cada ronda revisa los archivos de la parte en su HEAD.</li></ul> | `agents/reviewer.md`, `prompts/implementer.md` (bucle de review), `skills/event` (verificación D4), D-58 | F1 | Sonda: una parte con un defecto que solo detecta la checklist de la skill del repo; la review r1 debe marcarlo y llevar inventario |
| 2 | **Review final de PR por repo antes de entregar:** fresca, por lotes, con la skill del repo y otro modelo si el perfil lo pide. Es `closing.freshReviewPerRepo` de D12, que pasa de 0.5 a 0.4 | `skills/event/deliver.md`, D12 | F1; las reviews frescas y la auditoría encontraron 25 🟠 tras 50 reviews de parte | Sonda en el laboratorio multi-repo: entrega con un defecto que cruza partes |
| 3 | **Vigilar el tamaño de la entrega:** <ul><li>`state.delivery.size` por repo en cada entrega (archivos y líneas);</li><li>aviso a la persona con push y pregunta cuando crece más de un umbral del perfil (por defecto ×1,5 o +200 archivos) frente a la entrega anterior o al alcance del plan;</li><li>el informe da el desglose: src, tests, detectores y baseline, docs.</li></ul> | `skills/event/deliver.md`, `templates/report.md`, filas de `supervisor.md` («scope») | F2 | Sonda: reentrega con un crecimiento de 4×; debe preguntar antes de publicar |
| 4 | **Gates honestos:** <ul><li>cada gate informa de los tests ejecutados, saltados y condicionados;</li><li>un salto por variable de entorno o por categoría cuenta como «no ejecutado», no como verde;</li><li>el perfil puede declarar `gates[].requiresEnv`;</li><li>antes de cada reentrega, el gate equivalente a la CI del repo (parte de `localCi` de D13, adelantado).</li></ul> | `agents/reviewer.md`, `templates/baton.json`, D9 y D13 | F3 | Sonda: un test con `[Skip]` por variable; la review debe pedir ejecutarlo o declararlo |
| 5 | **Correctivos y reaperturas en el estado:** <ul><li>`status: reopened` y partes dinámicas (`FIX-<n>`, bloques como Q0–Q5) con su brief, sus rondas, sus hallazgos en `findings.jsonl` y su sitio en el informe;</li><li>«la persona revisó la PR y encontró X» es un evento con su propia ruta, no una nota en `decisions.md`.</li></ul> | `templates/state.json`, `skills/event`, `skills/status`, D12 | F4 | Sonda: tras la entrega, «he visto esto en la PR»; debe crear una parte FIX y llevarla hasta la reentrega |
| 6 | **Respaldo cuando no se puede arrancar una sesión:** <ol><li>`start_session`;</li><li>tarjeta;</li><li>con Remote Control o un turno ajeno, la parte se envía por mensaje a la última sesión viva del run (como `per-plan`), con el modelo bajado si la fila lo pide;</li><li>nunca el implementador como subagente del coordinador sin el sí de la persona (fila nueva).</li></ol> Además, el `README` documenta que Remote Control no deja arrancar sesiones. | `skills/event` («The next part's session»), `prompts/supervisor.md` | F5, F6, F13 | Sonda: el turno siguiente lo abre el mensaje de otra sesión; debe usar el paso 3 |
| 7 | **Despertar de respaldo y detección de sesiones paradas:** <ul><li>el implementador manda su `baton-result` al coordinador por mensaje, y `/baton:event` descarta el duplicado;</li><li>`/baton:status` y cada palabra de la persona revisan las sesiones `working` con `get_session`; una sesión en reposo sin resultado reciente se dice como «parada sin informe» y se reanuda con «sigue».</li></ul> | `prompts/implementer.md`, `skills/event`, `skills/status`, D10 | F7, F13 | Sonda: una sesión que termina sin bloque; el siguiente «¿cómo va?» debe detectarlo |
| 8 | **Un estado fiable:** contadores reales, `presses` completos y `implementer.approved` aparte de `actual`. `set_session_model` queda como herramienta de baton, solo con el sí de la persona o con una delegación de `spending`. El registro de hallazgos incluye las Critic | `skills/event`, `templates/state.json` | F8 | La sonda de límites de 0.3 repetida con cambio de modelo |
| 9 | **Modelo de las partes de cierre:** <ul><li>la propuesta pone Opus en una parte de cierre que arregla código, o la parte en dos («evidencia» y «arreglos»);</li><li>en el primer FAIL de Critic con un P2 en código nuevo, propone subir el modelo;</li><li>una Critic FAIL no gasta una ronda de review.</li></ul> | `prompts/models.md`, `prompts/implementer.md` | F9 | Sonda de propuesta sobre un plan con una parte «Cierre» |
| 10 | **Requisitos previos a la vista:** el perfil o el plan lista requisitos humanos (logins, apps de GitHub, variables del sistema) y la propuesta los comprueba o los pregunta antes del sí | `skills/run` (propuesta), `templates/baton.json` | F11 | Sonda: un requisito sin cumplir sale en la tabla |
| 11 | **Versiones fijadas:** `/baton:setup` y la revisión de la propuesta marcan `@latest` en hooks y gates como riesgo y piden fijar la versión | `skills/setup/detect.md`, `agents/reviewer.md` | F10 | Perfil con `npx x@latest`: aviso |
| 12 | **Traza para analizar:** `runDir/events.jsonl` con una línea por evento (hora, origen del turno, parte, decisión, contadores, arranque o tarjeta) y, al entregar, el uso por sesión con `get_usage`. Este análisis tuvo que reconstruirlo todo de 1,1 GB de transcripts | `skills/event`, `templates/report.md` | todo este documento | El informe de una sonda incluye el coste por papel sin scripts |
| 13 | **Windows y app:** `cwd` con la ruta nativa (`\`), y el `README` con los límites vistos: Remote Control, turnos ajenos y mensajes «queued» que hay que comprobar en el evento siguiente | `skills/event`, `README.md` | F13; 7 mensajes «queued» | Sonda de arranque en Windows sin reintento |

**Orden recomendado para el plan de 0.4:**
1. Las propuestas 1–4 (calidad de lo que se entrega). Atacan la causa del correctivo, que es el 77 % del coste.
2. Las 5–8 (que baton lleve el correctivo y la mecánica).
3. Las 9–13.

## 7. Qué no se pudo medir

- El coste real pagado: hay suscripción, y los USD son equivalentes de API.
- La causa de los despertares perdidos, como ya ocurría en la retro.
- Las sesiones de QA de Codex: no tienen transcript de Claude, solo sus salidas en `audit-pr/final/qa-*`.
- La parte de las 12 compactaciones atribuible a los avisos de subagentes de review. Hay una correlación de fechas en la fase C, pero no una prueba.
