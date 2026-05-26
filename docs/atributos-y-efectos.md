# Atributos y Estadísticas Calculadas

Catálogo oficial de variables que pueden ser afectadas por `efecto` en tags (típicamente `trait.*`, `perk.*`, `efecto.*`) y la mecánica de cada una en *Subordinación y Valor* (SyV).

---

## 1. Atributos Base (Persistidos)

Únicas magnitudes numéricas de capacidad persistidas en la hoja (ver [`hoja-modelo.md §2`](hoja-modelo.md)).

- **FISICO** (`fis`): Fuerza, potencia muscular, resistencia orgánica. Rango: 2..5 (tope absoluto; creación máx 4; 5 solo vía hito `triple_cero` o `mejora_atributo`).
- **TACTICO** (`tac`): Coordinación, puntería, reflejos, destreza técnica. Rango: 2..6 (creación máx 5; 6 solo vía hito).
- **MENTAL** (`men`): Fortaleza psicológica, resistencia al estrés, moral base, liderazgo. Rango: 2..7 (creación máx 6; 7 solo vía hito).

Las `skill.*` son **disparadores binarios** de tirada contra `atributo_dominante`, no bonificadores. Ver [`tag-modelo.md §4.6`](tag-modelo.md).

---

## 2. Estadísticas Calculadas (Dinámicas en caliente)

No se persisten en la hoja (evitan drift). El motor las computa al servir, a partir de los atributos base, el estado de salud/mental y los modificadores de los tags activos.

### 2.1. INICIATIVA
Orden de actuación en combate y prioridad de selección de objetivos.

- **Resolución**:
  1. Al inicio del combate cada personaje tira.
  2. Base = iniciativa macro de escuadra ± modificadores de estados y traits.
  3. Cada personaje tira **1d3o1** (un dado de tres observando el dado objetivo) y suma a su base.
  4. Se ubica en la cola con un d10 (posición 1..10).
  5. Empates: aleatorio.
- **Impacto táctico**: iniciativa alta actúa primero pero también es atacada primero; baja mantiene al personaje a resguardo en la retaguardia.

### 2.2. MORAL
Estado de ánimo, voluntad de lucha y cohesión psicológica individual.

- **Resolución**: valor individual por unidad. Eventos críticos (bajas cercanas, fuego pesado) exigen chequeo.
- **Consecuencias**: cada fallo resta 1 punto. La caída progresiva puede llevar a **Desesperación**/**Pánico** (pérdida de control), **Furia** (ataques descontrolados) o **Locura** (inutilización permanente para el combate).

### 2.3. MOVIMIENTO
Velocidad y capacidad de desplazamiento táctico.

- **Cálculo**: producto de **FISICO** y la orden táctica vigente del turno.
- **Escuadra**: la velocidad grupal está limitada por el menor movimiento individual entre miembros activos.

### 2.4. FATIGA
Recurso físico-mental que limita acciones continuas. Principal factor de desgaste.

- **Pool inicial**: **FISICO** + **MENTAL**.
- **Consumo**: cada turno con orden ejecutada, o eventos ambientales/mecánicos.
- **Estados de agotamiento**:
  - Los puntos de **FISICO** se consumen primero. Al agotarse, gana `salud.cansado`.
  - Luego se consumen los de **MENTAL**. Al agotarse, gana `salud.exhausto` y queda inmovilizado.

### 2.5. ESTRESS
Tensión acumulada a corto plazo; previene el colapso mental inmediato.

- **Odómetro** descendente basado en **MENTAL** (valor inicial usual: 3).
- Cada evento estresante resta 1. Al llegar a 0: el personaje recibe un tag mental negativo permanente por lo que resta del combate, y el odómetro se reinicia a su valor original.

---

## 3. Ejemplos en tags

Los traits canon usan este vocabulario en su campo `efecto`. Ver catálogo real en `mock/tags/trait/*.yaml` (formato `"(+1) INICIATIVA"`, `"(-1) FATIGA"`, etc., documentado en [`tag-modelo.md §4.7`](tag-modelo.md)).
