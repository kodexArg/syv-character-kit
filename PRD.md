# PRD — syv-character-kit

> **El producto es documentación, no una aplicación.** Este kit entrega la especificación completa necesaria para que cualquier equipo construya un sistema de personajes y combate de escuadras del universo *Subordinación y Valor* (SyV) — sin imponer lenguaje, framework, infraestructura ni stack.
>
> Sólo se admiten scripts mínimos como apoyo a la documentación (ej. samplers de referencia), **todos sujetos a futura eliminación**. No hay servidor, no hay UI, no hay base de datos en este repo. Hay archivos: schemas, catálogos, protocolos, mocks y reglas.
>
> Idioma: castellano rioplatense, voseo sobrio. Tags en notación punto. Payloads YAML en `snake_case_castellano`.

---

## 1. Propósito

Este PRD ordena el trabajo de documentar **cinco entregables**:

1. **Protocolo y reglas de construcción de personaje.** Schema, mutabilidad, derivaciones, sistema de tags.
2. **Generador procedural con elementos estocásticos.** Algoritmo determinístico por rango + sampler de identidad + prosa LLM.
3. **Contrato de API CRUD.** Endpoints, payloads, formas dinámicas; agnóstico al runtime.
4. **Estructura MOCK inicial.** Dos escuadras casi simétricas (Confederación Argentina y Ejército Rojo), 11 personajes cada una, que sirven de plantilla viva para futuros ejércitos.
5. **Reglas del motor de batalla y encuentros — alcance squad vs squad.** Sistema balanceado, comprensible, **replicable en papel**, escrito como protocolos.

Lo que se entrega es la documentación que permite construir todo lo anterior. La aplicación es responsabilidad de otro proyecto.

### 1.1. Contexto del universo SyV

El kit existe dentro del universo de *Subordinación y Valor*. Contexto mínimo necesario para que las decisiones de schema y motor de batalla mantengan fidelidad al lore — detalle completo en las fuentes canónicas al pie:

- **Año 2178.** La guerra arrastra dieciocho años. El frente es la **Zanja de Alsina**, una franja de tierra arrasada que cruza el Valle de la Patagonia. Niebla helada, comunicaciones rotas, ningún bando logra ruptura.
- **Confederación Argentina (azul).** Estado centralizado con base en **Ciudad Dársena**. Ejército Confederado: escuadras regulares de once, lideradas por un Sargento, cadena de mando formal.
- **Ejército Rojo (rojo).** Conglomerado de milicias obreras y portuarias nacidas de la revolución fabril de **Bahía Blanca**. Sin uniformes estandarizados. Cada célula obedece a un **Camarada Puntero** elegido por convicción política más que por rango.
- **Anatema Mecánico.** Prohibición universal de tecnología avanzada. Ambos bandos lo cumplen — la Confederación por decreto (Inquisición y Exorcistas), el Ejército Rojo por doctrina. **El kit asume el Anatema:** no hay drones, no hay computación en campo, no hay armamento "smart". Las armas son mecánicas; la coordinación es voz, gesto y banderín.
- **Tres facciones secundarias** existen en el lore (Pueblos del Pantano, Salvajes, Poseídos) pero **están fuera del MVP** del kit.

---

## 2. Mapa de artefactos

| Archivo | Propósito | Estado |
|---|---|---|
| [`PRD.md`](PRD.md) | Este documento. Visión y mapa. | vigente |
| [`API.md`](API.md) | Contrato HTTP. Fuente de verdad de endpoints. | vigente |
| [`MODEL.md`](MODEL.md) | Contrato de persistencia. Entidades, tipos, constraints. | vigente |
| [`AGENTS.md`](AGENTS.md) | Política editorial y convenciones. | vigente |
| [`docs/hoja-modelo.md`](docs/hoja-modelo.md) | Schema del personaje campo por campo. | vigente |
| [`docs/hoja-modelo.yaml`](docs/hoja-modelo.yaml) | Template programático vacío. | vigente |
| [`docs/tag-modelo.md`](docs/tag-modelo.md) | Sistema de tags: notación, categorías, catálogo. | vigente |
| [`docs/tag-modelo.yaml`](docs/tag-modelo.yaml) | Template de entrada de catálogo. | vigente |
| [`docs/tag-modelo-ejemplos.yaml`](docs/tag-modelo-ejemplos.yaml) | Cinco personajes ejemplo compuestos. | vigente |
| [`docs/tag-requeridos-por-categoria.md`](docs/tag-requeridos-por-categoria.md) | Índice rápido de campos `(+)` por categoría. | vigente |
| [`docs/atributos-y-efectos.md`](docs/atributos-y-efectos.md) | Vocabulario canónico de atributos y stats calculadas. | vigente |
| [`docs/user-stories.md`](docs/user-stories.md) | Catálogo de UCs ↔ endpoints. | vigente |
| [`docs/open-questions.md`](docs/open-questions.md) | Tensiones asumidas, OQs, notas de arquitectura. | vigente |
| [`gddr/01-flujo-obligatorio-creacion.md`](gddr/01-flujo-obligatorio-creacion.md) | Orden canónico de creación de personaje. | vigente (Fase 4 pendiente) |
| `gddr/02-motor-batalla.md` | Reglas de combate squad vs squad. | **pendiente** |
| [`mock/personajes/`](mock/personajes/) | 22 fixtures canon (dos escuadras). | parcial (ver §5) |
| [`tags/`](tags/) | Catálogo curado, sembrado por categoría. | vigente |
| [`resources/nombres/`](resources/nombres/) | Pools de nombres + apellidos. | vigente |
| [`scripts/`](scripts/) | Samplers de referencia. **Sujeto a eliminación.** | provisional |

Toda referencia desde el PRD a un detalle del schema, del flujo o del motor se hace por link al archivo correspondiente. **El PRD no duplica reglas.**

---

## 3. Principios de diseño

- **El PRD es contrato; el repo es la documentación.** Este documento define forma y alcance. Cómo se implemente, dónde corra, qué stack use — fuera de scope.
- **SOLID y open/close.** El schema extiende sin romper. Nuevos perks, tipos de hito, categorías de tag, facciones — sin migraciones, sin breaking changes.
- **Tags como modelo de primera clase.** *Lo que puede ser tag, es tag.* Rasgos, skills, traits, perks, equipo, lealtades a facciones/escuadras. La frontera con los campos estructurales (`identidad`, `atributos`, `aliados`, `nemesis`, `historial`, `historia`, `metadatos`) está fijada en [`docs/hoja-modelo.md`](docs/hoja-modelo.md) y [`docs/tag-modelo.md`](docs/tag-modelo.md).
- **Customs libres + enums abiertos.** El producto acepta tags, sub-categorías y tipos de hito fuera del canon. El motor downstream interpreta. Tensión documentada en [T-01](docs/open-questions.md).
- **Stats determinísticos por rango; identidad sorteada.** En creación, `{fis, tac, men}` se derivan de una tabla fija ([GDDR-01 §3](gddr/01-flujo-obligatorio-creacion.md)). Cero aleatoriedad en stats. Nombre, género, edad, rasgos, skills/traits/perks, equipo e historia sí se sortean.
- **Memoria viva como naturaleza del canonizado.** Un canonizado existe en el tiempo: nace, pelea, cambia. La ficha vigente no es la original. Mutaciones vía hitos en `historial[]`.
- **Reproducibilidad por seed para efímeros.** `(seed, faccion, rango)` produce el mismo personaje. Los canonizados pierden esta propiedad tras el primer hito ([T-05](docs/open-questions.md)).
- **LLM solo para prosa, solo una vez.** El modelo generativo escribe `historia` en la creación. Al canonizar, se congela.
- **Mocks separados de canonizados.** Los 22 mocks son fixtures inmutables; los canonizados son entidades vivas de la API. No hay sincronización ni promoción mock → canonizado.
- **Agnosis al renderer.** El schema describe *qué* tiene un personaje, no *cómo* se muestra. Las categorías de tag son metadato semántico, no instrucción de presentación.
- **Agnosis al sistema de azar.** Todas las probabilidades y modificadores se expresan en **porcentaje** sobre atributos en escala 0–9. Cualquier sistema de resolución (dados, cartas, digital) puede mapearlo a su moneda local. Ver [`AGENTS.md`](AGENTS.md) §"Aleatoriedad".
- **GDDR como puente de diseño.** El diseño de juego precede al software. Las decisiones de mecánicas y uso de recursos viven en [`gddr/`](gddr/) y se referencian con los schemas/catálogos.

---

## 4. Schema y reglas

**Forma de la hoja**: seis bloques estructurales (`identidad`, `atributos`, `historia`, `historial`, `aliados`, `nemesis`, `metadatos`, `extras`) más la lista plana `tags[]`. Definición autoritativa: [`docs/hoja-modelo.md`](docs/hoja-modelo.md).

**Sistema de tags**: notación punto `<categoria>[.<subcategoria>].<slug>`, multiset, catálogo extensible, `requires` como documentación ejecutable. Definición autoritativa: [`docs/tag-modelo.md`](docs/tag-modelo.md).

**Mutabilidad**: el estado vigente del canonizado cambia vía hitos en `historial[]`. Tabla de campos mutables / inmutables / derivados en [`docs/hoja-modelo.md §8`](docs/hoja-modelo.md). Catálogo sugerido de `tipo` de hito en [`docs/hoja-modelo.md §5`](docs/hoja-modelo.md). Los hitos `agregar_tag` / `quitar_tag` son el mecanismo central de evolución.

**Atributos y stats calculadas**: vocabulario canónico (`FISICO`, `TACTICO`, `MENTAL`, `INICIATIVA`, `MORAL`, `FATIGA`, `MOVIMIENTO`, `ESTRESS`) y su semántica de combate en [`docs/atributos-y-efectos.md`](docs/atributos-y-efectos.md). Los efectos de los tags se declaran contra este vocabulario.

**Generador procedural**: flujo obligatorio de creación, fases, sorteos ponderados, tabla determinística por rango en [`gddr/01-flujo-obligatorio-creacion.md`](gddr/01-flujo-obligatorio-creacion.md).

---

## 5. Mocks — dos escuadras canon

22 personajes, distribuidos en dos escuadras simétricas. Composición de cada escuadra: 1 + 1 + 1 + 1 + 4 + 3 (líder, segundo, apuntador, artillero, 4 fusileros, 3 reclutas). FZA total de escuadra completa: 2+2+2+2+(4×1)+(3×1) = **15** (derivado de `rol.combate.*` — ver §4). Fixtures en `mock/personajes/{faccion}/{nn}_{rango}_{apellido}.yaml`.

> **Columna `fixture_id`**: identificador del archivo en `mock/personajes/`, NO `personaje.identidad.slug`. El slug del personaje es una patente opaca `[A-Z0-9]{8}` que se asigna al persistir. La migración final de los mocks a patentes 8-char está pendiente ([OQ-12](docs/open-questions.md)).

### 5.1. Escuadra Confederación Argentina (11)

| # | `fixture_id` | Rango | Nombre canon |
|---|---|---|---|
| 01 | `mock.confederacion.01.aguirre` | `lider_de_escuadra` | Sargento Walter Aguirre |
| 02 | `mock.confederacion.02.sosa` | `segundo_al_mando` | Cabo Primero Sosa |
| 03 | `mock.confederacion.03.quiroga` | `apuntador` | Apuntador Quiroga |
| 04 | `mock.confederacion.04.funes` | `artillero` | Artillero Funes |
| 05 | `mock.confederacion.05.rodriguez` | `fusilero` | Soldado de Primera Marcela Rodríguez |
| 06 | `mock.confederacion.06.olivares` | `fusilero` | Soldado de Primera Olivares |
| 07 | `mock.confederacion.07.acosta` | `fusilero` | Soldado de Primera Acosta |
| 08 | `mock.confederacion.08.pereyra` | `fusilero` | Soldado de Primera Pereyra |
| 09 | `mock.confederacion.09.mendez` | `recluta` | Recluta Méndez |
| 10 | `mock.confederacion.10.lugones` | `recluta` | Recluta Lugones |
| 11 | `mock.confederacion.11.ramirez` | `recluta` | Recluta Ramírez |

### 5.2. Escuadra Ejército Rojo (11)

| # | `fixture_id` | Rango | Nombre canon |
|---|---|---|---|
| 12 | `mock.ejercito_rojo.01.mansilla` | `lider_de_escuadra` | Camarada Puntero Ramón Mansilla |
| 13 | `mock.ejercito_rojo.02.iturra` | `segundo_al_mando` | Segundo Camarada Iturra |
| 14 | `mock.ejercito_rojo.03.antinao` | `apuntador` | Tirador Antinao |
| 15 | `mock.ejercito_rojo.04.calfucura` | `artillero` | Ametrallador Calfucurá |
| 16 | `mock.ejercito_rojo.05.carcamo` | `fusilero` | Miliciano Veterano Fermín Cárcamo |
| 17 | `mock.ejercito_rojo.06.paine` | `fusilero` | Miliciano Veterano Paine |
| 18 | `mock.ejercito_rojo.07.soriano` | `fusilero` | Miliciano Veterano Soriano |
| 19 | `mock.ejercito_rojo.08.belenchini` | `fusilero` | Miliciano Veterano Belenchini |
| 20 | `mock.ejercito_rojo.09.bordon` | `recluta` | Voluntario Bordón |
| 21 | `mock.ejercito_rojo.10.maturana` | `recluta` | Voluntario Maturana |
| 22 | `mock.ejercito_rojo.11.bordagaray` | `recluta` | Voluntario Bordagaray |

**Inmutabilidad.** Los 22 mocks no aceptan hitos vía API (`POST /character/{slug}/event` → 409). Su evolución, si la hay, ocurre por reescritura del fixture.

**Pendiente** ([OQ-12](docs/open-questions.md)): migración final de los fixtures al modelo de lista plana de tags + patentes 8-char en `identidad.slug`.

---

## 6. API y casos de uso

**Endpoints**: definidos en [`API.md`](API.md). Si una ruta no figura ahí, no existe en el contrato. La convención `GET /meta/{categoria}` expone catálogos curados sin requerir edición del contrato cuando aparecen categorías nuevas — la dinámica del catálogo de tags se traslada al endpoint.

**Casos de uso**: catálogo de UCs (UC-01..UC-23) y mapping inverso a endpoints en [`docs/user-stories.md`](docs/user-stories.md).

**Modelo de persistencia**: entidades y constraints en [`MODEL.md`](MODEL.md). Sincronía estricta con `API.md`.

---

## 7. Motor de batalla — squad vs squad

**Entregable pendiente.** Sin documento todavía. Cuando se redacte, vivirá en `gddr/02-motor-batalla.md` y deberá:

- Definir el ciclo de turno (iniciativa → orden → resolución → desgaste).
- Especificar cómo se aplican los efectos declarados en los tags ([`docs/atributos-y-efectos.md`](docs/atributos-y-efectos.md)) durante el combate.
- Modelar la escuadra como unidad táctica: composición, `fza_aportada` agregada, moral de grupo, movimiento al ritmo del más lento.
- Establecer las condiciones de victoria/derrota de un encuentro squad vs squad.
- Ser **replicable en papel**: las reglas se escriben como protocolos secuenciales, no como pseudocódigo. Cualquier persona con la documentación debe poder arbitrar una batalla sin software.

Hasta que ese GDDR exista, las stats calculadas y su mecánica de resolución descritas en [`docs/atributos-y-efectos.md §2`](docs/atributos-y-efectos.md) son el punto de partida.

---

## 8. Alcance

### Cubierto por este PRD (entregables documentales)

- Schema completo de la hoja de personaje.
- Sistema de tags categorizado con catálogo curado y extensible.
- Vocabulario canónico de atributos y stats calculadas.
- Flujo obligatorio de creación (GDDR-01, Fases 1–3).
- 2 facciones jugables con sus subfacciones (`pelicanos`, `ejercito_revolucionario_del_pueblo`).
- 8 rangos operativos canon más `ciudadano`.
- 22 mocks (dos escuadras simétricas).
- Contrato de API HTTP (`API.md`).
- Contrato de persistencia (`MODEL.md`).
- Catálogos `/meta/*` dinámicos por categoría de tag.

### Pendiente dentro de este PRD

- GDDR-01 Fase 4 (tags adicionales, prosa, historial, metadatos en el flujo de creación).
- GDDR-02: motor de batalla squad vs squad.
- Migración final de los 22 mocks al modelo vigente ([OQ-12](docs/open-questions.md)).
- Schema completo de la entidad `escuadra` ([OQ-06](docs/open-questions.md)).

### Fuera de este PRD

- Implementación de la API (cualquier lenguaje, framework o stack).
- Persistencia concreta (motor de base, hosting, despliegue).
- Autenticación, autorización, rate limiting.
- UI, CLI de usuario final, dashboards.
- Las 3 facciones secundarias del lore.
- PJs civiles fuera del rol `ciudadano`.
- Generación de escuadras completas en una sola llamada.
- Edición arbitraria de canonizados fuera del mecanismo de hitos.
- Reverso de hitos.
- Versionado de la prosa congelada.

Cuando alguno de estos elementos se vuelva relevante, irá a un PRD separado.

---

## 9. Tensiones, open questions y arquitectura

Consolidado en [`docs/open-questions.md`](docs/open-questions.md). Tres secciones:

- **Tensiones asumidas** (T-01..T-10) — decisiones con costo conocido.
- **Open questions** (OQ-01..OQ-14) — sin decisión todavía.
- **Notas de arquitectura** (N-01..N-04) — no normativas; insumo para implementadores eventuales.

---

## 10. Política editorial

Convenciones de trabajo, identificadores, idioma, expresión de azar en porcentajes, rolling release y trato a los mocks: [`AGENTS.md`](AGENTS.md).

---

*Fuente canónica del universo (referencia de lore, no copiada):*

- [`/Dev/SyV/syv/src/content/docs/`](../syv/src/content/docs/) — documentación del universo *Subordinación y Valor*: trasfondo, atlas, personajes, diégesis, aventuras, media. **Única fuente válida** de lore del universo. Repo público: `https://github.com/kodexArg/syv`.

El kit no depende de ningún otro repo para definirse: el schema, los catálogos, las reglas de generación y las reglas del motor de batalla viven íntegramente acá. La cita al canon es para fidelidad narrativa, no dependencia técnica.
