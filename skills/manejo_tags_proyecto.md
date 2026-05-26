# Skill: Manejo y Visualización de Tags en syv-character-kit

Este skill describe las convenciones para el uso de tags dentro del proyecto y cómo interactúan con la visualización en Obsidian (Graph View). Debe ser consultado por cualquier agente de IA (como Claude o Gemini) al crear, modificar o procesar fichas de personajes, catálogos de tags o al configurar la visualización en Obsidian.

## Convenciones de Tags del Proyecto
1. **Formato Canónico en YAML:** 
   Los tags dentro de los archivos de personajes (`mock/personajes/`) y los catálogos de tags (`tags/`) **deben** escribirse siempre usando **notación punto**:
   `<categoria>[.<subcategoria>].<slug>`
   Ejemplos: `faccion.ejercito_rojo`, `rango.lider_de_escuadra`, `rasgo.alto`.
   *Nunca* usar corchetes de Obsidian `[[...]]` ni caracteres `#` dentro de los archivos YAML.

2. **Formato en Obsidian (Graph View):**
   Para que Obsidian pueda graficar y relacionar estos tags y personajes de forma nativa en su vista de gráfico sin alterar la portabilidad del YAML canónico, se realiza una conversión a notas Markdown espejo temporales:
   * La notación punto se mapea a la jerarquía de sub-tags de Obsidian reemplazando los puntos por barras diagonales: `#categoria/sub/slug`.
     * Ejemplo: `faccion.ejercito_rojo` $\rightarrow$ `#faccion/ejercito_rojo`.
   * Las referencias de relación (como aliados o némesis representados por slugs: `ref: WA3K9F2H`) se mapean a enlaces internos tradicionales de Obsidian: `[[Nombre del Personaje (SLUG)]]`.

## Instrucciones para el Agente de IA
* **Validación en YAML:** Al crear o modificar archivos YAML del proyecto, asegurá que todos los tags sigan estrictamente la notación punto.
* **Visualización en Obsidian:** Cuando el usuario pida ver o graficar relaciones en Obsidian, no intentes meter sintaxis de Obsidian dentro de los archivos `.yaml` originales. En su lugar, utilizá el script de automatización (`scripts/generar_grafo_obsidian.py`) para generar las vistas Markdown espejo dentro de un directorio oculto o ignorado por git (como `.vistas_obsidian/`), permitiendo que el Graph View funcione sin alterar el canon de datos.
