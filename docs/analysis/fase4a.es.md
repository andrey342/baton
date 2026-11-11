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
  
  **Corrección del 2026-11-11:** la retro de `fase4a-fix` comprobó contra los `cost-state` de la app que la lectura de caché cuesta 0,05×, no 0,1×. Con 0,05× el run cuesta **2.002 USD**, en lugar de 3.062. El reparto apenas cambia: la fase A es el 20,6 % y lo de después de la primera entrega, el 79,4 %. Las tablas de abajo siguen con la fórmula antigua (0,1×). Para recalcularlas, cambia el factor en la línea 22 de `scripts/fase4a-cost.py`.
  La persona trabaja con suscripción (el implementador se paró por el límite semanal [dec:97]), así que los USD son **equivalente a precio de API**, no lo que se pagó. Con esta fórmula, la retro reproducía el coste que registró la app con un error del 1 %.
- **Tamaño de las PR:** `git diff --shortstat <baseSha> <head>` en cada repo, solo lectura.
- **Fases del run** usadas en las tablas:
  - **A:** del lanzamiento a la primera entrega, 2026-10-27T18:20Z → 2026-10-31T03:18Z;
  - **B:** los arreglos de las reviews frescas de PR, hasta 09:30Z del 31-oct;
  - **C:** el correctivo de calidad que pidió el dueño, del 31-oct 09:30Z al merge del 2026-11-07T21:19Z.

## 1. Resumen

- **El plan se entregó en 81 h y se mergeó a los 11 días.** Las 9 partes (P0–P7 y CA) se entregaron a las 80 h 58 min, con 3 PR y el snapshot verificado [state]. El dueño revisó las PR y encontró 9 defectos de diseño y estructura que ninguna de las 50 reviews había marcado [dec:77]. De ahí salió un correctivo de 7 días y 18 h, con un implementador nuevo, y el merge llegó el 2026-11-07 a las 21:19 [dec:144].
- **El 79 % del coste fue después de la primera entrega.** Del total de ~3.062 USD, 648 USD corresponden a la fase A, 71 USD a la B y 2.344 USD a la C (tabla 2.2). Con la tarifa de caché real de la app el total es ~2.002 USD, con el mismo reparto. Mientras baton daba el plan por terminado, el trabajo de calidad apenas había empezado.
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

### 6.1 Propuestas de la guía de modelos de Anthropic

Las propuestas 14–17 no salen del run. Salen de contrastar baton, el 2026-11-09, con la guía [«Which Claude model should you build with?»](https://claude.dev/blog/which-claude-model-should-you-build-with/) (claude.dev, Addy Osmani, 2026-11-09), citada abajo como **[guía]**. Las cifras del run que usan son las de este documento.

En lo esencial, baton ya sigue la guía, así que estas propuestas no cambian el diseño:
- elige modelo y esfuerzo por papel y por parte, y la persona lo aprueba;
- empieza en `medium` y deja `xhigh`/`max` para cuando el plan los pide;
- cambia de modelo en un corte natural, con una sesión nueva por parte que arranca de un brief escrito; la caché pertenece al modelo que la escribió [guía];
- usa Sonnet medium para las reviews repetidas;
- deja Haiku para trabajo cuya salida prueba una gate.

| # | Propuesta | Cambia | Evidencia | Cómo probarla |
|---|---|---|---|---|
| 14 | **Modelo de los subagentes del implementador:** <ul><li>baton trae un agente nuevo, `baton:explorer`: solo lectura (Read, Grep, Glob y shell de lectura), `model: haiku`, para buscar en el repo, leer logs y resumir la salida de los tests;</li><li>`implementer.md` manda usarlo en lugar del `Explore` integrado, que corre en el modelo de la sesión y no en Haiku [guía];</li><li>los subagentes que editan código o deciden siguen en el modelo de la parte. Usar `sonnet` en bloques de edición en paralelo (el patrón líder y trabajadores de la [guía]) es una opción que la tabla puede proponer y la persona aprueba. Nunca es un defecto, y antes hay que medirla en una sonda;</li><li>el informe da aparte el coste de los subagentes del implementador (con la propuesta 12).</li></ul> | `agents/explorer.md` (nuevo), `prompts/implementer.md`, `templates/brief.md`, `prompts/models.md` | La fila «Subagentes de trabajo de los implementadores» es la más cara del run: 969,24 USD, el 31,6 % (tabla 2.2). Según los `.meta.json` del archivo, sin contar reviews ni Critic, hubo 48 subagentes `general-purpose`, 16 `Explore` y 1 fork en `claude-opus-5-5`, frente a 1 `general-purpose` y 5 `Explore` en Sonnet. La [guía] reserva los modelos pequeños para tareas en las que un error se ve barato, y deja las ediciones en el modelo principal | Sonda: una parte en Opus que obliga a buscar en el repo. El transcript del subagente de búsqueda debe estar en `claude-haiku-5-5`, y el de edición, en el modelo de la parte |
| 15 | **Fable y el orden de escalado en `models.md`:** <ul><li>Fable 5.2 (`fable`) entra en la lista de modelos con su precio: 8/40 USD por millón de tokens, con la lectura de caché a 0,20 USD, como Opus [guía]. El id exacto se confirma en una sonda;</li><li>punto de partida: una parte de riesgo alto, diseño abierto y tamaño L (un refactor grande, una migración). Y, en vez de proponer Opus en `xhigh` o `max`, la tabla ofrece Fable en `high`;</li><li>el techo de D-45 sigue: un implementador en Fable necesita un coordinador en Fable, y la tabla lo marca. El reviewer y la Critic no tienen techo (D-61), así que la Critic es el primer sitio donde probarlo;</li><li>«While the plan runs» pasa a tener orden. Cuando una parte sale más difícil que su fila: 1) autoverificación, un gate o test que pruebe el criterio que falla; 2) un nivel más de esfuerzo; 3) el modelo siguiente, con menos esfuerzo que el que tenía. Cada subida sigue siendo Spending.</li></ul> | `prompts/models.md`, D-63 | F9: P7 en Sonnet llegó a 4 FAIL seguidos de la Critic antes de subir. Según la [guía], en FrontierCode 2.0 Fable 5.2 en `high` puntuó como Opus 5.5 en `max` con un coste por tarea de la mitad, más o menos. Completa la propuesta 9 | Sonda de propuesta sobre un plan con una migración grande: la tabla ofrece Fable en `high`, con la marca del techo si el chat no es Fable |
| 16 | **Esfuerzo de partida coherente:** `models.start.implementer.effort` de la plantilla del perfil pasa de `high` a `medium`, como ya dice `models.md`; `modes.thorough` sigue en `high`. La propuesta sube a `high` cuando la parte es larga o su aceptación es sutil, como ya hace | `templates/baton.json` | La plantilla dice `high` y `models.md`, «`medium` by default». Según la [guía], en SWE-bench Pro Opus 5.5 en `medium` sacó unos 2,5 puntos menos que en `high` con un ~70 % del coste | Sonda: perfil nuevo; las partes sin evidencia de dificultad salen en `medium` |
| 17 | **Precios al día:** <ul><li>el peso de `models.md` tiene en cuenta el tramo de Haiku 5.5: por encima de 100K tokens cuesta 0,50/2,50 USD, cinco veces más. Factor 0,05 para partes S y 0,25 para M y L, que pasan de 100K. Y Fable entra con factor 4;</li><li>`scripts/fase4a-cost.py` usa Haiku a 0,10/0,50 USD (y su tramo) y Fable a 8/40 USD, en vez de Haiku 4.5 a 1/5 y Fable como Opus. Se vuelve a ejecutar y se corrigen la tabla 2.2 y «Fuentes y método» si cambian.</li></ul> | `prompts/models.md`, D-63, `docs/analysis/scripts/fase4a-cost.py` | Línea 8 del script; [guía], tabla de precios. La review extra con Fable de P7 está infravalorada a la mitad | Ejecutar el script otra vez; la diferencia queda escrita en «Fuentes y método» |

Lo que la [guía] trae y no se propone:
- **Reviews en `low` que repiten en `high` solo las que fallan.** La guía lo da para resultados que se comprueban solos. En este run las reviews dejaron pasar defectos de diseño (F1), y bajar su esfuerzo iría en contra de las propuestas 1–4.
- **La herramienta advisor y el alias `opusplan`.** La propia guía dice que no mejoran con claridad al ejecutor solo.

### 6.2 Lo que añade el run `fase4a-p7b`

El 2026-11-10 llegó la retro del run siguiente de MSG: `C:/MSG/.claude/runs/_baton-trazas/retro-fase4a-p7b.md`, citada abajo como **[p7b §N]**. Fue un run más pequeño:
- 5 partes de documentación y uso real, con una PR mergeada;
- 3 intervenciones de la persona, unos 119 USD y 0 compactaciones;
- 45 h 37 min de run, el 72 % esperando a la persona.

Confirma, con casos nuevos, las propuestas 1, 2, 7, 8 y 13:
- **Inventario:** 0 de las 10 reviews de baton lo llevaban, y ninguna se rechazó [p7b §7 F10].
- **Despertares:** U1 no despertó al coordinador, R lo hizo 6 h 40 min tarde y P7b, ≥ 56 min tarde [p7b §8.2].
- **Estado:** el estado y los hallazgos quedaron sin llevar, con 0 de 33 hallazgos en `findings.jsonl` [p7b F6, F11].
- **`cwd`:** 2 de 7 arranques se rechazaron por el `cwd` [p7b F2].

Las propuestas 18–21 son nuevas.

| # | Propuesta | Cambia | Evidencia | Cómo probarla |
|---|---|---|---|---|
| 18 | **El esfuerzo aprobado tiene que aplicarse desde el primer turno.** `start_session` arranca como mucho al esfuerzo del chat, y `set_session_effort` solo vale desde el turno siguiente, así que una parte que lo hace todo en un turno corre por debajo de su fila. Hay dos opciones: <ul><li>la propuesta pide que el coordinador corra al esfuerzo máximo de la tabla, y si no, marca la fila («correrá a medium»);</li><li>el arranque manda primero un turno corto y luego el trabajo.</li></ul> El estado guarda el esfuerzo real, leído de `get_session`, junto al aprobado (con la propuesta 8) | `skills/run` (propuesta), `skills/event` («The next part's session»), `prompts/models.md` («The ceiling») | U1, U2 y R, aprobadas en `high`, corrieron en `medium`, según el `output_config.effort` de sus transcripts [p7b §8.1, F5] | Sonda: chat en `medium` y una parte `high` de un solo turno. La tabla avisa, y el transcript de la parte muestra `high` con la opción elegida |
| 19 | **Regla de parada de la review final (completa la propuesta 2):** <ul><li>los 🟠 bloquean y abren otra ronda;</li><li>los 🟡 se arreglan una sola vez dentro de la ronda en curso y no abren una nueva;</li><li>si tras 2 rondas siguen apareciendo 🟠, se escala a la persona;</li><li>el brief de la review parte de los ejes que el plan declara (por ejemplo, «precondiciones reproducibles desde una organización vacía»), no de una lectura libre;</li><li>las gates largas corren dentro de la sesión del correctivo, no como turnos automáticos del coordinador.</li></ul> | `skills/event/deliver.md`, `prompts/supervisor.md`, `templates/baton.json` (`roles.finalReview`) | 4 rondas frescas fuera de baton (1🟠+6🟡 → 1🟠+4🟡 → 2🟠+3🟡 → 0🟠+7🟡): ≈ 47 USD, el 39 % del run, y 12 turnos automáticos en 77 min. Los 🟠 eran precondiciones imposibles de reproducir, y los cerró una sola instrucción de reverificarlas [p7b F8, F9] | Sonda: una entrega con 🟡 que reaparecen; la segunda ronda no abre una tercera |
| 20 | **El estado se escribe con una herramienta, no a mano:** <ul><li>un script (`scripts/state-apply`) aplica un evento al `state.json`: `rounds`, `endSha`, `verified`, `presses`, contadores y `lastSentAt`;</li><li>la hora sale siempre de `date -u`, y se rechazan las filas con una hora futura (completa la propuesta 8).</li></ul> | `skills/event` §3, `templates/state.json`, `scripts/` nuevo | La última parte quedó sin `endSha`, `rounds` ni `verified`, tras 42 `Edit` sueltos. Hubo filas de `decisions.md` con horas redondas inventadas y dos escritas en el futuro, a las 21:40 y 21:45 cuando eran las 21:34 [p7b F6, F7] | Sonda: un evento aplicado con el script deja el estado completo; una fila con hora futura se rechaza |
| 21 | **Sin turnos vacíos:** <ul><li>el implementador espera al reviewer en primer plano y no arma `Monitor` sobre él;</li><li>ante un fin de turno sin `baton-result`, el coordinador contesta sin abrir lecturas;</li><li>en cada evento, el coordinador reconcilia con `list_sessions {linked:true}`: una sesión cuya última actividad es posterior a lo ya verificado se trata como pendiente (completa la propuesta 7).</li></ul> | `prompts/implementer.md`, `skills/event` §1 | P7b abrió 2 turnos de `Monitor` después de su `done`. El primer fin de turno despertó al coordinador sin resultado y le costó 0,78 USD. El turno del coordinador quedó bloqueado 72 min y 7 h 18 min sin detectar las partes ya terminadas [p7b F1, F3] | Sonda: una parte termina con el reviewer en segundo plano; el coordinador no relee nada y el resultado llega en un solo evento |

Otras dos observaciones:
- **El límite real de turnos automáticos no coincide con el de baton:** hubo 12 turnos automáticos en 77 min sin que la app parara [p7b §8.8]. Pasa a las preguntas abiertas junto a D-59: hace falta una sonda que mida dónde corta la app antes de mantener el aviso a 8 y la parada a 9.
- **Fallos que se repiten de fase4a y son de la plantilla, no del run:**
  - en el texto del hook `deliver`, `-DryRun` va **con** `-ConfirmPush` y no en su lugar;
  - el modo auto deniega `bind_pr` en la entrega [p7b F13, F14].

  La plantilla de hooks y `deliver.md` tienen que corregirlo, o llamar a `bind_pr` solo cuando el perfil lo permita.

### 6.3 Lo que añade el run `fase4a-fix`

Es el correctivo de la 4a de MSG: 6 partes, una sesión por parte, mergeado el 2026-11-11. La fuente es el mensaje de su coordinador del 2026-11-11, con las filas `obs:` de `C:/MSG/.claude/runs/fase4a-fix/decisions.md`, citado como **[fix N]**. La retro llegará después, y sus cifras se añadirán aquí cuando llegue.

**Confirma:**
- **la 13:** `cwd` rechazado en un turno automático; sin `cwd` funciona porque el chat ya está en la carpeta [fix 1]. Pasa en los tres runs: hay que omitir `cwd` cuando coincide con la carpeta del coordinador;
- **la 20:** el estado se escribió entero con un script de Python, porque con Write o Edit era demasiado largo [fix 7];
- **la 21:** dos sesiones cerraron un turno de más después de que su `done` ya estuviera procesado, y cada uno gastó un despertar [fix 8]. `/baton:event` debe ignorar un resultado ya verificado sin contarlo;
- **la 1:** una cabecera de inventario mal sumada con filas correctas [fix 10a]. El coordinador tiene que contar las filas él mismo, no fiarse de la cabecera.

**Nuevas:**

| # | Propuesta | Cambia | Evidencia |
|---|---|---|---|
| 22 | **Buscar la tarjeta también por título:** la app nombra la sesión de una tarjeta a partir del título, no del `name`, así que «a card still waiting» la busca también por título. Mismo caso que P5 en fase4a (`baton-fase-4-etapa-4a-p5`) | `skills/event` («a card still waiting»), `skills/status` | [fix 2]; [retro §4] |
| 23 | **Origen de cada fila de autoridad:** `authority.alwaysAsk[]` lleva `from: profile|person`. Una fila de la persona («cada uso de Fable 5.2 pide un sí») la retiran sus propias palabras, y una del perfil no | `prompts/supervisor.md`, `templates/state.json` | [fix 3] |
| 24 | **El modelo exacto de reviewer y Critic:** la herramienta Agent solo acepta alias (`fable` puede dar la 5.1). Cuando la fila pide una versión concreta, baton la lanza con `claude -p --model <id>`, comprueba la línea `Model:` y suma su coste desde el JSON de la ejecución a `reviewer_usage` | `prompts/implementer.md`, `agents/reviewer.md`, `prompts/models.md` | [fix 4]: un Critic en `claude-fable-5-2` por `claude -p` costó 4,61 USD en 80 turnos, fuera de las cuentas de la sesión |
| 25 | **Aprobar la tabla de un `--dry-run`:** si la persona aprueba la tabla de un dry-run, el lanzamiento escribe el estado `proposed` aprobado en el mismo turno, en lugar de suponer que ya existía | `skills/run` (pasos 1 y 3) | [fix 5] |
| 26 | **El modelo de la primera ronda de la review final como opción:** la hoja o la propuesta pueden fijar un modelo para la primera ronda de la review final de la PR (con la 19), y así se puede medir un experimento («¿cierra Fable en una ronda?») | `templates/baton.json` (`roles.finalReview.firstRound`), la tabla de la propuesta | [fix 6]: no hubo dónde fijarlo. La auditoría tardó 4 rondas en Opus, con 🟠 12 → 4 → 1 → 0, la misma forma que en P7b |
| 27 | **El inventario de una auditoría por tandas:** cuando la review de una parte de cierre se apoya en una auditoría por tandas, el coordinador comprueba que la unión de las tandas cubre el diff exacto (lo hizo a mano: 137 = 137), y baton lo describe | `skills/event` (verificación), con la 1 y la 2 | [fix 10b] |
| 28 | **El informe filtra las filas `obs:`:** la tabla de decisiones lleva las decisiones y las escaladas, las `obs:` van aparte y resumidas, y enlaza a `decisions.md` entero | `templates/report.md`, `deliver.md` | [fix 11]: unas 45 filas |
| 29 | **La Critic por defecto en partes de backend con contrato público:** la tabla de la propuesta la pone y la persona puede quitarla | `prompts/models.md` | [fix, «lo que funcionó»]: en F4 y F5, la Critic encontró hallazgos, uno P2, tras dos reviews OK |

**La retro** (`C:/MSG/.claude/runs/_baton-trazas/retro-fase4a-fix.md`, archivo en `fase4a-fix-archivo/`), con la lectura de caché a 0,05×:

| Cifra | Valor |
|---|---|
| Partes | 6 en serie, con 17 rondas de reviewer y 6 de Critic, 1 replan (F4) y ningún reintento |
| Coste | 327,33 USD: coordinador 7,9 %, implementadores 58,8 %, reviewers 7,5 %, Critic 4,1 % y auditoría de la PR (F6) 21,2 % |
| Persona | 19 entradas: 10 del plan, 3 evitables y 2 en parte |
| A mano | ≥ 9 pasos del coordinador y entre 45 y 55 escrituras del estado |
| Cadena | aguantó 4 compactaciones y 9 h sin palabra de la persona |
| Despertares | duplicados o retenidos en F2, F3 y F6; el de F2 llegó 85 min tarde |
| Arranques | 2 de 8 rechazados por `cwd`; la tarjeta de F2 esperó 17 min |

El 56 % del coste del coordinador es reescritura de caché tras más de 1 h sin actividad.

La retro añade cuatro cosas a lo de arriba:

| # | Propuesta | Cambia | Evidencia |
|---|---|---|---|
| 30 | **Los P3 de documentación no gastan una ronda de review:** se corrigen dentro de la ronda siguiente o al entregar, como los 🟡 de la 19 | `prompts/implementer.md` (bucle de review) | 4 de los 8 NO del run fueron solo P3 de docs, y uno de ellos forzó el replan de F4. Mismo patrón que P7 en fase4a (informe al HEAD) |
| 31 | **Revisar la hoja antes de lanzar:** la propuesta señala criterios fuera del alcance y recoge las respuestas permanentes de la persona como delegaciones, antes de pedir el sí | `skills/run` (propuesta), con la 10 | retro de fase4a-fix |
| 32 | **El esfuerzo de un subagente lanzado por `claude -p`:** pasar `--effort` con la fila (con la 24) | `prompts/implementer.md` | La Critic en Fable por `claude -p` corrió en `medium`, aprobada en `high` |
| 33 | **El cierre deja la base al día:** tras el merge de la persona, `git pull --ff-only` en cada base al volver a ella, porque se queda atrasada | `skills/run/hooks.md` («The close») | retro de fase4a-fix |

También confirma, con más peso, las propuestas 13, 20 y 21 y el fallo de `bind_pr`, denegado ya en tres runs. La 13 gana un matiz: reintentar sin `cwd` antes de recurrir a la tarjeta.

**No es un fallo de baton:** las respuestas a sesiones ajenas al run cuentan para la cuota de mensajes [fix 9]. La app cuenta todos los envíos de un chat por cada palabra de la persona, y baton hace bien en contarlos. Lo que sí falta es lo de la propuesta 6: no atender sesiones ajenas en medio de una cadena de eventos.

### 6.4 Lo que añade el run `fase4a-limites`

Fuente: el mensaje de su coordinador del 2026-11-11 y la fila de las 22:11:41Z de `C:/MSG/.claude/runs/fase4a-limites/decisions.md`. El run seguía en curso cuando se escribió esto.

**Qué pasó:** la sesión de la parte L2 murió a mitad de turno (19:25:01Z) sin `baton-result`, y el coordinador no recibió ningún despertar. No se enteró hasta que la persona preguntó «¿cómo va?» a las 22:11, unas 2 h 45 min después. Se reanudó con «baton · continue part L2…».

**Causa, corregida por su coordinador el mismo día:** Claude Code se cayó en el PC por falta de memoria. La primera explicación (un script de tests en segundo plano que cerró el turno) no se sostiene, así que la propuesta 34 queda retirada.

**Por qué importa:** una sesión que muere en silencio no despierta a nadie, y nada en baton la detecta. Con las paradas silenciosas de fase4a (7) y los despertares perdidos de P7b (21), es el tercer caso de una parte parada sin que el coordinador lo sepa.

| # | Propuesta | Cambia | Evidencia |
|---|---|---|---|
| 34 | *Retirada:* prohibir `run_in_background` en la parte. La causa real fue una caída de Claude Code por memoria | — | — |
| 35 | **Vigilante de partes paradas o muertas:** <ul><li>en cada evento, en cada palabra de la persona y en `/baton:status`, una parte `working` cuya sesión está en reposo o no corre (`get_session`: `isRunning`) sin `result-<parte>.md` posterior a su último envío se dice como «parada sin resultado», y se le manda «continúa» una vez;</li><li>como el coordinador no puede sondear, se apoya en el despertar de respaldo de la 7 y en la reconciliación de la 21;</li><li>una rutina programada que haga esa comprobación cada N minutos queda como opción del perfil, con el sí de la persona.</li></ul> | `skills/event`, `skills/status`, con la 7 y la 21 | L2, y las paradas de fase4a (03-11 y 04-11) |

**Orden recomendado para el plan de 0.4:**
0. Una primera parte con los bugs de 0.3, que las dos retros piden como 0.3.1:
   - el `cwd` (13, ya visto en fase4a);
   - el esfuerzo del primer turno (18);
   - el despertar de respaldo y la reconciliación (7 y 21);
   - el estado con script y hora real (8 y 20);
   - los hallazgos completos;
   - el texto del hook `deliver`.

   Son cambios pequeños, y hacen fiable la medida de todo lo demás.
1. Las propuestas 1–4 (calidad de lo que se entrega), con la 19 dentro de la 2. Atacan la causa del correctivo, que es el 77 % del coste.
2. Las 5–8 (que baton lleve el correctivo y la mecánica).
3. Las 9–13. La 15 va con la 9, porque las dos tocan `models.md` y el modelo de las partes difíciles.
4. Las 14, 16 y 17: cambios pequeños de prompts, plantilla y precios. La 14 es la que más ahorra, porque su fila es la más cara del run.

## 7. Qué no se pudo medir

- El coste real pagado: hay suscripción, y los USD son equivalentes de API.
- La causa de los despertares perdidos, como ya ocurría en la retro.
- Las sesiones de QA de Codex: no tienen transcript de Claude, solo sus salidas en `audit-pr/final/qa-*`.
- La parte de las 12 compactaciones atribuible a los avisos de subagentes de review. Hay una correlación de fechas en la fase C, pero no una prueba.
