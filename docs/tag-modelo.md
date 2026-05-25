# Tag Modelo — Referencia del sistema de tags

> **Versión compatible**: schema v0.5.0.
> **Propósito**: definir qué es un tag, cómo se escribe, qué categorías existen y cómo
> se relacionan con la hoja de personaje. Para la estructura de la hoja completa,
> ver [`hoja-modelo.md`](hoja-modelo.md).

---

## §1 — Qué es un tag

Un **tag** es un identificador discreto que se aplica a un personaje. La regla rectora del schema:

> Todo lo que puede ser discreto y no es identidad estable, atributo numérico, prosa, o auditoría — **es tag**.

Los tags son la unidad universal del modelo: rasgos físicos, habilidades, equipo cargado, condiciones de salud, estado mental, facción a la que pertenece, rango militar, lealtades, némesis, todos viven como tags en la lista plana `personaje.tags[]`.

**Lo que NO es tag** (y por qué):
- **`identidad`** — slug, nombre, sobrenombre, rol narrativo, género, edad. Datos nominales únicos, no enumerables.
- **`atributos`** — `fis`, `tac`, `men`. Magnitudes numéricas continuas.
- **`historia`** — prosa biográfica larga.
- **`extras`** — diccionario libre para metadatos externos.
- **`historial`** — eventos temporales estructurados (no discretos).
- **`metadatos`** — timestamps de auditoría.

---

## §2 — Notación punto

Un tag se escribe como un **string único** con la forma:

```
<categoria>[.<subcategoria>...].<slug>
```

- El primer segmento es la **categoría** canónica.
- Si la categoría tiene sub-categorías, se anidan con puntos.
- El último segmento es el **slug** específico (lowercase + underscore, sin acentos).

Ejemplos:

| Tag | Categoría | Sub | Slug |
|---|---|---|---|
| `faccion.ejercito_rojo` | `faccion` | — | `ejercito_rojo` |
| `mental.panico` | `mental` | — | `panico` |
| `salud.herido` | `salud` | — | `herido` |
| `rasgo.altura_media` | `rasgo` | — | `altura_media` |
| `skill.comandancia` | `skill` | — | `comandancia` |
| `equipo.arma.pistola` | `equipo` | `arma` | `pistola` |
| `equipo.vestidura.uniforme_rojo` | `equipo` | `vestidura` | `uniforme_rojo` |
| `rol.oficio.francotirador` | `rol` | `oficio` | `francotirador` |
| `lealtad.faccion.ejercito_rojo` | `lealtad` | — | ref compuesta `faccion.ejercito_rojo` |
| `lealtad.pj.aguirre_walter` | `lealtad` | — | ref compuesta `pj.aguirre_walter` |
| `nemesis.pj.iturra_delia` | `nemesis` | — | ref compuesta `pj.iturra_delia` |

**Reglas del slug**: lowercase, underscores como único separador interno, sin acentos, sin espacios, sin caracteres especiales. Mismo formato para personajes (`aguirre_walter`), facciones (`ejercito_rojo`), escuadras, rangos (`lider_de_escuadra`) y cualquier slug del sistema.

**Repetibilidad**: la lista `tags[]` es un multiset, no un set. `equipo.utilitario.cargador` puede aparecer tres veces y eso significa tres cargadores físicos distintos. El motor itera la lista, no la deduplica.

**Resolución contra el catálogo**: dado un tag `equipo.arma.pistola`, el archivo canónico vive en `mock/tags/equipo/arma/pistola.yaml` (o en la fila correspondiente de la DB). El parser troza por `.` y mapea segmentos a directorios/columnas. Ver §5.

---

## §3 — Categorías canon

| Categoría | Significado | Sub-categorías | Ejemplos de tag completo |
|---|---|---|---|
| `faccion` | Pertenencia macro (bando). | — | `faccion.confederados`, `faccion.ejercito_rojo` |
| `rango` | Designación operativa jerárquica de campo. | — | `rango.lider_de_escuadra`, `rango.apuntador`, `rango.fusilero` |
| `escuadra` | Asignación a una escuadra concreta. | — | `escuadra.ricardo`, `escuadra.mansilla` (catálogo TBD) |
| `mando` | Capacidad de mando dentro de la facción. | — | `mando.capaz` (presencia = capacidad de tomar el mando si cae el líder activo) |
| `estado` | Disponibilidad operativa. Exactamente una por personaje. | — | `estado.activo`, `estado.disponible`, `estado.kia`, `estado.licencia` |
| `salud` | Estado físico actual. Acumulable. | — | `salud.cansado`, `salud.exhausto`, `salud.agotado`, `salud.herido`, `salud.malherido`, `salud.sangrando`, `salud.enfermo`, `salud.aturdido` |
| `mental` | Estado anímico actual. Acumulable. | — | `mental.panico`, `mental.confundido`, `mental.desmoralizado`, `mental.iracundo`, `mental.traumatizado`, `mental.conmocionado`, `mental.berserker`, `mental.sereno` |
| `rasgo` | Rasgo físico observable. | — | `rasgo.altura_media`, `rasgo.cicatriz_en_ceja`, `rasgo.pelo_corto` |
| `trait` | Rasgo de carácter sin mecánica activa. | — | `trait.taciturno`, `trait.miope`, `trait.mirada_larga` |
| `perk` | Ventaja reglada con efecto numérico. | — | `perk.sucesor_de_ricardo`, `perk.veterano` |
| `aspecto` | Mini-tag identitario con efecto mecánico en mini-frase. | — | `aspecto.cabron`, `aspecto.ojo_de_halcon`, `aspecto.muy_fuerte`, `aspecto.terco` |
| `skill` | Habilidad aprendida o entrenada. | — | `skill.comandancia`, `skill.medicina`, `skill.lectura_de_terreno`, `skill.comisariado` |
| `equipo` | Equipo cargado por el personaje. | `arma`, `utilitario`, `vestidura` | `equipo.arma.rifle_militar`, `equipo.utilitario.cargador`, `equipo.vestidura.uniforme_confederado` |
| `rol` | Roles operativos (oficio / jerarquía militar / narrativo / mecánico). | `oficio`, `jerarquia`, `narrativo`, `mecanico` | `rol.oficio.francotirador`, `rol.jerarquia.sargento`, `rol.narrativo.lider_revolucionario`, `rol.mecanico.lider`, `rol.mecanico.heroe` |
| `lealtad` | Lealtad real y declarable. Relacional. Ver §4. | — | `lealtad.faccion.confederados`, `lealtad.pj.aguirre_walter` |
| `nemesis` | Enemistad personal identificada en batalla. Relacional. Ver §4. | — | `nemesis.pj.iturra_delia` |

**Categorías abiertas**: el motor acepta tags fuera del canon (`origen: custom`). El catálogo se mantiene coherente por curaduría, no por integridad referencial.

**OQ-tag-1 (resuelta)**: la notación punto naturalmente soporta sub-categorías (ej. `equipo.arma.pistola`). Por simetría, `rol.*` adopta la Forma 2 (jerárquica) — `rol.oficio.X`, `rol.jerarquia.X`, etc.

---

## §4 — Categorías relacionales: `lealtad` y `nemesis`

Estas dos categorías codifican **vínculos dirigidos** hacia otra entidad. Su slug no es un identificador libre — es una **referencia compuesta** con prefijo que indica qué tipo de cosa se referencia.

### Patrón de referencia compuesta

| Prefijo del slug | Apunta a | Forma del tag completo |
|---|---|---|
| `faccion.` | Facción del catálogo | `lealtad.faccion.{slug}` |
| `pj.` | Personaje persistido | `lealtad.pj.{slug}` o `nemesis.pj.{slug}` |
| `escuadra.` | Escuadra (catálogo TBD) | `lealtad.escuadra.{slug}` |

El prefijo es parte literal del slug compuesto. Un parser ve `lealtad.faccion.confederados` y sabe que es una ref a la facción de slug `confederados`.

### `lealtad`

Solo lealtades **reales y declarables**. Las latentes, aspiracionales o secretas se manejarán por sistema aparte (TBD). Múltiples `lealtad.*` conviven en un mismo personaje; el orden en la lista es indicativo de jerarquía pero no normativo.

Para lealtades a entidades fuera del corpus (personajes históricos no persistidos), se permite **sintetizar un slug**: ej. `lealtad.pj.sargento_ricardo_postmortem` para citar a un mentor caído que no está en el roster activo. La ref no resuelve a un registro persistido, pero conserva la forma estable.

### `nemesis`

Se crea **en caliente** cuando un personaje identifica a otro como rival individual en batalla. Habilita reglas downstream del motor (ej. 50% de probabilidad de seleccionar al némesis como objetivo prioritario — sistema concreto TBD).

Formato único: `nemesis.pj.{slug}`. No se aceptan refs a facciones o conceptos abstractos.

Un personaje puede acumular múltiples némesis a lo largo de su vida.

---

## §5 — Catálogo: estructura del archivo de un tag

Cada tag canon o emergente tiene una entrada en el catálogo. En MVP los catálogos viven como archivos YAML:

```
mock/tags/{categoria}/{slug}.yaml                       # tag de un nivel
mock/tags/{categoria}/{subcategoria}/{slug}.yaml        # tag con sub-categoría
```

Ejemplo: `mock/tags/faccion/ejercito_rojo.yaml`, `mock/tags/equipo/arma/pistola.yaml`.

El template programático de un archivo de catálogo está en [`tag-modelo.yaml`](tag-modelo.yaml). Campos:

- **`categoria`** — string. Primer segmento del tag (ej. `equipo`).
- **`subcategoria`** — string opcional. Segmento intermedio cuando aplica (ej. `arma`).
- **`slug`** — string. Último segmento, identificador específico (lowercase, underscore, sin acentos).
- **`descripcion`** — 1-3 frases canónicas. Vive solo aquí; nunca se persiste dentro del personaje.
- **`origen`** — enum: `"canon"` | `"emergente"` | `"custom"`.
- **`metadatos`** — `version_introducida` (SemVer), `creado_en` (ISO-8601), `ultima_actualizacion` (ISO-8601).

**Campos específicos por categoría** (ver `tag-modelo.yaml`):
- `perk.efecto_reglado` — frase con bonus/penalidad numérico.
- `aspecto.efecto` — mini-frase trigger + probabilidad + efecto.
- `aspecto.tags_activables` — array de tags `mental.*` que el aspecto puede disparar.
- `skill.atributo_dominante` — `fis | tac | men`.
- `skill.rangos_naturales` — array de tags `rango.*`.
- `skill.facciones_predominantes` — array de tags `faccion.*`.
- `skill.equipo_sugerido` — array de tags `equipo.*`.
- `equipo.arma.calibre` — string. `null` si no aplica.
- `equipo.arma.tipo_accion` — `cerrojo | semiauto | automatico | cuerpo_a_cuerpo`.
- `equipo.arma.municion_tag_ref` — tag `equipo.utilitario.*` que representa la munición.
- `equipo.arma.alcance_narrativo` — `corto | medio | largo`.
- `equipo.vestidura.faccion_asociada` — tag `faccion.*`.

Las categorías relacionales (`lealtad`, `nemesis`) **no tienen entradas en el catálogo** — su semántica es del *formato* del tag, no del *contenido*. Las refs `pj.{slug}` y `faccion.{slug}` resuelven contra los catálogos de personajes y facciones respectivamente.

---

## §6 — Persistencia

Los tags del mock y los tags creados en caliente desde la API o el motor de batalla son **indistinguibles**. No hay un campo `origen: mock`. Un tag `faccion.ejercito_rojo` cargado de `mock/tags/faccion/ejercito_rojo.yaml` y otro creado al vuelo en una batalla resuelven al mismo identificador. El catálogo `mock/tags/**` es solo la fuente inicial que siembra la DB cuando arranca el sistema.

Esto implica que:
- Cualquier tag puede crearse en caliente (ej. un narrador agrega `aspecto.cabron` a un personaje durante una batalla — el aspecto debe existir en el catálogo, o crearse con `origen: custom` antes de aplicarse).
- La indistinción simplifica la lógica downstream: el motor no se preocupa por de dónde viene el tag, solo por qué dice.

---

## §7 — Open Questions

### OQ-tag-2 — `slug` derivado vs persistido en el catálogo
¿El archivo del catálogo persiste `slug` explícito, o se deriva del nombre de archivo? Persistido: ambigüedad cero, redundancia segura. Derivado: una sola fuente de verdad. Tensión menor; pendiente.

### OQ-tag-3 — Catálogo de personajes históricos
Personajes referenciados por `lealtad.pj.X` pero no presentes en el roster activo (ej. el Sargento Ricardo) actualmente caen al patrón de slug sintético (`lealtad.pj.sargento_ricardo_postmortem`). ¿Vale crear un catálogo separado `mock/personajes_historicos/` para entradas mínimas (slug + nombre + breve nota)? Costo: más curaduría. Beneficio: refs estables, queryables, y prosa contextual disponible.
