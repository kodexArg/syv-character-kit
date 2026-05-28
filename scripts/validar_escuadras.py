#!/usr/bin/env python3
"""
Validación de consistencia para escuadras y personajes.
Verifica que:
1. Las escuadras mock tengan miembros cuyas patentes existan en mock/personajes/.
2. Los personajes de mock tengan los tags 'escuadra.{slug}' y 'lealtad.escuadra.{slug}' correctos.
3. Las posiciones (pos) de los miembros sean consecutivas de 1 a N.
4. El costo de puntos (puntos) coincida con el rango/rol táctico del personaje.
5. Las escuadras cumplan las reglas estructurales de su plantilla (escuadra_de_infanteria).
6. Los campos 'rango' y 'nombre' de la escuadra coincidan con la ficha del personaje.
7. Se calculen correctamente las estadísticas agregadas / derivadas.
"""

import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
MOCK_ESC_DIR = ROOT / "mock" / "escuadras"
MOCK_PJ_DIR = ROOT / "mock" / "personajes"


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_derived_stats(escuadra: dict, miembros_pjs: dict) -> dict:
    miembros = escuadra["miembros"]

    fza_total = 0
    total_men = 0
    total_fatiga = 0
    active_count = 0
    movimientos = []
    lider_candidatos = []
    puntos_totales = sum(m.get("puntos", 0) for m in miembros)

    for m in miembros:
        ref = m["ref"]
        pj = miembros_pjs.get(ref)
        if not pj:
            continue

        tags = pj.get("tags", [])

        # Ignorar si está KIA para cálculos de combate
        is_kia = "estado.kia" in tags
        if is_kia:
            continue

        # Fuerza aportada
        fza = 1
        if "rol.combate.heroe" in tags:
            fza = 3
        elif "rol.combate.lider" in tags:
            fza = 2
        fza_total += fza

        # Para moral (men) y fatiga (fis + men)
        men = pj["atributos"]["men"]
        fis = pj["atributos"]["fis"]
        total_men += men
        total_fatiga += (fis + men)
        active_count += 1

        # Para movimiento (FISICO)
        movimientos.append(fis)

        # Para cadena de mando
        prioridad = 3  # por defecto soldado de infantería
        if "rango.lider_de_escuadra" in tags:
            prioridad = 1
        elif "rango.segundo_al_mando" in tags:
            prioridad = 2
        
        lider_candidatos.append({
            "ref": ref,
            "nombre": pj["identidad"]["nombre"],
            "prioridad": prioridad,
            "edad": pj["identidad"]["edad"]
        })

    # Cohesión/Moral promedio (promedio redondeado hacia abajo)
    moral_promedio = total_men // active_count if active_count > 0 else 0
    fatiga_promedio = total_fatiga // active_count if active_count > 0 else 0

    # Líder vigente y penalidad por decapitación
    lider_candidatos.sort(key=lambda x: (x["prioridad"], -x["edad"]))
    
    lider_vigente = None
    cohesion_vigente = moral_promedio
    penalizacion_lider = 0

    if lider_candidatos:
        lider_vigente = lider_candidatos[0]
        if lider_vigente["prioridad"] == 1:
            pass
        elif lider_vigente["prioridad"] == 2:
            cohesion_vigente -= 1
            penalizacion_lider = -1
        else:
            cohesion_vigente -= 2
            penalizacion_lider = -2
    else:
        cohesion_vigente = 0

    # Movimiento táctico
    movimiento_tactico = min(movimientos) if movimientos else 0

    # Estado de la escuadra
    if active_count == 0:
        estado = "retirada"
    elif fza_total < 8:
        estado = "desmembrada"
    elif lider_vigente and lider_vigente["prioridad"] == 3:
        estado = "decapitada"
    else:
        estado = "operativa"

    return {
        "fza_total": fza_total,
        "cohesion_vigente": max(0, cohesion_vigente),
        "moral_promedio": moral_promedio,
        "fatiga_promedio": fatiga_promedio,
        "penalizacion_lider": penalizacion_lider,
        "movimiento_tactico": movimiento_tactico,
        "puntos_totales": puntos_totales,
        "lider_vigente_nombre": lider_vigente["nombre"] if lider_vigente else "Ninguno",
        "lider_vigente_ref": lider_vigente["ref"] if lider_vigente else None,
        "estado_escuadra": estado,
        "activos": active_count
    }


def validate_infantry_template(escuadra: dict, personajes: dict) -> list:
    errors = []
    miembros = escuadra.get("miembros", [])
    slug_esc = escuadra["identidad"]["slug"]
    
    # 1. Cantidad de miembros
    count = len(miembros)
    if not (5 <= count <= 21):
        errors.append(f"Cantidad de miembros ({count}) fuera del rango reglamentario 5-21.")
    elif count != 11:
        print(f"  - [AVISO] La escuadra no cuenta con el tamaño óptimo de 11 miembros (tiene {count}).")

    # Obtener rangos e información de los miembros
    leaders_count = 0
    regulars_count = 0
    has_artillero = False
    has_apuntador = False
    has_cargador = False
    lider_pos1 = False

    for idx, m in enumerate(miembros):
        ref = m.get("ref")
        pos = m.get("pos")
        puntos_declarados = m.get("puntos")
        rango_declarado = m.get("rango")
        nombre_declarado = m.get("nombre")
        
        pj = personajes.get(ref)
        if not pj:
            continue
            
        tags = pj.get("tags", [])
        
        # Costo esperado en puntos según rango/rol en la escuadra
        puntos_esperados = 1  # default
        if rango_declarado == "lider_de_escuadra":
            puntos_esperados = 5
        elif rango_declarado == "segundo_al_mando" or rango_declarado == "apuntador":
            puntos_esperados = 4
        elif rango_declarado == "artillero" or rango_declarado == "tirador_designado":
            puntos_esperados = 3
        elif rango_declarado == "fusilero":
            puntos_esperados = 2
        elif rango_declarado == "recluta":
            # Si es recargador, cuesta 2 puntos (puesto idéntico al de soldado de segunda)
            if "rol.oficio.recargador" in tags:
                puntos_esperados = 2
            else:
                puntos_esperados = 1
        elif rango_declarado == "militante":
            puntos_esperados = 1
            
        if puntos_declarados != puntos_esperados:
            errors.append(f"Miembro '{pj['identidad']['nombre']}' ({ref}) tiene costo de {puntos_declarados} puntos, pero se esperaban {puntos_esperados} según su rango/rol.")

        # Verificar consistencia de rango declarado
        # El rol de apuntador en la escuadra lo puede tomar un apuntador, un segundo_al_mando (Cabo) o un fusilero
        if rango_declarado == "apuntador":
            compatibles = ("rango.apuntador", "rango.segundo_al_mando", "rango.fusilero")
            if not any(tag in tags for tag in compatibles):
                errors.append(f"Miembro '{pj['identidad']['nombre']}' ({ref}) tiene rol 'apuntador' en la escuadra, pero su rango en ficha no es compatible.")
        else:
            tag_rango_esperado = f"rango.{rango_declarado}"
            if tag_rango_esperado not in tags:
                errors.append(f"Miembro '{pj['identidad']['nombre']}' ({ref}) tiene rango declarado '{rango_declarado}', pero no cuenta con el tag '{tag_rango_esperado}'.")

        # Verificar consistencia de nombre declarado (debe coincidir con nombre o sobrenombre)
        pj_nombre = pj["identidad"]["nombre"]
        pj_sobrenombre = pj["identidad"].get("sobrenombre")
        if nombre_declarado not in (pj_nombre, pj_sobrenombre):
            errors.append(f"Miembro '{pj_nombre}' ({ref}) tiene nombre declarado '{nombre_declarado}', pero en su ficha figura '{pj_nombre}' / '{pj_sobrenombre}'.")

        # Contabilizar para plantilla
        if rango_declarado in ("lider_de_escuadra", "segundo_al_mando"):
            leaders_count += 1
            if idx == 0 and pos == 1 and rango_declarado == "lider_de_escuadra":
                lider_pos1 = True
            
        if rango_declarado in ("fusilero", "militante", "recluta"):
            regulars_count += 1
            
        if rango_declarado == "artillero":
            has_artillero = True
            
        if rango_declarado == "apuntador":
            has_apuntador = True
            
        if "rol.oficio.recargador" in tags or rango_declarado == "recluta":
            has_cargador = True

    # 1. Líder de Unidad en posición 1
    if not lider_pos1:
        errors.append("El Líder de Unidad (lider_de_escuadra) debe estar asignado en la posición 1 de la escuadra.")
        
    # 2. Líderes proporcionales (1 cada 4 infanterías)
    lideres_necesarios = (regulars_count + 3) // 4
    if leaders_count < lideres_necesarios:
        errors.append(f"Liderazgo insuficiente: se requieren al menos {lideres_necesarios} líderes/segundos para {regulars_count} soldados de infantería (se encontraron {leaders_count}).")

    # 3. Estructura de la Ametralladora (Artillero)
    if has_artillero:
        if not has_apuntador:
            errors.append("La escuadra tiene un Artillero (Ametralladora) pero carece de un Apuntador.")
        if not has_cargador:
            errors.append("La escuadra tiene un Artillero (Ametralladora) pero carece de un Cargador (recargador).")
    else:
        errors.append("La escuadra de infantería requiere exactamente 1 Ametralladora (artillero).")

    # 4. Cabo Apuntador
    if not has_apuntador:
        errors.append("La escuadra de infantería requiere al menos 1 Cabo Apuntador (apuntador).")
        
    return errors


def main():
    print("=== Iniciando Validación de Escuadras ===")
    
    # 1. Cargar todos los personajes
    personajes = {}
    for f in MOCK_PJ_DIR.rglob("*.yaml"):
        data = load_yaml(f)
        if "personaje" in data:
            pj = data["personaje"]
            slug = pj["identidad"]["slug"]
            personajes[slug] = pj

    print(f"Cargados {len(personajes)} personajes mock en total.")

    errors = []
    
    # 2. Validar cada escuadra
    escuadras = list(MOCK_ESC_DIR.rglob("*.yaml"))
    if not escuadras:
        print("Error: No se encontraron archivos de escuadras.")
        sys.exit(1)

    for esc_file in sorted(escuadras):
        data = load_yaml(esc_file)
        if "escuadra" not in data:
            errors.append(f"Archivo {esc_file.name} no contiene raíz 'escuadra'.")
            continue

        esc = data["escuadra"]
        ident = esc["identidad"]
        slug_esc = ident["slug"]
        nombre_esc = ident["nombre"]
        faccion_esc = ident["faccion"]
        tipo_esc = ident.get("tipo", "desconocido")
        
        print(f"\nProcesando Escuadra: {nombre_esc} ({slug_esc}) [Tipo: {tipo_esc}]")
        
        # Validar plantilla estructural si es de infantería
        if tipo_esc == "escuadra_de_infanteria":
            temp_errors = validate_infantry_template(esc, personajes)
            errors.extend(temp_errors)
        else:
            errors.append(f"Escuadra {slug_esc} tiene tipo desconocido: {tipo_esc}")
        
        # Validar miembros básicos
        miembros = esc.get("miembros", [])
        posiciones = []
        for idx, m in enumerate(miembros):
            ref = m.get("ref")
            pos = m.get("pos")
            posiciones.append(pos)
            
            if not ref:
                errors.append(f"Miembro en índice {idx} de {slug_esc} no tiene referencia 'ref'.")
                continue
                
            if ref not in personajes:
                errors.append(f"Miembro ref '{ref}' en escuadra {slug_esc} no existe en mock/personajes/.")
                continue
                
            pj = personajes[ref]
            pj_nombre = pj["identidad"]["nombre"]
            pj_tags = pj.get("tags", [])
            
            # Verificar consistencia de tags en el personaje
            tag_esperado = f"escuadra.{slug_esc}"
            tag_lealtad_esperada = f"lealtad.escuadra.{slug_esc}"
            tag_faccion_esperada = f"faccion.{faccion_esc}"
            
            if tag_esperado not in pj_tags:
                errors.append(f"Personaje '{pj_nombre}' ({ref}) pertenece a escuadra {slug_esc} pero no tiene tag '{tag_esperado}'.")
            if tag_lealtad_esperada not in pj_tags:
                errors.append(f"Personaje '{pj_nombre}' ({ref}) pertenece a escuadra {slug_esc} pero no tiene tag '{tag_lealtad_esperada}'.")
            if tag_faccion_esperada not in pj_tags:
                errors.append(f"Personaje '{pj_nombre}' ({ref}) tiene facción {faccion_esc} en escuadra pero no tiene tag '{tag_faccion_esperada}'.")

        # Validar posiciones consecutivas 1..N
        posiciones.sort()
        esperadas = list(range(1, len(miembros) + 1))
        if posiciones != esperadas:
            errors.append(f"Las posiciones de la escuadra {slug_esc} no son consecutivas del 1 al {len(miembros)}: {posiciones}")

        # Calcular y reportar estadísticas
        stats = calculate_derived_stats(esc, personajes)
        print(f"  - Miembros activos: {stats['activos']}/{len(miembros)}")
        print(f"  - Puntos Totales: {stats['puntos_totales']}")
        print(f"  - Fuerza Total (FZA): {stats['fza_total']}")
        print(f"  - Moral/Cohesión Promedio: {stats['moral_promedio']} (Vigente: {stats['cohesion_vigente']}, Penalidad: {stats['penalizacion_lider']})")
        print(f"  - Fatiga Promedio: {stats['fatiga_promedio']}")
        print(f"  - Movimiento Táctico: {stats['movimiento_tactico']}")
        print(f"  - Líder Vigente: {stats['lider_vigente_nombre']} ({stats['lider_vigente_ref']})")
        print(f"  - Estado de Escuadra: {stats['estado_escuadra'].upper()}")

    # 3. Validar personajes "huérfanos" (con tag escuadra.* pero que no están en el archivo de la escuadra)
    # y asegurar que todos los personajes de las escuadras canon estén asignados.
    for ref, pj in personajes.items():
        pj_tags = pj.get("tags", [])
        esc_tags = [t.partition(".")[2] for t in pj_tags if t.startswith("escuadra.")]
        
        # Ignorar NPCs que no forman parte del roster de 22
        if "npc" in pj.get("identidad", {}).get("rol", "").lower():
            continue
        # Ignorar si es el sargento postmortem
        if ref == "RS0P2M7N":
            continue

        for e_slug in esc_tags:
            # Buscar si el personaje está en el archivo yaml de la escuadra correspondiente
            esc_file_path = MOCK_ESC_DIR / ("confederacion" if "faccion.confederados" in pj_tags else "ejercito_rojo") / f"{e_slug}.yaml"
            if not esc_file_path.exists():
                # fallback simple en caso de que no esté en la subcarpeta esperada
                esc_file_path = MOCK_ESC_DIR / f"{e_slug}.yaml"
                
            if not esc_file_path.exists():
                errors.append(f"Personaje '{pj['identidad']['nombre']}' ({ref}) tiene tag escuadra.{e_slug} pero el archivo de escuadra no existe.")
                continue
                
            esc_data = load_yaml(esc_file_path)
            miembros_refs = [m["ref"] for m in esc_data["escuadra"]["miembros"]]
            if ref not in miembros_refs:
                errors.append(f"Personaje '{pj['identidad']['nombre']}' ({ref}) tiene tag escuadra.{e_slug} pero no está listado en {esc_file_path.name}.")

    print("\n=== Resultado de la Validación ===")
    if errors:
        print(f"SE ENCONTRARON {len(errors)} ERRORES:")
        for err in errors:
            print(f"  - [ERROR] {err}")
        sys.exit(1)
    else:
        print("¡VALIDACIÓN EXITOSA! Todos los archivos son consistentes.")
        sys.exit(0)


if __name__ == "__main__":
    main()
