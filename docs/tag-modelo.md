# Tag Modelo — Referencia narrativa de tags

> **Versión compatible**: schema v0.4.1 (en proceso de extensión hacia `rol.*` y eliminación
> del campo `personaje.rol`; ver OQ al final).
> **Propósito**: descripción campo por campo de la entidad **tag** como ciudadano de primera
> clase del catálogo (`/meta/*`). Para el template programático listo para copiar,
> ver [`docs/tag-modelo.yaml`](tag-modelo.yaml).
> **Relación con la hoja**: dentro de `personaje.tags[]` un tag aparece reducido a
> `{categoria, valor}`. La definición canónica completa de cada tag — descripción, atributos,
> reglas, refs cruzadas — vive aquí y se sirve por `/meta/{categoria}/{slug}`.

---

## Bloque 1 — Campos comunes a todos los tags

Todos los tags, sin importar su categoría, comparten este núcleo.

**`categoria`** — Familia canónica del tag. Enum abierto con valores canon: `rasgo`, `trait`, `perk`, `aspecto`, `skill`, y las familias jerárquicas `equipo.{arma, utilitario, vestidura}` y `rol.{oficio, jerarquia, narrativo, mecanico}` (esta última pendiente, ver OQ). La categoría determina qué campos específicos aplican además de los comunes.

**`valor`** — Identificador mínimo del tag. 1-2 palabras, 3 cuando el nombre canónico lo requiere (`rifle militar`, `Líder Revolucionario`). Cero prosa, cero paréntesis, cero comas internas. Es la *key* que aparece literal en `personaje.tags[].valor`. Sensible a mayúsculas: `Francotirador` ≠ `francotirador` (PRD §13.2).

**`slug`** — Forma kebab-case lowercase del `valor`, sin acentos ni espacios. Usada en URLs `/meta/{categoria}/{slug}` y como key estable para refs cruzadas. Ej: `valor: "Líder Revolucionario"` → `slug: lider-revolucionario`. Si dos `valor` distintos colapsan al mismo `slug`, hay conflicto de catálogo y el segundo debe renombrarse.

**`descripcion`** — Prosa corta canónica del tag, 1-3 frases. Vive solo aquí; nunca dentro de `personaje.tags[]`. Es lo que un cliente lee para entender qué significa el tag en el lore o en la mecánica.

**`origen`** — Procedencia del tag en el catálogo. Enum: `"canon"` (parte del pool semilla curado en el PRD), `"emergente"` (apareció primero en un personaje generado y luego se promovió al catálogo), `"custom"` (creado por un cliente externo, no validado).

**`metadatos`** — Bloque de auditoría. `version_introducida` (string SemVer del PRD donde entró el tag, ej. `"0.4.1"`). `creado_en` (ISO-8601). `ultima_actualizacion` (ISO-8601).

---

## Bloque 2 — Campos específicos por categoría

Cada categoría agrega campos propios al núcleo común. Lo que no se lista, no aplica.

### `rasgo`
Rasgo físico observable (cicatriz, contextura, color de ojos). Solo campos comunes. Sin mecánica.

### `trait`
Rasgo de carácter o condición sin mecánica activa (`miope`, `taciturno`, `idealista`). Solo campos comunes; la `descripcion` carga el peso narrativo.

### `perk`
Ventaja reglada del manual del juego con efecto numérico.
- **`efecto_reglado`** — string. Frase mecánica con el bonus/penalidad concreta. Ej: `"+1 al test de coordinación cuando lidera la escuadra"`.

### `aspecto`
Mini-tag identitario con efecto mecánico embebido en mini-frase (PRD §6.2). Sub-familia v0.4.0 con semilla canon de 10.
- **`efecto`** — string. Mini-frase con estructura `trigger + [probabilidad] + efecto`. Ej (`cabrón`): `"En combate cuerpo a cuerpo, 50% de activar [berserker] hasta fin del turno"`.
- **`tags_activables`** — array de `slug`. Refs a tags `estado_temporal` que este aspecto puede disparar. Ej: `[berserker]` para `cabrón`, `[panico]` para `cobarde`.

### `skill`
Habilidad aprendida o entrenada (`Comandancia`, `Medicina`, `Ingeniería`, `Comisariado`). Nota: `Tiro de precisión` fue eliminado en esta iteración; `Francotirador` se reclasifica como `rol.oficio` (ver OQ).
- **`atributo_dominante`** — enum `fis | tac | men`. Qué atributo del personaje activa la skill.
- **`rangos_naturales`** — array de strings. Rangos canon donde la skill aparece naturalmente.
- **`facciones_predominantes`** — array de strings. Facciones donde la skill es común.
- **`equipo_sugerido`** — array de `slug`. Refs a tags `equipo.*` que típicamente acompañan a la skill.

### `equipo.arma`
Arma física que el personaje carga.
- **`calibre`** — string. Ej: `"7.65 Mauser"`, `"9mm"`. `null` si no aplica (cuchillo).
- **`tipo_accion`** — enum: `"cerrojo" | "semiauto" | "automatico" | "cuerpo_a_cuerpo"`.
- **`municion_tag_ref`** — `slug` del tag `equipo.utilitario` que representa su munición (ej. `cargador`). `null` si arma blanca.
- **`alcance_narrativo`** — enum: `"corto" | "medio" | "largo"`. Distancia operativa típica.

### `equipo.utilitario`
Objeto utilitario del inventario (`cargador`, `silbato`, `cuaderno`, `brújula`, `botiquín`, `radio`, `mapa`, `cuchillo`, `vendaje`). Repetible: tres `cargador` son tres entidades físicas distintas.
- Solo campos comunes. La `descripcion` indica el uso típico.

### `equipo.vestidura`
Identidad visual del personaje, no protección numérica (PRD §0.3.0). Catálogo cerrado de 4 entradas, una por facción/rol.
- **`faccion_asociada`** — string. Facción a la que pertenece la vestidura.

### `rol.*` — pendiente
Sub-familias propuestas: `rol.oficio` (qué hace en combate: `francotirador`, `artillero`), `rol.jerarquia` (título militar: `sargento`, `cabo`), `rol.narrativo` (cómo lo nombra el lore: `lider_revolucionario`, `comisario`), `rol.mecanico` (preserva derivación de `fza_aportada`: `lider`, `heroe`). **Campos específicos sin definir hasta resolver OQ.**

---

## Bloque 3 — Refs cruzadas y composición

Los tags se referencian entre sí por `slug`, nunca por `valor` literal (el `slug` es estable, el `valor` puede tener variantes de case). Ejemplos:

- Un tag `aspecto` apunta a tags `estado_temporal` vía `tags_activables: [berserker]`.
- Un tag `skill` apunta a tags `equipo.*` vía `equipo_sugerido: [rifle-militar, prismaticos]`.
- Un tag `equipo.arma` apunta a su munición vía `municion_tag_ref: cargador`.

La API no valida que el `slug` referenciado exista. El catálogo se mantiene coherente por curaduría, no por integridad referencial.

---

## Bloque 4 — Persistencia y mock

En MVP los tags viven como archivos YAML individuales en `mock/tags/{categoria}/{slug}.yaml` (estructura tentativa). Cada archivo es la definición canónica de un tag. El endpoint `/meta/{categoria}/{slug}` sirve el contenido del archivo. Al pasar a la base de datos canon, cada tag será una fila con los mismos campos.

Lo que aparece dentro de `personaje.tags[]` es solo `{categoria, valor}` — el cliente que necesita la definición completa hace lookup contra `/meta/*`.

---

## Open Questions

### OQ-tag-1 — Forma de expresión de `rol.*`

El campo `rol` del personaje se elimina; los roles pasan a ser tags. Falta decidir cómo se expresan en `{categoria, valor}`. Tres formas en mesa:

- **Forma 1 — plano**: `categoria: rol, valor: francotirador|sargento|lider_revolucionario`. La sub-organización `rol.*` es solo del catálogo (UI/submenú), no del schema. Mínimo cambio.
- **Forma 2 — jerárquico paralelo a `equipo.*`**: `categoria: rol.{oficio|jerarquia|narrativo|mecanico}, valor: <especifico>`. Mejor para queries (`fza_aportada` busca solo en `rol.mecanico`); más complejidad.
- **Forma 3 — categoría = rol específico**: `categoria: rol.francotirador, valor: ???`. Rompe el modelo `{categoria, valor}` salvo que `valor` tenga semántica nueva (estado, fecha). Descartada salvo motivo concreto.

Voto del autor (claude): Forma 2. Pendiente confirmación del usuario.

### OQ-tag-2 — `slug` derivado vs persistido

¿El `slug` se persiste explícito en el YAML del tag, o se deriva al servir desde `valor`? Persistido evita ambigüedad con acentos y casing; derivado evita desincronización. Cierra parcialmente OQ #11 del PRD principal.

### OQ-tag-3 — `Francotirador` como `rol.oficio`

Una vez resuelta OQ-tag-1 con Forma 2 (o equivalente), `Francotirador` queda registrado como `categoria: rol.oficio, valor: Francotirador`. El tag `skill: Tiro de precisión` se elimina del catálogo.
