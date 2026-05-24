# Changelog

## [0.4.1] - 2026-05-24
### Changed
- Todos los tags del sistema reducidos a forma mínima (1-2 palabras, sin prosa interna, sin paréntesis, sin guiones largos, sin comas). Principio rector: el tag es identificador; el contexto narrativo vive en `historia`, en el catálogo `/meta/*`, o en una futura entidad `notas`.
- Aplicado en los 22 mocks YAML más ejemplos Aguirre y Mansilla del PRD más hoja ASCII canónica del Comandante Miguel. Total 638 tags mantenidos (igual count); valores únicos consolidados de 190 a 159 por eliminación de sinónimos: `Oratoria de muelle` + `Oratoria sindical` → `Oratoria`; `Manejo de FAP Confederado M2A` + `Manejo de FAP Modelo 45` + `Carga del FAP` → `Manejo de ametralladora`; `cargador 7.62` + `cargador 9mm` + `cargador 7.65 Mauser` + `cargador 7.92 Mauser` → `cargador`; entre otros.
- Información contextual incrustada en tags eliminada (`brújula de oficial — regalo del instructor de Stroeder`, `cuaderno de campaña — anotaciones de terreno, firma con la inicial R en el margen`, calibres de cargador, modelos específicos de armas). Lo documentado en prosa de `historia` se preserva; lo solo incrustado en tag y no en prosa se acepta como pérdida funcional — costo del minimalismo.

### Added
- Tensión 13.11 al PRD: trade-off entre tag mínimo y riqueza contextual.
- OQ #16 nueva: futura entidad `notas: array<{tag_ref, texto}>` como capa enriquecida opcional para tags que ameriten contexto persistido.
- OQ #13 (cargadores genéricos) marcada resuelta: genericidad a `cargador` implícitamente cierra la pregunta de simetría con armas.

### Notes
- Commits: `a1d5e66` y merge `d385875` (2026-05-24).
- PRD bumped a v0.4.1 (parche, refinamiento). PRD ahora 1550 líneas. Total tags semilla canon: 80 (sin cambios).
- Validación con script Python: cero tags con paréntesis, guiones largos, comas; máximo 4 palabras solo en nombres propios canon (Brazo derecho funcional, Arma pesada sin dotación, Veterano de flanqueo). 22 mocks parseables.

## [0.4.0] - 2026-05-24
### Added
- Categoría `aspecto` promovida de "reservada" (v0.3.0 sección 16) a implementación efectiva. Pool semilla de 10 aspectos canon: 3 dados por el cliente (`cabrón`, `ojo-de-halcón`, `muy-fuerte`) más 7 curados (`cobarde`, `carismático`, `terco`, `veloz`, `veterano-cicatrizado`, `devoto`, `impredecible`). Cada aspecto es un tag corto kebab-case con efecto mecánico embebido como mini-frase (probabilístico, condicional, bonus, o activa otros tags).
- Nuevo bloque ASPECTOS en la hoja ASCII canónica del Comandante Miguel (`[cabrón]`). Ejemplo Aguirre con aspecto `ojo-de-halcón` (coherente con su skill "Lectura de terreno boscoso"). Ejemplo Mansilla con aspecto `carismático` (coherente con su skill "Oratoria sindical").
- Endpoint `/meta/aspectos` con los 10 aspectos canon, formato `{valor, efecto, activa_tag?}`. Campo `activa_tag` opcional estructurado para los aspectos que disparan tags transitorios (`berserker`, `pánico`); el resto deja el efecto como string libre.
- Tipos de hito `agregar_aspecto` y `quitar_aspecto` con `metadata: {valor, motivo}` en sección 9.5. Aspectos son mutables como skills/traits/perks.
- Patrón implícito de tags activables (`berserker`, `pánico`) reconocido como sub-categoría conceptual `estado_temporal`. No canonizado con valores fijos; el motor downstream los identifica por nombre.

### Changed
- Sección 16 promovida de "Próximas olas — preview de aspectos" a "Aspectos — capa narrativa-mecánica". Contexto histórico preservado. Apuntada como próxima ola especulativa: aspectos largos al estilo H.I.T.O.S./Cultos Innombrables clásico (frases narrativas de 10-25 palabras), distintos de los aspectos cortos canon de v0.4.0.

### Notes
- Commits: `1cb98ab` y merge `02acc20` (2026-05-24).
- PRD bumped a v0.4.0 (mayor — feature nueva). PRD ahora 1525 líneas. Total tags semilla: 80 (70 + 10 aspectos).
- Los 22 mocks en `mock/personajes/` NO fueron tocados — aspectos solo se materializan en los 2 ejemplos del PRD y en la hoja ASCII de Miguel. Ola separada (futura) puede agregar aspectos al corpus de 22.
- Tensión 13.10 nueva sobre efecto en texto libre (motor debe interpretar mini-frase, igual que customs de perks). OQ #14 nueva sobre polaridad explícita de aspectos. OQ #15 nueva sobre versionado del catálogo `/meta/aspectos`.
- Diferencia formal documentada: `aspecto` (tag con efecto mecánico) vs `trait` (sin efecto mecánico) vs `perk` (pool fijo del reglamento).

## [0.3.2] - 2026-05-24
### Fixed
- Header de la hoja ASCII canónica de Miguel sincronizado a schema v0.3.1 (decía v0.2.5 porque el worker de v0.3.0/v0.3.1 no bumpeó esa referencia interna).

### Removed
- OQs #4 (restricción de perks por rol — cerrada por subordinación) y #14 (futuro de `armor` — cerrada con resolución eliminación) eliminadas de la sección Open Questions. OQs restantes renumeradas (15 → 13 vivas).
- Bullet duplicado de `fza_aportada` (la regla de derivación estaba documentada dos veces).

### Changed
- Tabla 7.11 "Pool curado rango × facción" actualizada con los 6 valores genéricos del catálogo `equipo.arma` v0.3.1. Columnas de "alcance" eliminadas donde el valor genérico las hacía redundantes.
- Referencias a OQ #14 en texto activo actualizadas; menciones en changelog histórico conservadas como registro válido.

### Notes
- PRD pasó de 1417 a 1421 líneas. El delta positivo viene del propio bloque de changelog v0.3.2; el cuerpo del PRD se redujo unas 4 líneas netas.
- Preservadas: referencias intencionales a "Artillero FAP" como nombre cultural del rol (no tag de arma) y "Manejo de FAP" como nombre de skill canon (no tag de arma).
- Sin cambios al sistema de tags ni al catálogo `/meta/*`. Sin tocar los 22 mocks.

## [0.3.1] - 2026-05-24
### Changed
- Catálogo `equipo.arma` rectificado de 10 valores específicos (Fusil FAL, FAP, Subfusil Halcón, Mauser 1909, etc.) a 6 genéricos: `pistola`, `revolver`, `rifle`, `rifle militar`, `SMG`, `ametralladora`. Coherente con la rectificación previa de vestidura. Detalle específico (calibre, modelo, óptica) se difumina; la diferenciación mecánica de tipos pesados (artilleros) se preserva con `ametralladora` como sexto tag.
- 22 YAMLs normalizados con el nuevo catálogo. Distribución resultante: 30 `rifle militar`, 12 `SMG`, 4 `pistola`, 4 `ametralladora`, 0 `rifle`, 0 `revolver`. `rifle` y `revolver` quedan en catálogo sin uso actual (disponibles para personajes futuros).
- "Cuchillo de campo" (Funes) y "Cuchillo de trabajo" (Calfucurá) movidos de `equipo.arma` a `equipo.utilitario` — no son armas de fuego, no encajan en el catálogo nuevo, pero son equipamiento narrativo legítimo.

### Removed
- Del catálogo de armas — bayoneta y granada de mano (implícitas en rifle militar / pueden aparecer como tags emergentes si la prosa lo justifica).

### Added
- OQ #15 — "¿Cargadores por calibre (7.62, 9mm, 7.65) deberían también generizarse a `munición rifle` / `munición pistola` / `munición SMG`? La rectificación de armas abre la pregunta de simetría. Sin decidir."

### Notes
- PRD bumped a v0.3.1. PRD ahora 1417 líneas. Total tags semilla: 70 (74 − 4 por armas: de 10 a 6).

## [0.3.0] - 2026-05-24
### Removed
- Concepto `armor` eliminado del sistema entero. Sin armaduras estructurales, sin defensa numérica. Cerrada OQ #14 con resolución (a). Si en el futuro hace falta defensa, vuelve como tag `trait: blindado` o derivado de skill defensiva.

### Changed
- "Fusil de cerrojo Springfield 1903 con mira" reemplazado por "Fusil Mauser 1909 con mira" en ficha de Antinao (Springfield no era canon del lore SyV). Cargadores 30-06 → 7.65 Mauser (calibre canon del Mauser argentino 1909). Reemplazos en `mock/ejercito_rojo/03_antinao.yaml`.

### Added
- Catálogo canon `/meta/*` materializado con 74 tags semilla (10 por categoría × 7 categorías abiertas + 4 vestiduras fijadas). Endpoints `/meta/rasgos`, `/meta/roles`, `/meta/skills`, `/meta/traits`, `/meta/perks`, `/meta/equipo/armas`, `/meta/equipo/utilitarios`, `/meta/equipo/vestiduras` documentados. Vestidura cerrada (4 valores); resto como semilla abierta — usuarios futuros agregan customs.
- Sección 16 nueva — preview arquitectónica de la próxima ola "Aspectos como frases (H.I.T.O.S. / Cultos Innombrables)". Reserva la categoría `aspecto` para v0.4.0 como capa narrativa de alto nivel (frases largas distintas de los traits cortos). Sin implementar todavía.
- Tensión 13.9 nueva — "Catálogo `/meta/*` como semilla, no como autoridad". Formaliza el principio del cliente sobre customs.

### Notes
- PRD bumped a v0.3.0 (mayor — cierre de fase). PRD ahora 1402 líneas.

## [0.2.6] - 2026-05-24
### Changed
- Sub-categoría de tag `equipo.armadura` renombrada a `equipo.vestidura`. Cambio conceptual: la vestidura es identidad visual del combatiente, no protección estructural. Catálogo canon reducido a 4 valores genéricos: `ropa de civil`, `uniforme rojo`, `uniforme confederado`, `camuflaje básico`. Aplicado en PRD.md y en los 22 mocks: 11 confederados con `uniforme confederado`, 8 rojos con `uniforme rojo`, 3 rojos con `ropa de civil` (Paine por identidad mapuche con contradicción; Bordón universitario voluntario reciente; Maturana captado sin convicción ideológica). `camuflaje básico` queda disponible en catálogo sin uso en el corpus actual.

### Removed
- Accesorios identitarios menores eliminados como tags. 5 ocurrencias de `brazalete rojo del Pueblo` removidas de `equipo.utilitario` en los mocks rojos. El criterio "nada de brazaletes, botas, accesorios menores" se documenta en el PRD: la identidad de facción se expresa por la vestidura completa, no por piezas sueltas.

### Added
- OQ #14 abierta: tras el cambio conceptual de armadura a vestidura, el campo derivado `armor` queda huérfano (ya no se deriva de algo coherente). Opciones documentadas: eliminar el concepto, volverlo escalar independiente, o derivarlo de otra fuente (rol_id, etc.). Pendiente decisión del cliente.

### Notes
- Valores históricos "chaleco antifragmentos reglamentario" y "chaleco antifragmentos rústico" introducidos en v0.2.4 quedan obsoletos. Las menciones residuales a `equipo.armadura` en el changelog del PRD y en OQs explicativas se preservan intencionalmente como referencias históricas, no como categorías activas.

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
