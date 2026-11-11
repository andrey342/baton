# Una fase real con baton 0.3: el resumen publicable

Este resumen es para el post de redes. Lleva solo cifras del proceso y fallos descritos de forma genérica: ni código, ni rutas, ni nombres de repos, ni nada del producto. El análisis completo, con todas las fuentes, está en `fase4a.es.md`; cada cifra de aquí sale de él.

## El contexto

- **baton** es un plugin para Claude Code que ejecuta un plan escrito parte por parte desde un chat coordinador. Cada parte va en su propia sesión, con el modelo que aprobó la persona, y un revisor independiente la comprueba hasta darla por buena.
- **El proyecto:** tres repositorios (una raíz y dos submódulos) en un monorepo con scripts propios para abrir, entregar y cerrar cada etapa de trabajo.
- **La etapa:** 9 partes planificadas, entregadas como 3 pull requests, una por repo.

## Las cifras

| | |
|---|---|
| Duración total | 11 días y 3 horas, del lanzamiento al merge |
| Primera entrega | a las 81 horas, con unas 26 de ellas esperando a la persona |
| Corrección tras la primera entrega | 7 días y 18 horas |
| Sesiones de implementación | 10: 9 partes y una de corrección |
| Mensajes de la persona al coordinador | unos 45 |
| Turnos automáticos del coordinador | unos 155: fines de turno de las sesiones y avisos de subagentes |
| Revisiones por parte antes de la primera entrega | 31, 13 de ellas rechazadas, más 15 críticas independientes |
| Revisiones y auditorías frescas después | 93 subagentes |
| Coste estimado (equivalente de API; se pagó con suscripción) | ~2.000 USD |
| Coste antes / después de la primera entrega | 21 % / 79 % |
| Peso del coordinador en el coste | 4,5 % |
| Peso de la revisión, en todas sus formas, en el coste | 33 % |
| Tamaño de la PR más grande | de ~310 archivos en la primera entrega a ~1.900 en la última |

## Qué funcionó

- **Una sesión por parte con su propio modelo:** Opus donde había riesgo y Sonnet donde no.
- **El coordinador comprueba en vez de fiarse del informe.** Cada «hecho» se verificó en los tres repos (commits, árbol limpio y tests repetidos), y las cuatro entregas se comprobaron contra GitHub.
- **Entregar con los propios scripts del repo:** tres PR enlazadas en orden, con el snapshot de los submódulos.
- **Delegar con límites:**
  - la persona dejó al coordinador decidir mientras dormía, y todo quedó apuntado con sus palabras literales;
  - nada se saltó una denegación de seguridad;
  - el merge y los borrados irreversibles siempre fueron de la persona.
- **El coordinador salió barato:** un 4,5 % del coste, aunque su contexto se compactó 12 veces sin perder el estado.

## Qué falló

1. **La revisión por parte no bastó.** Cada revisor miraba el cambio de su parte contra sus criterios, no la PR entera contra las reglas de arquitectura del repo. La persona encontró 9 defectos de diseño que habían pasado decenas de revisiones.
   - El arreglo fue una auditoría archivo por archivo con inventario obligatorio (archivos en alcance = archivos revisados, con un dato concreto por fila) y varias rondas de cierre.
   - Esa corrección costó más que todo el plan original.
2. **La PR creció sin aviso.** Al corregir aparecieron detectores nuevos y refactors de deuda anterior, y la PR se multiplicó por seis sin que el coordinador lo señalara. La persona lo vio sola.
3. **Tests en verde que no se habían ejecutado.** Unos tests condicionados a una variable de entorno salían como «saltados» en local, y la CI salió roja después de entregar.
4. **La app no siempre despierta al coordinador.** Hubo despertares perdidos y sesiones paradas sin informe. Los turnos abiertos por otra sesión, o desde el móvil con Remote Control, no pueden arrancar sesiones nuevas.
5. **Las partes de cierre, en un modelo pequeño.** Una parte de «cierre y QA» acabó escribiendo lógica nueva en un modelo pensado para tareas sencillas, y encadenó rondas de revisión hasta que se subió de modelo.
6. **Una herramienta en «latest»** cambió su formato a mitad del trabajo y llenó el análisis de impacto de falsos positivos.

## Qué cambia en la siguiente versión

- **La revisión carga siempre las reglas del repo y entrega un inventario por archivo.** El coordinador rechaza la revisión que no lo traiga.
- **Revisión final de cada PR completa, en lotes, antes de entregar.**
- **Aviso a la persona cuando la entrega crece por encima de un umbral.**
- **Los tests saltados cuentan como no ejecutados,** y antes de cada reentrega se pasa el equivalente de la CI.
- **Las correcciones después de entregar tienen su sitio en el plan,** con partes nuevas, rondas y registro, y no van en briefs escritos a mano.
- **Un respaldo para cuando la app no despierta o no deja abrir sesiones.**
