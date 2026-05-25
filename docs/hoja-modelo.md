# Hoja Modelo — Referencia del personaje

> **Estado**: rolling release; este documento describe el vigente.
> **Propósito**: definir la estructura de la hoja de personaje campo por campo.
>
> **Material de referencia**:
> - [`hoja-modelo.yaml`](hoja-modelo.yaml) — template programático del personaje vacío.
> - [`tag-modelo.md`](tag-modelo.md) — sistema de tags: definición, categorías, catálogo.
> - [`tag-modelo-ejemplos.yaml`](tag-modelo-ejemplos.yaml) — cinco personajes ejemplo en composición.

---

## §0 — Estructura de la hoja

Seis bloques estructurados más la lista plana de tags:

  personaje:
    identidad:    { slug, nombre, sobrenombre, rol, genero, edad }
    atributos:    { fis, tac, men }
    tags:         [...]      # lista plana de strings en notación punto
    historia:     str        # prosa biográfica congelada
    historial:    [...]      # eventos temporales (hitos)
    metadatos:    { creado_en, canonizado_en, ultima_actualizacion }
    extras:       object | null

**Regla rectora**: todo lo que puede ser discreto y no es identidad, atributo, prosa o auditoría — es tag. La justificación detallada vive en [`tag-modelo.md` §1](tag-modelo.md).

---

## §1 — Identidad

Quién es el personaje, fuera de su contexto operativo.

### 1.1. `slug` — la patente del personaje

El `slug` es la **patente opaca** del personaje. No es su nombre. Es el identificador estable que el sistema usa para referenciarlo en cualquier vínculo (refs `lealtad.pj.{slug}`, `nemesis.pj.{slug}`, eventos del historial, ediciones por API).

  slug:
    formato_protocolo: ^[A-Z0-9]{8}$
    formato_db: ^[A-Za-z0-9_]+$           # más laxo; ver nota abajo
    ejemplos: [K9F2H3M4, SLG3D7K2, NMC8H5P9]
    generacion: Servidor genera al persistir (random + colisión-check).
    custom: Admitido para mock data o curaduría manual; mismo regex y mismo check.
    mutable: false

**Por qué patente y no nombre**: dos personajes pueden llamarse igual; sus patentes no colisionan. Una refactorización narrativa (cambio de apellido por casamiento, alias revolucionario, etc.) no invalida refs existentes. Los renderers muestran `nombre`; los sistemas guardan `slug`.

**Exclusión por protocolo, no por base de datos**. La base permite el regex laxo `^[A-Za-z0-9_]+$` sin límite estricto de tamaño — esto deja la puerta abierta a casos especiales (slugs sintéticos para personajes históricos, slugs de tag como `pistola` o `lanzamisiles`, slugs de facciones como `ejercito_rojo`). El protocolo del personaje **se restringe a sí mismo** a 8 caracteres `[A-Z0-9]` para evitar colisiones por escala y mantener URLs/refs predecibles. Los validadores rechazan slugs de personaje fuera del protocolo; la DB no.

### 1.2. Resto del bloque

  nombre:
    tipo: string
    ejemplo: "Walter Aguirre"
    mutable: false                        # inmutable tras canonizar

  sobrenombre:
    tipo: string | null
    derivacion: Derivable al servir desde nombre + tags rango.* + tags rol.* de mando.
    nota: null cuando no hay distinción con el nombre real.

  rol:
    tipo: string
    default: ciudadano
    proposito: Identidad narrativa base (no posición operativa).
    ejemplos: ["Sargento Confederado", "Líder Revolucionario", "Médico de campaña"]
    aclaracion: NO confundir con tags rol.* — esos viven en tags[] y expresan la capa operativa.

  genero:
    tipo: string
    enum_abierto: [masculino, femenino, no_binario, otro]

  edad:
    tipo: int
    nota: Years al momento de creación. Mutable por decisión narrativa explícita, sin hito formal.

---

## §2 — Atributos

Tres valores numéricos que definen la capacidad base.

  fis:
    significado: Resistencia, potencia bruta.
    rango: 2..5

  tac:
    significado: Precisión, coordinación, reflejos.
    rango: 2..5

  men:
    significado: Liderazgo, moral base, resistencia psicológica.
    rango: 2..7                # hasta 7 en líderes

**Determinísticos por rango en creación**. Mutables solo vía hito `triple_cero` o `mejora_atributo`. Son las **únicas magnitudes numéricas persistidas** — toda otra capacidad derivada (fatiga máxima, moral máxima, mando vigente, fza_aportada) se calcula en caliente con fórmulas fijas, no se persiste, para evitar drift.

---

## §3 — Tags

Lista plana de strings en notación punto. Es la fuente de verdad de todo lo discreto del personaje.

**La definición completa, las categorías canon, el formato y las reglas de catálogo viven en [`tag-modelo.md`](tag-modelo.md)**. Acá solo se resume el contrato con la hoja.

  forma: <categoria>[.<subcategoria>].<slug>
  tipo:  list[str]              # multiset, no set — admite repetidos
  default: []

### 3.1. Derivaciones desde tags

El motor calcula al servir, sin persistir, para evitar drift:

  filiacion:
    fuente: tags rango.* + escuadra.*
    forma: "{rango} de la {escuadra.nombre} del {escuadra.cuerpo}"
    nota: null si falta alguno.

  fatiga_max:
    fuente: atributos.fis + atributos.men
    tipo: int

  moral_max:
    fuente: atributos.men
    tipo: int

  fza_aportada:
    fuente: tags rol.combate.*
    valores: { rol.combate.heroe: 3, rol.combate.lider: 2, default: 1 }

Cambios post-creación en `tags[]` se registran como hito `agregar_tag` / `quitar_tag` con metadata `{tag}`.

> **Aliados y némesis NO son derivados**. Son colecciones persistidas de primera clase. Ver §3.4.

### 3.2. Slug de tag ≠ slug de personaje

Asimetría deliberada:

- **Slug de tag** (catálogo): legible, lowercase + underscore. Ejemplos: `pistola`, `tirador_preciso`, `ejercito_rojo`. Es la pieza humana de la dot notation. Ver [`tag-modelo.md` §2](tag-modelo.md).
- **Slug de personaje** (`identidad.slug`): patente opaca `^[A-Z0-9]{8}$`. Ejemplo: `K9F2H3M4`. Ver §1.1.

Cuando un tag relacional referencia un personaje (ej. `lealtad.pj.K9F2H3M4`), el segmento final es la patente del personaje, no su nombre. Cuando un tag relacional referencia una entidad del catálogo (ej. `lealtad.faccion.ejercito_rojo`), el segmento final es el slug legible de la entidad. La distinción operativa: tags son metadato curado y se leen; personajes son entidades del juego y se identifican por patente.

### 3.4. Aliados y némesis — colecciones persistidas

Vínculos dirigidos a otros personajes. **No son derivados de tags** — son colecciones de primera clase, como `historial`. Cada entrada lleva ref a la patente del otro personaje + prosa breve sobre el vínculo.

  aliados:
    tipo: list[{ref, descripcion, desde?}]
    default: []
    contenido: Personajes con los que el portador tiene una alianza real y declarable.
    forma:
      ref:         patente [A-Z0-9]{8} del aliado
      descripcion: 1-3 frases sobre cómo se formó el vínculo
      desde:       ISO-8601 opcional

  nemesis:
    tipo: list[{ref, descripcion, desde?}]
    default: []
    contenido: Personajes identificados como rivales individuales.
    nota: Sin restricción de bando — un némesis del propio bando es legal (accidente, traición personal, vieja deuda).
    forma:
      ref:         patente [A-Z0-9]{8} del némesis
      descripcion: 1-3 frases sobre cómo se formó la enemistad
      desde:       ISO-8601 opcional

**Lifecycle**: ambas colecciones empiezan vacías. Se pueblan en caliente durante batalla o narrativa, vía hito `formacion_lealtad` (aliado) / `identificacion_nemesis` (némesis), o por curaduría directa.

**Por qué persistidas y no derivadas**: la relación lleva prosa (descripción del vínculo). Un tag `lealtad.pj.X` solo puede afirmar el vínculo, no contarlo. Las colecciones llevan la textura narrativa que el motor downstream necesita.

**Relación con tags `lealtad.*`**: las lealtades a facciones y escuadras siguen siendo tags (`lealtad.faccion.*`, `lealtad.escuadra.*`) porque son membresías declarativas sin necesidad de prosa. Las lealtades personales (`lealtad.pj.*`) y enemistades personales (`nemesis.pj.*`) **dejan de ser tags** y viven en estas colecciones.

### 3.3. Extensibilidad

El catálogo canon es andamiaje, no jaula. Cualquiera puede crear tag nuevo (`skill.lockpicking`), sub-categoría nueva (`equipo.montura.caballo_criollo`) o categoría nueva entera (`oficio_civil.herrero`) sin migración. El parser solo necesita el primer segmento para enrutar. Detalle en [`tag-modelo.md` §7](tag-modelo.md).

---

## §4 — Historia

Prosa biográfica original.

  tipo: string
  largo: 120-200 palabras
  generacion: LLM al crear el personaje en memoria volátil.
  idioma: Castellano rioplatense, primera persona narrativa.
  inmutable_tras: Canonización (persistir). Se congela como artefacto.

**No-determinismo asumido**: la prosa es no-reproducible aun con seed. No existe semilla que la regenere idéntica — se persiste como artefacto, no como derivado. Por eso el campo `semilla` del schema v0.4.x fue eliminado.

---

## §5 — Historial

Array de hitos. Cada entrada describe un evento temporal sobre el personaje canonizado.

  fecha:       ISO-8601
  tipo:        string         # abierto, ver tipos sugeridos
  descripcion: string
  ref_batalla: slug | null    # slug de batalla externa, opcional
  metadata:    object         # libre

**Tipos sugeridos**: `triple_cero`, `ascenso`, `herida`, `recuperacion`, `agregar_tag`, `quitar_tag`, `traslado`, `condecoracion`, `mejora_atributo`, `cambio_rango`, `cambio_mando`, `cambio_estado`, `cambio_salud`, `cambio_mental`, `asignacion_escuadra`, `identificacion_nemesis`, `formacion_lealtad`, `ruptura_lealtad`.

El enum es **sugerido, no cerrado**. Tipos custom son legítimos; la mitigación es curaduría, no validación. Personajes recién creados arrancan con `historial: []`.

---

## §6 — Metadatos

Campos de auditoría. No mutables por hitos, solo por el motor.

  creado_en:           ISO-8601    # creación en memoria volátil
  canonizado_en:       ISO-8601 | null   # fecha de persistir; null en efímeros
  ultima_actualizacion: ISO-8601    # se actualiza con cada hito

Eliminados respecto a v0.4.x: `modelo_prosa` (no relevante) y `es_canon` (derivable de `canonizado_en != null`).

---

## §7 — Extras

Escape hatch.

  tipo: object | null
  reglas: La API no inspecciona ni valida su contenido.
  proposito: Permite a clientes externos persistir metadatos propios sin romper el schema.

Soporta cualquier llave y estructura anidada. Si un cliente necesita guardar algo que no encaja en tags ni en los bloques canon, va acá.

---

## §8 — Mutabilidad: qué cambia y cómo

  mutables_via_hito:
    - atributos.{fis, tac, men}              # triple_cero | mejora_atributo
    - tags[]                                  # agregar_tag | quitar_tag
    - identidad.rol                           # ascenso | cambio_rol
    - metadatos.ultima_actualizacion          # automático en cada hito

  mutables_sin_hito:
    - identidad.edad                          # decisión narrativa
    - identidad.sobrenombre                   # derivado al servir

  inmutables:
    - identidad.slug
    - identidad.nombre
    - identidad.genero
    - historia
    - metadatos.creado_en
    - metadatos.canonizado_en

  derivados_no_persistidos:
    - filiacion, fatiga_max, moral_max, fza_aportada
    - aliados, nemesis (contenedores)
    - sobrenombre (cuando es derivable)

---

## §9 — Cambios respecto a v0.4.1

Refactor mayor — v0.5.0 (rolling release a partir de ese punto).

  identificador:
    antes: id + origen + semilla
    ahora: identidad.slug único — patente opaca [A-Z0-9]{8} generada al persistir.

  bloque_faccion:
    antes: faccion + filiacion + escuadra + rango + mando + estado (campos separados)
    ahora: Tags faccion.*, escuadra.*, rango.*, mando.capaz, estado.*. Filiacion derivada al servir.

  rol:
    antes: Campo rol aislado.
    ahora: identidad.rol como base narrativa (default "ciudadano"). Roles operativos como tags rol.{oficio,jerarquia,narrativo,mecanico}.*.

  estado_vital:
    antes: enum estado_salud + pools numéricos fatiga_max/actual, moral_max/actual.
    ahora: Tags salud.* y mental.* acumulables. Pools máximos derivados al servir.

  lealtades:
    antes: { primaria, secundarias, secretos }
    ahora: Tags lealtad.faccion.* / lealtad.pj.* / lealtad.escuadra.*. Lealtades secundarias/secretas: sistema aparte TBD.

  vinculos:
    antes: [{tipo, ref, descripcion}]
    ahora: Eliminado. Refs operativas → tags lealtad.* / nemesis.*. Prosa del vínculo → historia o historial.

  tags:
    antes: [{categoria, valor}]
    ahora: Lista plana de strings: <categoria>[.<subcategoria>].<slug>.

  nemesis:
    nuevo: Categoría agregada — enemistad creada en caliente.

  slug:
    antes: lowercase con guiones; ambiguo
    ahora: Patente opaca [A-Z0-9]{8} para personaje. Tags conservan slug legible.

**Mocks**: los 22 fixtures fueron migrados parcialmente en v0.5.0 (modelo intermedio de bloques de tags). **Pendiente**: re-migración al modelo final de lista plana en notación punto + adopción de patentes 8-char en `identidad.slug`.
