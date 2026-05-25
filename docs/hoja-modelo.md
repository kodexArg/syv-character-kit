# Hoja Modelo — SyV Character Sheet

> **Versión**: compatible con schema v0.4.1
> **Propósito**: referencia visual completa de la hoja de personaje canónica, incluyendo
> el bloque ESTADO_VITAL que introduce el tracking permanente de Fatiga y Moral.
> Este archivo NO modifica el PRD — es documentación de presentación.

---

## 1. Bloques de la hoja (orden canónico)

La hoja replica fielmente el payload JSON/YAML definido en PRD §6. El orden de bloques
corresponde al orden de presentación aprobado por el cliente (PRD §6.0).

| # | Bloque | Origen en schema |
|---|---|---|
| 1 | CABECERA (identidad nominal, pertenencia, datos biológicos, operativo) | campos estructurados de cabecera |
| 2 | ATRIBUTOS | `atributos.{fis, tac, men}` |
| 3 | RASGOS | `tags[categoria=rasgo]` |
| 4 | EQUIPO | `tags[categoria=equipo.*]` |
| 5 | SKILLS | `tags[categoria=skill]` |
| 6 | TRAITS | `tags[categoria=trait]` |
| 7 | PERKS | `tags[categoria=perk]` |
| 8 | ASPECTOS | `tags[categoria=aspecto]` |
| 9 | **ESTADO VITAL** | campos derivados persistidos (ver §3) |
| 10 | LEALTADES | `lealtades` |
| 11 | VINCULOS | `vinculos[]` |
| 12 | HISTORIAL | `historial[]` |
| 13 | HISTORIA | `historia` |
| 14 | METADATOS | `metadatos` |

---

## 2. Reglas de cálculo de Fatiga y Moral

### 2.1. Fatiga

```
fatiga_max  = atributos.fis + atributos.men
fatiga_actual = fatiga_max  (al crear; muta en juego)
```

Promedio de escuadra esperado ≈ 6 (base: FIS 3 + MEN 3 para rangos bajos).
Para líderes: FIS 3 + MEN 7 = 10.

### 2.2. Moral

```
moral_max    = atributos.men
moral_actual = moral_max   (al crear; muta en juego)
```

### 2.3. Naturaleza de los valores

- **Derivados al crear**: `fatiga_max` y `moral_max` se computan una sola vez de los
  atributos base y se persisten en la hoja. No se recalculan cada sesión salvo que
  cambie el atributo base (via hito `triple_cero` o `mejora_atributo`; en ese caso el
  narrador debe recalcular el tope manualmente y registrarlo como hito).
- **Mutables en juego**: `fatiga_actual` y `moral_actual` cambian durante la partida y
  se registran como hitos `cambio_estado_vital` (tipo abierto — ver OQ al pie).
- **Expresión**: pares `actual / máx` (ej. `7 / 10`). No se usan casillas gráficas en
  el schema de datos, pero la hoja ASCII los puede renderizar como pista opcional.

### 2.4. Posición en la hoja

El bloque ESTADO VITAL se ubica **después de ASPECTOS y antes de LEALTADES**. Justificación:
ATRIBUTOS definen los topes (datos de creación); ESTADO VITAL los consume como derivados
que evolucionan en juego, igual que las condiciones de combate. Colocarlo entre los bloques
de identidad mecánica (skills/traits/perks/aspectos) y los bloques de relación social
(lealtades/vínculos) refleja esa naturaleza intermedia.

---

## 3. Schema del bloque ESTADO_VITAL

El bloque no agrega campos raíz al personaje (respeta open/close del PRD). Se serializa
bajo la clave `estado_vital` al mismo nivel que `atributos`, como campo de primer nivel
no-tag.

```yaml
estado_vital:
  fatiga_max:    integer   # DERIVADO al crear: atributos.fis + atributos.men (inmutable salvo cambio de atributo)
  fatiga_actual: integer   # mutable; arranca igual a fatiga_max; decrece en juego
  moral_max:     integer   # DERIVADO al crear: atributos.men (inmutable salvo cambio de atributo)
  moral_actual:  integer   # mutable; arranca igual a moral_max; decrece en juego
```

**Invariantes:**
- `0 <= fatiga_actual <= fatiga_max`
- `0 <= moral_actual <= moral_max`
- Si cambia `atributos.fis` o `atributos.men`, el narrador actualiza `fatiga_max`
  (y `moral_max` si cambió `men`) vía hito dedicado y registra el delta en `historial[]`.

**Tipo de hito sugerido para mutaciones de ESTADO VITAL:**

```yaml
tipo: cambio_estado_vital
metadata:
  campo:         "fatiga_actual" | "moral_actual" | "fatiga_max" | "moral_max"
  valor_anterior: integer
  valor_nuevo:    integer
  motivo:        string   # ej. "agotamiento tras 3 turnos sin cobertura"
```

---

## 4. Hoja ASCII canónica — plantilla en blanco

```
+----------------------------------------------------------------------------+
| SyV CHARACTER SHEET                                          schema v0.4.1 |
| id: <id>                                                  origen: <origen> |
+----------------------------------------------------------------------------+
| NOMBRE         <nombre>                                                    |
| SOBRENOMBRE    <sobrenombre>                                               |
| FILIACION      <filiacion>                                                 |
| FACCION        <faccion>                                                   |
|                                                                            |
| EDAD           <edad>                                                      |
| GENERO         <genero>                                                    |
| ESTADO SALUD   <estado_salud>                                              |
|                                                                            |
| ROL            <rol>                                                       |
| ESTADO         <estado>                                                    |
| RANGO          <rango>                                                     |
| ESCUADRA       <escuadra.nombre>                    (<escuadra_id>)        |
| MANDO          <si|no>                                                     |
+----------------------------------------------------------------------------+
| ATRIBUTOS                                                                  |
|   FIS  #  [######]    TAC  #  [######]    MEN  #  [######]                |
+----------------------------------------------------------------------------+
| RASGOS                                                                     |
|   <rasgo>, <rasgo>, <rasgo>, ...                                           |
+----------------------------------------------------------------------------+
| EQUIPO                                                                     |
|   ARMAS        [<arma>]  [<arma>]                                          |
|   UTILITARIOS  [<util>]  [<util>]  [<util>]                               |
|   VESTIDURA    [<vestidura>]                                               |
+----------------------------------------------------------------------------+
| SKILLS                                                                     |
|   [<skill>]  [<skill>]  [<skill>]                                          |
+----------------------------------------------------------------------------+
| TRAITS                                                                     |
|   [<trait>]  [<trait>]                                                     |
+----------------------------------------------------------------------------+
| PERKS                                                                      |
|   [<perk>]                                                                 |
+----------------------------------------------------------------------------+
| ASPECTOS                                                                   |
|   [<aspecto>]                                                              |
+----------------------------------------------------------------------------+
| ESTADO VITAL                                                               |
|   FATIGA   <fatiga_actual> / <fatiga_max>    (= FIS + MEN al crear)       |
|   MORAL    <moral_actual>  / <moral_max>     (= MEN al crear)             |
+----------------------------------------------------------------------------+
| LEALTADES                                                                  |
|   primaria   : <lealtad_primaria>                                          |
|   secundarias: [<lealtad>, <lealtad>]                                      |
|   secretos   : [<secreto>]                                                 |
+----------------------------------------------------------------------------+
| VINCULOS                                                                   |
|   <tipo>  -> <ref_personaje_id>  (<descripcion_corta>)                    |
+----------------------------------------------------------------------------+
| HISTORIAL                                                                  |
|   <fecha>  <tipo_hito>  <descripcion>                                      |
+----------------------------------------------------------------------------+
| HISTORIA                                                                   |
|   <prosa 120-200 palabras>                                                 |
+----------------------------------------------------------------------------+
| METADATOS                                                                  |
|   semilla: <semilla>    modelo_prosa: <modelo|null>    es_canon: <bool>   |
|   creado_en: <ISO>      ultima_actualizacion: <ISO>                        |
+----------------------------------------------------------------------------+
```

---

## 5. Ejemplo rellenado — Lisandro Quiroga (mock.confederacion.03.quiroga)

Personaje seleccionado: **Apuntador Lisandro Quiroga** — Rango `Apuntador`.

Atributos: FIS 3, TAC 5, MEN 5.

**Cálculo del bloque ESTADO VITAL:**
```
fatiga_max    = FIS + MEN = 3 + 5 = 8
fatiga_actual = 8   (recién creado / inicio de campaña)
moral_max     = MEN = 5
moral_actual  = 5   (recién creado / inicio de campaña)
```

```
+----------------------------------------------------------------------------+
| SyV CHARACTER SHEET                                          schema v0.4.1 |
| id: mock.confederacion.03.quiroga                         origen: mock     |
+----------------------------------------------------------------------------+
| NOMBRE         Lisandro Quiroga                                            |
| SOBRENOMBRE    Cabo Apuntador Lisandro Quiroga                             |
| FILIACION      Apuntador de la Escuadra Ricardo                            |
|                del Ejercito de la Confederacion Argentina                  |
| FACCION        Confederacion                                               |
|                                                                            |
| EDAD           25                                                          |
| GENERO         masculino                                                   |
| ESTADO SALUD   saludable                                                   |
|                                                                            |
| ROL            Cabo Apuntador                                              |
| ESTADO         activo                                                      |
| RANGO          Apuntador                                                   |
| ESCUADRA       Escuadra Ricardo                        (esq_conf_03)       |
| MANDO          no                                                          |
+----------------------------------------------------------------------------+
| ATRIBUTOS                                                                  |
|   FIS  3  [###..]    TAC  5  [#####]    MEN  5  [#####]                  |
+----------------------------------------------------------------------------+
| RASGOS                                                                     |
|   altura alta, complexion delgada, pelo lacio, ojos atentos, habla escasa |
+----------------------------------------------------------------------------+
| EQUIPO                                                                     |
|   ARMAS        [rifle militar]                                             |
|   UTILITARIOS  [cargador]  [cargador]  [mapa]                             |
|   VESTIDURA    [uniforme confederado]                                      |
+----------------------------------------------------------------------------+
| SKILLS                                                                     |
|   [Tiro de precision]  [Lectura de mapas]                                  |
+----------------------------------------------------------------------------+
| TRAITS                                                                     |
|   [Paciente]  [Punteria fria]                                              |
+----------------------------------------------------------------------------+
| PERKS                                                                      |
|   [Olfato del terreno]                                                     |
+----------------------------------------------------------------------------+
| ASPECTOS                                                                   |
|   (ninguno)                                                                |
+----------------------------------------------------------------------------+
| ESTADO VITAL                                                               |
|   FATIGA    8 / 8    (FIS 3 + MEN 5)                                      |
|   MORAL     5 / 5    (MEN 5)                                               |
+----------------------------------------------------------------------------+
| LEALTADES                                                                  |
|   primaria   : Confederacion                                               |
|   secundarias: [su escuadra, el oficio del agrimensor]                    |
|   secretos   : []                                                          |
+----------------------------------------------------------------------------+
| VINCULOS                                                                   |
|   hermano_de_armas -> mock.confederacion.01.aguirre                        |
|                       (el Sargento le pide lectura del terreno antes de   |
|                        cada despliegue)                                    |
+----------------------------------------------------------------------------+
| HISTORIAL                                                                  |
|   2026-02-10  ascenso  Ascendido a Cabo tras eliminar a operador de radio  |
|                        enemigo a 280m en llovizna.                         |
+----------------------------------------------------------------------------+
| HISTORIA                                                                   |
|   Quiroga es de La Rioja, aunque su familia lleva dos generaciones en el  |
|   Alto Valle. Estudio dos anos de agrimensura antes de que el servicio    |
|   obligatorio lo interrumpiera. La formacion no fue al pedo: sabe leer    |
|   mapas topograficos con naturalidad y entiende de curvas de nivel, de    |
|   donde corre el agua y de donde sopla el viento en un valle encajonado.  |
|   El frente patagonico lo recibio con niebla y barro. Quiroga aprendio    |
|   rapido que el fusil de precision en baja visibilidad no es una ventaja  |
|   sino una responsabilidad. Lo ascendieron a Cabo despues de dar de baja  |
|   a un operador de radio enemigo a 280 metros, en llovizna, sin que nadie |
|   supiera desde donde habia disparado.                                     |
+----------------------------------------------------------------------------+
| METADATOS                                                                  |
|   semilla: mock-fixed-03    modelo_prosa: null    es_canon: true          |
|   creado_en: 2026-05-24     ultima_actualizacion: 2026-02-10              |
+----------------------------------------------------------------------------+
```

### 5.1. YAML con bloque estado_vital

```yaml
personaje:
  id: mock.confederacion.03.quiroga
  origen: mock
  semilla: mock-fixed-03

  nombre: Lisandro Quiroga
  sobrenombre: Cabo Apuntador Lisandro Quiroga
  filiacion: "Apuntador de la Escuadra Ricardo del Ejército de la Confederación Argentina"

  faccion: Confederación
  edad: 25
  genero: masculino
  estado_salud: saludable

  rol: Cabo Apuntador
  estado: activo
  rango: Apuntador
  escuadra_id: esq_conf_03
  mando: false

  atributos:
    fis: 3
    tac: 5
    men: 5

  estado_vital:
    fatiga_max:    8    # fis(3) + men(5) — inmutable salvo cambio de atributo
    fatiga_actual: 8    # mutable en juego
    moral_max:     5    # men(5) — inmutable salvo cambio de atributo
    moral_actual:  5    # mutable en juego

  tags:
    - { categoria: rasgo,             valor: "altura alta" }
    - { categoria: rasgo,             valor: "complexion delgada" }
    - { categoria: rasgo,             valor: "pelo lacio" }
    - { categoria: rasgo,             valor: "ojos atentos" }
    - { categoria: rasgo,             valor: "habla escasa" }
    - { categoria: rol,               valor: "apuntador" }
    - { categoria: skill,             valor: "Tiro de precisión" }
    - { categoria: skill,             valor: "Lectura de mapas" }
    - { categoria: trait,             valor: "Paciente" }
    - { categoria: trait,             valor: "Puntería fría" }
    - { categoria: perk,              valor: "Olfato del terreno" }
    - { categoria: "equipo.arma",     valor: "rifle militar" }
    - { categoria: "equipo.utilitario", valor: "cargador" }
    - { categoria: "equipo.utilitario", valor: "cargador" }
    - { categoria: "equipo.utilitario", valor: "mapa" }
    - { categoria: "equipo.vestidura", valor: "uniforme confederado" }

  lealtades:
    primaria: Confederación
    secundarias:
      - su escuadra
      - el oficio del agrimensor
    secretos: []

  vinculos:
    - tipo: hermano_de_armas
      ref_personaje_id: mock.confederacion.01.aguirre
      descripcion: "El Sargento le pide lectura del terreno antes de cada despliegue."

  historia: |
    Quiroga es de La Rioja, aunque su familia lleva dos generaciones en el Alto
    Valle. Estudió dos años de agrimensura antes de que el servicio obligatorio
    lo interrumpiera. [...texto completo en el mock...]

  historial:
    - fecha: "2026-02-10T08:00:00Z"
      tipo: ascenso
      descripcion: "Ascendido a Cabo tras eliminar a operador de radio enemigo a 280m en llovizna."
      ref_batalla: null
      metadata:
        rango_anterior: Apuntador
        rango_nuevo: Apuntador

  tags_iniciales:
    - { categoria: rasgo,               valor: "altura alta" }
    - { categoria: rasgo,               valor: "complexion delgada" }
    - { categoria: rasgo,               valor: "pelo lacio" }
    - { categoria: rasgo,               valor: "ojos atentos" }
    - { categoria: rasgo,               valor: "habla escasa" }
    - { categoria: rol,                 valor: "apuntador" }
    - { categoria: skill,               valor: "Tiro de precisión" }
    - { categoria: skill,               valor: "Lectura de mapas" }
    - { categoria: trait,               valor: "Paciente" }
    - { categoria: trait,               valor: "Puntería fría" }
    - { categoria: perk,                valor: "Olfato del terreno" }
    - { categoria: "equipo.arma",       valor: "rifle militar" }
    - { categoria: "equipo.utilitario", valor: "mapa" }
    - { categoria: "equipo.vestidura",  valor: "uniforme confederado" }

  metadatos:
    creado_en: "2026-05-24T00:00:00Z"
    canonizado_en: "2026-05-24T00:00:00Z"
    ultima_actualizacion: "2026-02-10T08:00:00Z"
    modelo_prosa: null
    es_canon: true

  extras: null
```

---

## 6. Tabla de referencia rápida — ESTADO VITAL por rango

Derivada de la tabla de atributos del PRD §7.2.

| Rango | FIS | TAC | MEN | fatiga_max (FIS+MEN) | moral_max (MEN) |
|---|---|---|---|---|---|
| `Lider de escuadra` | 3 | 5 | 7 | **10** | **7** |
| `Segundo al mando`  | 3 | 5 | 6 | **9**  | **6** |
| `Apuntador`         | 3 | 5 | 5 | **8**  | **5** |
| `Artillero`         | 3 | 4 | 3 | **6**  | **3** |
| `Fusilero`          | 3 | 3 | 3 | **6**  | **3** |
| `Recluta`           | 3 | 2 | 2 | **5**  | **2** |

Promedio de escuadra (composición 1+1+1+1+4+3): ≈ 6.5 de fatiga, ≈ 3.9 de moral.

---

## 7. Open Questions

Las siguientes preguntas quedan abiertas — no deben resolverse en este documento sino
en el PRD cuando el motor de batalla o el narrador tengan más contexto:

1. **Umbrales de Fatiga**: ¿hay niveles que disparen penalidades automáticas
   (ej. fatiga_actual ≤ 3 → tag `estado_temporal: fatigado`; fatiga_actual = 0 →
   tag `estado_temporal: exhausto`)? El PRD ya registra `Fatigado crónico` como trait
   canon y los aspectos `veterano-cicatrizado` y `devoto` hacen referencia a tags
   `cansado` / `exhausto` (§10.1 y pool de aspectos), lo cual sugiere que el patrón
   existe pero aún no está sistematizado. Candidato natural para una ola de
   `estado_temporal` una vez que el motor de batalla lo requiera.

2. **Umbrales de Moral**: ¿moral_actual = 0 → `pánico` automático (análogo al aspecto
   `cobarde`)? ¿O se deja al criterio del narrador? El pool de aspectos ya usa
   `pánico` como tag activable (§10 `/meta/aspectos`), pero no hay regla canónica
   de umbral definida en el PRD.

3. **Recalibración de topes tras triple_cero**: cuando un hito `triple_cero` incrementa
   `atributos.men`, ¿el narrador debe emitir además un hito `cambio_estado_vital`
   para actualizar `fatiga_max` y `moral_max`? ¿O la API lo recalcula derivado al servir
   (igual que `fza_aportada`)? Este PRD opta por persistir `fatiga_max` y `moral_max`
   para que el motor de batalla los lea sin recalcular — pero eso requiere un hito
   coordinado. Decisión pendiente de confirmación con el cliente.

4. **Tipo de hito canónico**: `cambio_estado_vital` es el nombre sugerido en §3 de
   este documento. Falta incorporarlo a la tabla §9.5 del PRD si el cliente lo aprueba.
