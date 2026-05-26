# Open Questions y Tensiones — syv-character-kit

> Decisiones de producto y diseño que el [`PRD`](../PRD.md) no resuelve directamente. Tres secciones:
>
> 1. **Tensiones asumidas** — decisiones tomadas con costo conocido. No se reabren salvo evidencia nueva.
> 2. **Open questions** — sin decisión todavía. Resolver impacta el contrato.
> 3. **Notas de arquitectura** — no normativas; insumo para implementadores eventuales.
>
> Cuando una entrada se resuelve, se elimina (no se archiva — el `git log` es la historia).

---

## 1. Tensiones asumidas

### T-01 — Customs libres + enums abiertos

**Decisión.** El producto acepta tags `skill`/`trait`/`perk` con valores fuera del catálogo, y enums (`tipo` de hito, `tipo` de vínculo, sub-categorías de tag) con valores custom.
**Costo.** El motor downstream interpreta valores libres.
**Por qué se acepta.** La alternativa paralizaría la creatividad narrativa.
**Mitigación.** Los catálogos `/meta/*` exponen la versión oficial como referencia.

### T-02 — Categorías de tag abiertas

**Decisión.** Las categorías y sub-categorías jerárquicas (`equipo.arma`, `equipo.utilitario`) son extensibles sin migración.
**Costo.** Posible fragmentación semántica (`equipo.weapon` vs `equipo.arma`).
**Mitigación.** `/meta/{categoria}` documenta el canon. Los consumidores normalizan al leer.

### T-03 — Sin versionado del payload

**Decisión.** No hay campo `version_canon`. El schema se extiende sin romper.
**Costo.** Si un campo está mal diseñado, no hay herramienta de migración.
**Mitigación.** Bloques fuertemente segmentados (`extras`, enums abiertos, customs libres) absorben la mayoría de la extensión.

### T-04 — Sin validación de referencias

**Decisión.** `aliados[].ref`, `nemesis[].ref` y `escuadra_id` no se verifican.
**Costo.** Referencias colgadas posibles.
**Mitigación.** `descripcion` del vínculo es obligatorio. `filiacion` tiene fallback ("Sargento del Ejército de la Confederación Argentina" si la escuadra no resuelve).

### T-05 — Memoria viva rompe reproducibilidad post-canonización

**Decisión.** Tras el primer hito, un canonizado deja de ser regenerable desde su seed.
**Costo.** Tests reproducibles deben usar efímeros.
**Mitigación.** El `historial[]` registra cada mutación; la trayectoria puede reconstruirse hacia atrás aplicando hitos en reversa.

### T-06 — Traits sin polaridad explícita

**Decisión.** Los tags `trait` no declaran polaridad. La categoría agrupa positivos (`imperturbable`), neutros (`impredecible`) y penalidades (`cobarde`) en la misma bolsa.
**Costo.** Un cliente que filtre "solo penalidades" interpreta `efecto` para inferirlo.
**Mitigación.** El catálogo puede declarar `polaridad: positivo | neutro | penalidad` como hint sugerido pero no autoritativo. Ver [`tag-modelo.md §4.7`](tag-modelo.md).

### T-07 — Sin mecanismo de alias

**Decisión.** `Francotirador` y `francotirador` son valores distintos. No hay grafo de equivalencia.
**Costo.** Queries no encuentran sinónimos.
**Mitigación.** El generador usa el vocab del catálogo. Documentar canónicos en `/meta/*`. Normalización a lowercase es una pre-condición razonable de v1.

### T-08 — Catálogo `/meta/*` como semilla, no como autoridad

**Decisión.** El catálogo curado es vocabulario sugerido, no enum cerrado. Excepción: `equipo.vestidura` (cerrado en 4 valores).
**Costo.** Convive con T-02 y T-07: usuarios crean sinónimos.
**Mitigación.** Marcar entradas con `origen: canon | emergente | custom` para que el cliente discrimine.

### T-09 — Efectos no inlineados en el personaje

**Decisión.** Los efectos de skills/traits/perks viven en `/meta/*`, no en cada tag del personaje.
**Costo.** Un cliente con 12 tags puede necesitar 12 lookups extra.
**Mitigación.** Eventual `?expand=tags` para resolver en una sola call. Fuera de v1 estricto.

### T-10 — Tags mínimos vs riqueza contextual

**Decisión.** Los tags son **identificador** (1-2 palabras, sin prosa). El contexto narrativo vive en `historia` o en el catálogo `/meta/*`.
**Costo.** Se pierde color que vivía dentro del tag ("brújula del instructor de Stroeder" → `brujula`).
**Mitigación.** La prosa de `historia` e `historial[]` se preserva. Una eventual entidad `notas` puede capturar contexto por-instancia si aparece el caso.

---

## 2. Open questions

### OQ-01 — Personajes históricos referenciados pero no en roster

Personajes citados en `aliados[].ref` que no son canon vigente (mentores caídos, figuras del pasado). ¿Crear `mock/personajes_historicos/` con entradas mínimas (slug + nombre + breve nota) o seguir con slugs sintéticos sin entrada?

### OQ-02 — Lealtades latentes / secretas / aspiracionales

El bloque eliminado `lealtades: {primaria, secundarias, secretos}` cubría más de lo que `lealtad.*` cubre hoy. Modelos a evaluar: tags `lealtad_latente.*`, entidad nueva `intenciones[]`, o extensión vía `extras`.

### OQ-03 — Titularidad de mando vigente

`mando.capaz` indica capacidad. ¿La titularidad vigente se deriva como `mando.capaz` AND mayor `rango.*` en la misma `escuadra.*`? ¿Cómo se rompen los empates?

### OQ-04 — Nombre del campo derivado

`filiacion` vs alternativas: `designacion`, `titulo`, `pie_de_firma`.

### OQ-05 — Gobernanza de mutaciones vía API

Sin auth, cualquiera con la URL puede emitir hitos. Tokens, lista blanca, o aceptación porque el corpus es curable.

### OQ-06 — Schema de la entidad `escuadra`

El tag `escuadra.{slug}` necesita catálogo análogo a `tags/faccion/`. Definir slug canónico y campos del archivo (nombre legible, cuerpo, facción asociada, composición vigente).

### OQ-07 — Interpretación de tags custom por el motor

¿LLM al aplicar la regla, o curador humano traduce a regla mecánica antes? Relacionado con T-01.

### OQ-08 — Política de avisos cuando el generador sale del canon

El campo `skill.facciones_predominantes` está documentado ([`tag-modelo.md §4.5`](tag-modelo.md)); falta política de avisos cuando el generador sortea un tag fuera de su facción esperada.

### OQ-09 — Eviction de tags obsoletos del catálogo

Si el catálogo retira un slug, los personajes que lo tienen no se actualizan. Sin alias (T-07) no hay puente.

### OQ-10 — Cap de tags por categoría

¿Hay máximo razonable? ¿Caps internos del generador? ¿La API valida o solo advierte?

### OQ-11 — Entidad `notas` como capa enriquecida de tags

`notas: list<{tag_ref, texto}>` permitiría persistir contexto narrativo atado a un tag específico sin contaminar el slug. Relacionado con T-10.

### OQ-12 — Migración final de los 22 mocks al modelo de lista plana

Bloqueada por la decisión sobre la prosa de `vinculos[].descripcion` (mover a `historia`, a entradas de `historial` con tipo `formacion_vinculo`, o descartar).

### OQ-13 — `excluye` vs `no:` en `require_all`

¿`excluye` agrega valor real sobre `require_all` con prefijo `no:`? Pendiente decidir si mantener ambos o consolidar en `no:`.

### OQ-14 — Endpoint `/meta/escuadras/{slug}` con composición vigente

Inverso del tag `escuadra.{slug}`: lista miembros, derivar `fza_aportada` agregada. Fuera de v1 estricto.

---

## 3. Notas de arquitectura

No normativas — el kit es **documentación**, no aplicación. Estas notas existen como insumo para implementadores eventuales.

### N-01 — Tags como ciudadanos de primera clase favorecen un inverted index

Con `tags[]` plano y multiset, las queries del tipo "personajes con `skill.francotirador` AND `rol.lider` AND `faccion.confederados`" se resuelven con tres lookups en un inverted index `tag → set<personaje_id>` y luego intersección. Los UCs 19, 20, 21, 22 confirman este patrón.

### N-02 — Campos derivados se computan al servir, no al persistir

`filiacion`, `fatiga_max`, `moral_max`, `fza_aportada`, `sobrenombre` (cuando es derivable) — fórmulas en [`hoja-modelo.md §3.1`](hoja-modelo.md). Persistirlos sería invitación al drift; computarlos al servir vale el costo.

### N-03 — Atributos no son derivados del rango post-creación

La tabla determinística de atributos por rango ([GDDR-01 §3](../gddr/01-flujo-obligatorio-creacion.md)) aplica **únicamente** en creación. Tras eso, los atributos son propiedad del personaje. Un ascenso cambia el tag `rango.*` pero no toca `{fis, tac, men}`. La única mutación de atributos viene por hitos `triple_cero` o `mejora_atributo`.

### N-04 — Trayectoria de tags vía historial reverso

El estado inicial de `tags[]` no se persiste como snapshot. Se reconstruye reproduciendo `historial[]` hacia adelante (desde la creación) o aplicando hitos `agregar_tag`/`quitar_tag` en reversa contra el estado vigente.
