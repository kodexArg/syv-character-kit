---
title: "GDDR-01: Flujo Obligatorio de Creación de Personaje"
tags:
  - syv/gddr
  - syv/personajes
aliases:
  - GDDR-01
  - Flujo de Creación
---

# GDDR-01: Flujo Obligatorio de Creación de Personaje

> [!info] Estado y Contexto
> - **Estado**: En redacción — Fases 1, 2 y 3 definidas. Fase 4 pendiente.
> - **Contexto**: Establecer la secuencia exacta de pasos necesarios para construir un personaje en *Subordinación y Valor*. El flujo **no sigue el orden visual de la hoja**: para que los atributos y los datos personales tengan sentido, la afiliación operativa (rango + facción + subfacción) se decide primero. La hoja describe la estructura del personaje *terminado*; este documento describe cómo se llega ahí.

## Orden de fases

```
Fase 1: Afiliación      → Rango, Facción, Subfacción, Escuadra
Fase 2: Identidad       → Nombre, Sobrenombre, Edad, Género, …
Fase 3: Atributos       → fis, tac, men (derivados de Fase 1)
Fase 4: Resto           → tags adicionales, historia, historial, metadatos
```

Cada fase depende de la anterior y puede imponer restricciones sobre la siguiente vía **tabla de reglas** (ver §Reglas).

---

## Fase 1 — Afiliación

Tres campos, **en este orden**: Rango → Facción → Subfacción. El sistema **solicita** cada uno; si no se provee, lo sortea con la tabla de pesos del campo correspondiente.

### 1.1. Rango

Cada personaje arranca con **exactamente un** tag `rango.*`. Catálogo canon en [`tags/rango/`](../tags/rango/):

- `ciudadano` *(implícito si no se asigna otro — corresponde al `rol: "ciudadano"` default de la hoja; no entra al sorteo)*
- `militante`
- `recluta`
- `fusilero`
- `apuntador`
- `artillero`
- `tirador_designado`
- `segundo_al_mando`
- `lider_de_escuadra`

**Sorteo ponderado (fallback si no se provee)** — creación de combatiente al azar:

| Rango | Peso |
| :--- | ---: |
| `recluta` | 30% |
| `fusilero` | 20% |
| `apuntador` | 10% |
| `artillero` | 10% |
| `tirador_designado` | 2% |
| `segundo_al_mando` | 7% |
| `lider_de_escuadra` | 3% |
| `militante` | 18% |

Suma 100%. La curva refleja escasez operativa.

`ciudadano` se asigna explícitamente cuando el caso de uso es NPC civil — no entra al sorteo.

### 1.2. Facción

Cada personaje arranca con **exactamente un** tag `faccion.*`. Catálogo canon en [`tags/faccion/`](../tags/faccion/):

- `confederados`
- `ejercito_rojo`

**Sorteo (fallback)**: uniforme 50/50 por defecto. Override por contexto de campaña.

### 1.3. Subfacción

Cada personaje arranca con **exactamente un** tag `subfaccion.*`. Catálogo canon en [`tags/subfaccion/`](../tags/subfaccion/):

- `pelicanos` *(Confederación)*
- `ejercito_revolucionario_del_pueblo` *(Ejército Rojo)*

**Sorteo (fallback)**: uniforme entre las subfacciones **compatibles con la facción** de §1.2. El catálogo de cada subfacción declara su `subfaccion.faccion_padre` (ver [[tag-modelo#4.2. Campos obligatorios condicionales — los (+)|tag-modelo.md §4.2]]).

### 1.4. Escuadra

Cada personaje activo arranca con **exactamente un** tag `escuadra.*`. Catálogo canon en [`tags/escuadra/`](../tags/escuadra/):

- `columna_mansilla` *(Ejército Rojo)*
- `cazadores_de_ricardo` *(Confederación)*

> [!important] Requisito de Existencia y Creación Automática (On-the-Fly)
> Al asignar el tag `escuadra.{slug}` a un personaje, el sistema asume que la entidad `escuadra` correspondiente **ya existe** en el almacenamiento persistente. Si **no existe**, el sistema **debe crearla inmediatamente** al vuelo (on-the-fly) inicializando una nueva entidad con las siguientes reglas:
> - **`identidad.slug`**: Se define exactamente con el `{slug}` del tag.
> - **`identidad.nombre`**: Se deriva formateando el slug (ej. `columna_mansilla` pasa a ser `"Columna Mansilla"`) o se solicita al usuario.
> - **`identidad.faccion`**: Se hereda del tag `faccion.*` del personaje creador.
> - **`identidad.tipo`**: Se inicializa como `"escuadra_de_infanteria"` (el tipo táctico predeterminado del MVP).
> - **`miembros`**: Se inicializa conteniendo al personaje creador, asignándole la primera posición táctica disponible según su rango (ej. si es `lider_de_escuadra` en la posición 1, o si no en orden consecutivo).
> - **`historial`**: Se inicializa con un hito de tipo `reorganizacion` documentando la autogeneración de la escuadra y la incorporación del miembro fundador.
> 
> Esta creación al vuelo asegura que no existan personajes activos huérfanos sin escuadra de encuadre en el sistema.

### 1.5. Reglas que esta fase puede imponer

Esta fase puede **restringir Género y Edad** de Fase 2 vía la tabla de reglas (ver §Reglas). Ejemplos típicos:

- Facción militar histórica → `genero ∈ {masculino}`.
- `lider_de_escuadra` → `edad ≥ 25`.
- `recluta` → `edad ≤ 22`.

Las reglas concretas son **TBD**.

### 1.6. Decisiones de Integración con el Combate y Flujo de Control

La regla de existencia y creación de escuadras desencadena las siguientes decisiones de diseño y comportamiento del sistema al intentar transicionar hacia el combate táctico:

#### 1.6.1. Requisito de Dos Escuadras Armadas
No es posible ingresar a la fase de batalla (detallada en [[02-motor-batalla|gddr/02-motor-batalla.md]]) si no se cuenta con **dos escuadras diferentes y totalmente armadas**. El combate táctico es de naturaleza escuadra contra escuadra, por lo que una sola escuadra (o escuadras que no pertenezcan a facciones opuestas, salvo en escenarios de entrenamiento explícitos) no puede iniciar una partida.

#### 1.6.2. Bloqueo por Validación Estructural
Dado que una escuadra autogenerada *on-the-fly* arranca con un único miembro, esta no cumple con las restricciones de la plantilla táctica (`cumple_template: false` debido a que tiene menos de 5 miembros, le faltan roles requeridos como el ametrallador o el apuntador, etc.).
- El motor del juego **debe bloquear el inicio de la batalla** si alguna de las dos escuadras seleccionadas no supera la validación estructural.
- El sistema debe exponer los errores mediante la lista `errores_validacion[]` generada por la plantilla de validación de la escuadra (ver [[escuadra-modelo#§4 — Plantilla de Validación (Infantería)|escuadra-modelo.md §4]]).

#### 1.6.3. Resolución de Escuadras Inválidas (Llenado Rápido / Autofill)
Para evitar que el flujo de juego se interrumpa indefinidamente, el sistema debe proveer dos mecanismos para completar las escuadras antes del combate:
1. **Llenado Manual (Flujo Campaña)**: El usuario continúa creando personajes de forma individual a través de las Fases 1 a 4, asignándoles el tag de la escuadra hasta que esta sea válida de forma natural.
2. **Autofill Procedural Táctico (Roster Rápido)**: La interfaz o el motor de juego ofrece la opción de "autocompletar" la escuadra de manera automática. Al gatillarse, el sistema genera de forma procedural los personajes necesarios para cumplir con el template `"escuadra_de_infanteria"` (respetando la proporción de líderes, asignando un apuntador, un artillero y su cargador), asignándoles nombres de los pools y calculando sus atributos determinísticamente por su rango, hasta alcanzar el mínimo reglamentario (5 miembros) o el óptimo operativo (11 miembros), descontando los puntos de reclutamiento correspondientes.

#### 1.6.4. Impacto de Bajas (KIA) en Campañas Continuas
Cuando un personaje muere en combate, su tag de estado pasa a `estado.kia`. Esto tiene un impacto directo en el flujo de campaña:
- El personaje KIA permanece en el registro de la escuadra con fines de auditoría histórica y de costo inicial de puntos (`puntos_totales`), pero **deja de contar** para el cálculo de estadísticas activas (`fza_total`, `moral_promedio`, `fatiga_promedio`, `movimiento_tactico`).
- Si al terminar un combate la escuadra sufre bajas tales que su roster activo cae por debajo del mínimo de 5 integrantes, o pierde a sus mandos tácticos (estado `desmembrada` o `decapitada`), la escuadra **pierde su aptitud para combate**.
- Para poder ingresar a una nueva fase de batalla, el sistema obligará a realizar una fase de reorganización (incorporando nuevos reclutas o usando autofill) hasta que la escuadra vuelva a cumplir con la validación del template.

---

## Fase 2 — Identidad personal

Genera el bloque `personaje.identidad` (ver [[hoja-modelo#§1 — Identidad|hoja-modelo.md §1]]) **respetando las restricciones de Fase 1**.

### 2.1. Género — tirada ponderada

| Resultado | Peso |
| :--- | ---: |
| masculino | 45% |
| femenino | 45% |
| no_binario | 5% |
| desconocido | 5% |

Si Fase 1 restringe el set, se re-sortea hasta caer dentro del set permitido (no se sesga la tabla base).

### 2.2. Edad — tirada uniforme

Rango por defecto: **12–70 años** (entero, uniforme). Si Fase 1 estrecha el rango, se re-sortea hasta caer dentro.

### 2.3. Nombre

Sorteo desde pools curados en [`resources/nombres/`](../resources/nombres/):

- `nombres_m.txt` — 25 nombres masculinos argentinos modernos, formato `Nombre|Apodo`.
- `nombres_f.txt` — 25 nombres femeninos argentinos modernos, formato `Nombre|Apodo`.
- `apellidos.txt` — 50 apellidos argentinos (mix hispano + inmigración).

**Composición**: `{nombre} {apellido}`. Selección uniforme dentro del pool del género.

**Implementación de referencia**: [scripts/sample_name.py](../scripts/sample_name.py) — función `sample(genero)`.

**Pools alternativos por facción/clase**: TBD. La estructura admite `nombres_m_<faccion>.txt` sin tocar el generador.

### 2.4. Sobrenombre — 50% de probabilidad

Cada nombre del pool trae un apodo asignado (`Francisco|Pancho`, `Ignacio|Nacho`, etc.).

- Probabilidad de emitir sobrenombre: **50%** por personaje.
- Si no se emite, el campo queda `null`; el motor puede derivarlo al servir.
- Apodos curados a mano (no existe dataset estructurado público de apodos rioplatenses).

### 2.5. `rol` — default

No se sortea. Arranca con valor `"ciudadano"` (default narrativo de la hoja). El rol operativo emerge después como tag `rol.*` en Fase 4.

### 2.6. `slug` — deferido al motor

No se genera en este paso. El servidor asigna patente `^[A-Z0-9]{8}$` al persistir. En memoria volátil el campo queda `null`.

---

## Fase 3 — Atributos

**Cero aleatoriedad**. Lookup determinista sobre el tag `rango.*` de Fase 1:

| Rango | `fis` | `tac` | `men` | Total |
| :--- | :---: | :---: | :---: | :---: |
| `ciudadano` | 2 | 2 | 2 | 6 |
| `militante` | 2 | 2 | 3 | 7 |
| `recluta` | 3 | 2 | 3 | 8 |
| `fusilero` | 3 | 3 | 3 | 9 |
| `apuntador` | 3 | 4 | 4 | 11 |
| `artillero` | 4 | 4 | 3 | 11 |
| `tirador_designado` | 4 | 5 | 3 | 12 |
| `segundo_al_mando` | 3 | 4 | 5 | 12 |
| `lider_de_escuadra` | 3 | 5 | 6 | 14 |

Topes absolutos:
- `fis 5`
- `tac 6`
- `men 7`

### 3.1. Inmutabilidad práctica

Los atributos quedan **fijos al rango de creación**. Un ascenso posterior cambia el tag `rango.*` pero **no** los atributos: si un cabo asciende a sargento, sus stats no se mueven — el progreso real es el equipo, los perks y los vínculos que junte en el campo. Ver [[hoja-modelo#§8 — Mutabilidad: qué cambia y cómo|hoja-modelo.md §8]].

Mutación posible solo vía hito `triple_cero` o `mejora_atributo` (eventos narrativos costosos).

---

## Fase 4 — Resto
*(Pendiente: tags adicionales, historia prosa, historial, metadatos en el flujo de creación.)*

---

## Reglas — referencia externa

Las restricciones cruzadas entre tags de Fase 1 y campos de Fase 2 (típicamente `genero` y `edad`) viven en la **tabla de reglas del proyecto**, fuera del scope de este GDDR.

El contrato que este flujo asume:

- Existe una tabla consultable que, dado el set de tags decididos en Fase 1, devuelve el set de valores válidos para cada campo restringible de Fase 2.
- El motor consulta la tabla **antes** de sortear cada campo de Fase 2 y aplica el recorte al pool/rango.
- Si la tabla no impone restricción sobre un campo, se usa la distribución por defecto.

Diseño, formato y ubicación de la tabla: ver documento de reglas del proyecto (scope separado).
