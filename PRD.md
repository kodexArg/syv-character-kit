# PRD — syv-character-kit

> **Documento vivo, rolling release.** Define el contrato de producto de la API generadora de personajes del universo *Subordinación y Valor* (SyV). No contiene decisiones de arquitectura, almacenamiento ni stack — solo el QUÉ. **El estado vigente es el único oficial**: no hay versiones, ni changelog, ni compatibilidad con el pasado. Para política editorial, ver [`AGENTS.md`](AGENTS.md).
>
> **Idioma**: castellano rioplatense, voseo sobrio.
> **Convención de identificadores en payloads YAML**: `snake_case_castellano` para campos estructurales; los tags se escriben en **notación punto** (`<categoria>[.<subcategoria>].<slug>`) con slugs en lowercase + underscore, sin acentos.
> **Fuente autoritativa del schema**: [`docs/hoja-modelo.md`](docs/hoja-modelo.md) (estructura del personaje) y [`docs/tag-modelo.md`](docs/tag-modelo.md) (sistema de tags). Este PRD describe el contrato de producto; los detalles del schema viven en /docs.

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
- **Customs libres + enums abiertos como política deliberada.** El producto acepta tags `skill`/`trait`/`perk` con valores fuera del canon. Los enums (`tipo` de hito, `tipo` de vínculo, sub-categoría de tag, etc.) tienen valores **sugeridos** pero no rechazan otros. **Tensión asumida**: el motor downstream que consuma estos customs tiene que poder interpretarlos. Ver sección 12.
- **Stats determinísticos por rango, narrativa sorteada.** En creación, los atributos se derivan de una matriz fija por rango operativo. Nombre, género, rasgos, skills/traits/perks, equipamiento e historia se sortean.
- **Memoria viva como naturaleza del recurso canonizado.** Un canonizado tiene historial y muta. No es un payload; es una entidad. Ver sección 8.
- **Reproducibilidad por seed para efímeros.** Toda creación admite `?seed=`. La misma `(seed, faccion, rango)` produce el mismo personaje, incluida la prosa inicial. **Limitación aceptada**: los canonizados pierden esta propiedad tras el primer hito.
- **LLM solo para prosa, solo una vez.** El modelo generativo escribe el campo `historia` en la creación efímera. Si el personaje se canoniza, esa prosa se congela.
- **Mocks separados de canonizados.** Los 22 mocks son fixtures inmutables del battle-system. Los canonizados son entidades vivas de la API. No hay sincronización ni promoción mock → canonizado.
- **El PRD es contrato; el repo es implementación.** Este documento define formas y reglas. Cómo se almacenan tablas, dónde corre el LLM, qué binding usa la persistencia — fuera de scope.
- **Agnosis al renderer.** El schema describe *qué* tiene un personaje, no *cómo* se muestra. Los tags se agrupan por categorías para que cualquier consumidor (CLI ASCII, UI web, motor de batalla, exportador a PDF) decida cómo presentarlos como secciones visuales. El modelo no impone una forma de renderizado. Una misma hoja puede aparecer como bloques ASCII, tarjetas, filas de tabla, o grafo de relaciones — todas son vistas válidas del mismo recurso.
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

---

## 6. Schema canónico del personaje

**Fuente autoritativa**: este PRD describe el *contrato de producto*. La spec detallada del schema vive en /docs y es la fuente de verdad para implementadores y curadores:

- [`docs/hoja-modelo.md`](docs/hoja-modelo.md) — estructura de la hoja de personaje (identidad, atributos, tags, historia, historial, metadatos, extras).
- [`docs/hoja-modelo.yaml`](docs/hoja-modelo.yaml) — template programático vacío.
- [`docs/tag-modelo.md`](docs/tag-modelo.md) — sistema de tags: notación punto, categorías canon, relacionales (`lealtad`, `nemesis`), catálogo.
- [`docs/tag-modelo.yaml`](docs/tag-modelo.yaml) — template de entrada de catálogo.

### 6.1. Estructura de la hoja (resumen)

```
personaje:
  identidad: {slug, nombre, sobrenombre, rol, genero, edad}
  atributos: {fis, tac, men}
  tags: [...]                  # lista plana de strings en notación punto
  historia: str                # prosa biográfica congelada
  historial: [...]             # eventos temporales (hitos)
  metadatos: {creado_en, canonizado_en, ultima_actualizacion}
  extras: object | null        # escape hatch libre
```

Solo seis bloques estructurados más la lista de tags. Regla rectora: **todo lo que puede ser discreto y no es identidad estable, atributo numérico, prosa o auditoría — es tag**.

### 6.2. Tags en notación punto

Un tag se escribe como string único: `<categoria>[.<subcategoria>].<slug>`. Ejemplos:

| Tag | Significado |
|---|---|
| `faccion.ejercito_rojo` | Pertenencia macro. |
| `rango.lider_de_escuadra` | Designación operativa jerárquica. |
| `escuadra.ricardo` | Asignación a escuadra concreta. |
| `mando.capaz` | Capacidad de mando (presencia = `true`). |
| `estado.activo` | Disponibilidad operativa (exactamente uno por personaje). |
| `salud.herido` | Estado físico actual; acumulable. |
| `mental.panico` | Estado anímico actual; acumulable. |
| `rasgo.altura_media` | Rasgo físico observable. |
| `trait.taciturno` | Rasgo de carácter sin mecánica. |
| `perk.veterano` | Ventaja reglada con efecto numérico. |
| `aspecto.cabron` | Mini-tag identitario con efecto en mini-frase. |
| `skill.comandancia` | Habilidad aprendida. |
| `equipo.arma.rifle_militar` | Arma cargada. |
| `equipo.utilitario.cargador` | Objeto utilitario (repetible). |
| `equipo.vestidura.uniforme_confederado` | Identidad visual. |
| `rol.oficio.francotirador` | Oficio operativo de combate. |
| `rol.jerarquia.sargento` | Título militar. |
| `rol.mecanico.lider` | Rol mecánico (afecta `fza_aportada`). |
| `lealtad.faccion.confederados` | Lealtad a una facción. |
| `lealtad.pj.aguirre_walter` | Lealtad a otro personaje persistido. |
| `nemesis.pj.iturra_delia` | Enemistad personal creada en batalla. |

Detalles completos de cada categoría — campos del catálogo, sub-categorías, patrones relacionales, OQs — en `docs/tag-modelo.md`.

### 6.3. Derivaciones del motor (no persistidas)

Calculadas en caliente al servir desde tags + atributos:

- **`filiacion`** — string `"{rango} de la {escuadra.nombre} del {escuadra.cuerpo}"` desde tags `rango.*` y `escuadra.*` (lookups en el catálogo).
- **`sobrenombre`** — derivable desde `nombre`, `rango.*` y `rol.*` de mando si aplican; `null` si no hay distinción con el nombre real.
- **`fatiga_max`** — `atributos.fis + atributos.men`.
- **`moral_max`** — `atributos.men`.
- **`fza_aportada`** — `3` con `rol.mecanico.heroe`, `2` con `rol.mecanico.lider`, `1` sin ninguno.
- **`aliados`** — lista derivada de personajes a los que el portador ha jurado lealtad personal. Computada proyectando los tags `lealtad.pj.*`. Comienza vacía al crear el personaje y se puebla en caliente al agregarse el tag relacional.
- **`nemesis`** — lista derivada de personajes identificados como rivales individuales. Computada proyectando los tags `nemesis.pj.*`. Mismo lifecycle que `aliados`: empieza vacía, se puebla en caliente. Un personaje puede tener un némesis del propio bando (accidente, traición personal); el sistema no lo prohíbe.

### 6.4. Lo que NO es tag

Recordatorio explícito:

- **`identidad`** (slug, nombre, sobrenombre, rol narrativo base, género, edad) — datos nominales únicos, no enumerables.
- **`atributos`** (fis, tac, men) — magnitudes numéricas continuas.
- **`historia`** — prosa biográfica de 120-200 palabras.
- **`historial`** — eventos temporales estructurados (no discretos).
- **`metadatos`** — timestamps de auditoría.
- **`extras`** — escape hatch para clientes externos.

### 6.5. Notas de campo

- **Repetibilidad**: `tags[]` es multiset. Tres `equipo.utilitario.cargador` son tres entidades físicas distintas.
- **Refs compuestas**: las relacionales (`lealtad`, `nemesis`) usan prefijos `faccion.`, `pj.`, `escuadra.` dentro del slug para indicar a qué tipo de entidad apuntan.
- **Indistinción mock/DB**: los tags cargados del catálogo mock y los creados en caliente desde la API o el motor son indistinguibles — no hay campo `origen` en el tag aplicado al personaje.
- **Catálogo de tags**: cada tag canon tiene archivo en `mock/tags/{categoria}[/{subcategoria}]/{slug}.yaml`. Las categorías relacionales (`lealtad`, `nemesis`) no tienen entradas de catálogo — su semántica es del formato del tag, no del contenido.

### 6.6. Extensibilidad total del sistema de tags

**Principio rector**: el catálogo canon es andamiaje, no jaula. El sistema de tags ofrece una ordenación sugerida (`faccion`, `rango`, `escuadra`, `skill`, `equipo.*`, `rol.*`, etc.) que cubre los casos comunes y permite a clientes downstream apoyarse en semántica conocida — pero **no impone restricciones** sobre qué se puede crear.

Tres ejes de extensibilidad, todos sin permiso ni migración:

1. **Nuevos valores dentro de una categoría existente** — `skill.lockpicking`, `rasgo.tatuaje_de_ancla`, `aspecto.terco_como_mula`. El generador o el narrador los crea al vuelo; entran al catálogo con `origen: emergente` la primera vez que aparecen, o como `custom` si llegan desde un cliente externo.
2. **Nuevas sub-categorías dentro de una familia** — `equipo.montura.caballo_criollo` agrega un nivel a `equipo.*`; `rol.administrativo.intendente` extiende `rol.*` más allá de las cuatro sub-jerarquías canon (`oficio`, `jerarquia`, `narrativo`, `mecanico`).
3. **Categorías nuevas enteras** — `oficio_civil.herrero`, `vicio.fuma`, `mascota.perro_pastor`. El parser solo necesita el primer segmento del tag para enrutar; las categorías nuevas conviven con las canon sin colisionar.

**Lo que el sistema garantiza:** un tag desconocido no rompe la hoja. El motor downstream que no lo reconozca lo puede ignorar o renderizarlo como genérico; el motor que sí lo entienda lo aplica con la semántica que su autor le dio. La API no rechaza personajes por tener tags fuera del canon.

**Lo que el sistema NO promete:** que dos generadores distintos vayan a coincidir sobre cómo nombrar el mismo concepto. La fragmentación silenciosa (`Francotirador` vs `francotirador`, o `skill.medicina` vs `medicina.curacion`) es un costo asumido (ver tensión 12.7). La mitigación es **curaduría del catálogo**, no validación del schema.

**Implicación para el cliente**: cualquier persona narrando una sesión, alimentando una batalla o creando un personaje a mano puede inventar el tag que su escena necesita. Si un personaje tiene un sombrero específico que importa para el lore, se crea `equipo.vestidura.sombrero_de_su_abuelo` y se aplica. Si esa idea cobra fuerza, alguien curará una entrada de catálogo para que otros la usen. Si no, queda como custom y muere con esa ficha. Ambos caminos son válidos.

Esta libertad es deliberada y central al diseño del producto: la mayoría de los personajes encajan en el andamiaje canon, pero los que necesitan algo único pueden expresarlo sin pelearse con el schema. Es el mismo trade-off que se asume con `extras: object` para los casos extremos, pero a nivel de tags conserva la semántica de búsqueda y filtrado.

### 6.7. Coherencia declarativa: el bloque `requires`

Cada entrada de catálogo puede declarar un bloque opcional `requires` con dos listas combinables — `require_all` y `require_any` — que enumeran tags pre-requisito para que el tag sea coherente sobre un personaje. Cualquier entrada admite el prefijo literal `"no:"` para invertir la condición (ej. `"no:salud.herido"` significa "el personaje debe NO tener `salud.herido`").

Esto es **documentación ejecutable**, no validación de schema. La API acepta personajes con combinaciones incoherentes; los generadores, validadores opcionales y curadores son quienes pueden consultar `requires` para decidir si aplicar, advertir o rechazar. La semántica precisa y un ejemplo completo viven en `docs/tag-modelo.md §4.3`.

---

## 7. Reglas de generación dinámica

Cómo se completa cada campo en un personaje **generado dinámicamente** (origen `"generado"`). Los mocks ignoran estas reglas: vienen escritos a mano. Los canonizados nacen como un generado o como un body explícito, y a partir de ahí mutan vía hitos (sección 8).

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
9. Inicializar `tags` con pools sorteados de `rasgo`, `rol.*`, `skill`, `trait`, `perk`, `equipo.arma`, `equipo.utilitario`, `equipo.vestidura` — cada categoría tiene sus propias reglas de sorteo detalladas en 7.4–7.8.
10. Inicializar `historial: []`.
11. Generar `historia` con LLM, anclada en facción + rango + rol + skills/traits/perks + lugar implícito.
12. La API compone `filiacion`, `sobrenombre` y `fza_aportada` derivados al servir.

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

(El bloque `origen_geografico` fue eliminado. Si la procedencia importa narrativamente, se cuenta en `historia` o se añade como `rasgo` / `extras`.)

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

### 7.14. Estado inicial de salud y mental

En personajes recién generados ambos bloques arrancan vacíos: `salud: []` y `mental: []` (sin tags `salud.*` ni `mental.*` aplicados). El motor downstream va aplicando y removiendo estos tags vía hitos `cambio_salud` / `cambio_mental` según el curso de la batalla.

---

## 8. Memoria viva — el diferencial del producto

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

- `identidad.slug`, `identidad.nombre`, `identidad.genero`, `historia`.
- `metadatos.creado_en`, `metadatos.canonizado_en`.

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

**Trayectoria de tags y auditoría.** El estado vigente de `tags[]` se modifica vía hitos `agregar_tag` y `quitar_tag` en el `historial`. La trayectoria completa de tags de un personaje se puede reconstruir hacia adelante reproduciendo el historial, o hacia atrás aplicando los hitos en reversa contra el estado vigente. El schema no expone un snapshot inmutable del estado inicial — la decisión de mantener el schema mínimo prima sobre la queryabilidad directa de "cómo nació el personaje".

**Nota — aspectos mutables.** No existen los hitos `mejora_aspecto`. Los cambios de identidad mecánica (perk, trait, skill) son adiciones/eliminaciones a las categorías correspondientes vía `agregar_tag` / `quitar_tag`.

**Nota — atributos y rango.** Los atributos `{fis, tac, men}` son propiedad del personaje, no derivados del rango post-creación. Cuando cambia `rango`, los atributos no se tocan. Los tags `categoria: rol` sí se realinean. La matriz por rango (7.2) aplica **únicamente** en creación.

---

## 9. Endpoints (alto nivel)

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

Pool canon de rasgos de carácter/condición. Cada entrada: `{ valor, descripcion, polaridad_sugerida: "positivo"|"neutro"|"penalidad"|null, rangos_comunes: [] }`. Ejemplos canon: `Sangre fría` (positivo), `Voz grave` (neutro), `Miope` (penalidad), `Obstinado` (penalidad), `Objetivo prioritario` (penalidad), `Hemorragia lenta` (penalidad). El campo `polaridad_sugerida` es hint no autoritativo — ver tensión 12.6.

### `GET /meta/perks`

Pool canon de ventajas mecánicas. Cada entrada: `{ valor, descripcion, efecto_mecanico, rangos_naturales: [] }`. Ejemplos canon: `Voz de mando`, `Recarga rápida`, `Cobertura instintiva`. El efecto mecánico describe el resultado en juego (ej. "MEN favorable en chequeo de mando colectivo").

### `GET /meta/aspectos`

Pool canon de aspectos. Cada entrada: `{ valor, efecto, activa_tag?, rangos_naturales?: [] }`. El campo `efecto` es la **mini-frase** de mecánica embebida (texto libre, en castellano, que el motor downstream interpreta). El campo opcional `activa_tag` indica cuando el efecto del aspecto dispara un tag transitorio (categoría conceptual `estado_temporal`, ej. `berserker`, `pánico`).

Pool semilla (10 aspectos):

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

Las seis categorías canon de con descripción y política de uso. Respuesta tipo:
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

### 10.1. Catálogo canon `/meta/*` — 80 tags semilla

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

**`/meta/equipo/vestiduras` — 4 vestiduras (cerrado por decisión del cliente):**
```
ropa de civil, uniforme rojo, uniforme confederado, camuflaje básico
```

**`/meta/aspectos` — 10 aspectos canon (nuevo):**
```
cabrón, ojo-de-halcón, muy-fuerte, cobarde, carismático,
terco, veloz, veterano-cicatrizado, devoto, impredecible
```

**Total: 80 tags semilla** (6 armas + 10 utilitarios + 10 rasgos + 10 roles + 10 skills + 10 traits + 10 perks + 4 vestiduras + 10 aspectos). La categoría `aspecto` se promueve a ciudadana canon (ver sección 15).

---

## 10. Los 22 mock — alcance del MVP

Los 22 personajes iniciales son fixtures en `mock/personajes/{faccion}/{nn}_{rango}_{apellido}.yaml`.

**Estado de los mocks.** Cada fixture tiene exactamente 1 tag `equipo.vestidura` del catálogo cerrado de 4 valores (uno por facción/rol). Tags emergentes (oficios, customs narrativos) coexisten con el catálogo canon — el catálogo es semilla, no purga.

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

## 11. Alcance MVP vs futuro

### Dentro de v1

- 2 facciones jugables: Confederación y Ejército Rojo.
- 6 rangos operativos canon con su matriz determinística.
- Pools canon de `skill`, `trait`, `perk` (este último con metadato `rangos_naturales`).
- Tablas curadas de nombres, edades, géneros, equipo por facción.
- Generación efímera con seed reproducible.
- 22 mocks regenerados al schema en iteración separada.
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
- Schema completo de la entidad `escuadra` (queda como entidad implícita; se especifica cuando se necesite).
- Endpoint `/meta/escuadras` con composición vigente (potencial v1.1).
- Operación "diff entre estado original y estado vigente" automatizada.

---

## 12. Tensiones explícitas y compromisos asumidos

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

**Mitigación.** El `historial` registra cada mutación con `agregar_tag` / `quitar_tag` y permite reconstruir la trayectoria. El schema no expone una promesa de regenerabilidad byte-a-byte; la prosa LLM no es determinísticamente reproducible y por eso no hay `semilla` ni snapshot.

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

**Decisión.** El catálogo canon de 70 tags semilla (sección 9.1) es vocabulario sugerido, no enum cerrado. La excepción es `equipo.vestidura`, cerrado en 4 valores por decisión del cliente.

**Costo.** Convive con la fragmentación documentada en 13.2 y 13.7: distintos usuarios pueden crear sinónimos del mismo concepto (`Tiro de precisión` canon vs `Francotirador` custom), y el catálogo emergente termina mezclando registros canónicos con customs no normalizados.

**Por qué se acepta.** El usuario explicitó: "completamos lo estándar, los casos más normales solamente; otros usuarios crearán tags personalizados". Forzar enum cerrado en `skill`/`trait`/`perk`/`equipo.{arma,utilitario}` paralizaría la creatividad narrativa, que es exactamente el diferencial del producto.

**Mitigación.** El catálogo semilla cubre los casos comunes del MVP — un cliente sano resuelve >80% de los personajes contra la semilla. Los `/meta/*` pueden marcar entradas con `origen: "canon" | "emergente"` para que el cliente discrimine. La normalización de case (OQ #11) y el mecanismo de alias (OQ #10) atacan el síntoma cuando lleguen a v1.

### 13.8. Denormalización opt-in de efectos de tags → dos fuentes de verdad potenciales

**Decisión.** Los efectos mecánicos de skills, traits y perks viven en `/meta/*`, no inlineados en cada tag de cada personaje.

**Costo.** Si un cliente necesita los efectos para procesar un personaje, tiene que hacer N calls adicionales a `/meta/*` o cachear el catálogo localmente. Un personaje con 12 tags puede requerir hasta 12 lookups adicionales.

**Por qué se acepta.** Inlinear el efecto en el tag del personaje es una trampa de denormalización: si el catálogo cambia (un perk recibe errata), habría que actualizar todos los personajes con ese perk.

**Mitigación.** La API puede soportar un query param `?expand=tags` que en una sola call devuelva la ficha del personaje con cada tag resuelto contra su entrada en `/meta/*`. Fuera de v1 estricto.

### 13.11. Tags mínimos vs riqueza contextual

**Decisión.** En los tags se normalizan a forma mínima: 1-2 palabras, 3 cuando el nombre canónico lo exige. Cero prosa, cero paréntesis, cero comas internas, cero guiones largos. El tag es **identificador**, no descripción.

**Costo.** Se pierde info contextual enriquecida que vivía dentro del propio tag — "brújula de oficial — regalo del instructor de Stroeder" colapsa a `brújula`; "cuaderno de campaña — anotaciones de terreno, firma con la inicial R en el margen" colapsa a `cuaderno`. Parte de ese color narrativo ya estaba duplicado en la prosa de `historia` (y ahí queda); parte se pierde irreversiblemente. La pérdida es aceptada como costo del minimalismo.

**Por qué se acepta.** Tags-como-ID habilitan inverted index trivial (14.2), comparación entre personajes, agregación en `/meta/*`, y semántica predecible para el motor downstream. Tags-como-prosa-disfrazada rompen esas tres cosas. La info contextual canónica vive en el catálogo `/meta/*`; el color narrativo vive en `historia`; la info estructurada por instancia, si llega a hacer falta, va a la futura entidad `notas` (OQ #16).

**Mitigación.** La pasada de preservó literal la prosa de `historia` e `historial[]` en los 22 mocks — toda la info contextual irrecuperable que estuviera reflejada ahí sigue viva. Una ola futura puede introducir `notas: array<{tag_ref, texto}>` si el caso de uso aparece (ver OQ #16).

---

### 13.10. Efecto del aspecto en texto libre → motor downstream interpreta mini-frase

**Decisión.** El campo `efecto` de cada entrada de `/meta/aspectos/{valor}` es **string libre** en castellano (consistente con `perk.efecto_mecanico`). No se estructura en parsing rígido (trigger / probabilidad / efecto / tag activado).

**Costo.** El motor de batalla necesita interpretar la mini-frase para aplicarla — probablemente vía LLM resolver o regla heurística (`split` por "si", "%", "+", "repite", "activa tag"). Aspectos custom escritos por humanos cargan más riesgo de parsing fallido que los 10 canon.

**Por qué se acepta.** Mismo compromiso de 13.1 (customs libres) y 13.8 (denormalización opt-in): forzar estructura rígida ahora paralizaría la curaduría de aspectos custom. El catálogo canon de 10 aspectos tiene mini-frases **bien formadas y predecibles** (patrón verbo + porcentaje + condición). Los customs cargan el riesgo.

**Mitigación.** El catálogo `/meta/aspectos` puede declarar `activa_tag` como campo opcional estructurado cuando el efecto dispara un tag transitorio (`berserker`, `pánico`). Esto absorbe el caso más común sin estructurar todo el efecto. Si la fricción crece, una ola futura puede introducir `efecto_estructurado: { trigger, probabilidad, efecto, activa_tag }` como hint opcional junto al texto libre.

---

## 13. Píldoras de arquitectura

### 14.1. Tags y stores no-transaccionales

El patrón de entidades pequeñas, repetibles, agrupables y sin esquema rígido (tags) es el caso textbook para un store no-transaccional o document-oriented. Cloudflare D1 con columna JSON o Workers KV con prefijo por categoría son candidatos naturales.

### 14.2. Tags como ciudadanos de primera clase → inverted index natural

Con los tags absorben rasgos, rol, skills, traits, perks y equipo subcategorizado — la mayor parte del contenido mutable del personaje. Esto refuerza la afinidad NoSQL/document-store ya señalada y añade una segunda observación: el query típico downstream es **"dame personajes con tag X"** o **"expandime los efectos mecánicos de estos tags"**. Es el patrón clásico de **inverted index sobre tags**, soportado nativamente por D1 con índices JSON o por Workers KV con clave compuesta `tag:{categoria}:{valor}` apuntando a lista de `personaje_id`.

Ejemplo concreto: la query "personajes con `skill: Francotirador` AND `rol: lider` AND facción `Confederación`" se resuelve con tres lookups en el inverted index (`skill:Francotirador`, `rol:lider`, filtro `faccion`) seguidos de intersección de sets de `personaje_id`. Más barato que un full scan sobre el campo JSON de cada ficha. Con los seis tipos de categoría canon y un corpus de ~100 canonizados, un inverted index en Workers KV cabe cómodamente en memoria.

Esta píldora no fija stack; solo registra que el diseño hace que las optimizaciones de búsqueda sean baratas si la necesidad aparece — y los UCs 19, 20, 21 y 22 (filtros por tag) confirman que aparecerá.

### 14.3. Campos derivados → cómputo al servir, no al persistir

`filiacion` y `fza_aportada` son derivados que la API computa al armar la respuesta. El campo `armor` fue eliminado del sistema: la vestidura es identidad visual y no aporta protección numérica; si más adelante se necesita defensa, vuelve como tag `trait: blindado` derivado de vestidura o skill defensiva.

---

## 14. Open questions

Decisiones de producto que el PRD no resuelve todavía. Cuando una se resuelve, esta sección se reescribe; las resueltas no quedan archivadas (vive en `git log`).

- **`slug` derivado vs persistido en archivos de catálogo de tag.** Ver `docs/tag-modelo.md §7`.
- **Catálogo de personajes históricos** referenciados por `lealtad.pj.*` pero no presentes en el roster activo (ej. mentores caídos citados en lealtades). Crear un catálogo `mock/personajes_historicos/` con entradas mínimas (slug, nombre, breve nota) o mantener slugs sintéticos sin entrada de catálogo.
- **Sistema de lealtades latentes / secretas / aspiracionales.** El bloque eliminado `lealtades: {primaria, secundarias, secretos}` cubría más de lo que `lealtad.*` cubre hoy. Modelos a evaluar: tags `lealtad_latente.*` con visibilidad restringida, entidad nueva `intenciones[]`, o extensión del bloque `extras`.
- **Regla canónica de titularidad de mando.** El tag `mando.capaz` indica capacidad. ¿La titularidad vigente se deriva como `mando.capaz` AND mayor `rango.*` en `escuadra.*`? ¿Empate de rango cómo se rompe?
- **Nombre final del campo derivado `filiacion`.** Alternativas: `designacion`, `titulo`, `pie_de_firma`.
- **Gobernanza de mutaciones de personaje vía API.** Sin auth, cualquiera con la URL puede emitir hitos. Tokens, lista blanca, o aceptación porque el corpus es curable.
- **Polaridad de `trait`.** ¿Existe `/meta/traits/{slug}.polaridad` como hint sugerido, o el motor downstream interpreta libremente? Tensión 12.6.
- **Schema completo de la entidad `escuadra`.** El tag `escuadra.{slug}` necesita un catálogo análogo a `mock/tags/faccion/`. Definir slug canónico y campos del archivo (nombre legible, cuerpo, facción asociada).
- **Interpretación de tags `custom` por el motor.** ¿LLM al aplicar la regla, o curador humano traduce a regla mecánica antes? Tensión 12.1.
- **Versionado de categorías canon de tags.** Las sub-categorías de la notación punto son ciudadanos explícitos del catálogo. Gobernanza pendiente.
- **Catálogo de tags canon por facción.** El campo `skill.facciones_predominantes` está documentado (`docs/tag-modelo.md §5`); falta política de avisos cuando el generador sortea un tag fuera de su facción esperada.
- **Política de eviction de tags obsoletos.** Si el catálogo retira un slug, los personajes que lo tienen no se actualizan. Sin mecanismo de alias todavía.
- **Límite de tags por categoría.** ¿Hay máximo razonable? ¿Caps internos del generador? ¿La API valida o advierte?
- **Polaridad explícita de aspectos.** ¿Los aspectos admiten `polaridad: positivo | neutro | penalidad`, o se tratan como neutros y el motor interpreta el texto libre del `efecto`?
- **Gobernanza del pool semilla de aspectos.** Los aspectos cargan más peso mecánico que skills o traits; sugiere gobernanza más estricta del catálogo.
- **Entidad `notas` como capa enriquecida de tags.** `notas: array<{tag_ref, texto}>` permitiría persistir contexto narrativo o mecánico atado a tags específicos sin contaminar el slug. Cubriría el caso histórico (cuaderno con anotaciones) y el caso de vínculos (descripción del mentor).
- **Migración final de los 22 mocks al modelo de lista plana de tags en notación punto.** Bloqueada por la decisión sobre la prosa de `vinculos[].descripcion` (mover a `historia`, a entradas de `historial` con tipo `formacion_vinculo`, o descartar).

---

## 15. Roadmap y naturaleza del entregable

### 16.1. Naturaleza agnóstica del PRD

Este documento describe el sistema de creación de personajes y sus reglas **sin comprometerse con un lenguaje de programación, framework, plataforma de despliegue ni stack concreto**. Las decisiones de implementación quedan diferidas.

Lo único canónico aquí es:

- **Schema de la hoja**: la forma completa del recurso `personaje` (§6) con todos sus campos, tipos y restricciones.
- **Reglas de atributos / tags / aspectos / estado_vital**: las invariantes de distribución por rango (§7), el sistema de tags categorizado (§6.2, §8, §9), la mecánica de aspectos (§9, §12.10), y el bloque `estado_vital` con sus derivados.
- **Generador de personajes**: el algoritmo determinístico y el pipeline de prosa que lo acompaña (§7, §7.2, §7.2.1, §7.9.5).
- **Suite de tests del generador**: las invariantes que todo generador conforme debe satisfacer (golden mocks, distribuciones esperadas, idempotencia por semilla).

Cualquier otro detalle — base de datos, lenguaje de programación, framework HTTP, runtime, infraestructura — es implementación y vive fuera de este PRD.

---

### 16.2. Hito 1 — Creación perfecta de personajes (**ACTIVO**)

Único hito al que apunta este PRD en su versión vigente. Cubre los cuatro entregables siguientes, todos agnósticos respecto del stack:

#### 16.2.1. Schema + reglas + validación

La hoja canónica (documentada en `docs/hoja-modelo.{yml,md}` y en §6–§9 de este PRD), las invariantes de atributos / tags / aspectos / estado_vital, y los validadores correspondientes. Entregable estático: no requiere servidor ni persistencia para ser validado.

#### 16.2.2. Generador procedural

Algoritmo (sin LLM) capaz de producir personajes nuevos respetando:

- Distribuciones de atributos por rango (§7.2 / §7.2.1).
- Pool de tags semilla por categoría (§8 y catálogos `/meta/*`).
- Pool de aspectos (§9).
- Semilla reproducible (`metadatos.semilla`): la misma `(semilla, faccion, rango)` produce siempre el mismo resultado.

#### 16.2.3. Generador vía LLM (prosa)

Pipeline que rellena el campo `historia` y enriquece descripciones narrativas a partir del personaje procedural. El LLM solo interviene en la prosa — la estructura y los atributos los produce el algoritmo procedural.

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

## 16. Aspectos como ciudadanos canon — capa narrativa-mecánica

### 17.1. Implementación efectiva

En la categoría **`aspecto`** se promueve de reserva a ciudadana canon del sistema de tags. La forma final de la primera ola es distinta de la previsión original (ver 17.3): se opta por **mini-tags identitarios cortos en kebab-case** (`cabrón`, `ojo-de-halcón`, `muy-fuerte`) con efecto mecánico embebido en una mini-frase corta servida por `/meta/aspectos/{valor}`, en lugar de la frase larga de 10–25 palabras que se había anticipado.

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

La nota arquitectónica de anticipaba aspectos como **frases narrativas largas** (10–25 palabras) al estilo de H.I.T.O.S. y Cultos Innombrables, donde el personaje "dice algo de sí mismo" en oración completa. Ejemplos previstos en aquel momento:

- `"Cuando la columna se quiebra, alguien tiene que mantener la voz."` (aspecto de líder)
- `"Aprendí a cazar antes que a leer; el monte no perdona el apuro."` (aspecto de tirador rural)
- `"No le debo nada a la Confederación, pero le debo todo a los muchachos de mi escuadra."` (aspecto de lealtad fracturada)

La primera ola de prefirió el formato corto porque encaja mejor con el resto del sistema de tags (kebab-case, query-friendly, inverted-index-friendly) y porque el efecto mecánico embebido en mini-frase ya cubre la función operacional del aspecto sin necesidad de la frase larga.

### 17.4. Próxima ola especulativa — aspectos largos como segunda capa

Queda apuntada (sin implementación ni reserva de categoría) una posible **segunda capa** de aspectos largos al estilo H.I.T.O.S./Cultos clásico, que viviría junto a la capa corta sin desplazarla. Podría modelarse como `categoria: aspecto_largo` o como un subcampo de cada `aspecto` corto. Decisión deferida hasta que aparezca un caso de uso narrativo que la justifique. Si llega, su consumo natural sería el motor narrativo (no el de batalla), invocando la frase como modificador situacional discrecional.

---

*Fuentes canónicas referenciadas (no copiadas):*

- `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md` — esquema y matriz de stats por rango.
- `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md` — pools de perks y complicaciones (estos últimos migrados como traits con polaridad negativa).
- `/Dev/syv-battle-game-system/lore/universo.md` — descriptores de facción usados como contexto del LLM.
- `/Dev/syv-battle-game-system/personajes/` — 22 fichas canon base que alimentan los mocks (regenerados al schema y normalizados).
- `https://github.com/kodexArg/syv-game-system/blob/main/arquitectura/esquemas/personaje.schema.json` — schema público de referencia.
