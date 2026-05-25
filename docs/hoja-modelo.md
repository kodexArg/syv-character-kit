# Hoja Modelo — Referencia narrativa de campos

> **Versión compatible**: schema v0.5.0 (refactor mayor — identidad estable colapsada a `slug`,
> `estado_vital` y `estado_salud` eliminados, bloques `salud` y `mental` como agrupaciones de tags).
> **Propósito**: descripción campo por campo de la hoja de personaje canónica. Para el template
> programático listo para copiar, ver [`docs/hoja-modelo.yaml`](hoja-modelo.yaml).
> **Sistema de tags**: ver [`docs/tag-modelo.md`](tag-modelo.md).

---

## Bloque 1 — Identidad

Quién es el personaje, fuera de su contexto operativo. Datos nominales y biológicos.

**`slug`** — Identificador único del personaje. String estable asignado **en el momento de persistir** (sea fixture mock o registro en base de datos). Reemplaza al trío anterior `{id, origen, semilla}` con un único valor. El slug se genera del lado servidor en la operación de guardado: esto evita race conditions y deja la creación en memoria volátil completamente libre de identificadores hasta que el personaje "se guarde" formalmente. Un slug puede corresponder a un mock (`aguirre-walter`) o a un registro persistido en la DB — el formato no encodea la procedencia, solo identifica. La operación es agnóstica al backend (mock plano vs DB) y conceptual a este nivel del PRD.

**`nombre`** — Nombre real del personaje. String inmutable asignado en creación; no es el título operativo. Ej. `"Walter Aguirre"`.

**`sobrenombre`** — Cómo se lo conoce operativamente. Derivable al servir desde `nombre`, `rango` y tags `rol.*` de mando si aplican. `null` cuando no hay distinción con el nombre real.

**`rol`** — Identidad narrativa base, no posición operativa. String con default `"ciudadano"` para personajes que no son militares activos. Para personajes incorporados a una facción puede mantenerse en `ciudadano` (la capa operativa la cubren los tags `rol.*`) o usarse para anotar la identidad cultural (`"obrero"`, `"campesino"`, `"estudiante"`). **No confundir con tags `rol.*`** (oficio, jerarquía militar, narrativa de combate) que viven en `tags[]`.

**`genero`** — Enum abierto: `"masculino"`, `"femenino"`, `"no_binario"`, `"otro"`.

**`edad`** — Años del personaje al momento de creación. Integer simple, sin mecánica de envejecimiento. Rango sugerido por posición operativa: reclutas 18-24, líderes 28-45.

---

## Bloque 2 — Facción

Cómo está insertado el personaje en la estructura militar/política del mundo. Todos los campos pueden ser `null` para civiles desafiliados.

**`faccion`** — Pertenencia macro. Enum abierto; valores de MVP: `"Confederación"` y `"Ejército Rojo"`. `null` para civiles sin bando declarado. Mutable solo vía hito explícito de cambio de bando.

**`filiacion`** — Cómo se lo presenta dentro de su facción. Derivable al servir como `"{rango} de la {escuadra.nombre} del {escuadra.cuerpo}"` cuando hay datos suficientes. `null` cuando falta `escuadra` o `rango`.

**`escuadra`** — `slug` de la escuadra a la que pertenece. `null` si el personaje está sin asignar o es civil. La API no valida que el slug exista (consistencia por curaduría, no integridad referencial). Mutable vía hito `asignacion_escuadra`.

**`rango`** — Designación operativa de campo. String abierto jerárquico; el motor de batalla lo usa para decidir línea de mando. Valores canon de Confederación: `"Lider de escuadra"`, `"Segundo al mando"`, `"Apuntador"`, `"Artillero"`, `"Fusilero"`, `"Recluta"`. `null` para civiles. Mutable vía hito `cambio_rango`.

**`mando`** — Booleano. ¿El personaje tiene capacidad de mando dentro de su facción? `true` si puede tomar el comando de su escuadra cuando el líder activo cae; `false` si no. La titularidad vigente se deriva (`mando == true AND es el de mayor rango en su escuadra`). Default `true` para líderes y segundos al mando. Mutable vía hito `cambio_mando`.

**`estado`** — Disponibilidad operativa. Enum mutable: `"activo"` (asignado y operativo), `"disponible"` (sin asignar; default en creación), `"kia"` (caído en combate), `"licencia"` (baja temporal). Distinto de los tags de salud (estado físico actual) y mental (estado anímico actual).

---

## Bloque 3 — Atributos

**`atributos`** — Set de tres valores numéricos que definen la capacidad base del personaje. Determinísticos por rango en creación (no se sortean); mutables post-creación solo vía hito `triple_cero` o `mejora_atributo`. Rango 2-5 para `fis` y `tac`; hasta 7 para `men` en líderes.

- **`fis`** (físico) — resistencia, potencia bruta, capacidad de carga.
- **`tac`** (táctico) — precisión, coordinación, reflejos.
- **`men`** (mental) — liderazgo, moral base, resistencia psicológica.

Estos tres atributos son las únicas magnitudes numéricas persistidas del personaje. Toda otra "capacidad" derivada (fatiga máxima, moral máxima, capacidad de mando situacional, etc.) se calcula en caliente por el motor con fórmulas fijas — no se persiste para evitar drift y simplificar la hoja.

---

## Bloque 4 — Salud

**`salud`** — Array de tags que describen el **estado físico actual** del personaje. Reemplaza el campo enumerado `estado_salud` y el bloque `estado_vital` (fatiga numérica) de versiones anteriores. La idea: la fatiga máxima y los pools numéricos los calcula el motor en caliente desde `atributos` (fórmula fija); lo que importa persistir es **qué condiciones actuales tiene encima el personaje**, expresadas como tags.

Catálogo canon del MVP (8 valores):

| Valor | Significado |
|---|---|
| `cansado` | Fatiga leve, primer escalón. |
| `exhausto` | Fatiga severa, penaliza acciones físicas. |
| `agotado` | Borde del colapso; sin reservas. |
| `herido` | Daño físico menor, sin sangrado activo. |
| `malherido` | Daño grave, requiere atención. |
| `sangrando` | Pérdida activa de sangre; empeora con el tiempo. |
| `enfermo` | Condición no traumática (fiebre, infección, intoxicación leve). |
| `aturdido` | Conmoción transitoria; reduce coordinación. |

Es una lista plana de strings; los tags son acumulables (`["herido", "sangrando"]` es válido y describe un personaje que está herido y además sangrando activamente). Los efectos mecánicos de cada tag los define el motor de batalla. Mutable vía hito `cambio_salud`.

---

## Bloque 5 — Mental

**`mental`** — Array de tags que describen el **estado anímico actual** del personaje. Reemplaza el seguimiento numérico de moral (`moral_max` / `moral_actual`). La moral máxima la calcula el motor desde `atributos.men`; lo persistido son las condiciones actuales.

Catálogo canon del MVP (8 valores):

| Valor | Significado |
|---|---|
| `pánico` | Pérdida de control; tiende a huir o congelarse. |
| `confundido` | Dificultad para procesar la situación. |
| `desmoralizado` | Baja convicción; menor disposición a riesgo. |
| `iracundo` | Furia controlada; bonifica ataque, penaliza precisión. |
| `traumatizado` | Cicatriz psicológica de un evento previo. |
| `conmocionado` | Shock agudo post-evento traumático inmediato. |
| `berserker` | Furia descontrolada; tag activable por aspecto `cabrón`. |
| `sereno` | Calma activa bajo presión; estado positivo. |

Como `salud`, es una lista plana acumulable. Mutable vía hito `cambio_mental`.

---

## Bloque 6 — Lealtades

**`lealtades`** — Estructura anidada con tres sub-campos. `primaria` es string; la lealtad principal del personaje (ej. `"Confederación"`, `"Sargento Ricardo (post mortem)"`). `secundarias` es array de strings; lealtades adicionales en orden de importancia. `secretos` es array de strings; lealtades ocultas que el personaje no declara abiertamente. Los tres son mutables vía hito `ruptura_vinculo` o hito manual.

---

## Bloque 7 — Tags

**`tags`** — Lista plana de entidades `{categoria, valor}`. El corazón del schema: todo lo que puede ser tag, es tag (rasgos físicos, habilidades, perks, aspectos, equipo, oficios y jerarquías militares).

**Lo que NO vive en `tags[]`:** identidad (Bloque 1), facción (Bloque 2), atributos (Bloque 3), salud (Bloque 4), mental (Bloque 5), lealtades, vínculos, historia, historial, metadatos, extras. Esos campos tienen tratamiento estructurado propio porque el motor necesita acceso semántico directo sin parsear listas.

Categorías canon: `rasgo`, `trait`, `perk`, `aspecto`, `skill`, familias jerárquicas `equipo.{arma, utilitario, vestidura}` y `rol.{oficio, jerarquia, narrativo, mecanico}` (esta última pendiente, ver OQ-tag-1 en `tag-modelo.md`). Categorías abiertas: se aceptan valores fuera del canon. Los tags son repetibles: tres `cargador` son tres entidades físicas distintas. Cada `valor` es mínimo (1-2 palabras). La definición canónica completa de cada tag vive en `/meta/{categoria}/{slug}` — ver `tag-modelo.md`.

Cambios post-creación se registran como hito `agregar_tag` / `quitar_tag`.

---

## Bloque 8 — Vínculos

**`vinculos`** — Array de relaciones con otros personajes. Cada vínculo tiene `tipo` (string abierto; sugeridos: `mentor`, `subordinado`, `hermano_de_armas`, `rival`, `deuda`, `enemigo_jurado`, `familia`, `romance`), `ref_personaje_slug` (slug del otro personaje o `null` si es externo al corpus), y `descripcion` (string obligatorio; fallback cuando el slug no resuelve). La API no valida que `ref_personaje_slug` exista. Mutable vía hitos `formacion_vinculo` y `ruptura_vinculo`.

---

## Bloque 9 — Historia

**`historia`** — Prosa biográfica original. String de 120-200 palabras escrito por LLM en la creación del personaje en memoria volátil. Al persistir se congela: nunca muta tras el guardado. Escrita en castellano rioplatense, primera persona narrativa. Es el único lugar donde vive la voz del personaje como descripción extendida.

**Nota sobre reproducibilidad**: la prosa es no-determinística por construcción. No existe semilla que la regenere idéntica — se persiste como artefacto, no como derivado. Esta es la razón por la que el campo `semilla` del schema anterior fue eliminado: prometía reproducibilidad que no podía cumplir para el bloque narrativo.

---

## Bloque 10 — Historial

**`historial`** — Array de hitos que registran la memoria viva del personaje persistido. Cada entrada tiene: `fecha` (ISO-8601), `tipo` (string abierto con valores sugeridos), `descripcion` (prose del evento), `ref_batalla` (slug de batalla del motor downstream o `null`), y `metadata` (object libre para datos estructurados del hito). Tipos sugeridos: `triple_cero`, `ascenso`, `herida`, `recuperacion`, `agregar_tag`, `quitar_tag`, `formacion_vinculo`, `ruptura_vinculo`, `traslado`, `condecoracion`, `mejora_atributo`, `cambio_rango`, `cambio_mando`, `cambio_estado`, `cambio_salud`, `cambio_mental`, `asignacion_escuadra`. Personajes recién creados arrancan con `historial: []`.

---

## Bloque 11 — Tags iniciales

**`tags_iniciales`** — Snapshot inmutable de `tags[]` tal como estaba al momento de creación. Array de `{categoria, valor}`. Permite a cualquier cliente calcular el diff entre el estado original y el vigente. Nunca muta.

---

## Bloque 12 — Metadatos

**`metadatos`** — Conjunto de campos de auditoría y trazabilidad.

- **`creado_en`** — ISO-8601, fecha de creación en memoria volátil.
- **`canonizado_en`** — ISO-8601 o `null`. Fecha en que el personaje fue persistido (mock o DB).
- **`ultima_actualizacion`** — ISO-8601; se actualiza con cada hito.

Eliminados respecto a versiones anteriores: `modelo_prosa` (qué LLM escribió la historia — no aporta valor operativo) y `es_canon` (derivable de la presencia de `slug` y `canonizado_en`).

---

## Bloque 13 — Extras

**`extras`** — Escape hatch deliberado. Object libre o `null`. La API no inspecciona ni valida su contenido. **Soporta cualquier llave** y estructura anidada arbitraria. Permite a clientes externos persistir metadatos propios sin romper el schema ni requerir un cambio de versión del PRD.

---

## Cambios respecto a v0.4.1

Refactor mayor — bump a v0.5.0.

| Antes | Ahora |
|---|---|
| `id` + `origen` + `semilla` (Bloque "Identidad estable") | `slug` único en Identidad, generado al persistir |
| Campo `rol` desacoplado en cabecera | Movido a Identidad; default `"ciudadano"`; convive con tags `rol.*` |
| `escuadra_id` | `escuadra` (mismo significado, nombre alineado a "slug") |
| `estado_salud` enum (`saludable|herido|baja`) | Bloque `salud` (array de tags acumulables) |
| `estado_vital` con `fatiga_max/actual` y `moral_max/actual` | Eliminado; el motor calcula pools en caliente. Estado actual = tags en `salud` y `mental` |
| `metadatos.modelo_prosa` y `metadatos.es_canon` | Eliminados |
| `vinculos[].ref_personaje_id` | `vinculos[].ref_personaje_slug` |
| `ref_batalla` en historial (id) | `ref_batalla` (slug) |

Los 22 mocks **no** se editan en este pase — el refactor es solo del schema y la documentación. La adaptación de los soldados existentes queda como tarea separada.
