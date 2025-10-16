# Asignación de materias (Fuerza bruta)

Este repositorio contiene una implementación por fuerza bruta para el
problema de asignación de estudiantes a materias respetando cupos.

Qué hace el programa
---------------------
- Lee un archivo con la descripción de materias (códigos y cupos) y la
  lista de estudiantes con las materias solicitadas y prioridades.
- Genera todas las asignaciones posibles (cada estudiante puede ser
  asignado a cualquier subconjunto no vacío de sus solicitudes) y
  selecciona la asignación válida que minimiza la insatisfacción
  general de los estudiantes.
- La búsqueda es exhaustiva (fuerza bruta); se aplica poda únicamente
  por factibilidad (si una rama excede los cupos, se descarta).
- Para evitar ejecuciones indefinidas hay un límite de tiempo por
  defecto (300 segundos). Si el cálculo excede ese tiempo, se devuelve
  un error de tiempo agotado.

Archivos principales
--------------------
- `Fuerza bruta.py`: contiene las definiciones de tipos (materia,
  materia_solicitada, estudiante) y la función `rocFB(...)` que ejecuta
  la búsqueda exhaustiva.
- `interfaz.py`: interfaz gráfica (Tkinter) que permite cargar un archivo
  de prueba, ejecutar la búsqueda en un hilo (para no bloquear la GUI)
  y mostrar la salida formateada. Muestra una animación "Cargando..."
  mientras se ejecuta el proceso.

Formato del archivo de entrada
------------------------------
El fichero de entrada debe seguir este formato:

1) k  (nº de materias)
2) k líneas con `codigo,cupo` (ej. `1001,10`)
3) r  (nº de estudiantes)
4) Para cada estudiante:
   - una línea `codigo_estudiante,s_j` donde s_j es el nº de solicitudes
   - s_j líneas con `codigo_materia,prioridad` (ej. `1001,3`)

Ejemplo:
```
3
1000,5
1001,10
1002,8
2
10,3
1000,3
1002,2
1001,1
11,2
1001,2
1002,1
```

Cómo usar
---------
- Ejecutar la interfaz gráfica (recomendado):

  ```powershell
  python "c:/Users/Juan Sebastian/Desktop/Proyecto1_ADAII/interfaz.py"
  ```

  - Usa "Abrir archivo de prueba" para seleccionar tu .txt de entrada.
  - Pulsa "Procesar y obtener solución". Verás "Cargando..." mientras
    se calcula la mejor asignación.

- Usar desde otro script / CLI:
  - Importa `Fuerza bruta.py` como módulo y llama a `rocFB(k, r, M, E)`
    pasando las estructuras `M` (lista de `materia`) y `E` (lista de
    `estudiante`) construidas con los namedtuples del módulo.
---------
Limitaciones
------------
- Algoritmo exhautivo: la complejidad crece exponencialmente con el
  tamaño de la entrada. Para instancias grandes puede no ser práctico.
- Control de tiempo: se impone un tiempo máximo para evitar ejecuciones
  que nunca terminan (valor por defecto: 5 minutos (300s)). Puedes modificar la
  constante `TIEMPO_MAX_SEGUNDOS` en `Fuerza bruta.py` si lo necesitas.
------------

