# Tag Modelo — Referencia del sistema de tags

> **Estado**: rolling release; este documento describe el vigente.
> **Propósito**: definir qué es un tag, cómo se escribe, qué puede expresar, y cómo se relaciona con la hoja de personaje. Para la estructura de la hoja completa, ver [`hoja-modelo.md`](hoja-modelo.md).

---

## §1 — Mecánica universal del tag

Un **tag** es la unidad atómica del schema. Es un identificador discreto que se aplica a un personaje y que, por sí solo, comunica una cosa concreta: una habilidad ganada, una marca en la piel, un fusil cargado al hombro, un estado mental de pánico, una lealtad jurada a una facción, una enemistad personal con otro soldado. Cualquier hecho discreto del mundo del personaje que no sea identidad estable, un atributo numérico, prosa o auditoría — puede expresarse como tag.

La regla rectora:

> Todo lo que puede ser discreto **es tag**.

Esta regla es deliberadamente expansiva. El sistema no intenta predecir todos los tipos de tag que existirán; intenta dar una notación lo suficientemente plana y declarativa para que cualquier hecho futuro encaje sin migración. El daño de un arma puede expresarse como tag (`equipo.arma.fal` declara su perfil de daño en su archivo de catálogo); una montura puede expresarse como tag el día que aparezca el primer caballo; un vicio, una cicatriz, un grado de iniciación en una logia, una mascota — todo es tag en cuanto se decide que lo es. **Adelantar templates para tipos de tag que aún no existen es un error**: alcanza con dejar la cancha preparada y dar indicios. El catálogo crece por curaduría a medida que las escenas lo piden, no por anticipación especulativa.

Los tags se agrupan visualmente en **categorías** (`skill`, `equipo.arma`, `salud`, `mental`, etc.) que los renderers usan para presentar la hoja como secciones legibles. Sin embargo, **el modelo es agnóstico al renderer**: la categoría es metadato semántico para que cualquier consumidor (CLI ASCII, UI web, motor de batalla, exportador a PDF) decida cómo agruparlos visualmente. El schema no impone una forma de renderizado. Una misma hoja servida por la API puede aparecer como bloques ASCII, como tarjetas de UI, o como filas de una tabla — todas son vistas válidas del mismo modelo.

**Lo que NO es tag** (y por qué):
- **`identidad`** — slug, nombre, sobrenombre, rol narrativo, género, edad. Datos nominales únicos, no enumerables.
- **`atributos`** — `fis`, `tac`, `men`. Magnitudes numéricas continuas.
- **`historia`** — prosa biográfica larga.
- **`historial`** — eventos temporales estructurados (no discretos).
- **`metadatos`** — timestamps de auditoría.
- **`extras`** — diccionario libre para metadatos externos.

---

## §2 — Notación punto

Un tag se escribe como un **string único** con la forma:

```
<categoria>[.<subcategoria>...].<slug>
```

- El primer segmento es la **categoría** (el eje semántico mayor).
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

**Resolución contra el catálogo**: dado un tag `equipo.arma.pistola`, el archivo canónico vive en `mock/tags/equipo/arma/pistola.yaml` (o en la fila correspondiente de la DB). El parser troza por `.` y mapea segmentos a directorios/columnas. Ver §6.

---

## §3 — Ejemplos curados (no es un catálogo cerrado)

La tabla siguiente lista las **categorías más usadas hasta ahora**. No es un canon cerrado: el sistema acepta categorías nuevas sin migración (ver §7 extensibilidad). Tomalas como puntos de referencia, no como un menú restrictivo.

| Categoría | Significado | Sub-categorías | Ejemplos de tag completo |
|---|---|---|---|
| `faccion` | Pertenencia macro (bando). | — | `faccion.confederados`, `faccion.ejercito_rojo` |
| `rango` | Designación operativa jerárquica de campo. | — | `rango.lider_de_escuadra`, `rango.apuntador`, `rango.fusilero` |
| `escuadra` | Asignación a una escuadra concreta. | — | `escuadra.ricardo`, `escuadra.mansilla` |
| `mando` | Capacidad de mando dentro de la facción. | — | `mando.capaz` |
| `estado` | Disponibilidad operativa. Exactamente una por personaje. | — | `estado.activo`, `estado.disponible`, `estado.kia`, `estado.licencia` |
| `salud` | Estado físico actual. Acumulable. | — | `salud.cansado`, `salud.exhausto`, `salud.agotado`, `salud.herido`, `salud.malherido`, `salud.sangrando`, `salud.enfermo`, `salud.aturdido` |
| `mental` | Estado anímico actual. Acumulable. | — | `mental.panico`, `mental.confundido`, `mental.desmoralizado`, `mental.iracundo`, `mental.traumatizado`, `mental.conmocionado`, `mental.berserker`, `mental.sereno` |
| `rasgo` | Rasgo físico observable. | — | `rasgo.altura_media`, `rasgo.cicatriz_en_ceja`, `rasgo.pelo_corto` |
| `trait` | Rasgo de carácter sin mecánica activa. | — | `trait.taciturno`, `trait.miope`, `trait.mirada_larga` |
| `perk` | Ventaja reglada con efecto numérico. | — | `perk.sucesor_de_ricardo`, `perk.veterano`, `perk.tirador_preciso` |
| `aspecto` | Mini-tag identitario con efecto mecánico en mini-frase. | — | `aspecto.cabron`, `aspecto.ojo_de_halcon`, `aspecto.muy_fuerte`, `aspecto.terco` |
| `skill` | Habilidad aprendida o entrenada. | — | `skill.comandancia`, `skill.medicina`, `skill.lectura_de_terreno` |
| `equipo` | Equipo cargado por el personaje. | `arma`, `utilitario`, `vestidura` | `equipo.arma.rifle_militar`, `equipo.utilitario.cargador`, `equipo.vestidura.uniforme_confederado` |
| `rol` | Roles operativos (oficio / jerarquía militar / narrativo / mecánico). | `oficio`, `jerarquia`, `narrativo`, `mecanico` | `rol.oficio.francotirador`, `rol.jerarquia.sargento`, `rol.mecanico.lider` |
| `lealtad` | Lealtad real y declarable. Relacional. Ver §5. | — | `lealtad.faccion.confederados`, `lealtad.pj.aguirre_walter` |
| `nemesis` | Enemistad personal identificada en batalla. Relacional. Ver §5. | — | `nemesis.pj.iturra_delia` |

**Categorías abiertas**: el motor acepta tags fuera de los ejemplos curados (`origen: custom`). El catálogo se mantiene coherente por curaduría, no por integridad referencial.

---

## §4 — Campos del archivo de catálogo

Cada tag canon o emergente tiene una entrada en el catálogo. La filosofía del archivo es **mostrativa, no obligatoria**: cuatro campos son siempre requeridos; todo lo demás es opcional y se declara solo si suma información real sobre el tag.

### 4.1. Campos obligatorios (siempre)

| Campo | Tipo | Descripción |
|---|---|---|
| `slug` | string | Último segmento del tag. Lowercase + underscore, sin acentos. |
| `nombre` | string | Etiqueta legible humana corta (1-3 palabras, sin slugificar). Lo que un renderer muestra como label. Ej. `"Tirador preciso"`, `"Pánico"`, `"Cabrón"`. |
| `categoria` | string | Primer segmento del tag. Si la categoría tiene sub-niveles, este campo conserva solo la raíz y `subcategoria` (opcional) lleva el intermedio. |
| `descripcion` | string | 1-3 frases canónicas. Vive solo aquí; nunca se persiste dentro del personaje. |

### 4.2. Campos comunes opcionales

- **`subcategoria`** — segmento intermedio cuando aplica (ej. `arma` para `equipo.arma.pistola`).
- **`origen`** — enum: `canon | emergente | custom`. Asumir `emergente` si el archivo existe pero la entrada nació al vuelo.
- **`metadatos`** — `version_introducida` (SemVer), `creado_en` (ISO-8601), `ultima_actualizacion` (ISO-8601). Útil para auditoría del catálogo.
- **`requires`** — sistema de dependencias (ver §4.3). Declara precondiciones de coherencia.
- **`excluye`** — lista de tags **incompatibles**. Si el personaje tiene cualquiera de estos, el tag no debería aplicarse. Forma declarativa simétrica al `no:` de `requires` (ver OQ-tag-4).
- **`tags_relacionados`** — informativo. Lista de tags que típicamente acompañan a este; ayuda al curador y al sorteador, no es regla.
- **`peso_narrativo`** — entero `1..5`. Sugerencia al sorteador sobre cuán frecuentemente apropiado es para personajes random. Hint, no probabilidad estricta.

### 4.3. Sistema `requires` — dependencias del tag

El bloque `requires` declara cuándo un tag es coherente sobre un personaje. Se compone de dos sub-bloques, ambos opcionales y combinables:

- **`require_all: [tag, tag, ...]`** — el personaje debe tener **TODOS** estos tags para que este sea válido.
- **`require_any: [tag, tag, ...]`** — basta con **UNO** de estos.

**Modificador NOT**: cualquier entrada de `require_all` o `require_any` puede prefijarse con `no:` para invertir la condición. Forma elegida: **string con prefijo literal** `"no:<tag>"`. Es la representación más limpia en YAML — sin objetos anidados, queryable con un simple `startswith("no:")` desde cualquier consumidor, y obvia a la lectura humana.

**Ejemplo: `perk.tirador_preciso`**

```yaml
tag:
  slug: tirador_preciso
  nombre: "Tirador preciso"
  categoria: perk
  descripcion: >
    Bonus al primer disparo apuntado tras un turno sin moverse.
    Requiere oficio de francotirador y condiciones físicas decentes.
  requires:
    require_all:
      - "rol.oficio.francotirador"
      - "no:salud.herido"
      - "no:salud.malherido"
    require_any:
      - "equipo.arma.rifle_militar"
      - "equipo.arma.rifle_de_caza"
```

Lectura: el personaje **debe** ser francotirador de oficio, **no debe** estar herido ni malherido, **y** debe portar uno de los dos rifles aceptados. Si cualquier condición falla, el tag es incoherente sobre ese personaje (el motor puede negarse a aplicarlo, o aplicarlo igual y emitir un warning — la política downstream decide).

**Lo que `requires` NO hace**: no impone validación de schema. La API acepta personajes con tags incoherentes — la coherencia es responsabilidad del generador y del curador. `requires` es **documentación ejecutable**, consultable por cualquier validador opcional, pero no parte del contrato duro.

### 4.4. Campos específicos por categoría

Cada familia de tag puede declarar bloques propios cuando tiene atributos que sólo le aplican. Todos son opcionales y se llenan solo si la categoría los reconoce. Los actualmente curados:

- **`perk.efecto_reglado`** — frase con bonus/penalidad numérico.
- **`aspecto.efecto`** — mini-frase trigger + probabilidad + efecto.
- **`aspecto.tags_activables`** — array de tags `mental.*` que el aspecto puede disparar.
- **`skill.atributo_dominante`** — `fis | tac | men`.
- **`skill.rangos_naturales`** — array de tags `rango.*`.
- **`skill.facciones_predominantes`** — array de tags `faccion.*`.
- **`skill.equipo_sugerido`** — array de tags `equipo.*`.
- **`equipo.arma.calibre`** — string. `null` si no aplica.
- **`equipo.arma.tipo_accion`** — `cerrojo | semiauto | automatico | cuerpo_a_cuerpo`.
- **`equipo.arma.municion_tag_ref`** — tag `equipo.utilitario.*` que representa la munición.
- **`equipo.arma.alcance_narrativo`** — `corto | medio | largo`.
- **`equipo.vestidura.faccion_asociada`** — tag `faccion.*`.

El template programático con todos los bloques marcados como opcionales vive en [`tag-modelo.yaml`](tag-modelo.yaml). Los tipos de tag aún no introducidos (montura, vicio, mascota, etc.) **no llevan template anticipado** — se documentan el día que aparece el primer caso real.

---

## §5 — Categorías relacionales: `lealtad` y `nemesis`

Estas dos categorías codifican **vínculos dirigidos** hacia otra entidad. Su slug no es un identificador libre — es una **referencia compuesta** con prefijo que indica qué tipo de cosa se referencia.

### Patrón de referencia compuesta

| Prefijo del slug | Apunta a | Forma del tag completo |
|---|---|---|
| `faccion.` | Facción del catálogo | `lealtad.faccion.{slug}` |
| `pj.` | Personaje persistido | `lealtad.pj.{slug}` o `nemesis.pj.{slug}` |
| `escuadra.` | Escuadra (catálogo TBD) | `lealtad.escuadra.{slug}` |

El prefijo es parte literal del slug compuesto. Un parser ve `lealtad.faccion.confederados` y sabe que es una ref a la facción de slug `confederados`.

### `lealtad`

Solo lealtades **reales y declarables**. Las latentes, aspiracionales o secretas se manejan por sistema aparte (TBD). Múltiples `lealtad.*` conviven en un mismo personaje; el orden en la lista es indicativo de jerarquía pero no normativo.

Para lealtades a entidades fuera del corpus (personajes históricos no persistidos), se permite **sintetizar un slug**: ej. `lealtad.pj.sargento_ricardo_postmortem` para citar a un mentor caído que no está en el roster activo. La ref no resuelve a un registro persistido, pero conserva la forma estable.

### `nemesis`

Se crea **en caliente** cuando un personaje identifica a otro como rival individual en batalla. Habilita reglas downstream del motor (ej. 50% de probabilidad de seleccionar al némesis como objetivo prioritario — sistema concreto TBD).

Formato único: `nemesis.pj.{slug}`. No se aceptan refs a facciones o conceptos abstractos.

Un personaje puede acumular múltiples némesis a lo largo de su vida. **No hay restricción de bando**: un personaje puede tener un némesis del propio bando (un accidente, una traición personal, una vieja deuda). El sistema no lo prohíbe.

### Contenedores derivados: Aliados y Némesis

Los tags `lealtad.pj.{slug}` y `nemesis.pj.{slug}` alimentan dos **vistas derivadas** que el motor expone al servir la hoja:

- **`aliados`** — lista de personajes a los que el portador ha jurado lealtad personal. Computada proyectando todos los `lealtad.pj.*` del personaje.
- **`nemesis`** — lista de personajes identificados como rivales individuales. Computada proyectando todos los `nemesis.pj.*`.

Ambos contenedores:

- **Comienzan vacíos** al crear un personaje. Se pueblan en caliente durante batalla, narrativa o curaduría — siempre como consecuencia de agregar el tag relacional correspondiente.
- **No son campos persistidos del schema**. Son vistas computadas al servir, equivalentes a `filiacion` o `fatiga_max` (ver PRD §6.3).
- Son **agnósticas al renderer**: un cliente puede mostrarlos como bloques `ALIADOS` / `NÉMESIS` en ASCII, como tarjetas, como grafo de relaciones, o ignorarlos. El modelo no impone forma.

---

## §6 — Catálogo y persistencia

### Estructura de archivos

```
mock/tags/{categoria}/{slug}.yaml                       # tag de un nivel
mock/tags/{categoria}/{subcategoria}/{slug}.yaml        # tag con sub-categoría
```

Ejemplo: `mock/tags/faccion/ejercito_rojo.yaml`, `mock/tags/equipo/arma/pistola.yaml`.

Las categorías relacionales (`lealtad`, `nemesis`) **no tienen entradas en el catálogo** — su semántica es del *formato* del tag, no del *contenido*. Las refs `pj.{slug}` y `faccion.{slug}` resuelven contra los catálogos de personajes y facciones respectivamente.

### Indistinción mock/DB

Los tags del mock y los tags creados en caliente desde la API o el motor de batalla son **indistinguibles**. No hay un campo `origen: mock` en el tag aplicado al personaje. Un tag `faccion.ejercito_rojo` cargado de `mock/tags/faccion/ejercito_rojo.yaml` y otro creado al vuelo en una batalla resuelven al mismo identificador. El catálogo `mock/tags/**` es la fuente inicial que siembra la DB cuando arranca el sistema.

Implicaciones:
- Cualquier tag puede crearse en caliente (ej. un narrador agrega `aspecto.cabron` a un personaje durante una batalla — el aspecto debe existir en el catálogo, o crearse con `origen: custom` antes de aplicarse).
- El motor no se preocupa por de dónde viene el tag, solo por qué dice.

---

## §7 — Extensibilidad

El catálogo canon es **andamiaje, no jaula**. Tres ejes de extensibilidad sin permiso ni migración:

1. **Nuevos valores dentro de una categoría existente** — `skill.lockpicking`, `rasgo.tatuaje_de_ancla`. Entran con `origen: emergente` la primera vez, o `custom` si vienen de un cliente externo.
2. **Nuevas sub-categorías dentro de una familia** — `equipo.montura.caballo_criollo` agrega un nivel a `equipo.*`. El día que aparezca, no antes.
3. **Categorías nuevas enteras** — `oficio_civil.herrero`, `vicio.fuma`, `mascota.perro_pastor`. El parser solo necesita el primer segmento para enrutar.

**Garantía**: un tag desconocido no rompe la hoja. **No promesa**: que dos generadores coincidan sobre cómo nombrar el mismo concepto. La fragmentación se mitiga con curaduría, no con validación. Ver PRD §6.6 y tensión 13.7.

---

## §8 — Open Questions

### OQ-tag-2 — `slug` derivado vs persistido en el catálogo
Resuelta: `slug` es campo obligatorio del archivo. Ambigüedad cero, redundancia segura.

### OQ-tag-3 — Catálogo de personajes históricos
Personajes referenciados por `lealtad.pj.X` pero no presentes en el roster activo (ej. el Sargento Ricardo) actualmente caen al patrón de slug sintético (`lealtad.pj.sargento_ricardo_postmortem`). ¿Vale crear un catálogo separado `mock/personajes_historicos/` para entradas mínimas (slug + nombre + breve nota)? Costo: más curaduría. Beneficio: refs estables, queryables, y prosa contextual disponible.

### OQ-tag-4 — `excluye` vs `no:` en `require_all`
¿`excluye` agrega valor real sobre `require_all` con prefijo `no:`? Una lectura: `excluye` es más legible (declara incompatibilidades desde el lado correcto), pero redundante con `no:`. Pendiente decidir si mantener ambos o consolidar en `no:` exclusivo.
