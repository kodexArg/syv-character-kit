# Changelog

## [0.3.0] - 2026-05-24
### Added
- Materialización de los 22 personajes mock (11 Confederación + 11 Ejército Rojo) como archivos YAML en `mock/personajes/{faccion}/{nn}_{apellido}.yaml`
- Conformidad total al schema v0.2.0/v0.2.1
- Transcripción fiel desde `/Dev/syv-battle-game-system/personajes/` enriquecida con campos nuevos
- Campos incluidos: edad, género, origen geográfico, apariencia estructurada, lealtades, vínculos intra-escuadra, historial retrospectivo, equipo táctico minimal
- Distribución de género: 3 mujeres + 1 no-binario en Confederación, 2 mujeres en Ejército Rojo
- 32 vínculos intra-escuadra documentados
- Vínculo asimétrico canon Mansilla→Aguirre como `rival`
- Total: 2215 líneas YAML

## [0.2.5] - 2026-05-24
### Changed
- Delta v0.2.3 — Rango ≠ Rol: `rol_id` removido del payload público (pasa a interno del motor); `mando` migrado de enum {titular|suplente|no_apto} a `bool` (capacidad), con la titularidad actual derivada de (mando=true AND mayor rango en la escuadra); `estado_salud` valor `activo` renombrado a `saludable` para no chocar con el nuevo campo `estado`.
- Delta v0.2.4 — Aspectos disueltos en tags: bloque `aspectos` eliminado entero. Sus contenidos migran a tres nuevas categorías canon de tags: `skill` (habilidades), `trait` (rasgos sin polaridad fija — incluye lo que antes eran complicaciones), `perk` (ventajas activables). `equipo` reformulado: armas/utilitarios/armaduras se expresan como tags con categoría jerárquica `equipo.arma`, `equipo.utilitario`, `equipo.armadura`. `fza_aportada` y `equipo.armor` pasan a regla derivada (no persistidos).
- Delta v0.2.5 — Escuadra y filiación: `peloton` renombrado a `escuadra`; `nombre_de_campo` renombrado a `sobrenombre`; nueva entidad implícita `escuadra` con id+nombre+cuerpo+facción; nuevo campo derivado `filiacion` (provisorio) que compone "{rango} de la {escuadra.nombre} del {escuadra.cuerpo}". Orden definitivo de cabecera: nombre → sobrenombre → filiacion → facción → datos biológicos → rol → estado → rango → escuadra → mando.

### Added
- Sección nueva "Hoja ASCII de referencia" con el ejemplo del Comandante Miguel Quilodrán (Líder Revolucionario, Escuadra Mardones del ERP) aprobado por el cliente como representación visual canónica.
- Píldora de arquitectura nueva sobre tags como inverted index, afinidad NoSQL/document-store.
- Tensión nueva sobre traits sin polaridad explícita.
- 4 open questions nuevas (nombre final de `filiacion`, polaridad de traits, derivación de `armor` total, endpoint `/meta/escuadras`).

### Removed
- Campos `rol_id`, `origen_geografico`, `fza_aportada` (como persistido), `especialidad`, `nombre_de_campo`, `equipo.armor` (escalar).
- Bloque entero `aspectos`.
- Enum `mando: {titular|suplente|no_apto}`, valor `activo` de `estado_salud`.

### Notes
- Los 22 mocks materializados (v0.3.0) siguen al schema v0.2.0/v0.2.1 y requieren regeneración al schema v0.2.5 en iteración separada.

## [0.2.2] - 2026-05-24
### Changed
- Reforma estructural completa del schema de personaje
- Identidad nominal desdoblada: `nombre` (identidad real) separado de `nombre_de_campo` (cómo se conoce a la unidad), más `especialidad` para Ejército Rojo que define el título de campo
- Sistema de mando desacoplado de `rol_id`: nuevo enum `mando: {titular | suplente | no_apto}` permite múltiples unidades del mismo `rol_id` en la escuadra con una sola titular vigente
- Sistema híbrido unificado: bloques `apariencia`, `equipo.armas[]` y `equipo.equipo_tactico[]` eliminados; unificación bajo `tags: array<{categoria, valor}>` repetibles y agrupables por categoría
- Categorías canon de tags: `rasgo`, `equipo`, `rol`; abiertas a nuevas categorías
- `tags_iniciales` redefinido como snapshot completo de `tags[]` al momento de creación
- `equipo.armor` queda como único campo escalar residual

### Added
- Nuevo rol canon `lider_revolucionario` para Ejército Rojo
- Sección "Píldoras de arquitectura" con nota sobre afinidad NoSQL/document-store
- Open question #5 sobre versionado y curación de categorías canon de tags

### Removed
- Bloque `apariencia` (breaking change)
- `equipo.armas[]` (breaking change)
- `equipo.equipo_tactico[]` (breaking change)
- Campo `tag_rol` (breaking change)

### Notes
- Los 22 mocks materializados (v0.3.0) quedan al schema v0.2.0/v0.2.1 y requieren regeneración en iteración separada

## [0.2.1] - 2026-05-24
### Changed
- Cierre taxativo de 4 open questions del PRD v0.2.0
- Edad es `integer` simple sin mecánica de envejecimiento; tipos de hito `cumpleaños` y `paso_del_tiempo` eliminados
- Historial sin límite, inline completo (no fragmentado)
- Cambios de `rol_id` post-creación realinean `tag_rol` y `fza_aportada` sin tocar atributos (los atributos son propiedad del personaje, no del rol)
- `POST /canonize` es idempotente por la tripleta `(seed, faccion, rol_id)`

### Fixed
- Resolución de ambigüedades sobre mutabilidad de edad y evolución temporal
- Clarificación de invariantes post-cambio-de-rol

### Opened
- 4 open questions pendientes: gobernanza de `POST /event`, mutabilidad fina de apariencia, interpretación de customs por motor, endpoint `GET /character/{id}/original`

## [0.2.0] - 2026-05-24
### Changed
- Reescritura completa del PRD introduciendo el concepto de "memoria viva con experiencia"
- Los personajes canonizados evolucionan, acumulan hitos, suben atributos, mutan vínculos y equipamiento
- Identidad expandida: edad, género, origen, apariencia, lealtades estructuradas
- Historial de hitos con metadata libre
- Vínculos a otros personajes
- Equipo táctico
- Bloque extras para extensibilidad

### Fixed
- Cierre de 4 open questions del v0.1.0:
  - Canonización solo en DB
  - Historia LLM se congela
  - Sin versionado de payload por SOLID/open-close
  - Restricción de perks por rol soft 80/20

### Added
- 5 tensiones explícitas documentadas
- Múltiples bloques nuevos para soporte de evolución de personajes

### Removed
- `version_canon` (breaking change)
- `armas[].nota` (breaking change)

## [0.1.0] - 2026-05-23
### Added
- PRD inicial de syv-character-kit MVP
- Schema base de personaje con 6 roles canon
- Tabla de 22 mocks: 11 Confederación + 11 Ejército Rojo
- Reglas de generación dinámica con seed reproducible
- Endpoints de alto nivel
- 8 open questions documentadas
