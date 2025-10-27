import os
import re
import time
import subprocess
import sys


NOMBRE_LIGANDO = "S1_II_1_E"

# --- Definiciones de archivos y variables principales ---
FILE_TO_MODIFY_PONER_COORDENADAS_COM = "ponedor_coordenadas_pdb_en_com.py"
LOG_FILE = f"{NOMBRE_LIGANDO}.log"
COM_FILE = f"{NOMBRE_LIGANDO}.com"
PDB_FILE = f"{NOMBRE_LIGANDO}.pdb"
MOL2_FILE = f"{NOMBRE_LIGANDO}.mol2"
FRCMOD_FILE = f"{NOMBRE_LIGANDO}.frcmod"

# Variables para la fase de Gaussian
NOMBRE_COM_BASE = "nada.com"
NOMBRE_PDB_BASE = f"{NOMBRE_LIGANDO}.pdb"

# Variables para la fase de Antechamber y Parmchk2
ABREVIATURA = "S1X" # ¡IMPORTANTE! Se define como cadena de texto. ###################
CARGA_NETA = 0 ################# CUIDADO!! ESTA CARGA SOLO SE USA EN ANTECHAMBER: PARA GAUSSIAN EL "nada.com" debe tener carga y multiplicidad correctas

# Variables para la fase de Dinámica (archivos_dinamica)
HACEDOR_FINAL_PDB_SCRIPT = "hacedor_final_pdb.py"
PDB_REF_VALUE = "HB1_BUENO.pdb" ################################
FINAL_PDB_VALUE = f"{NOMBRE_LIGANDO}+HB1.pdb" ################################
LEAP_IN_FILE_ORIGINAL = "primigenio_leap.in"
LEAP_IN_FILE_OUTPUT = "tleap.in"
ABREVIATURA = ABREVIATURA


def replace_in_file(filepath, variable_name, new_value):
    """
    Función genérica para reemplazar el valor (el string entre comillas) 
    de una variable específica en un archivo.
    Similar a 'sed -i' para asignaciones de variables Python.
    """
    try:
        # 1. Leer el contenido del archivo
        with open(filepath, 'r') as file:
            content = file.read()
        
        # 2. Definir la expresión regular de búsqueda
        # Busca: ^[espacios]variable_name[espacios]=[espacios]"cualquier_cosa"[espacios]$
        # El re.escape maneja caracteres especiales en el nombre de la variable.
        search_regex = re.compile(
            rf'^\s*{re.escape(variable_name)}\s*=\s*".*?"\s*$', 
            re.MULTILINE
        )
        
        # 3. Definir la línea de reemplazo
        replacement_line = f'{variable_name} = "{new_value}"'
        
        # 4. Realizar el reemplazo (solo la primera coincidencia por seguridad)
        new_content = search_regex.sub(replacement_line, content, count=1)
        
        # 5. Escribir el nuevo contenido de vuelta al archivo
        if new_content == content:
            print(f"Advertencia: No se encontró la variable '{variable_name}' para reemplazar en '{filepath}'.")
        else:
            with open(filepath, 'w') as file:
                file.write(new_content)
            print(f"Reemplazo de '{variable_name}' por '{new_value}' en '{filepath}' completado.")
        
    except FileNotFoundError:
        print(f"Error: El archivo '{filepath}' no fue encontrado. Compruebe la ruta.")
        sys.exit(1)
    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo '{filepath}': {e}")
        sys.exit(1)


def execute_shell_command(command, wait=True):
    """
    Ejecuta un comando de shell.
    Usa subprocess.run (espera) o subprocess.Popen (segundo plano, como '&').
    """
    print(f"\nEjecutando: {command}")
    
    if not wait:
        try:
            # Ejecución en segundo plano (para 'launch_g16 &')
            process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
            print(f"Proceso iniciado en segundo plano (PID: {process.pid}).")
            return process
        except Exception as e:
            print(f"Error al ejecutar el comando en segundo plano: {e}")
            return None
    
    try:
        # Ejecución síncrona (espera a que termine)
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=False)
        print("Comando ejecutado con éxito.")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
        # print("stderr:", e.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: El comando o archivo no fue encontrado. Comando: '{command.split()[0]}'")
        return None


def wait_for_gaussian_log():
    """
    Espera a que se cree el archivo .log y a que Gaussian indique
    la terminación normal.
    """
    print(f"\nEsperando a que aparezca el archivo de log: {LOG_FILE}...")
    
    # 1. Esperar a que exista el .log
    while not os.path.exists(LOG_FILE):
        print("... Log no encontrado. Esperando 1 segundo.")
        time.sleep(1)

    print(f"Archivo de log '{LOG_FILE}' encontrado.")

    # 2. Esperar a que el log termine ("Normal termination")
    print("Esperando a 'Normal termination of Gaussian' en el log...")
    while True:
        try:
            # Abrir y leer todo el contenido
            with open(LOG_FILE, 'r') as f:
                content = f.read()
                if "Normal termination of Gaussian" in content:
                    print("¡Gaussian terminado correctamente!")
                    break
        except Exception as e:
            # Capturar errores de IO si el archivo se está escribiendo
            print(f"Error de lectura del log: {e}. Reintentando en 1s.")
            pass
        
        print("... Log incompleto. Esperando 1 segundo.")
        time.sleep(1)


def process_leap_file(input_filepath, output_filepath, abbreviation, mol2, frcmod, final_pdb):
    """
    Lee el archivo de entrada de leap ('primigenio_leap.in'), realiza las sustituciones 
    de variables específicas ({ABREVIATURA}, {MOL2_FILE}, etc.) en las líneas
    correspondientes, y escribe el resultado en el nuevo archivo de salida ('tleap.in').
    """
    print(f"Procesando plantillas de LEAP: {input_filepath} -> {output_filepath}")
    try:
        with open(input_filepath, 'r') as infile:
            content = infile.read()
            
        # Expresiones regulares para los reemplazos.
        # Capturamos el comentario (#...) al final de la línea para preservarlo (\1).

        # 1. S1X=loadmol2 S1_IO_4_GD.mol2 ######### -> {ABREVIATURA}=loadmol2 {MOL2_FILE} #########
        content = re.sub(
            r'^S1X=loadmol2\s+S1_IO_4_GD\.mol2(\s*#+.*)$',
            f'{abbreviation}=loadmol2 {mol2}\\1',
            content,
            flags=re.MULTILINE
        )
        
        # 2. loadAmberparams S1_IO_4_GD.frcmod ############# -> loadAmberparams {FRCMOD_FILE} #############
        content = re.sub(
            r'^loadAmberparams\s+S1_IO_4_GD\.frcmod(\s*#+.*)$',
            f'loadAmberparams {frcmod}\\1',
            content,
            flags=re.MULTILINE
        )
        
        # 3. check S1X ################ -> check {ABREVIATURA} ################
        # Se añade el ':' solicitado por el usuario en el destino.
        content = re.sub(
            r'^check\s+S1X(\s*#+.*)$',
            f'check {abbreviation}\\1', 
            content,
            flags=re.MULTILINE
        )

        # 4. saveoff S1X S1X.lib ################## -> saveoff {ABREVIATURA} {ABREVIATURA}.lib ##################
        content = re.sub(
            r'^saveoff\s+S1X\s+S1X\.lib(\s*#+.*)$',
            f'saveoff {abbreviation} {abbreviation}.lib\\1',
            content,
            flags=re.MULTILINE
        )
        
        # 5. system=loadPDB S1_IO_4_GD+HB2.pdb ####################### -> system=loadPDB {FINAL_PDB_VALUE} #######################
        content = re.sub(
            r'^system=loadPDB\s+S1_IO_4_GD\+HB2\.pdb(\s*#+.*)$',
            f'system=loadPDB {final_pdb}\\1',
            content,
            flags=re.MULTILINE
        )
        
        with open(output_filepath, 'w') as outfile:
            outfile.write(content)
            
        print(f"Archivo de entrada de LEAP '{input_filepath}' procesado y guardado como '{output_filepath}'.")

    except FileNotFoundError:
        print(f"Error: El archivo de entrada de LEAP '{input_filepath}' no fue encontrado en el directorio actual ({os.getcwd()}).")
        sys.exit(1)
    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo LEAP: {e}")
        sys.exit(1)


def main():
    
        # Cambia al directorio charges
    CHARGES_DIR = "charges"
    print(f"\n--- 4. Cambiando a directorio '{CHARGES_DIR}' ---")
    try:
        os.chdir(CHARGES_DIR)
        print(f"Directorio actual: {os.getcwd()}")
    except FileNotFoundError:
        print(f"Error: El directorio '{CHARGES_DIR}' no existe. Abortando.")
        sys.exit(1)
        
    # --- 1. PREPARACIÓN: Reemplazo de texto (similar a sed -i) ---
    print("\n--- 1. Reemplazo de texto para 'ponedor_coordenadas_pdb_en_com.py' ---")
    
    # Reemplazo 1: nombre_com_base
    replace_in_file(
        FILE_TO_MODIFY_PONER_COORDENADAS_COM,
        "nombre_com_base",
        NOMBRE_COM_BASE
    )
    # Reemplazo 2: nombre_pdb
    replace_in_file(
        FILE_TO_MODIFY_PONER_COORDENADAS_COM,
        "nombre_pdb",
        NOMBRE_PDB_BASE
    )

    # --- 2. CÁLCULO GAUSSIAN: Ejecución y espera ---
    
    # Ejecuta el script que prepara el archivo .com final
    print("\n--- 2. Ejecución de 'ponedor_coordenadas_pdb_en_com.py' ---")
    execute_shell_command(f"python3 {FILE_TO_MODIFY_PONER_COORDENADAS_COM}")

    # Lanza Gaussian en segundo plano
    print("\n--- 3. Lanzamiento de Gaussian en segundo plano ---")
    gaussian_process = execute_shell_command(f"launch_g16 {COM_FILE}", wait=False)

    # Espera a que Gaussian termine
    if gaussian_process:
        wait_for_gaussian_log()
    
    print("\n? Gaussian terminado correctamente.")
    print("####")

    # --- 3. ANTECHAMBER: Preparación de parámetros ---

    # Cambia al directorio antechamber
    ANTECHAMBER_DIR = "../antechamber"
    print(f"\n--- 4. Cambiando a directorio '{ANTECHAMBER_DIR}' ---")
    try:
        os.chdir(ANTECHAMBER_DIR)
        print(f"Directorio actual: {os.getcwd()}")
    except FileNotFoundError:
        print(f"Error: El directorio '{ANTECHAMBER_DIR}' no existe. Abortando.")
        sys.exit(1)

    # Copia el log desde el directorio superior (asumiendo que '../' es el directorio de trabajo anterior)
    print("\n--- 5. Copiando archivo de log ---")
    execute_shell_command(f"cp ../charges/{LOG_FILE} .")

    # Ejecuta ANTECHAMBER
    print("\n--- 6. Ejecutando ANTECHAMBER ---")
    ANTECHAMBER_CMD = (
        f"antechamber -i {LOG_FILE} -fi gout -o {MOL2_FILE} -fo mol2 -c resp -s 2 -rn {ABREVIATURA} -nc {CARGA_NETA} -at gaff"
    )
    execute_shell_command(ANTECHAMBER_CMD)

    # Ejecuta PARMCHK2
    print("\n--- 7. Ejecutando PARMCHK2 ---")
    PARMCHK2_CMD = (
        f"parmchk2 -i {MOL2_FILE} -f mol2 -o {FRCMOD_FILE} -a Y"
    )
    execute_shell_command(PARMCHK2_CMD)
    
    # --- 4. PREPARACIÓN DE DINÁMICA: Copia y modificación de scripts ---
    
    # Cambia al directorio archivos_dinamica
    DINAMICA_DIR = "../archivos_dinamica"
    print(f"\n--- 9. Cambiando a directorio '{DINAMICA_DIR}' ---")
    try:
        os.chdir(DINAMICA_DIR)
        print(f"Directorio actual: {os.getcwd()}")
    except FileNotFoundError:
        print(f"Error: El directorio '{DINAMICA_DIR}' no existe. Abortando.")
        sys.exit(1)

    # Pega los archivos .mol2 y .frcmod que acaba de hacer (desde ../antechamber)
    print(f"\n--- 10. Pegando los archivos .mol2 ({MOL2_FILE}) , .frcmod ({FRCMOD_FILE}) y PDB_BASE {NOMBRE_PDB_BASE} ---")
    execute_shell_command(f"cp ../antechamber/{MOL2_FILE} .")
    execute_shell_command(f"cp ../antechamber/{FRCMOD_FILE} .")
    execute_shell_command(f"cp ../charges/{NOMBRE_PDB_BASE} .")
    
    
    # Modifica 'hacedor_final_pdb.py'
    print(f"\n--- 11. Modificando '{HACEDOR_FINAL_PDB_SCRIPT}' ---")
    
    # A. PDB_REF -> PDB_REF_VALUE
    replace_in_file(
        HACEDOR_FINAL_PDB_SCRIPT,
        "PDB_REF",
        PDB_REF_VALUE
    )
    
    # B. PDB_LIG -> NOMBRE_PDB_BASE
    replace_in_file(
        HACEDOR_FINAL_PDB_SCRIPT,
        "PDB_LIG",
        NOMBRE_PDB_BASE
    )
    
    # C. MOL2_FILE -> MOL2_FILE (valor)
    replace_in_file(
        HACEDOR_FINAL_PDB_SCRIPT,
        "MOL2_FILE",
        MOL2_FILE
    )

    # D. OUTPUT_PDB -> FINAL_PDB_VALUE
    replace_in_file(
        HACEDOR_FINAL_PDB_SCRIPT,
        "OUTPUT_PDB",
        FINAL_PDB_VALUE
    )       
    # E. ABREVIATURA_default (ABV) -> ABREVIATURA
    replace_in_file(
        HACEDOR_FINAL_PDB_SCRIPT,
        "ABREVIATURA",
        ABREVIATURA
    )

    # Ejecuta el script que genera el .pdb final
    print("\n--- 2. Ejecución de 'hacedor_final_pdb.py' ---")
    execute_shell_command(f"python3 {HACEDOR_FINAL_PDB_SCRIPT}")
    
    
    # NUEVO: Procesar 'primigenio_leap.in' y crear 'tleap.in'
    print(f"\n--- 12. Creando el script de tleap.in con variables actualizadas ---")
    process_leap_file(
        LEAP_IN_FILE_ORIGINAL, 
        LEAP_IN_FILE_OUTPUT, 
        ABREVIATURA, 
        MOL2_FILE, 
        FRCMOD_FILE, 
        FINAL_PDB_VALUE
    )    
    
    # Vuelve al directorio de origen (archivos_dinamica -> ..)
    print("\n--- 13. Volviendo al directorio de origen ---")
    os.chdir("..")
    print(f"Directorio actual: {os.getcwd()}")
    
    print("\n#### Fin del proceso completo de preparación y configuración ####")

if __name__ == "__main__":
    main()
