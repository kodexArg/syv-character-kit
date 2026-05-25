# GDDR-01: Flujo Obligatorio de Creación de Personaje

## Estado
En redacción — Paso 1 (Identidad) definido. Pasos siguientes pendientes.

## Contexto
Establecer la secuencia exacta de pasos necesarios para construir un personaje en *Subordinación y Valor*. El flujo sigue el orden de la hoja ([`docs/hoja-modelo.md`](../docs/hoja-modelo.md)): primero `identidad`, después `atributos`, después `tags`, etc.

---

## Paso 1 — Identidad

Se genera el bloque `personaje.identidad` (ver [`hoja-modelo.md §1`](../docs/hoja-modelo.md)). Cinco campos, en este orden:

### 1.1. `genero` — tirada ponderada

Distribución por defecto:

| Resultado    | Peso |
|--------------|-----:|
| masculino    |  45% |
| femenino     |  45% |
| no_binario   |   5% |
| desconocido  |   5% |

**Override por facción**: algunas facciones imponen límites (ej. fuerzas militares históricas restringidas a `masculino`). El límite se aplica re-sorteando hasta caer dentro del set permitido, no sesgando la tabla base.

### 1.2. `edad` — tirada uniforme

Rango por defecto: **12–70 años** (entero, distribución uniforme).

**Override por facción**: las facciones pueden estrechar el rango (ej. ejército regular 18–45). Misma mecánica que en género: se re-sortea hasta caer en el rango permitido.

### 1.3. `nombre` — generador de nombres

Sorteo desde pools de nombres + apellidos. Detalle del generador:

- **Pools**: nombres argentinos y latinoamericanos modernos, separados por género.
- **Composición**: `{nombre} {apellido}`; admite segundo nombre opcional.
- **Selección de pool**: por defecto pool general; clases/facciones pueden imponer pool específico (TBD).
- **Fuente de datos**: ficheros `.txt` curados, ubicación TBD (`mock/names/` candidato).
- **Búsqueda inicial de fuentes**: delegada a agente externo — listas públicas de nombres AR/LATAM modernos.

### 1.4. `sobrenombre` — incluido en el generador

El generador de nombres puede emitir sobrenombre además del nombre. Reglas:

- Probabilidad de tener sobrenombre: TBD.
- Pool de sobrenombres argentinos modernos (apodos comunes: "el Negro", "Chino", "Tincho", etc.).
- Si el generador no emite sobrenombre, el campo queda `null` y el motor lo deriva al servir (regla de [`hoja-modelo.md §1.2`](../docs/hoja-modelo.md)).

### 1.5. `rol` — default

No se sortea. Arranca con valor `"ciudadano"` (default de la hoja). El rol operativo emerge después como tag (`rol.*`).

### 1.6. `slug` — diferido al motor

No se genera en este paso. El servidor asigna patente `^[A-Z0-9]{8}$` al persistir (canonización). En memoria volátil el campo queda `null`.

---

## Paso 2 — Atributos
*(Pendiente)*

## Paso 3 — Tags
*(Pendiente)*

## Paso 4 — Historia
*(Pendiente)*
