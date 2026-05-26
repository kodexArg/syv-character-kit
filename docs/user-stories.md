---
title: "User Stories — syv-character-kit"
tags:
  - syv/docs/use-cases
aliases:
  - user-stories
  - Historias de Usuario
---

# User Stories — syv-character-kit

> [!info] Contexto y Casos de Uso
> - **Casos de Uso**: Catálogo de casos de uso del kit. Cada UC se mapea al endpoint que lo satisface en [[API|API.md]]. Si una historia no se puede satisfacer con un endpoint vigente, es señal de drift entre este archivo y [[API|API.md]].
> - **Convención**: El "actor" es siempre un consumidor de la API, no un usuario humano final — el kit no tiene UI propia.

---

## 1. Consumidores

- **Motor de batalla** — pide escuadras y personajes para escenarios; reporta hitos (triple-0, baja, captura).
- **Generador de escenarios** — pide PNJs filtrados por facción/rango/tag.
- **Sitio de lore** — muestra galerías de canonizados y líneas de tiempo.
- **Redactor narrativo** — canoniza personajes notables y agrega hitos manuales.
- **Curador de canon** — promueve efímeros, audita el roster.
- **Pipeline de QA** — corre el motor sobre los 22 mocks; verifica catálogos.

---

## 2. Catálogo de UC

| # | Como… | Quiero… | Para… | Endpoint |
|---|---|---|---|---|
| UC-01 | motor de batalla | pedir un personaje al azar | rellenar un slot vacío | `GET /character` |
| UC-02 | generador de escenarios | pedir un personaje por facción | poblar una escuadra de Ejército Rojo | `GET /character?faccion=` |
| UC-03 | sitio de lore | pedir un personaje por rango | mostrar "un sargento típico" | `GET /character?rango=` |
| UC-04 | redactor narrativo | combinar facción + rango | un Camarada Puntero específico | `GET /character?faccion=&rango=` |
| UC-05 | motor de batalla | pedir personaje exacto por slug | recargar al Sargento Aguirre | `GET /character/{slug}` |
| UC-06 | redactor | regenerar efímero con la misma seed | discutir variantes sin perder el original | `GET /character?seed=` |
| UC-07 | curador de canon | canonizar un personaje generado | entidad permanente del corpus | `POST /canonize` |
| UC-08 | herramienta de QA | listar todos los mocks | correr el motor sobre la población canon | `GET /roster/mock` |
| UC-09 | cualquier cliente | consultar catálogos curados | construir UIs sin hardcodear enums | `GET /meta/{categoria}` |
| UC-10 | motor de batalla | registrar triple-0 sobre canonizado | reflejar +1 en atributo | `POST /character/{slug}/event` |
| UC-11 | redactor | registrar ascenso narrativo | que la próxima `GET` muestre el nuevo rango | `POST /character/{slug}/event` |
| UC-12 | motor de batalla | registrar formación de vínculo | que ambos personajes lo recuerden | `POST /character/{slug}/event` |
| UC-13 | motor de batalla | registrar captura de arma enemiga | que el equipo vigente la incluya | `POST /character/{slug}/event` |
| UC-14 | redactor | registrar ruptura de lealtad | que pase a tener secreto o némesis | `POST /character/{slug}/event` |
| UC-15 | sitio de lore | pedir el mismo canonizado en t1 y t2 | mostrar evolución | `GET /character/{slug}` (dos veces) |
| UC-16 | cualquier cliente | pedir ficha con `?fields=` podada | bajar payload | `GET /character?fields=` |
| UC-17 | sitio de lore | pedir el `historial[]` | renderizar línea de tiempo | `GET /character/{slug}/historial` |
| UC-18 | curador | asignar personaje a escuadra | derivar `filiacion` y `estado: activo` | `POST /character/{slug}/event` |
| UC-19 | motor de batalla | filtrar por tag `skill: Francotirador` | armar pelotón de tiradores | `GET /character?tag=skill.francotirador` |
| UC-20 | redactor narrativo | pedir personaje con `trait.miope` | forzar complicación visual | `GET /character?tag=trait.miope` |
| UC-21 | editor de canon | listar todos los `equipo.arma` del roster | auditar inventario armamentístico | `GET /roster/mock` + filtro cliente |
| UC-22 | motor de batalla | filtrar `rol.lider` AND `faccion.confederados` | candidatos al mando ante caída del líder | `GET /character?tag=rol.lider&tag=faccion.confederados` |
| UC-23 | QA | consultar `/meta/tag_categories` | verificar que el generador no produce tags fuera del catálogo | `GET /meta/{categoria}` |
| UC-24 | motor de batalla | pedir la composición y valores calculados de una escuadra | evaluar su moral o movimiento | `GET /escuadras/{slug}` |
| UC-25 | curador | crear una nueva escuadra | registrar una unidad en campaña | `POST /escuadras` |
| UC-26 | motor de batalla | añadir un combatiente a una escuadra | reflejar un refuerzo táctico | `POST /escuadras/{slug}/miembro` |
| UC-27 | motor de batalla | remover un combatiente de una escuadra | registrar una baja o traslado | `DELETE /escuadras/{slug}/miembro/{char_slug}` |

---

## 3. Operaciones por endpoint

Vista inversa: para cada endpoint, qué UCs satisface. Sincroniza 1:1 con la tabla plana de [[API|API.md]].

| Método | Path | UCs |
|---|---|---|
| GET | `/character` | 01..04, 06, 16, 19, 20, 22 |
| GET | `/character/{slug}` | 05, 15, 16 |
| GET | `/character/{slug}/historial` | 17 |
| POST | `/character/{slug}/event` | 10..14, 18 |
| POST | `/canonize` | 07 |
| GET | `/roster/mock` | 08, 21 |
| GET | `/meta/{categoria}` | 09, 23 |
| GET | `/escuadras` | 24 |
| GET | `/escuadras/{slug}` | 24 |
| POST | `/escuadras` | 25 |
| POST | `/escuadras/{slug}/miembro` | 26 |
| DELETE | `/escuadras/{slug}/miembro/{char_slug}` | 27 |

---

## 4. Restricciones y bordes

Comportamientos que el cliente debe asumir al invocar.

- **Mocks son inmutables.** `POST /character/{slug}/event` sobre cualquiera de los 22 mocks devuelve **409**. Su evolución, si la hay, ocurre por reescritura del fixture.
- **Efímeros no aceptan eventos.** Sin slug persistido, `POST /character/{slug}/event` devuelve **404**.
- **Canonización es idempotente** por `(seed, faccion, rango)`. Reintentos no crean duplicados.
- **`identidad.slug` es opaco.** El cliente nunca lo construye; siempre se lo da el servidor al canonizar.
- **`?fields=` poda solo top-level**. No es JSON-pointer; no atraviesa subdocs.
- **Filtros `?tag=` admiten repetición** para AND lógico (`?tag=A&tag=B`). OR no está soportado en v1; el cliente lo resuelve con N calls + unión.
- **Hitos custom son legales.** El `tipo` de hito es enum abierto; el motor downstream interpreta los desconocidos como no-op sobre campos vigentes.
- **Vínculos personales (`aliados[]`, `nemesis[]`) no se filtran**. No hay `?tag=` para ellos — viven en colecciones, no en `tags[]`.

