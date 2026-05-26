#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import glob
import yaml

# Rutas del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONAJES_DIR = os.path.join(BASE_DIR, 'mock', 'personajes')
TAGS_DIR = os.path.join(BASE_DIR, 'tags')
OUTPUT_DIR = os.path.join(BASE_DIR, '.vistas_obsidian')

def get_tag_dictionary(tags_dir):
    """
    Lee recursivamente el directorio de tags y genera un diccionario
    con clave 'categoria.subcategoria.slug' y valor {'nombre', 'descripcion'}.
    """
    tag_dict = {}
    pattern = os.path.join(tags_dir, '**', '*.yaml')
    files = glob.glob(pattern, recursive=True) + glob.glob(os.path.join(tags_dir, '**', '*.yml'), recursive=True)
    
    for file_path in files:
        # Calcular el key en notación punto basado en la ruta relativa
        rel_path = os.path.relpath(file_path, tags_dir)
        tag_key = os.path.splitext(rel_path)[0].replace(os.sep, '.')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and 'tag' in data:
                    t = data['tag']
                    tag_dict[tag_key] = {
                        'nombre': t.get('nombre', tag_key),
                        'descripcion': t.get('descripcion', '').strip()
                    }
        except Exception as e:
            print(f"Error parseando tag {file_path}: {e}")
    return tag_dict

def get_characters(personajes_dir):
    """
    Lee recursivamente todos los personajes en mock/personajes/ y los organiza por slug.
    """
    characters = {}
    pattern = os.path.join(personajes_dir, '**', '*.yaml')
    files = glob.glob(pattern, recursive=True) + glob.glob(os.path.join(personajes_dir, '**', '*.yml'), recursive=True)
    
    for file_path in files:
        rel_path = os.path.relpath(file_path, personajes_dir)
        folder = os.path.dirname(rel_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and 'personaje' in data:
                    p = data['personaje']
                    identidad = p.get('identidad', {})
                    slug = identidad.get('slug')
                    if slug:
                        characters[slug] = {
                            'identidad': identidad,
                            'atributos': p.get('atributos', {}),
                            'tags': p.get('tags', []),
                            'historia': p.get('historia', ''),
                            'historial': p.get('historial', []),
                            'aliados': p.get('aliados', []),
                            'nemesis': p.get('nemesis', []),
                            'metadatos': p.get('metadatos', {}),
                            'extras': p.get('extras'),
                            'folder': folder,
                            'original_file': file_path
                        }
        except Exception as e:
            print(f"Error parseando personaje {file_path}: {e}")
    return characters

def format_obsidian_tag(tag_str):
    """
    Convierte 'faccion.ejercito_rojo' a 'faccion/ejercito_rojo'.
    """
    return tag_str.replace('.', '/')

def generate_obsidian_views():
    print("Iniciando generación de vistas para Obsidian...")
    
    # 1. Obtener datos
    tags_db = get_tag_dictionary(TAGS_DIR)
    chars_db = get_characters(PERSONAJES_DIR)
    
    print(f"Cargados {len(tags_db)} tags y {len(chars_db)} personajes.")
    
    # Mapeo de slug -> nombre de nota en Obsidian
    slug_to_note_title = {}
    for slug, char in chars_db.items():
        nombre = char['identidad'].get('nombre', 'Desconocido')
        slug_to_note_title[slug] = f"{nombre} ({slug})"
    
    # 2. Limpiar directorio de salida
    if os.path.exists(OUTPUT_DIR):
        print(f"Limpiando directorio existente: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 3. Crear glosario de tags
    glosario_path = os.path.join(OUTPUT_DIR, "Glosario de Tags.md")
    with open(glosario_path, 'w', encoding='utf-8') as gf:
        gf.write("# Glosario de Tags - Subordinación y Valor\n\n")
        gf.write("Este glosario contiene la descripción y taxonomía de todos los tags del catálogo.\n\n")
        
        # Agrupar tags por categoría principal (primer elemento de la notación punto)
        categories = {}
        for tag_key, info in sorted(tags_db.items()):
            parts = tag_key.split('.')
            cat = parts[0].capitalize()
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((tag_key, info))
            
        for cat, tags in sorted(categories.items()):
            gf.write(f"## {cat}\n\n")
            for key, info in tags:
                obs_tag = format_obsidian_tag(key)
                gf.write(f"- **#{obs_tag}** ({info['nombre']}): {info['descripcion']}\n")
            gf.write("\n")
            
    print(f"Creado Glosario de Tags en: {glosario_path}")

    # 4. Crear notas de personajes
    for slug, char in chars_db.items():
        identidad = char['identidad']
        atributos = char['atributos']
        tags = char['tags']
        historia = char['historia']
        historial = char['historial']
        aliados = char['aliados']
        nemesis = char['nemesis']
        folder = char['folder']
        
        note_title = slug_to_note_title[slug]
        
        # Determinar carpeta de destino en vistas
        dest_folder = os.path.join(OUTPUT_DIR, folder) if folder else OUTPUT_DIR
        os.makedirs(dest_folder, exist_ok=True)
        
        file_path = os.path.join(dest_folder, f"{note_title}.md")
        
        # Construir Frontmatter YAML
        frontmatter = {
            "slug": slug,
            "nombre": identidad.get("nombre"),
            "sobrenombre": identidad.get("sobrenombre"),
            "rol": identidad.get("rol"),
            "genero": identidad.get("genero"),
            "edad": identidad.get("edad"),
            "fis": atributos.get("fis"),
            "tac": atributos.get("tac"),
            "men": atributos.get("men"),
            "tags": [format_obsidian_tag(t) for t in tags]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Escribir frontmatter
            f.write("---\n")
            yaml.dump(frontmatter, f, allow_unicode=True, default_flow_style=False)
            f.write("---\n\n")
            
            # Título principal
            f.write(f"# {identidad.get('nombre')} ({slug})\n\n")
            
            # Ficha visual usando Callouts de Obsidian
            f.write("> [!INFO] **Identidad**\n")
            if identidad.get('sobrenombre'):
                f.write(f"> - **Sobrenombre:** {identidad.get('sobrenombre')}\n")
            f.write(f"> - **Rol:** {identidad.get('rol')}\n")
            f.write(f"> - **Género:** {identidad.get('genero')} | **Edad:** {identidad.get('edad')} años\n")
            f.write(">\n")
            f.write("> | FÍSICO | TÁCTICO | MENTAL |\n")
            f.write("> | :---: | :---: | :---: |\n")
            f.write(f"> | **{atributos.get('fis')}** | **{atributos.get('tac')}** | **{atributos.get('men')}** |\n\n")
            
            # Historia
            if historia:
                f.write("## Historia\n\n")
                # Formatear como bloque de cita estilizado
                history_lines = historia.split('\n')
                f.write("> [!QUOTE] Trasfondo\n")
                for line in history_lines:
                    if line.strip():
                        f.write(f"> {line.strip()}\n")
                f.write("\n")
                
            # Relaciones (Aliados y Némesis)
            if aliados or nemesis:
                f.write("## Relaciones\n\n")
                
                if aliados:
                    f.write("### Aliados\n")
                    for ally in aliados:
                        ref_slug = ally.get('ref')
                        desc = ally.get('descripcion', '').strip()
                        desde = ally.get('desde', '')
                        desde_str = f" (desde {desde})" if desde else ""
                        
                        target_title = slug_to_note_title.get(ref_slug)
                        if target_title:
                            f.write(f"- **[[{target_title}|{chars_db[ref_slug]['identidad']['nombre']}]]**{desde_str}: {desc}\n")
                        else:
                            f.write(f"- **{ref_slug}** (Desconocido){desde_str}: {desc}\n")
                    f.write("\n")
                    
                if nemesis:
                    f.write("### Némesis\n")
                    for nem in nemesis:
                        ref_slug = nem.get('ref')
                        desc = nem.get('descripcion', '').strip()
                        desde = nem.get('desde', '')
                        desde_str = f" (desde {desde})" if desde else ""
                        
                        target_title = slug_to_note_title.get(ref_slug)
                        if target_title:
                            f.write(f"- **[[{target_title}|{chars_db[ref_slug]['identidad']['nombre']}]]**{desde_str}: {desc}\n")
                        else:
                            f.write(f"- **{ref_slug}** (Desconocido){desde_str}: {desc}\n")
                    f.write("\n")
            
            # Historial
            if historial:
                f.write("## Historial y Cronología\n\n")
                for event in historial:
                    fecha = event.get('fecha', '')
                    tipo = event.get('tipo', '').replace('_', ' ').capitalize()
                    desc = event.get('descripcion', '').strip()
                    meta = event.get('metadata', {})
                    ref = meta.get('ref') if meta else None
                    
                    # Formato legible de fecha (quitar T y Z si es posible)
                    fecha_str = fecha.split('T')[0] if 'T' in fecha else fecha
                    
                    # Traducir referencia en el historial si la hay
                    ref_link = ""
                    if ref:
                        target_title = slug_to_note_title.get(ref)
                        if target_title:
                            ref_link = f" (Ref: [[{target_title}|{chars_db[ref]['identidad']['nombre']}]])"
                        else:
                            ref_link = f" (Ref: {ref})"
                            
                    f.write(f"### {fecha_str} — *{tipo}*\n")
                    f.write(f"{desc}{ref_link}\n\n")
                    
                    # Metadatos extra del evento
                    if meta:
                        other_metas = [f"**{k}**: {v}" for k, v in meta.items() if k != 'ref']
                        if other_metas:
                            f.write(f"*(Detalles: {', '.join(other_metas)})*\n\n")
            
            # Enlaces de Tags nativos al final de la nota
            f.write("## Tags del Personaje\n\n")
            obs_tags = [f"#{format_obsidian_tag(t)}" for t in tags]
            f.write(" ".join(obs_tags) + "\n")
            
    print("Vistas generadas exitosamente en .vistas_obsidian/")

if __name__ == "__main__":
    generate_obsidian_views()
