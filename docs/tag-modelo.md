# Tag Modelo — Referencia del sistema de tags

> **Estado**: rolling release; este documento describe el vigente.
> **Propósito**: definir qué es un tag, cómo se escribe, qué puede expresar y cómo se relaciona con la hoja de personaje. La estructura de la hoja completa vive en [`hoja-modelo.md`](hoja-modelo.md).
>
> **Material de referencia**:
> - [`tag-modelo.yaml`](tag-modelo.yaml) — template completo del archivo de catálogo de un tag.
> - [`tag-modelo-ejemplos.yaml`](tag-modelo-ejemplos.yaml) — cinco personajes que muestran cómo los tags componen una hoja real.
> - `mock/tags/**/*.yaml` — catálogo canon sembrado; consultar para ver tags reales por categoría.

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

**Reglas del slug de tag**: lowercase, underscores como único separador, sin acentos, sin espacios, sin caracteres especiales. Ejemplos: `pistola`, `tirador_preciso`, `ejercito_rojo`, `lider_de_escuadra`. El slug de un tag es **legible por diseño** — es la pieza humana de la notación punto.

> **Importante** — el slug de tag es distinto del **slug de personaje** (`identidad.slug`). Este último es una **patente opaca de 8 caracteres `[A-Z0-9]`** (ej. `K9F2H3M4`), no un nombre legible. Ver `hoja-modelo.md` para las reglas del slug de personaje. Las refs a otros personajes (vínculos personales) **no son tags** — viven en las colecciones `personaje.aliados[]` y `personaje.nemesis[]`. Ver §5.1.

**Repetibilidad**: `tags[]` es un multiset. Tres `equipo.utilitario.cargador` significan tres cargadores físicos. El motor itera, no deduplica.

**Resolución contra el catálogo**: el parser troza el tag por `.` y mapea segmentos a directorios. `equipo.arma.pistola` resuelve a `mock/tags/equipo/arma/pistola.yaml`. Ver §6.

Para ver tags concretos en uso compuesto sobre personajes, consultar [`tag-modelo-ejemplos.yaml`](tag-modelo-ejemplos.yaml).

---

## §3 — Categorías de referencia

Las categorías curadas hasta hoy. **No es un canon cerrado**: el sistema acepta categorías nuevas sin migración (ver §7). Tomalas como puntos de referencia, no como menú restrictivo. Para ver los slugs reales de cada categoría, consultar el directorio `mock/tags/{categoria}/` correspondiente.

  faccion:
    significado: Pertenencia macro (bando).

  rango:
    significado: Designación operativa jerárquica de campo.

  escuadra:
    significado: Asignación a una escuadra concreta.

  mando:
    significado: Capacidad de mando dentro de la facción.

  estado:
    significado: Disponibilidad operativa. Exactamente uno por personaje.

  salud:
    significado: Estado físico actual. Acumulable.

  mental:
    significado: Estado anímico actual. Acumulable.

  rasgo:
    significado: Rasgo físico observable.

  trait:
    significado: Rasgo de carácter sin mecánica activa.

  perk:
    significado: Ventaja reglada con efecto numérico.

  aspecto:
    significado: Mini-tag identitario con efecto mecánico en mini-frase.

  efecto:
    significado: Bloque de efecto de juego estructurado, referenciable por otros tags.

  skill:
    significado: Habilidad aprendida o entrenada.

  equipo:
    significado: Equipo cargado por el personaje.
    subcategorias: [arma, utilitario, vestidura]

  rol:
    significado: Roles operativos.
    subcategorias: [oficio, jerarquia, narrativo, combate]

  lealtad:
    significado: Lealtad a facción o escuadra. Relacional. Ver §5.
    subcategorias_implicitas: [faccion, escuadra]
    nota: Las lealtades personales viven en personaje.aliados[], NO acá.

El motor acepta tags fuera del canon. Marcalos con `origen: custom`. La coherencia del catálogo la sostiene la curaduría, no la integridad referencial.

---

## §4 — Campos del archivo de catálogo

Cada tag canon o emergente tiene una entrada en el catálogo. La filosofía es **mostrativa, no obligatoria**: cuatro campos son siempre requeridos. Todo lo demás es opcional y se declara solo si suma información real.

El template completo con todos los campos posibles vive en [`tag-modelo.yaml`](tag-modelo.yaml), usando dos marcas:

- `(*)` — campo obligatorio siempre.
- `(+)` — campo obligatorio cuando la categoría o subcategoría lo demanda.

### 4.1. Campos obligatorios siempre — los cuatro `(*)`

  slug:
    tipo: string
    regla: Último segmento del tag. Lowercase + underscore, sin acentos.

  nombre:
    tipo: string
    regla: Etiqueta legible humana corta, 1-3 palabras, sin slugificar.
    proposito: Lo que un renderer muestra como label.

  categoria:
    tipo: string
    regla: Primer segmento del tag. Si la categoría tiene sub-niveles, este campo guarda solo la raíz; `subcategoria` lleva el intermedio.

  descripcion:
    tipo: string
    regla: 1-3 frases canónicas.
    proposito: Única fuente de la prosa del tag. Nunca se persiste dentro del personaje.

### 4.2. Campos obligatorios condicionales — los `(+)`

Estos campos son obligatorios solo cuando la categoría o subcategoría del tag los demanda. Fuera de su contexto, no aplican.

  subcategoria:
    obligatorio_si: categoria ∈ {equipo, rol}
    uso: Segmento intermedio del tag (ej. "arma" para equipo.arma.pistola).

  peso:
    obligatorio_si: categoria = equipo
    tipo: int (0..50)
    unidad: kg
    nota: No confundir con peso_narrativo (hint 1..5 al sorteador).

  efectos:
    obligatorio_si: categoria = aspecto
    uso: Lista de referencias a tags de la categoría efecto.* que se aplican con el tag (reemplaza a aspecto.efecto).

  equipo_arma.tipo_accion:
    obligatorio_si: subcategoria = arma
    enum: [cerrojo, semiauto, automatico, cuerpo_a_cuerpo]

Ver también [`tag-requeridos-por-categoria.md`](tag-requeridos-por-categoria.md) — índice rápido bullet-point de todos los `(+)` por categoría.

### 4.3. Campos comunes opcionales

Declaralos solo si aportan información real:

  origen:
    enum: [canon, emergente, custom]
    default: emergente
    regla: Usar `emergente` si el archivo nació al vuelo y se promovió. Usar `custom` para entradas de clientes externos.

  metadatos:
    uso: Auditoría del catálogo.
    campos: [version_introducida, creado_en, ultima_actualizacion]

  requires:
    uso: Precondiciones de coherencia. Ver §4.4.

  excluye:
    uso: Lista de tags incompatibles. Si el personaje tiene cualquiera, el tag no debería aplicarse.
    nota: Simétrico al prefijo `no:` de `requires`. Ver OQ-tag-4.

  tags_relacionados:
    uso: Tags que típicamente acompañan a este. Informativo, no normativo.

  peso_narrativo:
    tipo: int (1..5)
    uso: Hint al sorteador sobre frecuencia apropiada. No es probabilidad estricta.

### 4.4. Sistema `requires` — dependencias del tag

El bloque `requires` declara cuándo un tag es coherente sobre un personaje. Tiene dos sub-bloques, ambos opcionales y combinables:

  require_all:
    semantica: El personaje debe tener TODOS estos tags.

  require_any:
    semantica: Basta con UNO de estos tags.

**Modificador NOT**: prefijá cualquier entrada con `"no:"` para invertir la condición. La forma es **string con prefijo literal** — sin objetos anidados, queryable con un `startswith("no:")` desde cualquier consumidor, obvia a la lectura humana.

Para ver el bloque `requires` aplicado a un tag real, consultar `mock/tags/perk/tirador_preciso.yaml`.

`requires` es **documentación ejecutable, no validación de schema**. La API acepta personajes con tags incoherentes. La coherencia es responsabilidad del generador y del curador. Cualquier validador opcional puede consultar `requires`; el contrato duro no lo impone.

### 4.5. Bloques específicos por categoría

Cada familia de tag declara bloques propios para atributos exclusivos: `perk`, `aspecto`, `skill`, `equipo_arma`, `equipo_vestidura`. Sus campos internos son opcionales salvo los marcados `(+)` en §4.2.

El template completo de cada bloque vive en [`tag-modelo.yaml`](tag-modelo.yaml). Para ejemplos canon ya curados, consultar los archivos correspondientes bajo `mock/tags/`.

**Los tipos de tag aún no introducidos** (montura, vicio, mascota, etc.) no llevan template anticipado. Se documentan el día que aparece el primer caso real.

### 4.6. Efectos y triggers

Para modularizar el comportamiento mecánico de los tags y habilitar que un mismo tag aplique múltiples efectos discretos o responda a eventos en partida, se incorporan los bloques opcionales `trigger` (con su propiedad `trigger-action`) y `efecto` (a nivel raíz del tag). Los efectos representan modificaciones o estados de juego estructurados.

La estructura distingue entre dos comportamientos mecánicos:

- **Efectos Gatillados (Con Trigger y Reactivos)**: Si el efecto se aplica de forma temporal o reactiva ante un evento en partida (ej. al fallar un chequeo moral o recibir daño), se define el bloque `trigger` en la raíz. En este caso, se usa la propiedad `trigger-action` dentro del bloque `trigger` para listar las referencias a los efectos gatillados (los cuales se definen en archivos independientes en la categoría `efecto.*`).
- **Efectos Pasivos/Permanentes (Sin Trigger)**: Si los efectos se aplican de forma permanente y constante mientras el personaje posea el tag, no se define el bloque `trigger`. En su lugar, el tag define su efecto de forma **inline** bajo la propiedad `efecto`, tomando la forma de un mapa `{slug_efecto: [instrucciones]}`. Esto elimina la necesidad de crear un archivo independiente en `mock/tags/efecto/`.

Estructura del bloque `trigger`:

  trigger:
    evento: str          # Evento que dispara el trigger (ej. chequeo_moral, daño_recibido, bajo_fuego).
    condicion: str       # Condición del evento (ej. fallado, primera_vez).
    probabilidad: float  # Opcional. Rango 0.0..1.0 (o string de porcentaje tipo "50%").
    trigger-action:      # Lista de referencias a tags de la categoría efecto.*
      - tag efecto.*     # Ej: efecto.furioso

Estructura de efectos permanentes/pasivos inline (a nivel raíz del tag):

  efecto:                # Mapa del efecto inline
    {slug_efecto}:       # Slug del efecto (usualmente el mismo del aspecto)
      - str              # Lista de instrucciones. Ej: "(+2) iniciativa"

Los tags de la categoría `efecto.*` que se definen como archivos independientes (bajo `mock/tags/efecto/{slug}.yaml`) detallan sus instrucciones utilizando el campo `efecto` a nivel de categoría como una lista simple:

  efecto:                # Lista de instrucciones o modificadores de comportamiento
    - str                # Ej: "marcar objetivo: cualquier enemigo", "-50% a todas sus tiradas"

### 4.7. Aspectos

Los **aspectos** (`aspecto.*`) son tags identitarios de grano medio que aportan color, particularidad y trasfondo al personaje. A diferencia de los efectos simples (que suelen ser temporales o de corta duración), los aspectos representan frases complejas de identidad y comportamiento que pueden gatillar o aplicar múltiples efectos.

Los aspectos más comunes y básicos del catálogo (como `aspecto.vanguardia` o `aspecto.cabron`) se usan como referencia, pero la categoría está diseñada para ser abierta y expandirse ante necesidades narrativas.

#### Estructura de un Aspecto
- Si el aspecto es **reactivo/temporal** (se gatilla ante un evento), define un bloque `trigger` con su correspondiente lista de `trigger-action` apuntando a un efecto externo en el catálogo.
- Si el aspecto es **pasivo/permanente**, define directamente el bloque raíz `efecto` de forma inline como un mapa `{slug_efecto: [modificadores]}`.

Ejemplo de Aspecto Reactivo (`aspecto.cabron`):
```yaml
tag:
  slug: cabron
  nombre: "Cabrón"
  categoria: aspecto
  descripcion: >
    De temperamento hosco y difícil, no tolera tonterías y reacciona de forma agresiva.
  trigger:
    evento: chequeo_moral
    condicion: fallado
    probabilidad: 0.5
    trigger-action:
      - efecto.furioso
```

Ejemplo de Aspecto Permanente (`aspecto.vanguardia`):
```yaml
tag:
  slug: vanguardia
  nombre: "Vanguardia"
  categoria: aspecto
  descripcion: >
    Personajes que siempre van al frente con confianza. Es el aspecto más valioso para un defensor.
  efecto:
    vanguardia:
      - "(+2) defensa"
      - "(+2) iniciativa"
      - "(+2) aggro" # El aggro se utiliza para el sistema de elección de objetivos
```

---

## §5 — Categoría relacional: `lealtad` (a facciones y escuadras)

`lealtad` codifica **vínculos dirigidos** hacia una facción o escuadra. Su slug no es identificador libre — es una **referencia compuesta** con prefijo que indica el tipo de entidad apuntada.

Patrón de referencia compuesta:

  faccion.:
    apunta_a: Facción del catálogo.
    forma: lealtad.faccion.{slug}

  escuadra.:
    apunta_a: Escuadra (catálogo TBD).
    forma: lealtad.escuadra.{slug}

El prefijo es parte literal del slug compuesto. Un parser que ve `lealtad.faccion.confederados` sabe que es una ref a la facción de slug `confederados`.

Solo lealtades **reales y declarables**. Las latentes, aspiracionales o secretas se manejan por sistema aparte (TBD). Múltiples `lealtad.*` conviven en un mismo personaje; el orden es indicativo, no normativo.

### 5.1. Lealtades y enemistades personales — NO son tags

Los vínculos personales (a otro personaje) **no se expresan como tags**. Viven en colecciones persistidas de primera clase sobre la hoja:

- `personaje.aliados[]` — list de `{ref, descripcion, desde?}`. Ver [`hoja-modelo.md §3.4`](hoja-modelo.md).
- `personaje.nemesis[]` — list de `{ref, descripcion, desde?}`. Mismo lifecycle.

**Por qué no son tags**: un vínculo personal lleva prosa (la historia del vínculo). Un tag puede afirmar la relación pero no contarla. Las colecciones llevan la textura narrativa.

**Ejemplo**:

  personaje.aliados:
    - ref: SRG1H4F9
      descripcion: >
        El sargento Ricardo lo formó tirador. Cayó en la ofensiva del Tercer Año.
        Cabral no falla un disparo a menos de doscientos metros — es la manera que
        encontró de no olvidarlo.
      desde: "2024-03-15"

  personaje.nemesis:
    - ref: K9F2H3M4
      descripcion: >
        Lo identificó como rival en el cruce del río — vio al otro disparar contra
        un médico desarmado. Desde entonces busca su cabeza específicamente.

**Sin restricción de bando para némesis**: un personaje puede tener un némesis del propio bando por accidente, traición personal o vieja deuda. El sistema no lo prohíbe.

---

## §6 — Catálogo y persistencia

### 6.1. Estructura de archivos

  tag de un nivel:           mock/tags/{categoria}/{slug}.yaml
  tag con sub-categoría:     mock/tags/{categoria}/{subcategoria}/{slug}.yaml

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

Para ver extensibilidad en uso real, consultar [`tag-modelo-ejemplos.yaml`](tag-modelo-ejemplos.yaml) — los personajes 2 (chamán) y 4 (pandillero) usan tags `origen: custom` para roles narrativos que no existían antes.

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
