# baton 0.3: coordinación con una sesión por parte

Que baton haga solo lo que el coordinador de la Fase 3 de MSG hizo a mano: proponer los modelos y esperar el sí, abrir una sesión nueva por parte con el modelo aprobado, verificar en lugar de creerse el informe, trabajar en varios repos sobre el checkout real respetando los scripts del repo, aceptar delegaciones del usuario, pausar y retomar, y cerrar el plan. Tiene que servir en MSG (raíz y dos submódulos, Docker, GitNexus) y en cualquier repo de uno solo.

baton: mode=normal

Fuentes: `C:\MSG\.claude\runs\_plantilla-coordinacion\` (`PROMPT-COORDINADOR.md` y `ejemplo-fase3-*.md`), el run real `C:\MSG\.claude\runs\fase3-mcp\` (`decisions.md`, `result-*.md`) y los scripts de `C:\MSG\.agents\skills\msg-run-state\scripts\`.

## Ya decidido

- **Los modelos los decide el análisis y los aprueba el usuario.** Nunca son fijos ni van por defecto. El `mode=`, el `models=` del plan y los del perfil solo son el punto de partida de la propuesta. No hay manera de saltarse la aprobación.
- **Una sesión de implementador nueva por parte**, con su modelo y su esfuerzo. El coordinador no implementa.
- **El diseño de UI lo elige siempre el usuario.** Instalar software tampoco se delega por defecto. Las credenciales no se delegan nunca.
- **Siguen en pie:** sin código ni hooks propios en el plugin (D-11); nada destructivo (D-14); el estado vive en archivos (D-09); el implementador pregunta solo por su bloque de resultado (D-20); el revisor es un subagente fresco de solo lectura de la sesión de la parte (D-03), con `run_in_background: false` (D-55).
- **Prioridad para MSG:** sesiones (1), multi-repo (2), checkout (3), hooks (4), autoridad (5) y `--adapt` (6). Con eso, una fase de MSG se lanza con un solo `/baton:run`. Las mejoras 7–12 vienen después.
- **Las secciones D1 a D14 de este plan son el diseño.** Cuentan como decididas cuando el usuario apruebe el plan. Lo que la Fase 4 manual enseñe se incorpora en la pausa antes de la parte 1.

## 1. De dónde partimos

| Flujo de MSG | baton 0.2 | Qué cambia |
|---|---|---|
| A.0 Propuesta de modelos y sí del usuario | Modelos del perfil o de `mode=`, sin pregunta (D-07, D-08) | Paso obligatorio de propuesta, antes de crear nada (D2) |
| A.1 Coordinador que no implementa, con carpeta de run | Igual: `state.json`, `decisions.md`, `settled.md`, `brief.md`… | No hace falta `coordinator.md`: el protocolo son las skills. Lo propio del run (tabla aprobada, delegaciones) va en `state.json` y `settled.md` |
| A.2 Una sesión nueva por parte | Una sesión para todo el plan (D-02) | Una por parte (D3). El diseño B que D-02 descartó es viable ahora: la app deja arrancar sesiones en los avisos encadenados a un turno del usuario, y si se niega queda la tarjeta |
| A.3 Protocolo del implementador | Casi igual | Commits por repo, espera en primer plano, entrega solo con un mensaje `entrega`, pausas dentro de la parte (D3, D10) |
| A.4 Verificar, no creerse el informe | Solo commits y `Verdict: OK` | `git status` limpio por repo, gitlinks y estado real de las PR, y desviaciones con evidencia equivalente (D4) |
| A.5 Autoridad delegable | Tabla cerrada fija | `authority` en el perfil y delegación en tiempo de ejecución, con filas que no se delegan (D7) |
| A.6 Pausa y continuación | `stop` termina el run | Estado `paused` con un `pause-<P>.md` por sesión (D10) |
| A.7 Límites de la app | Contadores con parada en 9 y 10 | Aviso con push a 8 y tarjeta cuando la app no deja arrancar (D3, D10) |
| A.8 Recursos exclusivos | — | `resources` y `locks` (D11) |
| A.9 Cierre del plan | Entrega e informe | Fase `closing` configurable (D12) |
| A.10 CI sin minutos | — | `localCi` (D13) |

## 2. Lo que la app permite, y lo que hay que medir

Comprobado en las pruebas de baton y en la Fase 3:

- **Arrancar una sesión** solo se puede en un turno que escribe el usuario, o en un `<side-sessions-event>` encadenado a uno suyo, para un paso que el usuario pidió en su propia sesión y dentro del mismo proyecto.
  - En la Fase 3 funcionó con varios avisos seguidos sin mensaje del usuario entre medias: P1 se arrancó desde un aviso de P0, P2 desde uno de P1, y lo mismo CA, P4 y P5.
  - **Falla en un turno que despierta el fin de un comando en segundo plano** (una `task-notification`) o el mensaje de otra sesión. El texto: «Start sessions only on the user's own words to you here; this turn runs an automated event, another session's message, or the task another session gave you. Propose the session instead (initiation "own_initiative")…». Así se perdió el arranque de P3, que fue a tarjeta.
  - La tarjeta `own_initiative` la arranca el usuario con un clic. **No se puede editar**: para cambiar su brief hay que retirarla con `dismiss_task` y proponer otra.
- **10 mensajes** a otras sesiones por cada mensaje del usuario (D-33), y **10 despertares** seguidos sin una palabra suya (D-56).
- **Despertares por paquete en la Fase 3:** entre 2 y 5, salvo CA, que tuvo 9 o 10 porque los implementadores cerraban el turno para esperar un subagente o un build. Desde que se les pidió esperar en primer plano, bajaron mucho. Con 8 se pidió un «sigue» por push, y no se llegó al límite ni se perdió ningún aviso.
- **La app no arranca una sesión con un modelo más caro que el del chat**: ignora la petición. Si la tabla tiene implementadores Opus, el coordinador tiene que ser Opus.
- Al coordinador le llegan los primeros 400 caracteres del informe de la sesión, así que la primera línea del bloque de resultado tiene que bastar (D-18). El `summary` de CA en la Fase 3 ocupaba más de 2.000 caracteres.
- Los `deny` del repo se aplican en modo auto. Un subagente en primer plano no cierra el turno (D-55).

Sin medir todavía (la parte 1 lo mide con sondas, o lo apunta la Fase 4). El coordinador de la Fase 3 no tiene evidencia de ninguno:

1. Si `start_session` cuenta en la cuota de 10 mensajes. En la Fase 3 nunca hubo un rechazo por cuota, y el máximo fueron 3 mensajes seguidos.
2. Si la tarjeta `own_initiative` conserva `model` y `effort`. La de P3 se retiró sin arrancarla.
3. Si un subagente revisor `opus` lanzado desde una sesión Sonnet corre de verdad en Opus. Las revisiones no lo registran. Desde 0.3, el revisor escribe su modelo en la revisión (D4).
4. Si, además de `task-notification` y los mensajes de otra sesión, rompen la cadena de avisos el despertar número 10 o una compactación.
5. Qué pasa si el chat coordinador cambia (otro chat retoma el run): los avisos van al chat que arrancó la sesión.

**Consecuencia para el diseño:** el coordinador nunca lanza comandos en segundo plano. Un turno abierto por su fin no puede arrancar la parte siguiente. Lo largo lo hace una sesión, o se espera en primer plano.

## 3. Diseño

### D1. El run en tres momentos

```text
/baton:run plan.md ──▶ 1. PROPUESTA (turno del usuario)
                         preflight, lectura del plan, análisis por parte
                         tabla de modelos + opciones del run ──▶ status: proposed
usuario: «sí» ───────▶ 2. LANZAMIENTO (turno del usuario: puede arrancar sesiones)
                         hooks onStart, ramas por repo, brief, state
                         start_session de la primera parte ──▶ status: running
avisos ──────────────▶ 3. EVENTOS (/baton:event)
                         verificar → siguiente parte en una sesión NUEVA
                         · preguntas · pausas · entregas parciales
                         última parte ──▶ status: closing (D12) ──▶ delivered
```

La propuesta y el lanzamiento quedan en dos turnos del usuario. Así el sí del usuario es el turno en el que se arranca la primera sesión, y su texto (el botón «Sí, lanza cada parte en su sesión con esta tabla») pide de forma explícita una sesión por parte, que es lo que la app exige para arrancarlas después en los avisos.

### D2. La propuesta de modelos (mejora 1, A.0)

**Análisis.** El coordinador lee el plan entero y clasifica cada parte con evidencia del propio plan (cita la sección), según la rúbrica de un archivo nuevo, `prompts/models.md`:

- riesgo: seguridad, autorización, datos o migraciones, concurrencia, contrato público;
- dificultad: decisiones de diseño abiertas frente a pasos ya prescritos;
- tamaño: archivos y repos que toca;
- tipo: dominio, infraestructura, frontend con el diseño ya elegido, documentación, QA, preflight, cierre;
- coste de un error: lo que se pierde si sale mal y el revisor lo detecta tarde.

La rúbrica da puntos de partida, no reglas. Por ejemplo: riesgo alto y diseño abierto → Opus medium; mecánico o documental → Sonnet medium; revisor un escalón por encima en las partes de riesgo; Critic Opus high donde haya contrato o aceptación independiente. Los modelos son Opus 5.5, Sonnet 5.5 y Haiku 5.5, y los esfuerzos low, medium, high, xhigh y max.

**La tabla**, en el idioma del usuario, con una fila por parte y una para las sesiones del cierre si el perfil activa `closing`:

```text
| Parte | Implementador | Revisor (skills)                 | Critic    | Peso | Motivo |
| P0    | Sonnet medium | Opus medium (—)                  | —         | S    | Pasos prescritos por new-run.ps1; error barato |
| P1    | Opus medium   | Opus high (msg-back-review)      | —         | L    | Autorización OAuth: seguridad y contrato público (§7.1) |
| CA    | Sonnet high   | Opus medium (msg-back-review)    | Opus high | M    | Cierre mecánico, pero la aceptación independiente es de riesgo |
| Cierre: correctivos | Sonnet high | Opus high (por repo)         | —         | M    | Arreglos acotados por los hallazgos |
Coste relativo: P1–P3 son ~60 % del total; bajar P4 a Sonnet medium ahorra ~10 %, con el diseño ya elegido.
Coordinador: este chat (Opus 5.5). Necesita Opus, porque hay implementadores Opus.
Opciones del run: entrega pr en orden backend → frontend → raíz · publicar: preguntar una vez · archivar las sesiones verificadas: no
```

- El **peso** es relativo (S, M o L por tamaño, multiplicado por el modelo y el esfuerzo con la tabla oficial de precios). No es una cifra en USD.
- **Botones:** «Sí, lanza cada parte en su sesión con esta tabla» / «Quiero cambiar algo». Si el usuario pide cambios, se actualiza la tabla y se vuelve a preguntar (`proposal.revisions` + 1). Con `--dry-run` se enseña la tabla y no se crea nada.
- **Comprobación del techo:** `get_session` da el modelo de este chat. Si alguna fila pide un modelo más caro, la tabla lo dice y propone cambiar de chat o bajar esa fila. Nunca se lanza en silencio con un modelo distinto del aprobado.
- **Lo aprobado** se guarda en `state.parts[].implementer|reviewer|critic` (`model`, `effort`, `skills`, `reason`), junto con `proposal.approvedAt` y las palabras del usuario. `decisions.md` recibe una fila «tabla aprobada».
- **Durante el run:** al verificar una parte, si fue más difícil o más fácil de lo previsto, el coordinador propone cambiar las siguientes. Subir es gasto (fila Spending, se pregunta); bajar se dice en una línea y se apunta.

### D3. Una sesión por parte (mejora 1, A.2–A.3)

- **`start_session`** por parte, con:
  - `initiation: "user_asked"`, `context: "fresh"`, `wake_when_done: true`;
  - `cwd`: el checkout o el worktree (D5), y `use_worktree: false`;
  - `name: baton-<run>-<parte>`, que cabe en los 24 caracteres de la app (D-21) con el id del run cortado a 12;
  - `title: baton · <plan> · <parte>`;
  - el `model` y el `effort` de la fila aprobada.
- **El prompt** nombra la parte y sus commits de partida por repo: «Lee `implementer.md` y haz la parte P2 desde raíz `<sha>` · backend `<sha>` · frontend `<sha>`: lee y sigue `brief.md`.» El `background` dice qué partes están hechas y las notas de entorno vigentes.
- **Si la app se niega a arrancarla** (turno automático, cadena rota): se propone la misma sesión como tarjeta `own_initiative`, con `status: waiting` y `waiting.kind: "start"`, y se avisa con un push («P3 lista para arrancar: un clic en la tarjeta»).
  - El id de la tarjeta se guarda en `waiting.taskId`.
  - Si el usuario escribe antes de pulsarla, su turno sí puede arrancar: el coordinador retira la tarjeta con `dismiss_task` y arranca la sesión él mismo, como hizo la Fase 3 con P3.
  - Si hay que cambiar el brief, se retira la tarjeta y se propone otra.
  - Si la tarjeta no conserva el modelo (punto 2 de §2), el texto de la tarjeta lo dice y el coordinador lo comprueba con `get_session` al primer aviso.
- **Lo que pasa de una parte a otra** está en git, en los `result-<P>.md` y en el handoff del repo si existe (hook `beforePart`, D6). Una sesión que no es la primera empieza leyendo los resultados anteriores y `git log` desde sus commits de partida.
- **Los mensajes** (respuestas, reintentos, `entrega`) van siempre a la sesión de la parte en curso (`parts[].session.id`), nunca a la de una parte anterior.
- **Espera en primer plano**, como regla fija de `implementer.md` desde la primera parte: no se cierra el turno con trabajo en marcha (un build, unos tests, un subagente). Un comando largo puede correr en segundo plano, pero el turno lo espera. Cada cierre despierta al coordinador y gasta uno de sus 10 despertares: en la Fase 3, CA gastó 9 o 10 por no hacerlo.
- **`sessions: "per-plan"`** queda como opción del perfil, con el comportamiento de 0.2: una sola sesión y un solo modelo de implementador en la tabla.
- **Coste:** cada sesión nueva vuelve a pagar su arranque (el prompt de la app y las reglas del repo, en caché de escritura). A cambio, no arrastra contexto y puede usar el modelo justo. Se mide en la parte 9.

### D4. El coordinador verifica (mejora 1, A.4)

En la tanda de lecturas de cada aviso con `done`, para cada repo de la parte:

- `git -C <repo> log --oneline <startSha>..HEAD`: hay commits;
- `git -C <repo> status --porcelain`: limpio, salvo lo que git ignora;
- en la raíz con submódulos, si la parte hizo snapshot: `git -C <raíz> ls-tree HEAD <sub>` igual a `git -C <sub> rev-parse HEAD`;
- el Grep de veredictos de siempre, y el de `critic-<P>-r*.md` si la parte tiene Critic.

Tras una entrega, también `gh pr view <n> --json state,headRefOid,mergeable,body`:

- el `headRefOid` tiene que coincidir con el HEAD local;
- los SHA que cita el cuerpo tienen que existir en la rama y el último tiene que ser el HEAD. En la Fase 3, una revisión fresca encontró SHA falsos en los cuerpos.

La Fase 3 también dejó estas comprobaciones:

- **Revisiones literales.** La revisión se guarda tal cual: hubo resúmenes «abreviados». El coordinador comprueba que cada `review-*.md` tiene las secciones del revisor (`### Criteria` y `### Gates`). Si faltan, pide la revisión literal.
- **El modelo del revisor.** La segunda línea de cada revisión es `Model: <el modelo con el que corre>`. El coordinador la compara con el de la fila aprobada y apunta cualquier diferencia.
- **El Critic.** Si da FAIL y el implementador lo cierra, el Critic se vuelve a pasar (`critic-<P>-r2.md`) antes del `done`. Un FAIL cerrado sin segunda pasada no vale.
- **Rondas agotadas.** Si se agotan las rondas con NO, el coordinador lee los hallazgos abiertos y verifica él en el código si se pueden replanificar o refutar. Después decide como en 0.2: replanificar una vez o escalar.

Una **desviación de un gate** (en la Fase 3, LocalDB en lugar del contenedor, o 22/24 en Playwright con la comparación con la base) solo se acepta con evidencia equivalente en el resultado (campo `deviations:`). Se apunta en `decisions.md` y pasa al informe. Si falta la evidencia, se pide; si la desviación toca una fila del usuario, se escala.

El bloque de resultado pasa a la versión 2. Se sigue llamando `baton-result`, y el coordinador acepta también `coord-result`, para que un run manual y uno de baton se lean igual:

```baton-result
status: done | question | blocked | failed | paused
part: P2
summary: una o dos líneas (lo largo va en el cuerpo de result-P2.md, debajo del bloque)
commits: root <sha> <asunto>; backend <sha> <asunto>
gates: <comando> → <exit>; …
evidence: <gate> → <ruta TRX/log> (<exit>, <recuento>)      # gates que el revisor no ejecuta (D9)
deviations: <gate> → <qué se hizo en su lugar> · <evidencia>
reviews: r1 NO (3); r2 OK · critic r1 FAIL (2) cerrados
pause: P2.8                    # solo al pararse en una pausa del plan dentro de la parte
question: …
needs: human
pr: <url>; <url>               # solo tras una entrega
reason: …
```

### D5. Multi-repo y dónde se trabaja (mejoras 2 y 3)

**`repos`** en el perfil. Sin este bloque, hay un solo repo implícito `.`, como en 0.2.

- Cada repo tiene `name`, `path`, `base`, `rules` y `reviewSkills`.
- **Cada parte declara sus repos.** Puede hacerlo el plan (línea `**Repos:** backend, frontend`) o el análisis de la propuesta, y en ese caso los muestra la tabla.
- **Una rama por repo, con el mismo nombre.** `state.repos.<name>` guarda `branch`, `base` y `baseSha`, y cada parte guarda `startSha` y `endSha` por repo.
- **El revisor** recibe un commit de partida por repo y revisa el diff de cada uno (como el revisor de la Fase 3).
- **Entrega:**
  - `deliveryOrder` (`["backend","frontend","root"]`);
  - el `snapshot` de submódulos antes de entregar la raíz (en MSG, `task-commit.ps1 -Phase submodule-snapshot` y el manifiesto). Solo puede ir **después del push de los submódulos**: el script exige que sus SHA ya estén en el remoto, un índice vacío y `-ExpectedSubmoduleHeads`. El orden queda: push de backend → push de frontend → snapshot → raíz;
  - PR hermanas enlazadas: cada cuerpo termina con «PR hermanas: …», y si ya existían se les añade un comentario;
  - entregas parciales: una pausa del plan puede llevar `deliver: backend`, como la pausa A→B de la Fase 3.

**`workspace: "worktree" | "checkout"`.**

- **`checkout`** trabaja en la carpeta real, que es lo que necesitan Docker Compose (el nombre del proyecto sale de la carpeta), GitNexus y los MCP con rutas absolutas.
  - El run vive en `<checkout>/.claude/runs/<run>/`, y una sola carpeta hace de `runDir` y de `workerRunDir`.
  - Solo puede haber un run abierto por checkout, y las partes van en serie.
  - El preflight exige cada repo limpio, según `untrackedPolicy` (D6).
  - Si nadie más crea las ramas (D6), se crean con `git switch -c <rama> <base>` en cada repo; si la rama ya existe y es de este plan, con `git switch <rama>`.
  - Al cerrar, después del merge del usuario, se vuelve a la base (`onClose` o `git switch <base>`).
- **`worktree`** (por defecto) funciona como en 0.2.
  - Añade `worktreeSetup`, comandos que la primera parte ejecuta tras el `install`.
  - Añade `env`, por ejemplo `COMPOSE_PROJECT_NAME=<run>`. El brief lo pasa como instrucción, porque `start_session` no recibe variables de entorno.
  - `setup` avisa si detecta Compose, GitNexus o MCP con rutas absolutas y el perfil dice `worktree`.

### D6. Respetar el proceso del repo (mejora 4)

Los hooks son comandos o instrucciones del perfil con marcadores (`{{run}}`, `{{planSlug}}`, `{{yyyymmdd}}`, `{{repoRunId}}`, `{{branch}}`, `{{repo}}`, `{{repos}}`, `{{report}}`, `{{title}}`). Cada uno dice quién lo ejecuta: `by: "coordinator"` (rápido, menos de 2 minutos, en un turno del coordinador) o `by: "session"` (lo hace la sesión como paso escrito en el brief).

| Hook | Cuándo | MSG |
|---|---|---|
| `onStart` | Al lanzar, antes de la primera sesión | `new-run.ps1 -RunId {{repoRunId}} -Repos MSG,Backend,Frontend -PlanSlug {{planSlug}}`, por el coordinador. En la Fase 3: `-RunId 20261021-fase3-mcp-p1 -PlanSlug fase3-mcp-remoto` |
| `beforePart` | Primer paso de cada parte | «Lee `.agents/runs/{{repoRunId}}/handoff.md`», por la sesión |
| `afterPart` | Antes de la revisión de la parte | «Deja `handoff.md` al día (msg-run-state)», por la sesión |
| `snapshot` | Tras el push de los submódulos y antes de entregar la raíz | `task-commit.ps1 -RunId {{repoRunId}} -Repo MSG -Phase submodule-snapshot -Message … -Paths … -ExpectedSubmoduleHeads …`, por la sesión |
| `deliver` | Cada repo, en `deliveryOrder`, al recibir `entrega` | `task-pr.ps1 -RunId {{repoRunId}} -Repos {{repo}} -ConfirmPush -UpdateBody -ReportPath {{report}} -Title "{{title}}"`, por la sesión (la Fase 3 hizo antes un `-DryRun`) |
| `onClose` | Tras el merge del usuario | `complete-run.ps1 -RunId {{repoRunId}}`, por el coordinador. Exige que `handoff.md` diga «Veredicto: cerrado» o «bloqueado». Después, la vuelta a `develop` |
| `afterMerge` | Tras `onClose` | El bump de los gitlinks de la raíz a los commits mergeados de los submódulos. En la Fase 3 se hizo con un `git commit` a mano, porque `task-commit.ps1` exige un run abierto. Lo hace la sesión y su push es una publicación (D7) |

`{{repoRunId}}` es `{{yyyymmdd}}-{{run}}`, salvo que el perfil dé otro formato. En MSG tiene que cumplir `^[0-9]{8}-[a-z0-9][a-z0-9-]{1,62}$`.

- **`branch.createdBy`:** `baton` (por defecto), `hook` (lo hace `onStart`) o `part:P0` (lo hace la primera parte, como en la Fase 3). Con `hook` o `part:`, baton no crea ramas y comprueba después que existen en cada repo.
- **`untrackedPolicy`**, para lo que hay sin seguimiento en el checkout al lanzar:
  - `stop`: se para y se enumera;
  - `exclude-local`: se añade a `.git/info/exclude`, se apunta en `state.excluded` y se quita al cerrar. En la Fase 3 hizo falta excluir el propio plan para que `new-run.ps1` aceptara la raíz;
  - `ignore`.
- **Cuando hay `deliver`**, la entrega la hace una sesión (la de la última parte, o la de la parte de una entrega parcial) al recibir `baton · entrega: <repos>`, que es el único mensaje que la autoriza a hacer push o abrir una PR. Sin `deliver`, entrega el coordinador como en 0.2 (`deliver.md`).

### D7. Autoridad ajustable y delegable (mejora 5, A.5)

- **`supervisor.md`** mantiene su tabla cerrada y añade estas filas, que la Fase 3 escaló o echó en falta:

  | Fila | Por qué |
  |---|---|
  | Diseño de UI: elegir entre propuestas de diseño, pantallas o estilos | El usuario lo corrigió cuando se dio por delegado |
  | Instalar software | — |
  | Almacenes de credenciales del usuario | Una sesión listó el Administrador de credenciales de Windows |
  | Tomar el escritorio con computer use | El usuario tuvo que pedir una pausa |
  | El entorno de la máquina: Docker que no arranca, memoria del host | Necesitó al usuario |
  | Aceptar un gate rojo por motivos del entorno | Falta `pwsh`, organización sin GitHub App, Playwright. Solo con evidencia equivalente (D4) |

  Todas se escalan siempre, salvo que el perfil diga otra cosa. Las credenciales y sus almacenes no se delegan nunca.
- **Un plan que contradice decisiones anteriores del usuario** no es una escalada en marcha, sino una comprobación previa. La propuesta (D2) y `/baton:plan` comparan el plan con los `settled.md` y `decisions.md` de los runs anteriores del repo, y enseñan cada choque antes de pedir el sí. Pasó al planificar la Fase 4.
- **En el perfil:**
  - `authority.alwaysAsk` añade filas propias del repo, por ejemplo «recrear contenedores fuera de los pasos marcados»;
  - `authority.allow` quita filas delegables, por ejemplo `publish` en un repo cuyas reglas piden PR sin preguntar (lo que D-06 ya hace);
  - `authority.neverDelegate` lista las filas que no se delegan. Por defecto son `ui-design` e `install-software`, y `credentials` está siempre aunque el perfil no la nombre.
- **Delegación en tiempo de ejecución.** Si el usuario escribe, por ejemplo, «autorizo el reset de P2.8, la pausa A→B y push/PR; el diseño no», el coordinador:
  - lo divide en filas con su alcance;
  - rechaza en una línea las que no se pueden delegar;
  - escribe el resto en la sección `## Delegated by the person` de `settled.md`, con las palabras literales, y en `state.authority.delegated[]` (`row`, `scope`, `at`, `words`).
  
  Las decisiones que tome con esas filas se apuntan como `decided under delegation` y se resumen en la siguiente palabra del usuario. La delegación dura lo que el run. En la Fase 3 el usuario delegó «el coordinador decide, incluido el diseño de P4.0» y después lo corrigió: el diseño no se delega.
- **`humanBeforePublish`** acepta `false`, `true` o `"ask-once"`. Con `ask-once` hay una sola pregunta en la primera publicación, que enumera todo lo que el run va a publicar: los push en orden, las PR, sus cuerpos y los comentarios de CI local. El sí cubre esa lista. El merge nunca entra (`merge: "never"` en el perfil).

### D8. Formato de plan tolerante y `--adapt` (mejora 6)

- **`plan.partHeading`** en el perfil o `partHeading=` en la línea `baton:`: una expresión con el grupo `id`. Admite ids alfanuméricos (`P1`, `CA`, `P4fix`) y encabezados numerados («7.1 P1 — …»). Para MSG: `^(?:\d+(?:\.\d+)*\s+)?(?<id>P\d+|CA)\b`.
- **El título nunca cuenta como parte**: el único `#` de nivel 1 no lo es, aunque encaje con la expresión.
- **Aceptación en línea:** una línea «**Aceptación P1:** …» o «Aceptación: …» vale como criterio único, que el revisor desglosa.
- **`decided: §5, §13, §3.4`** en la línea `baton:`: esas secciones cuentan como «Ya decidido», junto con la sección de ese nombre si existe.
- **Pausas dentro de una parte:** «Parada antes de P2.8», «antes del reset de P2.8». Se guardan en `parts[].pauses[]` con su texto. El brief las pone en la parte como «para aquí con `status: question`, `pause: P2.8` y `needs: human`». El coordinador las trata como la fila «pausas del plan», delegables.
- **`/baton:plan --adapt <plan.md>`** no reescribe el plan, que en MSG es un documento versionado («v0.8 LISTO PARA IMPLEMENTAR»):
  - lo analiza con las reglas de arriba;
  - enseña lo que entiende: partes, repos, criterios, pausas, decisiones y entregas parciales;
  - pregunta lo dudoso y escribe el mapa en `.claude/runs/_maps/<plan>.json`, que está excluido de git;
  - `/baton:run` usa ese mapa si existe y si el hash del plan coincide;
  - opcionalmente, propone una línea `baton:` para el plan.

### D9. Gates y evidencias (mejora 7)

- **`gates`** puede ir por repo (`{ "backend": [...], "frontend": [...] }`). La parte usa los de sus repos y los que su texto escribe «exactamente como el plan los escribe».
- **Gates de evidencia** (`{ "run": "...", "by": "implementer", "evidence": "TRX|log" }`): son los que el revisor no puede o no debe ejecutar, como un E2E con la pila arrancada o la recreación de contenedores.
  - El implementador los ejecuta y deja la ruta, el exit y el recuento en `evidence:`.
  - El revisor comprueba que el archivo existe, que es posterior al último commit de la parte y que el recuento cuadra. No los vuelve a ejecutar.
- **`reviewer.neverRun`:** patrones que el revisor no ejecuta nunca, por ejemplo `docker compose up`, `down -v`, `git push` o un reset. Van al prompt del revisor.

### D10. Pausa, continuación y límites (mejora 9, A.6–A.7)

- **«para» o `/baton:status pause`:**
  1. `stop_session` en cada sesión del run que esté trabajando.
  2. A cada una, el mensaje `baton · pausa: guarda tu estado en pause-<P>.md (qué está hecho, qué está a medias, qué toca después), no uses computer use y termina con status: paused`.
  3. `status: paused`.
  
  Después de la palabra del usuario hay cuota para esos mensajes.
- **«continúa» o `/baton:status continue`:**
  - una sesión viva: `baton · continúa P<x> desde pause-<P>.md`;
  - una sesión que ya no existe: una nueva para la misma parte, con el mismo brief, `pause-<P>.md` y `beforePart`.
  
  `stop` sigue siendo el final del run.
- **Límites:**
  - a 8 mensajes o despertares, un push («baton necesitará una palabra tuya pronto»);
  - a 9, la parada con «Continuar» de 0.2.
  
  Las tarjetas de D3 cubren los turnos automáticos.
- **Otro chat retoma:** si el chat de `/baton:status continue` no es `state.coordinator.sessionId`, lo dice. La parte en curso no le despertará: se lee con «sigue». Desde la siguiente parte, este chat pasa a ser el coordinador (`coordinator.sessionId` se actualiza).
- **Archivar sesiones:** solo con el sí del usuario, que puede darlo en las opciones de la propuesta («archivar las sesiones verificadas») o al cerrar.
  - Si una sesión no se deja archivar, queda en `state.sessions[].archived: false` y se reintenta en el siguiente turno del coordinador. En la Fase 3, el archivado falló durante horas con «live work».
  - Tras el tercer intento fallido, se avisa al usuario en una línea con el enlace a la sesión.

### D11. Recursos exclusivos (mejora 10, A.8)

- **`resources`** en el perfil. Puede ser `{ "computer-use": "exclusive", "docker-stack": "exclusive", "playwright-profile": "exclusive", "browser": ["playwright", "builtin"] }`. En la Fase 3 hubo que serializar computer use, el perfil de Playwright y la pila Docker.
- **Cada sesión declara qué usa** (`uses`), en el plan, en el mapa o en el análisis.
- **El coordinador lleva `state.locks`:**
  - una sesión que pide un recurso exclusivo ocupado espera en `waiting.kind: "resource"`;
  - un recurso de tipo pool asigna un navegador distinto a cada sesión que corre a la vez, y lo escribe en su brief, con sus propias organizaciones o datos.
- **En 0.3** las partes van en serie, así que esto solo afecta al cierre (pruebas con clientes y QA).

### D12. El cierre del plan como fase de baton (mejora 8, A.9)

`closing` en el perfil activa los pasos, en este orden. Se lee de un archivo nuevo, `skills/event/close.md`, igual que hoy `deliver.md`.

1. **`deliver`:** la entrega en orden por repo (D5, D6).
2. **`freshReviewPerRepo`:**
   - un subagente revisor por PR, con las `reviewSkills` de su repo y el modelo de la fila «Cierre» de la tabla;
   - los hallazgos van con dónde, qué, por qué, cómo arreglarlo y con qué test, en `closing-review-<repo>.md`;
   - van a una sesión de correctivo (brief `brief-fix-<nombre>.md`), sin esperar al usuario si así lo pidió (delegado).
3. **`userReview`:**
   - el coordinador espera las observaciones del usuario;
   - analiza cada una en el código y decide el arreglo;
   - le explica el porqué en una línea por observación y lo manda en un brief de correctivo.
4. **`clientTests`:** una sesión por cliente (lista en el perfil o en el plan), con la evidencia en la carpeta del run.
5. **`qaMatrix`:**
   - el coordinador diseña `qa-matrix.md` a partir del plan y de los contratos (`contracts` en el perfil): flujos para conectar, usar, gestionar, ciclo de vida y seguridad;
   - una sesión con el control del PC la ejecuta (recurso exclusivo);
   - lo que falle va a un correctivo.
6. **`qaRound2`:** se repite la matriz entera.
7. **`shortReport`:** `report-short.md`, una fila por caso de uso con qué hizo el agente, el efecto en el sistema y el veredicto.
8. **Tras el merge del usuario:** `onClose`, `afterMerge` (el bump de los gitlinks), volver a la base y ofrecer archivar las sesiones.

Las sesiones del cierre (correctivos, clientes, QA) son partes dinámicas (`FIX-qa`, `CLI-cursor`) con su propio `result-*.md`, y tienen revisor si tocan código. Su modelo sale de la fila «Cierre» aprobada; si se sale de ella, se propone en una línea con su motivo.

### D13. CI local (mejora 11, A.10)

- **`localCi`:** `{ "workflows": [...], "when": "ciUnavailable" | "always", "comment": true }`.
- **Detección:** si tras la entrega `gh pr checks` falla en segundos con un error de facturación o sin ejecutores, como en la Fase 3, se marca `ciUnavailable`.
- **Réplica:** una sesión reproduce cada job (sus `run:` con los mismos comandos) sobre los HEAD publicados y devuelve una tabla job → comando → exit.
- **Publicación:** el comentario en cada PR cuenta como publicación (D7). Con `ask-once`, entra en la lista que el usuario autorizó.

### D14. Detección en `/baton:setup` (mejora 12)

- **Con `.gitmodules`:**
  - propone `repos`, con `base` sacada de las reglas, no de la `branch` de `.gitmodules`: en MSG dice master/main y se trabaja en `develop`;
  - lee las reglas de cada repo (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*.mdc`) y las junta.
- **Con Compose, `.gitnexus` o un `.mcp.json` con rutas absolutas:** propone `workspace: "checkout"` y explica por qué.
- **Con scripts de run, PR o cierre que las reglas o las skills del repo nombran**, como los de `msg-run-state`: propone los hooks con sus parámetros, sin inventar ninguno.
- **Con skills de revisión por repo:** propone `reviewSkills`.
- Todo se propone; nada se escribe sin enseñarlo antes (`--show`).

## 4. Qué cambia, archivo por archivo

| Archivo | Cambio |
|---|---|
| `templates/baton.json` | v2: `workspace`, `sessions`, `repos`, `branch`, `untrackedPolicy`, `hooks`, `deliveryOrder`, `merge`, `humanBeforePublish: "ask-once"`, `authority`, `resources`, `reviewer.neverRun`, `models.start`, `plan.partHeading`, `plan.decided`, `closing`, `localCi`. `modes` sigue como punto de partida |
| `templates/state.json` | v2 (ejemplo abajo): `proposal`, `coordinator`, `repos`, partes con roles, sesión, `startSha`/`endSha` por repo, `pauses`, `uses` y `verified`, además de `authority`, `locks`, `excluded`, `closing` y los estados `proposed`, `paused` y `closing`. Sigue leyendo la v1 |
| `templates/brief.md` | Repos y ramas, partes con repos, pausas internas y gates de evidencia, revisor y Critic **por parte**, hooks de sesión, «si no eres la primera parte, lee…», entorno (`env`) |
| `prompts/implementer.md` | Espera en primer plano, commits por repo, `pause-<P>.md`, mensaje `entrega`, bloque v2 |
| `prompts/supervisor.md` | Filas nuevas, delegación, `neverDelegate`, `ask-once`, desviaciones con evidencia |
| `prompts/models.md` | Nuevo: la rúbrica de D2 |
| `agents/reviewer.md` | Commits de partida por repo, gates de evidencia, `neverRun`, línea `Model:` bajo el veredicto, Critic como segunda lente opcional |
| `skills/run` | Momentos 1 y 2 de D1. El lanzamiento sigue yendo por tandas |
| `skills/event` | Una sesión nueva por parte, verificación D4, tarjeta si la app se niega, pausas internas, delegación, entregas parciales |
| `skills/event/deliver.md` | Multi-repo, `deliveryOrder`, snapshot, PR hermanas, hook `deliver` |
| `skills/event/close.md` | Nuevo: D12 y D13 |
| `skills/status` | `pause`/`continue` (D10), una línea por sesión de parte con su modelo, retomar desde otro chat |
| `skills/setup` y `detect.md` | D14 |
| `skills/plan` | `--adapt` (D8). El plan nuevo puede llevar `**Repos:**` por parte |
| `README.md`, `docs/DESIGN.es.md`, `docs/DECISIONS.md` | D-58 en adelante. El diseño B pasa a ser el de por defecto, y D-02, D-07 y D-08 quedan sustituidos |

**Perfil de MSG**, como lo propondría `setup` (los parámetros exactos de los scripts se confirman en la pausa):

```json
{
  "version": 2,
  "workspace": "checkout",
  "sessions": "per-part",
  "repos": [
    { "name": "root", "path": ".", "base": "develop", "rules": ["AGENTS.md", "CLAUDE.md"], "reviewSkills": ["msg-doc-governance", "msg-contract-sync"] },
    { "name": "backend", "path": "MicroservicesGenerator-backend", "base": "develop", "rules": ["AGENTS.md", "CLAUDE.md", ".cursor/rules/*.mdc"], "reviewSkills": ["msg-back-review"] },
    { "name": "frontend", "path": "MicroservicesGenerator-frontend", "base": "develop", "rules": ["AGENTS.md", "CLAUDE.md", ".cursor/rules/*.mdc"], "reviewSkills": ["msg-front-code-review", "msg-front-design"] }
  ],
  "branch": { "name": "codex/{{planSlug}}", "createdBy": "hook" },
  "untrackedPolicy": "exclude-local",
  "hooks": {
    "onStart": { "by": "coordinator", "run": "pwsh -File .agents/skills/msg-run-state/scripts/new-run.ps1 -RunId {{repoRunId}} -Repos MSG,Backend,Frontend -PlanSlug {{planSlug}}" },
    "beforePart": { "by": "session", "text": "Lee .agents/runs/{{repoRunId}}/handoff.md y ejecuta el plan con msg-implement-plan en el nivel que pide su §0." },
    "afterPart": { "by": "session", "text": "Deja handoff.md al día para la parte siguiente (msg-run-state)." },
    "snapshot": { "by": "session", "repo": "root", "after": ["backend", "frontend"], "run": "pwsh -File .agents/skills/msg-run-state/scripts/task-commit.ps1 -RunId {{repoRunId}} -Repo MSG -Phase submodule-snapshot -Message … -Paths … -ExpectedSubmoduleHeads …" },
    "deliver": { "by": "session", "run": "pwsh -File .agents/skills/msg-run-state/scripts/task-pr.ps1 -RunId {{repoRunId}} -Repos {{repo}} -ConfirmPush -UpdateBody -ReportPath {{report}} -Title \"{{title}}\"" },
    "onClose": { "by": "coordinator", "run": "pwsh -File .agents/skills/msg-run-state/scripts/complete-run.ps1 -RunId {{repoRunId}}" },
    "afterMerge": { "by": "session", "text": "Sube los gitlinks de la raíz a los commits mergeados de backend y frontend, con un commit a mano (el run ya está cerrado)." }
  },
  "deliveryOrder": ["backend", "frontend", "root"],
  "delivery": "pr",
  "merge": "never",
  "humanBeforePublish": "ask-once",
  "authority": { "alwaysAsk": ["Recrear contenedores o resetear datos fuera de los pasos que el plan marca"], "neverDelegate": ["ui-design", "install-software"] },
  "resources": { "computer-use": "exclusive", "docker-stack": "exclusive", "playwright-profile": "exclusive", "browser": ["playwright", "builtin"] },
  "reviewer": { "neverRun": ["docker compose up", "docker compose down", "docker rm", "git push"] },
  "plan": { "partHeading": "^(?:\\d+(?:\\.\\d+)*\\s+)?(?<id>P\\d+|CA)\\b", "decided": ["§5", "§13", "§3.4"] },
  "closing": ["deliver", "freshReviewPerRepo", "userReview", "clientTests", "qaMatrix", "qaRound2", "shortReport"],
  "localCi": { "workflows": [".github/workflows/*.yml", "MicroservicesGenerator-backend/.github/workflows/*.yml", "MicroservicesGenerator-frontend/.github/workflows/*.yml"], "when": "ciUnavailable", "comment": true },
  "notes": "Docker: imágenes en serie y siempre desde MicroservicesGenerator-backend. Reset de datos coherente (SQL Server y Redpanda juntos). QA con organizaciones nuevas de dev-login. Playwright: nunca borrar cookies. Backend: gitnexus_impact antes de tocar un símbolo y detect_changes antes de cada commit."
}
```

**`state.json` v2**, una parte:

```json
{
  "version": 2, "run": "fase4-x", "status": "running", "workspace": "checkout",
  "coordinator": { "sessionId": "local_…", "model": "opus" },
  "proposal": { "approvedAt": "…", "words": "Sí, lanza cada parte en su sesión con esta tabla", "revisions": 1 },
  "repoRunId": "20261101-fase4-x",
  "repos": { "root": { "path": "C:/MSG", "branch": "codex/fase4-x", "base": "develop", "baseSha": "…" }, "backend": { "…": "…" }, "frontend": { "…": "…" } },
  "parts": [{
    "id": "P2", "title": "…", "repos": ["backend"], "status": "working",
    "implementer": { "model": "opus", "effort": "medium", "reason": "…" },
    "reviewer": { "model": "opus", "effort": "high", "skills": ["msg-back-review"], "reason": "…" },
    "critic": null, "weight": "L", "uses": ["docker-stack"],
    "pauses": [{ "before": "P2.8", "text": "reset de datos", "delegated": true }],
    "session": { "id": "local_…", "name": "baton-fase4-x-p2", "archived": false },
    "startSha": { "backend": "…" }, "endSha": null,
    "rounds": 0, "logged": 0, "decisions": 0, "retries": 0, "replanned": false, "verified": null
  }],
  "current": "P2",
  "authority": { "delegated": [{ "row": "plan-pause", "scope": "reset de P2.8", "at": "…", "words": "autorizo el reset…" }] },
  "locks": { "docker-stack": "local_…" }, "excluded": ["docs/plans/plan-fase-4-….md"],
  "closing": { "steps": [], "sessions": [] },
  "messagesSinceUser": 1, "wakesSinceUser": 3, "lastSentAt": "…", "waiting": null, "presses": []
}
```

## 5. Prioridad y entregas

- **0.3: una fase de MSG con un solo `/baton:run`.** Partes 1 a 9 de este plan: sesiones (1), multi-repo (2), checkout (3), hooks (4), autoridad (5), `--adapt` (6), y de la mejora 9 lo que las sesiones por parte necesitan (pausa, tarjetas, contadores, archivar). La entrega de MSG funciona con el hook `deliver`. Lo que queda fuera se sigue haciendo a mano.
- **0.4: gates y entorno.** Gates por repo y de evidencia (7), recursos exclusivos (10), detección en `setup` (12), y `worktreeSetup` y `env`.
- **0.5: el cierre.** Fase `closing` (8) con QA y su segunda ronda, e informe corto, y CI local (11).

Cada versión pasa sondas CLI (como D-54) y una ronda en vivo antes de usarse en MSG. 0.4 y 0.5 tendrán su propio plan, escrito con lo aprendido en la 0.3.

## Pausa antes de la parte 1

Las respuestas del coordinador de la Fase 3 (2026-10-26) ya están en §2, D3, D4, D6, D7, D10 y D11. Si la Fase 4 se hace antes a mano con `PROMPT-COORDINADOR.md`, conviene que su coordinador apunte en `decisions.md`, como filas «obs», lo que la Fase 3 no pudo responder:

- si `start_session` gastó cuota de mensajes;
- si una tarjeta arrancada conservó el modelo y el esfuerzo;
- el modelo real del revisor Opus lanzado desde sesiones Sonnet (que el revisor escriba su modelo en la revisión);
- si algo, además de `task-notification` y los mensajes de otra sesión, impidió arrancar una sesión;
- las líneas completas de `task-pr.ps1` y `task-commit.ps1` que usaron los implementadores;
- el coste por papel si se puede medir.

Con eso se ajustan D2 a D10 y el perfil de MSG antes de implementar.

## Parte 1 — Esquemas v2 y lo que falta medir

Escribir `templates/baton.json` v2, `templates/state.json` v2 y el bloque de resultado v2 (D4), y hacer que `event` y `status` sigan leyendo los runs v1. Medir con sondas CLI o en la app los puntos 1 a 4 de §2 y apuntarlos como decisiones.

**Aceptación**
- `claude plugin validate . --strict` → 0.
- `templates/state.json` y `templates/baton.json` se parsean como JSON y contienen todas las claves de §4.
- `docs/DECISIONS.md` tiene una decisión por cada punto medido de §2, con cómo se midió y qué salió; lo que no se pudo medir se dice.
- Una sonda con un `state.json` v1 de 0.2 en `/baton:status` lo informa sin errores.

## Parte 2 — Propuesta de modelos en `/baton:run`

Momento 1 de D1 y todo D2: `prompts/models.md`, análisis por parte con la sección citada, tabla con motivo y peso, techo de modelo, botones, revisiones de la tabla, `--dry-run`, y guardado en `state.json` y `decisions.md`.

**Aceptación**
- Sonda: `/baton:run --dry-run` sobre un plan de tres partes de riesgo distinto muestra una fila por parte, cada una con motivo y sección citada, y no crea ramas, worktrees ni sesiones.
- Sonda: la respuesta «baja P3 a Sonnet» produce una tabla nueva con `proposal.revisions` 2 y sin sesiones arrancadas.
- Sonda: con el chat en Sonnet y una fila Opus, la tabla dice que la fila Opus no se puede lanzar desde este chat.
- `skills/run/SKILL.md` no arranca ninguna sesión sin `proposal.approvedAt`.

## Parte 3 — Una sesión por parte y verificación del coordinador

D3 y D4: `start_session` por parte con su fila, el nombre corto, la tarjeta si la app se niega, los mensajes a la sesión de la parte en curso, la espera en primer plano en `implementer.md`, la verificación por repo, las desviaciones con evidencia y el bloque v2, aceptando también `coord-result`.

**Aceptación**
- Sonda de evento `done` con `git status` sucio: el coordinador no da la parte por hecha y manda «baton · P<x>: deja el árbol limpio…».
- Sonda de evento `done` válido: `state.json` tiene la parte siguiente `working` con su propia `session` y su fila, y el mensaje de arranque lleva un commit de partida por repo.
- Sonda: un resultado `coord-result` se lee igual que `baton-result`.
- `prompts/implementer.md` dice que no se cierra el turno con trabajo en marcha y que los mensajes `entrega` son los únicos que autorizan push o PR.
- Sonda: un `done` con un Critic FAIL cerrado sin `critic-<P>-r2.md`, o con una revisión sin `### Criteria`, no se da por hecho.
- Las skills `run` y `event` no lanzan ningún comando en segundo plano desde el coordinador (Grep de `run_in_background` en ellas).

## Parte 4 — Multi-repo y `workspace: checkout`

D5: `repos`, ramas por repo, `startSha` y `endSha` por repo, revisor con commits por repo, `deliveryOrder`, snapshot, PR hermanas, entregas parciales en pausas, modo `checkout` con un solo run abierto y preflight limpio.

**Aceptación**
- En un laboratorio con una raíz y dos submódulos (remotos bare locales), `/baton:run --dry-run` en `checkout` muestra las tres ramas y sus bases, y no crea ningún worktree.
- Sonda: un segundo `/baton:run` con un run abierto en el mismo checkout se para y lo explica.
- El prompt del revisor que genera el brief lleva un commit de partida por cada repo de la parte.
- La entrega del laboratorio (sin `gh`, como `branch`) sigue `deliveryOrder` y lo apunta en el informe.

## Parte 5 — Hooks y `untrackedPolicy`

D6: los seis hooks con sus marcadores y `by`, `branch.createdBy`, `untrackedPolicy` con `state.excluded` y su limpieza al cerrar, y la entrega por mensaje `entrega` cuando hay hook `deliver`.

**Aceptación**
- Sonda: un `onStart` que crea las ramas en los tres repos del laboratorio deja `state.repos.*.branch` comprobado con `git rev-parse`.
- Sonda: con un archivo sin seguimiento y `exclude-local`, el archivo acaba en `.git/info/exclude` y en `state.excluded`; al cerrar, la línea desaparece.
- Sonda: con `stop`, el lanzamiento se para y nombra el archivo.
- Ningún marcador de hook queda sin sustituir en un hook ejecutado ni en el brief (Grep de las dobles llaves sobre `decisions.md` y el brief).

## Parte 6 — Autoridad configurable y delegación

D7: las filas nuevas de `supervisor.md`, `authority.allow`, `alwaysAsk` y `neverDelegate`, la delegación en `settled.md` y en `state.authority`, y `humanBeforePublish: "ask-once"`.

**Aceptación**
- Sonda: «autorizo el reset y push/PR; el diseño también» deja delegados el reset y push/PR, y rechaza el diseño en una línea que dice por qué.
- Sonda: una pausa interna delegada se decide sin preguntar y deja una fila `decided under delegation`; una no delegada se escala con botones.
- Sonda: con `ask-once`, la primera publicación enumera todos los push y PR del run en una sola pregunta, y la segunda no pregunta.

## Parte 7 — Plan tolerante y `/baton:plan --adapt`

D8: `partHeading`, el título que no cuenta, la aceptación en línea, `decided:`, las pausas dentro de una parte, y el mapa en `.claude/runs/_maps/` con el hash del plan.

**Aceptación**
- Sonda: `--adapt` sobre `C:\MSG\docs\plans\plan-fase-3-servidor-mcp-remoto.md` encuentra P0, P1, P2, P3, CA, P4 y P5, las pausas antes de P2.8 y de P4.0 y la pausa A→B, y no modifica el plan (mismo hash antes y después).
- Sonda: `/baton:run --dry-run` con ese mapa enseña la tabla de modelos de esas siete partes.
- Sonda: cambiar una línea del plan invalida el mapa, y `run` lo dice.

## Parte 8 — Pausa, continuación y límites

D10: `pause` y `continue` con `pause-<P>.md`, aviso a 8 con push, retomar desde otro chat, y archivar con el sí del usuario y reintentar.

**Aceptación**
- Sonda: «para» con una parte trabajando deja `status: paused`, el mensaje de pausa enviado y una fila en `decisions.md`; «continúa» manda el mensaje de continuar a la sesión de la parte.
- Sonda: con `wakesSinceUser` 8 sale un push y el run sigue; con 9 se para con «Continuar».
- Sonda: `/baton:status continue` desde un chat que no es `coordinator.sessionId` lo dice y actualiza el coordinador cuando arranca la parte siguiente.

## Pausa antes de la parte 9

El usuario decide si la ronda en vivo va en el laboratorio multi-repo, directamente en una fase pequeña de MSG o en las dos.

## Parte 9 — Ronda en vivo y documentación

Un plan de al menos cuatro partes en el laboratorio multi-repo, en la app, con modelos distintos por parte, una pausa interna delegada, una pregunta escalada, un «para» y un «continúa», y la entrega en orden. Después, `README.md`, `docs/DESIGN.es.md` y `docs/DECISIONS.md` (D-58 en adelante) al día, con lo que no se haya visto en vivo dicho como tal.

**Aceptación**
- `docs/DECISIONS.md` recoge los resultados de la ronda: pulsaciones del usuario, despertares por parte, arranques rechazados y tarjetas, y coste por papel con la misma medida que D-45.
- El README explica el paso de propuesta, `workspace`, `repos`, `hooks` y la delegación, y su lista «no visto en vivo» está al día.
- `claude plugin validate . --strict` → 0.
