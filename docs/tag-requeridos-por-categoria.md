# Tags requeridos por categoría

> **Protocolo blando.** Índice canónico de campos obligatorios condicionales `(+)`
> por categoría y subcategoría. Complementa [`tag-modelo.md`](tag-modelo.md) §4.2.
>
> Los cuatro campos siempre obligatorios `(*)` — `slug`, `nombre`, `categoria`,
> `descripcion` — viven en §4.1 y **no** se repiten acá.
>
> Lo mantiene el orquestador: cada vez que se instaura una nueva regla de
> obligatoriedad condicional para una categoría, se anota acá como una bullet.

---

## equipo

- `subcategoria` ∈ {`arma`, `utilitario`, `vestidura`}
- `peso` — `int`, kilos, rango `0..50`. No confundir con `peso_narrativo` (hint 1..5 al sorteador).

## equipo.arma

- `equipo_arma.tipo_accion` ∈ {`cerrojo`, `semiauto`, `automatico`, `cuerpo_a_cuerpo`}
- `equipo_arma.alcance` ∈ {`corto`, `medio`, `largo`}

## aspecto

- `efecto` (a nivel raíz como string o lista de strings) o `trigger` (con su `trigger-action`) — requerido para asociar efectos al aspecto. Se usa `efecto` a nivel raíz (como string o lista de strings de modificadores de atributos base o estadísticas calculadas) para efectos pasivos/permanentes; se usa `trigger` con `trigger-action` si es reactivo/temporal.

## rol

- `subcategoria` ∈ {`oficio`, `jerarquia`, `narrativo`, `combate`}

## subfaccion

- `subfaccion.faccion_padre` — tag `faccion.*` obligatorio que apunta a la facción principal a la que pertenece la subfacción.

