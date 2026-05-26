---
title: "API — syv-character-kit"
tags:
  - syv/api
aliases:
  - API
  - API.md
---

# API — syv-character-kit

> [!info] Fuente de Verdad del Contrato HTTP
> Cualquier mención a rutas en [[PRD|PRD.md]], `docs/*`, mocks o código se resuelve contra este archivo. Si una ruta no figura acá, no existe en el contrato.
> 
> Convenciones de payload: ver [[hoja-modelo|docs/hoja-modelo.md]] y [[tag-modelo|docs/tag-modelo.md]]. Idioma: castellano rioplatense.

---

## Convención `GET /meta/{categoria}` — catálogo de tag

Cualquier `GET /meta/{categoria}` devuelve el catálogo canon de esa categoría de tag. La estructura de cada entrada es la definida en [docs/tag-modelo.yaml](docs/tag-modelo.yaml). La lista de categorías curadas (`skill`, `trait`, `perk`, `rasgo`, `equipo.arma`, `equipo.utilitario`, `equipo.vestidura`, `rol.*`, etc.) vive en [[tag-modelo#§3 — Categorías de referencia|docs/tag-modelo.md §3]].

Categorías nuevas se exponen automáticamente bajo `/meta/{categoria}` el día que existen — no requieren entry en este archivo. Para sub-categorías: `GET /meta/equipo/arma`, `GET /meta/rol/oficio`, etc.

Las sub-categorías se exponen con barras (`/meta/equipo/arma`), no con punto. La notación punto (`equipo.arma`) es solo del tag interno.

Mapea: UC-09.

**Casos que NO siguen la convención** (porque el payload difiere o agregan datos derivados):

- `GET /meta/factions` — facciones con descriptor de lore corto.
- `GET /meta/rangos` — rangos con tabla determinística de stats, `mando` default y rol cultural por facción. Tabla canónica en [[01-flujo-obligatorio-creacion#Fase 3 — Atributos|gddr/01-flujo-obligatorio-creacion.md §3]].
- `GET /meta/hito_types` — enum sugerido de tipos de hito (catálogo abierto; lista en [[hoja-modelo#§5 — Historial|docs/hoja-modelo.md §5]]).

---

## Personajes

### `GET /character`

Genera un personaje efímero. Parámetros opcionales: `faccion`, `rango`, `seed`, `fields`, `tag`. `fields` recibe dot-paths separados por coma: `fields=identidad.slug,atributos.fis`.

- `tag` admite repetición para filtrado en AND lógico (`?tag=skill.francotirador&tag=rol.lider`). El valor debe ser un tag completo en notación punto. OR no está soportado en v1 — el cliente lo resuelve con N calls + unión.
- Aplica al sorteo: el efímero generado debe portar todos los tags exigidos. Si la combinación es inviable, devuelve **409**.

Devuelve un `personaje` con `identidad.slug: null` (los efímeros no tienen slug hasta canonizarse), `historial: []`, `aliados: []`, `nemesis: []`, `metadatos.canonizado_en: null`, y los tags mínimos `estado.disponible` + `escuadra.*` correspondiente.

Mapea: UC-01..04, UC-06, UC-16, UC-19, UC-20, UC-22.

### `GET /character/{slug}`

Devuelve la ficha vigente del personaje con `identidad.slug` exacto. 404 si no existe. Acepta `fields=` (dot-paths CSV, ej. `fields=identidad.slug,identidad.nombre,atributos.fis`) para podar. Incluye los campos derivados (`filiacion`, `fatiga_max`, `moral_max`, `fza_aportada`) definidos en [[MODEL#1. personaje|MODEL.md §1]].

Mapea: UC-05, UC-15, UC-16.

### `GET /character/{slug}/historial`

Devuelve solo `historial[]`. Sin paginación en v1.

Mapea: UC-17.

### `POST /character/{slug}/event`

Registra un hito. Body: una entrada de `historial[]` (estructura en [[hoja-modelo#§5 — Historial|docs/hoja-modelo.md §5]]). Apendea, aplica efecto sobre campos vigentes, actualiza `metadatos.ultima_actualizacion`, devuelve ficha actualizada. 409 sobre mocks; 404 sobre efímeros.

Mapea: UC-10..14, UC-18.

### `POST /canonize`

Persiste un personaje generado como canon. Asigna `identidad.slug` (patente `[A-Z0-9]{8}` generada del lado servidor), congela `historia`, fija `metadatos.canonizado_en`. Idempotente por `(seed, faccion, rango)`.

Mapea: UC-07.

### `GET /roster/mock`

Lista los 22 fixtures con `slug`, `nombre`, `sobrenombre`, y los tags `faccion.*`, `rango.*`, `rol.*` correspondientes. Sin payload completo.

Mapea: UC-08.

---

## Escuadras

### `GET /escuadras`
Lista todas las escuadras persistidas. Acepta parámetro opcional `faccion` para filtrar.

### `GET /escuadras/{slug}`
Devuelve la ficha detallada de la escuadra con el `slug` exacto. Incluye todos los campos de identidad (incluyendo `tipo`), la lista de `miembros[]` (con sus `puntos_pagados`), la lista `historial[]` de hitos, y los campos calculados dinámicamente (`fza_total`, `cohesion_vigente`, `moral_promedio`, `fatiga_promedio`, `movimiento_tactico`, `puntos_totales`, `lider_vigente`, `estado_escuadra`, `cumple_template`, `errores_validacion[]`).

Mapea: UC-24.

### `POST /escuadras`
Crea y persiste una nueva escuadra. El body debe incluir la estructura de identidad (incluyendo `tipo`) y opcionalmente una lista inicial de miembros e historial.

Mapea: UC-25.

### `POST /escuadras/{slug}/miembro`
Añade un personaje como miembro de la escuadra.
- Body: `{ "ref": "PATENTE", "pos": int, "puntos": int }`.
- Efecto colateral: Añade la patente, posición (`pos`), costo en puntos (`puntos`), rango y nombre a la lista `miembros[]` de la escuadra, añade los tags `escuadra.{slug}` and `lealtad.escuadra.{slug}` a la hoja del personaje, y registra un hito `asignacion_escuadra` tanto en el `historial[]` del personaje como en el `historial[]` de la escuadra.

Mapea: UC-26.

### `DELETE /escuadras/{slug}/miembro/{char_slug}`
Remueve a un miembro de la escuadra.
- Efecto colateral: Quita la referencia de `miembros[]` en la escuadra, elimina los tags `escuadra.{slug}` y `lealtad.escuadra.{slug}` del personaje, y registra un hito de `traslado` en el `historial[]` del personaje y un hito de `reorganizacion` (baja de miembro) en el `historial[]` de la escuadra.

Mapea: UC-27.

---

## Tabla plana

| Método | Path | UC |
|---|---|---|
| GET | `/character` | 01..04, 06, 16, 19, 20, 22 |
| GET | `/character/{slug}` | 05, 15, 16 |
| GET | `/character/{slug}/historial` | 17 |
| POST | `/character/{slug}/event` | 10..14, 18 |
| POST | `/canonize` | 07 |
| GET | `/roster/mock` | 08, 21 |
| GET | `/meta/{categoria}` | 09, 23 |
| GET | `/meta/factions` | 09 |
| GET | `/meta/rangos` | 09 |
| GET | `/meta/hito_types` | 09 |
| GET | `/escuadras` | 24 |
| GET | `/escuadras/{slug}` | 24 |
| POST | `/escuadras` | 25 |
| POST | `/escuadras/{slug}/miembro` | 26 |
| DELETE | `/escuadras/{slug}/miembro/{char_slug}` | 27 |

Catálogo completo de UCs en [[user-stories|docs/user-stories.md]].
