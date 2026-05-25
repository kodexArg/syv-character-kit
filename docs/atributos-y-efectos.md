# Atributos y Estadísticas Calculadas

Este documento define el catálogo oficial de variables que pueden ser afectadas por los efectos de los tags (ej. en la categoría `trait.*` o `efecto.*`) y detalla la mecánica matemática y de diseño de juego que rige a cada una de ellas en *Subordinación y Valor* (SyV).

---

## 1. Atributos Base (Persistidos)

Los atributos base son las únicas magnitudes numéricas de capacidad que se persisten de forma fija en la hoja de personaje (ver [`hoja-modelo.md §2`](hoja-modelo.md)).

- **FISICO** (`fis`): Fuerza física, potencia muscular y resistencia del organismo. Rango: 2..5.
- **TACTICO** (`tac`): Coordinación, puntería, reflejos y destreza técnica de combate. Rango: 2..6 (6 exclusivo de `francotirador`).
- **MENTAL** (`men`): Fortaleza psicológica, resistencia al estrés, moral base y capacidad de liderazgo. Rango: 2..7 (7 exclusivo de `lider_de_escuadra`).

### 1.1. Skills como disparador de chequeos

Los tags `skill.*` no modifican atributos — los **chequean**. Cada skill declara `atributo_dominante` (`fis`, `tac` o `men`); cuando el motor necesita resolver una acción técnica, pregunta "¿el personaje tiene la skill X?" y, si la respuesta es sí, tira contra el atributo dominante de esa skill. Sin la skill, la acción no es intentable o se intenta con penalidad fuerte (regla del motor downstream).

Las skills son por tanto **habilitadores binarios** de tirada, no bonificadores. Toda categoría que sí modifica atributos o estadísticas calculadas (`trait`, `perk`, `efecto` standalone) usa el vocabulario de §2 y §3 vía el campo `efecto`. Ver [`tag-modelo.md §3`](tag-modelo.md) y [`tag-modelo.md §4.6`](tag-modelo.md).

---

## 2. Estadísticas Calculadas (Dinámicas en caliente)

Las estadísticas calculadas **no se persisten en la hoja** para evitar la desincronización (drift) de datos. Se computan en tiempo real por el motor de juego en base a los atributos base, el estado actual de salud/mental del personaje y los modificadores provistos por sus tags.

### 2.1. INICIATIVA
Determina el orden de actuación en combate y la prioridad en el sistema de selección de objetivos.

- **Mecánica de resolución**:
  1. Al inicio del combate, cada personaje realiza una tirada.
  2. Se calcula su valor base de Iniciativa sumando/restando la iniciativa macro de la escuadra y aplicando los modificadores de los estados (salud/mental) y traits del personaje.
  3. Cada personaje tira **1d3o1** (un dado de tres observando el dado objetivo, es decir, el dado de resolución del sistema) para sumar a su base.
  4. Los personajes se ubican en la fila de iniciativas utilizando un dado de 10 que indica su posición/turno en la cola de iniciativa (1 a 10).
  5. Los empates en el valor final se resuelven de forma puramente aleatoria.
- **Impacto táctico**: La iniciativa alta hace que actúes primero, pero también te expone: los personajes con iniciativa alta atacan primero y son atacados primero. Por el contrario, una iniciativa baja mantiene al personaje a resguardo en la parte posterior del campo de batalla cuando vuelan las balas.

### 2.2. MORAL
Representa el estado de ánimo, la voluntad de lucha y la cohesión psicológica individual de la unidad.

- **Mecánica de resolución**: Se guarda un valor individual por unidad en combate. Ciertos eventos críticos en la batalla (bajas cercanas, estar bajo fuego pesado) exigen realizar chequeos de **MORAL**.
- **Consecuencias**: Cada chequeo fallido resta un punto de moral al personaje. La pérdida progresiva de moral altera el comportamiento de la unidad, pudiendo conducirla a estados de:
  - **Desesperación** o **Pánico** (pérdida de control).
  - **Furia** (forzando ataques descontrolados).
  - **Locura** (inutilización permanente para el combate).

### 2.3. MOVIMIENTO
La velocidad y capacidad de desplazamiento táctico por el campo de batalla.

- **Mecánica de cálculo**: Es el producto directo del atributo base **FISICO** y de la orden táctica que esté cumpliendo la unidad en ese turno.
- **Movimiento de escuadra**: Para desplazamientos grupales coordinados, la velocidad total de la escuadra está limitada por el menor valor de movimiento individual entre sus miembros activos (la escuadra marcha al ritmo del más lento).

### 2.4. FATIGA
El recurso físico y mental que limita las acciones continuas en combate. Es el gran factor de desgaste de la partida.

- **Mecánica de pool**: Comienza con un total equivalente a la suma de **FISICO** + **MENTAL**.
- **Consumo**: Se consume en cada turno en el que se ejecuta una orden, o debido a eventos ambientales o mecánicos determinados.
- **Estados de agotamiento**:
  - Los puntos de **FISICO** se consumen siempre primero. Al agotarse por completo los puntos aportados por el físico, el personaje gana inmediatamente el tag de estado `salud.cansado`.
  - Una vez agotados los puntos físicos, se comienzan a consumir los puntos aportados por el atributo **MENTAL**. Al agotarse estos, el personaje gana el tag de estado `salud.exhausto` y queda completamente inmovilizado (no puede moverse en lo absoluto).

### 2.5. ESTRESS
Medidor de tensión acumulada a corto plazo que previene el colapso mental inmediato.

- **Mecánica de odómetro**: Funciona como un contador descendente basado en el atributo **MENTAL** (usualmente con un valor inicial de 3).
- **Consumo y reinicio**: Cada vez que ocurre una acción o evento estresante, el odómetro disminuye en 1. Al llegar a cero (0), el personaje sufre un colapso psicológico inmediato:
  - Se le asigna un tag mental negativo permanente por lo que resta de ese combate.
  - El contador de estrés se reinicia inmediatamente a su valor natural original (usualmente 3).

---

## 3. Ejemplos de Interacción en Tags

Muchos tags del catálogo canon modifican tanto la fatiga como el estrés para reflejar el desgaste físico y mental de sus habilidades.

- **Veloz** (`trait.veloz`):
  ```yaml
  efecto:
    - "(+1) INICIATIVA"
    - "(+1) MOVIMIENTO"
    - "(-1) FATIGA"  # Moverse rápido tiene un costo físico mayor
  ```
- **Cobarde** (`trait.cobarde`):
  ```yaml
  efecto:
    - "(-1) MORAL"
    - "(-1) INICIATIVA"
    - "(-1) ESTRESS"  # Menor tolerancia al estrés; el odómetro llega antes a cero
  ```
- **Veterano** (`trait.veterano`):
  ```yaml
  efecto:
    - "(+1) FISICO"
    - "(+1) MORAL"
    - "(+1) ESTRESS"  # Mayor tolerancia al estrés; odómetro inicial más grande
  ```
