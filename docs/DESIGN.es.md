# baton: el diseño

baton ejecuta un plan escrito por partes desde un chat de la app de escritorio de Claude, con las sesiones anidadas de la propia app y sin código propio. Este documento explica el diseño que se eligió (el A), cómo usa las sesiones nativas, qué conserva de foreman y por qué, las alternativas descartadas y las limitaciones conocidas. Las decisiones, con su porqué, están en [`DECISIONS.md`](DECISIONS.md): D-01…D-14 se fijaron al elegir el diseño y las demás salieron al construirlo y probarlo.

## El problema

Con planes largos, el usuario hacía de mensajero entre chats: copiaba rutas, pegaba «aplica esta revisión», autorizaba cada fase y vigilaba qué chat se había parado en un diálogo. foreman (v0.2) lo resolvió con código: un vigilante de 30 segundos, una máquina de estados, procesos `claude -p` para el revisor y el supervisor, hilos `--bg` y un panel propio. Funcionaba, pero con mucha superficie: guards, caché de marketplace, carreras entre el vigilante y la app, permisos de cada proceso. baton busca lo mismo con el 10 % de la complejidad apoyándose en lo que la app ya hace.

## Diseño A: un coordinador, una sesión implementadora por plan

- **El coordinador es el chat del usuario** con la skill `/baton:run` cargada. Lee las reglas del repo, crea el worktree y la rama del plan, escribe el estado en archivos y arranca **una** sesión implementadora anidada en modo `auto`, con el worktree como carpeta.
- **La sesión implementadora** sigue `prompts/implementer.md` y el brief de cada parte: implementa, hace commits, ejecuta los gates y lanza un **revisor fresco** como subagente de solo lectura (`agents/reviewer.md`). Guarda cada revisión, aplica los hallazgos hasta tres rondas sin mandar ningún mensaje al coordinador, y termina el turno con un bloque `baton-result`.
- **La app despierta al coordinador** cada vez que la sesión termina un turno. El coordinador lee `result-<parte>.md` y decide como supervisor con la tabla cerrada de `prompts/supervisor.md`. Después manda el brief siguiente, pregunta al usuario con botones y push, o entrega.
- **La entrega** sigue al repo: dejar la rama, abrir la PR (o actualizarla y comentarla si ya existe) o merge local. Nunca `--force` ni borrados. Al final, `report.md`.

### Cómo encaja con los límites de la app

| Límite (verificado en las pruebas) | Cómo lo resuelve baton |
|---|---|
| Solo un turno escrito por el usuario puede crear sesiones; ni el primer mensaje de una sesión creada por otra ni el aviso de otra sesión sirven. | Una sola sesión implementadora por plan, creada en el turno del lanzamiento, que el usuario teclea. Las partes se encadenan por mensajes, que sí se permiten en los turnos que abren los avisos. |
| Como mucho 10 mensajes a otras sesiones por cada mensaje del usuario en la sesión emisora; los avisos no lo reinician (D-33). | Un contador en `state.json`: como mucho 9 mensajes entre dos palabras del usuario y luego un botón «Continue». Un plan gasta un mensaje por parte y uno por respuesta o reintento; en las pruebas el pico fue 2. |
| `start_session` con `cwd` en el worktree de baton y `use_worktree: false`. | Aceptado sin diálogo de confianza; la sesión trabaja en la rama del plan, en `auto`. |
| Un subagente lanzado por el modelo funciona en `auto` y trabaja en la carpeta de su sesión. | El revisor es subagente de la sesión implementadora (D-03): cero mensajes por ronda y gates ejecutados en el worktree. `baton:reviewer` se resuelve con el plugin en scope `project` y el modelo y effort del brief. |
| Los `deny` del repo rigen en `auto` (sonda: `rm package.json` denegado por la regla de baton-lab y permitido en otro repo sin ella). | baton no toca los settings; el brief dice que una denegación no se esquiva. |
| La sesión anidada no lee lo que no está en su carpeta sin posible diálogo. | El coordinador copia al worktree el prompt del implementador, el del revisor y el plan (D-15); el implementador solo escribe dentro de su carpeta (D-04). |

## El estado vive en archivos

`state.json`, `decisions.md`, `report.md` y `findings.jsonl` están en el checkout. Los briefs, `settled.md`, los resultados y las revisiones están en la carpeta del worktree, y al entregar se copian al checkout. Nada depende de la memoria del chat: tras una compactación o al reabrir la app, «sigue» o `/baton:status continue` reconstruyen la situación desde los archivos (D-09). Las respuestas que se dan durante el run, del plan o de la persona, se escriben en `settled.md`, que el revisor lee junto al «Already decided» del plan (D-37).

## Lo que conserva de foreman, y por qué

| Idea de foreman | En baton |
|---|---|
| Plantilla de plan con criterios y pausas del autor | `templates/plan.md` y `/baton:plan`; partes y criterios en inglés o español. |
| Revisor fresco `OK/NO/BLOCKED`, tres rondas | Subagente de solo lectura con prompt fijo del plugin; la sesión solo le pasa hechos (parte, commit de inicio, ronda). |
| Tabla de autoridad cerrada con el porqué visible | `prompts/supervisor.md`; cada decisión es una fila en `decisions.md` y una línea en el chat. |
| Rama y worktree por plan con el prefijo del repo | `<prefix><plan>` en `.claude/worktrees/baton-<run>`, excluido de git. |
| Entrega según el repo | `branch`, `pr` (crear o actualizar y comentar), `merge` con `--abort` si falla. |
| Informe y registro de hallazgos | `report.md` con commits de git, revisiones, decisiones, respuestas y pulsaciones; `findings.jsonl` propone reglas cuando un hallazgo se repite. |

**Lo que se tira:** el vigilante, la máquina de estados, los procesos `claude -p`, los hilos `--bg`, el panel propio y los guards. La app ya despierta al coordinador, ya muestra las sesiones en la barra lateral y ya avisa cuando una necesita al usuario.

## Alternativas descartadas

- **B · Una sesión por parte, creadas todas al lanzar.** Cada parte tendría contexto limpio, pero todas las sesiones tendrían que crearse en el turno del lanzamiento (límite 1), y cada una empezaría a trabajar sin esperar a la anterior, salvo que se la frenara con instrucciones. Queda como evolución con `fresh=true` si el contexto de planes largos lo pide.
- **C · Todo dentro de la sesión del usuario** (implementar y revisar con subagentes, sin sesión anidada). Sin mensajes entre sesiones, pero el chat del usuario se llenaría con todo el trabajo y se compactaría pronto, que es justo lo que el usuario quería evitar (patrón P5 de foreman).

## Limitaciones conocidas

- El lanzamiento lo teclea el usuario; otra sesión no puede lanzarlo.
- Un plan muy largo sin pausas ni preguntas pide una palabra cada 9 mensajes.
- Las carpetas vacías de los worktrees se quedan mientras vive su sesión implementadora (D-35).
- `settings.local.json` no llega al worktree (D-31).
- Los diálogos de permiso de la sesión implementadora solo los ve la barra lateral.
- El contexto de la sesión implementadora crece con el plan; los briefs son autosuficientes para mitigarlo.
- La ruta del NO (revisión con hallazgos, arreglo, ronda 2) solo se ha probado con una sonda sin sesiones: las 10 revisiones de las pruebas en vivo dieron OK en la ronda 1.
