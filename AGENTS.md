# AGENTS.md — syv-character-kit

Política editorial y convenciones de trabajo del proyecto. Para entender QUÉ es el producto, leer [`PRD.md`](PRD.md). Para el schema, leer [`docs/hoja-modelo.md`](docs/hoja-modelo.md) y [`docs/tag-modelo.md`](docs/tag-modelo.md).

---

## Política del PRD: rolling release sin historia

**`PRD.md` es un documento vivo de versión única.** Refleja **solo el estado vigente** del producto. No hay:

- **Versionado**: no se escribe `v0.5.0`, `v0.4.1`, `Reemplaza:`, etc. Si el campo X ya no existe, simplemente no aparece en el PRD. Si una decisión cambió, se reescribe la sección — no se anota "antes era Y".
- **Changelog**: no hay sección `## 0. Changelog` ni equivalentes. El historial vive en `git log`. La intención detrás de un cambio vive en el mensaje del commit y en el cuerpo del PR. El PRD no es un diario.
- **Compatibilidad hacia atrás**: el PRD no documenta "migración desde la versión anterior". Si un implementador necesita reconstruir cómo era el contrato en un punto del pasado, lee `git log -- PRD.md` y compara revisiones. No es responsabilidad del PRD mantener esa lectura accesible.
- **Open Questions con número de versión**: las OQs activas viven en [`docs/open-questions.md`](docs/open-questions.md) (sin sufijo de versión). Cuando una se resuelve, se elimina la entrada o se reescribe la sección afectada. No se marca "OQ-12 resuelta en v0.5.0".

**Por qué.** El PRD es contrato, no narrativa. Los consumidores (clientes, motor de batalla, herramientas downstream) leen el PRD para saber qué pueden esperar HOY. La historia los confunde — si el campo `semilla` no existe, leer "se eliminó en v0.5.0 porque la prosa LLM no es reproducible" agrega ruido cognitivo y no aporta valor operativo. La explicación útil para implementadores actuales se reformula como "el schema no expone reproducibilidad determinista de la prosa: la prosa se persiste como artefacto al guardar" — sin mencionar la transición.

**Cuándo sí preservar contexto histórico.** Decisiones de diseño cuyo *por qué* sigue vivo se documentan en el cuerpo del PRD como "tensión asumida" o "decisión de producto" — sin fecha ni versión, solo el razonamiento. Ejemplo: "El sistema acepta tags fuera del canon. Costo: fragmentación silenciosa entre `Francotirador` y `francotirador`. Mitigación: curaduría del catálogo, no validación del schema". Eso es útil hoy. "Antes el schema validaba estrictamente, en v0.3.0 se abrió" no lo es.

---

## Política de los docs del schema (`/docs/`)

Mismo principio que el PRD: rolling release, sin versionado ni changelog. Todos los archivos bajo `docs/` (`hoja-modelo.{md,yaml}`, `tag-modelo.{md,yaml}`, `tag-modelo-ejemplos.yaml`, `tag-requeridos-por-categoria.md`, `atributos-y-efectos.md`, `user-stories.md`, `open-questions.md`, y cualquier doc nuevo) describen el estado vigente. Cualquier cambio se aplica como reescritura del párrafo o sección afectados; no se anota "antes era X".

**Excepción tolerable**: open questions activas y backlog explícito viven en [`docs/open-questions.md`](docs/open-questions.md). Las que son específicas del sistema de tags pueden quedar en `tag-modelo.md §8`. No es historia — es backlog.

---

## Mocks (`mock/personajes/`) y Catálogo (`tags/`)

Los 22 fixtures de personajes y los archivos de catálogo de tags son **datos**, no documentación. Se versionan vía git como cualquier otro código. Cuando el schema cambia, los mocks se migran (idealmente con un script Python en el commit que aplica el cambio) y el commit cuenta la historia.

No se mantienen versiones múltiples de un mock. No hay `aguirre_v0.4.yaml` y `aguirre_v0.5.yaml` — hay `01_aguirre.yaml` y refleja el schema vigente.

---

## Decisiones de Diseño de Juego (GDDRs)

El directorio [`gddr/`](file:///Dev/SyV/syv-character-kit/gddr/) contiene los **Game Design Decision Records (GDDRs)**. En este proyecto, "gddr" es exactamente lo que hace, ya que este es un kit para gestionar personajes del juego *Subordinación y Valor* (SyV). Al redactar un GDDR, no nos perdemos en la lógica de software o la API; lo utilizamos para definir cómo queremos que se utilicen las reglas y los archivos que hemos preparado (schemas, modelos, catálogos). Los GDDRs sirven como puente de diseño de juego, se referencian mutuamente con los archivos del proyecto e incluso pueden utilizar los mocks vigentes como ejemplos prácticos para ilustrar decisiones mecánicas o de diseño.

---

## Aleatoriedad: agnóstica al sistema, expresada en formato portable

El kit **no fija** un sistema de resolución de azar. El motor de batalla, las herramientas downstream o una mesa concreta pueden adoptar el que prefieran (dados, cartas, tirada digital, lo que sea). Para que las fichas, tags y modificadores sean reutilizables entre sistemas, toda magnitud se expresa con una de **tres formas portables** según el tipo:

- **Probabilidades de evento**: porcentaje. `40% de fallar el chequeo`, `5% de paniquear bajo fuego cruzado`. Nunca `tirada con desventaja` u otra expresión atada a un sistema concreto.
- **Modificadores sobre atributos o stats calculadas**: delta entero sobre la escala canónica de la variable. `(+1) MENTAL`, `(-1) INICIATIVA`, `(+2) FATIGA`. Las variables y sus escalas viven en [`docs/atributos-y-efectos.md`](docs/atributos-y-efectos.md). Estas son las "monedas" canónicas del kit; el motor downstream las mapea a su sistema.
- **Modificadores sobre tasas o magnitudes continuas**: porcentaje sobre la magnitud. `-100% MOVIMIENTO` (inmóvil), `+50% defensa por cobertura media`. Útil cuando el efecto escala con el valor base.

**Atributos base** en escala `2..7` (entero, más es mejor): `fis`, `tac`, `men`. Topes y reglas de creación en [`gddr/01-flujo-obligatorio-creacion.md`](gddr/01-flujo-obligatorio-creacion.md). La interpretación canónica sugerida es "decenas de porcentaje de éxito en chequeo roll-under" — referencia para diseño, no contrato.

**Coexistencia con sistemas de referencia**: las GDDRs y documentos auxiliares pueden ilustrar mecánicas con un sistema concreto (p. ej. `3d10o1` — tres dados de diez, observando el dado objetivo, mediana) **como ejemplo didáctico**. El contrato del kit son las tres formas portables de arriba; el ejemplo en dados es ilustrativo, no normativo.

**Por qué.** SyV es un universo, no un sistema. Atar el schema a una mecánica concreta amputa la portabilidad. El delta sobre escala canónica y el porcentaje sobre tasa son lingua franca: cualquier sistema sabe convertirlas a su moneda local.

---

## Convenciones de identificadores

- **Slugs**: lowercase + underscore, sin acentos, sin guiones (`ejercito_rojo`, `lider_de_escuadra`, `mansilla`). El separador uniforme es `_` para permitir composición en notación punto sin ambigüedad (`equipo.arma.pistola`, `lealtad.escuadra.mansilla`). Excepción: el `identidad.slug` del personaje es **patente opaca** `^[A-Z0-9]{8}$` (ej. `K9F2H3M4`), no slug legible — ver [`docs/hoja-modelo.md §1.1`](docs/hoja-modelo.md).
- **Tags**: notación punto `<categoria>[.<subcategoria>].<slug>`. Ver `docs/tag-modelo.md §2`.
- **Campos estructurales en YAML**: `snake_case_castellano` (`escuadra`, `atributos`, `mando`).
- **Idioma**: castellano rioplatense, voseo sobrio. Sin emojis salvo pedido explícito del usuario.

---

## Trabajo con Claude / agentes de IA

- Antes de cambiar el schema, asegurarse de que **todos** los archivos bajo `/docs/` (más `PRD.md`, `API.md`, `MODEL.md`) queden consistentes entre sí. Sincronía estricta entre `API.md` y `MODEL.md`.
- Después de cambios al schema, evaluar si los 22 mocks necesitan migración. Si sí, escribir el script Python en el mismo turno y aplicarlo.
- El PRD se actualiza al final, cuando los docs del schema ya están estables. El PRD enlaza a `/docs/` y a `API.md`/`MODEL.md` para los detalles; no los duplica.
- No agregar entradas de changelog. No agregar líneas "Versión: X". Si el modelo cambia, reescribir las secciones afectadas en lenguaje atemporal.
- Los cambios destructivos sobre `mock/personajes/` se hacen solo cuando el usuario lo autoriza explícitamente — la prosa de `historia` e `historial[].descripcion` es contenido editorial irreplazable.
- **Lore canon**: el universo SyV vive en `/Dev/SyV/syv-obsidian/` y `/Dev/SyV/syv-battle-game-system/`. Antes de inventar terminología (rangos, armas, geografía, facciones, vocabulario táctico), verificar contra esas fuentes para mantener fidelidad.
