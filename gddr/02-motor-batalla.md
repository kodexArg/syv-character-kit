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
| `iniciativa.valor` | `int` | `[0, 5]` (clamped) | Valor final de iniciativa con que la ficha entra a la grilla. Define directamente su columna. |
| `iniciativa.columna` | `int` | `[0, 5]` | Columna de la grilla en la que se asienta la ficha. `columna ≡ valor` post-clamp. |
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
   - **b.** `columna ← valor`. La ficha queda asentada en esa columna.
   - **c.** Se escribe el bloque completo `{ encuentro, valor, columna, orden }` en `escuadra.miembros[ref=…].iniciativa`. Mayor `orden` dentro de la columna implica posición más al frente (apilamiento LIFO).
4. **Fin del armado**. La extracción termina cuando la bolsa queda vacía. La grilla resultante queda fija para todo el encuentro.

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

**Iniciativa base por ficha**:

| Ficha | Rol | Bando | `base` |
|---|---|---|---|
| Aguirre | líder | Cazadores | 4 |
| Sosa | segundo | Cazadores | 3 |
| Quiroga | apuntador | Cazadores | 5 |
| Funes | artillero | Cazadores | 2 |
| Rodríguez | fusilero | Cazadores | 3 |
| Olivares | fusilero | Cazadores | 4 |
| Acosta | fusilero | Cazadores | 2 |
| Pereyra | fusilero | Cazadores | 3 |
| Méndez | recluta | Cazadores | 2 |
| Lugones | recluta | Cazadores | 1 |
| Ramírez | recluta | Cazadores | 1 |
| Mansilla | líder | Columna Mansilla | 5 |
| Iturra | segundo | Columna Mansilla | 4 |
| Antinao | apuntador | Columna Mansilla | 5 |
| Calfucurá | artillero | Columna Mansilla | 3 |
| Cárcamo | fusilero | Columna Mansilla | 3 |
| Painé | fusilero | Columna Mansilla | 4 |
| Soriano | fusilero | Columna Mansilla | 3 |
| Belenchini | fusilero | Columna Mansilla | 2 |
| Bordón | recluta | Columna Mansilla | 2 |
| Maturana | recluta | Columna Mansilla | 1 |
| Bordagaray | recluta | Columna Mansilla | 2 |

**Primeras seis extracciones** (alcanzan para fijar el patrón; las 16 restantes aplican la misma mecánica):

| `orden` | Ficha | Bando | `base` | `mod_esc` | `valor` | Acción sobre la grilla |
|---|---|---|---|---|---|---|
| 1 | Rodríguez | Cazadores | 3 | -3 | 0 | col 0: `[Rodríguez(1)]` |
| 2 | Mansilla | Columna Mansilla | 5 | 0 | 5 | col 5: `[Mansilla(2)]` |
| 3 | Lugones | Cazadores | 1 | -3 | 0 *(clamp)* | col 0: `[Lugones(3), Rodríguez(1)]` — Lugones entra al frente |
| 4 | Antinao | Columna Mansilla | 5 | 0 | 5 | col 5: `[Antinao(4), Mansilla(2)]` — Antinao desplaza a Mansilla |
| 5 | Aguirre | Cazadores | 4 | -3 | 1 | col 1: `[Aguirre(5)]` |
| 6 | Calfucurá | Columna Mansilla | 3 | 0 | 3 | col 3: `[Calfucurá(6)]` |

**Grilla resultante tras las 22 extracciones** (una de las permutaciones posibles del sorteo; cada ficha lleva entre paréntesis su `iniciativa.orden`):

```
col 5 ──┐  Antinao(4) → Mansilla(2)
col 4 ──┤  Painé(18) → Iturra(10)
col 3 ──┤  Soriano(17) → Cárcamo(14) → Calfucurá(6)
col 2 ──┤  Bordagaray(21) → Bordón(15) → Belenchini(11) → Quiroga(8)
col 1 ──┤  Maturana(19) → Olivares(12) → Aguirre(5)
col 0 ──┘  Ramírez(22) → Méndez(20) → Acosta(16) → Funes(13) → Pereyra(9) → Sosa(7) → Lugones(3) → Rodríguez(1)
            ▲                                                                                          ▲
            └─ frente: mayor `orden` actúa primero                                                     └─ fondo: menor `orden`
```

**Lectura A — "la última extraída actúa primero" (narrativa, sorteo)**:

Procesar columnas 5 → 0; dentro de cada columna, en orden inverso al de extracción de la bolsa.

**Lectura B — "mayor `orden` primero" (data, ordenamiento sobre el registro)**:

```sql
ORDER BY iniciativa.columna DESC, iniciativa.orden DESC
```

Ambas lecturas dan exactamente la misma secuencia de actuación:

1. Antinao  •  2. Mansilla  •  3. Painé  •  4. Iturra  •  5. Soriano  •  6. Cárcamo  •  7. Calfucurá  •  8. Bordagaray  •  9. Bordón  •  10. Belenchini  •  11. Quiroga  •  12. Maturana  •  13. Olivares  •  14. Aguirre  •  15. Ramírez  •  16. Méndez  •  17. Acosta  •  18. Funes  •  19. Pereyra  •  20. Sosa  •  21. Lugones  •  22. Rodríguez

> [!warning] Consecuencia táctica de la emboscada
> Los once miembros de la Columna Mansilla actúan **todos antes** que cualquier Cazador, salvo Quiroga (que cae a col 2 tras la penalización) y los dos Cazadores que quedan en col 1. La mitad superior de la grilla queda íntegra para el bando atacante. El `-3` no solo retrasa: aplasta la grilla del bando emboscado contra el suelo, y ocho Cazadores se apilan en col 0 sin posibilidad real de adelantarse.

> [!note] Sobre el azar dentro de col 0
> Ocho fichas Cazador colapsan en col 0 (todas las `base ≤ 3` aterrizan ahí por el `-3`, sumadas a las dos `base = 1` que ya iban negativas). El orden interno entre esas ocho lo decide exclusivamente el azar de extracción: la última en salir (mayor `iniciativa.orden`) actúa primero. Es la única veta real de aleatoriedad en el armado.

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
