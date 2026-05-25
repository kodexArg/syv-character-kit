# API — syv-character-kit

> **Fuente de verdad del contrato HTTP.** Cualquier mención a rutas en `PRD.md`, `docs/*`, mocks o código se resuelve contra este archivo. Si una ruta no figura acá, no existe en el contrato.
>
> Convenciones de payload: ver [`docs/hoja-modelo.md`](docs/hoja-modelo.md) y [`docs/tag-modelo.md`](docs/tag-modelo.md). Idioma: castellano rioplatense.

---

## Convención `GET /meta/{categoria}` — catálogo de tag

Cualquier `GET /meta/{categoria}` devuelve el catálogo canon de esa categoría de tag. La estructura de cada entrada es la definida en [`docs/tag-modelo.yaml`](docs/tag-modelo.yaml). La lista de categorías curadas (`skill`, `trait`, `perk`, `aspecto`, `rasgo`, `equipo.arma`, `equipo.utilitario`, `equipo.vestidura`, `rol.*`, etc.) vive en [`docs/tag-modelo.md §3`](docs/tag-modelo.md).

Categorías nuevas se exponen automáticamente bajo `/meta/{categoria}` el día que existen — no requieren entry en este archivo. Para sub-categorías: `GET /meta/equipo/arma`, `GET /meta/rol/oficio`, etc.

Mapea: UC-09.

**Casos que NO siguen la convención** (porque el payload difiere o agregan datos derivados):

- `GET /meta/factions` — facciones con descriptor de lore corto.
- `GET /meta/rangos` — rangos con tabla de stats, `mando` default, `estado` default, rol cultural por facción (ver PRD §7.2).
- `GET /meta/hito_types` — enum sugerido de tipos de hito (catálogo abierto; lista en [`docs/hoja-modelo.md §5`](docs/hoja-modelo.md)).
- `GET /meta/escuadras/{slug}` — composición de escuadra por query inverso al tag `escuadra.{slug}`. **Fuera de v1 estricto**, sujeto a necesidad.

---

## Personajes

### `GET /character`

Genera un personaje efímero. Parámetros opcionales: `faccion`, `rango`, `seed`, `fields`.

Devuelve un `personaje` con `identidad.slug: null` (los efímeros no tienen slug hasta canonizarse), `historial: []`, `aliados: []`, `nemesis: []`, `metadatos.canonizado_en: null`, y los tags mínimos `estado.disponible` + `escuadra.*` correspondiente.

Mapea: UC-01..04, UC-06, UC-16.

### `GET /character/{slug}`

Devuelve la ficha vigente del personaje con `identidad.slug` exacto. 404 si no existe. Acepta `fields=` para podar.

Mapea: UC-05, UC-15, UC-16.

### `GET /character/{slug}/historial`

Devuelve solo `historial[]`. Sin paginación en v1.

Mapea: UC-17.

### `POST /character/{slug}/event`

Registra un hito. Body: una entrada de `historial[]` (estructura en [`docs/hoja-modelo.md §5`](docs/hoja-modelo.md)). Apendea, aplica efecto sobre campos vigentes, actualiza `metadatos.ultima_actualizacion`, devuelve ficha actualizada. 409 sobre mocks; 404 sobre efímeros.

Mapea: UC-10..14, UC-18.

### `POST /canonize`

Persiste un personaje generado como canon. Asigna `identidad.slug` (patente `[A-Z0-9]{8}` generada del lado servidor), congela `historia`, fija `metadatos.canonizado_en`. Idempotente por `(seed, faccion, rango)`.

Mapea: UC-07.

### `GET /roster/mock`

Lista los 22 fixtures con `slug`, `nombre`, `sobrenombre`, y los tags `faccion.*`, `rango.*`, `rol.*` correspondientes. Sin payload completo.

Mapea: UC-08.

---

## Tabla plana

| Método | Path | UC |
|---|---|---|
| GET | `/character` | 01..04, 06, 16 |
| GET | `/character/{slug}` | 05, 15, 16 |
| GET | `/character/{slug}/historial` | 17 |
| POST | `/character/{slug}/event` | 10..14, 18 |
| POST | `/canonize` | 07 |
| GET | `/roster/mock` | 08 |
| GET | `/meta/{categoria}` | 09 |
| GET | `/meta/factions` | 09 |
| GET | `/meta/rangos` | 09 |
| GET | `/meta/hito_types` | 09 |
