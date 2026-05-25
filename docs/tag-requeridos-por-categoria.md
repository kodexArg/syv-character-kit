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

## aspecto

- `efectos` — lista de referencias a tags de la categoría `efecto.*` que se aplican con el tag.

## rol

- `subcategoria` ∈ {`oficio`, `jerarquia`, `narrativo`, `combate`}
