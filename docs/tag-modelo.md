---
title: "Tag Modelo — Referencia del sistema de tags"
tags:
  - syv/docs/schema
  - syv/tags
aliases:
  - Tag Modelo
  - Modelo de Tag
  - tag-modelo
---

# Tag Modelo — Referencia del sistema de tags

> [!info] Estado y Propósito
> - **Estado**: rolling release; este documento describe el vigente.
> - **Propósito**: definir qué es un tag, cómo se escribe, qué puede expresar y cómo se relaciona con la hoja de personaje. La estructura de la hoja completa vive en [[hoja-modelo|hoja-modelo.md]].
> 
> **Material de referencia**:
> - [tag-modelo.yaml](tag-modelo.yaml) — template completo del archivo de catálogo de un tag.
> - [tag-modelo-ejemplos.yaml](tag-modelo-ejemplos.yaml) — cinco personajes que muestran cómo los tags componen una hoja real.
> - `tags/**/*.yaml` — catálogo canon sembrado; consultar para ver tags reales por categoría.

---

## §1 — Mecánica universal del tag

Un **tag** es la unidad atómica del schema. Es un identificador discreto que se aplica a un personaje y comunica una cosa concreta: una habilidad ganada, una marca en la piel, un fusil al hombro, un estado mental de pánico, una lealtad jurada, una enemistad personal.

La regla rectora es una sola:

> [!tip] Regla Rectora
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

**Reglas del slug de tag**: lowercase, underscores como único separador, sin acentos, sin espacios, sin caracteres especiales. Ejemplos: `pistola`, `precision`, `ejercito_rojo`, `lider_de_escuadra`. El slug de un tag es **legible por diseño** — es la pieza humana de la notación punto.

> [!important] Asimetría de Slugs
> El slug de tag es distinto del **slug de personaje** (`identidad.slug`). Este último es una **patente opaca de 8 caracteres `[A-Z0-9]`** (ej. `K9F2H3M4`), no un nombre legible. Ver [[hoja-modelo#1.1. slug — la patente del personaje|hoja-modelo.md §1.1]] para las reglas del slug de personaje.
> 
> Las refs a otros personajes (vínculos personales) **no son tags** — viven en las colecciones `personaje.aliados[]` y `personaje.nemesis[]`. Ver [[#5.1. Lealtades y enemistades personales — NO son tags|§5.1]].

**Repetibilidad**: `tags[]` es un multiset. Tres `equipo.utilitario.cargador` significan tres cargadores físicos. El motor itera, no deduplica.

**Resolución contra el catálogo**: el parser troza el tag por `.` y mapea segmentos a directorios. `equipo.arma.pistola` resuelve a `tags/equipo/arma/pistola.yaml`. Ver §6.

Para ver tags concretos en uso compuesto sobre personajes, consultar [tag-modelo-ejemplos.yaml](tag-modelo-ejemplos.yaml).

---

## §3 — Categorías de referencia

Las categorías curadas hasta hoy. **No es un canon cerrado**: el sistema acepta categorías nuevas sin migración (ver §7). Tomalas como puntos de referencia, no como menú restrictivo. Para ver los slugs reales de cada categoría, consultar el directorio `tags/{categoria}/` correspondiente.

  faccion:
    significado: Pertenencia macro (bando).
  subfaccion:
    significado: Grupo militar o político subordinado a una facción principal.
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
    significado: >
      Rasgo de carácter, condición física o identidad mecánicamente activa.
      Cada trait declara un campo `efecto` con uno o más modificadores sobre
      el vocabulario canónico (FISICO/TACTICO/MENTAL/INICIATIVA/MORAL/
      FATIGA/MOVIMIENTO/ESTRESS). Polaridad mixta — admite positivos, neutros
      y penalidades, todos en la misma bolsa.
  perk:
    significado: >
      Ventaja reglada con efecto numérico, otorgada al azar como recompensa
      narrativa (típicamente vía hito en campo). Sin pool por rango ni
      precondiciones — un perk es siempre una sorpresa. No usa `requires`.
  efecto:
    significado: Bloque de efecto de juego estructurado, referenciable por otros tags.
  skill:
    significado: >
      Habilidad técnica aprendida que habilita y resuelve chequeos contra su
      atributo dominante (`fis`, `tac` o `men`). El motor pregunta "¿el personaje
      tiene skill X?" y, si la respuesta es sí, tira contra el atributo declarado
      en el campo `skill.atributo_dominante`. Una skill nunca aplica modificador
      directo a stats — es siempre un habilitador de tirada. Ver [[atributos-y-efectos|atributos-y-efectos.md]].
  equipo:
    significado: Equipo cargado por el personaje.
    subcategorias: [arma, utilitario, vestidura]
  rol:
    significado: Roles operativos.
    subcategorias: [oficio, jerarquia, narrativo, combate]
  lealtad:
    significado: Lealtad a facción, subfacción o escuadra. Relacional. Ver §5.
    subcategorias_implicitas: [faccion, subfaccion, escuadra]
    nota: Las lealtades personales viven en personaje.aliados[], NO acá.

El motor acepta tags fuera del canon. Marcalos con `origen: custom`. La coherencia del catálogo la sostiene la curaduría, no la integridad referencial.

---

## §4 — Campos del archivo de catálogo

Cada tag canon o emergente tiene una entrada en el catálogo. La filosofía es **mostrativa, no obligatoria**: cuatro campos son siempre requeridos. Todo lo demás es opcional y se declara solo si suma información real.

El template completo con todos los campos posibles vive en [tag-modelo.yaml](tag-modelo.yaml), usando dos marcas:

- `(*)` — campo obligatorio siempre.
- `(+)` — campo obligatorio cuando la categoría o subcategoría lo demanda.

### 4.1. Campos obligatorios siempre — los cuatro `(*)`

```yaml
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
```

### 4.2. Campos obligatorios condicionales — los `(+)`

Estos campos son obligatorios solo cuando la categoría o subcategoría del tag los demanda. Fuera de su contexto, no aplican.

```yaml
subcategoria:
  obligatorio_si: categoria ∈ {equipo, rol}
  uso: Segmento intermedio del tag (ej. "arma" para equipo.arma.pistola).

peso:
  obligatorio_si: categoria = equipo
  tipo: int (0..50)
  unidad: kg
  nota: No confundir con peso_narrativo (hint 1..5 al sorteador).

efecto:
  obligatorio_si: categoria = trait (salvo si tiene trigger) o categoria = efecto
  uso: String o lista de strings con los modificadores de atributos o estadísticas calculadas, sobre el vocabulario canónico de [[atributos-y-efectos|atributos-y-efectos.md]].

equipo_arma.tipo_accion:
  obligatorio_si: subcategoria = arma
  enum: [cerrojo, semiauto, automatico, cuerpo_a_cuerpo]

equipo_arma.alcance:
  obligatorio_si: subcategoria = arma
  enum: [corto, medio, largo]

subfaccion.faccion_padre:
  obligatorio_si: categoria = subfaccion
  tipo: tag faccion.*
  uso: Referencia a la facción principal a la que pertenece la subfacción.
```

### 4.3. Campos comunes opcionales

Declaralos solo si aportan información real:

```yaml
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
```

### 4.4. Sistema `requires` — dependencias del tag

El bloque `requires` declara cuándo un tag es coherente sobre un personaje. Tiene dos sub-bloques, ambos opcionales y combinables:

```yaml
require_all:
  semantica: El personaje debe tener TODOS estos tags.

require_any:
  semantica: Basta con UNO de estos tags.
```

**Modificador NOT**: prefijá cualquier entrada con `"no:"` para invertir la condición. La forma es **string con prefijo literal** — sin objetos anidados, queryable con un `startswith("no:")` desde cualquier consumidor, obvia a la lectura humana.

`requires` es **documentación ejecutable, no validación de schema**. La API acepta personajes con tags incoherentes. La coherencia es responsabilidad del generador y del curador. Cualquier validador opcional puede consultar `requires`; el contrato duro no lo impone.

**Exclusión deliberada — `perk` no usa `requires`.** Los perks son recompensas narrativas otorgadas al azar como sorpresa (típicamente vía hito en campo); no tienen pool por rango ni precondiciones de pertenencia. Cualquier perk puede aparecer sobre cualquier personaje. Reservar `requires` para categorías cuya coherencia depende del set de tags ya presente (típicamente skills avanzadas que asumen una base, o traits que asumen una condición previa).

### 4.5. Bloques específicos por categoría

Cada familia de tag declara bloques propios para atributos exclusivos: `perk`, `skill`, `equipo_arma`, `equipo_vestidura`, `subfaccion`. Sus campos internos son opcionales salvo los marcados `(+)` en §4.2.

El template completo de cada bloque vive en [tag-modelo.yaml](tag-modelo.yaml). Para ejemplos canon ya curados, consultar los archivos correspondientes bajo `tags/`.

**Los tipos de tag aún no introducidos** (montura, vicio, mascota, etc.) no llevan template anticipado. Se documentan el día que aparece el primer caso real.

### 4.6. Efectos y triggers

Para modularizar el comportamiento mecánico de los tags y habilitar que un mismo tag aplique múltiples efectos discretos o responda a eventos en partida, se incorporan los bloques opcionales `trigger` (con su propiedad `trigger-action`) y `efecto` (a nivel raíz del tag). Los efectos representan modificaciones o estados de juego estructurados.

La estructura distingue entre dos comportamientos mecánicos:

- **Efectos Gatillados (Con Trigger y Reactivos)**: Si el efecto se aplica de forma temporal o reactiva ante un evento en partida (ej. al fallar un chequeo moral o recibir daño), se define el bloque `trigger` en la raíz. En este caso, se usa la propiedad `trigger-action` dentro del bloque `trigger` para listar las referencias a los efectos gatillados (los cuales se definen en archivos independientes en la categoría `efecto.*`).
- **Efectos Pasivos/Permanentes (Sin Trigger)**: Si los efectos se aplican de forma permanente y constante mientras el personaje posea el tag, no se define el bloque `trigger`. En su lugar, el tag define su efecto de forma **inline** bajo la propiedad `efecto`, tomando la forma de un mapa `{slug_efecto: [instrucciones]}`. Esto elimina la necesidad de crear un archivo independiente en `tags/efecto/`.

Estructura del bloque `trigger`:

```yaml
trigger:
  evento: str          # Evento que dispara el trigger (ej. chequeo_moral, daño_recibido, bajo_fuego).
  condicion: str       # Condición del evento (ej. fallado, primera_vez).
  probabilidad: float  # Opcional. Rango 0.0..1.0 (o string de porcentaje tipo "50%").
  trigger-action:      # Lista de referencias a tags de la categoría efecto.*
    - tag efecto.*     # Ej: efecto.furioso
```

Estructura de efectos permanentes/pasivos inline (a nivel raíz del tag):

```yaml
efecto:                # String o lista de strings. Modificadores directos de atributos base o estadísticas calculadas.
  - str                # Ej: "(+2) INICIATIVA"
```

> [!tip] Variables Permitidas en Efectos
> Los modificadores de efectos solo pueden apuntar a:
> - Atributos base: `FISICO`, `TACTICO`, `MENTAL`
> - Estadísticas calculadas: `INICIATIVA`, `MORAL`, `FATIGA`, `MOVIMIENTO`, `ESTRESS`
> 
> Ejemplos: `"(+1) MENTAL"`, `"-100% MOVIMIENTO"`, `"(-1) FATIGA"`, `"(-1) ESTRESS"`. Ver [[atributos-y-efectos|atributos-y-efectos.md]].

Los tags de la categoría `efecto.*` que se definen como archivos independientes (bajo `tags/efecto/{slug}.yaml`) detallan sus instrucciones utilizando el campo `efecto` a nivel de categoría como una lista simple de strings:

```yaml
efecto:                # Lista de instrucciones o modificadores de comportamiento
  - str                # Ej: "marcar objetivo: cualquier enemigo", "-50% a todas sus tiradas"
```

### 4.7. Traits — identidad mecánicamente activa

Los **traits** (`trait.*`) son tags de identidad: rasgo de carácter, condición física o marca de comportamiento. Cada trait declara un campo `efecto` con uno o más modificadores sobre el vocabulario canónico (ver [[atributos-y-efectos|atributos-y-efectos.md]]). Polaridad mixta: el catálogo admite positivos (`carismatico`, `veterano`), penalidades (`cobarde`, `hemorragia_lenta`) y combinaciones (`terco`: `+MORAL`/`-INICIATIVA`).

La categoría es abierta y se expande ante necesidades narrativas. Los traits del catálogo (`tags/trait/*.yaml`) son la semilla canónica.

#### Estructura de un Trait

- Si el trait es **pasivo/permanente**, define el bloque raíz `efecto` (string o lista de strings).
- Si el trait es **reactivo/temporal** (se gatilla ante un evento), define un bloque `trigger` con su correspondiente lista de `trigger-action` apuntando a un efecto externo del catálogo `efecto.*`.

Ejemplo de Trait Pasivo (`trait.vanguardia`):
```yaml
tag:
  slug: vanguardia
  nombre: "Vanguardia"
  categoria: trait
  descripcion: >
    Personajes que siempre van al frente con confianza. El rasgo más valioso para un defensor.
  efecto:
    - "(+2) INICIATIVA"
    - "(+1) MORAL"
```

Ejemplo de Trait Reactivo (con trigger):
```yaml
tag:
  slug: ejemplo_reactivo
  nombre: "Ejemplo reactivo"
  categoria: trait
  descripcion: >
    Trait que se gatilla ante un evento concreto en partida.
  trigger:
    evento: chequeo_moral
    condicion: fallado
    probabilidad: 0.5
    trigger-action:
      - efecto.furioso
```

> [!info] Nota Histórica: Eliminación de aspectos
> La categoría `aspecto.*` se eliminó. Su semántica (identidad con efecto declarado) se fusiona con `trait.*`. Los antiguos aspectos del catálogo se migraron como traits.

---

## §5 — Categoría relacional: `lealtad` (a facciones, subfacciones y escuadras)

`lealtad` codifica **vínculos dirigidos** hacia una facción, subfacción o escuadra. Su slug no es identificador libre — es una **referencia compuesta** con prefijo que indica el tipo de entidad apuntada.

Patrón de referencia compuesta:

```yaml
faccion.:
  apunta_a: Facción del catálogo.
  forma: lealtad.faccion.{slug}

subfaccion.:
  apunta_a: Subfacción del catálogo.
  forma: lealtad.subfaccion.{slug}

escuadra.:
  apunta_a: Escuadra (catálogo TBD).
  forma: lealtad.escuadra.{slug}
```

El prefijo es parte literal del slug compuesto. Un parser que ve `lealtad.faccion.confederados` sabe que es una ref a la facción de slug `confederados`, y `lealtad.subfaccion.pelicanos` apunta a la subfacción de slug `pelicanos`.

Solo lealtades **reales y declarables**. Las latentes, aspiracionales o secretas se manejan por sistema aparte (TBD). Múltiples `lealtad.*` conviven en un mismo personaje; el orden es indicativo, no normativo.

### 5.1. Lealtades y enemistades personales — NO son tags

Los vínculos personales (a otro personaje) **no se expresan como tags**. Viven en colecciones persistidas de primera clase sobre la hoja:

- `personaje.aliados[]` — list de `{ref, descripcion, desde?}`. Ver [[hoja-modelo#§3.4. Aliados y némesis — colecciones persistidas|hoja-modelo.md §3.4]].
- `personaje.nemesis[]` — list de `{ref, descripcion, desde?}`. Mismo lifecycle.

**Por qué no son tags**: un vínculo personal lleva prosa (la historia del vínculo). Un tag puede afirmar la relación pero no contarla. Las colecciones llevan la textura narrativa.

**Ejemplo**:

```yaml
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
```

**Sin restricción de bando para némesis**: un personaje puede tener un némesis del propio bando por accidente, traición personal o vieja deuda. El sistema no lo prohíbe.

---

## §6 — Catálogo y persistencia

### 6.1. Estructura de archivos

```yaml
tag de un nivel:           tags/{categoria}/{slug}.yaml
tag con sub-categoría:     tags/{categoria}/{subcategoria}/{slug}.yaml
```

La categoría relacional `lealtad` **no tiene entradas en el catálogo**. Su semántica es del formato del tag, no del contenido. Las refs `faccion.{slug}`, `subfaccion.{slug}` y `escuadra.{slug}` resuelven contra los catálogos respectivos. Los vínculos personales (a otro personaje) no son tags — ver §5.1.

### 6.2. Indistinción mock/DB

Los tags del mock y los tags creados en caliente desde la API o el motor de batalla son **indistinguibles**. No hay campo `origen: mock` en el tag aplicado al personaje. Un tag `faccion.ejercito_rojo` cargado de `tags/faccion/ejercito_rojo.yaml` y otro creado al vuelo en una batalla resuelven al mismo identificador. El catálogo `tags/**` es la fuente inicial que siembra la DB al arrancar.

Implicaciones:

- Cualquier tag puede crearse en caliente. Si un narrador agrega `trait.cabron` durante una batalla, el trait debe existir en el catálogo, o crearse con `origen: custom` antes de aplicarse.
- El motor no se preocupa por de dónde viene el tag, solo por qué dice.

---

## §7 — Extensibilidad

El catálogo canon es **andamiaje, no jaula**. Tres ejes de extensibilidad sin permiso ni migración:

1. **Nuevos valores dentro de una categoría existente** — `skill.lockpicking`, `rasgo.tatuaje_de_ancla`. Entran con `origen: emergente` la primera vez, o `custom` si vienen de un cliente externo.
2. **Nuevas sub-categorías dentro de una familia** — `equipo.montura.caballo_criollo` agrega un nivel a `equipo.*`. El día que aparezca, no antes.
3. **Categorías nuevas enteras** — `oficio_civil.herrero`, `vicio.fuma`, `mascota.perro_pastor`. El parser solo necesita el primer segmento para enrutar.

**Garantía**: un tag desconocido no rompe la hoja.
**No promesa**: que dos generadores coincidan sobre cómo nombrar el mismo concepto.

La fragmentación se mitiga con curaduría, no con validación. Ver tensiones T-02 y T-07.

Para ver extensibilidad en uso real, consultar [tag-modelo-ejemplos.yaml](tag-modelo-ejemplos.yaml) — los personajes 2 (chamán) y 4 (pandillero) usan tags `origen: custom` para roles narrativos que no existían antes.

---

## §8 — Open Questions

> [!faq] Open Questions
> Pendientes específicos del sistema de tags. Open questions de producto en la página Notion del proyecto.

### OQ-tag-3 — Catálogo de personajes históricos

Personajes referenciados por `aliados[].ref` o `nemesis[].ref` pero ausentes del roster activo (mentores caídos citados en vínculos, figuras del pasado). ¿Conviene crear un catálogo separado `mock/personajes_historicos/` con entradas mínimas (patente sintética + nombre + breve nota) o tolerar refs colgadas?

- Costo: más curaduría.
- Beneficio: refs estables, queryables, y prosa contextual disponible.

Relacionado: OQ-01 y la tensión T-04 (sin validación de refs).

### OQ-tag-4 — `excluye` vs `no:` en `require_all`

¿`excluye` agrega valor real sobre `require_all` con prefijo `no:`? `excluye` es más legible al declarar incompatibilidades desde el lado correcto, pero redundante con `no:`. Pendiente decidir si mantener ambos o consolidar en `no:` exclusivo.
