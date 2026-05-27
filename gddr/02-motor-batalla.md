---
title: "GDDR-02: Motor de Batalla (Squad vs Squad)"
tags:
  - syv/gddr
  - syv/combate
aliases:
  - GDDR-02
  - Motor de Batalla
  - motor-batalla
---

# GDDR-02: Motor de Batalla (Squad vs Squad)

> [!info] Estado
> En diseño activo — los capítulos se redactan en iteración dirigida con el usuario. El archivo es la única versión viva; no se conserva historial de cambios.

## Contexto
Este documento define las reglas de combate a nivel táctico de [[escuadra-modelo|escuadras]] (squad vs squad) para *Subordinación y Valor*.

Las mecánicas se construyen sobre el vocabulario de [[atributos-y-efectos|atributos y efectos]] del kit, detallando el ciclo de turno, la iniciativa, la resolución de azar y el desgaste.

---

## §1 — Iniciativa

> [!important] Único elemento aleatorio del motor
> La iniciativa es el primer y previsiblemente único elemento aleatorio del motor de batalla. Toda otra resolución del combate procura ser determinística sobre el estado del momento; el azar entra solo al ordenar quién actúa primero dentro de cada empate de iniciativa.

### 1.1. Variables del subsistema

Tres valores volátiles — más una referencia de contexto — describen el estado de iniciativa de una ficha durante un encuentro. Todos viven en `escuadra.miembros[].iniciativa.*` (ver [[escuadra-modelo#2.2.1. `iniciativa` — estado volátil de combate|escuadra-modelo.md §2.2.1]]):

| Variable | Tipo | Rango | Significado |
|---|---|---|---|
| `iniciativa.valor` | `int` | `[0, 5]` (clamped) | Valor de iniciativa calculado por la fórmula de §1.2. Default define directamente la columna. |
| `iniciativa.columna` | `int` | `[0, 5]` | Columna de la grilla en la que se asienta la ficha. Default: `columna ≡ valor`. **Excepción**: ciertos roles aplican overrides de placement (ver §1.4 paso 3b — `lider_de_escuadra` se fuerza a col 0). |
| `iniciativa.orden` | `int` | `[1, n]` | ID asignado al salir de la bolsa; estable durante todo el encuentro. Mayor `orden` → más al frente dentro de su columna. |
| `iniciativa.encuentro` | `str` | `^[A-Z0-9]{8}$` | Patente opaca del encuentro al que pertenecen estos valores (ver §1.7). |

> [!important] Decisión de diseño: la escuadra como hogar del estado volátil
> Todos los valores volátiles de combate viven en `escuadra.miembros[].*`, no en la hoja del personaje. La hoja queda reservada para estado **permanente** (atributos, tags, historial canon, y el estado de salud que sobrevive al encuentro). Lo que es propio de un encuentro vive en el espejo embebido en la escuadra. Esto centraliza las escrituras durante combate y desacopla el ciclo de batalla del ciclo de canonización de personajes.

### 1.2. Entradas que producen `iniciativa.valor`

`iniciativa.valor` no es una propiedad persistida del personaje: se computa al inicio del encuentro a partir de tres insumos declarados.

```
iniciativa.valor = clamp( base + mod_escuadra + mod_acción, 0, 5 )
```

- `base` — iniciativa basal del personaje (u objeto pasible de iniciativa), derivada de sus atributos y tags. Cálculo en [[atributos-y-efectos|atributos-y-efectos.md]].
- `mod_escuadra` — modificador situacional compartido por todas las fichas de la escuadra (ej. `-3` por emboscada, `+1` por ataque coordinado, `0` por despliegue regular).
- `mod_acción` — modificador opcional declarado por la propia ficha (ej. `+1` por ataque a conciencia, `-1` por movimiento cauteloso).

Los tres modificadores se fijan **antes** de extraer la primera ficha y no se renegocian durante el armado.

### 1.3. Modelo conceptual: la bolsa de fichas

Cada personaje activo del encuentro — y cada objeto del escenario pasible de iniciativa propia (vehículo, arma emplazada, ingenio mecánico) — aporta exactamente una ficha al **pool de iniciativa**. El pool se imagina como una bolsa opaca: las fichas se extraen una por una y en ciego.

> [!tip] Por qué una bolsa
> La extracción aleatoria sirve un único propósito: dirimir empates entre fichas que terminan en la misma `columna`. El orden de extracción es la fuente del desempate, y el desempate **favorece a la ficha extraída más tarde** (ver §1.4 paso 3c).

El patrón estructural por columna es un **stack** (LIFO): cada nueva ficha en una columna se apila al frente y actúa antes que las que ya estaban.

### 1.4. Procedimiento de armado de la grilla

Antes del primer turno del encuentro:

1. **Declaración de modificadores y patente**. Cada escuadra fija su `mod_escuadra`. Cualquier ficha que vaya a usar `mod_acción` lo declara ahora. El motor genera una patente de encuentro `^[A-Z0-9]{8}$` (ver §1.7) que se escribirá en `iniciativa.encuentro` de cada ficha.
2. **Conformación de la bolsa**. Se vuelcan al pool una ficha por personaje activo de cada escuadra, más las fichas de objetos con iniciativa propia. En el caso canon (11 vs 11), la bolsa contiene 22 fichas.
3. **Extracción ficha por ficha**. Las extracciones se numeran `orden = 1, 2, …, n` por orden de salida. Para cada extracción:
   - **a.** Se calcula `valor = clamp(base + mod_escuadra + mod_acción, 0, 5)`.
   - **b.** Override por rol — **regla del sargento**: si la ficha tiene `rango.lider_de_escuadra`, su `columna` se fuerza a `0` independientemente de `valor`. El `valor` calculado se conserva en el registro como dato auditable, pero el placement va a col 0. Para cualquier otro rol, `columna ← valor`.
   - **c.** Se escribe el bloque completo `{ encuentro, valor, columna, orden }` en `escuadra.miembros[ref=…].iniciativa`. Mayor `orden` dentro de la columna implica posición más al frente (apilamiento LIFO).
4. **Fin del armado**. La extracción termina cuando la bolsa queda vacía. La grilla resultante queda fija para todo el encuentro.

> [!note] Por qué la regla del sargento
> El `lider_de_escuadra` es la única ficha que **siempre actúa en col 0**, independiente de su `base` o de los modificadores. Narrativamente, el sargento se reserva para leer el campo y dictar reacciones hacia el final del turno; mecánicamente, queda asociado a la "regla 1" del sistema de objetivos (§2.2): col 0 → enemigo al azar. La regla aplica **solo a `lider_de_escuadra`** — el `segundo_al_mando` sigue las reglas normales de placement.

> [!note] Persistencia entre turnos
> A priori, el siguiente turno sigue el mismo orden. La grilla armada queda vigente turno tras turno y no se re-arma por defecto.

### 1.5. Lectura de la grilla (orden de actuación)

La grilla se procesa con dos criterios concatenados:

1. **Primer criterio: `columna` descendente**. Las columnas se procesan en orden 5 → 4 → 3 → 2 → 1 → 0. Una columna vacía se salta sin consumir turno.
2. **Segundo criterio: `orden` descendente dentro de la columna**. Dentro de cada columna, las fichas se procesan por `iniciativa.orden` de mayor a menor.

Tres formas equivalentes de leer el segundo criterio:

- *Narrativa*: "la última en salir de la bolsa actúa primero".
- *Estructural*: "frente de la columna primero" (stack LIFO; el último apilado, arriba).
- *Sobre el dato*: "mayor `iniciativa.orden` primero" — ordenamiento directo sobre el registro.

Pseudocódigo de actuación:

```
for col in [5, 4, 3, 2, 1, 0]:
    for ficha in (miembros con iniciativa.columna == col) sorted by iniciativa.orden DESC:
        actuar(ficha)
```

### 1.6. Ejemplo — Emboscada en el Sector 12,15

> [!example] Escenario
> Los **Cazadores de Ricardo** (Confederados, 11 miembros — `mock/escuadras/confederacion/cazadores_de_ricardo.yaml`) son emboscados por la **Columna Mansilla** (Ejército Rojo, 11 miembros — `mock/escuadras/ejercito_rojo/columna_mansilla.yaml`) en el Sector 12,15. La bolsa contiene 22 fichas.

**Patente del encuentro**: el motor genera `K9F4M2P1` (ver §1.7). Se escribirá en `iniciativa.encuentro` de cada uno de los 22 miembros al asentar sus valores.

**Modificadores declarados al inicio**:
- Cazadores de Ricardo: `mod_escuadra = -3` (emboscados, sin línea de visión previa).
- Columna Mansilla: `mod_escuadra = 0` (atacan desde despliegue regular).
- Ninguna ficha declara `mod_acción` individual (`mod_acción = 0` para las 22).

**Aspectos declarados al inicio del encuentro**:
- **Quiroga** (Cazadores de Ricardo, `rango.tirador_designado` — en la Confederación, "Tirador Selecto"): `aspectos: ["oculto al acecho"]`. Al emerger, su rango le habilita la variante de selección invertida (ver §2.4.1).
- **Antinao** (Columna Mansilla, `rango.tirador_designado` — en el Ejército Rojo, "Cazador"): `aspectos: ["oculto al acecho"]`. Mismo rango, misma variante invertida al emerger.

> [!note] Nota terminológica
> `rango.tirador_designado` es el rango canónico del **tirador asignado de la escuadra**: un fusilero al que se le entregó un rifle con mira de precisión. Su **iniciativa basal es la misma que la de un fusilero regular** — no es un sniper de élite, es infantería con armamento mejorado. Llamado "**Tirador Selecto**" en la Confederación y "**Cazador**" en el Ejército Rojo (etiquetas culturales del mismo rango canónico). La coincidencia con el nombre de la escuadra "**Cazadores de Ricardo**" (Confederados) es nominal — la escuadra es la unidad táctica, el rango es la especialización del miembro.
>
> El **francotirador de élite** (`rango.francotirador`, clase aparte) existe en el universo del juego pero **queda fuera del MVP**: típicamente integra escuadras de reconocimiento de 2 a 4 efectivos, que no se modelan en esta versión. Cuando se incorporen, el aspecto `oculto al acecho` podrá aplicarles bajo la misma mecánica.

El efecto mecánico de `oculto al acecho` — sobre la actuación, sobre la visibilidad de la ficha y sobre la selección de objetivos — se documenta en [[#§2 — El Sistema de Columnas y la Marca de Objetivos|§2]]. La grilla que se arma en este §1.6 representa el estado inicial del encuentro, antes de que ningún aspecto se consuma o despliegue su efecto.

**Iniciativa base por ficha**:

| Ficha | Rol | Bando | `base` |
|---|---|---|---|
| Aguirre | lider_de_escuadra (sargento) | Cazadores de Ricardo | 4 |
| Sosa | segundo_al_mando | Cazadores de Ricardo | 3 |
| Quiroga | tirador_designado | Cazadores de Ricardo | 4 |
| Funes | artillero | Cazadores de Ricardo | 2 |
| Rodríguez | fusilero | Cazadores de Ricardo | 3 |
| Olivares | fusilero | Cazadores de Ricardo | 4 |
| Acosta | fusilero | Cazadores de Ricardo | 2 |
| Pereyra | fusilero | Cazadores de Ricardo | 3 |
| Méndez | recluta | Cazadores de Ricardo | 2 |
| Lugones | recluta | Cazadores de Ricardo | 1 *(tirada baja)* |
| Ramírez | recluta | Cazadores de Ricardo | 1 *(tirada baja)* |
| Mansilla | lider_de_escuadra (sargento) | Columna Mansilla | 5 |
| Iturra | segundo_al_mando | Columna Mansilla | 4 |
| Antinao | tirador_designado | Columna Mansilla | 4 |
| Calfucurá | artillero | Columna Mansilla | 3 |
| Cárcamo | fusilero | Columna Mansilla | 3 |
| Painé | fusilero | Columna Mansilla | 4 |
| Soriano | fusilero | Columna Mansilla | 3 |
| Belenchini | fusilero | Columna Mansilla | 2 |
| Bordón | recluta | Columna Mansilla | 2 |
| Maturana | recluta | Columna Mansilla | 0 *(pifia)* |
| Bordagaray | recluta | Columna Mansilla | 2 |

**Primeras seis extracciones** (alcanzan para fijar el patrón, incluyendo el override del sargento; las 16 restantes aplican la misma mecánica):

| `orden` | Ficha | Bando | `base` | `mod_esc` | `valor` → `columna` | Acción sobre la grilla |
|---|---|---|---|---|---|---|
| 1 | Rodríguez | Cazadores | 3 | -3 | 0 → col 0 | col 0: `[Rodríguez(1)]` |
| 2 | Mansilla | Mansilla | 5 | 0 | 5 → **col 0** *(sargento override)* | col 0: `[Mansilla(2), Rodríguez(1)]` |
| 3 | Lugones | Cazadores | 1 | -3 | 0 *(clamp)* → col 0 | col 0: `[Lugones(3), Mansilla(2), Rodríguez(1)]` |
| 4 | Antinao | Mansilla | 4 | 0 | 4 → col 4 | col 4: `[Antinao(4)]` |
| 5 | Aguirre | Cazadores | 4 | -3 | 1 → **col 0** *(sargento override)* | col 0: `[Aguirre(5), Lugones(3), Mansilla(2), Rodríguez(1)]` |
| 6 | Calfucurá | Mansilla | 3 | 0 | 3 → col 3 | col 3: `[Calfucurá(6)]` |

**Grilla resultante tras las 22 extracciones** (una de las permutaciones posibles del sorteo; cada ficha lleva entre paréntesis su `iniciativa.orden`):

```
col 5 ──┐  (vacía)
col 4 ──┤  Painé(18) → Iturra(10) → Antinao(4)
col 3 ──┤  Soriano(17) → Cárcamo(14) → Calfucurá(6)
col 2 ──┤  Bordagaray(21) → Bordón(15) → Belenchini(11)
col 1 ──┤  Olivares(12) → Quiroga(8)
col 0 ──┘  Ramírez(22) → Méndez(20) → Maturana(19) → Acosta(16) → Funes(13) → Pereyra(9) → Sosa(7) → Aguirre(5) → Lugones(3) → Mansilla(2) → Rodríguez(1)
            ▲                                                                                                                                            ▲
            └─ frente: mayor `orden` actúa primero                                                                                                       └─ fondo: menor `orden`
```

**Lectura A — "la última extraída actúa primero" (narrativa, sorteo)**:

Procesar columnas 5 → 0; dentro de cada columna, en orden inverso al de extracción de la bolsa.

**Lectura B — "mayor `orden` primero" (data, ordenamiento sobre el registro)**:

```sql
ORDER BY iniciativa.columna DESC, iniciativa.orden DESC
```

Ambas lecturas dan exactamente la misma secuencia de actuación:

1. Painé  •  2. Iturra  •  3. Antinao  •  4. Soriano  •  5. Cárcamo  •  6. Calfucurá  •  7. Bordagaray  •  8. Bordón  •  9. Belenchini  •  10. Olivares  •  11. Quiroga  •  12. Ramírez  •  13. Méndez  •  14. Maturana  •  15. Acosta  •  16. Funes  •  17. Pereyra  •  18. Sosa  •  19. Aguirre  •  20. Lugones  •  21. Mansilla  •  22. Rodríguez

> [!warning] Consecuencia táctica de la emboscada + regla del sargento
> Con la regla del sargento (§1.4 paso 3b), **ambos `lider_de_escuadra` aterrizan en col 0**: Mansilla (su `valor 5` la habría llevado a col 5) y Aguirre (su `valor 1` la habría puesto en col 1). Los dos quedan apilados al fondo del turno entre colimbas y pifias. Como Mansilla era la única ficha con `valor 5` y el override la baja, **col 5 queda completamente vacía** — el motor la salta sin consumir turno. La grilla efectiva arranca en col 4. Con Antinao oculto en col 4 (junto a Painé e Iturra) y Quiroga oculta en col 1 (junto a Olivares), las primeras nueve fichas que **realmente actúan** son ocho Mansilla (Painé, Iturra, Soriano, Cárcamo, Calfucurá, Bordagaray, Bordón, Belenchini) y un Cazador — Olivares, el único con `columna > 0` visible. El `-3` aplasta y la regla del sargento descabeza: la línea de mando confederada se mueve al caos del col 0.

> [!note] Sobre las once fichas de col 0
> Once fichas terminan en col 0:
> - **Ocho Cazadores** arrastrados por el `-3` (todas las `base ≤ 3` aterrizan ahí, incluyendo Lugones y Ramírez con tirada baja `base = 1`).
> - **Maturana**, colimba mansillera, por pifia (`base = 0`).
> - Los dos **`lider_de_escuadra`** — **Mansilla** y **Aguirre** — por la regla del sargento (§1.4 paso 3b), independientemente de su `valor` calculado.
>
> El orden interno entre esas once lo decide exclusivamente el azar de extracción: la última en salir (mayor `iniciativa.orden`) actúa primero. Es la única veta real de aleatoriedad en el armado. Como ambos sargentos terminan con `orden` bajos (Mansilla 2, Aguirre 5), actúan casi al final del turno y se dirigen con regla 1 del §2 (col 0 → enemigo al azar).

### 1.7. Encuentro: patente opaca, entidad implícita

El **encuentro** es la unidad temporal de combate a la que pertenecen los valores de `iniciativa.*`. En este kit no se modela como entidad propia (no hay endpoint `/encuentros/{patente}`, no hay tabla de encuentros): solo se reconoce su existencia mediante una patente opaca.

| Atributo | Valor |
|---|---|
| Formato | `^[A-Z0-9]{8}$` (mismo formato que la patente de personaje). |
| Generación | El motor de batalla downstream genera la patente. El kit ofrece un helper [[API#`GET /meta/encuentro/new`\|`GET /meta/encuentro/new`]] que devuelve una patente nueva con check de unicidad contra las ya vistas en `escuadra.miembros[].iniciativa.encuentro`. |
| Persistencia | No se guarda como entidad. Solo aparece embebida en `escuadra.miembros[].iniciativa.encuentro` y, opcionalmente, en `escuadra.historial[].ref_batalla` (que admite la misma patente) o en `escuadra.historial[].metadata`. |
| Lifecycle | Al iniciar un nuevo encuentro sobre la misma escuadra se sobreescribe `iniciativa` completo en cada miembro. A priori, dentro de un mismo encuentro el orden de la grilla se conserva turno tras turno. |

> [!note] Por qué no modelarlo como entidad
> Este kit es de **creación y curaduría** de personajes y escuadras. La temporalidad del combate (encuentros, rondas, turnos) la maneja el motor de batalla downstream. Acá solo dejamos el gancho: una patente referenciable, suficiente para que la escuadra escriba historial coherente sin requerir un schema de combate completo en el kit.

---

## §2 — El Sistema de Columnas y la Marca de Objetivos

Con la grilla de iniciativa armada (§1), cada ficha que activa su turno debe resolver una pregunta: **¿a quién ataca?** Las reglas son sencillas y se chequean en orden estricto.

### 2.1. Definiciones direccionales sobre la grilla

Tomamos como referencia el diagrama horizontal de columnas (col 5 a la izquierda, col 0 a la derecha; dentro de cada columna, frente a la izquierda y fondo a la derecha — ver [[#1.5. Lectura de la grilla (orden de actuación)|§1.5]]).

- **A la izquierda de una ficha**: cualquier enemigo en una columna mayor, **o** en la misma columna con `iniciativa.orden` mayor.
- **A la derecha de una ficha**: cualquier enemigo en una columna menor, **o** en la misma columna con `iniciativa.orden` menor.

La dirección coincide con la secuencia de actuación: **izquierda = actúa antes**, **derecha = actúa después**.

### 2.2. Reglas base de selección de objetivo

Cuando una ficha ejecuta su turno, el motor evalúa estas reglas en orden — la primera que aplica resuelve el objetivo:

1. **`iniciativa.columna == 0` → enemigo al azar**. La ficha actúa caóticamente; ataca a un enemigo cualquiera entre los supervivientes visibles, sin importar lado.
2. **Hay enemigos visibles a la izquierda → el más cercano hacia la izquierda**. La ficha apunta a la **columna más alta posible**; dentro de esa columna, al de `iniciativa.orden` más alto. Mientras quede algún enemigo a la izquierda, la derecha no se evalúa.
3. **`iniciativa.columna == 1` y left limpio → enemigo al azar a la derecha**. La ficha ataca a un enemigo cualquiera entre los visibles a la derecha.
4. **Resto: enemigo más cercano hacia la derecha**. Columna más alta entre las inferiores; dentro de esa columna, mayor `orden`.

> [!tip] La forma sintética del criterio
> "Ataca al enemigo de la columna más alta que puedas; dentro de esa columna, al de `iniciativa.orden` más grande." Las reglas 1 y 3 inyectan caos en col 0 y col 1, pero el resto del campo opera por este criterio.

### 2.3. Invariantes operativas

- **Left tiene prioridad sobre right**: para considerar la derecha, la izquierda debe quedar sin enemigos visibles.
- **Columna más alta, siempre preferida** en cualquier dirección.
- **Re-evaluación en cada oportunidad**: el cómputo de "quién está a la izquierda/derecha, vivo y visible" se rehace al momento de cada ataque. El motor no cachea la elección de blanco — ciertos aspectos pueden alterar el estado del campo entre cálculos (un aliado puede haber caído, una ficha oculta puede haber emergido, etc.).
- **Visible ≠ vivo**: un aspecto como `oculto al acecho` (§2.4.1) hace a una ficha invisible al cómputo de enemigos sin matarla; la ficha sigue ocupando su `iniciativa.columna` y `iniciativa.orden` en la grilla.

### 2.4. Aspectos como mecanismo de modulación de las reglas

Los **aspectos del miembro** (`escuadra.miembros[].aspectos[]` — ver [[escuadra-modelo#2.2. Miembros|escuadra-modelo.md §2.2]]) son el canal principal por el que las reglas base de §1 y §2.2 se modulan en el campo.

El campo `aspectos[]` admite tanto **frases narrativas libres** (ej. `"veterano del 12,15"`, `"cojea por herida vieja"`) como **strings canon** con mecánica reconocida por el motor. Las primeras son material para color y resoluciones puntuales narrativas; las segundas alteran las reglas formales del combate. Este capítulo formaliza el primer aspecto canon — más se irán documentando a medida que se vayan definiendo.

Un aspecto canon puede operar sobre uno o más de estos ejes:

- **Secuencia de actuación** (§1): cuándo actúa la ficha — postergándose, repitiendo, o saltando turnos.
- **Visibilidad / targetabilidad**: la ficha figura o no como enemigo para los cómputos de objetivo del resto del campo.
- **Criterio de selección**: invertir, reordenar o restringir el árbol de decisión de §2.2 para la ficha que porta el aspecto.

#### 2.4.1. Aspecto: `oculto al acecho`

Aspecto canon pensado para fichas **especializadas en disparo de precisión y emboscada**. Su perfil natural en el kit del MVP es `rango.tirador_designado` — el tirador asignado de la escuadra (un fusilero al que se le entregó un rifle con mira de precisión). En la **Confederación** se lo llama "**Tirador Selecto**"; en el **Ejército Rojo**, "**Cazador**" — distintas etiquetas culturales para el mismo rango canónico.

**No aplica** a `lider_de_escuadra` (sargento), `segundo_al_mando`, `artillero`, ni a `fusilero` o `recluta` regulares — el motor rechaza la declaración para esos roles. `rango.apuntador` tampoco califica: el apuntador del kit es el rol de soporte del FAP (ver [[escuadra-modelo#§4 — Plantilla de Validación (Infantería)|escuadra-modelo.md §4]]), no un tirador stealth.

> [!note] Fuera del MVP
> El **francotirador de élite** (`rango.francotirador`, clase aparte) podrá portar el aspecto bajo la misma mecánica, pero **queda fuera del MVP**: típicamente integra escuadras de reconocimiento de 2 a 4 efectivos, que no se modelan en esta versión.

**Efecto sobre la actuación** (eje 1 + eje 2):
- Mientras la ficha conserva el aspecto es **intarjeteable**: no figura como enemigo para el cómputo de objetivos del resto del campo (§2.3).
- Cuando llega su `iniciativa.orden` en la secuencia, **no actúa**: se mantiene oculta. La secuencia continúa con la siguiente ficha.

**Condiciones de emergencia**: el motor reevalúa, al cierre de cada actuación intermedia y al cierre del turno, si la ficha cumple **simultáneamente**:

1. **No tiene enemigos visibles a su izquierda** (ningún superviviente en columnas superiores ni con `orden` mayor en su misma columna).
2. **No tiene enemigos a su derecha con acciones pendientes** (todos los enemigos en columnas inferiores o con `orden` menor en su misma columna ya actuaron o fueron eliminados).

Si ambas condiciones se cumplen, el aspecto se consume (`aspectos[]` pierde la entrada `"oculto al acecho"`) y la ficha ejecuta su ataque siguiendo las reglas de §2.2. Si nunca se cumplen, la ficha **persiste oculta a través de los turnos** — `oculto al acecho` no caduca por tiempo.

**Variante por rango** (eje 3): toda ficha con `rango.tirador_designado` que emerja de `oculto al acecho` aplica **criterio de selección invertido**: dentro de la columna elegida, ataca al de `iniciativa.orden` **más bajo** en lugar del más alto. Es la única excepción explícita al criterio "id más grande primero" (§2.2 tip). Como en el MVP el aspecto solo se declara sobre `tirador_designado`, el invertido es de facto el criterio universal de las fichas que portan `oculto al acecho` por ahora.

> [!important] Por qué exponer este aspecto antes que cualquier otro
> `oculto al acecho` ilustra el patrón canon completo: opera simultáneamente sobre los tres ejes de modulación (secuencia, visibilidad, criterio). Cualquier futuro aspecto que altere la grilla operará sobre alguna combinación de estos tres ejes, y se documentará bajo el mismo molde de "efecto + condiciones de activación + variantes por rango".

### 2.5. Ejemplo aplicado — Emboscada en el Sector 12,15 (continuación de §1.6)

Sobre la grilla armada en §1.6 aplican tres mecánicas no triviales:

- **Antinao** (Columna Mansilla, `rango.tirador_designado` / "Cazador", col 4, orden 4) — `oculto al acecho` activo; variante invertida al emerger.
- **Quiroga** (Cazadores de Ricardo, `rango.tirador_designado` / "Tirador Selecto", col 1, orden 8) — `oculto al acecho` activo; variante invertida al emerger.
- **Mansilla** y **Aguirre** (ambos `lider_de_escuadra`) — col 0 por regla del sargento (§1.4 paso 3b).

**Turno 1 — recorrido cualitativo**:

**Apertura (pos 1)**: Painé (col 4 Mansilla, primera ficha activa de la grilla — col 5 vacía) aplica regla 4. Quiroga, oculta en col 1, no figura. El Cazador visible de columna más alta es **Olivares** (col 1, único Caz con `columna > 0` tras los overrides). Painé ataca a Olivares.

**Iturra (pos 2)**: aplica regla 4. Sin enemigos a la izquierda (col 4 mismo orden mayor = Painé aliada; col 5 vacía). Olivares ya cayó. La columna más alta con Cazadores visibles es col 0 — DESC por `orden`, el primero es **Ramírez(22)**. Iturra ataca a Ramírez.

**Antinao (pos 3, oculto)**: le toca pero `oculto al acecho` activo. Condiciones de emergencia: (a) no tiene enemigos visibles a la izquierda (col 5 vacía, col 4 mismo orden mayor son aliadas Painé e Iturra) → ✓. (b) Tiene muchos enemigos pendientes a la derecha — toda col 0 con Cazadores aún por procesarse — → ✘. Antinao **persiste oculto**.

**Barrida col 3 + col 2 (pos 4–9)**: cada Mansilla aplica regla 4 sobre col 0, atravesando los Cazadores en orden DESC. **Soriano → Méndez(20)**. **Cárcamo → Acosta(16)** (Maturana(19) es Mansilla, se salta). **Calfucurá → Funes(13)**. **Bordagaray → Pereyra(9)**. **Bordón → Sosa(7)**. **Belenchini → Aguirre(5)** — el sargento confederado cae bajo el override sin haber actuado.

**Olivares y Quiroga en col 1 (pos 10–11)**: Olivares ya cayó en pos 1, se salta. Quiroga le toca; aplica condiciones — toda la línea Mansilla en cols 4, 3, 2 sigue intacta, condición (a) ✘. Quiroga **persiste oculta**.

**Cierre de col 0 (pos 12–22)**: los Cazadores ya caídos se saltan al llegar a sus posiciones. La única ficha mansillera viva con turno en col 0 es **Maturana** (pos 14, regla 1 → random); le quedan dos Cazadores visibles (Lugones, Rodríguez) y dispara al azar — digamos a **Lugones**. Más tarde **Mansilla** (pos 21, sargento mansillero col 0, regla 1 → random) tiene un único blanco visible — Rodríguez — y lo elimina.

**Cierre del turno** — el motor evalúa condiciones de emergencia:

- **Antinao** (col 4): condición (a) "sin enemigos visibles a la izquierda" — vacuamente cierta (col 5 vacía; col 4 mismo `orden` mayor son aliadas) → ✓. Condición (b) "sin enemigos pendientes a la derecha" — turno cerrado → ✓. → **Emerge** y consume el aspecto. Busca blanco por regla 4 con criterio **invertido** (variante tirador_designado). El único Cazador vivo es Quiroga — oculta, intarjeteable. **No hay blanco legal — Antinao pasa sin disparar**.
- **Quiroga** (col 1): condición (a) — falla. La línea Mansilla en cols 4, 3 y 2 sigue intacta (Painé, Iturra, Soriano, Cárcamo, Calfucurá, Bordagaray, Bordón, Belenchini). → **No emerge**, entra al turno 2 con el aspecto vigente.

**Estado al cierre del turno 1**:
- **Cazadores vivos**: solo Quiroga (oculta).
- **Mansilla vivos**: los 11 — **cero bajas**. Olivares era el único Cazador con `columna > 0` capaz de disparar, pero cayó por la primera andanada de Painé antes de su propio turno; nadie más del bando emboscado tuvo ocasión de tirar.

**Turnos subsiguientes**: el campo entra en deadlock. Quiroga no puede emerger porque la línea Mansilla está casi intacta; los Mansilla no pueden disparar a Quiroga porque es intarjeteable. Antinao reintentará emerger cada turno, pero sin blanco legal pasa sin disparar.

> [!note] Lectura táctica
> Tres mecánicas concurren para producir el aniquilamiento del bando emboscado:
> 1. **`mod_escuadra = -3`** comprime ocho Cazadores en col 0 desde el armado.
> 2. **Regla del sargento** mete a Aguirre en col 0 — el sargento confederado se hunde junto a sus colimbas y cae sin actuar. Mansilla, también en col 0 por la misma regla, llega a actuar solo porque su `orden = 2` la pone anteúltima y para entonces queda un único blanco vivo.
> 3. **`oculto al acecho` en Quiroga** retira a la única Cazadora con `valor > 0` del cómputo de objetivos: vive pero no contribuye porque su rango requiere izquierda limpia para emerger — y la izquierda es la escuadra Mansilla casi entera.
>
> El bando atacante limpia col 1 (Olivares) en la primera andanada y col 0 en orden DESC durante el resto del turno. Ningún Cazador logra disparar; Antinao emerge sin blanco legal y Quiroga sobrevive intacta sin posibilidad de intervenir.

> [!warning] Resolución de impactos: pendiente
> El traceo asume que cada ataque resuelve en baja del blanco. La mecánica real de daño y resolución de impactos (tiradas, dificultades, defensas) no está documentada todavía. El ejemplo de §2 ilustra **cómo se elige el blanco**, no si el blanco cae.
