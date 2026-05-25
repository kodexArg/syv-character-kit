# Hoja Modelo — Referencia narrativa de campos

> **Versión compatible**: schema v0.5.0 (refactor mayor — tags como ciudadanos universales
> del modelo; colapso de bloques `faccion`, `salud`, `mental`, `vinculos`, `lealtades`,
> `rasgos/traits/perks/etc` a la lista plana `tags[]` con notación punto).
> **Propósito**: descripción campo por campo de la hoja de personaje. Para el template
> programático, ver [`hoja-modelo.yaml`](hoja-modelo.yaml).
> **Sistema de tags**: definición, categorías y catálogo en [`tag-modelo.md`](tag-modelo.md).

---

## Estructura de la hoja

```
personaje:
  identidad: {...}
  atributos: {...}
  tags: [...]               # lista plana de strings en notación punto
  historia: str
  historial: [...]
  metadatos: {...}
  extras: object | null
```

Solo seis bloques estructurados (más la lista de tags). La regla rectora: **todo lo que puede ser discreto y no es identidad/atributo/prosa/audit, es tag**. La justificación detallada de qué es tag y qué no en [`tag-modelo.md` §1](tag-modelo.md#1--qué-es-un-tag).

---

## §1 — Identidad

Quién es el personaje, fuera de su contexto operativo.

**`slug`** — Identificador único. String estable asignado **en el momento de persistir** (mock o DB). Convención: lowercase + underscore, sin acentos. Formato canónico: `{apellido}_{nombre}` (ej. `aguirre_walter`). Generado del lado servidor en el guardado, evita race conditions. El slug también funciona como clave de referencia compuesta en tags relacionales (`lealtad.pj.{slug}`, `nemesis.pj.{slug}`). Ver [`tag-modelo.md` §4](tag-modelo.md#4--categorías-relacionales-lealtad-y-nemesis).

**`nombre`** — Nombre real. String inmutable. Ej. `"Walter Aguirre"`.

**`sobrenombre`** — Cómo se lo conoce operativamente. Derivable al servir desde `nombre`, tags `rango.*` y tags `rol.*` de mando si aplican. `null` cuando no hay distinción.

**`rol`** — Identidad narrativa base, no posición operativa. String con default `"ciudadano"`. Puede contener un título narrativo (`"Sargento Confederado"`, `"Líder Revolucionario"`) o quedarse en `"ciudadano"` con la capa operativa expresada en tags `rol.*`. **No confundir con tags `rol.*`** (que viven en `tags[]`).

**`genero`** — Enum abierto: `"masculino"`, `"femenino"`, `"no_binario"`, `"otro"`.

**`edad`** — Years al momento de creación. Integer.

---

## §2 — Atributos

Set de tres valores numéricos que definen la capacidad base. Determinísticos por rango en creación; mutables solo vía hito `triple_cero` o `mejora_atributo`. Rango 2-5 para `fis` y `tac`; hasta 7 para `men` en líderes.

- **`fis`** — resistencia, potencia bruta.
- **`tac`** — precisión, coordinación, reflejos.
- **`men`** — liderazgo, moral base, resistencia psicológica.

Son las **únicas magnitudes numéricas persistidas**. Toda otra capacidad derivada (fatiga máxima, moral máxima, capacidad de mando vigente, fza_aportada) se calcula en caliente con fórmulas fijas — no se persiste para evitar drift.

---

## §3 — Tags

Lista plana de strings en notación punto. Es la fuente de verdad para todo lo discreto del personaje. **Definición completa, categorías canon, sub-categorías, formato y reglas de catálogo viven en [`tag-modelo.md`](tag-modelo.md).**

Resumen de las categorías canon y dónde caen los datos del personaje:

| Tag | Qué representa |
|---|---|
| `faccion.*` | Pertenencia macro (Confederación, Ejército Rojo). |
| `rango.*` | Designación operativa jerárquica (`rango.lider_de_escuadra`, `rango.apuntador`). |
| `escuadra.*` | Asignación a escuadra concreta. |
| `mando.capaz` | Presencia = capacidad de mando si cae el líder activo. |
| `estado.*` | Disponibilidad operativa (`estado.activo`, `estado.disponible`, `estado.kia`, `estado.licencia`). Exactamente una. |
| `salud.*` | Estado físico actual; acumulable. Reemplaza el enum `estado_salud` y los pools `fatiga_max/actual` de v0.4.x. |
| `mental.*` | Estado anímico actual; acumulable. Reemplaza pools `moral_max/actual`. |
| `rasgo.*` | Rasgos físicos observables. |
| `trait.*` | Rasgos de carácter sin mecánica activa. |
| `perk.*` | Ventajas regladas con efecto numérico. |
| `aspecto.*` | Mini-tags identitarios con efecto mecánico en mini-frase. |
| `skill.*` | Habilidades aprendidas o entrenadas. |
| `equipo.arma.*` / `equipo.utilitario.*` / `equipo.vestidura.*` | Equipo cargado. Utilitarios son repetibles (tres `equipo.utilitario.cargador` = tres entidades físicas). |
| `rol.oficio.*` / `rol.jerarquia.*` / `rol.narrativo.*` / `rol.mecanico.*` | Roles operativos. `rol.mecanico.lider` y `rol.mecanico.heroe` participan en la derivación de `fza_aportada`. |
| `lealtad.faccion.*` / `lealtad.pj.*` / `lealtad.escuadra.*` | Lealtades reales y declarables. Solo las "que el personaje declararía si se le pregunta". Detalle de la sintaxis compuesta en [`tag-modelo.md` §4](tag-modelo.md#4--categorías-relacionales-lealtad-y-nemesis). |
| `nemesis.pj.*` | Enemistad individual identificada en batalla; creada en caliente; habilita reglas downstream. |

**Derivaciones desde tags** (motor al servir, no persistidas):

- **`filiacion`** — string `"{rango} de la {escuadra.nombre} del {escuadra.cuerpo}"`, derivado de los tags `rango.*` y `escuadra.*` (lookups en el catálogo). `null` si falta alguno.
- **`fatiga_max` / `moral_max`** — formulas fijas sobre `atributos` (`fis + men`, `men`).
- **`fza_aportada`** — `3` con `rol.mecanico.heroe`, `2` con `rol.mecanico.lider`, `1` sin ninguno.

Cambios post-creación en `tags[]` se registran como hito `agregar_tag` / `quitar_tag` con metadata `{tag}`.

### Extensibilidad total

El sistema de tags no tiene catálogo cerrado. Las categorías listadas arriba (`faccion`, `rango`, `escuadra`, `skill`, `equipo.*`, `rol.*`, etc.) son el **andamiaje canon** que organiza los casos comunes y permite a clientes downstream apoyarse en una semántica conocida — pero **no son una jaula**. Cualquiera puede:

- **Crear un tag nuevo** dentro de una categoría existente (`skill.lockpicking`, `equipo.utilitario.linterna_a_manivela`, `rasgo.tatuaje_de_ancla`).
- **Crear una sub-categoría nueva** dentro de una familia (`equipo.montura.caballo_criollo`, `rol.administrativo.intendente`).
- **Crear una categoría nueva entera** que no estaba prevista (`oficio_civil.herrero`, `vicio.fuma`, `mascota.perro_pastor`). El parser solo necesita el primer segmento `<categoria>` para enrutar.

Estos tags se persisten exactamente igual que los canon — la única diferencia es su `origen` en el catálogo (`emergente` o `custom`). El motor downstream que no los reconozca los puede ignorar o renderizar como genéricos; el motor que sí los entienda los aplica con su semántica propia. El esquema **no rechaza tags por desconocidos**.

Esta libertad es deliberada y central al diseño. La gracia del sistema es que la mayoría de los personajes encajan en el andamiaje canon, pero los que necesitan algo único (un personaje con un dialecto raro, un cura con un cáliz, un mecánico con una llave inglesa con historia) pueden expresarlo sin pelearse con el schema. El costo asumido — fragmentación silenciosa entre `Francotirador` y `francotirador`, o entre `skill.medicina` y `medicina.curacion` — se mitiga con curaduría del catálogo, no con restricciones del schema.

---

## §4 — Historia

Prosa biográfica original. String de 120-200 palabras escrito por LLM en la creación del personaje en memoria volátil. Al persistir se congela: nunca muta tras el guardado. Castellano rioplatense, primera persona narrativa.

**Nota sobre reproducibilidad**: la prosa es no-determinística por construcción. No existe semilla que la regenere idéntica — se persiste como artefacto, no como derivado. Por eso el campo `semilla` del schema anterior fue eliminado.

---

## §5 — Historial

Array de hitos. Cada entrada: `fecha` (ISO-8601), `tipo` (string abierto), `descripcion` (prosa), `ref_batalla` (slug de batalla o `null`), `metadata` (object libre).

Tipos sugeridos: `triple_cero`, `ascenso`, `herida`, `recuperacion`, `agregar_tag`, `quitar_tag`, `traslado`, `condecoracion`, `mejora_atributo`, `cambio_rango`, `cambio_mando`, `cambio_estado`, `cambio_salud`, `cambio_mental`, `asignacion_escuadra`, `identificacion_nemesis`, `formacion_lealtad`, `ruptura_lealtad`. Personajes recién creados arrancan con `historial: []`.

---

## §6 — Metadatos

Campos de auditoría.

- **`creado_en`** — ISO-8601, creación en memoria volátil.
- **`canonizado_en`** — ISO-8601 o `null`. Fecha en que se persistió.
- **`ultima_actualizacion`** — ISO-8601; se actualiza con cada hito.

Eliminados respecto a v0.4.x: `modelo_prosa` y `es_canon` (este último derivable de `canonizado_en != null`).

---

## §7 — Extras

Escape hatch. Object libre o `null`. **Soporta cualquier llave** y estructura anidada arbitraria. La API no inspecciona ni valida su contenido. Permite a clientes externos persistir metadatos propios sin romper el schema.

---

## Cambios respecto a v0.4.1

Refactor mayor — v0.5.0.

| Antes | Ahora |
|---|---|
| `id` + `origen` + `semilla` | `identidad.slug` único, generado al persistir |
| Bloque `faccion` (faccion/filiacion/escuadra/rango/mando/estado) | Tags `faccion.*`, `escuadra.*`, `rango.*`, `mando.capaz`, `estado.*`. `filiacion` derivada al servir. |
| Campo `rol` aislado | En `identidad.rol` (narrativo base, default `"ciudadano"`). Roles operativos como tags `rol.oficio/jerarquia/narrativo/mecanico.*`. |
| `estado_salud` enum y `estado_vital` (fatiga/moral numéricos) | Tags `salud.*` y `mental.*` acumulables. Pools máximos calculados en caliente. |
| `lealtades: {primaria, secundarias, secretos}` | Tags `lealtad.faccion.*` / `lealtad.pj.*` / `lealtad.escuadra.*`. Secundarias/secretas: TBD aparte. |
| `vinculos: [{tipo, ref, descripcion}]` | Eliminado. Refs operativas → tags `lealtad.*` / `nemesis.*`. Prosa del vínculo → `historia` o `historial`. |
| `tags: [{categoria, valor}]` | Lista plana de strings en notación punto: `<categoria>[.<subcategoria>].<slug>`. |
| (sin equivalente) | Categoría `nemesis`: enemistad creada en caliente. |
| `metadatos.modelo_prosa` y `metadatos.es_canon` | Eliminados. |
| Slugs con `-` | Slugs con `_` (uniforme: personajes, escuadras, facciones, tags). |
| `vinculos[].ref_personaje_id` | `lealtad.pj.{slug}` / `nemesis.pj.{slug}`. |

Los 22 mocks fueron migrados parcialmente en v0.5.0 (al modelo intermedio de bloques de tags). **Pendiente**: re-migración al modelo final de lista plana con notación punto + manejo de la prosa de `vinculos[].descripcion` (que actualmente todavía existe en los mocks).
