# PRD — syv-character-kit

> **Documento vivo.** Define el contrato de producto de la API generadora de personajes del universo *Subordinación y Valor* (SyV). No contiene decisiones de arquitectura, almacenamiento ni stack — solo el QUÉ.
>
> **Versión**: 0.2.2
> **Reemplaza**: 0.2.1
> **Idioma**: castellano rioplatense, voseo sobrio.
> **Convención de identificadores en payloads JSON/YAML**: `snake_case_castellano` (consistente con `faccion`, `atributos`, `aspectos`, `estado_salud`, `fza_aportada` ya usados en `/Dev/syv-battle-game-system/`).

---

## 0. Changelog

### v0.2.2

Patch incremental sobre v0.2.1. Introduce tres cambios estructurales al schema:

- **Identidad nominal desdoblada**: `nombre` pasa a ser el nombre real del personaje; se agrega `nombre_de_campo` (el apodo o título operativo) como campo independiente opcional, y `especialidad` para facciones que componen el título a partir del rol (Ejército Rojo). Para Confederación, `especialidad` es `null` por defecto.
- **Mando desacoplado del rol**: se agrega el enum `mando` (`titular` | `suplente` | `no_apto`) que registra la jerarquía vigente de forma independiente de `rol_id`. Cambiar `mando` no toca atributos ni equipamiento. El `rol_id` sigue definiendo stats y armas únicamente en creación.
- **Sistema híbrido tags + campos**: el bloque `apariencia` desaparece — su contenido migra a tags con `categoria: rasgo`. El inventario (`armas[]`, `equipo_tactico[]`) también desaparece del bloque `equipo` y pasa a tags con `categoria: equipo`. El campo `equipo.armor` (entero 0–3) es el único campo escalar que queda en `equipo`. Se agrega el bloque `tags: [{categoria, valor}]` al top level. `tag_rol` se elimina como campo separado; sus valores migran a tags con `categoria: rol`. `tags_iniciales` se redefine como snapshot de la lista `tags` completa al momento de creación (no solo los tags de rol).

**Breaking changes vs v0.2.1**: eliminados `apariencia` (bloque completo), `equipo.armas[]`, `equipo.equipo_tactico[]`, `tag_rol`; agregados `nombre_de_campo`, `especialidad`, `mando`, `tags[]`.

### v0.2.1

Patch incremental sobre v0.2.0. Cierra cuatro *open questions* que habían quedado abiertas: **OQ#1** (edad), **OQ#3** (límite del historial), **OQ#5** (mutabilidad de atributos al cambiar de rol_id), y **OQ#7** (idempotencia de `POST /canonize`). Como resultado de OQ#1, se eliminan del vocabulario de hitos los tipos `cumpleanos` y `paso_del_tiempo`. Se clarifica taxativamente que los atributos `{fis, tac, men}` son propiedad del personaje y no se derivan del rol_id post-creación. Quedan 4 OQs abiertas (renumeradas 1–4 en sección 14).

### v0.2.0

Esta versión cierra las cuatro *open questions* abiertas en v0.1.0 y, sobre esas decisiones, introduce un cambio de naturaleza del recurso: el personaje canonizado deja de ser una foto inmutable y pasa a ser una **memoria viva con experiencia**.

**OQ resueltas:**

- **OQ#1 (`/canonize` y el repo de fichas):** la canonización persiste **únicamente** en la base de la API. Nunca toca `/Dev/syv-battle-game-system/personajes/`, nunca abre PRs. Los mocks Markdown del battle-system y los canonizados de la API son **dos universos paralelos**, ambos legítimos, sin sincronización automática.
- **OQ#2 (historia en canonizados):** la prosa generada por LLM **se congela** en el momento de la canonización y queda inmutable. Pasa a formar parte de la identidad del personaje (id). No se regenera nunca, aunque cambie el modelo.
- **OQ#3 (versionado del canon de pools):** **no hay migraciones**. La extensibilidad del schema se resuelve por diseño SOLID y open/close desde el día uno. El campo `version_canon` desaparece del personaje. Filosofía explícita: si el schema necesita una migración, fallamos antes en el diseño que en la operación.
- **OQ#4 (restricción de perks por rol):** restricción **soft** (80/20). El sorteo sesga al ~80% hacia perks naturales del `rol_id` y deja ~20% para perks "de sabor" que crean fricción narrativa intencional.

**Concepto nuevo — memoria viva con experiencia:** un personaje canonizado evoluciona. Acumula batallas, sube atributos, gana cicatrices, rompe lealtades, captura armas, pierde compañeros. La ficha es el estado vigente de una entidad que existe en el tiempo, no una instantánea de su creación. Esto reformula el schema (sección 6), incorpora bloques nuevos (`historial`, `vinculos`, `lealtades` estructuradas) y rompe deliberadamente la reproducibilidad por seed para canonizados tras el primer hito (sección 8).

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

`syv-character-kit` resuelve esto siendo **la fuente única de personajes** del ecosistema. Concentra las tablas curadas (nombres, conceptos, perks, complicaciones, equipamiento), aplica la matriz determinística por rol, delega a un modelo generativo solo la prosa inicial, y — diferencial de esta versión — **administra el ciclo de vida del personaje canonizado**: nace, pelea, cambia, queda registrado.

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
- **Customs libres + enums abiertos como política deliberada.** El producto acepta `perk_fijo` o `complicacion_fija` con `id` `p_custom_*` / `c_custom_*` y descripción en texto libre. Los enums (`tipo` de hito, `tipo` de vínculo, `categoria` de tag, etc.) tienen valores **sugeridos** pero no rechazan otros. **Tensión asumida**: el motor downstream que consuma estos customs tiene que poder interpretarlos (probablemente vía LLM). Ver sección 13.
- **Stats determinísticos por rol, narrativa sorteada.** En creación, los atributos y los campos mecánicos se derivan de una matriz fija por rol. Nombre, concepto, perk, complicación, equipamiento e historia se sortean.
- **Memoria viva como naturaleza del recurso canonizado.** Un canonizado tiene historial y muta. No es un payload; es una entidad. Ver sección 9.
- **Reproducibilidad por seed para efímeros.** Toda creación admite `?seed=`. La misma `(seed, rol, faccion)` produce el mismo personaje, incluida la prosa inicial. **Limitación aceptada**: los canonizados pierden esta propiedad tras el primer hito — su historial los hace únicos.
- **LLM solo para prosa, solo una vez.** El modelo generativo escribe el campo `historia` en el momento de la creación efímera. Si el personaje se canoniza, esa prosa se congela. Después de eso, ninguna llamada a LLM mediada por la API toca al personaje.
- **Mocks separados de canonizados.** Los 22 mocks son fixtures inmutables del battle-system. Los canonizados son entidades vivas de la API. No hay sincronización ni promoción mock → canonizado.
- **El PRD es contrato; el repo es implementación.** Este documento define formas y reglas. Cómo se almacenan tablas, dónde corre el LLM, qué binding usa la persistencia — fuera de scope.

## 5. Casos de uso

| # | Como… | Quiero… | Para… |
|---|---|---|---|
| UC-01 | motor de batalla | pedir un personaje al azar sin restricciones | rellenar un slot vacío en un escenario |
| UC-02 | generador de escenarios | pedir un personaje filtrando por facción | poblar una escuadra de Ejército Rojo |
| UC-03 | sitio de lore | pedir un personaje filtrando por rol | mostrar "un sargento confederado típico" |
| UC-04 | redactor narrativo | pedir un personaje filtrando por facción y rol | tener un Camarada Puntero específico para un cuento |
| UC-05 | motor de batalla | pedir un personaje exacto por id | recargar al Sargento Aguirre en una continuación |
| UC-06 | redactor | regenerar el mismo personaje efímero con la misma seed | discutir variantes sin perder el original |
| UC-07 | curador de canon | canonizar un personaje generado | que pase a ser entidad permanente del corpus de la API |
| UC-08 | herramienta de QA | listar todos los mock | correr el motor sobre la población canon completa |
| UC-09 | cualquier cliente | consultar el catálogo de roles, facciones, perks, complicaciones, tipos de hito | construir UIs sin hardcodear enums |
| UC-10 | motor de batalla | registrar un triple-0 sobre un canonizado | que el +1 al atributo quede reflejado en la ficha vigente |
| UC-11 | redactor | registrar un ascenso narrativo sobre un canonizado | que la próxima `GET` muestre el nuevo rango y el hito |
| UC-12 | motor de batalla | registrar la formación de un vínculo (mentor, hermano de armas) entre dos canonizados | que ambos personajes lo recuerden |
| UC-13 | motor de batalla | registrar la captura de un arma enemiga | que el equipo vigente la incluya |
| UC-14 | redactor | registrar la ruptura de una lealtad | que el personaje pase a tener un secreto o un enemigo jurado |
| UC-15 | sitio de lore | pedir el mismo canonizado en t1 (post-canonización) y t2 (tras 4 hitos) | mostrar evolución visible en la ficha |
| UC-16 | cualquier cliente | pedir la ficha con `?fields=` podada | bajar payload cuando solo le interesa el resumen |
| UC-17 | sitio de lore | pedir el `historial[]` de un canonizado | renderizar una línea de tiempo del personaje |

## 6. JSON canónico del personaje (v0.2.2)

Sección central del PRD. Define la forma del recurso `personaje` que la API devuelve.

El schema es **estricto** en estructura y **abierto** en valores: los campos están definidos, pero los enums admiten valores sugeridos sin rechazar otros, y existe un campo `extras` libre al top level.

### 6.1. Esquema (vista en YAML legible)

```yaml
personaje:
  # ── Identidad estable ──────────────────────────────────────────────────
  id: string                            # estable para mocks y canonizados; null para efímeros
  origen: enum                          # "mock" | "generado" | "canonizado"
  semilla: string                       # seed original que produjo la ficha; siempre presente

  nombre: string                        # nombre real, ej. "Walter Aguirre"
  nombre_de_campo: string | null        # como se lo conoce operativamente, ej. "Sargento Walter Aguirre"
                                        # null si no hay nick/título distinto del nombre real
  edad: integer                         # años, 16..70 sugerido. Integer simple; no hay mecánica de envejecimiento.
                                        # Si envejece, decisión narrativa directa sin hito formal.
  genero: enum                          # "masculino" | "femenino" | "no_binario" | "otro" (abierto)

  faccion: enum                         # "Confederación" | "Ejército Rojo" (otras 3 fuera de MVP)
  rol: string                           # denominación narrativa cultural, ej. "Líder Revolucionario"
  rol_id: enum                          # identificador mecánico (sugerido, ver 7.2; abierto)
                                        # valores canon: lider_escuadra, lider_revolucionario,
                                        # segundo_mando, apuntador, artillero, fusilero, recluta
  especialidad: string | null           # solo en facciones que la usan (Ejército Rojo: "comandancia",
                                        # "medicina", "ingenieria", etc.). Define el título de campo
                                        # cuando aplica. En Confederación siempre null.
  mando: enum                           # "titular" | "suplente" | "no_apto"
                                        # titular   = lidera actualmente la escuadra
                                        # suplente  = elegible pero no lidera actualmente
                                        # no_apto   = no elegible para mando (reclutas, fusileros sin
                                        #             trayectoria de mando)

  origen_geografico:                    # estructurado mínimo
    region: string                      # ej. "Patagonia Norte", "Pampa Húmeda"
    localidad: string                   # ej. "Neuquén", "Bahía Blanca"

  # ── Lealtades (estructuradas completas) ────────────────────────────────
  lealtades:
    primaria: string                    # ej. "Confederación", "Sargento Ricardo (post mortem)"
    secundarias: array<string>          # ej. ["su escuadra", "su provincia natal"]
    secretos: array<string>             # ej. ["recibió pagos del enemigo en 2024"]

  # ── Atributos (set único mutable) ──────────────────────────────────────
  atributos:
    fis: integer                        # 2..5 (techo 5)
    tac: integer                        # 2..5 (techo 5)
    men: integer                        # 2..5; líderes hasta 7

  # ── Aspectos (perk fijo + complicación fija; mutables vía hito) ────────
  aspectos:
    concepto: string                    # frase narrativa breve; mutable vía hito narrativo
    perk_fijo:
      id: string                        # ref al pool canon (ej. "p03_voz_de_mando") o "p_custom_*"
      nombre: string
      descripcion: string               # condición + efecto; texto libre para customs
    complicacion_fija:
      id: string                        # "c*" o "c_custom_*"
      nombre: string
      descripcion: string

  # ── Equipamiento (mutable) ─────────────────────────────────────────────
  equipo:
    armor: integer                      # 0..3 (Ejército Rojo: techo 1 por doctrina)
    # armas e items tácticos viven como tags con categoria: equipo (ver bloque tags)

  fza_aportada: integer                 # 1..3, derivado de rol_id

  # ── Tags (sistema híbrido extensible) ─────────────────────────────────
  tags:
    - categoria: string                 # categoría abierta. Categorías canon previstas:
                                        #   rasgo   → rasgos físicos, cicatrices, apariencia
                                        #   equipo  → armas, munición, accesorios tácticos
                                        #   rol     → etiquetas mecánicas de rol (ej. "lider", "apuntador")
                                        # Otras categorías emergen naturalmente sin tocar el schema.
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
      tipo: string                      # sugerido: triple_cero | ascenso | herida | baja_temporal |
                                        # agregar_tag | quitar_tag | formacion_vinculo | ruptura_vinculo |
                                        # traslado | condecoracion | mejora_atributo | mejora_aspecto |
                                        # cambio_mando (abierto; el motor puede emitir tipos custom)
      descripcion: string
      ref_batalla: string | null        # id de batalla del motor downstream; opcional
      metadata: object                  # libre, open/close (ej. { atributo: "fis", delta: 1 })

  # ── Estado vigente (snapshot de runtime) ───────────────────────────────
  estado_salud: enum                    # "activo" | "herido" | "baja" (siempre "activo" en creación)
  tags_iniciales: array<{categoria, valor}>  # snapshot completo de tags[] al crear; preservado para auditoría

  # ── Metadatos ──────────────────────────────────────────────────────────
  metadatos:
    creado_en: string                   # ISO-8601 (creación efímera)
    canonizado_en: string | null        # ISO-8601 (null para efímeros y mocks)
    ultima_actualizacion: string        # ISO-8601 (igual a creado_en si nunca mutó)
    modelo_prosa: string | null         # identificador del LLM que escribió `historia` (null en mocks)
    es_canon: boolean                   # true para mock y canonizado, false para efímero

  # ── Escape hatch para extensibilidad ───────────────────────────────────
  extras: object | null                 # libre, no validado. Para que consumidores
                                        # adjunten datos sin pedir cambio de schema.
```

**Lo que NO es tag (sigue siendo campo estructurado):** identidad nominal (`nombre`, `nombre_de_campo`, `edad`, `genero`, `origen_geografico`), posicionamiento (`faccion`, `rol`, `rol_id`, `especialidad`, `mando`, `estado_salud`, `fza_aportada`), `atributos`, `lealtades`, `aspectos`, `vinculos`, `historial`, `historia`, `metadatos`. Estos campos tienen semántica mecánica o narrativa precisa que requiere acceso directo sin interpretación de categoría.

### 6.2. Notas de campo (lo no obvio)

- **`id`**: para mocks tiene forma `mock.{faccion_slug}.{nn}.{apellido_slug}` (ej. `mock.confederacion.01.aguirre`). Para canonizados, `canon.{ulid}`. Para efímeros, `null`.
- **`nombre`**: el nombre real del personaje, sin título ni rango. Ej. "Walter Aguirre".
- **`nombre_de_campo`**: cómo se lo conoce operativamente. En Confederación: rango + nombre ("Sargento Walter Aguirre"). En Ejército Rojo: se compone determinísticamente según `especialidad` ({titulo} + {nombre}); si no tiene especialidad, es el título revolucionario + nombre ("Camarada Puntero Ramón Mansilla"). `null` si no hay distinción con el nombre real.
- **`especialidad`**: solo para facciones que usan títulos funcionales (Ejército Rojo). Valores sugeridos: `comandancia`, `medicina`, `ingenieria`, `comisariado`. En Confederación es siempre `null`.
- **`mando`**: registra la jerarquía vigente de forma independiente del `rol_id`. Una escuadra puede tener dos unidades con `rol_id: lider_revolucionario` — una con `mando: titular` y otra con `mando: suplente`. Cambiar `mando` no toca atributos, equipamiento ni ningún otro campo. Modificarlo requiere un hito `cambio_mando` (ver sección 9.5).
- **`rol_id`**: define stats y armas BASE únicamente en el momento de creación. Post-creación es solo una etiqueta identificadora; no regenera atributos.
- **`origen_geografico`**: mínimo estructurado (region + localidad). Si en el futuro se quiere agregar coordenadas o sector militar, va en `extras` o se extiende el sub-objeto sin romper.
- **`lealtades`**: `primaria` es la afiliación nuclear (típicamente la facción, pero puede ser una persona — ver Aguirre con "Sargento Ricardo (post mortem)"). `secretos` permite tensiones narrativas que el motor puede explotar.
- **`atributos`**: un único set **mutable**. Cuando un triple-0 sube `fis`, se **sobreescribe** el valor. La trazabilidad de "cómo llegó al valor actual" vive en `historial[]`, no en campos separados base/actuales/efectivos.
- **`aspectos.perk_fijo` y `aspectos.complicacion_fija`**: estructuras completas (id + nombre + descripción). La hoja siempre trae el set completo denormalizado; el cliente no consulta el pool aparte. Si el id empieza con `p_custom_` / `c_custom_`, el contenido es texto libre y el motor downstream lo interpreta.
- **`equipo.armor`**: único campo escalar del bloque equipo. El resto del inventario (armas, munición, accesorios) vive en `tags` con `categoria: equipo`.
- **`tags`**: lista plana de entidades `{categoria, valor}`. Categorías abiertas. Tags repetibles: `{categoria: equipo, valor: "cargador 9mm"}` puede aparecer tres veces. Cambios en tags se registran como hitos `agregar_tag` / `quitar_tag` con `metadata: {categoria, valor}`.
- **`vinculos[].ref_personaje_id`**: la API **no valida** que el id exista. Esto permite vínculos con personajes que aún no están canonizados, o con NPCs externos. El campo `descripcion` es el fallback obligatorio.
- **`historia`**: prosa biográfica original. En creación efímera la genera el LLM. En la canonización **se congela** y no muta nunca. La biografía posterior (qué le pasó después) se reconstruye desde `historial[]`.
- **`historial[]`**: solo hitos importantes. No es un log detallado de batalla — eso lo lleva el motor en su propio almacenamiento. El historial de la API responde "¿qué cosas le pasaron a este personaje que vale la pena recordar?".
- **`tags_iniciales`**: snapshot completo de la lista `tags[]` al momento de creación, incluyendo todas las categorías (rasgo, equipo, rol, etc.). Preservado para auditoría e inmutable post-creación.
- **`metadatos.modelo_prosa`**: trazabilidad. Útil para auditar drift narrativo y para saber qué generación de modelo está congelada en cada canonizado.
- **`extras`**: escape hatch deliberado. Cualquier consumidor puede adjuntar campos sin pedir cambio de schema. La API no los inspecciona.
- **`version_canon` (ELIMINADO desde v0.2.0)**: el schema no se versiona en el payload; se extiende sin romper.

### 6.3. Ejemplo 1 — Confederado (mock canonizado con historia acumulada)

```yaml
personaje:
  id: mock.confederacion.01.aguirre
  origen: mock
  semilla: mock-fixed-01

  nombre: Walter Aguirre
  nombre_de_campo: Sargento Walter Aguirre
  edad: 28
  genero: masculino

  faccion: Confederación
  rol: Sargento (Líder de escuadra)
  rol_id: lider_escuadra
  especialidad: null
  mando: titular

  origen_geografico:
    region: Patagonia Norte
    localidad: Neuquén

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

  fza_aportada: 2

  tags:
    # rasgo (antes: apariencia)
    - { categoria: rasgo, valor: "altura media" }
    - { categoria: rasgo, valor: "complexion atletica" }
    - { categoria: rasgo, valor: "pelo castaño corto" }
    - { categoria: rasgo, valor: "barba de tres días" }
    - { categoria: rasgo, valor: "mirada que se demora en las cosas" }
    - { categoria: rasgo, valor: "cicatriz vertical sobre ceja izquierda (Sector 12,15)" }
    # equipo (antes: apariencia.armas + equipo_tactico)
    - { categoria: equipo, valor: "Fusil FAL (alcance media)" }
    - { categoria: equipo, valor: "Pistola reglamentaria M9 (alcance corta)" }
    - { categoria: equipo, valor: "prismáticos militares — trofeo del Sector 12,15, lente derecha rajada pero usable" }
    - { categoria: equipo, valor: "cuaderno de campaña — anotaciones de terreno, marcas de Ricardo en las primeras hojas" }
    # rol
    - { categoria: rol, valor: "lider" }
    - { categoria: rol, valor: "sargento" }

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
        rol_id_anterior: segundo_mando
        rol_id_nuevo: lider_escuadra
    - fecha: "2026-04-02T09:00:00Z"
      tipo: agregar_tag
      descripcion: "Recuperó los prismáticos del oficial enemigo abatido en la cresta norte."
      ref_batalla: "batalla_cresta_norte"
      metadata:
        categoria: equipo
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

  estado_salud: activo
  tags_iniciales:
    - { categoria: rasgo, valor: "altura media" }
    - { categoria: rasgo, valor: "complexion atletica" }
    - { categoria: rasgo, valor: "pelo castaño corto" }
    - { categoria: rasgo, valor: "barba de tres días" }
    - { categoria: rasgo, valor: "mirada que se demora en las cosas" }
    - { categoria: equipo, valor: "Fusil FAL (alcance media)" }
    - { categoria: equipo, valor: "Pistola reglamentaria M9 (alcance corta)" }
    - { categoria: equipo, valor: "cuaderno de campaña — anotaciones de terreno, marcas de Ricardo en las primeras hojas" }
    - { categoria: rol, valor: "lider" }
    - { categoria: rol, valor: "sargento" }

  metadatos:
    creado_en: "2026-01-15T00:00:00Z"
    canonizado_en: "2026-01-15T00:00:00Z"
    ultima_actualizacion: "2026-05-10T22:45:00Z"
    modelo_prosa: null
    es_canon: true

  extras: null
```

### 6.4. Ejemplo 2 — Ejército Rojo (mock canonizado con historia acumulada)

```yaml
personaje:
  id: mock.ejercito_rojo.01.mansilla
  origen: mock
  semilla: mock-fixed-12

  nombre: Ramón Mansilla
  nombre_de_campo: Camarada Puntero Ramón Mansilla
  edad: 34
  genero: masculino

  faccion: Ejército Rojo
  rol: Camarada Puntero (Líder de escuadra)
  rol_id: lider_revolucionario
  especialidad: comisariado
  mando: titular

  origen_geografico:
    region: Pampa Bonaerense
    localidad: Bahía Blanca

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

  fza_aportada: 2

  tags:
    # rasgo (antes: apariencia)
    - { categoria: rasgo, valor: "altura alta" }
    - { categoria: rasgo, valor: "complexion delgada" }
    - { categoria: rasgo, valor: "pelo entrecano corto" }
    - { categoria: rasgo, valor: "lentes de armazón fino reforzado con alambre" }
    - { categoria: rasgo, valor: "habla pausada, voz grave" }
    # equipo (antes: armas + equipo_tactico)
    - { categoria: equipo, valor: "Subfusil Halcón (alcance corta)" }
    - { categoria: equipo, valor: "Pistola Browning (alcance corta)" }
    - { categoria: equipo, valor: "cuaderno de notas — anotaciones de campaña y borradores de comunicados" }
    - { categoria: equipo, valor: "brújula de oficial — regalo del instructor de Stroeder" }
    # rol
    - { categoria: rol, valor: "lider" }
    - { categoria: rol, valor: "comisario" }

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

  estado_salud: activo
  tags_iniciales:
    - { categoria: rasgo, valor: "altura alta" }
    - { categoria: rasgo, valor: "complexion delgada" }
    - { categoria: rasgo, valor: "pelo entrecano corto" }
    - { categoria: rasgo, valor: "lentes de armazón fino reforzado con alambre" }
    - { categoria: rasgo, valor: "habla pausada, voz grave" }
    - { categoria: equipo, valor: "Subfusil Halcón (alcance corta)" }
    - { categoria: equipo, valor: "Pistola Browning (alcance corta)" }
    - { categoria: equipo, valor: "cuaderno de notas — anotaciones de campaña y borradores de comunicados" }
    - { categoria: equipo, valor: "brújula de oficial — regalo del instructor de Stroeder" }
    - { categoria: rol, valor: "lider" }
    - { categoria: rol, valor: "comisario" }

  metadatos:
    creado_en: "2026-01-15T00:00:00Z"
    canonizado_en: "2026-01-15T00:00:00Z"
    ultima_actualizacion: "2026-05-03T11:15:00Z"
    modelo_prosa: null
    es_canon: true

  extras: null
```

---

## 7. Reglas de generación dinámica

Cómo se completa cada campo en un personaje **generado dinámicamente** (origen `"generado"`). Los mocks ignoran estas reglas: vienen escritos a mano. Los canonizados nacen como un generado o como un body explícito, y a partir de ahí mutan vía hitos (sección 9).

### 7.1. Inputs y orden de resolución

El cliente pasa hasta tres parámetros: `faccion`, `rol_id`, `seed`. Si falta alguno, se sortea desde la semilla. Orden:

1. Resolver `seed` (si no vino, generar uno criptográfico y devolverlo).
2. Inicializar PRNG determinístico con `seed`.
3. Resolver `faccion` (input o sorteo uniforme entre las 2 facciones MVP).
4. Resolver `rol_id` (input o sorteo según distribución de escuadra: ver 7.2).
5. Derivar campos determinísticos (atributos, fza_aportada, armor, categoría de armas, mando).
6. Sortear campos narrativos (nombre, edad, género, origen geográfico, rasgos, concepto, perk fijo, complicación fija, armas concretas).
7. Componer `nombre_de_campo` determinísticamente (ver 7.3).
8. Inicializar `tags` con pool sorteado de rasgo + equipo + rol.
9. Inicializar bloques vacíos donde corresponde (`lealtades.secretos: []`, `vinculos: []`, `historial: []`).
10. Generar `historia` con LLM, anclada en facción + rol + concepto + perk + complicación + origen geográfico + edad.
11. Copiar `tags` a `tags_iniciales` (snapshot inmutable).

### 7.2. Atributos, `mando`, `fza_aportada` (determinísticos)

Tabla tomada de `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md`. **No se sortean.**

| `rol_id` | Rol (Confederación) | Rol (Ejército Rojo) | FIS | TAC | MEN | FZA | `mando` default |
|---|---|---|---|---|---|---|---|
| `lider_escuadra` | Sargento | — | 3 | 5 | 7 | 2 | `titular` |
| `lider_revolucionario` | — | Camarada Puntero | 3 | 5 | 7 | 2 | `titular` |
| `segundo_mando` | Cabo Primero | Segundo Camarada | 3 | 5 | 6 | 2 | `suplente` |
| `apuntador` | Apuntador | Tirador | 3 | 5 | 5 | 2 | `no_apto` |
| `artillero` | Artillero FAP | Ametrallador | 3 | 4 | 3 | 2 | `no_apto` |
| `fusilero` | Fusilero / Soldado 1ª | Miliciano Veterano | 3 | 3 | 3 | 1 | `no_apto` |
| `recluta` | Recluta / Soldado 2ª | Voluntario | 3 | 2 | 2 | 1 | `no_apto` |

**`mando` en generación:** default `titular` solo si `rol_id ∈ {lider_escuadra, lider_revolucionario}`; `suplente` para `segundo_mando`; `no_apto` para el resto. Cambiar `mando` post-creación requiere hito `cambio_mando` y no toca ningún otro campo.

**Distribución por escuadra de 11**: 1 + 1 + 1 + 1 + 4 + 3. FZA total: 15.

**Sorteo de rol cuando no se fija**: proporcional a la composición (la API tiende a entregar fusileros/reclutas, lo cual es realista).

**Nota sobre `tag_rol` (ELIMINADO):** en versiones anteriores existía un campo `tag_rol: array<string>` con etiquetas mecánicas del rol. Desde v0.2.2 estas etiquetas son tags con `categoria: rol` dentro del bloque `tags[]`. La tabla de stats por rol (antes documentaba `tag_rol`) ya no tiene esa columna; las etiquetas de rol se documentan en el catálogo `/meta/tag_categories`.

### 7.3. `nombre` y `nombre_de_campo` (sorteo + composición determinística)

**`nombre`**: tabla curada de nombres reales (sin prefijo de rango). Segmentada por facción.

- **Confederación**: tono militar formal, gentilicios del centro/norte/cuyo (Córdoba, Mendoza, Neuquén, Buenos Aires), apellidos hispano-criollos. Ejemplos canon en uso: *Aguirre, Sosa, Quiroga, Funes, Rodríguez, Olivares, Acosta, Pereyra, Méndez, Lugones, Ramírez*.
- **Ejército Rojo**: tono obrero/patagónico, apellidos con presencia mapuche y costa sur (Bahía Blanca, Stroeder, Comodoro, Bariloche). Ejemplos canon en uso: *Mansilla, Iturra, Antinao, Calfucurá, Cárcamo, Paine, Soriano, Belenchini, Bordón, Maturana, Bordagaray*.

El pool **excluye** los 22 ya canonizados para evitar duplicados con mocks.

**`nombre_de_campo`**: se compone determinísticamente a partir del `nombre` real:

- **Confederación**: `{rango_narrativo} + {nombre}`. Ej. "Sargento Walter Aguirre". El rango narrativo se deriva de `rol_id` según tabla canon.
- **Ejército Rojo con `especialidad`**: `{titulo_especialidad} + {nombre}`. Ej. si especialidad es `medicina`, el título puede ser "Doctor"; si es `ingenieria`, "Ingeniero".
- **Ejército Rojo sin `especialidad`**: título revolucionario genérico + nombre. Ej. "Camarada Puntero Ramón Mansilla".
- **Null si no hay distinción**: para personajes donde el nombre de campo sea idéntico al nombre real (casos futuros), se acepta `null`.

### 7.4. `edad`, `genero`, `origen_geografico`

- **`edad`**: sorteo en rango sugerido por `rol_id` (reclutas: 18–24; fusileros: 20–35; líderes: 28–45). Tabla curada.
- **`genero`**: sorteo según distribución curada por facción (Confederación: ~85% masculino, ~15% femenino; Ejército Rojo: ~70% masculino, ~25% femenino, ~5% no-binario por presencia obrera/sindical mixta). Valores sugeridos: `masculino`, `femenino`, `no_binario`, `otro`. La distribución es ajustable a futuro sin tocar schema.
- **`origen_geografico`**: tabla curada `(region, localidad)` por facción. Bahía Blanca, Stroeder, Comodoro, Bariloche para Ejército Rojo. Neuquén, Mendoza, Córdoba, Buenos Aires interior para Confederación.

### 7.5. Tags de rasgo (antes: `apariencia`)

El bloque `apariencia` ya no existe como campo separado. En su lugar, la generación popula tags con `categoria: rasgo`.

- **En generados dinámicamente**: mínimo viable. 1 tag de altura, 1 tag de complexión, 2-3 tags de rasgos físicos sorteados de pool corto por facción. Sin tags de cicatriz en creación.
- **En mocks**: ricos, escritos a mano como tags.
- **En canonizados**: heredan del generado o del body; nuevas cicatrices se agregan vía hito `agregar_tag` con `categoria: rasgo`.

Pool curado de rasgo por facción: ~20 valores sugeridos por facción, abierto a extensión sin tocar schema.

### 7.6. `lealtades`

- **En generados**: `primaria` = nombre de la facción; `secundarias` = 0-2 entradas sorteadas de pool curado por facción + origen ("su escuadra", "su provincia natal", "los aserraderos del alto valle"); `secretos: []` vacío.
- **En mocks y canonizados**: ricas, escritas o agregadas vía hito.

### 7.7. `aspectos.concepto`

Frase narrativa breve (10–20 palabras) que define la identidad nuclear. Tabla curada de ~60–100 conceptos por facción, sorteada por PRNG. Determinismo perfecto, control narrativo total, costo cero en runtime.

### 7.8. `aspectos.perk_fijo` y `aspectos.complicacion_fija`

Sorteo sobre los pools canon de `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md` (12 perks, 10 complicaciones).

**Restricción 80/20 (soft)** por `rol_id`:

- ~80% de las veces, el sorteo se hace sobre el subconjunto de perks/complicaciones "naturales" del rol (ej. `Voz de mando` y `Recarga rápida` son naturales de líderes; `Tirador frío` lo es de apuntadores).
- ~20% de las veces, el sorteo cae libre sobre el pool completo, generando combinaciones inesperadas pero válidas ("un recluta con Voz de mando" produce un personaje con sabor narrativo).

La clasificación natural/no-natural por rol vive como metadato en cada entrada del pool: `roles_naturales: [lider_escuadra, lider_revolucionario, segundo_mando]`. Open: cualquier perk nuevo se etiqueta al crearse.

### 7.9. `equipo.armor`

Tabla determinística:

| `rol_id` | armor |
|---|---|
| `lider_escuadra` | 1 |
| `lider_revolucionario` | 1 |
| `segundo_mando` | 1 |
| `apuntador` | 1 |
| `artillero` | 0 |
| `fusilero` | 0 |
| `recluta` | 0 |

Ejército Rojo aplica techo `armor` máximo 1 (doctrina anti-equipamiento pesado).

### 7.10. Tags de equipo (antes: `equipo.armas` y `equipo.equipo_tactico`)

Las armas y accesorios tácticos se generan como tags con `categoria: equipo`. El pool curado tiene la misma lógica que antes pero produce tags en lugar de objetos estructurados.

Pool curado `rol_id × faccion`:

| `rol_id` | Confederación (default) | Ejército Rojo (default) |
|---|---|---|
| `lider_escuadra` / `lider_revolucionario` | Fusil FAL (media) + Pistola reglamentaria (corta) | Subfusil Halcón (corta) + Pistola (corta) |
| `segundo_mando` | Fusil FAL (media) + Pistola reglamentaria (corta) | Subfusil o Fusil ligero (media) + Pistola (corta) |
| `apuntador` | Fusil de precisión (larga) | Fusil de cerrojo Mauser (larga) |
| `artillero` | FAP (media) | Ametralladora ligera (media) |
| `fusilero` | Fusil FAL (media) | Fusil Mauser (larga) o subfusil (corta) |
| `recluta` | Fusil FAL (corta) | Lo que haya disponible |

El tag de arma incluye el alcance en el valor: `{nombre} (alcance {categoria})`. El origen, la captura y el estado se materializan como hito `agregar_tag` / `quitar_tag` si aplica.

Ítem táctico adicional: 50% ninguno, 50% 1 tag de pool genérico (`vendaje`, `cantimplora`). En mocks: hasta 4 tags narrativos.

### 7.11. `vinculos` y `historial`

- **En generados dinámicamente**: ambos vacíos (`vinculos: []`, `historial: []`). El personaje efímero todavía no tuvo tiempo de vivir.
- **En mocks**: se inicializan con el contenido escrito a mano (ver ejemplos 6.3 y 6.4).
- **En canonizados**: heredan del generado/body inicial; el motor downstream los puebla vía `POST /character/{id}/event` (sección 10).

### 7.12. `historia` (LLM)

Prosa de 120–200 palabras. Generada por un modelo de Workers AI con prompt que recibe:

- `faccion` (con descriptor de lore de `/Dev/syv-battle-game-system/lore/universo.md`).
- `rol` narrativo + `concepto`.
- `perk_fijo.nombre` y `complicacion_fija.nombre`.
- `nombre`, `nombre_de_campo`, `edad`, `genero`, `origen_geografico` (para que la prosa los respete).
- Instrucción de tono: militar, austero, sin marketing, sin épica fácil, voz rioplatense, 2–3 párrafos.

Para reproducibilidad bajo `?seed=`:

1. Clave de cache = `hash(seed + inputs + version_modelo)`.
2. Si hay hit, se retorna la prosa cacheada.
3. Si no, se llama al modelo con `temperature` fija y se persiste.

Si el personaje se canoniza, la prosa pasa al campo `historia` del registro persistente y queda **inmutable**. Cambiar el modelo después no afecta a los canonizados existentes.

### 7.13. `tags_iniciales` y `estado_salud`

- `tags_iniciales` = snapshot completo de `tags[]` al momento de creación, incluyendo todas las categorías (rasgo, equipo, rol y cualquier otra que el generador haya producido). Preservado para auditoría; inmutable post-creación. Permite calcular el diff entre estado original y estado vigente comparando `tags_iniciales` con `tags[]` actuales.
- `estado_salud` = `"activo"` en creación. Estados `"herido"` y `"baja"` los inyecta el motor downstream vía eventos (registrados también como hitos).

---

## 8. Reproducibilidad por semilla

- Toda llamada de **generación efímera** admite `?seed=<string>`. Si no se pasa, la API genera uno (formato sugerido: ULID en minúsculas) y lo retorna en `personaje.semilla`.
- La PRNG es determinística (no `Math.random()`): la misma `seed` produce la misma secuencia.
- La prosa LLM se cachea por clave `(seed, inputs, version_modelo)` para que repetir la llamada con la misma semilla devuelva exactamente la misma prosa.
- Garantía contractual para **efímeros**: con `(seed, faccion, rol_id)` fijos y `version_modelo` fija, la respuesta es byte-a-byte equivalente excepto `metadatos.creado_en`.

**Limitación aceptada para canonizados:** tras la canonización, el personaje conserva su `semilla` original pero **deja de ser regenerable** porque su historial muta. Una `GET /character/{id}` en t1 y la misma en t2 (tras un hito) devuelven payloads distintos. Esto es deliberado y constituye el diferencial del producto: los canonizados son entidades vivas, no funciones puras de una seed.

La `semilla` original se preserva para trazabilidad y para reconstruir el "estado en el momento de la creación" cuando se quiera comparar el personaje original con su versión actual (operación no soportada por la API en v1; queda como herramienta de inspección manual).

---

## 9. Memoria viva — el diferencial del producto

Esta sección es nueva en v0.2.0 y define la naturaleza del recurso canonizado.

### 9.1. Naturaleza del canonizado

Un personaje canonizado **existe en el tiempo**. Tiene un instante de nacimiento (`canonizado_en`) y un estado vigente que cambia cuando le pasan cosas. El motor de batalla, el redactor narrativo y el curador del lore son los que generan los eventos que modifican al personaje; la API los **registra y los aplica**.

La ficha que devuelve `GET /character/{id}` es siempre el **estado vigente**, no el estado original. Para ver "qué era este personaje el día que lo canonizaron" hay que filtrar mentalmente sacando los hitos del `historial[]` — operación no asistida por la API en v1.

### 9.2. Eventos y mutación

Los cambios ocurren vía `POST /character/{id}/event`. El cuerpo del evento es una entrada de `historial[]` (`fecha`, `tipo`, `descripcion`, `ref_batalla`, `metadata`). Al registrarse, la API:

1. **Apendea** la entrada al `historial[]`.
2. **Aplica** el efecto del evento sobre los campos vigentes correspondientes, según el `tipo` y la `metadata`.
3. **Actualiza** `metadatos.ultima_actualizacion`.

### 9.3. Campos mutables vs inmutables

**Mutables** (cambian vía hito):

- `atributos.fis`, `atributos.tac`, `atributos.men` (via `triple_cero` o `mejora_atributo`).
- `aspectos.concepto`, `aspectos.perk_fijo`, `aspectos.complicacion_fija` (vía `mejora_aspecto` narrativo).
- `equipo.armor` (vía hito narrativo explícito).
- `tags[]` (vía `agregar_tag` / `quitar_tag` — cubre armas, accesorios, rasgos físicos como cicatrices).
- `vinculos[]` (vía `formacion_vinculo`, `ruptura_vinculo`).
- `lealtades.secundarias`, `lealtades.secretos` (vía `cambio_lealtad`).
- `rol`, `rol_id`, `fza_aportada` (vía `ascenso` o `traslado` — los atributos `{fis,tac,men}` no se tocan; los tags con `categoria: rol` se realinean al nuevo rol vía hitos `quitar_tag` + `agregar_tag`).
- `mando` (vía `cambio_mando` — no toca ningún otro campo).
- `nombre_de_campo` (vía `ascenso` o `cambio_mando`, cuando el título cambia).
- `estado_salud` (vía `herida`, `baja`, `recuperacion`).
- `metadatos.ultima_actualizacion` (siempre).

**Inmutables** (definen la identidad del canonizado):

- `id`.
- `nombre` (el nombre real nunca cambia).
- `genero`.
- `origen_geografico` (region y localidad de nacimiento — no cambia aunque el personaje se mude).
- `semilla` original.
- `historia` (prosa biográfica congelada al canonizar).
- `metadatos.creado_en`, `metadatos.canonizado_en`, `metadatos.modelo_prosa`, `metadatos.es_canon`.
- `tags_iniciales` (snapshot de tags al crear; auditoría).

**`edad`**: **mutable** vía modificación directa (decisión narrativa explícita del curador). No hay mecánica de envejecimiento ni hito formal asociado; `cumpleanos` y `paso_del_tiempo` quedan eliminados del vocabulario canon.

### 9.4. Granularidad del historial

- Solo hitos importantes. El motor de batalla lleva su propio log detallado de combate (turnos, dados, daños) aparte. El `historial[]` del personaje responde a "¿qué cosas le pasaron que vale la pena recordar en su ficha?".
- **Sin límite de tamaño.** El `historial[]` viaja inline completo en la respuesta. Se asume que "solo hitos importantes" lo mantiene acotado en la práctica. Si en producción algún canonizado supera ~100 entradas y la latencia se vuelve perceptible, se reevalúa en ese momento. No hay paginación en v1.

### 9.5. Tipos de hito (canon sugerido — abierto)

El campo `tipo` admite cualquier string. El canon **sugiere** un vocabulario para que motor, redactor y sitio de lore hablen el mismo idioma:

| `tipo` | Disparador típico | Efecto sobre campos vigentes |
|---|---|---|
| `triple_cero` | Motor (regla mecánica) | `atributos.<atributo> += 1` (techo 5, MEN-líder 7); `metadata: { atributo, delta, valor_anterior, valor_nuevo }` |
| `mejora_atributo` | Narrador (decisión externa) | igual a `triple_cero` pero sin disparador mecánico |
| `ascenso` | Narrador | `rol`, `rol_id`, `fza_aportada` se reemplazan; `nombre_de_campo` se recompone; tags `categoria: rol` se realinean; atributos `{fis,tac,men}` NO se tocan; `metadata: { rol_id_anterior, rol_id_nuevo }` |
| `traslado` | Narrador | `rol` y/o `rol_id` (si cambia función); `fza_aportada` se realinea; tags `categoria: rol` se realinean; atributos NO se tocan |
| `cambio_mando` | Narrador o motor | `mando` se reemplaza; ningún otro campo cambia; `metadata: { de, a, motivo }` |
| `agregar_tag` | Motor o narrador | append a `tags[]`; `metadata: { categoria, valor }` |
| `quitar_tag` | Motor o narrador | remove de `tags[]`; `metadata: { categoria, valor }` |
| `herida` | Motor o narrador | `estado_salud: "herido"`; opcionalmente `agregar_tag` con `categoria: rasgo` (cicatriz) |
| `baja_temporal` | Motor | `estado_salud: "baja"` |
| `recuperacion` | Motor o narrador | `estado_salud: "activo"` |
| `formacion_vinculo` | Narrador | append a `vinculos[]`; `metadata: { vinculo_creado }` |
| `ruptura_vinculo` | Narrador | remove o transformación de `vinculos[]` |
| `cambio_lealtad` | Narrador | mutación de `lealtades.secundarias` o `lealtades.secretos` |
| `mejora_aspecto` | Narrador | reemplazo de `aspectos.concepto`, `perk_fijo` o `complicacion_fija` |
| `condecoracion` | Narrador | no muta campos vigentes (queda como hito puro) |

El motor o el narrador pueden emitir tipos custom; la API los acepta y los apendea al historial. El efecto sobre campos vigentes solo ocurre para los tipos conocidos; tipos custom **no mutan** la ficha (quedan como hito puro).

**Nota sobre atributos y rol_id.** Los atributos `{fis, tac, men}` son **propiedad del personaje**, no derivados del rol_id post-creación. Cuando un personaje cambia de `rol_id` (por ascenso, traslado u otro hito), los atributos vigentes no se tocan. Los tags con `categoria: rol` sí se realinean al nuevo rol (son etiquetas del rol vigente, no propiedad permanente del personaje). La matriz determinística por rol (sección 7.2) aplica **únicamente** en el momento de creación.

---

## 10. Endpoints (alto nivel)

Cada entrada describe la intención y el shape, no la implementación.

### `GET /character`

Genera un personaje efímero. Parámetros opcionales:

- `faccion`: `confederacion` | `ejercito_rojo`
- `rol_id`: uno de los 7 sugeridos
- `seed`: string libre
- `fields`: lista separada por comas para podar la respuesta (ver `GET /character/{id}`)

Devuelve un `personaje` con `origen: "generado"`, `id: null`, `es_canon: false`, `historial: []`, `vinculos: []`, `metadatos.canonizado_en: null`.

Mapea: UC-01..04, UC-06, UC-16.

### `GET /character/{id}`

Devuelve el personaje con id exacto. Funciona para mocks (`mock.*`) y canonizados (`canon.*`). Devuelve 404 si no existe.

Parámetros opcionales:

- `fields`: lista separada por comas (ej. `?fields=id,nombre,atributos,equipo,tags`). Permite podar el payload. Si no se pasa, devuelve la ficha completa, incluido `historial[]` inline.

Mapea: UC-05, UC-15, UC-16.

### `GET /character/{id}/historial`

Devuelve solo el `historial[]` del personaje. Útil para renderizar líneas de tiempo sin cargar la ficha completa.

Sin paginación en v1 (el historial viaja completo). Si en el futuro se reevalúa el límite de tamaño, este endpoint sería el candidato natural para incorporar un cursor.

Mapea: UC-17.

### `POST /character/{id}/event`

Registra un hito sobre un canonizado. Body: una entrada de `historial[]` (`fecha`, `tipo`, `descripcion`, `ref_batalla`, `metadata`).

Efecto:

1. Apendea la entrada al `historial[]`.
2. Aplica el efecto sobre campos vigentes según `tipo` (ver tabla 9.5).
3. Actualiza `metadatos.ultima_actualizacion`.

Devuelve la ficha completa actualizada.

Solo aplica a `origen: "canonizado"`. Sobre mocks devuelve 409 (los mocks son inmutables). Sobre efímeros devuelve 404 (no existen como recurso persistente).

Gobernanza de quién puede llamar este endpoint: ver Open Question #1 (sección 14).

Mapea: UC-10..14.

### `GET /roster/mock`

Lista los 22 fixtures con `id`, `nombre`, `nombre_de_campo`, `faccion`, `rol_id`, `rol`. Sin payload completo.

Mapea: UC-08.

### `POST /canonize`

Toma un personaje generado (vía body con la ficha completa + seed) y lo persiste como canon **en el almacenamiento de la API**. Asigna `id` estable (`canon.{ulid}`), cambia `origen` a `"canonizado"`, marca `metadatos.es_canon: true`, fija `metadatos.canonizado_en`. La prosa de `historia` se congela en este momento.

**Idempotencia.** `POST /canonize` es idempotente por la tripleta `(seed, faccion, rol_id)`. Si se llama dos veces con los mismos parámetros, se devuelve el id del primero canonizado en lugar de crear uno nuevo. Si un curador quiere dos versiones distintas del mismo arquetipo, debe variar la seed o el rol_id.

**Explícito:** este endpoint nunca toca `/Dev/syv-battle-game-system/personajes/`. Nunca abre PRs. Los canonizados son un universo de la API; los mocks Markdown del battle-system son un universo paralelo.

Mapea: UC-07.

### `GET /meta/factions`

Devuelve el catálogo de facciones con descriptor de lore corto.

### `GET /meta/roles`

Devuelve los 7 `rol_id` sugeridos con su tabla de stats, `mando` default, `fza_aportada`, `armor` y nombres narrativos por facción.

### `GET /meta/perks` y `GET /meta/complications`

Devuelven los pools canon vigentes. Cada entrada incluye `id`, `nombre`, `condicion`, `efecto`, `roles_naturales` (lista de `rol_id` para los que el perk es "natural" en la restricción 80/20).

### `GET /meta/hito_types`

Devuelve los tipos de hito sugeridos (tabla 9.5) con su descriptor de efecto. **Importante**: estos son **sugeridos**, no exhaustivos. Cualquier motor puede emitir un `tipo` custom y la API lo registra en el historial sin aplicar mutación.

### `GET /meta/vinculo_types`

Devuelve los tipos de vínculo sugeridos (mentor, subordinado, hermano_de_armas, rival, deuda, enemigo_jurado, familia, romance). Mismos términos: sugeridos, no exhaustivos.

### `GET /meta/tag_categories`

Devuelve el catálogo de categorías de tags canon sugeridas (`rasgo`, `equipo`, `rol`, etc.) con descriptor de uso. Categorías abiertas: el catálogo es sugerido, no exhaustivo.

Mapea (todos los `/meta/*`): UC-09.

---

## 11. Los 22 mock — alcance del MVP

Los 22 personajes iniciales son fixtures versionadas en `mock/personajes/{faccion}/{nn}_{rol}_{apellido}.yaml`, escritos al schema v0.2.0/v0.2.1 (con `apariencia`, `lealtades`, `vinculos`, `historial` poblados a mano). Su contenido base proviene del Markdown canon de `/Dev/syv-battle-game-system/personajes/`; el MVP los **importa y enriquece** para el schema nuevo.

**Nota sobre migración de mocks.** Los 22 fixtures en `mock/personajes/` están al schema v0.2.0/v0.2.1 y **no han sido actualizados al schema v0.2.2**. La migración (eliminar `apariencia`, convertir `armas[]` y `equipo_tactico[]` a tags, agregar `nombre_de_campo`, `especialidad`, `mando`) se realizará en una iteración separada. Hasta entonces, los mocks son válidos para tests que no dependan de los campos nuevos.

Esta tabla fija el contrato de existencia.

### 11.1. Escuadra Confederación (11)

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

### 11.2. Escuadra Ejército Rojo (11)

| # | `id` | Rol | `rol_id` | Nombre canon |
|---|---|---|---|---|
| 12 | `mock.ejercito_rojo.01.mansilla` | Camarada Puntero | `lider_revolucionario` | Camarada Puntero Ramón Mansilla |
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

**Composición.** El reglamento local define la escuadra como **1 + 1 + 1 + 1 + 4 + 3**. El PRD adopta esta composición porque es la que ya existe en el canon. Si el reglamento migra a otra, primero se cambia el reglamento, después el PRD, después se regenera el set de mocks.

**Nota sobre mutabilidad de mocks.** Los mocks son **inmutables** desde la API (`POST /character/{id}/event` sobre un mock devuelve 409). Su evolución, si la hay, ocurre por reescritura manual del fixture YAML y un release de la API. Esto los distingue de los canonizados, que evolucionan vía evento.

---

## 12. Alcance MVP vs futuro

### Dentro de v1

- 2 facciones jugables: Confederación y Ejército Rojo.
- 7 `rol_id` con su matriz determinística (agrega `lider_revolucionario` para Ejército Rojo).
- Pools canon de perks (12) y complicaciones (10) con metadato `roles_naturales`.
- Tablas curadas de nombres, edades, géneros, orígenes geográficos, conceptos, armas y equipo por facción.
- Generación efímera con seed reproducible.
- 22 mocks importados, enriquecidos al schema v0.2.2 (con tags, lealtades, vínculos, historial escritos a mano) en iteración separada.
- Canonización persistente (solo DB de la API; no toca battle-system).
- **Memoria viva**: endpoint de evento, mutación de campos vigentes, historial inline.
- **Aspectos mutables, vínculos mutables, tags mutables** sobre canonizados.
- **Sistema híbrido tags + campos**: rasgo, equipo, rol como categorías canon; abiertas a extensión.
- **Mando como enum independiente** del rol_id.
- **Lealtades estructuradas** con secretos.
- **Customs libres** (`p_custom_*`, `c_custom_*`) en perks y complicaciones.
- **Extras** libres al top level.
- **Enums abiertos** con catálogos `/meta/*` que sugieren valores (incluye `/meta/tag_categories`).
- Endpoints `/meta/*` para introspección del canon (incluye `hito_types`, `vinculo_types`, `tag_categories`).
- Restricción 80/20 soft de perks por rol.
- Poda de respuesta con `?fields=`.

### Explícitamente fuera de v1

- Las 3 facciones secundarias (Pueblos del Pantano, Los Salvajes, Los Poseídos): existen en lore, no se generan ni se sirven.
- PJs civiles.
- Perks de batalla y complicaciones temporales (son del motor de batalla, no del generador).
- Sistema de hexágonos, mapa, escenarios.
- Runtime de batalla (la API registra hitos, no los simula).
- Autenticación, autorización, rate limiting, cuotas.
- UI propia (la API es headless).
- Generación de escuadras completas en una sola llamada (se compone con N llamadas).
- Edición arbitraria de canonizados (solo cambios vía evento; no `PATCH /character/{id}`).
- Edición de mocks vía API.
- Reverso de hitos (no hay "deshacer" un evento; la única forma de corregir es otro evento que documente la corrección).
- Versionado de la prosa congelada (no se regenera nunca).
- Internacionalización (todo en español).
- Operación "diff entre estado original y estado vigente" (la `semilla` + `tags_iniciales` se preservan pero no hay endpoint que reconstruya automáticamente).

---

## 13. Tensiones explícitas y compromisos asumidos

Esta sección documenta decisiones que el PRD toma sabiendo que tienen un costo. No son problemas a resolver: son trade-offs aceptados.

### 13.1. Customs libres + enums abiertos → motor downstream interpreta contenido libre

**Decisión.** El producto acepta `perk_fijo`/`complicacion_fija` con id `p_custom_*` y descripción en texto libre. Acepta `tipo` de hito y `tipo` de vínculo con valores fuera del canon sugerido. Acepta `extras` no validado.

**Costo.** El motor de batalla que consuma un canonizado con `perk_fijo.id = p_custom_eco_del_penasco` no tiene mecanismo formal para entender su efecto. La interpretación queda a su cargo (probablemente vía LLM al momento de aplicar la regla, o vía intervención humana).

**Por qué se acepta.** La alternativa — exigir que todo perk pase por el pool oficial — paralizaría la creación de personajes notables y forzaría a "embutir" sabor narrativo en perks genéricos. El producto es un generador de **personajes con identidad**, no de fichas mecánicas intercambiables. El motor downstream tiene que poder lidiar con la riqueza que el producto habilita.

**Mitigación.** El catálogo `/meta/perks` siempre devuelve la versión "oficial" para que el motor tenga un fallback de comparación. Los customs llevan prefijo `p_custom_*` / `c_custom_*` para ser fácilmente detectables.

### 13.2. Tags con categorías abiertas → riesgo de fragmentación semántica

**Decisión.** Las categorías de tags son un enum abierto: cualquier cliente puede emitir `{categoria: "apariencia", valor: "..."}` en lugar de `{categoria: "rasgo", ...}`, o inventar sinónimos como `physical`, `aspecto_visual`, etc. No hay validación de categorías.

**Costo.** El motor downstream que consuma tags y quiera agruparlos por categoría tiene que interpretar semánticamente las categorías. Si distintos clientes inventan sinónimos, la fragmentación hace que el agrupamiento sea un problema de interpretación, no de recuperación.

**Por qué se acepta.** Consistente con la política de enums abiertos del producto. Exigir categorías estrictas requeriría un registry centralizado con proceso de aprobación, lo que va en contra del principio de extensión sin migraciones.

**Mitigación.** El catálogo `/meta/tag_categories` documenta las categorías canon sugeridas (`rasgo`, `equipo`, `rol`, etc.). Los clientes bien informados las usan. El catálogo está versionado junto al PRD. Los consumidores que necesiten agrupamiento semántico estricto deben normalizar las categorías al leer, no al escribir.

### 13.3. Sin versionado del payload → riesgo de drift si SOLID falla

**Decisión.** Se elimina `version_canon`. El schema se extiende sin romper, los enums son abiertos, hay `extras` libre. No hay migraciones.

**Costo.** Si en algún momento se descubre que un campo está mal diseñado y necesita romperse, no hay herramienta de versionado para migrar. La única salida sería convivir con dos formas del mismo campo, lo cual deteriora el contrato.

**Por qué se acepta.** Versionar y migrar es caro y propenso a error. La filosofía SOLID/open-close apuesta a que el diseño inicial sea lo suficientemente robusto para no requerir breaking changes. Los precedentes de la decisión: `extras`, enums abiertos, customs libres — todos absorben extensión sin tocar el contrato.

**Mitigación.** La sección 6 está diseñada con bloques fuertemente segmentados y orientados a extensión. Cualquier campo nuevo entra en `extras`, en un bloque nuevo top-level, o como nuevo valor de enum. Si una vez en producción se descubre una necesidad de breaking change, esta tensión se reabre en una v0.3.0.

### 13.4. Sin validación de `ref_personaje_id` → referencias colgadas posibles

**Decisión.** El campo `vinculos[].ref_personaje_id` se acepta sin verificar que apunte a un id existente. Puede apuntar a un personaje futuro, a un NPC externo, o a un id mal escrito.

**Costo.** Un cliente que renderice vínculos puede recibir un `ref_personaje_id` que no resuelve. Un `GET` sobre ese id devuelve 404.

**Por qué se acepta.** Validar referencias implica orden de creación, ciclos de dependencia, y una capa de integridad referencial que no se justifica en el MVP. Además, muchos vínculos legítimos apuntan a personajes externos al corpus de la API.

**Mitigación.** El campo `descripcion` del vínculo es **obligatorio y crítico**. Sirve de fallback para que el vínculo tenga sentido aunque la referencia no resuelva. Los consumidores deben renderizar primero la descripción y secundariamente intentar resolver el id.

### 13.5. Memoria viva rompe reproducibilidad post-canonización → naturaleza del producto

**Decisión.** Un canonizado, una vez recibido su primer hito, deja de ser regenerable desde su `semilla`. La ficha vigente difiere de la ficha original.

**Costo.** La promesa de "reproducibilidad total por seed" no aplica a canonizados con historial. Tests que dependen de "regenerar el mismo personaje" deben usar efímeros, no canonizados.

**Por qué se acepta.** Es lo que constituye el diferencial del producto. Un personaje vivo cambia. Si fuera reproducible byte-a-byte tras N hitos, sería una función pura, no una memoria.

**Mitigación.** La `semilla` original se preserva en el campo `semilla`. `tags_iniciales` preserva el estado del inventario y rasgos en el momento de la creación. Una herramienta externa puede tomar `(semilla, faccion, rol_id)` y regenerar el "estado en el momento de la creación" para comparar — pero esto no es operación soportada por la API en v1.

---

## 14. Píldoras de arquitectura

Observaciones de afinidad técnica que no son decisiones de stack pero vale la pena registrar para cuando llegue la fase de arquitectura.

### 14.1. Tags y stores no-transaccionales

El patrón de entidades pequeñas, repetibles, agrupables y sin esquema rígido (tags) es el caso textbook para un store no-transaccional o document-oriented. Cloudflare D1 con columna JSON o Workers KV con prefijo por categoría son candidatos naturales. No decidimos stack acá — esta píldora solo registra la afinidad para cuando llegue la fase de arquitectura.

---

## 15. Open questions v0.2.2

Preguntas reales que esta versión deja abiertas para la próxima iteración. Las OQs cerradas en v0.2.1 fueron incorporadas como decisiones en las secciones correspondientes.

1. **Gobernanza de `POST /character/{id}/event`.** ¿Quién puede llamarlo? El motor de batalla obvio (para `triple_cero`, `herida`, `baja`). ¿Pero un redactor narrativo puede emitir `ascenso` o `cambio_lealtad` desde cualquier cliente? Sin auth en v1, en la práctica cualquiera con la URL puede. Decidir si esto se atemporaliza con tokens, lista blanca de orígenes, o si se acepta porque el corpus de canonizados es pequeño y curable a mano.

2. **Mutabilidad fina de rasgos físicos.** Cicatrices mutan (se agregan vía `agregar_tag` con `categoria: rasgo`). ¿Pero una herida grave puede mutar tags de complexión ("queda enjuto tras la convalecencia")? ¿Los rasgos de altura y complexión son absolutamente inmutables o pueden modificarse vía hito narrativo explícito? El PRD los marca modificables como cualquier tag, pero no hay restricción explícita; podría clarificarse.

3. **Interpretación de customs por el motor.** ¿El motor de batalla se compromete a interpretar `p_custom_*` con un LLM al momento de aplicar la regla, o existe un workflow donde un curador humano traduce el custom a una regla mecánica antes de que el personaje entre a batalla? Esta tensión está documentada (13.1) pero el flujo operacional concreto queda abierto.

4. **Persistencia de `semilla` vs entidad viva.** La `semilla` se preserva post-canonización para trazabilidad. ¿Es útil exponer un endpoint `GET /character/{id}/original` que regenere la ficha al estado de creación (sin historial) para que herramientas externas puedan calcular el diff? Fuera de v1 pero útil para auditoría narrativa.

5. **Versionado de categorías canon de tags.** ¿Las categorías canon (`rasgo`, `equipo`, `rol`, etc.) se versionan junto al PRD o viven en un catálogo separado consultable vía `/meta/tag_categories`? Si separado, ¿quién las cura y con qué proceso? El endpoint existe en el schema de v0.2.2, pero la gobernanza del catálogo queda abierta.

---

*Fuentes canónicas referenciadas (no copiadas):*

- `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md` — esquema y matriz de stats por rol.
- `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md` — pools de perks y complicaciones.
- `/Dev/syv-battle-game-system/lore/universo.md` — descriptores de facción usados como contexto del LLM.
- `/Dev/syv-battle-game-system/personajes/` — 22 fichas canon base que alimentan los mocks (pendientes de actualizar al schema v0.2.2).
- `https://github.com/kodexArg/syv-game-system/blob/main/arquitectura/esquemas/personaje.schema.json` — schema público de referencia.
