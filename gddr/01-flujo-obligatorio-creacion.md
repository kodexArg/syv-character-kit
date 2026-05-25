# GDDR-01: Flujo Obligatorio de Creación de Personaje

## Estado
En redacción — Fases 1, 2 y 3 definidas. Fase 4 pendiente.

## Contexto
Establecer la secuencia exacta de pasos necesarios para construir un personaje en *Subordinación y Valor*. El flujo **no sigue el orden visual de la hoja**: para que los atributos y los datos personales tengan sentido, la afiliación operativa (rango + facción + subfacción) se decide primero. La hoja describe la estructura del personaje *terminado*; este documento describe cómo se llega ahí.

## Orden de fases

```
Fase 1: Afiliación      → Rango, Facción, Subfacción
Fase 2: Identidad       → Nombre, Sobrenombre, Edad, Género, …
Fase 3: Atributos       → fis, tac, men (derivados de Fase 1)
Fase 4: Resto           → tags adicionales, historia, historial, metadatos
```

Cada fase depende de la anterior y puede imponer restricciones sobre la siguiente vía **tabla de reglas** (ver §Reglas).

---

## Fase 1 — Afiliación

Tres campos, **en este orden**: Rango → Facción → Subfacción. El sistema **solicita** cada uno; si no se provee, lo sortea con la tabla de pesos del campo correspondiente.

### 1.1. Rango

Cada personaje arranca con **exactamente un** tag `rango.*`. Catálogo canon en [`tags/rango/`](../tags/rango/):

- `ciudadano` *(implícito si no se asigna otro — corresponde al `rol: "ciudadano"` default de la hoja; no entra al sorteo)*
- `militante`
- `recluta`
- `fusilero`
- `apuntador`
- `artillero`
- `francotirador`
- `segundo_al_mando`
- `lider_de_escuadra`

**Sorteo ponderado (fallback si no se provee)** — creación de combatiente al azar:

| Rango               | Peso |
|---------------------|-----:|
| `recluta`           |  20% |
| `fusilero`          |  40% |
| `apuntador`         |  12% |
| `artillero`         |  12% |
| `francotirador`     |   5% |
| `segundo_al_mando`  |   7% |
| `lider_de_escuadra` |   3% |
| `militante`         |   1% |

Suma 100%. La curva refleja escasez operativa.

`ciudadano` se asigna explícitamente cuando el caso de uso es NPC civil — no entra al sorteo.

### 1.2. Facción

Cada personaje arranca con **exactamente un** tag `faccion.*`. Catálogo canon en [`tags/faccion/`](../tags/faccion/):

- `confederados`
- `ejercito_rojo`

**Sorteo (fallback)**: uniforme 50/50 por defecto. Override por contexto de campaña.

### 1.3. Subfacción (escuadra)

Cada personaje arranca con **exactamente un** tag `escuadra.*`. Catálogo canon en [`tags/escuadra/`](../tags/escuadra/):

- `mansilla` *(Ejército Rojo)*
- `ricardo` *(Confederados)*

**Sorteo (fallback)**: uniforme entre las escuadras **compatibles con la facción** de §1.2.

### 1.4. Reglas que esta fase puede imponer

Esta fase puede **restringir Género y Edad** de Fase 2 vía la tabla de reglas (ver §Reglas). Ejemplos típicos:

- Facción militar histórica → `genero ∈ {masculino}`.
- `lider_de_escuadra` → `edad ≥ 25`.
- `recluta` → `edad ≤ 22`.

Las reglas concretas son **TBD**.

---

## Fase 2 — Identidad personal

Genera el bloque `personaje.identidad` (ver [`hoja-modelo.md §1`](../docs/hoja-modelo.md)) **respetando las restricciones de Fase 1**.

### 2.1. Género — tirada ponderada

| Resultado    | Peso |
|--------------|-----:|
| masculino    |  45% |
| femenino     |  45% |
| no_binario   |   5% |
| desconocido  |   5% |

Si Fase 1 restringe el set, se re-sortea hasta caer dentro del set permitido (no se sesga la tabla base).

### 2.2. Edad — tirada uniforme

Rango por defecto: **12–70 años** (entero, uniforme). Si Fase 1 estrecha el rango, se re-sortea hasta caer dentro.

### 2.3. Nombre

Sorteo desde pools curados en [`resources/nombres/`](../resources/nombres/):

- `nombres_m.txt` — 25 nombres masculinos argentinos modernos, formato `Nombre|Apodo`.
- `nombres_f.txt` — 25 nombres femeninos argentinos modernos, formato `Nombre|Apodo`.
- `apellidos.txt` — 50 apellidos argentinos (mix hispano + inmigración).

**Composición**: `{nombre} {apellido}`. Selección uniforme dentro del pool del género.

**Implementación de referencia**: [`scripts/sample_name.py`](../scripts/sample_name.py) — función `sample(genero)`.

**Pools alternativos por facción/clase**: TBD. La estructura admite `nombres_m_<faccion>.txt` sin tocar el generador.

### 2.4. Sobrenombre — 50% de probabilidad

Cada nombre del pool trae un apodo asignado (`Francisco|Pancho`, `Ignacio|Nacho`, etc.).

- Probabilidad de emitir sobrenombre: **50%** por personaje.
- Si no se emite, el campo queda `null`; el motor puede derivarlo al servir.
- Apodos curados a mano (no existe dataset estructurado público de apodos rioplatenses).

### 2.5. `rol` — default

No se sortea. Arranca con valor `"ciudadano"` (default narrativo de la hoja). El rol operativo emerge después como tag `rol.*` en Fase 4.

### 2.6. `slug` — diferido al motor

No se genera en este paso. El servidor asigna patente `^[A-Z0-9]{8}$` al persistir. En memoria volátil el campo queda `null`.

---

## Fase 3 — Atributos

**Cero aleatoriedad**. Lookup determinista sobre el tag `rango.*` de Fase 1 (ver [GDDR-03](03-determinismo-atributos-por-rango.md)):

| Rango               | `fis` | `tac` | `men` | Total |
|---------------------|------:|------:|------:|------:|
| `ciudadano`         |   2   |   2   |   2   |  6    |
| `militante`         |   3   |   2   |   3   |  8    |
| `recluta`           |   3   |   2   |   2   |  7    |
| `fusilero`          |   3   |   3   |   3   |  9    |
| `apuntador`         |   3   |   5   |   4   | 12    |
| `artillero`         |   5   |   3   |   3   | 11    |
| `francotirador`     |   3   |   6   |   3   | 12    |
| `segundo_al_mando`  |   3   |   4   |   5   | 12    |
| `lider_de_escuadra` |   3   |   4   |   7   | 14    |

Topes absolutos:
- `fis 5` → solo `artillero`.
- `tac 6` → solo `francotirador`.
- `men 7` → solo `lider_de_escuadra`.

### 3.1. Inmutabilidad práctica

Los atributos quedan **fijos al rango de creación**. Un ascenso posterior cambia el tag `rango.*` pero **no** los atributos: si un cabo asciende a sargento, sus stats no se mueven — el progreso real es el equipo, los perks y los vínculos que junte en el campo. Ver [`hoja-modelo.md §8`](../docs/hoja-modelo.md).

Mutación posible solo vía hito `triple_cero` o `mejora_atributo` (eventos narrativos costosos).

---

## Fase 4 — Resto
*(Pendiente: tags adicionales, historia prosa, historial, metadatos.)*

---

## Reglas — referencia externa

Las restricciones cruzadas entre tags de Fase 1 y campos de Fase 2 (típicamente `genero` y `edad`) viven en la **tabla de reglas del proyecto**, fuera del scope de este GDDR.

El contrato que este flujo asume:

- Existe una tabla consultable que, dado el set de tags decididos en Fase 1, devuelve el set de valores válidos para cada campo restringible de Fase 2.
- El motor consulta la tabla **antes** de sortear cada campo de Fase 2 y aplica el recorte al pool/rango.
- Si la tabla no impone restricción sobre un campo, se usa la distribución por defecto.

Diseño, formato y ubicación de la tabla: ver documento de reglas del proyecto (scope separado).
