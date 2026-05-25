# Modelo de Azar — Mecánica de tiradas

> **Estado**: rolling release; este documento describe la regla vigente de aleatorización.
> **Propósito**: definir el comportamiento conceptual de las tiradas de dados para la resolución de acciones en el sistema.

---

## §1 — La tirada base (3d10 Mediana)

La resolución estándar de cualquier acción que requiera azar se basa en comparar el valor de un atributo (como `fis`, `tac` o `men`) contra el resultado de lanzar tres dados de diez caras (3d10).

El valor representativo de la tirada no es la suma de los dados, sino su **mediana** (el valor central al ordenarlos de menor a mayor). Para superar la prueba, el valor de la mediana obtenido debe estar por abajo (menor o igual) del atributo a comparar.

*   **Ejemplo base**:
    *   Si tenés un atributo de FÍSICO (`fis`) con valor 3.
    *   Hacés la tirada de dados y obtenés `[3, 5, 1]`.
    *   Al ordenar los valores, el resultado de la mediana es **3**.
    *   Como 3 es menor o igual al atributo a comparar (3), superás la tirada.

---

## §2 — Variaciones de la tirada (Menor y Mayor)

Dependiendo del contexto táctico, de la preparación del personaje o de su estado de salud, el sistema puede demandar evaluar un dado distinto de la mediana. Esto introduce desventajas o ventajas situacionales sin alterar el número de dados lanzados.

### 2.1. Exigencia del dado MENOR (Desventaja)
En situaciones de desventaja extrema, fatiga o falta de entrenamiento, el sistema extrae el valor del dado **menor** de la tirada en lugar de la mediana. Esto reduce drásticamente las probabilidades de éxito, al requerir que incluso el resultado más bajo sea suficiente para superar el atributo.

*   **Ejemplos de aplicación**:
    *   Un personaje herido disparando bajo presión.
    *   Un colimba disparando una ametralladora.

### 2.2. Exigencia del dado MAYOR (Ventaja)
En condiciones ideales, especialización extrema o preparación táctica minuciosa, el sistema permite extraer el valor del dado **mayor** de la tirada de 3d10. Esto eleva de forma significativa la probabilidad de superar el atributo.

*   **Ejemplos de aplicación**:
    *   Un francotirador disparando en el hexágono con el dado mayor.

---

## §3 — Dirección de diseño (Indicios)

Esta mecánica busca capturar de forma cualitativa las diferencias entre la mediocridad del combate caótico (donde la mediana es la norma), la torpeza bajo estrés o falta de instrucción (dado menor) y la precisión quirúrgica o ventajas tácticas de preparación (dado mayor).

No es objeto de este documento detallar el análisis probabilístico de la curva ni la implementación de fórmulas específicas, sino fijar la intención mecánica del sistema para su posterior modelado.
