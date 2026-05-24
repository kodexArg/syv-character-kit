# PRD — syv-character-kit

> **Documento vivo.** Define el contrato de producto de la API generadora de personajes del universo *Subordinación y Valor* (SyV). No contiene decisiones de arquitectura, almacenamiento ni stack — solo el QUÉ.
>
> **Versión**: 0.1.0 (MVP)
> **Idioma**: castellano rioplatense.
> **Convención de identificadores en payloads JSON/YAML**: `snake_case_castellano` (consistente con `faccion`, `atributos`, `aspectos`, `estado_salud`, `fza_aportada` ya usados en `/Dev/syv-battle-game-system/`).

---

## 1. Visión del producto

`syv-character-kit` es una API HTTP que entrega fichas de personaje canónicas del universo SyV bajo demanda. Cada llamada produce un personaje listo para ser consumido por el motor de batalla, por herramientas de narrativa o por interfaces de exploración del universo. Los personajes pueden ser efímeros (generados al vuelo) o canonizados (persistidos como parte del corpus oficial). El producto encapsula la fidelidad al canon de SyV: reglamento de combate, lore, nomenclatura de roles, distribución estadística y voz narrativa.

## 2. Problema y oportunidad

El ecosistema SyV está repartido en tres repositorios con responsabilidades distintas (`syv` — sitio público del universo; `syv-game-system` — esquemas formales y reglas abstractas; `syv-battle-game-system` — reglamento de combate y fichas vivas). Cada producto que necesita personajes los inventa por su cuenta o copia fichas manualmente. Esto fragmenta el canon, multiplica errores de tono y desactualiza fichas cuando el reglamento evoluciona.

`syv-character-kit` resuelve esto siendo **la fuente única de personajes** para todo el ecosistema. Concentra las tablas curadas (nombres, conceptos, perks, complicaciones, equipamiento), aplica la matriz determinística de stats por rol, y delega a un modelo generativo solo la prosa de la historia personal — anclada en lore. Cualquier consumidor pide un personaje y recibe una ficha que es válida contra el reglamento y consistente con el universo.

## 3. Usuarios y consumidores previstos

La API no tiene UI propia: sus clientes son otros componentes del ecosistema SyV.

- **Motor de batalla** (`syv-battle-game-system` o sucesor): pide escuadras completas para escenarios de prueba o partidas reales.
- **Generador de escenarios y aventuras**: pide PNJs y antagonistas con tono y stats coherentes al sector geográfico solicitado.
- **Sitio público de lore** (`syv`): muestra galerías de personajes canónicos y permite "tirar un personaje al azar" como herramienta de inmersión para lectores.
- **Herramientas narrativas internas**: redactores que necesitan inspiración para conscriptos secundarios, milicianos sin nombre, oficiales de relleno.
- **Pipelines de QA del reglamento**: tests que ejercitan el motor contra una población estadísticamente representativa de personajes para detectar desbalances.

## 4. Principios de diseño

- **Stats determinísticos por rol, narrativa sorteada.** Los atributos (FIS/TAC/MEN), `fza_aportada`, `armor`, `tag_rol` y la categoría de armas se derivan de una matriz fija por rol+facción. Nombre, concepto, perk fijo, complicación fija, arma concreta e historia se sortean.
- **Reproducibilidad por semilla.** Toda llamada admite `?seed=<string>`. La misma tripleta `(seed, rol, faccion)` produce el mismo personaje en cada invocación, incluida la prosa generada por LLM.
- **Fidelidad al canon de `syv-game-system` y `syv-battle-game-system`.** El esquema, el rango de atributos, la composición de escuadra, los pools de perks/complicaciones y los nombres de roles vienen de archivos versionados — no se inventan ni se mutan en código de la API.
- **Workers AI solo para prosa.** El modelo generativo se usa exclusivamente para producir el campo `historia`. Stats, nombre, perk y complicación nunca pasan por un LLM.
- **Mock canónico separado de generación dinámica.** Los 22 personajes iniciales son fixtures versionadas, no salida del generador. Quien pida `/character/{id}` para un mock recibe siempre la misma ficha curada a mano.
- **El PRD es contrato; el repo es implementación.** Este documento define formas y reglas. Cómo se almacenan tablas, dónde corre el LLM, qué binding usa el endpoint de persistencia — fuera de scope hasta que el PRD esté firme.

## 5. Casos de uso

Cada caso describe una intención del consumidor, no un endpoint. La sección 9 mapea casos a endpoints.

| # | Como… | Quiero… | Para… |
|---|---|---|---|
| UC-01 | motor de batalla | pedir un personaje al azar sin restricciones | rellenar un slot vacío en un escenario de prueba |
| UC-02 | generador de escenarios | pedir un personaje filtrando por facción | poblar una escuadra de Ejército Rojo en un escenario rojo-vs-rojo |
| UC-03 | sitio de lore | pedir un personaje filtrando por rol | mostrar "un sargento confederado típico" en una galería temática |
| UC-04 | redactor narrativo | pedir un personaje filtrando por facción y rol | tener un Camarada Puntero específico para un cuento |
| UC-05 | motor de batalla | pedir un personaje exacto por id | recargar el Sargento Walter Aguirre en una continuación de campaña |
| UC-06 | redactor | regenerar el mismo personaje con la misma seed | discutir variantes sin perder el original |
| UC-07 | curador de canon | canonizar un personaje generado que vale la pena conservar | que pase a ser parte del corpus permanente del universo |
| UC-08 | herramienta de QA | listar todos los mock | correr el motor sobre la población canon completa y medir resultados |
| UC-09 | cualquier cliente | consultar el catálogo de roles, facciones, perks y complicaciones que la API entiende | construir UIs de selección sin hardcodear enums |

## 6. JSON canónico del personaje

Sección central del PRD. Define la forma exacta del recurso `personaje` que la API devuelve.

### 6.1. Esquema (vista en YAML legible)

```yaml
personaje:
  id: string                          # estable solo para mocks y canonizados; null para efímeros
  version_canon: string               # versión del corpus canónico contra el que se generó (ej. "0.1.0")
  origen: enum                        # "mock" | "generado" | "canonizado"
  semilla: string                     # seed que produjo esta ficha; siempre presente (también auto-generada si no se pasó)

  nombre: string                      # nombre completo, ej. "Sargento Walter Aguirre"
  faccion: enum                       # "Confederación" | "Ejército Rojo" (otras 3 fuera de MVP)
  rol: string                         # denominación narrativa, ej. "Líder de escuadra (Sargento)"
  rol_id: enum                        # identificador mecánico del rol (ver tabla 7.2)
  tag_rol: array<string>              # tags mecánicos asignados por rol, ej. ["líder", "sargento"]

  atributos:
    fis: integer                      # 2..5 (hasta 7 para líderes en mental, ver reglamento)
    tac: integer                      # 2..5
    men: integer                      # 2..7

  aspectos:
    concepto: string                  # frase narrativa breve, identidad nuclear del personaje
    perk_fijo:
      id: string                      # referencia al pool canon de perks (ej. "p03_voz_de_mando")
      nombre: string                  # nombre legible
      descripcion: string             # condición + efecto, copiado del pool
    complicacion_fija:
      id: string                      # referencia al pool canon de complicaciones
      nombre: string
      descripcion: string

  equipo:
    armor: integer                    # 0..3, derivado de rol (ver tabla 7.6)

  armas:                              # 1..2 armas
    - nombre: string                  # ej. "Fusil FAL"
      categoria_alcance: enum         # "corta" | "media" | "larga"
      nota: string | null             # detalle opcional, ej. "con óptica 4x"

  fza_aportada: integer               # 1..3, derivado de rol

  historia: string                    # 120-200 palabras, prosa generada anclada en lore

  estado_salud: enum                  # siempre "activo" en creación; "herido" | "baja" reservados para runtime de batalla
  tags_iniciales: array<string>       # en creación, igual a tag_rol (sin lesiones previas)

  metadatos:
    creado_en: string                 # ISO-8601
    modelo_prosa: string | null       # identificador del modelo LLM que escribió la historia (null en mocks)
    es_canon: boolean                 # true para mock y canonizados, false para efímeros
```

### 6.2. Notas de campo (lo no obvio)

- **`id`**: para mocks tiene forma `mock.{faccion_slug}.{nn}.{apellido_slug}` (ej. `mock.confederacion.01.aguirre`). Para canonizados, `canon.{ulid}`. Para efímeros, `null`.
- **`version_canon`**: permite a consumidores saber contra qué snapshot de pools y tablas se generó la ficha. Útil cuando el reglamento agrega perks o cambia stats por rol.
- **`semilla`**: si el cliente no la pasa, la API genera una y la devuelve. Esto garantiza que UC-06 funcione siempre (cualquier ficha es regenerable).
- **`rol_id`**: identificador estable independiente del nombre narrativo. Permite que "Sargento" (Confederación) y "Camarada Puntero" (Ejército Rojo) compartan `rol_id: lider_escuadra` y por lo tanto compartan stats y `tag_rol`.
- **`aspectos.perk_fijo` y `aspectos.complicacion_fija`**: estructuras completas (id + nombre + descripción) para que el consumidor no tenga que resolver una referencia contra el pool por separado. La fuente de verdad de los pools sigue siendo `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md`.
- **`armas[].nota`**: campo opcional para variaciones narrativas (óptica, captura, modificación artesanal) sin contaminar el campo `nombre`.
- **`estado_salud` en creación**: siempre `"activo"`. Existe en el payload para que la ficha sea compatible con el motor de batalla sin necesidad de transformación. Estados `"herido"` y `"baja"` los inyecta el motor en runtime; nunca los emite el generador.
- **`metadatos.modelo_prosa`**: trazabilidad de qué modelo generó la prosa. Necesario para auditar drift narrativo cuando se actualice el modelo.

### 6.3. Ejemplo 1 — Confederado

```yaml
personaje:
  id: mock.confederacion.01.aguirre
  version_canon: "0.1.0"
  origen: mock
  semilla: mock-fixed-01

  nombre: Sargento Walter Aguirre
  faccion: Confederación
  rol: Líder de escuadra (Sargento)
  rol_id: lider_escuadra
  tag_rol: [líder, sargento]

  atributos:
    fis: 3
    tac: 5
    men: 7

  aspectos:
    concepto: "Cabo Primero ascendido a la fuerza tras sobrevivir al Sector 12,15."
    perk_fijo:
      id: p_custom_sucesor_de_ricardo
      nombre: Sucesor de Ricardo
      descripcion: >
        Cuando la escuadra no tiene líder funcional y debe actuar sin órdenes
        del HQ, tirada de MEN favorable para cualquier chequeo de mando o iniciativa.
    complicacion_fija:
      id: c_custom_eco_del_penasco
      nombre: Eco del peñasco
      descripcion: >
        Cuando un aliado cae por fuego enemigo en la misma ronda, la ronda
        siguiente la tirada de MEN para chequeos de moral o mando es desfavorable.

  equipo:
    armor: 1

  armas:
    - nombre: Fusil FAL
      categoria_alcance: media
      nota: "con óptica 4x"
    - nombre: Pistola reglamentaria M9
      categoria_alcance: corta
      nota: null

  fza_aportada: 2

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

  estado_salud: activo
  tags_iniciales: [líder, sargento]

  metadatos:
    creado_en: "2026-05-23T00:00:00Z"
    modelo_prosa: null
    es_canon: true
```

### 6.4. Ejemplo 2 — Ejército Rojo

```yaml
personaje:
  id: mock.ejercito_rojo.01.mansilla
  version_canon: "0.1.0"
  origen: mock
  semilla: mock-fixed-12

  nombre: Camarada Puntero Ramón Mansilla
  faccion: Ejército Rojo
  rol: Camarada Puntero (Líder de escuadra)
  rol_id: lider_escuadra
  tag_rol: [líder, sargento]

  atributos:
    fis: 3
    tac: 5
    men: 7

  aspectos:
    concepto: "Comisario político devenido comandante de campo por necesidad orgánica."
    perk_fijo:
      id: p03_voz_de_mando
      nombre: Voz de mando
      descripcion: >
        Mientras el líder está activo en la escuadra, todos los compañeros
        usan el MEN del líder en chequeos de MENTAL.
    complicacion_fija:
      id: c06_obstinado
      nombre: Obstinado
      descripcion: >
        Si se emite una orden que implique retroceder o ceder posición,
        tirada de MEN desfavorable para obedecer.

  equipo:
    armor: 1

  armas:
    - nombre: Subfusil Halcón
      categoria_alcance: corta
      nota: null
    - nombre: Pistola Browning
      categoria_alcance: corta
      nota: "capturada al enemigo"

  fza_aportada: 2

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

  estado_salud: activo
  tags_iniciales: [líder, sargento]

  metadatos:
    creado_en: "2026-05-23T00:00:00Z"
    modelo_prosa: null
    es_canon: true
```

---

## 7. Reglas de generación

Cómo se completa cada campo en un personaje **generado dinámicamente**. Los mocks ignoran estas reglas: vienen escritos a mano.

### 7.1. Inputs y orden de resolución

El cliente pasa hasta tres parámetros: `faccion`, `rol_id`, `seed`. Si falta alguno, se sortea desde la semilla. El orden de resolución es:

1. Resolver `seed` (si no vino, generar uno aleatorio criptográfico y devolverlo en la respuesta).
2. Inicializar PRNG determinístico con `seed`.
3. Resolver `faccion` (input o sorteo uniforme entre las 2 facciones MVP).
4. Resolver `rol_id` (input o sorteo según distribución de escuadra: ver 7.2).
5. Derivar campos determinísticos (atributos, tag_rol, fza_aportada, armor, categoría de armas).
6. Sortear campos narrativos (nombre, concepto, perk_fijo, complicacion_fija, arma concreta).
7. Generar historia con LLM, anclada en facción + rol + concepto + perk + complicación.

### 7.2. Atributos, `tag_rol` y `fza_aportada` (determinísticos)

Tabla canónica tomada de `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md`. **No se sortean.**

| `rol_id` | Rol (Confederación) | Rol (Ejército Rojo) | FIS | TAC | MEN | FZA | `tag_rol` |
|---|---|---|---|---|---|---|---|
| `lider_escuadra` | Sargento | Camarada Puntero | 3 | 5 | 7 | 2 | `[líder, sargento]` |
| `segundo_mando` | Cabo Primero | Segundo Camarada | 3 | 5 | 6 | 2 | `[líder]` |
| `apuntador` | Apuntador (Cabo especialista) | Tirador | 3 | 5 | 5 | 2 | `[apuntador]` |
| `artillero` | Artillero FAP | Ametrallador | 3 | 4 | 3 | 2 | `[artillero]` |
| `fusilero` | Fusilero / Soldado de Primera | Miliciano Veterano | 3 | 3 | 3 | 1 | `[infantería]` |
| `recluta` | Recluta / Soldado de Segunda | Voluntario | 3 | 2 | 2 | 1 | `[recargador]` |

**Distribución por escuadra de 11**: 1 líder + 1 segundo + 1 apuntador + 1 artillero + 4 fusileros + 3 reclutas. FZA total: 15.

**Política de sorteo de rol cuando el cliente no lo fija**: probabilidad proporcional a la composición de escuadra (la API tiende a entregar fusileros/reclutas, lo cual es realista).

### 7.3. `nombre` (sorteo de tablas curadas por facción)

Tabla curada de nombres argentinos, segmentada por facción. Vive en YAML versionado dentro del repo (no se documenta acá la tabla completa).

- **Confederación**: tono militar formal, gentilicios del centro/norte y cuyo (Córdoba, Mendoza, Neuquén, Buenos Aires), apellidos hispano-criollos. Ejemplos canon en uso: *Aguirre, Sosa, Quiroga, Funes, Rodríguez, Olivares, Acosta, Pereyra, Méndez, Lugones, Ramírez*.
- **Ejército Rojo**: tono obrero/patagónico, apellidos con presencia mapuche y de la costa sur (Bahía Blanca, Stroeder, Comodoro, Bariloche). Ejemplos canon en uso: *Mansilla, Iturra, Antinao, Calfucura, Cárcamo, Paine, Soriano, Belenchini, Bordón, Maturana, Bordagaray*.

Los nombres del pool **excluyen** los 22 ya canonizados para evitar duplicados con mocks. La fuente curada se mantiene a mano por el equipo de narrativa.

El prefijo de rol (ej. "Sargento", "Camarada Puntero", "Miliciano Veterano") se prepone determinísticamente según `rol_id` + `faccion`.

### 7.4. `aspectos.concepto`

Frase narrativa breve (10–20 palabras) que define la identidad nuclear del personaje. Dos estrategias posibles, **el PRD recomienda la primera**:

- **Recomendado**: tabla curada de ~60–100 conceptos por facción, sorteada por la PRNG. Determinismo perfecto, control narrativo total, costo cero en runtime.
- **Alternativa rechazada para MVP**: generación AI con prompt acotado. Introduce dependencia de LLM en un campo que también determina downstream el contenido de `historia`, lo cual encadena dos llamadas LLM y dificulta la reproducibilidad por seed.

Decisión: **tabla curada**. La opción AI queda como evolución posible si la tabla se siente repetitiva en producción.

### 7.5. `aspectos.perk_fijo` y `aspectos.complicacion_fija`

Sorteo uniforme sobre los pools canon definidos en `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md` (12 perks, 10 complicaciones a la fecha del MVP). El PRD no replica los pools: los referencia. La API expone su snapshot vigente vía `GET /meta/perks` y `GET /meta/complications`.

Restricciones opcionales sugeridas (a confirmar — ver Open Questions):

- Algunos perks son inherentes a un rol (ej. `Voz de mando` solo tiene sentido en líderes). Una capa de filtro `perks_compatibles_por_rol_id` podría aplicarse antes del sorteo.

### 7.6. `equipo.armor`

Tabla determinística propuesta por el PRD (a validar con el reglamento):

| `rol_id` | armor |
|---|---|
| `lider_escuadra` | 1 |
| `segundo_mando` | 1 |
| `apuntador` | 1 |
| `artillero` | 0 (cargado de FAP, sin chaleco) |
| `fusilero` | 0 |
| `recluta` | 0 |

Los Confederados aplican esta tabla tal cual. El Ejército Rojo aplica la misma tabla con `armor` máximo 1: doctrina anti-equipamiento pesado.

### 7.7. `armas`

Tabla curada por `rol_id` × `faccion`. Cada celda contiene 1–2 armas + un pool de variantes opcionales.

| `rol_id` | Confederación (default) | Ejército Rojo (default) |
|---|---|---|
| `lider_escuadra` | Fusil FAL + Pistola reglamentaria | Subfusil Halcón + Pistola capturada |
| `segundo_mando` | Fusil FAL + Pistola reglamentaria | Subfusil o Fusil ligero + Pistola |
| `apuntador` | Fusil de precisión (larga) | Fusil de cerrojo Mauser (larga) |
| `artillero` | FAP (media) | Ametralladora ligera (media) |
| `fusilero` | Fusil FAL (corta/media) | Fusil de cerrojo Mauser (larga) o subfusil (corta) |
| `recluta` | Fusil FAL (corta) | Lo que haya disponible (corta o larga) |

La categoría de alcance es determinística por entrada de tabla; el nombre exacto y la `nota` se sortean dentro de las variantes definidas para esa celda.

### 7.8. `historia` (Workers AI)

Prosa de 120–200 palabras. Generada por un modelo de Workers AI con un prompt que recibe como contexto:

- `faccion` (con su descriptor de lore — Confederación o Ejército Rojo, según texto de `/Dev/syv-battle-game-system/lore/universo.md`).
- `rol` narrativo + `concepto`.
- `perk_fijo.nombre` y `complicacion_fija.nombre`.
- Nombre del personaje (para que la prosa lo nombre correctamente).
- Instrucción de tono: militar, austero, sin marketing, sin épica fácil, voz rioplatense, 2–3 párrafos.

Para mantener reproducibilidad bajo `?seed=`, la API:

1. Computa una clave de cache = `hash(seed + version_canon + version_modelo + campos_de_input)`.
2. Si la clave existe en cache, retorna la prosa cacheada.
3. Si no, llama al modelo con `temperature` fija y `seed` derivada de la clave, persiste el resultado y lo retorna.

### 7.9. `tags_iniciales` y `estado_salud`

- `tags_iniciales` = copia de `tag_rol` (en creación no hay lesiones previas).
- `estado_salud` = `"activo"` (constante en creación).

### 7.10. `version_canon`

Cadena versionada del corpus (pools de perks/complicaciones + tablas de nombres + matriz de atributos). Se incrementa cuando cambia cualquiera de esas tres fuentes. Toda ficha emitida lleva la `version_canon` con la que se generó.

---

## 8. Reproducibilidad y semilla

- Toda llamada de generación admite `?seed=<string>`.
- Si no se pasa, la API genera uno (formato sugerido: ULID en minúsculas) y lo retorna en `personaje.semilla`.
- La PRNG es determinística (no `Math.random()`): la misma `seed` produce la misma secuencia de decisiones.
- La historia generada por LLM se cachea por clave `(seed, version_canon, version_modelo, inputs)` para que repetir la llamada con la misma semilla devuelva exactamente la misma prosa.
- Cambiar `version_canon` o `version_modelo` **invalida** la cache deliberadamente: la ficha con la misma seed bajo distinto canon es legítimamente distinta.
- Garantía contractual: con `(seed, faccion, rol_id)` fijos y `version_canon` + `version_modelo` fijos, la respuesta es byte-a-byte equivalente excepto `metadatos.creado_en`.

---

## 9. Endpoints (alto nivel)

Cada entrada describe la intención y el shape de la respuesta, no la implementación.

### `GET /character`

Genera un personaje dinámico. Parámetros opcionales:

- `faccion`: `confederacion` | `ejercito_rojo`
- `rol_id`: uno de los 6 (ver 7.2)
- `seed`: string libre

Devuelve un objeto `personaje` con `origen: "generado"` y `metadatos.es_canon: false`.

Mapea: UC-01, UC-02, UC-03, UC-04, UC-06.

### `GET /character/{id}`

Devuelve el personaje con id exacto. Funciona para mocks (`mock.*`) y canonizados (`canon.*`). Devuelve 404 si el id no existe.

Mapea: UC-05.

### `GET /roster/mock`

Lista los 22 fixtures con `id`, `nombre`, `faccion`, `rol_id`, `rol`. Sin payload completo (eso requiere `/character/{id}`).

Mapea: UC-08.

### `POST /canonize`

Toma un personaje generado (vía `id` efímero firmado o vía body con la ficha completa + seed) y lo persiste como canon. Asigna `id` estable, cambia `origen` a `"canonizado"`, marca `metadatos.es_canon: true`. Requiere capacidad de almacenamiento persistente; el efecto secundario opcional de abrir un PR al repo de fichas `/Dev/syv-battle-game-system/personajes/{faccion}/` queda fuera del MVP (ver Open Questions).

Mapea: UC-07.

### `GET /meta/factions`

Devuelve el catálogo de facciones reconocidas por la API, con su descriptor de lore corto.

### `GET /meta/roles`

Devuelve los 6 `rol_id` con su tabla de stats, `tag_rol`, `fza_aportada`, `armor` y nombres narrativos por facción.

### `GET /meta/perks` y `GET /meta/complications`

Devuelven el pool canon vigente. Cada entrada incluye `id`, `nombre`, `condicion`, `efecto` y opcionalmente `compatible_con_rol_id` (si se implementa la restricción de 7.5).

Mapea: UC-09 para los cuatro `/meta/*`.

---

## 10. Los 22 mock — alcance del MVP

Los 22 personajes iniciales son fixtures versionadas en `mock/personajes/{faccion}/{nn}_{rol}_{apellido}.yaml`. Su contenido completo (stats, perk fijo, complicación fija, historia) ya existe en formato Markdown en `/Dev/syv-battle-game-system/personajes/`; el MVP de `syv-character-kit` los **importa y convierte** al schema JSON canónico definido en sección 6.

Esta tabla fija el contrato de existencia. La materialización completa de cada YAML (transcripción 1:1 desde el Markdown canon a YAML) ocurre en una iteración posterior al PRD.

### 10.1. Escuadra Confederación (11)

| # | `id` | Rol | `rol_id` | Nombre canon |
|---|---|---|---|---|
| 01 | `mock.confederacion.01.aguirre` | Sargento | `lider_escuadra` | Sargento Walter Aguirre |
| 02 | `mock.confederacion.02.sosa` | Cabo Primero | `segundo_mando` | Cabo Primero Sosa |
| 03 | `mock.confederacion.03.quiroga` | Apuntador | `apuntador` | Apuntador Quiroga |
| 04 | `mock.confederacion.04.funes` | Artillero FAP | `artillero` | Artillero Funes |
| 05 | `mock.confederacion.05.rodriguez` | Fusilero | `fusilero` | Soldado de Primera Marcela Rodríguez |
| 06 | `mock.confederacion.06.olivares` | Fusilero | `fusilero` | Soldado de Primera Olivares |
| 07 | `mock.confederacion.07.acosta` | Fusilero | `fusilero` | Soldado de Primera Acosta |
| 08 | `mock.confederacion.08.pereyra` | Fusilero | `fusilero` | Soldado de Primera Pereyra |
| 09 | `mock.confederacion.09.mendez` | Recluta | `recluta` | Recluta Méndez |
| 10 | `mock.confederacion.10.lugones` | Recluta | `recluta` | Recluta Lugones |
| 11 | `mock.confederacion.11.ramirez` | Recluta | `recluta` | Recluta Ramírez |

### 10.2. Escuadra Ejército Rojo (11)

| # | `id` | Rol | `rol_id` | Nombre canon |
|---|---|---|---|---|
| 12 | `mock.ejercito_rojo.01.mansilla` | Camarada Puntero | `lider_escuadra` | Camarada Puntero Ramón Mansilla |
| 13 | `mock.ejercito_rojo.02.iturra` | Segundo Camarada | `segundo_mando` | Segundo Camarada Iturra |
| 14 | `mock.ejercito_rojo.03.antinao` | Tirador | `apuntador` | Tirador Antinao |
| 15 | `mock.ejercito_rojo.04.calfucura` | Ametrallador | `artillero` | Ametrallador Calfucurá |
| 16 | `mock.ejercito_rojo.05.carcamo` | Miliciano Veterano | `fusilero` | Miliciano Veterano Fermín Cárcamo |
| 17 | `mock.ejercito_rojo.06.paine` | Miliciano Veterano | `fusilero` | Miliciano Veterano Paine |
| 18 | `mock.ejercito_rojo.07.soriano` | Miliciano Veterano | `fusilero` | Miliciano Veterano Soriano |
| 19 | `mock.ejercito_rojo.08.belenchini` | Miliciano Veterano | `fusilero` | Miliciano Veterano Belenchini |
| 20 | `mock.ejercito_rojo.09.bordon` | Voluntario | `recluta` | Voluntario Bordón |
| 21 | `mock.ejercito_rojo.10.maturana` | Voluntario | `recluta` | Voluntario Maturana |
| 22 | `mock.ejercito_rojo.11.bordagaray` | Voluntario | `recluta` | Voluntario Bordagaray |

**Nota sobre composición.** El reglamento local (`/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md`) y los 22 personajes ya escritos definen la escuadra como **1 + 1 + 1 + 1 + 4 + 3**. El briefing inicial mencionó una composición alternativa (1 sargento + 1 cabo primero + 1 cabo especialista + 1 dragoneante + 2 soldados 1ª + 5 soldados 2ª); el PRD adopta la composición que **ya existe en el canon** porque ese es el corpus que la API debe servir. Si se quiere migrar a otra composición, primero se cambia el reglamento, después el PRD se actualiza, después se regenera el set de mocks.

---

## 11. Alcance MVP vs futuro

### Dentro de v1

- 2 facciones jugables: Confederación y Ejército Rojo.
- 6 `rol_id` con su matriz determinística de stats / tags / FZA / armor.
- Pools canon de perks (12) y complicaciones (10) tomados del reglamento local.
- Tablas curadas de nombres, conceptos y armas por facción.
- Generación con seed reproducible.
- 22 mocks importados y servibles por `/character/{id}` y `/roster/mock`.
- Endpoint de canonización con persistencia básica.
- Endpoints `/meta/*` para introspección del canon.

### Explícitamente fuera de v1

- Las 3 facciones secundarias (Pueblos del Pantano, Los Salvajes, Los Poseídos): existen en lore, no se generan ni se sirven.
- Perks de batalla y complicaciones temporales (son del motor de batalla, no del generador).
- Modificadores de progresión (+1 atributo por triple-0): runtime, no creación.
- Sistema de hexágonos, mapa, escenarios.
- Autenticación, autorización, rate limiting, cuotas.
- UI propia (la API es headless).
- Generación de escuadras completas en una sola llamada (se compone en cliente con N llamadas filtradas por `rol_id`).
- Edición de personajes canonizados (alta sí, modificación no).
- Internacionalización (todo en español).

---

## 12. Open questions

Preguntas reales que el PRD no resuelve y quedan abiertas para la próxima iteración:

1. **`/canonize` y el repo de fichas**: ¿la canonización solo persiste en almacenamiento de la API, o además abre automáticamente un PR a `/Dev/syv-battle-game-system/personajes/{faccion}/`? Si abre PR, ¿con qué credenciales actúa la API y cómo se nombra la rama?
2. **Historia en canonizados**: cuando un personaje pasa de efímero a canonizado, ¿se congela la prosa generada por LLM como parte permanente del id, o se regenera al vuelo cada vez que se pide (con riesgo de drift si cambia el modelo)?
3. **Versionado del canon de pools**: si el reglamento agrega un perk o cambia el efecto de uno existente, ¿cómo se versiona el corpus? ¿Las fichas viejas mantienen su `version_canon` original o se "migran" al nuevo?
4. **Restricción de perks por rol**: ¿algunos perks (`Voz de mando`, `Recarga rápida`) deben filtrarse para que solo aparezcan en el `rol_id` que tiene sentido, o se permite que cualquier perk caiga en cualquier rol y queda como sabor narrativo?
5. **Modelo de Workers AI**: ¿qué modelo concreto se usa para `historia` (Llama 3.x, Mistral, otro), con qué temperatura, y bajo qué presupuesto de tokens por llamada? El PRD asume su existencia; la elección es operacional.
6. **Nombres y géneros**: la tabla curada de nombres ¿incluye género explícito (femenino, masculino, no-binario) y la API permite filtrar por género? Hoy el canon tiene mezcla (Marcela Rodríguez, Walter Aguirre) sin convención fija.
7. **Anti-duplicación de nombres**: la sección 7.3 dice que el pool excluye los 22 canon. ¿Pero el pool excluye también los canonizados nuevos a medida que se acumulan? Si sí, ¿hay un punto en que el pool se agota?
8. **Idempotencia de `POST /canonize`**: si se canoniza dos veces el mismo personaje generado (misma seed, mismos inputs), ¿se crea un canon nuevo o se devuelve el id del primero?

---

*Fuentes canónicas referenciadas (no copiadas):*

- `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md` — esquema y matriz de stats por rol.
- `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md` — pools de perks y complicaciones.
- `/Dev/syv-battle-game-system/lore/universo.md` — descriptores de facción usados como contexto del LLM.
- `/Dev/syv-battle-game-system/personajes/` — 22 fichas canon que alimentan los mocks.
- `https://github.com/kodexArg/syv-game-system/blob/main/arquitectura/esquemas/personaje.schema.json` — schema público de referencia.
