# PRD — syv-character-kit

> **Documento vivo.** Define el contrato de producto de la API generadora de personajes del universo *Subordinación y Valor* (SyV). No contiene decisiones de arquitectura, almacenamiento ni stack — solo el QUÉ.
>
> **Versión**: 0.2.0
> **Reemplaza**: 0.1.0
> **Idioma**: castellano rioplatense, voseo sobrio.
> **Convención de identificadores en payloads JSON/YAML**: `snake_case_castellano` (consistente con `faccion`, `atributos`, `aspectos`, `estado_salud`, `fza_aportada` ya usados en `/Dev/syv-battle-game-system/`).

---

## 0. Changelog

### v0.2.1

Patch incremental sobre v0.2.0. Cierra cuatro *open questions* que habían quedado abiertas: **OQ#1** (edad), **OQ#3** (límite del historial), **OQ#5** (mutabilidad de atributos al cambiar de rol_id), y **OQ#7** (idempotencia de `POST /canonize`). Como resultado de OQ#1, se eliminan del vocabulario de hitos los tipos `cumpleanos` y `paso_del_tiempo`. Se clarifica taxativamente que los atributos `{fis, tac, men}` son propiedad del personaje y no se derivan del rol_id post-creación. Quedan 4 OQs abiertas (renumeradas 1–4 en sección 14).

### v0.2.0

Esta versión cierra las cuatro *open questions* abiertas en v0.1.0 y, sobre esas decisiones, introduce un cambio de naturaleza del recurso: el personaje canonizado deja de ser una foto inmutable y pasa a ser una **memoria viva con experiencia**.

**OQ resueltas:**

- **OQ#1 (`/canonize` y el repo de fichas):** la canonización persiste **únicamente** en la base de la API. Nunca toca `/Dev/syv-battle-game-system/personajes/`, nunca abre PRs. Los mocks Markdown del battle-system y los canonizados de la API son **dos universos paralelos**, ambos legítimos, sin sincronización automática.
- **OQ#2 (historia en canonizados):** la prosa generada por LLM **se congela** en el momento de la canonización y queda inmutable. Pasa a formar parte de la identidad del personaje (id). No se regenera nunca, aunque cambie el modelo.
- **OQ#3 (versionado del canon de pools):** **no hay migraciones**. La extensibilidad del schema se resuelve por diseño SOLID y open/close desde el día uno. El campo `version_canon` desaparece del personaje. Filosofía explícita: si el schema necesita una migración, fallamos antes en el diseño que en la operación.
- **OQ#4 (restricción de perks por rol):** restricción **soft** (80/20). El sorteo sesga al ~80% hacia perks naturales del `rol_id` y deja ~20% para perks "de sabor" que crean fricción narrativa intencional.

**Concepto nuevo — memoria viva con experiencia:** un personaje canonizado evoluciona. Acumula batallas, sube atributos, gana cicatrices, rompe lealtades, captura armas, pierde compañeros. La ficha es el estado vigente de una entidad que existe en el tiempo, no una instantánea de su creación. Esto reformula el schema (sección 6), incorpora bloques nuevos (`historial`, `vinculos`, `apariencia`, `lealtades` estructuradas) y rompe deliberadamente la reproducibilidad por seed para canonizados tras el primer hito (sección 8).

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
- **Customs libres + enums abiertos como política deliberada.** El producto acepta `perk_fijo` o `complicacion_fija` con `id` `p_custom_*` / `c_custom_*` y descripción en texto libre. Los enums (`tipo` de hito, `tipo` de vínculo, `categoria_alcance`, etc.) tienen valores **sugeridos** pero no rechazan otros. **Tensión asumida**: el motor downstream que consuma estos customs tiene que poder interpretarlos (probablemente vía LLM). Ver sección 13.
- **Stats determinísticos por rol, narrativa sorteada.** En creación, los atributos y los campos mecánicos se derivan de una matriz fija por rol. Nombre, concepto, perk, complicación, arma e historia se sortean.
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

## 6. JSON canónico del personaje (v0.2.0)

Sección central del PRD. Define la forma del recurso `personaje` que la API devuelve.

El schema es **estricto** en estructura y **abierto** en valores: los campos están definidos, pero los enums admiten valores sugeridos sin rechazar otros, y existe un campo `extras` libre al top level.

### 6.1. Esquema (vista en YAML legible)

```yaml
personaje:
  # ── Identidad estable ──────────────────────────────────────────────────
  id: string                            # estable para mocks y canonizados; null para efímeros
  origen: enum                          # "mock" | "generado" | "canonizado"
  semilla: string                       # seed original que produjo la ficha; siempre presente

  nombre: string                        # nombre completo, ej. "Sargento Walter Aguirre"
  edad: integer                         # años, 16..70 sugerido. Integer simple; no hay mecánica de envejecimiento.
                                        # Si envejece, decisión narrativa directa sin hito formal.
  genero: enum                          # "masculino" | "femenino" | "no_binario" | "otro" (abierto)

  faccion: enum                         # "Confederación" | "Ejército Rojo" (otras 3 fuera de MVP)
  rol: string                           # denominación narrativa, ej. "Sargento"
  rol_id: enum                          # identificador mecánico (sugerido, ver 7.2; abierto)
  tag_rol: array<string>                # tags mecánicos, ej. ["líder", "sargento"]

  origen_geografico:                    # estructurado mínimo
    region: string                      # ej. "Patagonia Norte", "Pampa Húmeda"
    localidad: string                   # ej. "Neuquén", "Bahía Blanca"

  # ── Apariencia (estructurada completa) ─────────────────────────────────
  apariencia:
    altura: enum                        # "muy_bajo" | "bajo" | "medio" | "alto" | "muy_alto" (sugerido)
    complexion: enum                    # "delgado" | "atletico" | "robusto" | "corpulento" (sugerido)
    rasgos: array<string>               # ej. ["pelo negro", "mirada dura", "barba descuidada"]
    cicatrices: array<string>           # ej. ["corte vertical en mejilla derecha (Sector 12,15)"]

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
    armas:                              # 1..2 armas
      - nombre: string                  # ej. "Fusil FAL"
        categoria_alcance: enum         # "corta" | "media" | "larga" (sugerido; abierto)
    equipo_tactico: array | null        # ej. [{ nombre: "granadas humo x2", descripcion: "..." }]

  fza_aportada: integer                 # 1..3, derivado de rol_id

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
                                        # captura_equipo | formacion_vinculo | ruptura_vinculo |
                                        # traslado | condecoracion | mejora_atributo | mejora_aspecto
                                        # (abierto; el motor puede emitir tipos custom)
      descripcion: string
      ref_batalla: string | null        # id de batalla del motor downstream; opcional
      metadata: object                  # libre, open/close (ej. { atributo: "fis", delta: 1 })

  # ── Estado vigente (snapshot de runtime) ───────────────────────────────
  estado_salud: enum                    # "activo" | "herido" | "baja" (siempre "activo" en creación)
  tags_iniciales: array<string>         # snapshot al crear; preservado para auditoría

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

### 6.2. Notas de campo (lo no obvio)

- **`id`**: para mocks tiene forma `mock.{faccion_slug}.{nn}.{apellido_slug}` (ej. `mock.confederacion.01.aguirre`). Para canonizados, `canon.{ulid}`. Para efímeros, `null`.
- **`origen_geografico`**: mínimo estructurado (region + localidad). Si en el futuro se quiere agregar coordenadas o sector militar, va en `extras` o se extiende el sub-objeto sin romper.
- **`apariencia` estructurada**: sobre-diseñada deliberadamente para soldados (ver tensión en 13). La inversión queda lista para PJs civiles y para galería visual.
- **`lealtades`**: `primaria` es la afiliación nuclear (típicamente la facción, pero puede ser una persona — ver Aguirre con "Sargento Ricardo (post mortem)"). `secretos` permite tensiones narrativas que el motor puede explotar.
- **`atributos`**: un único set **mutable**. Cuando un triple-0 sube `fis`, se **sobreescribe** el valor. La trazabilidad de "cómo llegó al valor actual" vive en `historial[]`, no en campos separados base/actuales/efectivos.
- **`aspectos.perk_fijo` y `aspectos.complicacion_fija`**: estructuras completas (id + nombre + descripción). La hoja siempre trae el set completo denormalizado; el cliente no consulta el pool aparte. Si el id empieza con `p_custom_` / `c_custom_`, el contenido es texto libre y el motor downstream lo interpreta.
- **`equipo.armas[]`**: deliberadamente minimal. Solo `nombre` y `categoria_alcance`. **Sin** origen, **sin** nota, **sin** estado. Si el motor necesita más, va en `extras` o en una entrada del `historial` (ej. `captura_equipo` con descripción rica).
- **`equipo.equipo_tactico`**: array de objetos `{nombre, descripcion}`. Open: granadas, prismáticos, radio, vendaje, lo que sea.
- **`vinculos[].ref_personaje_id`**: la API **no valida** que el id exista. Esto permite vínculos con personajes que aún no están canonizados, o con NPCs externos. El campo `descripcion` es el fallback obligatorio.
- **`historia`**: prosa biográfica original. En creación efímera la genera el LLM. En la canonización **se congela** y no muta nunca. La biografía posterior (qué le pasó después) se reconstruye desde `historial[]`.
- **`historial[]`**: solo hitos importantes. No es un log detallado de batalla — eso lo lleva el motor en su propio almacenamiento. El historial de la API responde "¿qué cosas le pasaron a este personaje que vale la pena recordar?".
- **`metadatos.modelo_prosa`**: trazabilidad. Útil para auditar drift narrativo y para saber qué generación de modelo está congelada en cada canonizado.
- **`extras`**: escape hatch deliberado. Cualquier consumidor puede adjuntar campos sin pedir cambio de schema. La API no los inspecciona.
- **`version_canon` (ELIMINADO)**: la v0.1.0 lo proponía. Se elimina. El schema no se versiona en el payload; se extiende sin romper, y los consumidores se adaptan por tolerancia (campos nuevos, valores nuevos en enums).

### 6.3. Ejemplo 1 — Confederado (mock canonizado con historia acumulada)

```yaml
personaje:
  id: mock.confederacion.01.aguirre
  origen: mock
  semilla: mock-fixed-01

  nombre: Sargento Walter Aguirre
  edad: 28
  genero: masculino

  faccion: Confederación
  rol: Sargento (Líder de escuadra)
  rol_id: lider_escuadra
  tag_rol: [líder, sargento]

  origen_geografico:
    region: Patagonia Norte
    localidad: Neuquén

  apariencia:
    altura: medio
    complexion: atletico
    rasgos:
      - pelo castaño corto
      - barba de tres días
      - mirada que se demora en las cosas
    cicatrices:
      - corte vertical sobre la ceja izquierda (Sector 12,15)

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
    armas:
      - nombre: Fusil FAL
        categoria_alcance: media
      - nombre: Pistola reglamentaria M9
        categoria_alcance: corta
    equipo_tactico:
      - nombre: prismáticos militares
        descripcion: "Trofeo del Sector 12,15. Lente derecha rajada pero usable."
      - nombre: cuaderno de campaña
        descripcion: "Anotaciones de terreno, marcas de Ricardo en las primeras hojas."

  fza_aportada: 2

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
      tipo: captura_equipo
      descripcion: "Recuperó los prismáticos del oficial enemigo abatido en la cresta norte."
      ref_batalla: "batalla_cresta_norte"
      metadata:
        item: "prismáticos militares"
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
  tags_iniciales: [líder, sargento]

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

  nombre: Camarada Puntero Ramón Mansilla
  edad: 34
  genero: masculino

  faccion: Ejército Rojo
  rol: Camarada Puntero (Líder de escuadra)
  rol_id: lider_escuadra
  tag_rol: [líder, sargento]

  origen_geografico:
    region: Pampa Bonaerense
    localidad: Bahía Blanca

  apariencia:
    altura: alto
    complexion: delgado
    rasgos:
      - pelo entrecano corto
      - lentes de armazón fino reforzado con alambre
      - habla pausada, voz grave
    cicatrices: []

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
    armas:
      - nombre: Subfusil Halcón
        categoria_alcance: corta
      - nombre: Pistola Browning
        categoria_alcance: corta
    equipo_tactico:
      - nombre: cuaderno de notas
        descripcion: "Anotaciones de campaña y borradores de comunicados."
      - nombre: brújula de oficial
        descripcion: "Regalo del instructor de Stroeder."

  fza_aportada: 2

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
  tags_iniciales: [líder, sargento]

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
5. Derivar campos determinísticos (atributos, tag_rol, fza_aportada, armor, categoría de armas).
6. Sortear campos narrativos (nombre, edad, género, origen geográfico, apariencia mínima, concepto, perk fijo, complicación fija, arma concreta).
7. Inicializar bloques vacíos donde corresponde (`lealtades.secretos: []`, `vinculos: []`, `historial: []`, `equipo_tactico: null` o ítem mínimo).
8. Generar `historia` con LLM, anclada en facción + rol + concepto + perk + complicación + origen geográfico + edad.

### 7.2. Atributos, `tag_rol` y `fza_aportada` (determinísticos)

Tabla tomada de `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md`. **No se sortean.**

| `rol_id` | Rol (Confederación) | Rol (Ejército Rojo) | FIS | TAC | MEN | FZA | `tag_rol` |
|---|---|---|---|---|---|---|---|
| `lider_escuadra` | Sargento | Camarada Puntero | 3 | 5 | 7 | 2 | `[líder, sargento]` |
| `segundo_mando` | Cabo Primero | Segundo Camarada | 3 | 5 | 6 | 2 | `[líder]` |
| `apuntador` | Apuntador | Tirador | 3 | 5 | 5 | 2 | `[apuntador]` |
| `artillero` | Artillero FAP | Ametrallador | 3 | 4 | 3 | 2 | `[artillero]` |
| `fusilero` | Fusilero / Soldado 1ª | Miliciano Veterano | 3 | 3 | 3 | 1 | `[infantería]` |
| `recluta` | Recluta / Soldado 2ª | Voluntario | 3 | 2 | 2 | 1 | `[recargador]` |

**Distribución por escuadra de 11**: 1 + 1 + 1 + 1 + 4 + 3. FZA total: 15.

**Sorteo de rol cuando no se fija**: proporcional a la composición (la API tiende a entregar fusileros/reclutas, lo cual es realista).

### 7.3. `nombre` (sorteo de tablas curadas por facción)

Tabla curada de nombres argentinos, segmentada por facción.

- **Confederación**: tono militar formal, gentilicios del centro/norte/cuyo (Córdoba, Mendoza, Neuquén, Buenos Aires), apellidos hispano-criollos. Ejemplos canon en uso: *Aguirre, Sosa, Quiroga, Funes, Rodríguez, Olivares, Acosta, Pereyra, Méndez, Lugones, Ramírez*.
- **Ejército Rojo**: tono obrero/patagónico, apellidos con presencia mapuche y costa sur (Bahía Blanca, Stroeder, Comodoro, Bariloche). Ejemplos canon en uso: *Mansilla, Iturra, Antinao, Calfucurá, Cárcamo, Paine, Soriano, Belenchini, Bordón, Maturana, Bordagaray*.

El pool **excluye** los 22 ya canonizados para evitar duplicados con mocks. El prefijo de rol se prepone determinísticamente.

### 7.4. `edad`, `genero`, `origen_geografico`

- **`edad`**: sorteo en rango sugerido por `rol_id` (reclutas: 18–24; fusileros: 20–35; líderes: 28–45). Tabla curada.
- **`genero`**: sorteo según distribución curada por facción (Confederación: ~85% masculino, ~15% femenino; Ejército Rojo: ~70% masculino, ~25% femenino, ~5% no-binario por presencia obrera/sindical mixta). Valores sugeridos: `masculino`, `femenino`, `no_binario`, `otro`. La distribución es ajustable a futuro sin tocar schema.
- **`origen_geografico`**: tabla curada `(region, localidad)` por facción. Bahía Blanca, Stroeder, Comodoro, Bariloche para Ejército Rojo. Neuquén, Mendoza, Córdoba, Buenos Aires interior para Confederación.

### 7.5. `apariencia`

- **En generados dinámicamente**: mínimo viable. `altura` y `complexion` sorteadas de tablas curadas; `rasgos` con 2-3 items de pool corto por facción; `cicatrices: []` vacío.
- **En mocks**: rica, escrita a mano.
- **En canonizados**: hereda del generado o del body, muta vía hitos (ej. una herida agrega una cicatriz).

La inversión en estructura es deliberada (ver sección 13).

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

La clasificación natural/no-natural por rol vive como metadato en cada entrada del pool: `roles_naturales: [lider_escuadra, segundo_mando]`. Open: cualquier perk nuevo se etiqueta al crearse.

### 7.9. `equipo.armor`

Tabla determinística:

| `rol_id` | armor |
|---|---|
| `lider_escuadra` | 1 |
| `segundo_mando` | 1 |
| `apuntador` | 1 |
| `artillero` | 0 |
| `fusilero` | 0 |
| `recluta` | 0 |

Ejército Rojo aplica techo `armor` máximo 1 (doctrina anti-equipamiento pesado).

### 7.10. `equipo.armas`

Tabla curada `rol_id × faccion`. Cada celda contiene 1–2 armas + variantes por categoría de alcance.

| `rol_id` | Confederación (default) | Ejército Rojo (default) |
|---|---|---|
| `lider_escuadra` | Fusil FAL + Pistola reglamentaria | Subfusil Halcón + Pistola |
| `segundo_mando` | Fusil FAL + Pistola reglamentaria | Subfusil o Fusil ligero + Pistola |
| `apuntador` | Fusil de precisión (larga) | Fusil de cerrojo Mauser (larga) |
| `artillero` | FAP (media) | Ametralladora ligera (media) |
| `fusilero` | Fusil FAL (corta/media) | Fusil Mauser (larga) o subfusil (corta) |
| `recluta` | Fusil FAL (corta) | Lo que haya disponible |

Solo `nombre` y `categoria_alcance` van al payload. El resto (origen, captura, estado) se materializa como entrada del `historial` si aplica.

### 7.11. `equipo.equipo_tactico`

- **En generados**: 50% `null`, 50% 1 ítem genérico ("vendaje", "cantimplora").
- **En mocks y canonizados**: hasta 3-4 ítems narrativos.

### 7.12. `vinculos` y `historial`

- **En generados dinámicamente**: ambos vacíos (`vinculos: []`, `historial: []`). El personaje efímero todavía no tuvo tiempo de vivir.
- **En mocks**: se inicializan con el contenido escrito a mano (ver ejemplos 6.3 y 6.4).
- **En canonizados**: heredan del generado/body inicial; el motor downstream los puebla vía `POST /character/{id}/event` (sección 10).

### 7.13. `historia` (LLM)

Prosa de 120–200 palabras. Generada por un modelo de Workers AI con prompt que recibe:

- `faccion` (con descriptor de lore de `/Dev/syv-battle-game-system/lore/universo.md`).
- `rol` narrativo + `concepto`.
- `perk_fijo.nombre` y `complicacion_fija.nombre`.
- `nombre`, `edad`, `genero`, `origen_geografico` (para que la prosa los respete).
- Instrucción de tono: militar, austero, sin marketing, sin épica fácil, voz rioplatense, 2–3 párrafos.

Para reproducibilidad bajo `?seed=`:

1. Clave de cache = `hash(seed + inputs + version_modelo)`.
2. Si hay hit, se retorna la prosa cacheada.
3. Si no, se llama al modelo con `temperature` fija y se persiste.

Si el personaje se canoniza, la prosa pasa al campo `historia` del registro persistente y queda **inmutable**. Cambiar el modelo después no afecta a los canonizados existentes.

### 7.14. `tags_iniciales` y `estado_salud`

- `tags_iniciales` = copia de `tag_rol` al momento de creación (preservado para auditoría aunque después el personaje cambie de rol).
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
- `equipo.armor`, `equipo.armas`, `equipo.equipo_tactico` (vía `captura_equipo`, `perdida_equipo`).
- `vinculos[]` (vía `formacion_vinculo`, `ruptura_vinculo`).
- `lealtades.secundarias`, `lealtades.secretos` (vía `cambio_lealtad`).
- `apariencia.cicatrices` (vía `herida` grave).
- `rol`, `rol_id`, `tag_rol`, `fza_aportada` (vía `ascenso` o `traslado` — `tag_rol` y `fza_aportada` se realinean al nuevo rol; los atributos `{fis,tac,men}` no se tocan).
- `estado_salud` (vía `herida`, `baja`, `recuperacion`).
- `metadatos.ultima_actualizacion` (siempre).

**Inmutables** (definen la identidad del canonizado):

- `id`.
- `nombre`.
- `genero`.
- `origen_geografico` (region y localidad de nacimiento — no cambia aunque el personaje se mude).
- `semilla` original.
- `historia` (prosa biográfica congelada al canonizar).
- `metadatos.creado_en`, `metadatos.canonizado_en`, `metadatos.modelo_prosa`, `metadatos.es_canon`.
- `tags_iniciales` (snapshot de tags al crear; auditoría).

**`edad`**: **mutable** vía modificación directa (decisión narrativa explícita del curador). No hay mecánica de envejecimiento ni hito formal asociado; `cumpleanos` y `paso_del_tiempo` quedan eliminados del vocabulario canon (ver 9.5).

**`apariencia.rasgos`, `apariencia.altura`, `apariencia.complexion`**: por defecto **inmutables** salvo cicatrices (que sí mutan). Ver Open Question #3 (sección 14).

### 9.4. Granularidad del historial

- Solo hitos importantes. El motor de batalla lleva su propio log detallado de combate (turnos, dados, daños) aparte. El `historial[]` del personaje responde a "¿qué cosas le pasaron que vale la pena recordar en su ficha?".
- **Sin límite de tamaño.** El `historial[]` viaja inline completo en la respuesta. Se asume que "solo hitos importantes" lo mantiene acotado en la práctica. Si en producción algún canonizado supera ~100 entradas y la latencia se vuelve perceptible, se reevalúa en ese momento. No hay paginación en v1.

### 9.5. Tipos de hito (canon sugerido — abierto)

El campo `tipo` admite cualquier string. El canon **sugiere** un vocabulario para que motor, redactor y sitio de lore hablen el mismo idioma:

| `tipo` | Disparador típico | Efecto sobre campos vigentes |
|---|---|---|
| `triple_cero` | Motor (regla mecánica) | `atributos.<atributo> += 1` (techo 5, MEN-líder 7); `metadata: { atributo, delta, valor_anterior, valor_nuevo }` |
| `mejora_atributo` | Narrador (decisión externa) | igual a `triple_cero` pero sin disparador mecánico |
| `ascenso` | Narrador | `rol`, `rol_id`, `tag_rol`, `fza_aportada` se reemplazan; atributos `{fis,tac,men}` NO se tocan; `metadata: { rol_id_anterior, rol_id_nuevo }` |
| `traslado` | Narrador | `rol` y/o `rol_id` (si cambia función); `tag_rol` y `fza_aportada` se realinean al nuevo rol; atributos `{fis,tac,men}` NO se tocan |
| `herida` | Motor o narrador | `estado_salud: "herido"`; opcionalmente `apariencia.cicatrices += [...]` |
| `baja_temporal` | Motor | `estado_salud: "baja"` |
| `recuperacion` | Motor o narrador | `estado_salud: "activo"` |
| `captura_equipo` | Motor o narrador | append a `equipo.armas` o `equipo.equipo_tactico`; `metadata: { item }` |
| `perdida_equipo` | Motor o narrador | remove de `equipo.armas` o `equipo.equipo_tactico` |
| `formacion_vinculo` | Narrador | append a `vinculos[]`; `metadata: { vinculo_creado }` |
| `ruptura_vinculo` | Narrador | remove o transformación de `vinculos[]` |
| `cambio_lealtad` | Narrador | mutación de `lealtades.secundarias` o `lealtades.secretos` |
| `mejora_aspecto` | Narrador | reemplazo de `aspectos.concepto`, `perk_fijo` o `complicacion_fija` |
| `condecoracion` | Narrador | no muta campos vigentes (queda como hito puro) |

El motor o el narrador pueden emitir tipos custom; la API los acepta y los apendea al historial. El efecto sobre campos vigentes solo ocurre para los tipos conocidos; tipos custom **no mutan** la ficha (quedan como hito puro).

**Nota sobre atributos y rol_id.** Los atributos `{fis, tac, men}` son **propiedad del personaje**, no derivados del rol_id post-creación. Cuando un personaje cambia de `rol_id` (por ascenso, traslado u otro hito), los atributos vigentes no se tocan: el personaje no pierde ni resetea lo que ganó. `tag_rol` y `fza_aportada` sí se realinean a la matriz del nuevo rol (son etiquetas mecánicas del rol vigente, no propiedad del personaje). La matriz determinística por rol (sección 7.2) aplica **únicamente** en el momento de creación.

---

## 10. Endpoints (alto nivel)

Cada entrada describe la intención y el shape, no la implementación.

### `GET /character`

Genera un personaje efímero. Parámetros opcionales:

- `faccion`: `confederacion` | `ejercito_rojo`
- `rol_id`: uno de los 6 sugeridos
- `seed`: string libre
- `fields`: lista separada por comas para podar la respuesta (ver `GET /character/{id}`)

Devuelve un `personaje` con `origen: "generado"`, `id: null`, `es_canon: false`, `historial: []`, `vinculos: []`, `metadatos.canonizado_en: null`.

Mapea: UC-01..04, UC-06, UC-16.

### `GET /character/{id}`

Devuelve el personaje con id exacto. Funciona para mocks (`mock.*`) y canonizados (`canon.*`). Devuelve 404 si no existe.

Parámetros opcionales:

- `fields`: lista separada por comas (ej. `?fields=id,nombre,atributos,equipo`). Permite podar el payload. Si no se pasa, devuelve la ficha completa, incluido `historial[]` inline.

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

Lista los 22 fixtures con `id`, `nombre`, `faccion`, `rol_id`, `rol`. Sin payload completo.

Mapea: UC-08.

### `POST /canonize`

Toma un personaje generado (vía body con la ficha completa + seed) y lo persiste como canon **en el almacenamiento de la API**. Asigna `id` estable (`canon.{ulid}`), cambia `origen` a `"canonizado"`, marca `metadatos.es_canon: true`, fija `metadatos.canonizado_en`. La prosa de `historia` se congela en este momento.

**Idempotencia.** `POST /canonize` es idempotente por la tripleta `(seed, faccion, rol_id)`. Si se llama dos veces con los mismos parámetros, se devuelve el id del primero canonizado en lugar de crear uno nuevo. Si un curador quiere dos versiones distintas del mismo arquetipo, debe variar la seed o el rol_id.

**Explícito:** este endpoint nunca toca `/Dev/syv-battle-game-system/personajes/`. Nunca abre PRs. Los canonizados son un universo de la API; los mocks Markdown del battle-system son un universo paralelo.

Mapea: UC-07.

### `GET /meta/factions`

Devuelve el catálogo de facciones con descriptor de lore corto.

### `GET /meta/roles`

Devuelve los 6 `rol_id` sugeridos con su tabla de stats, `tag_rol`, `fza_aportada`, `armor` y nombres narrativos por facción.

### `GET /meta/perks` y `GET /meta/complications`

Devuelven los pools canon vigentes. Cada entrada incluye `id`, `nombre`, `condicion`, `efecto`, `roles_naturales` (lista de `rol_id` para los que el perk es "natural" en la restricción 80/20).

### `GET /meta/hito_types`

Devuelve los tipos de hito sugeridos (tabla 9.5) con su descriptor de efecto. **Importante**: estos son **sugeridos**, no exhaustivos. Cualquier motor puede emitir un `tipo` custom y la API lo registra en el historial sin aplicar mutación.

### `GET /meta/vinculo_types`

Devuelve los tipos de vínculo sugeridos (mentor, subordinado, hermano_de_armas, rival, deuda, enemigo_jurado, familia, romance). Mismos términos: sugeridos, no exhaustivos.

Mapea (todos los `/meta/*`): UC-09.

---

## 11. Los 22 mock — alcance del MVP

Los 22 personajes iniciales son fixtures versionadas en `mock/personajes/{faccion}/{nn}_{rol}_{apellido}.yaml`, escritos al schema v0.2.0 (con `apariencia`, `lealtades`, `vinculos`, `historial` poblados a mano). Su contenido base proviene del Markdown canon de `/Dev/syv-battle-game-system/personajes/`; el MVP los **importa y enriquece** para el schema nuevo.

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

**Composición.** El reglamento local define la escuadra como **1 + 1 + 1 + 1 + 4 + 3**. El PRD adopta esta composición porque es la que ya existe en el canon. Si el reglamento migra a otra, primero se cambia el reglamento, después el PRD, después se regenera el set de mocks.

**Nota sobre mutabilidad de mocks.** Los mocks son **inmutables** desde la API (`POST /character/{id}/event` sobre un mock devuelve 409). Su evolución, si la hay, ocurre por reescritura manual del fixture YAML y un release de la API. Esto los distingue de los canonizados, que evolucionan vía evento.

---

## 12. Alcance MVP vs futuro

### Dentro de v1

- 2 facciones jugables: Confederación y Ejército Rojo.
- 6 `rol_id` con su matriz determinística.
- Pools canon de perks (12) y complicaciones (10) con metadato `roles_naturales`.
- Tablas curadas de nombres, edades, géneros, orígenes geográficos, conceptos, armas, equipo táctico mínimo por facción.
- Generación efímera con seed reproducible.
- 22 mocks importados, enriquecidos al schema v0.2.0 (con apariencia, lealtades, vínculos, historial escritos a mano).
- Canonización persistente (solo DB de la API; no toca battle-system).
- **Memoria viva**: endpoint de evento, mutación de campos vigentes, historial inline.
- **Aspectos mutables, vínculos mutables, equipo mutable** sobre canonizados.
- **Apariencia estructurada** (sobre-diseñada para soldados, lista para futuro).
- **Lealtades estructuradas** con secretos.
- **Customs libres** (`p_custom_*`, `c_custom_*`) en perks y complicaciones.
- **Extras** libres al top level.
- **Enums abiertos** con catálogos `/meta/*` que sugieren valores.
- Endpoints `/meta/*` para introspección del canon (incluye `hito_types` y `vinculo_types`).
- Restricción 80/20 soft de perks por rol.
- Poda de respuesta con `?fields=`.

### Explícitamente fuera de v1

- Las 3 facciones secundarias (Pueblos del Pantano, Los Salvajes, Los Poseídos): existen en lore, no se generan ni se sirven.
- PJs civiles (la apariencia sobre-diseñada queda esperando este caso).
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
- Operación "diff entre estado original y estado vigente" (la `semilla` se preserva pero no hay endpoint que reconstruya).

---

## 13. Tensiones explícitas y compromisos asumidos

Esta sección documenta decisiones que el PRD toma sabiendo que tienen un costo. No son problemas a resolver: son trade-offs aceptados.

### 13.1. Customs libres + enums abiertos → motor downstream interpreta contenido libre

**Decisión.** El producto acepta `perk_fijo`/`complicacion_fija` con id `p_custom_*` y descripción en texto libre. Acepta `tipo` de hito y `tipo` de vínculo con valores fuera del canon sugerido. Acepta `extras` no validado.

**Costo.** El motor de batalla que consuma un canonizado con `perk_fijo.id = p_custom_eco_del_penasco` no tiene mecanismo formal para entender su efecto. La interpretación queda a su cargo (probablemente vía LLM al momento de aplicar la regla, o vía intervención humana).

**Por qué se acepta.** La alternativa — exigir que todo perk pase por el pool oficial — paralizaría la creación de personajes notables y forzaría a "embutir" sabor narrativo en perks genéricos. El producto es un generador de **personajes con identidad**, no de fichas mecánicas intercambiables. El motor downstream tiene que poder lidiar con la riqueza que el producto habilita.

**Mitigación.** El catálogo `/meta/perks` siempre devuelve la versión "oficial" para que el motor tenga un fallback de comparación. Los customs llevan prefijo `p_custom_*` / `c_custom_*` para ser fácilmente detectables.

### 13.2. Apariencia estructurada para soldados → sobre-diseño consciente

**Decisión.** El bloque `apariencia` tiene altura, complexión, rasgos y cicatrices estructurados. Para soldados — el caso del MVP — esto es más granularidad de la que el motor necesita.

**Costo.** Más campos a llenar, más sorteo, más mantenimiento de pools. Para la generación efímera, varias entradas son ruido.

**Por qué se acepta.** El producto se proyecta a PJs civiles, a una galería visual en el sitio público, y a una capa narrativa donde "tiene una cicatriz vertical sobre la ceja" sí importa. Es inversión futura. Estructurar ahora — mientras hay 22 mocks y cero canonizados — es barato; estructurar después implicaría migrar.

**Mitigación.** En generados, la apariencia se llena al mínimo (altura, complexión, 2-3 rasgos, sin cicatrices). El campo es estructuralmente rico pero operacionalmente liviano por default.

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

**Mitigación.** La `semilla` original se preserva en el campo `semilla`. Una herramienta externa puede tomar `(semilla, faccion, rol_id)` y regenerar el "estado en el momento de la creación" para comparar — pero esto no es operación soportada por la API en v1. Para efímeros la promesa se mantiene intacta.

---

## 14. Open questions v0.2.1

Preguntas reales que esta versión deja abiertas para la próxima iteración. Las OQs cerradas en v0.2.1 (#1 edad, #3 historial, #5 rol_id atributos, #7 idempotencia) fueron incorporadas como decisiones en las secciones correspondientes.

1. **Gobernanza de `POST /character/{id}/event`.** ¿Quién puede llamarlo? El motor de batalla obvio (para `triple_cero`, `herida`, `baja`). ¿Pero un redactor narrativo puede emitir `ascenso` o `cambio_lealtad` desde cualquier cliente? Sin auth en v1, en la práctica cualquiera con la URL puede. Decidir si esto se atemporaliza con tokens, lista blanca de orígenes, o si se acepta porque el corpus de canonizados es pequeño y curable a mano.

2. **Mutabilidad fina de `apariencia`.** Cicatrices mutan (claro). ¿Pero una herida grave puede mutar `complexion` ("queda enjuto tras la convalecencia")? ¿Los rasgos son absolutamente inmutables o pueden modificarse vía hito narrativo explícito? El PRD los marca inmutables por default, sabiendo que es debatible.

3. **Interpretación de customs por el motor.** ¿El motor de batalla se compromete a interpretar `p_custom_*` con un LLM al momento de aplicar la regla, o existe un workflow donde un curador humano traduce el custom a una regla mecánica antes de que el personaje entre a batalla? Esta tensión está documentada (13.1) pero el flujo operacional concreto queda abierto.

4. **Persistencia de `semilla` vs entidad viva.** La `semilla` se preserva post-canonización para trazabilidad. ¿Es útil exponer un endpoint `GET /character/{id}/original` que regenere la ficha al estado de creación (sin historial) para que herramientas externas puedan calcular el diff? Fuera de v1 pero útil para auditoría narrativa.

---

*Fuentes canónicas referenciadas (no copiadas):*

- `/Dev/syv-battle-game-system/reglamento/02_hoja_personaje.md` — esquema y matriz de stats por rol.
- `/Dev/syv-battle-game-system/reglamento/03_atributos_perks.md` — pools de perks y complicaciones.
- `/Dev/syv-battle-game-system/lore/universo.md` — descriptores de facción usados como contexto del LLM.
- `/Dev/syv-battle-game-system/personajes/` — 22 fichas canon base que alimentan los mocks (enriquecidos al schema v0.2.0 en el repo de la API).
- `https://github.com/kodexArg/syv-game-system/blob/main/arquitectura/esquemas/personaje.schema.json` — schema público de referencia.
