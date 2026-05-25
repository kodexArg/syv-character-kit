# API — syv-character-kit

> **Fuente de verdad de endpoints.** Este archivo documenta el contrato HTTP de la API generadora de personajes SyV. Cualquier mención a rutas/endpoints en `PRD.md`, `docs/*`, mocks o código debe consultarse contra este documento. Si una ruta no figura acá, no existe en el contrato.
>
> Idioma: castellano rioplatense. Convenciones de payload: ver [`docs/hoja-modelo.md`](docs/hoja-modelo.md) y [`docs/tag-modelo.md`](docs/tag-modelo.md).

---

## `GET /character`

Genera un personaje efímero. Parámetros opcionales: `faccion`, `rango`, `seed`, `fields`.

Devuelve un `personaje` con `identidad.slug: null` (los efímeros no tienen slug hasta canonizarse), `historial: []`, `metadatos.canonizado_en: null`, y los tags mínimos `estado.disponible` y la asignación de escuadra correspondiente como `escuadra.*`.

Mapea: UC-01..04, UC-06, UC-16.

## `GET /character/{slug}`

Devuelve el personaje con `identidad.slug` exacto. 404 si no existe. Acepta `fields=` para podar.

Mapea: UC-05, UC-15, UC-16.

## `GET /character/{slug}/historial`

Devuelve solo `historial[]`. Sin paginación en v1.

Mapea: UC-17.

## `POST /character/{slug}/event`

Registra un hito sobre un canonizado. Body: una entrada de `historial[]`. Apendea, aplica efecto, actualiza timestamp, devuelve ficha actualizada. 409 sobre mocks; 404 sobre efímeros (que aún no tienen slug). Ver OQ #2 sobre gobernanza (PRD §15).

Mapea: UC-10..14, UC-18.

## `GET /roster/mock`

Lista los 22 fixtures con `slug`, `nombre`, `sobrenombre`, y los tags `faccion.*`, `rango.*`, `rol.*` correspondientes. Sin payload completo.

Mapea: UC-08.

## `POST /canonize`

Persiste un personaje generado como canon. Asigna `identidad.slug` (servidor, convención `{apellido}_{nombre}`), congela `historia`, fija `metadatos.canonizado_en`. Idempotente por `(seed, faccion, rango)`.

Mapea: UC-07.

## `GET /meta/factions`

Catálogo de facciones con descriptor de lore corto.

## `GET /meta/rangos`

Catálogo de rangos sugeridos con tabla de stats, `mando` default, `estado` default, rol cultural por facción.

## `GET /meta/skills`

Pool canon de habilidades. Cada entrada: `{ valor, descripcion, rangos_naturales: [], facciones_predominantes: [] }`. Ejemplos canon: `Comandancia`, `Tiro de precisión`, `Primeros auxilios`, `Oratoria`, `Lectura de terreno`, `Coordinación`, `Comisariado`. El endpoint lista el vocab sugerido; valores fuera del canon son válidos.

## `GET /meta/traits`

Pool canon de rasgos de carácter/condición. Cada entrada: `{ valor, descripcion, rangos_comunes: [] }`. Ejemplos canon: `Sangre fría`, `Voz grave`, `Miope`, `Obstinado`, `Objetivo prioritario`, `Hemorragia lenta`. Los traits no llevan polaridad explícita — el motor downstream interpreta su mecánica según contexto.

## `GET /meta/perks`

Pool canon de ventajas mecánicas. Cada entrada: `{ valor, descripcion, efecto_mecanico, rangos_naturales: [] }`. Ejemplos canon: `Voz de mando`, `Recarga rápida`, `Cobertura instintiva`. El efecto mecánico describe el resultado en juego (ej. "MEN favorable en chequeo de mando colectivo").

## `GET /meta/aspectos`

Pool canon de aspectos. Cada entrada: `{ valor, efecto, activa_tag?, rangos_naturales?: [] }`. El campo `efecto` es la **mini-frase** de mecánica embebida (texto libre, en castellano, que el motor downstream interpreta). El campo opcional `activa_tag` indica cuando el efecto del aspecto dispara un tag transitorio (categoría conceptual `estado_temporal`, ej. `berserker`, `pánico`).

Pool semilla (10 aspectos):

| `valor` | `efecto` | `activa_tag` |
|---|---|---|
| `cabrón` | 75% de activar tag `[berserker]` si falla tirada de MENTAL. | `berserker` |
| `ojo-de-halcón` | +1 INICIATIVA en el primer turno de batalla. | — |
| `muy-fuerte` | Repite tiradas de FIS. | — |
| `cobarde` | 50% de activar tag `[pánico]` si recibe fuego sin cobertura. | `pánico` |
| `carismático` | +1 a chequeos MEN de aliados en el mismo hex mientras esté activo. | — |
| `terco` | Repite chequeos MEN al recibir orden de retirada. | — |
| `veloz` | +1 INICIATIVA en todos los turnos. | — |
| `veterano-cicatrizado` | Repite tiradas con tag `cansado` o `exhausto`. | — |
| `devoto` | +1 a chequeos morales si el líder de escuadra sigue vivo. | — |
| `impredecible` | Primera tirada de cada batalla es aleatoriamente favorable o desfavorable (50/50). | — |

El campo `efecto` es **string libre** (consistente con `perk.efecto_mecanico`). Si el motor downstream necesita estructurarlo (trigger / probabilidad / efecto / tag activado) en parsing rígido, se introduce en una ola futura. Valores fuera del pool semilla son válidos pero requieren entry curada manualmente — el generador no los emite.

## `GET /meta/rasgos`

Vocabulario sugerido de rasgos físicos (`categoria: rasgo`). Entries: `{ valor, tipo: "altura"|"complexion"|"rasgo_fisico"|"cicatriz", facciones_comunes: [] }`. Facilita coherencia entre generador y herramientas externas sin forzar enums cerrados.

## `GET /meta/tag_categories`

Las seis categorías canon con descripción y política de uso. Respuesta tipo:
```json
[
  { "categoria": "rasgo",            "descripcion": "Atributos visuales del cuerpo. Altura, complexión, rasgos físicos, cicatrices." },
  { "categoria": "rol",              "descripcion": "Etiquetas mecánicas del rol vigente. lider, heroe, tirador, etc." },
  { "categoria": "skill",            "descripcion": "Habilidades aprendidas o entrenadas." },
  { "categoria": "trait",            "descripcion": "Rasgos de carácter o condición, sin polaridad fija." },
  { "categoria": "perk",             "descripcion": "Ventajas mecánicas activables del reglamento canónico del juego." },
  { "categoria": "aspecto",          "descripcion": "Mini-tag identitario con efecto mecánico embebido en mini-frase. Pool semilla en /meta/aspectos." },
  { "categoria": "equipo.arma",      "descripcion": "Arma de fuego. Catálogo de 6 genéricos: pistola, revolver, rifle, rifle militar, SMG, ametralladora." },
  { "categoria": "equipo.utilitario","descripcion": "Consumible o accesorio táctico (sin identidad de facción)." },
  { "categoria": "equipo.vestidura", "descripcion": "Identidad visual de facción. Catálogo: uniforme confederado, uniforme rojo, ropa de civil, camuflaje básico." }
]
```
Abierto — futuras categorías se agregan sin breaking change.

## `GET /meta/equipo/vestiduras`

Devuelve el catálogo canon de vestiduras. Ej:
```
[
  { "valor": "uniforme confederado", "faccion": "Confederación" },
  { "valor": "uniforme rojo",        "faccion": "Ejército Rojo" },
  { "valor": "ropa de civil" },
  { "valor": "camuflaje básico" }
]
```

## `GET /meta/equipo/armas`

Catálogo sugerido de armas con alcance y facción predominante. Sin validación — el generador lo usa como pool; el cliente puede listarlo para UIs.

## `GET /meta/equipo/utilitarios`

Catálogo sugerido de utilitarios. Mismas semánticas que `/meta/equipo/armas`.

## `GET /meta/hito_types`

Catálogo sugerido de tipos de hito. Incluye el efecto sobre campos vigentes para cada tipo canon (ver tabla PRD §9.5).

## `GET /meta/vinculo_types`

Catálogo sugerido de tipos de vínculo. Abierto.

## `GET /meta/escuadras/{slug}` (potencial, sujeto a necesidad)

Si se introduce un endpoint de escuadras, devolvería `slug`, `nombre`, `cuerpo`, `faccion`, y la composición vigente por query inverso al tag `escuadra.{slug}` en los personajes. Queda **fuera de v1 estricto**.

---

Mapeo conjunto de los `/meta/*`: UC-09.

Para el catálogo canon de los 80 tags semilla devueltos por los endpoints `/meta/*`, ver PRD §9.1 (Catálogo canon).

---

## Deuda técnica v0.5.0

La migración a modelo v0.5.0 (slug canónico) está completa en los endpoints de personaje y canonización. Quedan inconsistencias menores:

- `/meta/traits` debe refinarse más (estructura futura con categorías sub-traits: físicos, psicológicos, de facción)
- `/meta/aspectos` formalización pendiente de efecto parsing rígido (trigger, probabilidad, tag)
- Documentación de 6 categorías semilla vs. ~16 actuales en canon (refactor futuro de secciones `/meta/*` para reflejar esquema actual)

Estos debts se resuelven en iteración futura sin impacto en v1 de API.
