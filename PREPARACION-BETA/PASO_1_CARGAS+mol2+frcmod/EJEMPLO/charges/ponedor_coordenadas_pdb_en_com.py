import os

def generar_com_desde_pdb(archivo_com_base, archivo_pdb, linea_ref="0 1"):
    """
    Genera un nuevo archivo .com para Gaussian a partir de la cabecera del archivo .com_base
    y las coordenadas filtradas del archivo .pdb, incluyendo la línea en blanco OBLIGATORIA al final.

    Args:
        archivo_com_base (str): Nombre del archivo .com de donde tomar la cabecera.
        archivo_pdb (str): Nombre del archivo .pdb de donde extraer los datos.
        linea_ref (str): La línea de referencia en el .com (ej: "0 1").
    """
    # 1. Determinar el nombre del nuevo archivo .com
    nombre_base = os.path.splitext(archivo_pdb)[0]
    nuevo_archivo_com = f"{nombre_base}.com"

    # 2. Procesar el archivo .pdb para obtener las coordenadas filtradas
    try:
        with open(archivo_pdb, 'r') as f:
            lineas_pdb = f.readlines()
    except FileNotFoundError:
        print(f"Error: El archivo PDB '{archivo_pdb}' no se encontró.")
        return

    datos_filtrados = []
    
    for linea in lineas_pdb:
        if linea.startswith(("ATOM", "HETATM")):
            try:
                residuo = linea[17:20].strip()

                if residuo == "UNL":
                    # Columna 12 (Símbolo atómico): 4 caracteres
                    simbolo = linea[76:80].strip()

                    # Coordenadas (X, Y, Z)
                    x = float(linea[30:38].strip())
                    y = float(linea[38:46].strip())
                    z = float(linea[46:54].strip())

                    # Formato: Símbolo con 4 caracteres y 3 decimales
                    datos_filtrados.append(f"{simbolo:<4}{x:8.3f} {y:8.3f} {z:8.3f}")

            except ValueError:
                continue
            except IndexError:
                continue

    # 3. Leer y preparar la cabecera del archivo .com original
    try:
        with open(archivo_com_base, 'r') as f:
            contenido_com = f.readlines()
    except FileNotFoundError:
        print(f"Error: El archivo COM base '{archivo_com_base}' no se encontró.")
        return

    # Encontrar la línea de referencia (ej: "0 1")
    indice_referencia = -1
    for i, linea in enumerate(contenido_com):
        if linea_ref.strip() in linea.strip():
            indice_referencia = i
            break

    if indice_referencia == -1:
        print(f"Advertencia: No se encontró la línea de referencia '{linea_ref}' en el .com base. No se generó el archivo.")
        return

    # 4. Construir el nuevo contenido .com
    # Conservar la cabecera hasta (e incluyendo) la línea de referencia
    nuevo_contenido_com = contenido_com[:indice_referencia + 1]
    
    # Añadir las coordenadas (sin línea en blanco entre 0 1 y la molécula)
    # Nota: Ya hemos asegurado que cada línea de coordenada termine en "\n"
    nuevo_contenido_com.extend([linea_datos + "\n" for linea_datos in datos_filtrados])

    # 🔑 MODIFICACIÓN CLAVE PARA GAUSSIAN: Añadir una línea en blanco al final del archivo.
    # Si la última línea no es ya un salto de línea (como debería ser),
    # añadimos un salto de línea adicional.
    if not nuevo_contenido_com[-1].endswith('\n'):
        nuevo_contenido_com.append('\n') # Asegura que la última coordenada termine en un salto de línea
    
    nuevo_contenido_com.append('\n') # Esta es la línea en blanco obligatoria de Gaussian

    # 5. Escribir el nuevo archivo .com
    try:
        with open(nuevo_archivo_com, 'w') as f:
            f.writelines(nuevo_contenido_com)
        print(f"✅ Éxito: Se ha generado el nuevo archivo de entrada para Gaussian: '{nuevo_archivo_com}'.")
        print(f"   Se incluyeron {len(datos_filtrados)} átomos 'UNL' con la línea final obligatoria.")
    except Exception as e:
        print(f"Error al escribir el archivo '{nuevo_archivo_com}': {e}")


# --- Ejemplo de Uso ---
nombre_com_base = "nada.com"
nombre_pdb = "pdb_ligando_con_H_y_receptor_sin_K.pdb"
linea_carga_spin = "0 1"
generar_com_desde_pdb(nombre_com_base, nombre_pdb, linea_carga_spin)
