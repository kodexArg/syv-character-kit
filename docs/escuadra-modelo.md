---
title: "Escuadra Modelo — Referencia de la entidad Escuadra"
tags:
  - syv/docs/schema
  - syv/escuadra
aliases:
  - Escuadra Modelo
  - Modelo de Escuadra
  - escuadra-modelo
---

# Escuadra Modelo — Referencia de la entidad Escuadra

> [!info] Estado y Propósito
> - **Estado**: rolling release; este documento describe el vigente.
> - **Propósito**: definir la estructura, comportamiento, sistema de puntos, historial y plantillas de validación de la entidad Escuadra.

---

## §1 — Propósito de la Entidad

La **Escuadra** (`escuadra`) es la unidad táctica fundamental en *Subordinación y Valor*. Agrupa a un conjunto de combatientes ([[hoja-modelo|hojas de personaje]]) bajo una sola identidad operativa. Sirve para registrar la hoja de vida de la unidad mediante un historial de hitos, y para controlar y verificar la composición reglamentaria de las escuadras en base a plantillas de validación y un balance en puntos de reclutamiento (ver [[escuadra-modelo.yaml]]).

---

## §2 — Estructura de la Escuadra

Una escuadra consta de un bloque de **identidad**, una lista plana de **miembros** con su posición y costo en puntos, y una colección de **historial** de hitos.

### 2.1. Identidad

- `slug`: PK de la escuadra (lowercase + underscore). Debe tener sentido con la trama del juego. Ejemplos: `cazadores_de_ricardo`, `columna_mansilla`. Coincide exactamente con el segmento final del tag `escuadra.{slug}` en las [[hoja-modelo#§3 — Tags|hojas de los miembros (ver hoja-modelo.md §3)]].
- `nombre`: Nombre legible. Ejemplos: "Cazadores de Ricardo", "Columna Mansilla".
- `faccion`: Slug de la facción macro a la que responde (`confederados` | `ejercito_rojo`).
- `tipo`: Tipo operativo de escuadra que rige las reglas de su plantilla. Para el MVP: `escuadra_de_infanteria`.

### 2.2. Miembros

La composición de miembros contiene la patente, el orden táctico, el costo en puntos, rango y nombre compuesto/de guerra de cada personaje (ver [[hoja-modelo]]):

```yaml
miembros:
  - ref:            WA3K9F2H    # [[hoja-modelo#1.1. slug — la patente del personaje|patente opaca [A-Z0-9]{8}]]
    pos:            int         # orden de despliegue en la formación
    puntos:         int         # costo en puntos de reclutamiento del miembro
    rango:          str         # slug de rango (ej. "lider_de_escuadra")
    nombre:         str         # nombre compuesto de guerra del personaje
```

#### Tabla de Costo en Puntos por Unidad
El costo en puntos se define de acuerdo al rango y la función de la tropa (se declaran como tags de rango en [[tag-modelo]]):
- **==`1` punto==**: Colimbas/Reclutas (rango `recluta`) e integrantes de milicias (rango `militante`).
- **==`2` puntos==**: Soldados de segunda / regulares (rango `fusilero`).
- **==`3` puntos==**: Especialistas (rangos `artillero`, `francotirador`).
- **==`4` puntos==**: Segundos mandos y apuntadores (rango `segundo_al_mando`, y roles de `apuntador`).
- **==`5` puntos==**: Líderes de unidad (rango `lider_de_escuadra`).

### 2.3. Historial de Escuadra (`historial[]`)
La escuadra mantiene una hoja de vida de todos los eventos significativos que le suceden al grupo táctico o a sus integrantes individuales:

```yaml
historial:
  - fecha:       str       # ISO-8601
    tipo:        str       # enum abierto: baja_miembro | ascenso_miembro | combate_finalizado | reorganizacion
    descripcion: str       # Prosa descriptiva
    ref_batalla: str | null# Batalla de referencia si aplica
    metadata:    object    # Libre
```

> [!tip] Tipos Comunes de Hitos
> - `baja_miembro`: Registro cuando un personaje de la escuadra pasa a estado `kia`.
> - `ascenso_miembro`: Registro cuando un integrante es promovido en rango o asume el mando.
> - `combate_finalizado`: Hitos operacionales globales de la escuadra.
> - `reorganizacion`: Modificaciones en el listado de miembros activos.

---

## §3 — Valores Agregados y Derivados (Calculados al servir)

Estas estadísticas tácticas se calculan dinámicamente en caliente a partir de la composición de los miembros activos (no KIA) y no se persisten en la base de datos (ver [[hoja-modelo#derivados_no_persistidos|hoja-modelo.md §8]]):

### 3.1. Fuerza Aportada Total (`fza_total`)

- **Fórmula**: Suma de la `fza_aportada` de los miembros activos (no KIA). Las magnitudes son:
  - `rol.combate.heroe`: ==3== (ver [[tag-modelo#§3 — Categorías de referencia|tag-modelo.md §3]])
  - `rol.combate.lider`: ==2==
  - Otros: ==1==

### 3.2. Moral de Escuadra (`moral_promedio`)

Representa la cohesión psicológica media del grupo táctico.
- **Fórmula**: Promedio entero redondeado hacia abajo del atributo MENTAL (`men`) de todos los miembros activos (ver [[atributos-y-efectos#1. Atributos Base (Persistidos)|atributos-y-efectos.md §1]]).

### 3.3. Fatiga de Escuadra (`fatiga_promedio`)

Representa el desgaste físico-mental promedio de la escuadra.
- **Fórmula**: Promedio entero redondeado hacia abajo del valor total de `fatiga_max` (`fis` + `men`) de todos los miembros activos (ver [[atributos-y-efectos#2.4. FATIGA|atributos-y-efectos.md §2.4]]).

### 3.4. Movimiento Táctico de Escuadra (`movimiento_tactico`)

- **Fórmula**: `min(MOVIMIENTO)` de todos los miembros activos. La unidad marcha al ritmo de su miembro más lento (ver [[atributos-y-efectos#2.3. MOVIMIENTO|atributos-y-efectos.md §2.3]]).

### 3.5. Puntos Totales (`puntos_totales`)

- **Fórmula**: Suma de los `puntos` de todos los miembros del listado (incluidos inactivos/KIA para mantener la auditoría de costo inicial).

### 3.6. Líder Vigente (`lider_vigente`)

Determina qué personaje ejerce la autoridad táctica efectiva sobre el terreno, evaluado en este orden de prioridad entre los miembros activos:
1. `lider_de_escuadra`
2. `segundo_al_mando`
3. Combatiente activo de mayor edad.

### 3.7. Estado de la Escuadra (`estado_escuadra`)

Indica la condición operativa de la unidad:
- `operativa`: Escuadra con líder o segundo activo, y con suficiente capacidad de combate.
- `decapitada`: Líder y segundo caídos o incapacitados.
- `desmembrada`: `fza_total < 8` (baja operatividad, propensa a la desintegración).
- `retirada`: Unidad fuera de combate.

---

## §4 — Plantilla de Validación (Infantería)

Una escuadra de tipo `"escuadra_de_infanteria"` debe respetar las siguientes restricciones en su organización de combate (verificadas programáticamente contra [[tag-requeridos-por-categoria]]):

1. **Líder de Unidad**: Requiere exactamente ==1 miembro== con rango `lider_de_escuadra` (costo 5). Debe ocupar la posición ==`1`==.
2. **Líderes proporcionales**: Mínimo ==1 rango de mando== (`lider_de_escuadra` o `segundo_al_mando`) por cada ==4 soldados== de infantería regular (`fusilero`, `militante`, `recluta`).
3. **Estructura de la Ametralladora (FAP)**: Requiere exactamente ==1 ametrallador especialista== (rango `artillero`, costo 3) que cuente con:
   - 1 Apuntador (Cabo Apuntador / Tirador, costo 4).
   - 1 Cargador (típicamente recluta, costo 1).
4. **Cabo Apuntador**: Requiere al menos ==1 miembro== con rol de apuntador (Cabo/Tirador, costo 4).
5. **Tamaño de Roster**: Mínimo ==5== y máximo ==21== integrantes. El tamaño óptimo son ==11 miembros==.

> [!warning] Fallo en la Validación
> Si una escuadra activa viola alguna de estas condiciones, se expone mediante los campos derivados:
> - `cumple_template`: `false`
> - `errores_validacion[]`: Lista de strings detallando cada infracción estructural detectada.

