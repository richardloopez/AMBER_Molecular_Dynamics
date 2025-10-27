import os

carpetas_totales = []
carpetas_completadas = []

# Recorre todas las carpetas del directorio actual
for carpeta in os.listdir('.'):
    if os.path.isdir(carpeta):
        carpetas_totales.append(carpeta)
        for root, dirs, files in os.walk(carpeta):
            for archivo in files:
                if archivo.endswith('.pdb') and '+ANT' in archivo:
                    print(f"La carpeta {carpeta} contiene el archivo {archivo}")
                    carpetas_completadas.append(carpeta)
                    break  # no hace falta buscar más dentro de esta carpeta

# Calcula las faltantes
carpetas_faltantes = list(set(carpetas_totales) - set(carpetas_completadas))


print("""
      
      
      
      
      
      
      
      ESPACIO
      
      
      
      
      
      
      
      """)

print("""
      
      
      
      
      
      
      
      TE DIGO LAS QUE NO ESTÁN:
      
      
      
      
      
      
      
      """)
# Imprime resultados
for carpeta in carpetas_faltantes:
    print(f"La carpeta {carpeta} no contiene el archivo esperado.")

print("""
      
      
      
      
      
      
      
      
      TAMBIÉN TE DIGO LAS QUE SÍ ESTÁN:
      
      
      
      
      
      
      
      
      
      """)

for carpeta in carpetas_completadas:
    print(f"La carpeta {carpeta} contiene el archivo esperado.")
