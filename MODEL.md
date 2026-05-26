---
title: "MODEL — syv-character-kit"
tags:
  - syv/model
aliases:
  - MODEL
  - MODEL.md
---

# MODEL — syv-character-kit

> [!info] Contrato de Persistencia
> Lista de entidades, campos, tipos y constraints que cualquier base de datos (relacional, documental, KV) debe poder representar para servir [[API|API.md]] sin pérdida.
> 
> Sub-producto de [[API|API.md]]: si una operación HTTP devuelve un campo, este documento lo tipifica. Si una operación lo muta, este documento marca la regla. **Sincronía absoluta con [[API|API.md]].**
> 
> No prescribe stack. Mismo idioma que el resto del kit: snake_case_castellano, voseo sobrio, tags en notación punto.
> 
> Detalle narrativo del schema en [[hoja-modelo|docs/hoja-modelo.md]] y [[tag-modelo|docs/tag-modelo.md]]. Este documento es la versión esqueleto para implementadores de persistencia.

---

## Entidades

Cuatro entidades persistidas (`personaje`, `tag_catalogo`, `escuadra`, `faccion`) más dos colecciones embebidas (`hito`, `vinculo`). Los demás "entes" del modelo (skills, traits, perks, equipo) son **tags** y viven como entradas de `tag_catalogo`.

---

## 1. `personaje`

Resource principal. Servido por `GET /character/{slug}`, mutado por `POST /character/{slug}/event`, creado por `POST /canonize`.

| Campo | Tipo | Mutable | Notas |
|---|---|---|---|
| `identidad.slug` | `str` `^[A-Z0-9]{8}$` \| `null` | set una vez | PK. `null` en efímeros. Asignada por el servidor al canonizar. |
| `identidad.nombre` | `str` | inmutable | Legible. No único. |
| `identidad.sobrenombre` | `str \| null` | mutable (sin hito) | Derivable; `null` si no aplica. |
| `identidad.rol` | `str` | mutable vía hito `ascenso`/`cambio_rol` | Default `"ciudadano"`. Narrativo, no operativo. |
| `identidad.genero` | `str` | inmutable | Enum abierto: `masculino \| femenino \| no_binario \| otro`. |
| `identidad.edad` | `int` | mutable (sin hito) | Decisión narrativa. |
| `atributos.fis` | `int` (2..5) | vía `triple_cero`/`mejora_atributo` | |
| `atributos.tac` | `int` (2..6) | vía `triple_cero`/`mejora_atributo` | Tope absoluto 6; creación máx 5; vía hito hasta tope. |
| `atributos.men` | `int` (2..7) | vía `triple_cero`/`mejora_atributo` | Tope absoluto 7; creación máx 6; vía hito hasta tope. |
| `tags[]` | `list<str>` (multiset) | vía `agregar_tag`/`quitar_tag` | Notación punto `<categoria>[.<subcategoria>].<slug>`. Admite repetidos. |
| `historia` | `str` | inmutable tras canonizar | 120–200 palabras. Congelada. |
| `historial[]` | `list<hito>` (embebida) | append-only vía `POST /event` | Ver §1.1. |
| `aliados[]` | `list<vinculo>` | mutable vía hito `formacion_lealtad` | Ver §1.2. |
| `nemesis[]` | `list<vinculo>` | mutable vía hito `identificacion_nemesis` | Misma forma que `aliados[]`. |
| `metadatos.creado_en` | `str` ISO-8601 | inmutable | |
| `metadatos.canonizado_en` | `str` ISO-8601 \| `null` | set una vez | `null` en efímeros. |
| `metadatos.ultima_actualizacion` | `str` ISO-8601 | actualiza con cada hito | |
| `extras` | `object \| null` | libre | Escape hatch. La API no inspecciona. |

**Campos derivados** — computados al servir, **no persistidos**:

- `filiacion` — desde tags `rango.*` + `escuadra.*`.
- `fatiga_max` = `fis + men`.
- `moral_max` = `men`.
- `fza_aportada` — desde `rol.combate.*` (`heroe: 3`, `lider: 2`, default `1`).

Aparecen en la response de `GET /character` and `GET /character/{slug}` junto con los campos persistidos. Se recomputan en cada lectura — el cliente no los muta.

### 1.1. `hito` (embebido en `personaje.historial[]`)

| Campo | Tipo | Notas |
|---|---|---|
| `fecha` | `str` ISO-8601 | |
| `tipo` | `str` | Enum abierto. Catálogo sugerido en [[hoja-modelo#§5 — Historial|docs/hoja-modelo.md §5]]. |
| `descripcion` | `str` | Obligatorio. |
| `ref_batalla` | `str \| null` | Slug de batalla externa. |
| `metadata` | `object` | Libre. Convención común: `{ atributo, delta, valor_anterior, valor_nuevo }` para triple-0/mejora; `{ categoria, valor }` para agregar/quitar tag. |

### 1.2. `vinculo` (embebido en `personaje.aliados[]` y `personaje.nemesis[]`)

| Campo | Tipo | Notas |
|---|---|---|
| `ref` | `str` `^[A-Z0-9]{8}$` | Patente de otro `personaje`. Sin FK enforcement (ver T-04). |
| `descripcion` | `str` | Obligatorio. 1–3 frases sobre el vínculo. |
| `desde` | `str` ISO-8601 \| `null` | Opcional. |

---

## 2. `tag_catalogo`

Catálogo de tags curados. Servido por `GET /meta/{categoria}`. Sembrado desde `tags/**/*.yaml` al arrancar.

| Campo | Tipo | Obligatorio | Notas |
|---|---|---|---|
| `slug` | `str` lowercase + underscore | sí | Último segmento del tag. |
| `nombre` | `str` | sí | Label humano. |
| `categoria` | `str` | sí | Primer segmento del tag. |
| `subcategoria` | `str \| null` | si `categoria ∈ {equipo, rol}` | Segmento intermedio. |
| `descripcion` | `str` | sí | 1–3 frases. |
| `origen` | `str` | no (default `emergente`) | Enum: `canon \| emergente \| custom`. |
| `efecto` | `str \| list<str> \| null` | si `categoria = trait` y sin `trigger`; o si `categoria = efecto` | Modificadores sobre vocabulario canónico ([[atributos-y-efectos|docs/atributos-y-efectos.md]]). |
| `trigger` | `object \| null` | no | `{ evento, condicion, probabilidad?, trigger-action[] }`. Ver [[tag-modelo#4.6. Efectos y triggers|tag-modelo.md §4.6]]. |
| `requires` | `object \| null` | no | `{ require_all[], require_any[] }`. Prefijo `"no:"` para NOT. Documentación ejecutable, no validación. |
| `excluye` | `list<str> \| null` | no | Tags incompatibles. |
| `peso` | `int` (0..50) | si `categoria = equipo` | Unidad: kg. |
| `peso_narrativo` | `int` (1..5) | no | Hint al sorteador. |
| `tags_relacionados` | `list<str>` | no | Informativo. |
| `metadatos` | `object` | no | `{ version_introducida, creado_en, ultima_actualizacion }`. |

**Bloques específicos por categoría** (opcionales salvo `(+)` arriba): `equipo_arma`, `equipo_vestidura`, `subfaccion`, `skill`, `perk`. Esquema completo en [docs/tag-modelo.yaml](docs/tag-modelo.yaml).

**PK** sugerida: `(categoria, subcategoria, slug)` o el tag completo en notación punto como string.

**Índice operativo**: inverted index `tag_full → set<personaje.slug>` reconstruido desde `personaje.tags[]` (ver N-01).

---

## 3. `escuadra`

Resource principal de agrupación táctica. Servido por `GET /escuadras/{slug}`, modificado por altas/bajas de miembros.

| Campo | Tipo | Mutable | Notas |
|---|---|---|---|
| `identidad.slug` | `str` lowercase + underscore | inmutable | PK. Coincide con el segmento final del tag `escuadra.{slug}`. |
| `identidad.nombre` | `str` | mutable | Nombre de la escuadra. |
| `identidad.faccion` | `str` (slug de `faccion`) | inmutable | Referencia a la facción. |
| `identidad.tipo` | `str` | inmutable | Tipo de escuadra (ej. `escuadra_de_infanteria`). |
| `miembros[]` | `list<miembro>` (embebida) | mutable | Lista ordenada de integrantes con costo en puntos. |
| `historial[]` | `list<hito_escuadra>` (embebida) | append-only | Log de eventos de la escuadra. |
| `metadatos.creado_en` | `str` ISO-8601 | inmutable | |
| `metadatos.ultima_actualizacion` | `str` ISO-8601 | actualiza con cada cambio | |
| `extras` | `object \| null` | libre | Escape hatch. |

**Campos derivados** — computados al servir, **no persistidos**:

- `fza_total` — Suma de `fza_aportada` de miembros activos (no KIA).
- `cohesion_vigente` — Promedio de `men` de miembros activos (redondeado hacia abajo). Penalizado con `(-2)` si el líder está KIA/licencia sin reemplazo, o `(-1)` si el segundo al mando asume el mando vigente.
- `moral_promedio` — Promedio entero (redondeado hacia abajo) del valor `moral_max` (o Moral actual) de todos los miembros activos.
- `fatiga_promedio` — Promedio entero (redondeado hacia abajo) de la `fatiga_max` de todos los miembros activos.
- `movimiento_tactico` — `min(MOVIMIENTO)` de los miembros activos.
- `puntos_totales` — Suma de `puntos` de todos los miembros (activos e inactivos).
- `lider_vigente` — Patente del personaje currently al mando.
- `estado_escuadra` — `operativa | decapitada | desmembrada | retirada`.
- `cumple_template` — `bool`. Indica si cumple con las restricciones estructurales de su `tipo`.
- `errores_validacion[]` — `list<str>`. Listado de infracciones estructurales si `cumple_template` es falso.

Aparecen en la response de `GET /escuadras/{slug}` y se recomputan en cada lectura.

### 3.1. `miembro` (embebido en `escuadra.miembros[]`)

| Campo | Tipo | Notas |
|---|---|---|
| `ref` | `str` `^[A-Z0-9]{8}$` | Patente del personaje. FK virtual hacia `personaje`. |
| `pos` | `int` | Orden táctico en la formación. |
| `puntos` | `int` | Costo en puntos de reclutamiento (escala 1..5). |
| `rango` | `str` | Slug de rango del personaje (ej. `lider_de_escuadra`). |
| `nombre` | `str` | Nombre compuesto / de guerra del personaje. |

### 3.2. `hito_escuadra` (embebido en `escuadra.historial[]`)

| Campo | Tipo | Notas |
|---|---|---|
| `fecha` | `str` ISO-8601 | |
| `tipo` | `str` | Enum abierto (baja_miembro, ascenso_miembro, combate_finalizado, reorganizacion). |
| `descripcion` | `str` | Obligatorio. |
| `ref_batalla` | `str \| null` | Batalla de referencia si aplica. |
| `metadata` | `object` | Libre. |

---

## 4. `faccion`

| Campo | Tipo | Notas |
|---|---|---|
| `slug` | `str` lowercase + underscore | PK. |
| `nombre` | `str` | Legible. |
| `descripcion` | `str` | Descriptor de lore corto. |

Servido por `GET /meta/factions`. Sembrado desde `tags/faccion/*.yaml`. Conjunto **cerrado-curado**: pocas facciones (2-3 hoy: `confederados`, `ejercito_rojo`), todas canon, todas referenciadas por `escuadra.identidad.faccion` y por la tabla de rangos.

### 4.1. Relación `faccion` ↔ `subfaccion` (asimetría deliberada)

`faccion` and `subfaccion` **no son simétricas**, y la diferencia es de diseño:

| Aspecto | `faccion` | `subfaccion` |
|---|---|---|
| Naturaleza | Entidad de primera clase (esta §4). | Categoría de `tag_catalogo` (§2). |
| Cardinalidad | Cerrado-curado (2-3 hoy). | Abierto-emergente (cualquier grupo táctico, sindicato, célula). |
| Endpoint | `GET /meta/factions` (dedicado). | `GET /meta/subfaccion` (genérico `/meta/{categoria}`). |
| FK desde otras entidades | `escuadra.identidad.faccion`; tabla de rangos. | Ninguna. Solo aparece en `personaje.tags[]`. |
| Forma como membresía sobre personaje | Tag `faccion.{slug}` + `lealtad.faccion.{slug}`. | Tag `subfaccion.{slug}` + `lealtad.subfaccion.{slug}`. |
| Padre | — | `subfaccion.faccion_padre: faccion.{slug}` (campo del tag, ver [[tag-modelo#4.2. Campos obligatorios condicionales — los (+)|docs/tag-modelo.md §4.2]]). |

**Por qué la asimetría es correcta**: `faccion` ancla la geometría operativa del juego (escuadras pertenecen a una facción; los rangos canónicos están definidos por facción; las batallas tienen bandos). Necesita identidad estable y endpoint dedicado. `subfaccion` agrupa narrativamente — un tercio, una célula, un sindicato armado — y el catálogo crece por curaduría a demanda. Forzarla a entidad primera clase infla el modelo sin beneficio; degradar `faccion` a tag rompe las FK existentes.

**Dualidad entidad+tag**: tanto `faccion` como `escuadra` son entidades persistidas **y** existen además como namespace de tag (`faccion.confederados`, `escuadra.{slug}`) para expresar membresía declarativa sobre `personaje.tags[]`. El slug del tag coincide con el PK de la entidad. Esta dualidad es el patrón canónico del kit cuando una entidad es referenciable como membresía narrativa.

**Pertenencia subfaccion → faccion**: vive en el catálogo (`subfaccion.faccion_padre`), no en la hoja del personaje. La hoja taggea ambas independientemente (`faccion.ejercito_rojo` + `subfaccion.ejercito_revolucionario_del_pueblo`); la coherencia entre las dos la sostiene la curaduría (ver invariante "tags fuera de catálogo se aceptan" en §5).

---

## 5. Invariantes globales

- **Mocks son inmutables.** El backend marca los 22 personajes de `mock/personajes/**` como read-only. `POST /character/{slug}/event` → 409.
- **Efímeros no se persisten.** `GET /character` sin canonizar nunca toca la base.
- **Canonización es idempotente solo si hay `seed`.** Con seed presente, la tupla `(seed, faccion, rango)` actúa como llave única y reintentos no crean duplicados. Con seed ausente, cada `POST /canonize` genera un personaje nuevo (no hay idempotencia posible — el sorteo es ciego).
- **`historial[]` es append-only.** No hay reverso de hito en v1 (ver [[PRD#8. Alcance|PRD.md §8]] — "Fuera de este PRD").
- **Tags fuera de catálogo se aceptan.** Cualquier valor en `personaje.tags[]` que no exista en `tag_catalogo` es legal — se persiste tal cual. Curaduría se hace por proceso, no por constraint.
- **Referencias en `aliados[]`/`nemesis[]` no son FK.** Se aceptan refs colgadas (ver T-04).
- **Idioma de los datos**: castellano rioplatense. Tags en lowercase + underscore, sin acentos.
