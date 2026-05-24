# PRD — syv-character-kit

> **Documento vivo.** Define el contrato de producto de la API generadora de personajes del universo *Subordinación y Valor* (SyV). No contiene decisiones de arquitectura, almacenamiento ni stack — solo el QUÉ.
>
> **Versión**: 0.2.5
> **Reemplaza**: 0.2.2 (consolidación de los deltas v0.2.3 + v0.2.4 + v0.2.5; se saltean los releases intermedios)
> **Idioma**: castellano rioplatense, voseo sobrio.
> **Convención de identificadores en payloads JSON/YAML**: `snake_case_castellano` (consistente con `faccion`, `atributos`, `estado_salud` ya usados en `/Dev/syv-battle-game-system/`).

---

## 0. Changelog

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
- **Tags como modelo de primera clase.** La regla es: *"lo que puede ser tag, es tag."* Rasgos físicos, habilidades aprendidas, ventajas mecánicas, condiciones de carácter, inventario de equipo — todo eso es un tag categorizado. Lo que NO es tag: identidad (`nombre`, `sobrenombre`, `edad`, `genero`), pertenencia (`faccion`), posicionamiento operativo (`rol`, `rango`, `estado`, `escuadra_id`, `mando`, `estado_salud`), `atributos`, `lealtades`, `vinculos`, `historial`, `historia`, `metadatos`. La frontera es deliberada: el campo estructurado se usa cuando el motor necesita acceso semántico directo sin parsear una lista (ej. `rango` para decidir mando, `estado` para filtrar disponibilidad). Todo lo demás convive en `tags[]` con categorías abiertas. Esto permite extender el modelo de personaje sin agregar campos, sin migraciones, sin breaking changes. Las seis categorías canon actuales son: `rasgo`, `rol`, `skill`, `trait`, `perk`, y la familia jerárquica `equipo.{arma,utilitario,armadura}`.

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

## 6. JSON canónico del personaje (v0.2.5)

Sección central del PRD. Define la forma del recurso `personaje` que la API devuelve.

El schema es **estricto** en estructura y **abierto** en valores: los campos están definidos, pero los enums admiten valores sugeridos sin rechazar otros, y existe un campo `extras` libre al top level.

### 6.0. Hoja ASCII de referencia — ejemplo aprobado por el cliente

La siguiente hoja es la **representación visual canónica** del payload del personaje, aprobada por el cliente como ejemplo de referencia. Es complementaria al JSON canónico de 6.1: el JSON es el **contrato de datos**, la hoja es la **convención de presentación**. Toda UI que renderice un personaje debería poder componer una vista equivalente.

```
+----------------------------------------------------------------------------+
| SyV CHARACTER SHEET                                          schema v0.2.5 |
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
|   ARMAS        [subfusil Halcon]  [pistola Browning capturada]             |
|   UTILITARIOS  [cargador 9m]  [cargador 9m]  [cargador 9m]                 |
|                [silbato de contramaestre]  [brazalete rojo del Pueblo]     |
|   ARMADURAS    [chaleco antifragmentos rustico]              armor: 1     |
+----------------------------------------------------------------------------+
| SKILLS                                                                     |
|   [Comandancia]  [Oratoria de muelle]  [Lectura de columna]                |
+----------------------------------------------------------------------------+
| TRAITS                                                                     |
|   [Sangre fria]  [Objetivo prioritario]                                    |
+----------------------------------------------------------------------------+
| PERKS                                                                     |
|   [Voz de mando]                                                           |
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
- `ARMOR: 1` en la línea de ARMADURAS es valor derivado de la suma de aportes de los tags `equipo.armadura`.
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
                                        #   perk                → ventajas mecánicas activables
                                        #   equipo.arma         → arma de fuego, cuerpo a cuerpo, etc.
                                        #   equipo.utilitario   → cargador, vendaje, brazalete, silbato, etc.
                                        #   equipo.armadura     → chalecos, cascos, etc. (aportan a `armor` derivado)
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
  #   armor           : integer 0..3   (suma de aportes de tags equipo.armadura, segun /meta/equipo/armaduras)
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
  | `rasgo` | Atributos visuales del cuerpo | `altura media`, `barba canosa`, `cicatriz vertical sobre ceja izquierda`, `quemadura en antebrazo derecho` |
  | `rol` | Etiquetas mecánicas del rol vigente | `lider`, `heroe`, `sargento` |
  | `skill` | Habilidades aprendidas o entrenadas | `Comandancia`, `Francotirador`, `Medicina`, `Oratoria de muelle`, `Lectura de columna`, `Ingeniería`, `Comisariado` |
  | `trait` | Rasgos de carácter o condición, sin polaridad fija | `Sangre fría`, `Miope`, `Objetivo prioritario`, `Hemorragia lenta`, `Voz grave`, `Obstinado` |
  | `perk` | Ventajas mecánicas activables | `Voz de mando`, `Recarga rápida`, `Cobertura instintiva`, `Sucesor de Ricardo` |
  | `equipo.arma` | Arma de fuego o cuerpo a cuerpo (incluye alcance en el valor) | `Fusil FAL (alcance media)`, `Pistola Browning (alcance corta)` |
  | `equipo.utilitario` | Consumible o accesorio sin capacidad de armor | `cargador 9mm`, `vendaje`, `brújula de oficial`, `silbato de contramaestre` |
  | `equipo.armadura` | Protección con aporte de `armor` declarado en `/meta/equipo/armaduras/{valor}` | `chaleco antifragmentos reglamentario` (armor: 1), `chaleco antifragmentos rústico` (armor: 1) |

  La categoría es string libre — los enums son abiertos — pero el canon de v0.2.5 son las seis listadas. Usar valores fuera del canon es válido; el riesgo semántico está documentado en tensiones 13.1 y 13.2.

  **Reglas de derivación que dependen de tags:**
  - `armor` (DERIVADO): suma de aportes de cada tag `equipo.armadura` consultando `/meta/equipo/armaduras/{valor}`. El campo no se persiste; la API lo computa al servir.
  - `fza_aportada` (DERIVADO): tag `{categoria: rol, valor: heroe}` → 3; `{categoria: rol, valor: lider}` → 2; sin ninguno → 1. El campo no se persiste; la API lo computa al servir.
  - `sobrenombre` en Ejército Rojo (DERIVADO): se construye desde el tag `skill` de mando más prominente: `Comandancia` → `"Comandante {nombre}"`; `Medicina` → `"Doctor {nombre}"`; `Ingeniería` → `"Ingeniero {nombre}"`; `Comisariado` → `"Camarada Puntero {nombre}"`; sin ninguno → `"Camarada {nombre}"`. Ver 7.3.
- **Decisión consciente — sub-categorías con punto**: el equipo se modela como `equipo.arma`, `equipo.utilitario`, `equipo.armadura` (jerárquico con punto) en lugar de un sub-campo aparte. Ventajas: filtrado por prefijo `equipo.*`, legibilidad visual, sin nuevos sub-campos en el schema. Este patrón puede aplicarse a futuro a otras categorías que necesiten subdivisión.
- **`fza_aportada`** (DERIVADO, no persistido): tag `categoria: rol, valor: heroe` → 3; `categoria: rol, valor: lider` → 2; sin ninguno → 1. El motor lo computa al servir.
- **`armor`** (DERIVADO, no persistido): suma de aportes de cada tag `equipo.armadura` consultando `/meta/equipo/armaduras/{valor}`. El motor lo computa al servir.
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
    - { categoria: rasgo, valor: "pelo castaño corto" }
    - { categoria: rasgo, valor: "barba de tres días" }
    - { categoria: rasgo, valor: "mirada que se demora en las cosas" }
    - { categoria: rasgo, valor: "cicatriz vertical sobre ceja izquierda (Sector 12,15)" }
    # rol (mecánico)
    - { categoria: rol, valor: "lider" }
    # skills (antes: especialidad + saberes implícitos)
    - { categoria: skill, valor: "Comandancia" }
    - { categoria: skill, valor: "Lectura de terreno boscoso" }
    # traits (sin polaridad; ex-complicación migra acá como Eco del peñasco)
    - { categoria: trait, valor: "Mirada larga" }
    - { categoria: trait, valor: "Eco del peñasco" }   # penalidad: tras caída aliada, MEN desfavorable la ronda siguiente
    # perks (ex-perk_fijo migra acá como Sucesor de Ricardo)
    - { categoria: perk, valor: "Sucesor de Ricardo" }  # sin líder funcional, MEN favorable para mando/iniciativa
    # equipo.arma
    - { categoria: "equipo.arma", valor: "Fusil FAL (alcance media)" }
    - { categoria: "equipo.arma", valor: "Pistola reglamentaria M9 (alcance corta)" }
    # equipo.utilitario
    - { categoria: "equipo.utilitario", valor: "prismáticos militares — trofeo del Sector 12,15, lente derecha rajada pero usable" }
    - { categoria: "equipo.utilitario", valor: "cuaderno de campaña — anotaciones de terreno, marcas de Ricardo en las primeras hojas" }
    # equipo.armadura (aporta a armor derivado)
    - { categoria: "equipo.armadura", valor: "chaleco antifragmentos reglamentario" }

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
        valor: "prismáticos militares — trofeo del Sector 12,15, lente derecha rajada pero usable"
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
    - { categoria: rasgo, valor: "pelo castaño corto" }
    - { categoria: rasgo, valor: "barba de tres días" }
    - { categoria: rasgo, valor: "mirada que se demora en las cosas" }
    - { categoria: rol, valor: "lider" }
    - { categoria: skill, valor: "Comandancia" }
    - { categoria: skill, valor: "Lectura de terreno boscoso" }
    - { categoria: trait, valor: "Mirada larga" }
    - { categoria: trait, valor: "Eco del peñasco" }
    - { categoria: perk, valor: "Sucesor de Ricardo" }
    - { categoria: "equipo.arma", valor: "Fusil FAL (alcance media)" }
    - { categoria: "equipo.arma", valor: "Pistola reglamentaria M9 (alcance corta)" }
    - { categoria: "equipo.utilitario", valor: "cuaderno de campaña — anotaciones de terreno, marcas de Ricardo en las primeras hojas" }
    - { categoria: "equipo.armadura", valor: "chaleco antifragmentos reglamentario" }

  metadatos:
    creado_en: "2026-01-15T00:00:00Z"
    canonizado_en: "2026-01-15T00:00:00Z"
    ultima_actualizacion: "2026-05-10T22:45:00Z"
    modelo_prosa: null
    es_canon: true

  # Derivados servidos por la API (no persistidos):
  #   filiacion: ya en cabecera
  #   fza_aportada: 2   (tag rol=lider)
  #   armor: 1          (chaleco antifragmentos reglamentario aporta 1)

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
    - { categoria: rasgo, valor: "pelo entrecano corto" }
    - { categoria: rasgo, valor: "lentes de armazón fino reforzado con alambre" }
    - { categoria: rasgo, valor: "habla pausada, voz grave" }
    # rol (mecánico)
    - { categoria: rol, valor: "lider" }
    # skills (ex-especialidad: "comisariado" + saberes operativos)
    - { categoria: skill, valor: "Comisariado" }
    - { categoria: skill, valor: "Oratoria sindical" }
    - { categoria: skill, valor: "Lectura de mapas" }
    # traits (ex-complicación c06_obstinado migra acá)
    - { categoria: trait, valor: "Voz grave" }
    - { categoria: trait, valor: "Obstinado" }   # penalidad: si la orden implica retroceder, MEN desfavorable
    # perks (ex-perk_fijo p03_voz_de_mando)
    - { categoria: perk, valor: "Voz de mando" }
    # equipo.arma
    - { categoria: "equipo.arma", valor: "Subfusil Halcón (alcance corta)" }
    - { categoria: "equipo.arma", valor: "Pistola Browning (alcance corta)" }
    # equipo.utilitario
    - { categoria: "equipo.utilitario", valor: "cuaderno de notas — anotaciones de campaña y borradores de comunicados" }
    - { categoria: "equipo.utilitario", valor: "brújula de oficial — regalo del instructor de Stroeder" }
    # equipo.armadura
    - { categoria: "equipo.armadura", valor: "chaleco antifragmentos rústico" }

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
    - { categoria: rasgo, valor: "pelo entrecano corto" }
    - { categoria: rasgo, valor: "lentes de armazón fino reforzado con alambre" }
    - { categoria: rasgo, valor: "habla pausada, voz grave" }
    - { categoria: rol, valor: "lider" }
    - { categoria: skill, valor: "Comisariado" }
    - { categoria: skill, valor: "Oratoria sindical" }
    - { categoria: skill, valor: "Lectura de mapas" }
    - { categoria: trait, valor: "Voz grave" }
    - { categoria: trait, valor: "Obstinado" }
    - { categoria: perk, valor: "Voz de mando" }
    - { categoria: "equipo.arma", valor: "Subfusil Halcón (alcance corta)" }
    - { categoria: "equipo.arma", valor: "Pistola Browning (alcance corta)" }
    - { categoria: "equipo.utilitario", valor: "cuaderno de notas — anotaciones de campaña y borradores de comunicados" }
    - { categoria: "equipo.utilitario", valor: "brújula de oficial — regalo del instructor de Stroeder" }
    - { categoria: "equipo.armadura", valor: "chaleco antifragmentos rústico" }

  metadatos:
    creado_en: "2026-01-15T00:00:00Z"
    canonizado_en: "2026-01-15T00:00:00Z"
    ultima_actualizacion: "2026-05-03T11:15:00Z"
    modelo_prosa: null
    es_canon: true

  # Derivados servidos por la API (no persistidos):
  #   filiacion: ya en cabecera
  #   fza_aportada: 2   (tag rol=lider)
  #   armor: 1          (chaleco antifragmentos rústico aporta 1; techo Ejército Rojo: 1)

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
9. Inicializar `tags` con pools sorteados de `rasgo`, `rol`, `skill`, `trait`, `perk`, `equipo.arma`, `equipo.utilitario`, `equipo.armadura` — cada categoría tiene sus propias reglas de sorteo detalladas en 7.4–7.8.
10. Inicializar bloques vacíos (`lealtades.secretos: []`, `vinculos: []`, `historial: []`).
11. Generar `historia` con LLM, anclada en facción + rango + rol + skills/traits/perks + lugar implícito.
12. Copiar `tags` a `tags_iniciales` (snapshot inmutable).
13. La API compone `filiacion`, `fza_aportada` y `armor` derivados al servir.

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

### 7.10. `lealtades`

- **En generados**: `primaria` = nombre de la facción; `secundarias` = 0-2 entradas sorteadas; `secretos: []`.
- **En mocks y canonizados**: ricas, escritas o agregadas vía hito.

### 7.11. Tags de `equipo.*`

Pool curado `rango × faccion` produce tags en lugar de objetos estructurados.

| `rango` | Confederación (default) | Ejército Rojo (default) |
|---|---|---|
| `Lider de escuadra` | Fusil FAL (media) + Pistola reglamentaria (corta) | Subfusil Halcón (corta) + Pistola (corta) |
| `Segundo al mando` | Fusil FAL (media) + Pistola reglamentaria (corta) | Subfusil o Fusil ligero (media) + Pistola (corta) |
| `Apuntador` | Fusil de precisión (larga) | Fusil de cerrojo Mauser (larga) |
| `Artillero` | FAP (media) | Ametralladora ligera (media) |
| `Fusilero` | Fusil FAL (media) | Fusil Mauser (larga) o subfusil (corta) |
| `Recluta` | Fusil FAL (corta) | Lo que haya disponible |

- **`equipo.arma`**: cada arma incluye el alcance en el valor.
- **`equipo.utilitario`**: 50% ninguno, 50% 1 tag genérico (`cargador`, `vendaje`, `cantimplora`). En mocks: hasta 4-5 narrativos.
- **`equipo.armadura`**: tabla determinística por rango. Líderes/segundos/apuntadores: 1 armadura ligera (aporta 1). Artilleros/fusileros/reclutas Confederación: nada o muy ligera (aporta 0). Ejército Rojo: techo 1 por doctrina anti-equipamiento pesado.

El campo derivado `armor` total se computa al servir sumando aportes desde `/meta/equipo/armaduras/{valor}`.

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

**`filiacion`, `fza_aportada`, `armor`**: derivados al servir; no mutables porque no son persistidos.

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
| `herida` | Motor o narrador | `estado_salud: "herido"`; opcionalmente `agregar_tag` con `categoria: rasgo` |
| `recuperacion` | Motor o narrador | `estado_salud: "saludable"` |
| `formacion_vinculo` | Narrador | append a `vinculos[]`; `metadata: { vinculo_creado }` |
| `ruptura_vinculo` | Narrador | remove o transformación de `vinculos[]` |
| `cambio_lealtad` | Narrador | mutación de `lealtades.secundarias` o `lealtades.secretos` |
| `condecoracion` | Narrador | no muta campos vigentes (hito puro) |

**Detalle de `agregar_tag` y `quitar_tag` — los hitos de tags son el mecanismo central de evolución del personaje.**

`agregar_tag` y `quitar_tag` operan sobre cualquier categoría de la lista plana `tags[]`. `metadata` siempre lleva `{ categoria, valor }` como mínimo; se puede extender con contexto narrativo o mecánico.

Ejemplos representativos:

| Situación narrativa | `tipo` | `metadata` ejemplo |
|---|---|---|
| Personaje aprende una habilidad de su mentor | `agregar_tag` | `{ categoria: "skill", valor: "Lectura de columna" }` |
| Herida grave en combate deja secuela | `agregar_tag` | `{ categoria: "trait", valor: "Hemorragia lenta" }` + hito `herida` coordinado |
| Captura enemiga. Le requisaron el arma | `quitar_tag` | `{ categoria: "equipo.arma", valor: "Fusil FAL (alcance media)" }` |
| Captura y recuperación de armamento enemigo | `agregar_tag` | `{ categoria: "equipo.arma", valor: "Pistola Browning capturada (alcance corta)" }` |
| Hazaña reconocida por el alto mando | `agregar_tag` | `{ categoria: "perk", valor: "Cobertura instintiva" }` |
| Consigue tres cargadores tras asaltar una posición | `agregar_tag` (×3) | `{ categoria: "equipo.utilitario", valor: "cargador 9mm" }` — tres hitos independientes o un único hito con `metadata.cantidad: 3` si la implementación lo admite |
| Recupera visión normal tras tratamiento | `quitar_tag` | `{ categoria: "trait", valor: "Miope" }` — requiere justificación narrativa en `descripcion` |

**Trayectoria de tags y auditoría.** El estado vigente de `tags[]` es el resultado de aplicar en orden todos los hitos `agregar_tag` y `quitar_tag` sobre el snapshot `tags_iniciales` (inmutable al crear). Esto significa que la trayectoria completa de tags de un personaje se puede reconstruir reproduciendo su `historial[]` contra `tags_iniciales`, sin necesidad de un campo de historial separado para tags. Operación útil para auditoría y para el endpoint potencial `POST /character/{id}/original` (ver OQ #9).

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

Pool canon de habilidades. Cada entrada: `{ valor, descripcion, rangos_naturales: [], facciones_predominantes: [] }`. Ejemplos canon: `Comandancia`, `Francotirador`, `Medicina`, `Oratoria de muelle`, `Lectura de columna`, `Ingeniería`, `Comisariado`. El endpoint lista el vocab sugerido; valores fuera del canon son válidos.

### `GET /meta/traits`

Pool canon de rasgos de carácter/condición. Cada entrada: `{ valor, descripcion, polaridad_sugerida: "positivo"|"neutro"|"penalidad"|null, rangos_comunes: [] }`. Ejemplos canon: `Sangre fría` (positivo), `Voz grave` (neutro), `Miope` (penalidad), `Obstinado` (penalidad), `Objetivo prioritario` (penalidad), `Hemorragia lenta` (penalidad). El campo `polaridad_sugerida` es hint no autoritativo — ver tensión 13.6.

### `GET /meta/perks`

Pool canon de ventajas mecánicas. Cada entrada: `{ valor, descripcion, efecto_mecanico, rangos_naturales: [] }`. Ejemplos canon: `Voz de mando`, `Recarga rápida`, `Cobertura instintiva`. El efecto mecánico describe el resultado en juego (ej. "MEN favorable en chequeo de mando colectivo").

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
  { "categoria": "perk",             "descripcion": "Ventajas mecánicas activables." },
  { "categoria": "equipo.arma",      "descripcion": "Arma de fuego o cuerpo a cuerpo. Valor incluye alcance." },
  { "categoria": "equipo.utilitario","descripcion": "Consumible o accesorio sin aporte de armor." },
  { "categoria": "equipo.armadura",  "descripcion": "Protección con aporte de armor declarado en /meta/equipo/armaduras/{valor}." }
]
```
Abierto — futuras categorías se agregan sin breaking change.

### `GET /meta/equipo/armaduras/{valor}`

Devuelve el aporte de `armor` de cada armadura canon. Usado por la API para componer el campo derivado `armor`. Ej: `GET /meta/equipo/armaduras/chaleco+antifragmentos+reglamentario` → `{ valor: "chaleco antifragmentos reglamentario", armor: 1, faccion_predominante: "Confederación" }`.

### `GET /meta/equipo/armas`, `GET /meta/equipo/utilitarios`

Catálogos sugeridos de armas y utilitarios con alcance y facción predominante. Sin validación — el generador los usa como pool; el cliente puede listarlos para UIs.

### `GET /meta/hito_types`, `GET /meta/vinculo_types`

Catálogos sugeridos. Todos abiertos. `hito_types` incluye el efecto sobre campos vigentes para cada tipo canon (ver tabla 9.5).

### `GET /meta/escuadras/{id}` (potencial, sujeto a necesidad)

Si se introduce un endpoint de escuadras, devolvería `id`, `nombre`, `cuerpo`, `faccion`, y la composición vigente por query inverso a `escuadra_id`. Queda fuera de v1 estricto.

Mapea (todos los `/meta/*`): UC-09.

---

## 11. Los 22 mock — alcance del MVP

Los 22 personajes iniciales son fixtures en `mock/personajes/{faccion}/{nn}_{rango}_{apellido}.yaml`.

**Estado de migración.** Los 22 fixtures actuales están al schema v0.2.0/v0.2.1 y **no han sido actualizados al schema v0.2.5**. Requieren regeneración completa: nueva cabecera (sobrenombre/filiacion/estado/rango/escuadra_id/mando bool), aspectos disueltos en tags `skill`/`trait`/`perk`, equipo migrado a sub-categorías `equipo.*`, eliminación de `rol_id`, `origen_geografico`, `especialidad`, `apariencia`, `fza_aportada` (como campo) y `equipo.armor` (como campo). La regeneración se realizará en iteración separada. Hasta entonces, los mocks son válidos solo para tests que no dependan del schema nuevo.

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
- **Sistema de tags como ciudadanos de primera clase**: rasgo, rol, skill, trait, perk, equipo.{arma,utilitario,armadura}.
- **Campos derivados**: `filiacion`, `fza_aportada`, `armor` total — computados al servir.
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

**Decisión.** Las categorías de tags son un enum abierto. Las sub-categorías jerárquicas con punto (`equipo.arma`, `equipo.utilitario`, `equipo.armadura`) también son extensibles.

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

### 13.8. Denormalización opt-in de efectos de tags → dos fuentes de verdad potenciales

**Decisión.** Los efectos mecánicos de skills, traits y perks viven en `/meta/*`, no inlineados en cada tag de cada personaje.

**Costo.** Si un cliente necesita los efectos para procesar un personaje, tiene que hacer N calls adicionales a `/meta/*` o cachear el catálogo localmente. Un personaje con 12 tags puede requerir hasta 12 lookups adicionales.

**Por qué se acepta.** Inlinear el efecto en el tag del personaje es una trampa de denormalización: si el catálogo cambia (un perk recibe errata), habría que actualizar todos los personajes con ese perk.

**Mitigación.** La API puede soportar un query param `?expand=tags` que en una sola call devuelva la ficha del personaje con cada tag resuelto contra su entrada en `/meta/*`. Fuera de v1 estricto.

---

## 14. Píldoras de arquitectura

### 14.1. Tags y stores no-transaccionales

El patrón de entidades pequeñas, repetibles, agrupables y sin esquema rígido (tags) es el caso textbook para un store no-transaccional o document-oriented. Cloudflare D1 con columna JSON o Workers KV con prefijo por categoría son candidatos naturales.

### 14.2. Tags como ciudadanos de primera clase → inverted index natural

Con v0.2.5 los tags absorben rasgos, rol, skills, traits, perks y equipo subcategorizado — la mayor parte del contenido mutable del personaje. Esto refuerza la afinidad NoSQL/document-store ya señalada y añade una segunda observación: el query típico downstream es **"dame personajes con tag X"** o **"expandime los efectos mecánicos de estos tags"**. Es el patrón clásico de **inverted index sobre tags**, soportado nativamente por D1 con índices JSON o por Workers KV con clave compuesta `tag:{categoria}:{valor}` apuntando a lista de `personaje_id`.

Ejemplo concreto: la query "personajes con `skill: Francotirador` AND `rol: lider` AND facción `Confederación`" se resuelve con tres lookups en el inverted index (`skill:Francotirador`, `rol:lider`, filtro `faccion`) seguidos de intersección de sets de `personaje_id`. Más barato que un full scan sobre el campo JSON de cada ficha. Con los seis tipos de categoría canon y un corpus de ~100 canonizados, un inverted index en Workers KV cabe cómodamente en memoria.

Esta píldora no fija stack; solo registra que el diseño v0.2.5 hace que las optimizaciones de búsqueda sean baratas si la necesidad aparece — y los UCs 19, 20, 21 y 22 (filtros por tag) confirman que aparecerá.

### 14.3. Campos derivados → cómputo al servir, no al persistir

`filiacion`, `fza_aportada` y `armor` total son derivados que la API computa al armar la respuesta. Esto evita inconsistencias (no se puede tener un `armor` desincronizado con los tags `equipo.armadura`) y simplifica el modelo de persistencia. El costo es CPU al servir; se asume bajo dado el tamaño del payload.

---

## 15. Open questions v0.2.5

1. **Nombre final del campo derivado `filiacion`.** Alternativas en evaluación: `designacion`, `titulo`, `pie_de_firma`. El nombre `filiacion` se usa como provisorio en v0.2.5. Decidir antes de v1.0.

2. **Gobernanza de `POST /character/{id}/event`.** ¿Quién puede llamarlo? Sin auth en v1, cualquiera con la URL puede. Decidir si se atemporaliza con tokens, lista blanca, o se acepta porque el corpus es curable.

3. **Polaridad de `trait`.** ¿Existe `/meta/traits/{valor}.polaridad` como hint sugerido, o se deja al motor downstream interpretar libremente? Documentado en 13.6 pero el endpoint no está decidido.

4. **`armor` derivado siempre vs on-demand.** ¿La API devuelve `armor` total siempre derivado en la respuesta de `GET /character/{id}`, o solo cuando el cliente expande tags `equipo.armadura` con sus efectos? Recomendación implícita: siempre devolverlo, costo CPU bajo. Confirmar.

5. **Schema completo de la entidad `escuadra`.** v0.2.5 introduce `escuadra_id` y la entidad implícita (`id`, `nombre`, `cuerpo`, `faccion`) pero no especifica un schema completo ni endpoints CRUD. Definir en v1.1 o cuando aparezca el primer consumidor que necesite gestionar escuadras.

6. **Mutabilidad fina de rasgos físicos.** Cicatrices mutan vía `agregar_tag`. ¿Pero altura o complexión pueden mutar tras una herida grave ("queda enjuto tras la convalecencia")? El PRD las marca modificables como cualquier tag, sin restricción explícita.

7. **Interpretación de customs por el motor.** ¿El motor de batalla interpreta `perk` custom con LLM al aplicar la regla, o un curador humano traduce el custom a regla mecánica antes? Tensión documentada (13.1), flujo operacional abierto.

8. **Versionado de categorías canon de tags.** Las categorías y sub-categorías (`rasgo`, `skill`, `equipo.arma`, etc.) se documentan en `/meta/tag_categories`. ¿Gobernanza del catálogo? ¿Se versiona junto al PRD?

9. **`POST /character/{id}/original`.** ¿Útil exponer un endpoint que regenere la ficha al estado de creación (sin historial) usando `semilla` + `tags_iniciales`, para que herramientas externas calculen el diff? Fuera de v1; útil para auditoría.

10. **Catálogo de tags canon por facción.** ¿El catálogo `/meta/skills` tiene entries segmentadas por facción (`facciones_predominantes: ["Ejército Rojo"]`)? ¿El generador rechaza o avisa cuando sortea un tag que el canon considera cruzado (ej. `skill: Comisariado` para un personaje Confederado)? ¿O se acepta con libertad?

11. **Política de eviction de tags obsoletos.** Si el catálogo `/meta/skills` retira un valor (ej. `Oratoria de muelle` renombrado a `Oratoria sindical`), los personajes que ya tienen ese tag no se actualizan. ¿Se acepta silenciosamente o se implementa un job de migración? ¿Existe un mecanismo de alias para que ambos valores resuelvan al mismo efecto?

12. **Normalización de case en `valor`.** ¿El schema normaliza `valor` de tags a lowercase antes de persistir? Evita fragmentación silenciosa (`Francotirador` ≠ `francotirador`). Tensión 13.7. Decisión mínima viable antes de v1.

13. **Límite de tags por categoría.** ¿Hay un máximo razonable de tags por categoría? Un personaje con 20 `equipo.utilitario` es sintácticamente válido pero semánticamente raro. ¿El generador tiene caps internos? ¿La API los valida o advierte?

---

*Fuentes canónicas referenciadas (no copiadas):*

- `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md` — esquema y matriz de stats por rango.
- `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md` — pools de perks y complicaciones (estos últimos migrados como traits con polaridad negativa en v0.2.5).
- `/Dev/syv-battle-game-system/lore/universo.md` — descriptores de facción usados como contexto del LLM.
- `/Dev/syv-battle-game-system/personajes/` — 22 fichas canon base que alimentan los mocks (pendientes de regeneración al schema v0.2.5).
- `https://github.com/kodexArg/syv-game-system/blob/main/arquitectura/esquemas/personaje.schema.json` — schema público de referencia.
