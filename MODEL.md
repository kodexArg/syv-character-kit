# MODEL — syv-character-kit

> **Contrato de persistencia.** Lista de entidades, campos, tipos y constraints que cualquier base de datos (relacional, documental, KV) debe poder representar para servir [`API.md`](API.md) sin pérdida.
>
> Sub-producto de `API.md`: si una operación HTTP devuelve un campo, este documento lo tipifica. Si una operación lo muta, este documento marca la regla. **Sincronía absoluta con `API.md`.**
>
> No prescribe stack. Mismo idioma que el resto del kit: snake_case_castellano, voseo sobrio, tags en notación punto.
>
> Detalle narrativo del schema en [`docs/hoja-modelo.md`](docs/hoja-modelo.md) y [`docs/tag-modelo.md`](docs/tag-modelo.md). Este documento es la versión esqueleto para implementadores de persistencia.

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

Aparecen en la response de `GET /character` y `GET /character/{slug}` junto con los campos persistidos. Se recomputan en cada lectura — el cliente no los muta.

### 1.1. `hito` (embebido en `personaje.historial[]`)

| Campo | Tipo | Notas |
|---|---|---|
| `fecha` | `str` ISO-8601 | |
| `tipo` | `str` | Enum abierto. Catálogo sugerido en [`hoja-modelo.md §5`](docs/hoja-modelo.md). |
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
| `efecto` | `str \| list<str> \| null` | si `categoria = trait` y sin `trigger`; o si `categoria = efecto` | Modificadores sobre vocabulario canónico ([`atributos-y-efectos.md`](docs/atributos-y-efectos.md)). |
| `trigger` | `object \| null` | no | `{ evento, condicion, probabilidad?, trigger-action[] }`. Ver [`tag-modelo.md §4.6`](docs/tag-modelo.md). |
| `requires` | `object \| null` | no | `{ require_all[], require_any[] }`. Prefijo `"no:"` para NOT. Documentación ejecutable, no validación. |
| `excluye` | `list<str> \| null` | no | Tags incompatibles. |
| `peso` | `int` (0..50) | si `categoria = equipo` | Unidad: kg. |
| `peso_narrativo` | `int` (1..5) | no | Hint al sorteador. |
| `tags_relacionados` | `list<str>` | no | Informativo. |
| `metadatos` | `object` | no | `{ version_introducida, creado_en, ultima_actualizacion }`. |

**Bloques específicos por categoría** (opcionales salvo `(+)` arriba): `equipo_arma`, `equipo_vestidura`, `subfaccion`, `skill`, `perk`. Esquema completo en [`docs/tag-modelo.yaml`](docs/tag-modelo.yaml).

**PK** sugerida: `(categoria, subcategoria, slug)` o el tag completo en notación punto como string.

**Índice operativo**: inverted index `tag_full → set<personaje.slug>` reconstruido desde `personaje.tags[]` (ver N-01).

---

## 3. `escuadra`

Entidad implícita. Schema pendiente (ver OQ-06). Forma mínima asumida hasta entonces:

| Campo | Tipo | Notas |
|---|---|---|
| `slug` | `str` lowercase + underscore | PK. Coincide con el segmento final del tag `escuadra.{slug}`. |
| `nombre` | `str` | Legible. |
| `cuerpo` | `str` | Pertenencia organizacional. |
| `faccion_padre` | `str` (slug de `faccion`) | Referencia. |

Composición vigente se reconstruye via inverted index sobre `personaje.tags[]` filtrando por `escuadra.{slug}`.

---

## 4. `faccion`

| Campo | Tipo | Notas |
|---|---|---|
| `slug` | `str` lowercase + underscore | PK. |
| `nombre` | `str` | Legible. |
| `descripcion` | `str` | Descriptor de lore corto. |

`subfaccion` sigue el mismo modelo, con campo adicional `faccion_padre: str`. Vive en `tag_catalogo` bajo `categoria = subfaccion`.

---

## 5. Invariantes globales

- **Mocks son inmutables.** El backend marca los 22 personajes de `mock/personajes/**` como read-only. `POST /character/{slug}/event` → 409.
- **Efímeros no se persisten.** `GET /character` sin canonizar nunca toca la base.
- **Canonización es idempotente solo si hay `seed`.** Con seed presente, la tupla `(seed, faccion, rango)` actúa como llave única y reintentos no crean duplicados. Sin seed, cada `POST /canonize` genera un personaje nuevo (no hay idempotencia posible — el sorteo es ciego).
- **`historial[]` es append-only.** No hay reverso de hito en v1 (ver [`PRD.md §8`](PRD.md) — "Fuera de este PRD").
- **Tags fuera de catálogo se aceptan.** Cualquier valor en `personaje.tags[]` que no exista en `tag_catalogo` es legal — se persiste tal cual. Curaduría se hace por proceso, no por constraint.
- **Referencias en `aliados[]`/`nemesis[]` no son FK.** Se aceptan refs colgadas (ver T-04).
- **Idioma de los datos**: castellano rioplatense. Tags en lowercase + underscore, sin acentos.
