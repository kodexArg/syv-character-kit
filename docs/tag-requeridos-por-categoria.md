---
title: "Tags requeridos por categoría"
tags:
  - syv/docs/schema
  - syv/tags
aliases:
  - tag-requeridos-por-categoria
  - Tags Requeridos
---

# Tags requeridos por categoría

> [!info] Protocolo Blando
> - **Protocolo blando**: Índice canónico de campos obligatorios condicionales `(+)` por categoría y subcategoría.
> - **Complemento**: Este documento complementa a [[tag-modelo#4.2. Campos obligatorios condicionales — los (+)|tag-modelo.md §4.2]].
> 
> Los cuatro campos siempre obligatorios `(*)` — `slug`, `nombre`, `categoria`, `descripcion` — viven en [[tag-modelo#4.1. Campos obligatorios siempre — los cuatro (*)|tag-modelo.md §4.1]] y **no** se repiten acá.
> 
> Lo mantiene el orquestador: cada vez que se instaura una nueva regla de obligatoriedad condicional para una categoría, se anota acá como una bullet.

---

## equipo

- `subcategoria` ∈ {`arma`, `utilitario`, `vestidura`}
- `peso` — `int`, kilos, rango `0..50`. No confundir con `peso_narrativo` (hint 1..5 al sorteador).

## equipo.arma

- `equipo_arma.tipo_accion` ∈ {`cerrojo`, `semiauto`, `automatico`, `cuerpo_a_cuerpo`}
- `equipo_arma.alcance` ∈ {`corto`, `medio`, `largo`}

## trait

- `efecto` (a nivel raíz como string o lista de strings) **o** `trigger` (con su `trigger-action`) — uno de los dos es obligatorio. `efecto` para pasivos/permanentes (sobre el vocabulario canónico de [[atributos-y-efectos|atributos-y-efectos.md]]); `trigger` con `trigger-action` para reactivos/temporales.

## skill

- `skill.atributo_dominante` ∈ {`fis`, `tac`, `men`} — obligatorio. Define el atributo contra el que el motor tira cuando resuelve un chequeo asociado a esta skill. Una skill **no** lleva campo `efecto`: es habilitador de tirada, no modificador (ver [[atributos-y-efectos|atributos-y-efectos.md]]).

## perk

- **No lleva `requires` ni `excluye`** — los perks se otorgan al azar como recompensa narrativa (vía hito en campo), sin precondiciones de pertenencia ni dependencias de otros tags (ver [[tag-modelo#4.4. Sistema requires — dependencias del tag|tag-modelo.md §4.4]]). Cualquier perk puede caer sobre cualquier personaje.
- `efecto` recomendado (no obligatorio en v1): los perks suelen aportar un modificador numérico explícito sobre el vocabulario canónico.

## efecto

- `efecto` (a nivel raíz como lista de strings) — obligatorio. Lista de instrucciones o modificadores. Los tags `efecto.*` son standalone, referenciables desde el `trigger-action` de un trait reactivo.

## rol

- `subcategoria` ∈ {`oficio`, `jerarquia`, `narrativo`, `combate`}

## subfaccion

- `subfaccion.faccion_padre` — tag `faccion.*` obligatorio que apunta a la facción principal a la que pertenece la subfacción.


