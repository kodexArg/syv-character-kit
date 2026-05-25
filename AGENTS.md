# AGENTS.md — syv-character-kit

Política editorial y convenciones de trabajo del proyecto. Para entender QUÉ es el producto, leer [`PRD.md`](PRD.md). Para el schema, leer [`docs/hoja-modelo.md`](docs/hoja-modelo.md) y [`docs/tag-modelo.md`](docs/tag-modelo.md).

---

## Política del PRD: rolling release sin historia

**`PRD.md` es un documento vivo de versión única.** Refleja **solo el estado vigente** del producto. No hay:

- **Versionado**: no se escribe `v0.5.0`, `v0.4.1`, `Reemplaza:`, etc. Si el campo X ya no existe, simplemente no aparece en el PRD. Si una decisión cambió, se reescribe la sección — no se anota "antes era Y".
- **Changelog**: no hay sección `## 0. Changelog` ni equivalentes. El historial vive en `git log`. La intención detrás de un cambio vive en el mensaje del commit y en el cuerpo del PR. El PRD no es un diario.
- **Compatibilidad hacia atrás**: el PRD no documenta "migración desde la versión anterior". Si un implementador necesita reconstruir cómo era el contrato en un punto del pasado, lee `git log -- PRD.md` y compara revisiones. No es responsabilidad del PRD mantener esa lectura accesible.
- **Open Questions con número de versión**: las OQs activas viven en `## 14. Open questions` (sin sufijo de versión). Cuando una se resuelve, se elimina la entrada o se reescribe la sección afectada. No se marca "OQ-12 resuelta en v0.5.0".

**Por qué.** El PRD es contrato, no narrativa. Los consumidores (clientes, motor de batalla, herramientas downstream) leen el PRD para saber qué pueden esperar HOY. La historia los confunde — si el campo `semilla` no existe, leer "se eliminó en v0.5.0 porque la prosa LLM no es reproducible" agrega ruido cognitivo y no aporta valor operativo. La explicación útil para implementadores actuales se reformula como "el schema no expone reproducibilidad determinista de la prosa: la prosa se persiste como artefacto al guardar" — sin mencionar la transición.

**Cuándo sí preservar contexto histórico.** Decisiones de diseño cuyo *por qué* sigue vivo se documentan en el cuerpo del PRD como "tensión asumida" o "decisión de producto" — sin fecha ni versión, solo el razonamiento. Ejemplo: "El sistema acepta tags fuera del canon. Costo: fragmentación silenciosa entre `Francotirador` y `francotirador`. Mitigación: curaduría del catálogo, no validación del schema". Eso es útil hoy. "Antes el schema validaba estrictamente, en v0.3.0 se abrió" no lo es.

---

## Política de los docs del schema (`/docs/`)

Mismo principio que el PRD: rolling release, sin versionado ni changelog. Los archivos `docs/hoja-modelo.md`, `docs/hoja-modelo.yaml`, `docs/tag-modelo.md`, `docs/tag-modelo.yaml` describen el estado vigente. Cualquier cambio se aplica como reescritura del párrafo o sección afectados; no se anota "antes era X".

**Excepción tolerable**: una sub-sección final tipo "Open Questions" o "Pendientes" puede vivir en `tag-modelo.md` para enmarcar trabajo futuro. No es historia — es backlog.

---

## Mocks (`mock/personajes/`) y Catálogo (`tags/`)

Los 22 fixtures de personajes y los archivos de catálogo de tags son **datos**, no documentación. Se versionan vía git como cualquier otro código. Cuando el schema cambia, los mocks se migran (idealmente con un script Python en el commit que aplica el cambio) y el commit cuenta la historia.

No se mantienen versiones múltiples de un mock. No hay `aguirre_v0.4.yaml` y `aguirre_v0.5.yaml` — hay `01_aguirre.yaml` y refleja el schema vigente.

---

## Decisiones de Diseño de Juego (GDDRs)

El directorio [`gddr/`](file:///Dev/SyV/syv-character-kit/gddr/) contiene los **Game Design Decision Records (GDDRs)**. En este proyecto, "gddr" es exactamente lo que hace, ya que este es un kit para gestionar personajes del juego *Subordinación y Valor* (SyV). Al redactar un GDDR, no nos perdemos en la lógica de software o la API; lo utilizamos para definir cómo queremos que se utilicen las reglas y los archivos que hemos preparado (schemas, modelos, catálogos). Los GDDRs sirven como puente de diseño de juego, se referencian mutuamente con los archivos del proyecto e incluso pueden utilizar los mocks vigentes como ejemplos prácticos para ilustrar decisiones mecánicas o de diseño.

---

## Aleatoriedad: agnóstica al sistema, expresada en porcentajes

El kit **no fija** un sistema de resolución de azar. El motor de batalla, las herramientas downstream o una mesa concreta pueden adoptar el que prefieran (dados, cartas, tirada digital, lo que sea). Para que las fichas, tags y modificadores sean reutilizables entre sistemas, toda probabilidad, ventaja, penalización o bonificación se expresa como **valor porcentual**.

- **Probabilidades y modificadores siempre en %**: `-20% a la puntería`, `+50% a la defensa por cobertura media`, `+10% de iniciativa por entrenamiento`. Nunca en unidades específicas de un sistema concreto (no `+2 al d20`, no `-1d6 al daño`).
- **Atributos en escala 0–9** (entero, más es mejor): `fis`, `tac`, `men`, `pun`, etc. La interpretación canónica sugerida es **decenas de porcentaje**: `3` ≈ 30–39%, `7` ≈ 70–79%. Esta lectura es solo referencia para diseño y balance; el sistema de resolución concreto decide cómo mapearla a su mecánica.
- **Coexistencia con sistemas de referencia**: las GDDRs o documentos auxiliares pueden ilustrar mecánicas con un sistema concreto (p. ej. `3d6o1` — tres dados de seis, observando el dado objetivo que suele ser la mediana) **solo como ejemplo didáctico**. El contrato del kit sigue siendo el porcentaje; el ejemplo en dados es ilustrativo, no normativo.
- **Aspectos** (tags con efecto mecánico) declaran sus modificadores como porcentajes, no como reglas atadas a un sistema. Un aspecto `cobertura_media` aporta `+50% defensa`, no "tirada con ventaja".

**Por qué.** SyV es un universo, no un sistema. Atar el schema a una mecánica concreta amputa la portabilidad. El porcentaje es lingua franca: cualquier sistema sabe convertirlo a su moneda local.

---

## Convenciones de identificadores

- **Slugs**: lowercase + underscore, sin acentos, sin guiones (`aguirre_walter`, `ejercito_rojo`, `lider_de_escuadra`). El separador uniforme es `_` para permitir composición en notación punto sin ambigüedad (`equipo.arma.pistola`, `lealtad.pj.aguirre_walter`).
- **Tags**: notación punto `<categoria>[.<subcategoria>].<slug>`. Ver `docs/tag-modelo.md §2`.
- **Campos estructurales en YAML**: `snake_case_castellano` (`escuadra`, `atributos`, `mando`).
- **Idioma**: castellano rioplatense, voseo sobrio. Sin emojis salvo pedido explícito del usuario.

---

## Trabajo con Claude / agentes de IA

- Antes de cambiar el schema, asegurarse de que los 4 archivos de `/docs/` queden consistentes entre sí.
- Después de cambios al schema, evaluar si los 22 mocks necesitan migración. Si sí, escribir el script Python en el mismo turno y aplicarlo.
- El PRD se actualiza al final, cuando los docs del schema ya están estables. El PRD copia conceptos clave y enlaza a `/docs/` para los detalles. Evitar duplicación; preferir links.
- No agregar entradas de changelog. No agregar líneas "Versión: X". Si el modelo cambia, reescribir las secciones afectadas en lenguaje atemporal.
- Los cambios destructivos sobre `mock/personajes/` se hacen solo cuando el usuario lo autoriza explícitamente — la prosa de `historia` e `historial[].descripcion` es contenido editorial irreplazable.
