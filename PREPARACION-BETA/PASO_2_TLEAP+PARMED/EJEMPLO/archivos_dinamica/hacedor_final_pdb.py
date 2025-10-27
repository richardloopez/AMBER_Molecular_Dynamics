import os




def combinar_estructuras_y_actualizar_atomtypes(
    pdb_referencia_path,
    pdb_ligando_path,
    mol2_path,
    abreviatura_ligando,
    nuevo_pdb_nombre="complejo_final.pdb"
):
    """
    Combina un PDB de referencia con las coordenadas de un ligando de otro PDB,
    actualiza los atomtypes y asegura que las líneas TER (con NOU) se mantengan
    y se les actualice el nombre del residuo.

    Args:
        pdb_referencia_path (str): Ruta al archivo PDB de referencia.
        pdb_ligando_path (str): Ruta al archivo PDB del ligando.
        mol2_path (str): Ruta al archivo MOL2 para extraer los atomtypes.
        abreviatura_ligando (str): La abreviatura del ligando (ej: "LIG").
        nuevo_pdb_nombre (str): Nombre del archivo PDB de salida.
    """
    
    # --- 1. Procesar el PDB del Ligando y obtener los datos "UNL" ---
    try:
        with open(pdb_ligando_path, 'r') as f:
            lineas_ligando = f.readlines()
    except FileNotFoundError:
        print(f"Error: Archivo de ligando '{pdb_ligando_path}' no encontrado.")
        return

    ligando_unl_lines = []
    for linea in lineas_ligando:
        if linea.startswith(("ATOM", "HETATM")):
            residuo = linea[17:20].strip()
            if residuo == "UNL":
                ligando_unl_lines.append(linea)

    num_ligando_atoms = len(ligando_unl_lines)
    if num_ligando_atoms == 0:
        print("Advertencia: No se encontraron residuos 'UNL' en el PDB del ligando. Proceso detenido.")
        return
        
    # --- 2. Procesar el MOL2 y obtener los Atomtypes ---
    try:
        with open(mol2_path, 'r') as f:
            lineas_mol2 = f.readlines()
    except FileNotFoundError:
        print(f"Error: Archivo MOL2 '{mol2_path}' no encontrado.")
        return

    atomtypes = []
    is_atom_section = False
    
    for linea in lineas_mol2:
        if linea.strip().startswith("@<TRIPOS>ATOM"):
            is_atom_section = True
            continue
        
        if linea.strip().startswith("@<TRIPOS>BOND"):
            is_atom_section = False
            break
        
        if is_atom_section:
            campos = linea.strip().split()
            if len(campos) > 1:
                atomtypes.append(campos[1])

    num_atomtypes = len(atomtypes)
    
    # Validación Crítica: Coincidencia de número de átomos
    if num_ligando_atoms != num_atomtypes:
        print(f"\n❌ ERROR CRÍTICO: Discrepancia en el número de átomos y atomtypes.")
        print(f"   Átomos UNL en PDB de ligando: {num_ligando_atoms}")
        print(f"   Atomtypes en MOL2: {num_atomtypes}")
        print("   El código se detiene para evitar errores en el PDB de salida.")
        return

    # --- 3. Procesar el PDB de Referencia y realizar la sustitución ---
    try:
        with open(pdb_referencia_path, 'r') as f:
            lineas_referencia = f.readlines()
    except FileNotFoundError:
        print(f"Error: Archivo de referencia '{pdb_referencia_path}' no encontrado.")
        return

    nuevo_pdb_contenido = []
    primer_nou_indice = -1
    
    # Índices de las líneas ATOM/HETATM "NOU" que deben eliminarse
    indices_atom_nou_a_eliminar = []
    
    # Bucle para identificar qué hacer con cada línea
    for i, linea in enumerate(lineas_referencia):
        if len(linea) >= 20: 
            residuo_en_linea = linea[17:20].strip()
            
            if residuo_en_linea == "NOU":
                # Si es un átomo, se marca para eliminación (y si es el primero, se marca como punto de inserción)
                if linea.startswith(("ATOM", "HETATM")):
                    if primer_nou_indice == -1:
                        primer_nou_indice = i
                    indices_atom_nou_a_eliminar.append(i)
                
                # Si es una línea TER, se modifica el residuo y se añade al nuevo contenido
                elif linea.startswith("TER"):
                    # Reemplazar 'NOU' por la abreviatura_ligando.ljust(3) en las posiciones 18-20
                    linea_modificada = linea[:17] + abreviatura_ligando.ljust(3) + linea[20:]
                    # Solo añadimos TER si no hemos pasado el punto de inserción
                    # Si ya insertamos los átomos, se añade al final de la inserción
                    if primer_nou_indice == -1:
                         nuevo_pdb_contenido.append(linea_modificada)
                    # Si ya estamos en el bucle de construcción, se añade después del reemplazo
                    # La lógica de inserción manejará esto más tarde.

    if primer_nou_indice == -1:
        print("Advertencia: No se encontraron residuos ATOM/HETATM 'NOU' en el PDB de referencia. El ligando se añadirá al final.")
    
    # Construir el nuevo PDB
    i = 0
    while i < len(lineas_referencia):
        linea = lineas_referencia[i]
        
        # 1. Punto de inserción
        if i == primer_nou_indice:
            
            # Insertar todas las líneas del ligando con los cambios de formato
            for j, ligando_linea in enumerate(ligando_unl_lines):
                # Sustituir "UNL" por la abreviatura
                linea_modificada = ligando_linea[:17] + abreviatura_ligando.ljust(3) + ligando_linea[20:]
                
                # Sustituir el tipo de átomo (columna 3, posiciones 13-16) por el atomtype
                atomtype_a_aplicar = atomtypes[j].ljust(4)
                linea_modificada = linea_modificada[:12] + atomtype_a_aplicar + linea_modificada[16:]
                
                nuevo_pdb_contenido.append(linea_modificada)

            # Saltar las líneas ATOM/HETATM NOU que fueron reemplazadas
            if indices_atom_nou_a_eliminar:
                i = indices_atom_nou_a_eliminar[-1] + 1
            else:
                i += 1
            
        # 2. Línea NOU-TER que debe ser renombrada y mantenida
        elif linea.startswith("TER") and len(linea) >= 20 and linea[17:20].strip() == "NOU":
            # Reemplazar 'NOU' por la abreviatura y añadir al contenido
            linea_modificada = linea[:17] + abreviatura_ligando.ljust(3) + linea[20:]
            nuevo_pdb_contenido.append(linea_modificada)
            i += 1
            
        # 3. Línea ATOM/HETATM NOU que debe ser eliminada (si no es el punto de inserción)
        elif i in indices_atom_nou_a_eliminar:
            i += 1
            
        # 4. Línea normal (ATOM/HETATM no NOU, cabecera, etc.)
        else:
            nuevo_pdb_contenido.append(linea)
            i += 1


    # Caso especial: Si no había NOU, se inserta al final.
    if primer_nou_indice == -1:
         for j, ligando_linea in enumerate(ligando_unl_lines):
            linea_modificada = ligando_linea[:17] + abreviatura_ligando.ljust(3) + ligando_linea[20:]
            atomtype_a_aplicar = atomtypes[j].ljust(4)
            linea_modificada = linea_modificada[:12] + atomtype_a_aplicar + linea_modificada[16:]
            nuevo_pdb_contenido.append(linea_modificada)
            

    # --- 4. Escribir el nuevo archivo PDB ---
    try:
        with open(nuevo_pdb_nombre, 'w') as f:
            f.writelines(nuevo_pdb_contenido)
        print(f"\n✅ Éxito: Archivo generado '{nuevo_pdb_nombre}'.")
        print(f"   {num_ligando_atoms} átomos de ligando ('{abreviatura_ligando}') insertados.")
    except Exception as e:
        print(f"Error al escribir el archivo '{nuevo_pdb_nombre}': {e}")




# --- EJEMPLO DE USO ---

# Variables de entrada
PDB_REF = "ANT_BUENO.pdb"
PDB_LIG = "S2_IO_14_E.pdb"
MOL2_FILE = "S2_IO_14_E.mol2"
ABREVIATURA = "S2X"
# Variable de salida (Punto de la solicitud)
OUTPUT_PDB = "S2_IO_14_E+ANT.pdb"
# Descomentar para ejecutar:
combinar_estructuras_y_actualizar_atomtypes(
     PDB_REF,
     PDB_LIG,
     MOL2_FILE,
     ABREVIATURA,
     OUTPUT_PDB
 )

print("Script cargado. Descomenta las últimas líneas para ejecutar el ejemplo.")