# PRD — syv-character-kit

> **Documento vivo.** Define el contrato de producto de la API generadora de personajes del universo *Subordinación y Valor* (SyV). No contiene decisiones de arquitectura, almacenamiento ni stack — solo el QUÉ.
>
> **Versión**: 0.4.1
> **Reemplaza**: 0.4.0 (normalización transversal de tags a forma mínima)
> **Idioma**: castellano rioplatense, voseo sobrio.
> **Convención de identificadores en payloads JSON/YAML**: `snake_case_castellano` (consistente con `faccion`, `atributos`, `estado_salud` ya usados en `/Dev/syv-battle-game-system/`).

---

## 0. Changelog

### v0.4.1

Pasada transversal de **normalización de tags a forma mínima**: tag = identificador, no descripción. Patch sobre v0.4.0; sin nuevas categorías ni features de schema.

- **Principio del tag mínimo**: cada `valor` de tag se reduce a 1-2 palabras (3 cuando el nombre canónico lo requiere — `rifle militar`, `Tiro de precisión`). Cero prosa, cero paréntesis, cero comas internas, cero guiones largos. Documentado como bullet explícito en 6.2.
- **22 mocks normalizados**: `cargador 7.62` / `cargador 9mm` / `cargador 7.65 Mauser` / `cargador 7.92 Mauser` → `cargador`; `cuaderno de campaña — anotaciones de terreno, firma con la inicial R` → `cuaderno`; `brújula de oficial — regalo del instructor de Stroeder` → `brújula`; `cicatriz vertical sobre ceja izquierda (Sector 12,15)` → `cicatriz en ceja`; `Manejo de FAP Confederado M2A` → `Manejo de ametralladora`; `Lectura de terreno boscoso` → `Lectura de terreno`; `Oratoria de muelle` → `Oratoria`; etc. Aplicado a 22 fixtures en `mock/personajes/`. Prosa de `historia` e `historial[]` preservada literal.
- **Ejemplos del PRD normalizados**: Aguirre (6.3), Mansilla (6.4), hoja ASCII canónica de Comandante Miguel (6.0) actualizados al schema mínimo. UTILITARIOS de Miguel pasa de `[cargador 9m]` x3 + `[silbato de contramaestre]` a `[cargador]` x3 + `[silbato]`.
- **Catálogos `/meta/*` alineados**: `/meta/skills` y `/meta/equipo/utilitarios` rebajan sus semillas de 10 a versiones mínimas coherentes (`cargador`, `silbato`, `cuaderno`, `brújula`, `prismáticos`, `botiquín`, `radio`, `mapa`, `cuchillo`, `vendaje`; `Comandancia`, `Tiro de precisión`, `Manejo de ametralladora`, `Operación de radio`, etc.).
- **Tensión nueva 13.11**: "Tags mínimos vs riqueza contextual" — trade-off explícito documentado. La info contextual canónica vive en `/meta/*`, el color narrativo en `historia`, la info estructurada por instancia (si llegara a hacer falta) en una futura entidad `notas`.
- **OQ nueva #16**: entidad `notas: array<{tag_ref, texto}>` como capa enriquecida; pendiente, se acepta pérdida actual.
- **OQ #13 resuelta**: cargadores se generizan a `cargador` (sin calibre). El calibre se infiere del `equipo.arma` portado.

### v0.4.0

Implementación efectiva de **aspectos como categoría canon de primera clase**. Cierra la reserva que dejó v0.3.0 (sección 17) y materializa la primera ola de capa narrativa-mecánica del schema. Bump mayor — categoría nueva ciudadana del modelo de tags.

- **Categoría `aspecto` canon**: nueva sub-familia de tag `{categoria: aspecto, valor: kebab-case}`. Distinta de `trait` (rasgo de carácter sin mecánica activa) y de `perk` (ventaja del reglamento canónico del juego). Un aspecto es un mini-tag identitario con efecto mecánico embebido en una **mini-frase** servida por `/meta/aspectos/{valor}`. Pool abierto, semilla curada, customs permitidos pero no auto-generables.
- **Pool semilla de 10 aspectos canon en `/meta/aspectos`**: `cabrón`, `ojo-de-halcón`, `muy-fuerte` (los tres dados por el cliente como referencia obligada), más 7 curados: `cobarde`, `carismático`, `terco`, `veloz`, `veterano-cicatrizado`, `devoto`, `impredecible`. Cada uno con efecto en frase corta (trigger + probabilidad opcional + efecto).
- **Nuevo bloque ASPECTOS en hoja ASCII canónica**: Miguel Quilodran recibe el aspecto `cabrón` (coherente con líder duro, ex-comisario político). El bloque queda inmediatamente después de PERKS.
- **Ejemplos del PRD actualizados**: Aguirre suma aspecto `ojo-de-halcón` (su olfato de terreno y disciplina visual encajan). Mansilla suma aspecto `carismático` (orador sindical, comisariado). Prosa de `historia` e `historial[]` literalmente preservada.
- **Hitos `agregar_aspecto` y `quitar_aspecto`**: dos tipos nuevos en 9.5 con `metadata: { valor, motivo }`. Patrón consistente con la mutabilidad ya canon de skills/traits/perks.
- **Categoría implícita `estado_temporal`**: se reconoce el patrón de tags activables por aspecto (`berserker`, `pánico`) como sub-categoría conceptual de tag. No se canoniza con catálogo cerrado en v0.4.0 — solo se documenta el patrón para que el motor downstream lo identifique.
- **Sección 17 promovida**: deja de ser "preview reservado" y pasa a "Aspectos como ciudadanos canon — capa narrativa-mecánica". Conserva la nota arquitectónica original como contexto histórico y deja apuntada una posible próxima ola (aspectos largos al estilo H.I.T.O.S./Cultos Innombrables, frases narrativas de 10–25 palabras) sin implementarla.
- **Nueva tensión 13.10**: el efecto del aspecto vive en texto libre; el motor downstream necesita interpretar la mini-frase (probable vía LLM o regla heurística). Aceptado, mismo compromiso que customs de perks/traits.
- **Total tags semilla**: pasa de 70 a 80 (los 70 anteriores + 10 aspectos canon).

**Breaking changes vs v0.3.2.**

- Ninguno estructural. Es feature aditiva: categoría nueva, endpoint nuevo, dos hitos nuevos. Los 22 mocks NO se tocan en este release (ola separada).

### v0.3.2

Pasada de poda cosmética. Sin cambios funcionales.

- Header de la hoja ASCII de Miguel sincronizado a `schema v0.3.1`.
- OQs cerradas (#4 `armor` on-demand y #14 `armor` tras v0.3.0) eliminadas de la sección 15; OQs restantes renumeradas.
- Referencias huérfanas a campos obsoletos limpiadas en texto activo (tabla de equipo 7.11 actualizada a genéricos).
- Bullet duplicado de `fza_aportada` en sección 6.2 eliminado.

### v0.3.1

Rectificación de catálogo de armas. YAGNI aplicado a `equipo.arma`, coherente con el patrón ya establecido en vestidura (v0.2.6).

- **Catálogo `equipo.arma` reducido a 6 genéricos**: `pistola`, `revolver`, `rifle`, `rifle militar`, `SMG`, `ametralladora`. Eliminadas las 10 entradas específicas anteriores (FAL, FAP Confederado M2A, FAP Modelo 45, Fusil de precisión Mauser, Pistola reglamentaria M9, Subfusil Halcón, Fusil Mauser 1909, Ametralladora ligera, Pistola Browning capturada, Bayoneta, Granada de mano).
- **Mapeo en los 22 YAMLs**: `Fusil FAL` / `Fusil FAL con óptica 4x` / `Fusil de precisión FAL Tiro` → `rifle militar`; `FAP Confederado M2A` / `FAP Modelo 45` → `ametralladora`; `Fusil Mauser 1909 con mira` / `Fusil de cerrojo Mauser 1909` → `rifle militar`; `Subfusil Halcón` → `SMG`; `Pistola reglamentaria M9` / `Pistola Browning capturada` → `pistola`.
- **Eliminación de cuchillos del catálogo de armas**: `Cuchillo de campo` y `Cuchillo de trabajo` movidos de `equipo.arma` a `equipo.utilitario` en los mocks de Funes y Calfucurá. No entran al catálogo de armas de fuego.
- **Bayoneta y granada eliminadas del catálogo canon**: eran parte del catálogo semilla anterior pero no tienen representación en los 22 mocks. Siguen siendo posibles tags emergentes si la prosa o historial lo justifican.
- **Total de tags semilla**: baja de 74 a 70 (6 armas + 10 utilitarios + 10 rasgos + 10 roles + 10 skills + 10 traits + 10 perks + 4 vestiduras).

**Breaking changes vs v0.3.0.**

- Catálogo `/meta/equipo/armas`: de 10 a 6 valores genéricos.
- En los 22 mocks: todos los tags `equipo.arma` específicos reemplazados por genéricos. Los `Cuchillo de campo` y `Cuchillo de trabajo` que estaban en `equipo.arma` pasan a `equipo.utilitario`.

### v0.3.0

Cierre de fase del schema del personaje. Reconcilia los tres pendientes que dejó v0.2.6 y prepara terreno para la próxima ola narrativa. Bump mayor — sistema de tags consolidado.

- **Eliminación de `armor`**: el campo derivado `armor` se elimina del sistema. La rectificación de v0.2.6 (armadura → vestidura como identidad visual, no protección) dejó al campo sin sustento conceptual. Si más adelante se necesita defensa numérica, vuelve como tag `trait: blindado` derivado de vestidura específica o de skill defensiva. Cierra OQ #14 con resolución (a). El endpoint `/meta/equipo/armaduras/{valor}` queda fuera del PRD.
- **Springfield 1903 → Mauser 1909**: tag `equipo.arma` con valor "Fusil de cerrojo Springfield 1903 con mira" reemplazado en el mock afectado por "Fusil Mauser 1909 con mira" (arma de cerrojo canon del Ejército Rojo). Cargadores de calibre 30-06 normalizados a 7.65 Mauser. Prosa de los personajes no se toca.
- **Catálogo canon `/meta/*` con 74 tags semilla**: se materializa la lista de tags estándar que cada endpoint `/meta/skills`, `/meta/traits`, `/meta/perks`, `/meta/rasgos`, `/meta/roles`, `/meta/equipo/{armas,utilitarios,vestiduras}` devuelve como vocabulario sugerido. 10 rasgos + 10 roles + 10 skills + 10 traits + 10 perks + 10 armas + 10 utilitarios + 4 vestiduras = 74. La lista cubre los casos normales del MVP; otros usuarios crearán tags personalizados que entrarán al catálogo emergente. Documentado en sección 10 y como tensión en 13.9.
- **Reserva de la categoría `aspecto` para v0.4.0**: la próxima ola introduce aspectos como **frases narrativas largas** (10–25 palabras), inspirados en el patrón de H.I.T.O.S. y Cultos Innombrables. No se implementa hoy; se documenta como nota arquitectónica en sección 17 para que la próxima iteración tenga camino claro.
- **Bump mayor a v0.3.0**: el sistema de tags está sólido, los 22 mocks normalizados, los pendientes cerrados. Cierra una fase entera del schema.

**Breaking changes vs v0.2.6.**

- Eliminado: campo derivado `armor` y endpoint `/meta/equipo/armaduras/{valor}`.
- Renombrado en mock: arma "Fusil de cerrojo Springfield 1903 con mira" → "Fusil Mauser 1909 con mira".

### v0.2.6

Rectificación conceptual sobre la sub-categoría de equipamiento identitario:

- **`equipo.armadura` → `equipo.vestidura`**: la vestidura es identidad visual de facción, no protección defensiva. El catálogo pasa a cuatro valores genéricos: `ropa de civil`, `uniforme rojo`, `uniforme confederado`, `camuflaje básico`.
- **Eliminación de accesorios menores identitarios**: tags `equipo.utilitario` con valor "brazalete rojo del Pueblo" (y equivalentes) eliminados — no son tags propios, son ruido.
- **OQ #14 abierta**: el campo derivado `armor` queda como TODO pendiente. La rectificación a vestidura como concepto identitario abre la pregunta sobre si `armor` sigue siendo derivado, vuelve a campo escalar, o desaparece. Ver sección 15.
- Los 22 mocks actualizados: cada personaje tiene exactamente 1 tag `equipo.vestidura` con valor en el catálogo de 4.

### v0.2.5 (consolidación de v0.2.3 + v0.2.4 + v0.2.5)

Tres deltas acumulados sobre v0.2.2 se incorporan en un único release. La motivación común es alinear el schema con la terminología operativa del reglamento (escuadra, rango, mando como capacidad) y con la naturaleza real del personaje SyV (un conjunto de tags categorizados, no un objeto rígido con sub-bloques).

**Delta v0.2.3 — rango ≠ rol, escuadra, mando como capacidad, estado vital.**

- Se agrega `rango` (string abierto): designación operativa de campo. Es la pieza que el motor de batalla usa para decidir mando. Canon abierto: `Lider de escuadra`, `Apuntador`, `Fusilero`, `Recluta`, `Artillero`, `Segundo al mando`, etc.
- Se agrega `escuadra_id` (string | null): referencia a la entidad escuadra. `null` = sin asignar.
- `mando` deja de ser enum (`titular`/`suplente`/`no_apto`) y pasa a ser **booleano** (capacidad de mando: si `true`, el personaje puede asumir liderazgo cuando el actual cae). La "titularidad" actual del mando se **deriva**: `mando == true AND es el de mayor rango de mando en su escuadra_id`. No se persiste como campo.
- Se agrega `estado` (enum): `activo` | `disponible` | `kia` | `licencia`. Reemplaza a la dimensión "asignación" que antes estaba implícita.
- `rol` queda desacoplado de `rango`: es el papel narrativo/cultural ("Sargento Confederado", "Líder Revolucionario", "Comisario"). Mismo `rango` operativo puede ser ejercido por distintos `rol`.
- `estado_salud` se renombra a `saludable` | `herido` | `baja` (antes incluía `activo`, lo cual chocaba con el nuevo `estado: activo`).
- Eliminados: `rol_id` (pasa a ser interno del motor de creación), `origen_geografico` (si la procedencia importa, va a `historia`).

**Delta v0.2.4 — bloque `aspectos` eliminado; skills/traits/perks como tags; equipo en sub-categorías.**

- Bloque `aspectos` (concepto + perk_fijo + complicacion_fija) eliminado por completo. El concepto narrativo, si importa, se cuenta en `historia`.
- Tres categorías canon nuevas de tags:
  - `skill` — habilidades aprendidas o entrenadas (Comandancia, Francotirador, Medicina, Ingeniería, Lectura de columna, Oratoria de muelle).
  - `trait` — rasgos de carácter o condición, **sin polaridad fija**. Incluye positivos (Sangre fría), neutros (Voz grave) y penalidades que antes eran complicaciones (Miope, Hemorragia lenta, Objetivo prioritario).
  - `perk` — ventajas mecánicas activables (Voz de mando, Recarga rápida, Cobertura instintiva).
- `especialidad` eliminada (pasa a ser un tag `skill` — ej. Mansilla tiene `Comisariado` en SKILLS).
- Equipo deja de ser bloque `equipo: { armas[], equipo_tactico[], armor }`. Pasa a ser **sub-categorías jerárquicas** de tag: `equipo.arma`, `equipo.utilitario`, `equipo.armadura`. Decisión consciente: forma jerárquica con punto en lugar de un sub-campo aparte. Más query-friendly (filtrar `equipo.*` por prefijo) y visualmente legible.
- `armor` total deja de ser campo persistido y pasa a ser **derivado**: el motor lo computa al servir sumando puntos de armor de los tags `equipo.armadura`. Cada armadura declara su aporte en `/meta/equipo/armaduras/{valor}`.
- `fza_aportada` deja de ser campo persistido y pasa a ser **derivado**: tag `categoria: rol, valor: lider` → 2; `categoria: rol, valor: heroe` → 3; sin ninguno → 1. El motor lo computa al servir.

**Delta v0.2.5 — escuadra, sobrenombre, filiación, reordenamiento de cabecera.**

- `peloton` / `peloton_id` se renombra a `escuadra` / `escuadra_id` por consistencia con el reglamento SyV.
- `nombre_de_campo` se renombra a `sobrenombre`.
- Se agrega `filiacion` (string, **derivado**, no persistido). Se compone al servir como `"{rango} de la {escuadra.nombre} del {escuadra.cuerpo}"`. Si `escuadra_id` es `null`, se omite la cláusula de escuadra. El nombre `filiacion` es **provisorio** — ver OQ.
- Se introduce la entidad implícita `escuadra` (`id`, `nombre`, `cuerpo`, `faccion`). No se especifica su schema completo en este release; queda para cuando se necesite.
- **Orden definitivo de la cabecera** (visible en 6.1, 6.0 y los ejemplos): identidad nominal (nombre → sobrenombre → filiacion) → pertenencia macro (faccion) → datos biológicos (edad → genero → estado_salud) → narrativo (rol) → operativo (estado → rango → escuadra → mando).

**Breaking changes vs v0.2.2.**

- Eliminados: `rol_id`, `origen_geografico`, `aspectos` (bloque completo), `fza_aportada` (como campo), `especialidad`, `nombre_de_campo`, `equipo.armor` (como campo), enum `mando: {titular|suplente|no_apto}`, `tag_rol` (ya eliminado en v0.2.2; se confirma su no-retorno).
- Renombrados: `nombre_de_campo` → `sobrenombre`; `peloton*` → `escuadra*`; `estado_salud: activo` → `saludable`.
- Agregados: `rango`, `escuadra_id`, `mando` (bool), `estado` (enum), `sobrenombre`, `filiacion` (derivado), categorías canon de tag `skill`, `trait`, `perk`, sub-categorías `equipo.arma` / `equipo.utilitario` / `equipo.armadura`.

### v0.2.2

Patch incremental sobre v0.2.1. Introdujo identidad nominal desdoblada (`nombre` + `nombre_de_campo`), `especialidad`, `mando` como enum, y sistema híbrido tags + campos. Reemplazado por v0.2.5; los detalles quedan en el commit log.

### v0.2.1

Patch incremental sobre v0.2.0. Cerró cuatro OQs: edad simple, historial sin límite, atributos inmutables al cambiar de rol, idempotencia de `POST /canonize`.

### v0.2.0

Introdujo la **memoria viva**: el personaje canonizado deja de ser una foto inmutable y pasa a ser una entidad con historial y mutaciones por hito. Cerró las cuatro OQs originales de v0.1.0 (canonización solo en API; historia congelada; sin migraciones; restricción 80/20 soft de perks).

---

## 1. Visión del producto

`syv-character-kit` es una API HTTP que entrega fichas de personaje canónicas del universo SyV bajo demanda. Cada llamada produce un personaje listo para ser consumido por el motor de batalla, por herramientas de narrativa o por interfaces de exploración del universo.

Los personajes existen en tres modos:

- **Efímeros**: generados al vuelo, sin persistencia. Determinísticos por seed.
- **Mocks**: 22 fixtures versionadas escritas a mano, importadas del corpus narrativo del battle-system. Inmutables.
- **Canonizados**: persistidos por la API como parte del corpus oficial *de la API*. **Mutables y evolutivos**: acumulan historia.

El producto encapsula tres fidelidades: al **reglamento** (matriz de stats, composición de escuadra), al **lore** (tono, geografía, nomenclatura por facción) y al **tiempo** (un personaje canonizado existe y cambia).

## 2. Problema y oportunidad

El ecosistema SyV está repartido en tres repositorios con responsabilidades distintas (`syv` — sitio público; `syv-game-system` — esquemas y reglas abstractas; `syv-battle-game-system` — reglamento de combate y fichas de origen). Cada producto que necesita personajes los inventa por su cuenta o copia fichas manualmente.

`syv-character-kit` resuelve esto siendo **la fuente única de personajes** del ecosistema. Concentra las tablas curadas (nombres, conceptos, skills, traits, perks, equipamiento), aplica la matriz determinística por rango, delega a un modelo generativo solo la prosa inicial, y — diferencial de esta versión — **administra el ciclo de vida del personaje canonizado**: nace, pelea, cambia, queda registrado.

El diferencial frente a un generador clásico es la memoria viva. Cualquier consumidor pide un personaje en t1 y en t2 y recibe **el mismo personaje en estados distintos**, no dos personajes nuevos.

## 3. Usuarios y consumidores previstos

La API no tiene UI propia: sus clientes son otros componentes del ecosistema SyV.

- **Motor de batalla**: pide escuadras completas para escenarios. Reporta hitos posteriores (triple-0, baja, captura) para que la API los registre en el `historial` del personaje canonizado.
- **Generador de escenarios y aventuras**: pide PNJs con tono y stats coherentes al sector geográfico. Crea principalmente efímeros.
- **Sitio público de lore**: muestra galerías de canonizados con su biografía vigente (no la original). Permite "tirar un personaje al azar" como herramienta de inmersión.
- **Herramientas narrativas internas**: redactores que canonizan personajes notables y agregan hitos manuales ("ascendido", "trasladado", "amputación").
- **Pipelines de QA del reglamento**: tests que ejercitan el motor contra los 22 mocks y miden desbalances.

## 4. Principios de diseño

- **SOLID y open/close como pilar.** El schema se diseña desde el día uno para extenderse sin romperse. Nuevos perks, nuevos tipos de hito, nuevas categorías de equipamiento, nuevas facciones — se agregan sin migraciones, sin breaking changes. Si una decisión de diseño nos obligaría a romper esto, se rechaza la decisión.
- **Customs libres + enums abiertos como política deliberada.** El producto acepta tags `skill`/`trait`/`perk` con valores fuera del canon. Los enums (`tipo` de hito, `tipo` de vínculo, sub-categoría de tag, etc.) tienen valores **sugeridos** pero no rechazan otros. **Tensión asumida**: el motor downstream que consuma estos customs tiene que poder interpretarlos. Ver sección 13.
- **Stats determinísticos por rango, narrativa sorteada.** En creación, los atributos se derivan de una matriz fija por rango operativo. Nombre, género, rasgos, skills/traits/perks, equipamiento e historia se sortean.
- **Memoria viva como naturaleza del recurso canonizado.** Un canonizado tiene historial y muta. No es un payload; es una entidad. Ver sección 9.
- **Reproducibilidad por seed para efímeros.** Toda creación admite `?seed=`. La misma `(seed, faccion, rango)` produce el mismo personaje, incluida la prosa inicial. **Limitación aceptada**: los canonizados pierden esta propiedad tras el primer hito.
- **LLM solo para prosa, solo una vez.** El modelo generativo escribe el campo `historia` en la creación efímera. Si el personaje se canoniza, esa prosa se congela.
- **Mocks separados de canonizados.** Los 22 mocks son fixtures inmutables del battle-system. Los canonizados son entidades vivas de la API. No hay sincronización ni promoción mock → canonizado.
- **El PRD es contrato; el repo es implementación.** Este documento define formas y reglas. Cómo se almacenan tablas, dónde corre el LLM, qué binding usa la persistencia — fuera de scope.
- **Tags como modelo de primera clase.** La regla es: *"lo que puede ser tag, es tag."* Rasgos físicos, habilidades aprendidas, ventajas mecánicas, condiciones de carácter, inventario de equipo — todo eso es un tag categorizado. Lo que NO es tag: identidad (`nombre`, `sobrenombre`, `edad`, `genero`), pertenencia (`faccion`), posicionamiento operativo (`rol`, `rango`, `estado`, `escuadra_id`, `mando`, `estado_salud`), `atributos`, `lealtades`, `vinculos`, `historial`, `historia`, `metadatos`. La frontera es deliberada: el campo estructurado se usa cuando el motor necesita acceso semántico directo sin parsear una lista (ej. `rango` para decidir mando, `estado` para filtrar disponibilidad). Todo lo demás convive en `tags[]` con categorías abiertas. Esto permite extender el modelo de personaje sin agregar campos, sin migraciones, sin breaking changes. Las categorías canon actuales son: `rasgo`, `rol`, `skill`, `trait`, `perk`, `aspecto`, y la familia jerárquica `equipo.{arma,utilitario,vestidura}`.

## 5. Casos de uso

| # | Como… | Quiero… | Para… |
|---|---|---|---|
| UC-01 | motor de batalla | pedir un personaje al azar sin restricciones | rellenar un slot vacío en un escenario |
| UC-02 | generador de escenarios | pedir un personaje filtrando por facción | poblar una escuadra de Ejército Rojo |
| UC-03 | sitio de lore | pedir un personaje filtrando por rango | mostrar "un sargento confederado típico" |
| UC-04 | redactor narrativo | pedir un personaje filtrando por facción y rango | tener un Camarada Puntero específico para un cuento |
| UC-05 | motor de batalla | pedir un personaje exacto por id | recargar al Sargento Aguirre en una continuación |
| UC-06 | redactor | regenerar el mismo personaje efímero con la misma seed | discutir variantes sin perder el original |
| UC-07 | curador de canon | canonizar un personaje generado | que pase a ser entidad permanente del corpus de la API |
| UC-08 | herramienta de QA | listar todos los mock | correr el motor sobre la población canon completa |
| UC-09 | cualquier cliente | consultar el catálogo de facciones, rangos, skills, traits, perks, equipo, tipos de hito | construir UIs sin hardcodear enums |
| UC-10 | motor de batalla | registrar un triple-0 sobre un canonizado | que el +1 al atributo quede reflejado en la ficha vigente |
| UC-11 | redactor | registrar un ascenso narrativo sobre un canonizado | que la próxima `GET` muestre el nuevo rango y el hito |
| UC-12 | motor de batalla | registrar la formación de un vínculo (mentor, hermano de armas) entre dos canonizados | que ambos personajes lo recuerden |
| UC-13 | motor de batalla | registrar la captura de un arma enemiga | que el equipo vigente la incluya |
| UC-14 | redactor | registrar la ruptura de una lealtad | que el personaje pase a tener un secreto o un enemigo jurado |
| UC-15 | sitio de lore | pedir el mismo canonizado en t1 (post-canonización) y t2 (tras 4 hitos) | mostrar evolución visible en la ficha |
| UC-16 | cualquier cliente | pedir la ficha con `?fields=` podada | bajar payload cuando solo le interesa el resumen |
| UC-17 | sitio de lore | pedir el `historial[]` de un canonizado | renderizar una línea de tiempo del personaje |
| UC-18 | curador | asignar un personaje a una escuadra | ver `filiacion` y `estado: activo` derivados correctamente |
| UC-19 | motor de batalla | filtrar personajes por tag `skill: Francotirador` | armar un pelotón de tiradores para una misión de hostigamiento |
| UC-20 | redactor narrativo | pedir un personaje con tag `trait: Miope` | forzar una complicación visual específica en una escena de tensión |
| UC-21 | editor de canon | listar todos los tags `equipo.arma` del roster de mocks | auditar coherencia del inventario armamentístico antes de una batalla |
| UC-22 | motor de batalla | filtrar personajes por tag `rol: lider` AND `faccion: Ejército Rojo` | identificar candidatos al mando ante la caída del líder vigente |
| UC-23 | herramienta de QA | consultar `/meta/tag_categories` y `/meta/skills` | verificar que el generador no produce tags fuera del vocab canon |

## 6. JSON canónico del personaje (v0.4.0)

Sección central del PRD. Define la forma del recurso `personaje` que la API devuelve.

El schema es **estricto** en estructura y **abierto** en valores: los campos están definidos, pero los enums admiten valores sugeridos sin rechazar otros, y existe un campo `extras` libre al top level.

### 6.0. Hoja ASCII de referencia — ejemplo aprobado por el cliente

La siguiente hoja es la **representación visual canónica** del payload del personaje, aprobada por el cliente como ejemplo de referencia. Es complementaria al JSON canónico de 6.1: el JSON es el **contrato de datos**, la hoja es la **convención de presentación**. Toda UI que renderice un personaje debería poder componer una vista equivalente.

```
+----------------------------------------------------------------------------+
| SyV CHARACTER SHEET                                          schema v0.4.0 |
| id: mock.ejercito_rojo.??.miguel                          origen: mock     |
+----------------------------------------------------------------------------+
| NOMBRE         Miguel Quilodran                                            |
| SOBRENOMBRE    Comandante Miguel                                           |
| FILIACION      Lider de la Escuadra Mardones                               |
|                del Ejercito Revolucionario del Pueblo                      |
| FACCION        Ejercito Rojo                                               |
|                                                                            |
| EDAD           41                                                          |
| GENERO         masculino                                                   |
| ESTADO SALUD   saludable                                                   |
|                                                                            |
| ROL            Lider Revolucionario                                        |
| ESTADO         Activo                                                      |
| RANGO          Lider de escuadra                                           |
| ESCUADRA       Escuadra Mardones                       (esq_rojo_07)       |
| MANDO          si                                                          |
+----------------------------------------------------------------------------+
| ATRIBUTOS                                                                  |
|   FIS  3  [###..]    TAC  5  [#####]    MEN  7  [#######]                 |
+----------------------------------------------------------------------------+
| RASGOS                                                                     |
|   alto, corpulento, barba canosa, pelo corto, manos grandes,              |
|   mandibula marcada, quemadura en antebrazo derecho                       |
+----------------------------------------------------------------------------+
| EQUIPO                                                                     |
|   ARMAS        [SMG]  [pistola]                                            |
|   UTILITARIOS  [cargador]  [cargador]  [cargador]  [silbato]              |
|   VESTIDURA    [uniforme rojo]                                             |
+----------------------------------------------------------------------------+
| SKILLS                                                                     |
|   [Comandancia]  [Oratoria]  [Coordinación]                                |
+----------------------------------------------------------------------------+
| TRAITS                                                                     |
|   [Sangre fria]  [Objetivo prioritario]                                    |
+----------------------------------------------------------------------------+
| PERKS                                                                     |
|   [Voz de mando]                                                           |
+----------------------------------------------------------------------------+
| ASPECTOS                                                                   |
|   [cabrón]                                                                 |
+----------------------------------------------------------------------------+
| LEALTADES                                                                  |
|   primaria   : Ejercito Rojo                                               |
|   secundarias: [los muelles del sur, la asamblea de Stroeder]              |
|   secretos   : []                                                          |
+----------------------------------------------------------------------------+
| VINCULOS                                                                   |
|   mentor          -> pending.viejo_petrov     (capataz de muelle)          |
|   hermano_armas   -> mock.ejercito_rojo.02.iturra                          |
|   subordinado     -> mock.ejercito_rojo.09.bordon                          |
|   rival           -> mock.confederacion.01.aguirre   (asimetrico)          |
+----------------------------------------------------------------------------+
| HISTORIAL                                                                  |
|   2174-11-03  formacion_vinculo  Petrov lo cubrio en la represion de la   |
|                                  huelga; quedo la quemadura del cano.     |
|   2177-08-19  ascenso            Designado Lider Revolucionario tras la   |
|                                  caida del companero Mardones.            |
|   2178-02-04  triple_cero (MEN)  Mantuvo la columna bajo fuego en Roca.   |
+----------------------------------------------------------------------------+
| HISTORIA                                                                   |
|   Quilodran nacio en Comodoro, hijo de un estibador del Golfo. Trabajo el  |
|   muelle desde los catorce y organizo a los descargadores antes de los     |
|   veinte. Cuando el Ejercito Rojo se reorganizo en el sur, no tuvo que     |
|   postularse: lo nombraron. No le gusto. Lo acepto igual.                  |
+----------------------------------------------------------------------------+
| METADATOS                                                                  |
|   semilla: mock-fixed-??     modelo_prosa: null     es_canon: true         |
|   creado_en: 2026-05-24      ultima_actualizacion: 2178-02-04              |
+----------------------------------------------------------------------------+
```

Observaciones sobre la hoja:

- La cabecera respeta el **orden definitivo** documentado en el changelog v0.2.5.
- `FILIACION` es campo derivado, no persistido. Se compone como `"{rango} de la {escuadra.nombre} del {escuadra.cuerpo}"`.
- `VESTIDURA` muestra la identidad visual del personaje (categoría `equipo.vestidura`). El campo `armor` fue eliminado del sistema en v0.3.0 (ver changelog).
- `MANDO si` corresponde a `mando: true` en el JSON.
- `ESTADO Activo` corresponde a `estado: activo` (asignación operativa), distinto de `ESTADO SALUD saludable` (condición física).

### 6.1. Esquema (vista en YAML legible)

```yaml
personaje:
  # ── Identidad estable ──────────────────────────────────────────────────
  id: string                            # estable para mocks y canonizados; null para efímeros
  origen: enum                          # "mock" | "generado" | "canonizado"
  semilla: string                       # seed original que produjo la ficha; siempre presente

  # ── Cabecera: orden definitivo de presentación ─────────────────────────
  # 1) Identidad nominal
  nombre: string                        # nombre real, ej. "Walter Aguirre"
  sobrenombre: string | null            # como se lo conoce operativamente, ej. "Sargento Walter Aguirre"
                                        # null si no hay nick/título distinto del nombre real
  filiacion: string                     # DERIVADO, no persistido. Se compone al servir como:
                                        #   "{rango} de la {escuadra.nombre} del {escuadra.cuerpo}"
                                        # Si escuadra_id es null, se omite la cláusula de escuadra.
                                        # Nombre PROVISORIO — ver OQ #1.

  # 2) Pertenencia macro
  faccion: enum                         # "Confederación" | "Ejército Rojo" (otras 3 fuera de MVP)

  # 3) Datos biológicos
  edad: integer                         # años, 16..70 sugerido. Sin mecánica de envejecimiento.
  genero: enum                          # "masculino" | "femenino" | "no_binario" | "otro" (abierto)
  estado_salud: enum                    # "saludable" | "herido" | "baja" (en creación: "saludable")

  # 4) Narrativo
  rol: string                           # papel narrativo/cultural; abierto.
                                        # Ej: "Sargento Confederado", "Líder Revolucionario", "Comisario".
                                        # Desacoplado de rango: distintos `rol` pueden ejercer el mismo `rango`.

  # 5) Operativo
  estado: enum                          # "activo" | "disponible" | "kia" | "licencia"
                                        # activo     = asignado a escuadra y operativo
                                        # disponible = no asignado, listo para integrarse
                                        # kia        = caído en combate
                                        # licencia   = baja temporal (recuperación, traslado)
  rango: string                         # designación operativa de campo; jerárquica; abierta.
                                        # Ej: "Lider de escuadra", "Apuntador", "Fusilero", "Recluta",
                                        # "Artillero", "Segundo al mando".
                                        # Pieza que el motor de batalla usa para mando.
  escuadra_id: string | null            # ref a entidad escuadra. null = sin asignar.
  mando: boolean                        # capacidad de mando. Si true, puede asumir liderazgo cuando
                                        # el actual cae. La "titularidad" actual del mando se DERIVA:
                                        # (mando == true) AND (es el de mayor rango de mando en su escuadra).

  # ── Lealtades (estructuradas completas) ────────────────────────────────
  lealtades:
    primaria: string                    # ej. "Confederación", "Sargento Ricardo (post mortem)"
    secundarias: array<string>
    secretos: array<string>

  # ── Atributos (set único mutable) ──────────────────────────────────────
  atributos:
    fis: integer                        # 2..5 (techo 5)
    tac: integer                        # 2..5 (techo 5)
    men: integer                        # 2..5; líderes hasta 7

  # ── Tags (sistema híbrido extensible — corazón del schema) ─────────────
  tags:
    - categoria: string                 # categoría abierta. Categorías canon previstas:
                                        #   rasgo               → rasgos físicos, cicatrices, apariencia
                                        #   rol                 → etiquetas mecánicas de rol (ej. "lider", "heroe")
                                        #   skill               → habilidades aprendidas/entrenadas
                                        #   trait               → rasgos de carácter o condición (SIN polaridad fija)
                                        #   perk                → ventajas mecánicas activables (canon del reglamento)
                                        #   aspecto             → mini-tag identitario con efecto mecánico
                                        #                          embebido en mini-frase (ver /meta/aspectos)
                                        #   equipo.arma         → arma de fuego, cuerpo a cuerpo, etc.
                                        #   equipo.utilitario   → cargador, vendaje, silbato, etc.
                                        #   equipo.vestidura    → identidad visual de facción (uniforme, ropa de civil, camuflaje)
                                        # Sub-categorías jerárquicas con punto (decisión consciente para
                                        # filtrar por prefijo y mantener legibilidad).
      valor: string                     # Tags repetibles: tres "cargador 9mm" son tres entidades distintas.

  # ── Vínculos con otros personajes (mutables) ───────────────────────────
  vinculos:
    - tipo: string                      # sugerido: mentor | subordinado | hermano_de_armas |
                                        # rival | deuda | enemigo_jurado | familia | romance (abierto)
      ref_personaje_id: string | null   # id si existe en el corpus; null si externo. SIN VALIDACIÓN.
      descripcion: string               # crítica; fallback cuando ref_personaje_id no resuelve

  # ── Prosa biográfica original (congelada al canonizar) ─────────────────
  historia: string                      # 120-200 palabras, generada por LLM en creación efímera;
                                        # se congela al canonizar y no muta nunca más

  # ── Memoria viva: historial de hitos ───────────────────────────────────
  historial:
    - fecha: string                     # ISO-8601
      tipo: string                      # sugerido: triple_cero | ascenso | herida | recuperacion |
                                        # agregar_tag | quitar_tag | formacion_vinculo | ruptura_vinculo |
                                        # traslado | condecoracion | mejora_atributo |
                                        # cambio_rango | cambio_mando | cambio_estado | asignacion_escuadra
                                        # (abierto; el motor puede emitir tipos custom)
      descripcion: string
      ref_batalla: string | null        # id de batalla del motor downstream; opcional
      metadata: object                  # libre, open/close (ej. { atributo: "fis", delta: 1 })

  # ── Snapshot de auditoría ──────────────────────────────────────────────
  tags_iniciales: array<{categoria, valor}>  # snapshot completo de tags[] al crear; inmutable

  # ── Metadatos ──────────────────────────────────────────────────────────
  metadatos:
    creado_en: string                   # ISO-8601 (creación efímera)
    canonizado_en: string | null        # ISO-8601 (null para efímeros y mocks)
    ultima_actualizacion: string
    modelo_prosa: string | null
    es_canon: boolean

  # ── Campos derivados servidos por la API (NO persistidos) ──────────────
  # La API los computa al armar la respuesta y los incluye en el payload.
  # Documentados aquí para que el cliente sepa qué esperar.
  #
  #   filiacion       : string         (ya documentado arriba en cabecera)
  #   fza_aportada    : integer 1..3   (tag rol=heroe → 3; rol=lider → 2; sin → 1)
  #
  # Si el cliente quiere derivar localmente, los puede recalcular desde los tags.

  # ── Escape hatch para extensibilidad ───────────────────────────────────
  extras: object | null                 # libre, no validado.
```

**Lo que NO es tag (sigue siendo campo estructurado):** identidad (`nombre`, `sobrenombre`, `edad`, `genero`), pertenencia (`faccion`), posicionamiento operativo (`rol`, `rango`, `estado`, `escuadra_id`, `mando`, `estado_salud`), `atributos`, `lealtades`, `vinculos`, `historial`, `historia`, `metadatos`. El resto del personaje vive como tags: rasgos, skills, traits, perks, equipo.

### 6.2. Notas de campo (lo no obvio)

- **`id`**: para mocks `mock.{faccion_slug}.{nn}.{apellido_slug}`. Para canonizados `canon.{ulid}`. Para efímeros `null`.
- **`sobrenombre`**: cómo se lo conoce operativamente. En Confederación: rango + nombre ("Sargento Walter Aguirre"). En Ejército Rojo: título revolucionario + nombre, derivable del tag `skill` de mando si aplica ("Camarada Puntero Ramón Mansilla"). `null` si no hay distinción con el nombre real.
- **`filiacion`** (DERIVADO, no persistido): se compone al servir como `"{rango} de la {escuadra.nombre} del {escuadra.cuerpo}"`. Si `escuadra_id` es `null`, se omite la cláusula `"de la Escuadra ..."` y queda `"{rango} del {cuerpo}"` (o solo `"{rango}"` si tampoco hay cuerpo conocido). **Nombre provisorio**: ver OQ #1; alternativas en evaluación: `designacion`, `titulo`, `pie_de_firma`.
- **`rango`** vs **`rol`**: `rango` es operativo y jerárquico (lo que el motor de batalla usa para decidir mando). `rol` es narrativo/cultural (cómo lo describe el lore). Mismo `rango` ("Lider de escuadra") puede ser ejercido por distintos `rol` ("Sargento Confederado", "Líder Revolucionario", "Comisario").
- **`mando` (booleano)**: capacidad, no titularidad. Si `true`, el personaje es apto para liderar; cuando el líder activo cae, el de mayor `rango` con `mando: true` en la misma `escuadra_id` asume. La titularidad vigente es derivada y no se persiste. Cambiar `mando` post-creación requiere hito `cambio_mando`.
- **`estado`**: dimensión de **asignación/disponibilidad**, no de salud. `activo` requiere `escuadra_id != null`; `disponible` es lo natural para un personaje recién generado sin asignar; `kia` y `licencia` son condiciones que sacan al personaje de la rotación.
- **`estado_salud`**: dimensión de **condición física**. Renombrado desde v0.2.2 para no chocar con `estado: activo`. Valores: `saludable` (default), `herido`, `baja`.
- **`escuadra_id`**: referencia a la entidad `escuadra`. La API **no valida** que el id exista (mismo criterio que `vinculos[].ref_personaje_id`).
- **Entidad `escuadra`** (implícita en v0.2.5; schema completo queda para futuro):
  ```yaml
  escuadra:
    id: string            # ej. "esq_rojo_07"
    nombre: string        # ej. "Escuadra Mardones" (narrativo, no id)
    cuerpo: string        # ej. "Ejército Revolucionario del Pueblo"
    faccion: string
    # composición: query por personajes con escuadra_id == self.id
  ```
- **`atributos`**: un único set **mutable**. Triple-0 o `mejora_atributo` sobreescriben el valor. La trazabilidad vive en `historial[]`.
- **`tags`**: el corazón del schema. Lista plana de entidades `{categoria, valor}`. Categorías y sub-categorías abiertas. Tags repetibles (tres `cargador 9mm` son tres entidades distintas — tienen presencia física y pueden perderse de a uno). Cambios se registran como hitos `agregar_tag` / `quitar_tag`.

  Las **seis categorías canon** en v0.2.5 son:

  | Categoría | Tipo | Ejemplos canon |
  |---|---|---|
  | `rasgo` | Atributos visuales del cuerpo | `altura media`, `barba descuidada`, `cicatriz en ceja`, `manos curtidas` |
  | `rol` | Etiquetas mecánicas del rol vigente | `lider`, `heroe`, `sargento` |
  | `skill` | Habilidades aprendidas o entrenadas | `Comandancia`, `Tiro de precisión`, `Primeros auxilios`, `Oratoria`, `Lectura de terreno`, `Comisariado` |
  | `trait` | Rasgos de carácter o condición, sin polaridad fija | `Sangre fría`, `Objetivo prioritario`, `Hemorragia lenta`, `Voz grave`, `Obstinado` |
  | `perk` | Ventajas mecánicas activables del reglamento canónico | `Voz de mando`, `Recarga rápida`, `Cobertura instintiva`, `Sucesor de Ricardo` |
  | `aspecto` | Mini-tag identitario con efecto mecánico embebido en mini-frase | `cabrón`, `ojo-de-halcón`, `muy-fuerte`, `carismático`, `terco` |
  | `equipo.arma` | Arma de fuego (6 valores genéricos) | `pistola`, `revolver`, `rifle`, `rifle militar`, `SMG`, `ametralladora` |
  | `equipo.utilitario` | Consumible o accesorio táctico | `cargador`, `vendaje`, `brújula`, `silbato`, `cuaderno` |
  | `equipo.vestidura` | Identidad visual de facción (no defensiva) | `uniforme confederado`, `uniforme rojo`, `ropa de civil`, `camuflaje básico` |

  La categoría es string libre — los enums son abiertos — pero el canon de v0.2.5 son las seis listadas. Usar valores fuera del canon es válido; el riesgo semántico está documentado en tensiones 13.1 y 13.2.

  **Reglas de derivación que dependen de tags:**
  - `fza_aportada` (DERIVADO): tag `{categoria: rol, valor: heroe}` → 3; `{categoria: rol, valor: lider}` → 2; sin ninguno → 1. El campo no se persiste; la API lo computa al servir.
  - `sobrenombre` en Ejército Rojo (DERIVADO): se construye desde el tag `skill` de mando más prominente: `Comandancia` → `"Comandante {nombre}"`; `Medicina` → `"Doctor {nombre}"`; `Ingeniería` → `"Ingeniero {nombre}"`; `Comisariado` → `"Camarada Puntero {nombre}"`; sin ninguno → `"Camarada {nombre}"`. Ver 7.3.
- **Distinción explícita trait / perk / aspecto** (tres familias cercanas, fáciles de confundir):
  - `trait` — rasgo de carácter o condición **sin efecto mecánico activo**. El motor o el narrador lo usa como color o contexto, no como regla. Ejemplos: `Obstinado`, `Voz grave`, `Mirada larga`. Pool abierto.
  - `perk` — ventaja activable **definida en el reglamento canónico del juego** (ver `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md`). Pool fijo de 12 valores canon; el efecto mecánico está documentado en el reglamento. Ejemplos: `Voz de mando`, `Recarga rápida`.
  - `aspecto` — mini-tag con **efecto mecánico embebido en una mini-frase** definida en `/meta/aspectos/{valor}.efecto`. Estructura semántica de la frase: trigger (condición de activación) + probabilidad opcional + efecto (bonus, repetición, activación de otro tag). Pool abierto, semilla canon de 10, customs permitidos pero no auto-generables. Inspirado en H.I.T.O.S. y Cultos Innombrables pero recortado a frase corta de mecánica directa.
- **Tags activables (`estado_temporal` como patrón implícito)**: algunos aspectos disparan tags transitorios — `cabrón` puede activar `[berserker]`, `cobarde` puede activar `[pánico]`. Estos tags **no se canonizan con catálogo cerrado** en v0.4.0: son un patrón reconocido (`categoria: estado_temporal`, sub-familia conceptual abierta) que el motor de batalla aplica y revoca según turno. Documentado para que el motor downstream sepa identificar el patrón cuando lo encuentre.
- **Principio del tag mínimo (v0.4.1)**: cada `valor` de tag es un **identificador corto** (idealmente 1-2 palabras, 3 cuando el nombre canónico lo requiere — `rifle militar`, `Tiro de precisión`). Nunca prosa, paréntesis, comas internas ni guiones largos. La info contextual ("brújula regalo del instructor", "cuaderno con anotaciones de terreno") **no vive en el tag**: vive en (a) la prosa de `historia` cuando el dato pertenece a la voz narrativa del personaje, (b) el catálogo `/meta/*` cuando es definición canónica, o (c) una futura entidad `notas: array<{tag_ref, texto}>` (ver OQ) si el contexto amerita persistencia estructurada. La info que no esté en ninguno de esos tres lugares se pierde — costo aceptado por el minimalismo. Aplicado transversalmente en v0.4.1 a los 22 mocks y a los ejemplos del PRD.
- **Decisión consciente — sub-categorías con punto**: el equipo se modela como `equipo.arma`, `equipo.utilitario`, `equipo.vestidura` (jerárquico con punto) en lugar de un sub-campo aparte. Ventajas: filtrado por prefijo `equipo.*`, legibilidad visual, sin nuevos sub-campos en el schema. Este patrón puede aplicarse a futuro a otras categorías que necesiten subdivisión.
- **Categoría `trait` sin polaridad**: incluye positivos (`Sangre fria`), neutros (`Voz grave`) y penalidades que antes eran complicaciones (`Miope`, `Hemorragia lenta`, `Objetivo prioritario`). El motor downstream decide cómo aplicar polaridad, opcionalmente consultando `/meta/traits/{valor}.polaridad` si existe. Ver tensión 13.6.
- **`vinculos[].ref_personaje_id`**: la API **no valida** que el id exista. `descripcion` es el fallback obligatorio.
- **`historia`**: prosa original. Se congela al canonizar.
- **`historial[]`**: solo hitos importantes. Sin paginación en v1.
- **`tags_iniciales`**: snapshot completo de `tags[]` al crear; inmutable; permite calcular diff entre estado original y vigente.
- **`extras`**: escape hatch deliberado. La API no inspecciona su contenido.

### 6.3. Ejemplo 1 — Confederado (mock canonizado con historia acumulada)

```yaml
personaje:
  id: mock.confederacion.01.aguirre
  origen: mock
  semilla: mock-fixed-01

  # Cabecera (orden v0.2.5)
  nombre: Walter Aguirre
  sobrenombre: Sargento Walter Aguirre
  filiacion: "Lider de escuadra de la Escuadra Ricardo del Ejército de la Confederación Argentina"

  faccion: Confederación

  edad: 28
  genero: masculino
  estado_salud: saludable

  rol: Sargento Confederado

  estado: activo
  rango: Lider de escuadra
  escuadra_id: esq_conf_03
  mando: true

  lealtades:
    primaria: Sargento Ricardo (post mortem)
    secundarias:
      - su escuadra
      - los aserraderos del alto valle
    secretos: []

  atributos:
    fis: 3
    tac: 5
    men: 7

  tags:
    # rasgo
    - { categoria: rasgo, valor: "altura media" }
    - { categoria: rasgo, valor: "complexion atletica" }
    - { categoria: rasgo, valor: "pelo corto" }
    - { categoria: rasgo, valor: "barba corta" }
    - { categoria: rasgo, valor: "mirada lenta" }
    - { categoria: rasgo, valor: "cicatriz en ceja" }
    # rol (mecánico)
    - { categoria: rol, valor: "lider" }
    # skills (antes: especialidad + saberes implícitos)
    - { categoria: skill, valor: "Comandancia" }
    - { categoria: skill, valor: "Lectura de terreno" }
    # traits (sin polaridad; ex-complicación migra acá como Eco del peñasco)
    - { categoria: trait, valor: "Mirada larga" }
    - { categoria: trait, valor: "Eco del peñasco" }   # penalidad: tras caída aliada, MEN desfavorable la ronda siguiente
    # perks (ex-perk_fijo migra acá como Sucesor de Ricardo)
    - { categoria: perk, valor: "Sucesor de Ricardo" }  # sin líder funcional, MEN favorable para mando/iniciativa
    # aspecto (efecto mecánico en mini-frase; ver /meta/aspectos)
    - { categoria: aspecto, valor: "ojo-de-halcón" }    # +1 INICIATIVA en el primer turno de batalla
    # equipo.arma
    - { categoria: "equipo.arma", valor: "rifle militar" }
    - { categoria: "equipo.arma", valor: "pistola" }
    # equipo.utilitario
    - { categoria: "equipo.utilitario", valor: "prismáticos" }
    - { categoria: "equipo.utilitario", valor: "cuaderno" }
    # equipo.vestidura (identidad visual de facción)
    - { categoria: "equipo.vestidura", valor: "uniforme confederado" }

  vinculos:
    - tipo: mentor
      ref_personaje_id: null
      descripcion: >
        Sargento Ricardo, su mentor, caído en el Sector 12,15. Aguirre heredó
        el parche y el peso. No habla de él, pero firma con la inicial R en el margen.
    - tipo: subordinado
      ref_personaje_id: mock.confederacion.02.sosa
      descripcion: "Cabo Primero Sosa, su mano derecha. Le confía la columna cuando él va al frente."
    - tipo: hermano_de_armas
      ref_personaje_id: mock.confederacion.05.rodriguez
      descripcion: "Soldado Marcela Rodríguez. Sobrevivieron juntos al invierno del 24."

  historia: |
    Walter Aguirre es de Neuquén, aunque hace tres años que no pisa la provincia.
    Antes del servicio trabajaba con su padre en corte de madera en el alto valle —
    sabe leer el terreno boscoso porque pasó la infancia entre árboles que matan
    si no los respetás. Entró a la Confederación como conscripto, sobrevivió al
    primer invierno en el frente sur, y llegó a soldado de primera antes de que
    alguien notara que era más cuidadoso que la mayoría. El Sargento Ricardo lo
    eligió Cabo Primero al mes. No con palabras: con tareas que necesitaban
    hacerse bien, no rápido. En el Sector 12,15, cuando la radio se rompió y
    Ricardo cayó, Walter organizó la columna y sacó a todos. Semanas después
    llegó el parche. No lo festejó.

  historial:
    - fecha: "2026-03-12T14:20:00Z"
      tipo: ascenso
      descripcion: "Ascendido a Sargento tras la pérdida de Ricardo en el Sector 12,15."
      ref_batalla: "batalla_sector_12_15"
      metadata:
        rango_anterior: "Segundo al mando"
        rango_nuevo: "Lider de escuadra"
    - fecha: "2026-04-02T09:00:00Z"
      tipo: agregar_tag
      descripcion: "Recuperó los prismáticos del oficial enemigo abatido en la cresta norte."
      ref_batalla: "batalla_cresta_norte"
      metadata:
        categoria: "equipo.utilitario"
        valor: "prismáticos"
    - fecha: "2026-05-10T22:45:00Z"
      tipo: triple_cero
      descripcion: "Triple-0 en chequeo de MEN durante la retirada táctica de Estación 9."
      ref_batalla: "batalla_estacion_9"
      metadata:
        atributo: men
        delta: 1
        valor_anterior: 6
        valor_nuevo: 7

  tags_iniciales:
    - { categoria: rasgo, valor: "altura media" }
    - { categoria: rasgo, valor: "complexion atletica" }
    - { categoria: rasgo, valor: "pelo corto" }
    - { categoria: rasgo, valor: "barba corta" }
    - { categoria: rasgo, valor: "mirada lenta" }
    - { categoria: rol, valor: "lider" }
    - { categoria: skill, valor: "Comandancia" }
    - { categoria: skill, valor: "Lectura de terreno" }
    - { categoria: trait, valor: "Mirada larga" }
    - { categoria: trait, valor: "Eco del peñasco" }
    - { categoria: perk, valor: "Sucesor de Ricardo" }
    - { categoria: aspecto, valor: "ojo-de-halcón" }
    - { categoria: "equipo.arma", valor: "rifle militar" }
    - { categoria: "equipo.arma", valor: "pistola" }
    - { categoria: "equipo.utilitario", valor: "cuaderno" }
    - { categoria: "equipo.vestidura", valor: "uniforme confederado" }

  metadatos:
    creado_en: "2026-01-15T00:00:00Z"
    canonizado_en: "2026-01-15T00:00:00Z"
    ultima_actualizacion: "2026-05-10T22:45:00Z"
    modelo_prosa: null
    es_canon: true

  # Derivados servidos por la API (no persistidos):
  #   filiacion: ya en cabecera
  #   fza_aportada: 2   (tag rol=lider)

  extras: null
```

### 6.4. Ejemplo 2 — Ejército Rojo (mock canonizado con historia acumulada)

```yaml
personaje:
  id: mock.ejercito_rojo.01.mansilla
  origen: mock
  semilla: mock-fixed-12

  # Cabecera (orden v0.2.5)
  nombre: Ramón Mansilla
  sobrenombre: Camarada Puntero Ramón Mansilla
  filiacion: "Lider de escuadra de la Escuadra Belenchini del Ejército Revolucionario del Pueblo"

  faccion: Ejército Rojo

  edad: 34
  genero: masculino
  estado_salud: saludable

  rol: Líder Revolucionario

  estado: activo
  rango: Lider de escuadra
  escuadra_id: esq_rojo_07
  mando: true

  lealtades:
    primaria: Ejército Rojo
    secundarias:
      - el boletín sindical de los metalúrgicos
      - los instructores de Stroeder
    secretos:
      - mantiene correspondencia con un primo en territorio Confederado

  atributos:
    fis: 3
    tac: 5
    men: 7

  tags:
    # rasgo
    - { categoria: rasgo, valor: "altura alta" }
    - { categoria: rasgo, valor: "complexion delgada" }
    - { categoria: rasgo, valor: "pelo entrecano" }
    - { categoria: rasgo, valor: "lentes" }
    - { categoria: rasgo, valor: "voz grave" }
    # rol (mecánico)
    - { categoria: rol, valor: "lider" }
    # skills (ex-especialidad: "comisariado" + saberes operativos)
    - { categoria: skill, valor: "Comisariado" }
    - { categoria: skill, valor: "Oratoria" }
    - { categoria: skill, valor: "Lectura de mapas" }
    # traits (ex-complicación c06_obstinado migra acá)
    - { categoria: trait, valor: "Voz grave" }
    - { categoria: trait, valor: "Obstinado" }   # penalidad: si la orden implica retroceder, MEN desfavorable
    # perks (ex-perk_fijo p03_voz_de_mando)
    - { categoria: perk, valor: "Voz de mando" }
    # aspecto (efecto mecánico en mini-frase; ver /meta/aspectos)
    - { categoria: aspecto, valor: "carismático" }      # +1 a chequeos MEN de aliados en el mismo hex
    # equipo.arma
    - { categoria: "equipo.arma", valor: "SMG" }
    - { categoria: "equipo.arma", valor: "pistola" }
    # equipo.utilitario
    - { categoria: "equipo.utilitario", valor: "cuaderno" }
    - { categoria: "equipo.utilitario", valor: "brújula" }
    # equipo.vestidura (identidad visual de facción)
    - { categoria: "equipo.vestidura", valor: "uniforme rojo" }

  vinculos:
    - tipo: mentor
      ref_personaje_id: null
      descripcion: >
        Instructor Belenchini (de Stroeder), que le enseñó a leer mapas
        cuando todavía redactaba comunicados sindicales.
    - tipo: rival
      ref_personaje_id: mock.confederacion.01.aguirre
      descripcion: >
        Sargento Aguirre. Mansilla anotó su nombre en el informe del Sector
        12,15. No se conocen en persona; el rival es de papel y de mapa.
    - tipo: subordinado
      ref_personaje_id: mock.ejercito_rojo.02.iturra
      descripcion: "Segundo Camarada Iturra. Cuadro disciplinado, pero lento para improvisar."

  historia: |
    Mansilla no disparó un arma en combate hasta los treinta y dos años. Era
    redactor del boletín sindical de los metalúrgicos de Bahía Blanca, después
    comisario político de la segunda región, después instructor de cuadros en
    Stroeder. La revolución tiene usos para un hombre que sabe leer mapas y
    convencer a otros de que la causa vale el riesgo. El campo de batalla no
    estaba en su programa. Cuando llegó el informe del Sector 12,15, Mansilla
    fue uno de los tres hombres que lo analizaron. Anotó: "respuesta táctica
    competente del oficial azul". Después recomendó eliminarlo antes de la
    siguiente operación. El alto mando lo comisionó para liderar la escuadra
    de caza — no por tirador, sino porque conoce el informe y no carga rencor.

  historial:
    - fecha: "2026-02-28T10:00:00Z"
      tipo: traslado
      descripcion: "Comisionado de Stroeder al frente sur como líder de escuadra de caza."
      ref_batalla: null
      metadata:
        motivo: "decisión del alto mando tras análisis del Sector 12,15"
    - fecha: "2026-04-18T17:30:00Z"
      tipo: formacion_vinculo
      descripcion: "Identifica formalmente al Sargento Aguirre como objetivo prioritario."
      ref_batalla: null
      metadata:
        vinculo_creado:
          tipo: rival
          ref: mock.confederacion.01.aguirre
    - fecha: "2026-05-03T11:15:00Z"
      tipo: condecoracion
      descripcion: "Reconocimiento del Comité Central por la operación de Estación 9."
      ref_batalla: "batalla_estacion_9"
      metadata:
        otorgado_por: "Comité Central"

  tags_iniciales:
    - { categoria: rasgo, valor: "altura alta" }
    - { categoria: rasgo, valor: "complexion delgada" }
    - { categoria: rasgo, valor: "pelo entrecano" }
    - { categoria: rasgo, valor: "lentes" }
    - { categoria: rasgo, valor: "voz grave" }
    - { categoria: rol, valor: "lider" }
    - { categoria: skill, valor: "Comisariado" }
    - { categoria: skill, valor: "Oratoria" }
    - { categoria: skill, valor: "Lectura de mapas" }
    - { categoria: trait, valor: "Voz grave" }
    - { categoria: trait, valor: "Obstinado" }
    - { categoria: perk, valor: "Voz de mando" }
    - { categoria: aspecto, valor: "carismático" }
    - { categoria: "equipo.arma", valor: "SMG" }
    - { categoria: "equipo.arma", valor: "pistola" }
    - { categoria: "equipo.utilitario", valor: "cuaderno" }
    - { categoria: "equipo.utilitario", valor: "brújula" }
    - { categoria: "equipo.vestidura", valor: "uniforme rojo" }

  metadatos:
    creado_en: "2026-01-15T00:00:00Z"
    canonizado_en: "2026-01-15T00:00:00Z"
    ultima_actualizacion: "2026-05-03T11:15:00Z"
    modelo_prosa: null
    es_canon: true

  # Derivados servidos por la API (no persistidos):
  #   filiacion: ya en cabecera
  #   fza_aportada: 2   (tag rol=lider)

  extras: null
```

---

## 7. Reglas de generación dinámica

Cómo se completa cada campo en un personaje **generado dinámicamente** (origen `"generado"`). Los mocks ignoran estas reglas: vienen escritos a mano. Los canonizados nacen como un generado o como un body explícito, y a partir de ahí mutan vía hitos (sección 9).

### 7.1. Inputs y orden de resolución

El cliente pasa hasta tres parámetros: `faccion`, `rango` (o un alias de rango operativo), `seed`. Si falta alguno, se sortea desde la semilla. Orden:

1. Resolver `seed` (si no vino, generar uno criptográfico y devolverlo).
2. Inicializar PRNG determinístico con `seed`.
3. Resolver `faccion` (input o sorteo uniforme entre las 2 facciones MVP).
4. Resolver `rango` (input o sorteo según distribución de escuadra de 11: ver 7.2).
5. Derivar atributos `{fis, tac, men}` desde la matriz por rango.
6. Derivar `mando` (bool) y `estado` default según rango (ver 7.2).
7. Sortear campos narrativos (nombre, edad, género, rasgos, rol cultural).
8. Componer `sobrenombre` determinísticamente según facción (ver 7.3).
9. Inicializar `tags` con pools sorteados de `rasgo`, `rol`, `skill`, `trait`, `perk`, `equipo.arma`, `equipo.utilitario`, `equipo.vestidura` — cada categoría tiene sus propias reglas de sorteo detalladas en 7.4–7.8.
10. Inicializar bloques vacíos (`lealtades.secretos: []`, `vinculos: []`, `historial: []`).
11. Generar `historia` con LLM, anclada en facción + rango + rol + skills/traits/perks + lugar implícito.
12. Copiar `tags` a `tags_iniciales` (snapshot inmutable).
13. La API compone `filiacion` y `fza_aportada` derivados al servir.

### 7.2. Atributos, `mando`, `estado` (determinísticos por rango)

Tabla derivada de `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md`. **No se sortean.** La columna `rol_id` interna del motor de creación mapea al `rango` público.

| `rango` (público) | Rol Confederación (rol cultural) | Rol Ejército Rojo (rol cultural) | FIS | TAC | MEN | `mando` default | `estado` default |
|---|---|---|---|---|---|---|---|
| `Lider de escuadra` | Sargento Confederado | Líder Revolucionario | 3 | 5 | 7 | `true` | `disponible` |
| `Segundo al mando` | Cabo Primero | Segundo Camarada | 3 | 5 | 6 | `true` | `disponible` |
| `Apuntador` | Apuntador | Tirador | 3 | 5 | 5 | `false` | `disponible` |
| `Artillero` | Artillero FAP | Ametrallador | 3 | 4 | 3 | `false` | `disponible` |
| `Fusilero` | Fusilero / Soldado 1ª | Miliciano Veterano | 3 | 3 | 3 | `false` | `disponible` |
| `Recluta` | Recluta / Soldado 2ª | Voluntario | 3 | 2 | 2 | `false` | `disponible` |

**`mando` default**: `true` para `Lider de escuadra` y `Segundo al mando` (capacidad de asumir liderazgo); `false` para el resto. Cambiar `mando` post-creación requiere hito `cambio_mando`.

**`estado` default**: `disponible` para todo generado sin escuadra asignada. Cuando se asigna `escuadra_id` (vía hito `asignacion_escuadra`), pasa a `activo`.

**Distribución por escuadra de 11**: 1 + 1 + 1 + 1 + 4 + 3.

**Sorteo de rango cuando no se fija**: proporcional a la composición (la API tiende a entregar fusileros/reclutas, lo cual es realista).

#### 7.2.1. Estado vital derivado por rango

Tabla de referencia de `fatiga_max` y `moral_max` según la matriz de atributos de §7.2. Derivada en creación: `fatiga_max = fis + men`; `moral_max = men`. Los valores persisten en la hoja y mutan solo si cambia el atributo base.

| Rango | FIS | TAC | MEN | `fatiga_max` (FIS+MEN) | `moral_max` (MEN) |
|---|---|---|---|---|---|
| `Lider de escuadra` | 3 | 5 | 7 | **10** | **7** |
| `Segundo al mando`  | 3 | 5 | 6 | **9**  | **6** |
| `Apuntador`         | 3 | 5 | 5 | **8**  | **5** |
| `Artillero`         | 3 | 4 | 3 | **6**  | **3** |
| `Fusilero`          | 3 | 3 | 3 | **6**  | **3** |
| `Recluta`           | 3 | 2 | 2 | **5**  | **2** |

Promedio de escuadra (composición 1+1+1+1+4+3): ≈ 6.5 de fatiga, ≈ 3.9 de moral.

### 7.3. `nombre` y `sobrenombre` (sorteo + composición determinística)

**`nombre`**: tabla curada de nombres reales (sin prefijo de rango), segmentada por facción. Excluye los 22 ya canonizados.

- **Confederación**: tono militar formal, gentilicios del centro/norte/cuyo. Ejemplos canon: *Aguirre, Sosa, Quiroga, Funes, Rodríguez, Olivares, Acosta, Pereyra, Méndez, Lugones, Ramírez*.
- **Ejército Rojo**: tono obrero/patagónico, apellidos con presencia mapuche y costa sur. Ejemplos canon: *Mansilla, Iturra, Antinao, Calfucurá, Cárcamo, Paine, Soriano, Belenchini, Bordón, Maturana, Bordagaray, Quilodran*.

**`sobrenombre`**: composición determinística desde `nombre` real:

- **Confederación**: `{rango militar narrativo} + {nombre}`. Ej. "Sargento Walter Aguirre".
- **Ejército Rojo**: usa un título derivado de una **skill** de comandancia, medicina o ingeniería si está presente; si no, título revolucionario genérico + nombre. Ej. con skill `Medicina` → "Doctor Quilodran"; con skill `Comandancia` → "Camarada Puntero Quilodran"; sin ninguna → "Camarada Quilodran".
- **`null`**: cuando no hay distinción con el nombre real.

### 7.4. `edad`, `genero`

- **`edad`**: sorteo en rango sugerido por rango operativo (reclutas: 18–24; fusileros: 20–35; líderes: 28–45). Tabla curada.
- **`genero`**: distribución curada por facción (Confederación ~85/15/0/0; Ejército Rojo ~70/25/5/0). Abierto.

(El bloque `origen_geografico` fue eliminado en v0.2.3. Si la procedencia importa narrativamente, se cuenta en `historia` o se añade como `rasgo` / `extras`.)

### 7.5. Tags de `rasgo`

El generador produce 1 tag de altura + 1 tag de complexión obligatorios, más 2-3 rasgos físicos sorteados de pool corto segmentado por facción:

- **Confederación**: pools con rasgos que reflejan procedencia del interior — tez mate, rasgos rurales, marcas de trabajo físico en tierra seca. Ejemplos: `complexión atlética`, `manos callosas`, `mirada directa`.
- **Ejército Rojo**: pools con rasgos de procedencia costera/industrial patagónica — tez curtida de puerto o de meseta, marcas de trabajo manual en frío. Ejemplos: `complexión delgada`, `manos ásperas`, `lentes de armazón fino`.

Sin tags de cicatriz en creación — las cicatrices son consecuencia narrativa y se agregan vía hito `agregar_tag {categoria: rasgo}` después de una herida o acción dramática. En mocks los rasgos son ricos y escritos a mano; en canonizados heredan y acumulan.

### 7.6. Tags de `rol` (mecánico)

El generador asigna exactamente 1 tag `categoria: rol` derivado del `rango` del personaje. Tabla de conversión:

| `rango` | tag `rol` generado | `fza_aportada` derivado |
|---|---|---|
| `Lider de escuadra` | `lider` | 2 |
| `Segundo al mando` | `lider` | 2 |
| `Apuntador` | `tirador` | 1 |
| `Artillero` | `artillero` | 1 |
| `Fusilero` | `fusilero` | 1 |
| `Recluta` | `recluta` | 1 |

El tag `heroe` (→ `fza_aportada: 3`) no se genera en creación — es un tag que solo se agrega vía hito `agregar_tag` por acción extraordinaria reconocida narrativamente.

### 7.7. Tags de `skill`

Pool curado por facción y rango. El generador agrega 1-3 skills según rango:

| `rango` | Skills garantizados | Skills adicionales (sorteo del pool facción) |
|---|---|---|
| `Lider de escuadra` | `Comandancia` | 1-2 del pool (ej. `Oratoria de muelle`, `Lectura de columna` para Ejército Rojo; `Lectura de terreno` para Confederación) |
| `Segundo al mando` | — | 1-2 del pool (tácticos o de comunicación) |
| `Apuntador` | `Francotirador` | 0-1 adicional |
| `Artillero` | — | 1 del pool de artillería |
| `Fusilero` | — | 0-1 del pool general |
| `Recluta` | — | 0 (raramente 1 simple) |

El tag `skill` más prominente en Ejército Rojo influye en la composición del `sobrenombre` (ver 7.3 y nota de derivación en 6.2).

### 7.8. Tags de `trait`

Pool curado abierto, sin polaridad fija. El generador agrega 1-2 traits:

- **80% del peso**: traits coherentes con el rol y rango (ej. `Sangre fría` para líderes, `Voz grave` para oradores, `Mirada larga` para apuntadores).
- **20% del peso**: "complicación" — trait con efecto mecánico desfavorable en alguna circunstancia (`Miope`, `Obstinado`, `Hemorragia lenta`, `Objetivo prioritario`). Esta distribución es análoga al 80/20 de perks: el personaje siempre tiene algún borde oscuro potencial.

Los traits no se eliminan fácilmente — a diferencia del equipo, son parte de la identidad. Quitarlos vía hito `quitar_tag {categoria: trait}` requiere justificación narrativa explícita en `descripcion`.

### 7.9. Tags de `perk`

Pool canon (origen en `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md`). **Restricción 80/20 soft**: ~80% sobre el subconjunto natural del rango, ~20% libre para perks inesperados que den sabor. El generador agrega típicamente 1 perk (líderes con más probabilidad; reclutas raramente).

Perks canon actuales de referencia (abierto, no exhaustivo):

| Perk | Rango natural | Efecto resumido |
|---|---|---|
| `Voz de mando` | Líder / Segundo | MEN favorable en chequeo de mando colectivo |
| `Recarga rápida` | Artillero / Apuntador | Recarga sin costo de acción |
| `Cobertura instintiva` | Fusilero / Segundo | Se cubre automáticamente al primer disparo recibido |
| `Sucesor de Ricardo` | Líder | MEN favorable para mando/iniciativa cuando no hay líder funcional |

### 7.9.5. Tags de `aspecto`

Pool semilla canon de 10 aspectos en `/meta/aspectos` (ver 10.x). **Política deliberada: los aspectos son raros.** No todo personaje generado tiene uno — debe haber un porqué narrativo. Distribución del generador:

- **70%**: 0 aspectos. La mayoría de fusileros y reclutas no llevan aspecto.
- **25%**: 1 aspecto. Sorteo del pool semilla con peso por rango (líderes ponderan a `cabrón`, `carismático`, `terco`; apuntadores ponderan a `ojo-de-halcón`; artilleros y veteranos a `muy-fuerte`, `veterano-cicatrizado`).
- **5%**: 2 aspectos. Casos de personajes notables. El generador rara vez los emite; típicamente aparecen en mocks o en canonizados que acumulan aspectos vía hito.

**Customs**: permitidos en mocks y canonizados (vía hito `agregar_aspecto`), pero **no auto-generables**. Cualquier aspecto fuera del pool semilla debe ser curado a mano y registrado en `/meta/aspectos` para que el motor downstream lo pueda interpretar.

### 7.10. `lealtades`

- **En generados**: `primaria` = nombre de la facción; `secundarias` = 0-2 entradas sorteadas; `secretos: []`.
- **En mocks y canonizados**: ricas, escritas o agregadas vía hito.

### 7.11. Tags de `equipo.*`

Pool curado `rango × faccion` produce tags en lugar de objetos estructurados.

| `rango` | Confederación (default) | Ejército Rojo (default) |
|---|---|---|
| `Lider de escuadra` | `rifle militar` + `pistola` | `SMG` + `pistola` |
| `Segundo al mando` | `rifle militar` + `pistola` | `SMG` o `rifle militar` + `pistola` |
| `Apuntador` | `rifle militar` (larga) | `rifle militar` (larga) |
| `Artillero` | `ametralladora` | `ametralladora` |
| `Fusilero` | `rifle militar` | `rifle militar` o `SMG` |
| `Recluta` | `rifle militar` | Lo que haya disponible |

- **`equipo.arma`**: un valor genérico del catálogo de 6 (`pistola`, `revolver`, `rifle`, `rifle militar`, `SMG`, `ametralladora`). El alcance ya no se incluye en el valor del tag.
- **`equipo.utilitario`**: 50% ninguno, 50% 1 tag genérico (`cargador`, `vendaje`, `cantimplora`). En mocks: hasta 4-5 narrativos.
- **`equipo.vestidura`**: tabla determinística por facción. Todos los Confederados: `uniforme confederado`. Rojos integrados (líderes, veteranos): `uniforme rojo`. Rojos de origen civil reciente o andrajosos: `ropa de civil` o `camuflaje básico`. Catálogo canon: `uniforme confederado`, `uniforme rojo`, `ropa de civil`, `camuflaje básico`.

### 7.12. `vinculos` y `historial`

- **En generados dinámicamente**: ambos vacíos.
- **En mocks**: inicializados con el contenido a mano.
- **En canonizados**: heredan; el motor downstream los puebla vía evento.

### 7.13. `historia` (LLM)

Prosa de 120–200 palabras. Prompt recibe: `faccion`, `rol`, `rango`, skills/traits/perks principales, `nombre`, `sobrenombre`, `edad`, `genero`. Instrucción de tono militar austero, voz rioplatense, 2–3 párrafos.

Cache por `hash(seed + inputs + version_modelo)`. Si se canoniza, se congela.

### 7.14. `tags_iniciales` y `estado_salud`

- `tags_iniciales` = snapshot completo de `tags[]` al crear; inmutable.
- `estado_salud` = `"saludable"` en creación.

---

## 8. Reproducibilidad por semilla

- Toda llamada de **generación efímera** admite `?seed=<string>`. Si no se pasa, la API genera uno y lo retorna en `personaje.semilla`.
- PRNG determinístico. La prosa LLM se cachea por clave `(seed, inputs, version_modelo)`.
- Garantía contractual para **efímeros**: con `(seed, faccion, rango)` fijos y `version_modelo` fija, la respuesta es byte-a-byte equivalente excepto `metadatos.creado_en`.

**Limitación aceptada para canonizados:** tras la canonización, el personaje conserva su `semilla` pero deja de ser regenerable porque su historial muta. Esto es deliberado.

---

## 9. Memoria viva — el diferencial del producto

### 9.1. Naturaleza del canonizado

Un personaje canonizado **existe en el tiempo**. La ficha que devuelve `GET /character/{id}` es el **estado vigente**, no el original.

### 9.2. Eventos y mutación

Los cambios ocurren vía `POST /character/{id}/event`. La API apendea al `historial[]`, aplica el efecto sobre campos vigentes, y actualiza `metadatos.ultima_actualizacion`.

### 9.3. Campos mutables vs inmutables

**Mutables** (cambian vía hito):

- `atributos.{fis, tac, men}` (via `triple_cero` o `mejora_atributo`).
- `tags[]` (vía `agregar_tag` / `quitar_tag` — cubre rasgos, skills, traits, perks, equipo en todas sus sub-categorías).
- `vinculos[]` (vía `formacion_vinculo`, `ruptura_vinculo`).
- `lealtades.secundarias`, `lealtades.secretos` (vía `cambio_lealtad`).
- `rol`, `rango` (vía `ascenso`, `traslado`, `cambio_rango`). Atributos `{fis, tac, men}` NO se tocan; los tags `categoria: rol` se realinean.
- `escuadra_id` (vía `asignacion_escuadra`).
- `mando` (vía `cambio_mando`).
- `estado` (vía `cambio_estado` — incluye transiciones a `kia`, `licencia`, etc.).
- `estado_salud` (vía `herida`, `recuperacion`).
- `sobrenombre` (vía `ascenso` o `cambio_rango`, cuando el título cambia).
- `metadatos.ultima_actualizacion` (siempre).

**Inmutables** (definen la identidad del canonizado):

- `id`, `nombre`, `genero`, `semilla`, `historia`, `tags_iniciales`.
- `metadatos.creado_en`, `metadatos.canonizado_en`, `metadatos.modelo_prosa`, `metadatos.es_canon`.

**`edad`**: mutable vía decisión narrativa explícita; sin hito formal.

**`filiacion`, `fza_aportada`**: derivados al servir; no mutables porque no son persistidos.

### 9.4. Granularidad del historial

Solo hitos importantes. **Sin límite ni paginación en v1.**

### 9.5. Tipos de hito (canon sugerido — abierto)

| `tipo` | Disparador típico | Efecto sobre campos vigentes |
|---|---|---|
| `triple_cero` | Motor | `atributos.<atributo> += 1` (techo 5; MEN-líder 7); `metadata: { atributo, delta, valor_anterior, valor_nuevo }` |
| `mejora_atributo` | Narrador | igual a `triple_cero` sin disparador mecánico |
| `ascenso` | Narrador | `rol`, `rango` se reemplazan; `sobrenombre` se recompone; tags `categoria: rol` se realinean; atributos NO se tocan; `metadata: { rango_anterior, rango_nuevo }` |
| `traslado` | Narrador | `rol` y/o `rango` y/o `escuadra_id` cambian; atributos NO se tocan |
| `cambio_rango` | Narrador o motor | `rango` se reemplaza; `metadata: { de, a, motivo }` |
| `cambio_mando` | Narrador o motor | `mando` (bool) se reemplaza; ningún otro campo cambia; `metadata: { de, a, motivo }` |
| `cambio_estado` | Motor o narrador | `estado` se reemplaza (ej. transición a `kia`, `licencia`); `metadata: { de, a, motivo }` |
| `asignacion_escuadra` | Narrador o motor | `escuadra_id` se reemplaza; típicamente lleva `estado: activo` cuando pasa a una escuadra real; `metadata: { de, a, motivo }` |
| `agregar_tag` | Motor o narrador | append a `tags[]`; `metadata: { categoria, valor }` |
| `quitar_tag` | Motor o narrador | remove de `tags[]`; `metadata: { categoria, valor }` |
| `agregar_aspecto` | Narrador o motor | append a `tags[]` con `categoria: aspecto`; `metadata: { valor, motivo }`. Atajo semántico de `agregar_tag` para la categoría que requiere curaduría explícita |
| `quitar_aspecto` | Narrador | remove de `tags[]` con `categoria: aspecto`; `metadata: { valor, motivo }` |
| `herida` | Motor o narrador | `estado_salud: "herido"`; opcionalmente `agregar_tag` con `categoria: rasgo` |
| `recuperacion` | Motor o narrador | `estado_salud: "saludable"` |
| `formacion_vinculo` | Narrador | append a `vinculos[]`; `metadata: { vinculo_creado }` |
| `ruptura_vinculo` | Narrador | remove o transformación de `vinculos[]` |
| `cambio_lealtad` | Narrador | mutación de `lealtades.secundarias` o `lealtades.secretos` |
| `condecoracion` | Narrador | no muta campos vigentes (hito puro) |
| `cambio_estado_vital` | Motor o narrador | mutación de `estado_vital.{fatiga_actual,moral_actual,fatiga_max,moral_max}`; `metadata: { campo, valor_anterior, valor_nuevo, motivo }` |

**Detalle de `agregar_tag` y `quitar_tag` — los hitos de tags son el mecanismo central de evolución del personaje.**

`agregar_tag` y `quitar_tag` operan sobre cualquier categoría de la lista plana `tags[]`. `metadata` siempre lleva `{ categoria, valor }` como mínimo; se puede extender con contexto narrativo o mecánico.

Ejemplos representativos:

| Situación narrativa | `tipo` | `metadata` ejemplo |
|---|---|---|
| Personaje aprende una habilidad de su mentor | `agregar_tag` | `{ categoria: "skill", valor: "Lectura de columna" }` |
| Herida grave en combate deja secuela | `agregar_tag` | `{ categoria: "trait", valor: "Hemorragia lenta" }` + hito `herida` coordinado |
| Captura enemiga. Le requisaron el arma | `quitar_tag` | `{ categoria: "equipo.arma", valor: "rifle militar" }` |
| Captura y recuperación de armamento enemigo | `agregar_tag` | `{ categoria: "equipo.arma", valor: "pistola" }` |
| Hazaña reconocida por el alto mando | `agregar_tag` | `{ categoria: "perk", valor: "Cobertura instintiva" }` |
| Consigue tres cargadores tras asaltar una posición | `agregar_tag` (×3) | `{ categoria: "equipo.utilitario", valor: "cargador" }` — tres hitos independientes o un único hito con `metadata.cantidad: 3` si la implementación lo admite |
| Recupera visión normal tras tratamiento | `quitar_tag` | `{ categoria: "trait", valor: "Miope" }` — requiere justificación narrativa en `descripcion` |

**Trayectoria de tags y auditoría.** El estado vigente de `tags[]` es el resultado de aplicar en orden todos los hitos `agregar_tag` y `quitar_tag` sobre el snapshot `tags_iniciales` (inmutable al crear). Esto significa que la trayectoria completa de tags de un personaje se puede reconstruir reproduciendo su `historial[]` contra `tags_iniciales`, sin necesidad de un campo de historial separado para tags. Operación útil para auditoría y para el endpoint potencial `POST /character/{id}/original` (ver OQ #8).

**Nota — aspectos mutables ya no aplican como bloque.** En v0.2.5 no existen los hitos `mejora_aspecto`. Los cambios de identidad mecánica (perk, trait, skill) son adiciones/eliminaciones a las categorías correspondientes vía `agregar_tag` / `quitar_tag`.

**Nota — atributos y rango.** Los atributos `{fis, tac, men}` son propiedad del personaje, no derivados del rango post-creación. Cuando cambia `rango`, los atributos no se tocan. Los tags `categoria: rol` sí se realinean. La matriz por rango (7.2) aplica **únicamente** en creación.

---

## 10. Endpoints (alto nivel)

### `GET /character`

Genera un personaje efímero. Parámetros opcionales: `faccion`, `rango`, `seed`, `fields`.

Devuelve un `personaje` con `origen: "generado"`, `id: null`, `es_canon: false`, `historial: []`, `vinculos: []`, `metadatos.canonizado_en: null`, `estado: "disponible"`, `escuadra_id: null`.

Mapea: UC-01..04, UC-06, UC-16.

### `GET /character/{id}`

Devuelve el personaje con id exacto. 404 si no existe. Acepta `fields=` para podar.

Mapea: UC-05, UC-15, UC-16.

### `GET /character/{id}/historial`

Devuelve solo `historial[]`. Sin paginación en v1.

Mapea: UC-17.

### `POST /character/{id}/event`

Registra un hito sobre un canonizado. Body: una entrada de `historial[]`. Apendea, aplica efecto, actualiza timestamp, devuelve ficha actualizada. 409 sobre mocks; 404 sobre efímeros. Ver OQ #2 sobre gobernanza.

Mapea: UC-10..14, UC-18.

### `GET /roster/mock`

Lista los 22 fixtures con `id`, `nombre`, `sobrenombre`, `faccion`, `rango`, `rol`. Sin payload completo.

Mapea: UC-08.

### `POST /canonize`

Persiste un personaje generado como canon. Asigna `id`, congela `historia`, fija `canonizado_en`. Idempotente por `(seed, faccion, rango)`.

Mapea: UC-07.

### `GET /meta/factions`

Catálogo de facciones con descriptor de lore corto.

### `GET /meta/rangos`

Catálogo de rangos sugeridos con tabla de stats, `mando` default, `estado` default, rol cultural por facción.

### `GET /meta/skills`

Pool canon de habilidades. Cada entrada: `{ valor, descripcion, rangos_naturales: [], facciones_predominantes: [] }`. Ejemplos canon: `Comandancia`, `Tiro de precisión`, `Primeros auxilios`, `Oratoria`, `Lectura de terreno`, `Coordinación`, `Comisariado`. El endpoint lista el vocab sugerido; valores fuera del canon son válidos.

### `GET /meta/traits`

Pool canon de rasgos de carácter/condición. Cada entrada: `{ valor, descripcion, polaridad_sugerida: "positivo"|"neutro"|"penalidad"|null, rangos_comunes: [] }`. Ejemplos canon: `Sangre fría` (positivo), `Voz grave` (neutro), `Miope` (penalidad), `Obstinado` (penalidad), `Objetivo prioritario` (penalidad), `Hemorragia lenta` (penalidad). El campo `polaridad_sugerida` es hint no autoritativo — ver tensión 13.6.

### `GET /meta/perks`

Pool canon de ventajas mecánicas. Cada entrada: `{ valor, descripcion, efecto_mecanico, rangos_naturales: [] }`. Ejemplos canon: `Voz de mando`, `Recarga rápida`, `Cobertura instintiva`. El efecto mecánico describe el resultado en juego (ej. "MEN favorable en chequeo de mando colectivo").

### `GET /meta/aspectos`

Pool canon de aspectos. Cada entrada: `{ valor, efecto, activa_tag?, rangos_naturales?: [] }`. El campo `efecto` es la **mini-frase** de mecánica embebida (texto libre, en castellano, que el motor downstream interpreta). El campo opcional `activa_tag` indica cuando el efecto del aspecto dispara un tag transitorio (categoría conceptual `estado_temporal`, ej. `berserker`, `pánico`).

Pool semilla v0.4.0 (10 aspectos):

| `valor` | `efecto` | `activa_tag` |
|---|---|---|
| `cabrón` | 75% de activar tag `[berserker]` si falla tirada de MENTAL. | `berserker` |
| `ojo-de-halcón` | +1 INICIATIVA en el primer turno de batalla. | — |
| `muy-fuerte` | Repite tiradas de FIS. | — |
| `cobarde` | 50% de activar tag `[pánico]` si recibe fuego sin cobertura. | `pánico` |
| `carismático` | +1 a chequeos MEN de aliados en el mismo hex mientras esté activo. | — |
| `terco` | Repite chequeos MEN al recibir orden de retirada. | — |
| `veloz` | +1 INICIATIVA en todos los turnos. | — |
| `veterano-cicatrizado` | Repite tiradas con tag `cansado` o `exhausto`. | — |
| `devoto` | +1 a chequeos morales si el líder de escuadra sigue vivo. | — |
| `impredecible` | Primera tirada de cada batalla es aleatoriamente favorable o desfavorable (50/50). | — |

El campo `efecto` es **string libre** (consistente con `perk.efecto_mecanico`). Si el motor downstream necesita estructurarlo (trigger / probabilidad / efecto / tag activado) en parsing rígido, se introduce en una ola futura. Valores fuera del pool semilla son válidos pero requieren entry curada manualmente — el generador no los emite.

### `GET /meta/rasgos`

Vocabulario sugerido de rasgos físicos (`categoria: rasgo`). Entries: `{ valor, tipo: "altura"|"complexion"|"rasgo_fisico"|"cicatriz", facciones_comunes: [] }`. Facilita coherencia entre generador y herramientas externas sin forzar enums cerrados.

### `GET /meta/tag_categories`

Las seis categorías canon de v0.2.5 con descripción y política de uso. Respuesta tipo:
```json
[
  { "categoria": "rasgo",            "descripcion": "Atributos visuales del cuerpo. Altura, complexión, rasgos físicos, cicatrices." },
  { "categoria": "rol",              "descripcion": "Etiquetas mecánicas del rol vigente. lider, heroe, tirador, etc." },
  { "categoria": "skill",            "descripcion": "Habilidades aprendidas o entrenadas." },
  { "categoria": "trait",            "descripcion": "Rasgos de carácter o condición, sin polaridad fija." },
  { "categoria": "perk",             "descripcion": "Ventajas mecánicas activables del reglamento canónico del juego." },
  { "categoria": "aspecto",          "descripcion": "Mini-tag identitario con efecto mecánico embebido en mini-frase. Pool semilla en /meta/aspectos." },
  { "categoria": "equipo.arma",      "descripcion": "Arma de fuego. Catálogo de 6 genéricos: pistola, revolver, rifle, rifle militar, SMG, ametralladora." },
  { "categoria": "equipo.utilitario","descripcion": "Consumible o accesorio táctico (sin identidad de facción)." },
  { "categoria": "equipo.vestidura",  "descripcion": "Identidad visual de facción. Catálogo: uniforme confederado, uniforme rojo, ropa de civil, camuflaje básico." }
]
```
Abierto — futuras categorías se agregan sin breaking change.

### `GET /meta/equipo/vestiduras`

Devuelve el catálogo canon de vestiduras. Ej: `GET /meta/equipo/vestiduras` → `[{ valor: "uniforme confederado", faccion: "Confederación" }, { valor: "uniforme rojo", faccion: "Ejército Rojo" }, { valor: "ropa de civil" }, { valor: "camuflaje básico" }]`.

### `GET /meta/equipo/armas`, `GET /meta/equipo/utilitarios`

Catálogos sugeridos de armas y utilitarios con alcance y facción predominante. Sin validación — el generador los usa como pool; el cliente puede listarlos para UIs.

### `GET /meta/hito_types`, `GET /meta/vinculo_types`

Catálogos sugeridos. Todos abiertos. `hito_types` incluye el efecto sobre campos vigentes para cada tipo canon (ver tabla 9.5).

### `GET /meta/escuadras/{id}` (potencial, sujeto a necesidad)

Si se introduce un endpoint de escuadras, devolvería `id`, `nombre`, `cuerpo`, `faccion`, y la composición vigente por query inverso a `escuadra_id`. Queda fuera de v1 estricto.

Mapea (todos los `/meta/*`): UC-09.

### 10.1. Catálogo canon `/meta/*` — 80 tags semilla (v0.4.0)

Cada endpoint `/meta/*` devuelve esta **semilla canónica** más cualquier valor agregado por los mocks o personajes canonizados existentes. El catálogo es semilla, **no autoridad**: otros usuarios crearán tags personalizados que entran al catálogo emergente. La fragmentación semántica que esto introduce está documentada como tensión en 13.9.

**`/meta/rasgos` — 10 rasgos físicos canon:**
```
alto, medio, bajo, delgado, atletico, corpulento,
piel curtida, manos grandes, barba canosa, cicatriz facial
```

**`/meta/roles` — 10 roles canon (etiquetas mecánicas + funcionales de campo):**
```
lider, sargento, cabo, camarada, apuntador, artillero,
infanteria, recargador, comisariado, veterano
```

**`/meta/skills` — 10 skills canon:**
```
Comandancia, Tiro de precisión, Manejo de ametralladora, Operación de radio,
Primeros auxilios, Lectura de mapas, Lectura de terreno,
Conocimiento de meseta, Oratoria, Comisariado
```

**`/meta/traits` — 10 traits canon (sin polaridad fija):**
```
Objetivo prioritario, Voz grave, Mirada larga, Obstinado,
Pánico en abierto, Hemorragia lenta, Recluta novato, Templado bajo fuego,
Lealtad obrera, Fatigado crónico
```

**`/meta/perks` — 10 perks canon del reglamento:**
```
Voz de mando, Puntería fría, Cobertura instintiva, Resistencia al dolor,
Veterano de flanqueo, Sangre fría, Recarga rápida, Olfato del terreno,
Tenaz, Disparo de oportunidad
```

**`/meta/equipo/armas` — 6 armas canon (genéricos):**
```
pistola, revolver, rifle, rifle militar, SMG, ametralladora
```

**`/meta/equipo/utilitarios` — 10 utilitarios canon:**
```
cargador, silbato, cuaderno, brújula, prismáticos,
botiquín, radio, mapa, cuchillo, vendaje
```

**`/meta/equipo/vestiduras` — 4 vestiduras (cerrado por decisión del cliente en v0.2.6):**
```
ropa de civil, uniforme rojo, uniforme confederado, camuflaje básico
```

**`/meta/aspectos` — 10 aspectos canon (nuevo en v0.4.0):**
```
cabrón, ojo-de-halcón, muy-fuerte, cobarde, carismático,
terco, veloz, veterano-cicatrizado, devoto, impredecible
```

**Total: 80 tags semilla** (6 armas + 10 utilitarios + 10 rasgos + 10 roles + 10 skills + 10 traits + 10 perks + 4 vestiduras + 10 aspectos). La categoría `aspecto` se promueve a ciudadana canon en v0.4.0 (ver sección 16).

---

## 11. Los 22 mock — alcance del MVP

Los 22 personajes iniciales son fixtures en `mock/personajes/{faccion}/{nn}_{rango}_{apellido}.yaml`.

**Estado de migración.** Los 22 fixtures fueron regenerados al schema v0.2.5/v0.2.6 y normalizados en v0.3.0 (eliminación residual de `armor` — no existía en la regeneración; reemplazo del único `Springfield 1903` por `Mauser 1909` en el mock del Tirador Antinao). Cada mock tiene exactamente 1 tag `equipo.vestidura` del catálogo de 4 valores cerrado. Tags emergentes (oficios, customs narrativos) coexisten con el catálogo canon de 70 tags semilla descripto en 10.1 — el catálogo es semilla, no purga.

### 11.1. Escuadra Confederación (11)

| # | `id` | Rango operativo | Nombre canon |
|---|---|---|---|
| 01 | `mock.confederacion.01.aguirre` | `Lider de escuadra` | Sargento Walter Aguirre |
| 02 | `mock.confederacion.02.sosa` | `Segundo al mando` | Cabo Primero Sosa |
| 03 | `mock.confederacion.03.quiroga` | `Apuntador` | Apuntador Quiroga |
| 04 | `mock.confederacion.04.funes` | `Artillero` | Artillero Funes |
| 05 | `mock.confederacion.05.rodriguez` | `Fusilero` | Soldado de Primera Marcela Rodríguez |
| 06 | `mock.confederacion.06.olivares` | `Fusilero` | Soldado de Primera Olivares |
| 07 | `mock.confederacion.07.acosta` | `Fusilero` | Soldado de Primera Acosta |
| 08 | `mock.confederacion.08.pereyra` | `Fusilero` | Soldado de Primera Pereyra |
| 09 | `mock.confederacion.09.mendez` | `Recluta` | Recluta Méndez |
| 10 | `mock.confederacion.10.lugones` | `Recluta` | Recluta Lugones |
| 11 | `mock.confederacion.11.ramirez` | `Recluta` | Recluta Ramírez |

### 11.2. Escuadra Ejército Rojo (11)

| # | `id` | Rango operativo | Nombre canon |
|---|---|---|---|
| 12 | `mock.ejercito_rojo.01.mansilla` | `Lider de escuadra` | Camarada Puntero Ramón Mansilla |
| 13 | `mock.ejercito_rojo.02.iturra` | `Segundo al mando` | Segundo Camarada Iturra |
| 14 | `mock.ejercito_rojo.03.antinao` | `Apuntador` | Tirador Antinao |
| 15 | `mock.ejercito_rojo.04.calfucura` | `Artillero` | Ametrallador Calfucurá |
| 16 | `mock.ejercito_rojo.05.carcamo` | `Fusilero` | Miliciano Veterano Fermín Cárcamo |
| 17 | `mock.ejercito_rojo.06.paine` | `Fusilero` | Miliciano Veterano Paine |
| 18 | `mock.ejercito_rojo.07.soriano` | `Fusilero` | Miliciano Veterano Soriano |
| 19 | `mock.ejercito_rojo.08.belenchini` | `Fusilero` | Miliciano Veterano Belenchini |
| 20 | `mock.ejercito_rojo.09.bordon` | `Recluta` | Voluntario Bordón |
| 21 | `mock.ejercito_rojo.10.maturana` | `Recluta` | Voluntario Maturana |
| 22 | `mock.ejercito_rojo.11.bordagaray` | `Recluta` | Voluntario Bordagaray |

**Composición:** escuadra de 11 = 1 + 1 + 1 + 1 + 4 + 3.

**Mutabilidad.** Los mocks son **inmutables** desde la API. `POST /character/{id}/event` sobre un mock devuelve 409. Su evolución, si la hay, ocurre por reescritura manual del fixture.

---

## 12. Alcance MVP vs futuro

### Dentro de v1

- 2 facciones jugables: Confederación y Ejército Rojo.
- 6 rangos operativos canon con su matriz determinística.
- Pools canon de `skill`, `trait`, `perk` (este último con metadato `rangos_naturales`).
- Tablas curadas de nombres, edades, géneros, equipo por facción.
- Generación efímera con seed reproducible.
- 22 mocks regenerados al schema v0.2.5 en iteración separada.
- Canonización persistente (solo DB de la API).
- **Memoria viva**: endpoint de evento, mutación de campos vigentes, historial inline.
- **Sistema de tags como ciudadanos de primera clase**: rasgo, rol, skill, trait, perk, aspecto, equipo.{arma,utilitario,vestidura}.
- **Campos derivados**: `filiacion`, `fza_aportada` — computados al servir.
- **`mando` como booleano**: capacidad de mando; titularidad derivada.
- **`estado` como dimensión de asignación**: activo/disponible/kia/licencia.
- **Lealtades estructuradas** con secretos.
- **Customs libres** (valores fuera del canon en cualquier categoría de tag).
- **Extras** libres al top level.
- **Enums abiertos** con catálogos `/meta/*`.
- Restricción 80/20 soft de perks por rango.
- Poda de respuesta con `?fields=`.

### Explícitamente fuera de v1

- Las 3 facciones secundarias.
- PJs civiles.
- Perks de batalla y complicaciones temporales (son del motor de batalla).
- Sistema de hexágonos, mapa, escenarios.
- Runtime de batalla.
- Autenticación, autorización, rate limiting.
- UI propia.
- Generación de escuadras completas en una sola llamada.
- Edición arbitraria de canonizados (solo cambios vía evento).
- Edición de mocks vía API.
- Reverso de hitos.
- Versionado de la prosa congelada.
- Schema completo de la entidad `escuadra` (queda como entidad implícita en v0.2.5; se especifica cuando se necesite).
- Endpoint `/meta/escuadras` con composición vigente (potencial v1.1).
- Operación "diff entre estado original y estado vigente" automatizada.

---

## 13. Tensiones explícitas y compromisos asumidos

### 13.1. Customs libres + enums abiertos → motor downstream interpreta contenido libre

**Decisión.** El producto acepta tags `skill`/`trait`/`perk` con valores fuera del canon. Acepta `tipo` de hito y de vínculo con valores custom. Acepta `extras` no validado.

**Costo.** El motor downstream tiene que interpretar el efecto de un `perk` custom o un `trait` custom.

**Por qué se acepta.** La alternativa paralizaría la creación de personajes notables.

**Mitigación.** Los catálogos `/meta/*` siempre devuelven la versión oficial como fallback de comparación.

### 13.2. Tags con categorías abiertas → riesgo de fragmentación semántica

**Decisión.** Las categorías de tags son un enum abierto. Las sub-categorías jerárquicas con punto (`equipo.arma`, `equipo.utilitario`, `equipo.vestidura`) también son extensibles.

**Costo.** Distintos clientes pueden inventar sinónimos (`equipo.weapon` vs `equipo.arma`).

**Por qué se acepta.** Consistente con la política de enums abiertos.

**Mitigación.** `/meta/tag_categories` documenta el canon. Los consumidores deben normalizar al leer.

### 13.3. Sin versionado del payload → riesgo de drift si SOLID falla

**Decisión.** No hay `version_canon`. Schema extensible sin romper.

**Costo.** Si un campo está mal diseñado, no hay herramienta de versionado para migrar.

**Por qué se acepta.** Versionar y migrar es caro. Apostamos a SOLID/open-close.

**Mitigación.** Bloques fuertemente segmentados; `extras`, enums abiertos, customs libres absorben extensión.

### 13.4. Sin validación de `ref_personaje_id` ni `escuadra_id` → referencias colgadas posibles

**Decisión.** Ni `vinculos[].ref_personaje_id` ni `escuadra_id` se verifican.

**Costo.** Posibles referencias rotas.

**Por qué se acepta.** Validar implica orden de creación, ciclos, integridad referencial — costo desproporcionado para MVP.

**Mitigación.** `descripcion` del vínculo es obligatorio. Para escuadras, `filiacion` se compone con fallback ("Sargento del Ejército de la Confederación Argentina" si la escuadra no resuelve).

### 13.5. Memoria viva rompe reproducibilidad post-canonización

**Decisión.** Un canonizado, tras su primer hito, deja de ser regenerable desde su `semilla`.

**Costo.** Tests que dependen de regenerar el mismo personaje deben usar efímeros.

**Por qué se acepta.** Es el diferencial del producto.

**Mitigación.** `semilla` y `tags_iniciales` se preservan.

### 13.6. Traits sin polaridad explícita → el motor downstream interpreta

**Decisión.** Los tags `trait` no tienen polaridad fija. La categoría agrupa positivos (`Sangre fría`), neutros (`Voz grave`) y penalidades (`Obstinado`, `Miope`, `Objetivo prioritario`).

**Costo.** Un cliente que necesite filtrar "solo penalidades" tiene que consultar `/meta/traits/{valor}.polaridad` (si existe) o tratar a todos los traits como neutros y aplicar reglas downstream.

**Por qué se acepta.** No obliga a categorizar moralmente cada trait. Muchas ambigüedades del lore son reales (¿`Voz grave` es positiva o penalidad? depende de la escena). Forzar polaridad al schema empobrecería esa ambigüedad.

**Mitigación.** El catálogo `/meta/traits` puede declarar `polaridad: positivo | neutro | penalidad` como hint sugerido pero no autoritativo. Los traits custom no la tendrán.

### 13.7. Sinónimos y aliases de tags → fragmentación semántica silenciosa

**Decisión.** El sistema no tiene mecanismo de alias ni normalización de tags en v1. `Francotirador` y `francotirador` son valores distintos. `equipo.arma` y `equipo.weapon` son categorías distintas.

**Costo.** Una query por `skill: Francotirador` no encontrará a un personaje cargado con `skill: francotirador` (minúscula). Distintos generadores pueden usar `Oratoria de muelle` y `Oratoria sindical` para el mismo concepto.

**Por qué se acepta.** Implementar alias en v1 requiere un grafo de equivalencia, gobernanza del catálogo y resolución en writes — costo alto para un MVP donde el generador es la única fuente.

**Mitigación.** El generador es determinístico y usa el vocab del catálogo `/meta/*`. El problema surge cuando humanos o motores externos escriben tags manualmente. Documentar claramente en `/meta/tag_categories` los valores canónicos. Normalización de case (lowercase en `valor`) es una solución mínima viable que debería resolverse antes de v1.

### 13.9. Catálogo `/meta/*` como semilla, no como autoridad

**Decisión.** El catálogo canon de 70 tags semilla (sección 10.1) es vocabulario sugerido, no enum cerrado. La excepción es `equipo.vestidura`, cerrado en 4 valores por decisión del cliente en v0.2.6.

**Costo.** Convive con la fragmentación documentada en 13.2 y 13.7: distintos usuarios pueden crear sinónimos del mismo concepto (`Tiro de precisión` canon vs `Francotirador` custom), y el catálogo emergente termina mezclando registros canónicos con customs no normalizados.

**Por qué se acepta.** El usuario explicitó: "completamos lo estándar, los casos más normales solamente; otros usuarios crearán tags personalizados". Forzar enum cerrado en `skill`/`trait`/`perk`/`equipo.{arma,utilitario}` paralizaría la creatividad narrativa, que es exactamente el diferencial del producto.

**Mitigación.** El catálogo semilla cubre los casos comunes del MVP — un cliente sano resuelve >80% de los personajes contra la semilla. Los `/meta/*` pueden marcar entradas con `origen: "canon" | "emergente"` para que el cliente discrimine. La normalización de case (OQ #11) y el mecanismo de alias (OQ #10) atacan el síntoma cuando lleguen a v1.

### 13.8. Denormalización opt-in de efectos de tags → dos fuentes de verdad potenciales

**Decisión.** Los efectos mecánicos de skills, traits y perks viven en `/meta/*`, no inlineados en cada tag de cada personaje.

**Costo.** Si un cliente necesita los efectos para procesar un personaje, tiene que hacer N calls adicionales a `/meta/*` o cachear el catálogo localmente. Un personaje con 12 tags puede requerir hasta 12 lookups adicionales.

**Por qué se acepta.** Inlinear el efecto en el tag del personaje es una trampa de denormalización: si el catálogo cambia (un perk recibe errata), habría que actualizar todos los personajes con ese perk.

**Mitigación.** La API puede soportar un query param `?expand=tags` que en una sola call devuelva la ficha del personaje con cada tag resuelto contra su entrada en `/meta/*`. Fuera de v1 estricto.

### 13.11. Tags mínimos vs riqueza contextual (v0.4.1)

**Decisión.** En v0.4.1 los tags se normalizan a forma mínima: 1-2 palabras, 3 cuando el nombre canónico lo exige. Cero prosa, cero paréntesis, cero comas internas, cero guiones largos. El tag es **identificador**, no descripción.

**Costo.** Se pierde info contextual enriquecida que vivía dentro del propio tag — "brújula de oficial — regalo del instructor de Stroeder" colapsa a `brújula`; "cuaderno de campaña — anotaciones de terreno, firma con la inicial R en el margen" colapsa a `cuaderno`. Parte de ese color narrativo ya estaba duplicado en la prosa de `historia` (y ahí queda); parte se pierde irreversiblemente. La pérdida es aceptada como costo del minimalismo.

**Por qué se acepta.** Tags-como-ID habilitan inverted index trivial (14.2), comparación entre personajes, agregación en `/meta/*`, y semántica predecible para el motor downstream. Tags-como-prosa-disfrazada rompen esas tres cosas. La info contextual canónica vive en el catálogo `/meta/*`; el color narrativo vive en `historia`; la info estructurada por instancia, si llega a hacer falta, va a la futura entidad `notas` (OQ #16).

**Mitigación.** La pasada de v0.4.1 preservó literal la prosa de `historia` e `historial[]` en los 22 mocks — toda la info contextual irrecuperable que estuviera reflejada ahí sigue viva. Una ola futura puede introducir `notas: array<{tag_ref, texto}>` si el caso de uso aparece (ver OQ #16).

---

### 13.10. Efecto del aspecto en texto libre → motor downstream interpreta mini-frase

**Decisión.** El campo `efecto` de cada entrada de `/meta/aspectos/{valor}` es **string libre** en castellano (consistente con `perk.efecto_mecanico`). No se estructura en parsing rígido (trigger / probabilidad / efecto / tag activado) en v0.4.0.

**Costo.** El motor de batalla necesita interpretar la mini-frase para aplicarla — probablemente vía LLM resolver o regla heurística (`split` por "si", "%", "+", "repite", "activa tag"). Aspectos custom escritos por humanos cargan más riesgo de parsing fallido que los 10 canon.

**Por qué se acepta.** Mismo compromiso de 13.1 (customs libres) y 13.8 (denormalización opt-in): forzar estructura rígida ahora paralizaría la curaduría de aspectos custom. El catálogo canon de 10 aspectos tiene mini-frases **bien formadas y predecibles** (patrón verbo + porcentaje + condición). Los customs cargan el riesgo.

**Mitigación.** El catálogo `/meta/aspectos` puede declarar `activa_tag` como campo opcional estructurado cuando el efecto dispara un tag transitorio (`berserker`, `pánico`). Esto absorbe el caso más común sin estructurar todo el efecto. Si la fricción crece, una ola futura puede introducir `efecto_estructurado: { trigger, probabilidad, efecto, activa_tag }` como hint opcional junto al texto libre.

---

## 14. Píldoras de arquitectura

### 14.1. Tags y stores no-transaccionales

El patrón de entidades pequeñas, repetibles, agrupables y sin esquema rígido (tags) es el caso textbook para un store no-transaccional o document-oriented. Cloudflare D1 con columna JSON o Workers KV con prefijo por categoría son candidatos naturales.

### 14.2. Tags como ciudadanos de primera clase → inverted index natural

Con v0.2.5 los tags absorben rasgos, rol, skills, traits, perks y equipo subcategorizado — la mayor parte del contenido mutable del personaje. Esto refuerza la afinidad NoSQL/document-store ya señalada y añade una segunda observación: el query típico downstream es **"dame personajes con tag X"** o **"expandime los efectos mecánicos de estos tags"**. Es el patrón clásico de **inverted index sobre tags**, soportado nativamente por D1 con índices JSON o por Workers KV con clave compuesta `tag:{categoria}:{valor}` apuntando a lista de `personaje_id`.

Ejemplo concreto: la query "personajes con `skill: Francotirador` AND `rol: lider` AND facción `Confederación`" se resuelve con tres lookups en el inverted index (`skill:Francotirador`, `rol:lider`, filtro `faccion`) seguidos de intersección de sets de `personaje_id`. Más barato que un full scan sobre el campo JSON de cada ficha. Con los seis tipos de categoría canon y un corpus de ~100 canonizados, un inverted index en Workers KV cabe cómodamente en memoria.

Esta píldora no fija stack; solo registra que el diseño v0.2.5 hace que las optimizaciones de búsqueda sean baratas si la necesidad aparece — y los UCs 19, 20, 21 y 22 (filtros por tag) confirman que aparecerá.

### 14.3. Campos derivados → cómputo al servir, no al persistir

`filiacion` y `fza_aportada` son derivados que la API computa al armar la respuesta. El campo `armor` fue eliminado del sistema en v0.3.0: la vestidura es identidad visual y no aporta protección numérica; si más adelante se necesita defensa, vuelve como tag `trait: blindado` derivado de vestidura o skill defensiva.

---

## 15. Open questions v0.4.0

1. **Nombre final del campo derivado `filiacion`.** Alternativas en evaluación: `designacion`, `titulo`, `pie_de_firma`. El nombre `filiacion` se usa como provisorio en v0.2.5. Decidir antes de v1.0.

2. **Gobernanza de `POST /character/{id}/event`.** ¿Quién puede llamarlo? Sin auth en v1, cualquiera con la URL puede. Decidir si se atemporaliza con tokens, lista blanca, o se acepta porque el corpus es curable.

3. **Polaridad de `trait`.** ¿Existe `/meta/traits/{valor}.polaridad` como hint sugerido, o se deja al motor downstream interpretar libremente? Documentado en 13.6 pero el endpoint no está decidido.

4. **Schema completo de la entidad `escuadra`.** v0.2.5 introduce `escuadra_id` y la entidad implícita (`id`, `nombre`, `cuerpo`, `faccion`) pero no especifica un schema completo ni endpoints CRUD. Definir en v1.1 o cuando aparezca el primer consumidor que necesite gestionar escuadras.

5. **Mutabilidad fina de rasgos físicos.** Cicatrices mutan vía `agregar_tag`. ¿Pero altura o complexión pueden mutar tras una herida grave ("queda enjuto tras la convalecencia")? El PRD las marca modificables como cualquier tag, sin restricción explícita.

6. **Interpretación de customs por el motor.** ¿El motor de batalla interpreta `perk` custom con LLM al aplicar la regla, o un curador humano traduce el custom a regla mecánica antes? Tensión documentada (13.1), flujo operacional abierto.

7. **Versionado de categorías canon de tags.** Las categorías y sub-categorías (`rasgo`, `skill`, `equipo.arma`, etc.) se documentan en `/meta/tag_categories`. ¿Gobernanza del catálogo? ¿Se versiona junto al PRD?

8. **`POST /character/{id}/original`.** ¿Útil exponer un endpoint que regenere la ficha al estado de creación (sin historial) usando `semilla` + `tags_iniciales`, para que herramientas externas calculen el diff? Fuera de v1; útil para auditoría.

9. **Catálogo de tags canon por facción.** ¿El catálogo `/meta/skills` tiene entries segmentadas por facción (`facciones_predominantes: ["Ejército Rojo"]`)? ¿El generador rechaza o avisa cuando sortea un tag que el canon considera cruzado (ej. `skill: Comisariado` para un personaje Confederado)? ¿O se acepta con libertad?

10. **Política de eviction de tags obsoletos.** Si el catálogo `/meta/skills` retira un valor (ej. `Oratoria de muelle` renombrado a `Oratoria sindical`), los personajes que ya tienen ese tag no se actualizan. ¿Se acepta silenciosamente o se implementa un job de migración? ¿Existe un mecanismo de alias para que ambos valores resuelvan al mismo efecto?

11. **Normalización de case en `valor`.** ¿El schema normaliza `valor` de tags a lowercase antes de persistir? Evita fragmentación silenciosa (`Francotirador` ≠ `francotirador`). Tensión 13.7. Decisión mínima viable antes de v1.

12. **Límite de tags por categoría.** ¿Hay un máximo razonable de tags por categoría? Un personaje con 20 `equipo.utilitario` es sintácticamente válido pero semánticamente raro. ¿El generador tiene caps internos? ¿La API los valida o advierte?

13. **~~¿Cargadores por calibre deberían generizarse?~~** **Resuelto en v0.4.1**: todos los cargadores colapsan a `cargador` (sin calibre). El calibre se infiere del tag `equipo.arma` que el personaje porta; mantener el calibre en el tag del cargador era info duplicada y rompía el principio de tag mínimo (13.11).

14. **Polaridad explícita de aspectos.** ¿Los aspectos admiten un campo `polaridad: positivo | neutro | penalidad` (análogo al hint sugerido de traits en 13.6) o se tratan como neutros y el motor downstream interpreta? Algunos del pool semilla son ambiguos: `terco` repite chequeos MEN al recibir orden de retirada (¿es ventaja porque el personaje se mantiene firme, o penalidad porque desobedece?); `impredecible` es literalmente 50/50. Decidir si vale el campo o si el texto libre del `efecto` es suficiente.

15. **Versionado del pool semilla de aspectos.** ¿El catálogo canon de 10 aspectos en `/meta/aspectos` se versiona con bump explícito del schema cuando se agregan o retiran entries, o evoluciona libremente como semilla abierta (mismo trato que `/meta/skills` o `/meta/traits`)? Los aspectos cargan más peso mecánico que un skill o trait, lo cual sugiere gobernanza más estricta. Sin decidir.

16. **Entidad `notas` como capa enriquecida de tags (v0.4.1).** ¿Implementar `notas: array<{tag_ref, texto}>` para persistir contexto narrativo o mecánico atado a tags específicos sin contaminar el `valor` del tag? Caso típico: el `cuaderno` de Aguirre tenía "anotaciones de terreno, firma con la inicial R en el margen" — info que hoy o vive en la prosa de `historia` (si pertenece a la voz narrativa) o se pierde. Una entidad `notas` permitiría persistirla estructuradamente sin romper el principio del tag mínimo (13.11). Pendiente; se acepta pérdida actual.

17. **Umbrales de Fatiga.** ¿Hay niveles que disparen penalidades automáticas (ej. `fatiga_actual <= 3` → tag `estado_temporal: fatigado`; `fatiga_actual = 0` → tag `estado_temporal: exhausto`)? El PRD ya registra `Fatigado crónico` como trait canon y los aspectos `veterano-cicatrizado` y `devoto` hacen referencia a tags `cansado` / `exhausto` (§10.1 y pool de aspectos), lo cual sugiere que el patrón existe pero aún no está sistematizado. Candidato natural para una ola de `estado_temporal` una vez que el motor de batalla lo requiera.

18. **Umbrales de Moral.** ¿`moral_actual = 0` → `pánico` automático (análogo al aspecto `cobarde`)? ¿O se deja al criterio del narrador? El pool de aspectos ya usa `pánico` como tag activable (§10 `/meta/aspectos`), pero no hay regla canónica de umbral definida en el PRD.

19. **Recalibración de topes tras `triple_cero`.** Cuando un hito `triple_cero` incrementa `atributos.men`, ¿el narrador debe emitir además un hito `cambio_estado_vital` para actualizar `fatiga_max` y `moral_max`? ¿O la API los recalcula derivados al servir (igual que `fza_aportada`)? El PRD opta por persistir `fatiga_max` y `moral_max` para que el motor de batalla los lea sin recalcular — pero eso requiere un hito coordinado. Decisión pendiente de confirmación con el cliente.

20. **Tipo de hito canónico `cambio_estado_vital`.** El nombre sugerido en la tabla de hitos canon (§9.5) cubre mutaciones de `fatiga_actual`, `moral_actual`, `fatiga_max` y `moral_max`. Falta incorporarlo formalmente a la tabla §9.5 si el cliente lo aprueba.

---

## 16. Roadmap y naturaleza del entregable

### 16.1. Naturaleza agnóstica del PRD

Este documento describe el sistema de creación de personajes y sus reglas **sin comprometerse con un lenguaje de programación, framework, plataforma de despliegue ni stack concreto**. Las decisiones de implementación quedan diferidas.

Lo único canónico aquí es:

- **Schema de la hoja**: la forma completa del recurso `personaje` (§6) con todos sus campos, tipos y restricciones.
- **Reglas de atributos / tags / aspectos / estado_vital**: las invariantes de distribución por rango (§7), el sistema de tags categorizado (§6.2, §8, §10), la mecánica de aspectos (§10, §13.10), y el bloque `estado_vital` con sus derivados.
- **Generador de personajes**: el algoritmo determinístico y el pipeline de prosa que lo acompaña (§7, §7.2, §7.2.1, §7.9.5).
- **Suite de tests del generador**: las invariantes que todo generador conforme debe satisfacer (golden mocks, distribuciones esperadas, idempotencia por semilla).

Cualquier otro detalle — base de datos, lenguaje de programación, framework HTTP, runtime, infraestructura — es implementación y vive fuera de este PRD.

---

### 16.2. Hito 1 — Creación perfecta de personajes (**ACTIVO**)

Único hito al que apunta este PRD en su versión vigente. Cubre los cuatro entregables siguientes, todos agnósticos respecto del stack:

#### 16.2.1. Schema + reglas + validación

La hoja canónica (documentada en `docs/hoja-modelo.{yml,md}` y en §6–§10 de este PRD), las invariantes de atributos / tags / aspectos / estado_vital, y los validadores correspondientes. Entregable estático: no requiere servidor ni persistencia para ser validado.

#### 16.2.2. Generador procedural

Algoritmo (sin LLM) capaz de producir personajes nuevos respetando:

- Distribuciones de atributos por rango (§7.2 / §7.2.1).
- Pool de tags semilla por categoría (§8 y catálogos `/meta/*`).
- Pool de aspectos (§10).
- Semilla reproducible (`metadatos.semilla`): la misma `(semilla, faccion, rango)` produce siempre el mismo resultado.

#### 16.2.3. Generador vía LLM (prosa)

Pipeline que rellena el campo `historia` y enriquece descripciones narrativas a partir del personaje procedural. En los mocks actuales el campo `metadatos.modelo_prosa` vale `null`; este hito activa ese campo para los personajes generados. El LLM solo interviene en la prosa — la estructura y los atributos los produce el algoritmo procedural (§16.2.2).

#### 16.2.4. Suite de tests del generador

Tests agnósticos que validan el comportamiento del generador:

- **Golden mocks**: el generador reproduce los 22 personajes existentes fijando su semilla canónica.
- **Invariantes de schema**: todo personaje generado satisface las restricciones de §6 (tipos, campos obligatorios, rangos de atributos).
- **Distribuciones por rango**: los atributos generados caen dentro de las bandas de §7.2.1.
- **Idempotencia con semilla fija**: `generar(semilla, faccion, rango)` devuelve el mismo payload en llamadas sucesivas.

Esta suite es entregable del Hito 1, no del Hito 2.

---

### 16.3. Hito 2 — API en contenedor Docker (**BLOQUEADO**)

<!-- BLOQUEADO: no se avanza con este hito hasta autorización explícita del usuario kodex. -->

Convertir el sistema del Hito 1 en un servicio HTTP empaquetado en Docker. Endpoints mínimos:

- Obtener personaje existente por ID (mock o canonizado).
- Generar personaje nuevo con o sin semilla explícita.

Incluye **tests de contrato y de integración** del servicio HTTP. Lenguaje y framework sin definir todavía — la decisión queda para cuando se autorice el hito.

---

### 16.4. Hito 3 — Sistema de escuadras (**BLOQUEADO**)

<!-- BLOQUEADO: no se avanza con este hito hasta autorización explícita del usuario kodex. -->

Modelado y API del sistema de escuadras: composición de escuadra, `fza_aportada` agregada, lealtad de escuadra, dinámicas inter-escuadra. También empaquetado como API en Docker. Mismo criterio de bloqueo que el Hito 2.

---

### 16.5. Excluido del alcance actual

Mientras los Hitos 2 y 3 permanezcan bloqueados, los siguientes elementos están **fuera del PRD vigente**:

- La API HTTP y sus endpoints.
- El contenedor Docker y cualquier decisión de infraestructura.
- El sistema de escuadras (schema completo, CRUD, dinámicas de grupo).
- Persistencia en base de datos.
- Autenticación y autorización de llamadas.
- Cualquier interfaz de usuario (UI, CLI de usuario final, dashboards).

Estos temas pueden documentarse en PRDs separados cuando sus hitos sean autorizados.

---

## 17. Aspectos como ciudadanos canon — capa narrativa-mecánica (v0.4.0)

### 17.1. Implementación efectiva

En v0.4.0 la categoría **`aspecto`** se promueve de reserva a ciudadana canon del sistema de tags. La forma final de la primera ola es distinta de la previsión original (ver 17.3): se opta por **mini-tags identitarios cortos en kebab-case** (`cabrón`, `ojo-de-halcón`, `muy-fuerte`) con efecto mecánico embebido en una mini-frase corta servida por `/meta/aspectos/{valor}`, en lugar de la frase larga de 10–25 palabras que se había anticipado.

Referencias cruzadas al resto del PRD:

- **Schema**: 6.1 — categoría `aspecto` listada entre las canon previstas.
- **Hoja ASCII**: 6.0 — Miguel lleva bloque ASPECTOS con `[cabrón]`.
- **Distinción trait/perk/aspecto**: 6.2 — los tres se separan explícitamente.
- **Tags activables (`estado_temporal`)**: 6.2 — patrón implícito reconocido (no canon).
- **Ejemplos**: 6.3 (Aguirre con `ojo-de-halcón`) y 6.4 (Mansilla con `carismático`).
- **Generación**: 7.9.5 — política de raridad (70/25/5) y customs no auto-generables.
- **Mutación**: 9.5 — hitos `agregar_aspecto` y `quitar_aspecto`.
- **Endpoint**: 10 — `GET /meta/aspectos` con pool semilla de 10 entries.
- **Catálogo**: 10.1 — los 10 aspectos canon en la lista de tags semilla; total sube a 80.
- **Tensión**: 13.10 — efecto en texto libre, motor downstream interpreta.

### 17.2. Diferencia entre `aspecto`, `trait` y `perk`

La primera ola de aspectos abre una capa intermedia entre los rasgos de carácter sin mecánica (`trait`) y las ventajas activables canónicas del reglamento (`perk`). El aspecto **embebe su mecánica** en una mini-frase, no la delega al reglamento; y es **abierto al custom**, no fijo. Esa combinación lo vuelve la pieza ideal para capturar identidad mecánicamente activa sin saturar el catálogo cerrado de perks. Ver 6.2 para la tabla completa de la distinción.

### 17.3. Contexto histórico — la previsión original de aspectos como frases largas

La nota arquitectónica de v0.3.0 anticipaba aspectos como **frases narrativas largas** (10–25 palabras) al estilo de H.I.T.O.S. y Cultos Innombrables, donde el personaje "dice algo de sí mismo" en oración completa. Ejemplos previstos en aquel momento:

- `"Cuando la columna se quiebra, alguien tiene que mantener la voz."` (aspecto de líder)
- `"Aprendí a cazar antes que a leer; el monte no perdona el apuro."` (aspecto de tirador rural)
- `"No le debo nada a la Confederación, pero le debo todo a los muchachos de mi escuadra."` (aspecto de lealtad fracturada)

La primera ola de v0.4.0 prefirió el formato corto porque encaja mejor con el resto del sistema de tags (kebab-case, query-friendly, inverted-index-friendly) y porque el efecto mecánico embebido en mini-frase ya cubre la función operacional del aspecto sin necesidad de la frase larga.

### 17.4. Próxima ola especulativa — aspectos largos como segunda capa

Queda apuntada (sin implementación ni reserva de categoría) una posible **segunda capa** de aspectos largos al estilo H.I.T.O.S./Cultos clásico, que viviría junto a la capa corta sin desplazarla. Podría modelarse como `categoria: aspecto_largo` o como un subcampo de cada `aspecto` corto. Decisión deferida hasta que aparezca un caso de uso narrativo que la justifique. Si llega, su consumo natural sería el motor narrativo (no el de batalla), invocando la frase como modificador situacional discrecional.

---

*Fuentes canónicas referenciadas (no copiadas):*

- `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md` — esquema y matriz de stats por rango.
- `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md` — pools de perks y complicaciones (estos últimos migrados como traits con polaridad negativa en v0.2.5).
- `/Dev/syv-battle-game-system/lore/universo.md` — descriptores de facción usados como contexto del LLM.
- `/Dev/syv-battle-game-system/personajes/` — 22 fichas canon base que alimentan los mocks (regenerados al schema v0.2.6 y normalizados en v0.3.0).
- `https://github.com/kodexArg/syv-game-system/blob/main/arquitectura/esquemas/personaje.schema.json` — schema público de referencia.
