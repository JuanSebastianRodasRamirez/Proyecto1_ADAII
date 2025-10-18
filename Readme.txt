Proyecto 1 - ADA II: Repartición Óptima de Cupos

Descripción general
-------------------
Esta entrega contiene una interfaz gráfica y tres implementaciones de algoritmos para la asignación de materias a estudiantes: Programación Dinámica, Fuerza Bruta y Voraz.

Archivos entregados
-------------------
- interfaz.py
  - Interfaz gráfica (Tkinter). Permite cargar un archivo de entrada, seleccionar el algoritmo (pd, fb, vz) y procesar la solución.
  - Ejecuta el algoritmo en un hilo separado para evitar que la ventana quede "No responde". Los resultados se muestran en el panel derecho y se escriben en un archivo de salida.

- dinamico.py
  - Implementación del algoritmo de Programación Dinámica (función `rocPD(M, E, tiempo_max=None)`).
  - Genera la solución óptima y controla un timeout por defecto (5 minutos).

- fuerzabruta.py
  - Implementación (esperada) del algoritmo por Fuerza Bruta. Contiene la función `rocFB(...)` y clases/constructores usados por la interfaz.
  - Si el archivo tiene un nombre distinto, la interfaz intenta reconocer variantes comunes.

- voraz.py
  - Implementación (esperada) del algoritmo Voraz con la función `rocV(...)`.

- salida_dinamica1.txt, salida_voraz1.txt, salida_fuerzabruta1.txt
  - Ejemplos de archivos de salida que pueden generarse tras ejecutar los algoritmos.

- __pycache__/
  - Archivos compilados por Python (no necesarios en la entrega, pero pueden aparecer si ejecuta la aplicación).

- Readme.txt
  - Este archivo: resumen de los contenidos e instrucciones de ejecución.

Formato de entrada esperado
---------------------------
El formato de entrada que entiende la aplicación es (ejemplo):

k
codigoMateria1,cupo1
codigoMateria2,cupo2
...

r
codigoEst1,numSolicitudes1
m11,prioridad11
m12,prioridad12
...
codigoEst2,numSolicitudes2
...

- k: número de materias.
- Para cada materia: código (string) y cupo (entero).
- r: número de estudiantes.
- Para cada estudiante: su código y el número de materias que solicita, seguido de esas líneas "materia,prioridad".

Ejemplo mínimo:

3
M1,2
M2,1
M3,2
2
E1,2
M1,1
M2,2
E2,1
M3,1

Instrucciones para ejecutar
--------------------------
1) Extraer el contenido del archivo ZIP de entrega en una carpeta local.

2) Abrir una terminal y situarse en la carpeta donde se extrajo el contenido (la carpeta que contiene `interfaz.py`). Por ejemplo:

  cd /ruta/al/directorio_del_proyecto

3) Ejecutar la interfaz gráfica con Python (asegúrate de tener Python instalado). Comandos generales:

  python interfaz.py

Si necesitas usar una ruta explícita al ejecutable de Python (opcional):

  /ruta/al/python interfaz.py

En Windows PowerShell la forma análoga sería:

  & "C:\ruta\a\python.exe" "interfaz.py"

4) En la ventana que se abre:
- Usa "Abrir archivo de prueba" para seleccionar un archivo de entrada en el formato descrito más arriba.
- Selecciona el algoritmo: "Programación Dinámica" (pd), "Fuerza Bruta" (fb) o "Voraz" (vz).
- Pulsa "Procesar y obtener solución".
  - La aplicación ejecutará el cálculo en un hilo aparte y mostrará una etiqueta "Cargando..." mientras procesa.
  - Al terminar mostrará la solución en el panel derecho y guardará un archivo de salida en la carpeta del proyecto, por ejemplo `salida_dinamica1.txt`.

Problemas comunes y soluciones
-----------------------------
- Ventana "No responde": Esto debe estar solucionado porque la interfaz lanza el cálculo en un hilo separado y solo actualiza widgets desde el hilo principal.
- Errores al cargar módulos: Asegúrate de que `fuerzabruta.py` y `voraz.py` existan y exporten las funciones esperadas (`rocFB` y `rocV` respectivamente). La interfaz intenta detectar nombres alternativos, pero es mejor que los archivos se llamen exactamente como aquí.

Autores
------------------
- Juan Sebastian Tobar Moriones (20240194)
- Juan Sebastian Rodas Ramirez (202359681)
- Johan Andres Ceballos Tabarez (202372229)

Fecha: 17 Octubre 2025
