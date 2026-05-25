# Tag Modelo — Referencia del sistema de tags

> **Estado**: rolling release; este documento describe el vigente.
> **Propósito**: definir qué es un tag, cómo se escribe, qué puede expresar y cómo se relaciona con la hoja de personaje. La estructura de la hoja completa vive en [`hoja-modelo.md`](hoja-modelo.md).

---

## §1 — Mecánica universal del tag

Un **tag** es la unidad atómica del schema. Es un identificador discreto que se aplica a un personaje y comunica una cosa concreta: una habilidad ganada, una marca en la piel, un fusil al hombro, un estado mental de pánico, una lealtad jurada, una enemistad personal.

La regla rectora es una sola:

> Todo lo que puede ser discreto **es tag**.

Esta regla es expansiva por diseño. El sistema no predice los tipos de tag que existirán; provee una notación plana y declarativa para que cualquier hecho futuro encaje sin migración. El daño de un arma es un tag (`equipo.arma.fal` declara su perfil en el archivo de catálogo). Una montura es un tag el día que aparece el primer caballo. Un vicio, una cicatriz, un grado de iniciación, una mascota — todo es tag en cuanto se decide que lo es.

**Adelantar templates para tipos de tag que aún no existen es un error.** El catálogo crece por curaduría a medida que las escenas lo piden, no por anticipación especulativa. Alcanza con dejar la cancha preparada.

Los tags se agrupan visualmente en **categorías** (`skill`, `equipo.arma`, `salud`, `mental`, etc.) que los renderers usan para presentar la hoja como secciones legibles. El modelo es **agnóstico al renderer**: la categoría es metadato semántico, no instrucción de presentación. Una misma hoja servida por la API puede aparecer como bloques ASCII, tarjetas de UI o filas de tabla — todas son vistas válidas.

**Lo que NO es tag**:

- `identidad` — slug, nombre, sobrenombre, rol narrativo, género, edad. Datos nominales únicos.
- `atributos` — `fis`, `tac`, `men`. Magnitudes numéricas continuas.
- `historia` — prosa biográfica larga.
- `historial` — eventos temporales estructurados.
- `metadatos` — timestamps de auditoría.
- `extras` — diccionario libre para clientes externos.

---

## §2 — Notación punto

Un tag se escribe como un **string único** con la forma `<categoria>[.<subcategoria>...].<slug>`.

- El primer segmento es la **categoría** (eje semántico mayor).
- Los segmentos intermedios son **sub-categorías** anidadas.
- El último segmento es el **slug** específico (lowercase + underscore, sin acentos).

Ejemplos canónicos:

    faccion.ejercito_rojo            categoria: faccion        slug: ejercito_rojo
    mental.panico                    categoria: mental         slug: panico
    salud.herido                     categoria: salud          slug: herido
    rasgo.altura_media               categoria: rasgo          slug: altura_media
    skill.comandancia                categoria: skill          slug: comandancia
    equipo.arma.pistola              categoria: equipo         sub: arma         slug: pistola
    equipo.vestidura.uniforme_rojo   categoria: equipo         sub: vestidura    slug: uniforme_rojo
    rol.oficio.francotirador         categoria: rol            sub: oficio       slug: francotirador
    lealtad.faccion.ejercito_rojo    categoria: lealtad        ref compuesta:    faccion.ejercito_rojo
    lealtad.pj.aguirre_walter        categoria: lealtad        ref compuesta:    pj.aguirre_walter
    nemesis.pj.iturra_delia          categoria: nemesis        ref compuesta:    pj.iturra_delia

**Reglas del slug**: lowercase, underscores como único separador, sin acentos, sin espacios, sin caracteres especiales. Aplica a todo slug del sistema — personajes (`aguirre_walter`), facciones (`ejercito_rojo`), escuadras, rangos (`lider_de_escuadra`), tags.

**Repetibilidad**: `tags[]` es un multiset. Tres `equipo.utilitario.cargador` significan tres cargadores físicos. El motor itera, no deduplica.

**Resolución contra el catálogo**: el parser troza el tag por `.` y mapea segmentos a directorios. `equipo.arma.pistola` resuelve a `mock/tags/equipo/arma/pistola.yaml`. Ver §6.

---

## §3 — Categorías de referencia

Las categorías más usadas hasta hoy. **No es un canon cerrado**: el sistema acepta categorías nuevas sin migración (ver §7). Tomalas como puntos de referencia, no como menú restrictivo.

  faccion:
    significado: Pertenencia macro (bando).
    ejemplos: [faccion.confederados, faccion.ejercito_rojo]

  rango:
    significado: Designación operativa jerárquica de campo.
    ejemplos: [rango.lider_de_escuadra, rango.apuntador, rango.fusilero]

  escuadra:
    significado: Asignación a una escuadra concreta.
    ejemplos: [escuadra.ricardo, escuadra.mansilla]

  mando:
    significado: Capacidad de mando dentro de la facción.
    ejemplos: [mando.capaz]

  estado:
    significado: Disponibilidad operativa. Exactamente uno por personaje.
    ejemplos: [estado.activo, estado.disponible, estado.kia, estado.licencia]

  salud:
    significado: Estado físico actual. Acumulable.
    ejemplos: [salud.cansado, salud.exhausto, salud.herido, salud.malherido, salud.sangrando, salud.enfermo, salud.aturdido]

  mental:
    significado: Estado anímico actual. Acumulable.
    ejemplos: [mental.panico, mental.confundido, mental.desmoralizado, mental.iracundo, mental.traumatizado, mental.berserker, mental.sereno]

  rasgo:
    significado: Rasgo físico observable.
    ejemplos: [rasgo.altura_media, rasgo.cicatriz_en_ceja, rasgo.pelo_corto]

  trait:
    significado: Rasgo de carácter sin mecánica activa.
    ejemplos: [trait.taciturno, trait.miope, trait.mirada_larga]

  perk:
    significado: Ventaja reglada con efecto numérico.
    ejemplos: [perk.sucesor_de_ricardo, perk.veterano, perk.tirador_preciso]

  aspecto:
    significado: Mini-tag identitario con efecto mecánico en mini-frase.
    ejemplos: [aspecto.cabron, aspecto.ojo_de_halcon, aspecto.muy_fuerte, aspecto.terco]

  skill:
    significado: Habilidad aprendida o entrenada.
    ejemplos: [skill.comandancia, skill.medicina, skill.lectura_de_terreno]

  equipo:
    significado: Equipo cargado por el personaje.
    subcategorias: [arma, utilitario, vestidura]
    ejemplos: [equipo.arma.rifle_militar, equipo.utilitario.cargador, equipo.vestidura.uniforme_confederado]

  rol:
    significado: Roles operativos (oficio, jerarquía militar, narrativo, mecánico).
    subcategorias: [oficio, jerarquia, narrativo, mecanico]
    ejemplos: [rol.oficio.francotirador, rol.jerarquia.sargento, rol.mecanico.lider]

  lealtad:
    significado: Lealtad real y declarable. Relacional. Ver §5.
    ejemplos: [lealtad.faccion.confederados, lealtad.pj.aguirre_walter]

  nemesis:
    significado: Enemistad personal identificada en batalla. Relacional. Ver §5.
    ejemplos: [nemesis.pj.iturra_delia]

El motor acepta tags fuera del canon. Marcalos con `origen: custom`. La coherencia del catálogo la sostiene la curaduría, no la integridad referencial.

---

## §4 — Campos del archivo de catálogo

Cada tag canon o emergente tiene una entrada en el catálogo. La filosofía es **mostrativa, no obligatoria**: cuatro campos son siempre requeridos. Todo lo demás es opcional y se declara solo si suma información real.

### 4.1. Campos obligatorios

Estos cuatro campos están **siempre** en el archivo:

  slug:
    tipo: string
    regla: Último segmento del tag. Lowercase + underscore, sin acentos.

  nombre:
    tipo: string
    regla: Etiqueta legible humana corta, 1-3 palabras, sin slugificar.
    proposito: Lo que un renderer muestra como label.
    ejemplos: ["Tirador preciso", "Pánico", "Cabrón"]

  categoria:
    tipo: string
    regla: Primer segmento del tag. Si la categoría tiene sub-niveles, este campo guarda solo la raíz; `subcategoria` (opcional) lleva el intermedio.

  descripcion:
    tipo: string
    regla: 1-3 frases canónicas.
    proposito: Única fuente de la prosa del tag. Nunca se persiste dentro del personaje.

### 4.2. Campos comunes opcionales

Declaralos solo si aportan información real:

  subcategoria:
    uso: Segmento intermedio cuando aplica.
    ejemplo: "arma" para equipo.arma.pistola

  origen:
    enum: [canon, emergente, custom]
    default: emergente
    regla: Usar `emergente` si el archivo nació al vuelo y se promovió. Usar `custom` para entradas de clientes externos.

  metadatos:
    uso: Auditoría del catálogo.
    campos:
      version_introducida: SemVer
      creado_en: ISO-8601
      ultima_actualizacion: ISO-8601

  requires:
    uso: Precondiciones de coherencia. Ver §4.3.

  excluye:
    uso: Lista de tags incompatibles. Si el personaje tiene cualquiera, el tag no debería aplicarse.
    nota: Simétrico al prefijo `no:` de `requires`. Ver OQ-tag-4.

  tags_relacionados:
    uso: Tags que típicamente acompañan a este. Informativo, no normativo. Ayuda al curador y al sorteador.

  peso_narrativo:
    tipo: int (1..5)
    uso: Hint al sorteador sobre frecuencia apropiada para personajes random. No es probabilidad estricta.

### 4.3. Sistema `requires` — dependencias del tag

El bloque `requires` declara cuándo un tag es coherente sobre un personaje. Tiene dos sub-bloques, ambos opcionales y combinables:

  require_all:
    semantica: El personaje debe tener TODOS estos tags.

  require_any:
    semantica: Basta con UNO de estos tags.

**Modificador NOT**: prefijá cualquier entrada con `"no:"` para invertir la condición. La forma es **string con prefijo literal** — sin objetos anidados, queryable con un `startswith("no:")` desde cualquier consumidor, obvia a la lectura humana.

Ejemplo completo — `perk.tirador_preciso`:

  tag:
    slug: tirador_preciso
    nombre: "Tirador preciso"
    categoria: perk
    descripcion: >
      Bonus al primer disparo apuntado tras un turno sin moverse.
      Requiere oficio de francotirador y condiciones físicas decentes.
    requires:
      require_all:
        - rol.oficio.francotirador
        - "no:salud.herido"
        - "no:salud.malherido"
      require_any:
        - equipo.arma.rifle_militar
        - equipo.arma.rifle_de_caza

Lectura: el personaje **debe** ser francotirador de oficio, **no debe** estar herido ni malherido, **y** debe portar uno de los dos rifles aceptados. Si cualquier condición falla, el tag es incoherente sobre ese personaje. La política downstream decide si el motor lo rechaza, emite warning o lo aplica igual.

`requires` es **documentación ejecutable, no validación de schema**. La API acepta personajes con tags incoherentes. La coherencia es responsabilidad del generador y del curador. Cualquier validador opcional puede consultar `requires`; el contrato duro no lo impone.

### 4.4. Campos específicos por categoría

Cada familia de tag puede declarar bloques propios para atributos exclusivos. Todos son opcionales. Hoy hay curados estos:

  perk:
    efecto_reglado: string  # frase con bonus/penalidad numérico

  aspecto:
    efecto: string                          # mini-frase trigger + probabilidad + efecto
    tags_activables: [tag mental.*, ...]    # tags que el aspecto puede disparar

  skill:
    atributo_dominante: fis | tac | men
    rangos_naturales: [tag rango.*, ...]
    facciones_predominantes: [tag faccion.*, ...]
    equipo_sugerido: [tag equipo.*, ...]

  equipo.arma:
    calibre: string                          # null si no aplica
    tipo_accion: cerrojo | semiauto | automatico | cuerpo_a_cuerpo
    municion_tag_ref: tag equipo.utilitario.*
    alcance_narrativo: corto | medio | largo

  equipo.vestidura:
    faccion_asociada: tag faccion.*

El template programático completo con todos los bloques marcados opcionales vive en [`tag-modelo.yaml`](tag-modelo.yaml). **Los tipos de tag aún no introducidos** (montura, vicio, mascota, etc.) no llevan template anticipado. Se documentan el día que aparece el primer caso real.

---

## §5 — Categorías relacionales: `lealtad` y `nemesis`

Estas dos categorías codifican **vínculos dirigidos** hacia otra entidad. Su slug no es identificador libre — es una **referencia compuesta** con prefijo que indica el tipo de entidad apuntada.

Patrón de referencia compuesta:

  faccion.:
    apunta_a: Facción del catálogo
    forma: lealtad.faccion.{slug}

  pj.:
    apunta_a: Personaje persistido
    forma: lealtad.pj.{slug}  |  nemesis.pj.{slug}

  escuadra.:
    apunta_a: Escuadra (catálogo TBD)
    forma: lealtad.escuadra.{slug}

El prefijo es parte literal del slug compuesto. Un parser que ve `lealtad.faccion.confederados` sabe que es una ref a la facción de slug `confederados`.

### 5.1. `lealtad`

Solo lealtades **reales y declarables**. Las latentes, aspiracionales o secretas se manejan por sistema aparte (TBD). Múltiples `lealtad.*` conviven en un mismo personaje; el orden es indicativo, no normativo.

Para entidades fuera del corpus (personajes históricos no persistidos), **sintetizá un slug estable**. Ejemplo: `lealtad.pj.sargento_ricardo_postmortem` para citar a un mentor caído que no está en el roster activo. La ref no resuelve a registro persistido, pero conserva forma estable.

### 5.2. `nemesis`

Se crea **en caliente** cuando un personaje identifica a otro como rival individual en batalla. Habilita reglas downstream del motor (ej. 50% de probabilidad de seleccionar al némesis como objetivo prioritario — sistema concreto TBD).

Formato único: `nemesis.pj.{slug}`. No se aceptan refs a facciones ni conceptos abstractos.

Un personaje acumula múltiples némesis a lo largo de su vida. **No hay restricción de bando** — un personaje puede tener un némesis del propio bando por accidente, traición personal o vieja deuda. El sistema no lo prohíbe.

### 5.3. Contenedores derivados: Aliados y Némesis

Los tags `lealtad.pj.{slug}` y `nemesis.pj.{slug}` alimentan dos **vistas derivadas** que el motor expone al servir la hoja:

  aliados:
    fuente: Proyección de todos los tags lealtad.pj.* del personaje.
    contenido: Lista de personajes a los que el portador ha jurado lealtad personal.

  nemesis:
    fuente: Proyección de todos los tags nemesis.pj.* del personaje.
    contenido: Lista de personajes identificados como rivales individuales.

Ambos contenedores:

- **Empiezan vacíos** al crear un personaje. Se pueblan en caliente durante batalla, narrativa o curaduría, siempre como consecuencia de agregar el tag relacional correspondiente.
- **No son campos persistidos del schema**. Son vistas computadas al servir, equivalentes a `filiacion` o `fatiga_max` (ver PRD §6.3).
- Son **agnósticas al renderer**: un cliente los muestra como bloques ASCII, tarjetas, grafo de relaciones, o los ignora. El modelo no impone forma.

---

## §6 — Catálogo y persistencia

### 6.1. Estructura de archivos

  tag de un nivel:           mock/tags/{categoria}/{slug}.yaml
  tag con sub-categoría:     mock/tags/{categoria}/{subcategoria}/{slug}.yaml

Ejemplos: `mock/tags/faccion/ejercito_rojo.yaml`, `mock/tags/equipo/arma/pistola.yaml`.

Las categorías relacionales (`lealtad`, `nemesis`) **no tienen entradas en el catálogo**. Su semántica es del formato del tag, no del contenido. Las refs `pj.{slug}` y `faccion.{slug}` resuelven contra los catálogos de personajes y facciones.

### 6.2. Indistinción mock/DB

Los tags del mock y los tags creados en caliente desde la API o el motor de batalla son **indistinguibles**. No hay campo `origen: mock` en el tag aplicado al personaje. Un tag `faccion.ejercito_rojo` cargado de `mock/tags/faccion/ejercito_rojo.yaml` y otro creado al vuelo en una batalla resuelven al mismo identificador. El catálogo `mock/tags/**` es la fuente inicial que siembra la DB al arrancar.

Implicaciones:

- Cualquier tag puede crearse en caliente. Si un narrador agrega `aspecto.cabron` durante una batalla, el aspecto debe existir en el catálogo, o crearse con `origen: custom` antes de aplicarse.
- El motor no se preocupa por de dónde viene el tag, solo por qué dice.

---

## §7 — Extensibilidad

El catálogo canon es **andamiaje, no jaula**. Tres ejes de extensibilidad sin permiso ni migración:

1. **Nuevos valores dentro de una categoría existente** — `skill.lockpicking`, `rasgo.tatuaje_de_ancla`. Entran con `origen: emergente` la primera vez, o `custom` si vienen de un cliente externo.
2. **Nuevas sub-categorías dentro de una familia** — `equipo.montura.caballo_criollo` agrega un nivel a `equipo.*`. El día que aparezca, no antes.
3. **Categorías nuevas enteras** — `oficio_civil.herrero`, `vicio.fuma`, `mascota.perro_pastor`. El parser solo necesita el primer segmento para enrutar.

**Garantía**: un tag desconocido no rompe la hoja.
**No promesa**: que dos generadores coincidan sobre cómo nombrar el mismo concepto.

La fragmentación se mitiga con curaduría, no con validación. Ver PRD §6.6 y tensión 13.7.

---

## §8 — Open Questions

### OQ-tag-2 — `slug` derivado vs persistido en el catálogo

**Resuelta**: `slug` es campo obligatorio del archivo. Ambigüedad cero, redundancia segura.

### OQ-tag-3 — Catálogo de personajes históricos

Personajes referenciados por `lealtad.pj.X` pero no presentes en el roster activo (ej. el Sargento Ricardo) caen al patrón de slug sintético (`lealtad.pj.sargento_ricardo_postmortem`). Pregunta abierta: ¿conviene crear un catálogo separado `mock/personajes_historicos/` para entradas mínimas (slug + nombre + breve nota)?

- Costo: más curaduría.
- Beneficio: refs estables, queryables, y prosa contextual disponible.

### OQ-tag-4 — `excluye` vs `no:` en `require_all`

¿`excluye` agrega valor real sobre `require_all` con prefijo `no:`? Una lectura: `excluye` es más legible al declarar incompatibilidades desde el lado correcto, pero redundante con `no:`. Pendiente decidir si mantener ambos o consolidar en `no:` exclusivo.
