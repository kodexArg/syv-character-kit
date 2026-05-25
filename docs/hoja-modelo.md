# Hoja Modelo — Referencia narrativa de campos

> **Versión compatible**: schema v0.4.1
> **Propósito**: descripción campo por campo de la hoja de personaje canónica. Para el template
> programático listo para copiar, ver [`docs/hoja-modelo.yml`](hoja-modelo.yml).

---

## Bloque 1 — Identidad estable

**`id`** — Identificador único del personaje. String inmutable asignado en creación. Para mocks sigue el patrón `mock.{faccion_slug}.{nn}.{apellido_slug}` (ej. `mock.confederacion.01.aguirre`); para canonizados usa `canon.{ulid}`; para efímeros es `null`. El motor de batalla usa este campo como clave de referencia en vínculos y reportes de hito.

**`origen`** — Enum de tres valores: `"mock"` para los 22 fixtures inmutables, `"generado"` para efímeros sin persistencia, y `"canonizado"` para personajes persistidos por la API. Inmutable: no cambia si el personaje sube de estado.

**`semilla`** — Seed que produjo la ficha. String inmutable presente en todos los modos. Permite a cualquier cliente reproducir el estado inicial del personaje (atributos, tags, prosa) para calcular diffs. Para mocks toma la forma `mock-fixed-{nn}`.

---

## Bloque 2 — Cabecera

**`nombre`** — Nombre real del personaje. String inmutable asignado en creación; no es el título operativo. Ej. `"Walter Aguirre"`.

**`sobrenombre`** — Cómo se lo conoce operativamente. Derivado al servir desde `nombre`, `rango` y tags de skill de mando; nunca se persiste. En Confederación: `"{rango narrativo} {nombre}"`. En Ejército Rojo: se construye desde la skill de comandancia más prominente (`Comandancia` → `"Comandante {nombre}"`). `null` cuando no hay distinción con el nombre real.

**`filiacion`** — Derivado al servir; no persiste. Se compone como `"{rango} de la {escuadra.nombre} del {escuadra.cuerpo}"`. Si `escuadra_id` es `null`, se omite la cláusula de escuadra. El nombre del campo es provisorio (ver OQ en PRD §15.1).

**`faccion`** — Pertenencia macro del personaje. Enum abierto; valores de MVP: `"Confederación"` y `"Ejército Rojo"`. Inmutable salvo hito explícito de cambio de bando.

**`edad`** — Años del personaje al momento de creación. Integer simple, sin mecánica de envejecimiento. Rango sugerido por rango operativo: reclutas 18-24, líderes 28-45.

**`genero`** — Enum abierto: `"masculino"`, `"femenino"`, `"no_binario"`, `"otro"`. La distribución en creación es curada por facción.

**`estado_salud`** — Condición física del personaje. Enum mutable: `"saludable"` (default en creación), `"herido"`, `"baja"`. Distinto de `estado` (asignación operativa).

**`rol`** — Papel narrativo y cultural. String abierto; describe cómo lo nombra el lore, no su posición jerárquica. Ej. `"Sargento Confederado"`, `"Líder Revolucionario"`, `"Comisario"`. Desacoplado de `rango`: distintos `rol` pueden ejercer el mismo `rango`.

**`estado`** — Dimensión de asignación/disponibilidad. Enum mutable: `"activo"` (asignado a escuadra y operativo), `"disponible"` (sin asignar; default en creación), `"kia"` (caído en combate), `"licencia"` (baja temporal).

**`rango`** — Designación operativa de campo. String abierto jerárquico; el motor de batalla lo usa para decidir mando. Valores canon: `"Lider de escuadra"`, `"Segundo al mando"`, `"Apuntador"`, `"Artillero"`, `"Fusilero"`, `"Recluta"`. Mutable vía hito `cambio_rango`.

**`escuadra_id`** — Referencia string a la entidad escuadra. `null` cuando el personaje no está asignado. La API no valida que el id exista. Mutable vía hito `asignacion_escuadra`.

**`mando`** — Booleano que indica capacidad de mando, no titularidad activa. Si `true`, el personaje puede asumir liderazgo cuando el líder activo cae. La titularidad vigente se deriva: `mando == true AND es el de mayor rango de mando en su escuadra_id`. Default `true` para `Lider de escuadra` y `Segundo al mando`; `false` para el resto. Mutable vía hito `cambio_mando`.

---

## Bloque 3 — Lealtades

**`lealtades`** — Estructura anidada con tres sub-campos. `primaria` es string; la lealtad principal del personaje (ej. `"Confederación"`, `"Sargento Ricardo (post mortem)"`). `secundarias` es array de strings; lealtades adicionales en orden de importancia. `secretos` es array de strings; lealtades ocultas que el personaje no declara abiertamente. Los tres son mutables vía hito `ruptura_vinculo` o hito manual.

---

## Bloque 4 — Atributos

**`atributos`** — Set de tres valores numéricos que definen la capacidad base del personaje. Determinísticos por rango en creación (no se sortean); mutables post-creación solo vía hito `triple_cero` o `mejora_atributo`. Rango 2-5 para `fis` y `tac`; hasta 7 para `men` en líderes. `fis` (físico) determina resistencia y potencia bruta. `tac` (táctico) determina precisión y coordinación. `men` (mental) determina liderazgo, moral y resistencia psicológica.

---

## Bloque 5 — Estado vital

**`estado_vital`** — Bloque de seguimiento permanente de Fatiga y Moral. Se ubica después de ASPECTOS y antes de LEALTADES en la hoja. Campos derivados en creación y mutables en juego.

**`fatiga_max`** — Integer derivado al crear: `atributos.fis + atributos.men`. Se persiste en la hoja (no se recalcula al servir). Inmutable salvo cambio de atributo base; en ese caso el narrador recalcula y registra el delta como hito `cambio_estado_vital`. Invariante: `fatiga_actual <= fatiga_max`.

**`fatiga_actual`** — Integer mutable en juego. Arranca igual a `fatiga_max` en creación. Decrece por agotamiento en combate o escenario; puede recuperarse. Invariante: `0 <= fatiga_actual <= fatiga_max`. Los cambios se registran como hito `cambio_estado_vital`.

**`moral_max`** — Integer derivado al crear: `atributos.men`. Se persiste. Inmutable salvo cambio de `men`. Invariante: `moral_actual <= moral_max`.

**`moral_actual`** — Integer mutable en juego. Arranca igual a `moral_max` en creación. Refleja el estado anímico del personaje; decrece bajo presión, pérdida de aliados o situaciones traumáticas. Invariante: `0 <= moral_actual <= moral_max`. Los cambios se registran como hito `cambio_estado_vital`.

---

## Bloque 6 — Tags

**`tags`** — Lista plana de entidades `{categoria, valor}`. El corazón del schema: todo lo que puede ser tag, es tag. Categorías canon: `rasgo` (rasgos físicos), `rol` (mecánico), `skill` (habilidades), `trait` (carácter/condición sin mecánica activa), `perk` (ventaja activable del reglamento), `aspecto` (mini-tag con efecto mecánico en mini-frase), `equipo.arma`, `equipo.utilitario`, `equipo.vestidura`. Categorías abiertas: se aceptan valores fuera del canon. Los tags son repetibles: tres `cargador` son tres entidades físicas distintas. El `valor` de cada tag es mínimo: 1-2 palabras (3 cuando el nombre canónico lo requiere). Cambios post-creación se registran como hito `agregar_tag` / `quitar_tag`.

---

## Bloque 7 — Vínculos

**`vinculos`** — Array de relaciones con otros personajes. Cada vínculo tiene `tipo` (string abierto; sugeridos: `mentor`, `subordinado`, `hermano_de_armas`, `rival`, `deuda`, `enemigo_jurado`, `familia`, `romance`), `ref_personaje_id` (id del otro personaje o `null` si es externo al corpus), y `descripcion` (string obligatorio; fallback cuando el id no resuelve). La API no valida que `ref_personaje_id` exista. Mutable vía hitos `formacion_vinculo` y `ruptura_vinculo`.

---

## Bloque 8 — Historia

**`historia`** — Prosa biográfica original. String de 120-200 palabras generado por LLM en la creación del personaje efímero. Al canonizar se congela: nunca muta tras la canonización. Escrita en castellano rioplatense, primera persona narrativa. Es el único lugar donde vive la voz del personaje como descripción extendida.

---

## Bloque 9 — Historial

**`historial`** — Array de hitos que registran la memoria viva del personaje canonizado. Cada entrada tiene: `fecha` (ISO-8601), `tipo` (string abierto con valores sugeridos), `descripcion` (prose del evento), `ref_batalla` (id de batalla del motor downstream o `null`), y `metadata` (object libre para datos estructurados del hito). Tipos sugeridos: `triple_cero`, `ascenso`, `herida`, `recuperacion`, `agregar_tag`, `quitar_tag`, `formacion_vinculo`, `ruptura_vinculo`, `traslado`, `condecoracion`, `mejora_atributo`, `cambio_rango`, `cambio_mando`, `cambio_estado`, `asignacion_escuadra`, `cambio_estado_vital`. Solo para canonizados; efímeros y mocks lo tienen vacío o como datos de auditoría.

---

## Bloque 10 — Tags iniciales

**`tags_iniciales`** — Snapshot inmutable de `tags[]` tal como estaba al momento de creación. Array de `{categoria, valor}`. Permite a cualquier cliente calcular el diff entre el estado original y el vigente. Nunca muta.

---

## Bloque 11 — Metadatos

**`metadatos`** — Conjunto de campos de auditoría y trazabilidad. `creado_en` (ISO-8601, fecha de creación efímera). `canonizado_en` (ISO-8601 o `null`; solo canonizados). `ultima_actualizacion` (ISO-8601; se actualiza con cada hito). `modelo_prosa` (string o `null`; modelo LLM que escribió `historia`). `es_canon` (boolean; `true` para mocks y canonizados).

---

## Bloque 12 — Extras

**`extras`** — Escape hatch deliberado. Object libre o `null`. La API no inspecciona ni valida su contenido. Permite a clientes externos persistir metadatos propios sin romper el schema ni requerir un cambio de versión del PRD.
