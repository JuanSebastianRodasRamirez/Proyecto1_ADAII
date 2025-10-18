# --------------------------------------------------------
# Proyecto ADA II - Repartición Óptima de Cupos
# Integrantes: 
# Juan Sebastian Tobar Moriones (20240194)
# Juan Sebastian Rodas Ramirez (202359681)
# Johan Andres Ceballos Tabarez (202372229)
#
# Universidad: Universidad del Valle
# Profesor: Jesús Alexander Aranda
#
# Fecha de creación: 28 de septiembre del 2025
# Última modificación: 17 de octubre del 2025
#
# Archivo: dinamico.py
# --------------------------------------------------------


from math import prod
import time
from typing import Optional

# Tiempo máximo por defecto (5 minutos)
TIEMPO_MAX_SEGUNDOS = 5 * 60

# ----------------------------------------
# 1. Conversión de vector de cupos <-> número
# ----------------------------------------
def vector_a_numero(c, m):
    """Convierte un vector de cupos c en número n"""
    k = len(m)
    I = [prod((m[j] + 1) for j in range(i + 1, k)) for i in range(k)]
    return sum(c[i] * I[i] for i in range(k))

def numero_a_vector(n, m):
    """Convierte número n en vector de cupos c"""
    k = len(m)
    I = [prod((m[j] + 1) for j in range(i + 1, k)) for i in range(k)]
    c = []
    for i in range(k):
        ci = n // I[i]
        n = n % I[i]
        c.append(ci)
    return c

# ----------------------------------------
# 2. Función de insatisfacción de un estudiante
# ----------------------------------------
def insatisfaccion_estudiante(msj, A_j):
    """Calcula f_j dado msj = [(materia, prioridad)] y A_j asignadas"""
    total_materias = len(msj)
    
    if total_materias == 0:
        return 0
    
    # γ(|msⱼ|) = 3 * |msⱼ| - 1 (según el cálculo que muestras)
    gamma = 3 * total_materias - 1
    
    if gamma == 0:  # evitar división por cero
        return 0
    
    # materias asignadas (solo los códigos)
    asignadas = {m for (m, _) in A_j}
    
    # suma de prioridades de materias NO asignadas
    suma_no_asignadas = sum(p for (m, p) in msj if m not in asignadas)
    
    # fórmula: (1 - |maⱼ|/|msⱼ|) × (suma_prioridades_no_asignadas / γ(|msⱼ|))
    f = (1 - len(A_j) / total_materias) * (suma_no_asignadas / gamma)
    return f

# ----------------------------------------
# 3. Subconjuntos válidos de materias asignables
# ----------------------------------------
def subconjuntos_validos(msj, cupos_actuales, materias):
    """Genera subconjuntos A_j de materias que aún tienen cupo disponible (sin itertools)."""
    validas = []
    n = len(msj)
    # recorrer todas las máscaras de subconjunto de 0..2^n-1
    for mask in range(1 << n):
        subset = []
        ok = True
        for i in range(n):
            if (mask >> i) & 1:
                m, p = msj[i]
                try:
                    idx = materias.index(m)
                    if cupos_actuales[idx] == 0:
                        ok = False
                        break
                    subset.append((m, p))
                except ValueError:
                    # La materia no existe en la lista de materias disponibles
                    ok = False
                    break
        if ok:
            validas.append(tuple(subset))
    return validas

# ----------------------------------------
# 4. Algoritmo principal de Programación Dinámica
# ----------------------------------------
def rocPD(M, E, tiempo_max: Optional[float] = None):
    """
        Programa Dinámica (rocPD)

        Firma esperada:
                rocPD(M, E, tiempo_max=None)

        Parámetros:
                - M: lista de tuplas (codigo_materia, cupo). Cada elemento es (m, c).
                - E: lista de tuplas (codigo_estudiante, [(materia, prioridad)]). Cada
                         entrada representa a un estudiante y su lista de solicitudes.
                - tiempo_max: (opcional) límite en segundos para abortar la búsqueda y
                         lanzar TimeoutError si se excede.

        Retorno:
                - (solucion, costo_optimo)
                    * solucion: lista de pares (estudiante, A_j) en el mismo orden de E,
                        donde A_j es la colección de materias asignadas al estudiante.
                    * costo_optimo: float con la insatisfacción promedio mínima encontrada.

        Excepciones:
                - TimeoutError: si el tiempo de ejecución supera `tiempo_max`.

        Observaciones de implementación:
                - El algoritmo codifica cada estado de cupos como un número (funciones
                    vector_a_numero / numero_a_vector). Recorre los estudiantes y usa
                    programación dinámica para computar la insatisfacción mínima por
                    estado. Se mantiene un diccionario `decision` para reconstruir la
                    solución final.

        Complejidad aproximada:
                - El número de estados es el producto de (cupo_i + 1) para cada materia.
                - El bucle principal itera sobre r (nº estudiantes) y sobre todos los
                    estados, por lo que la complejidad en tiempo y memoria puede crecer
                    exponencialmente con el número y tamaño de cupos. Para entradas
                    grandes puede ser inviable.
    """
    if not E:  # Si no hay estudiantes
        return [], 0.0
        
    materias = [m for (m, _) in M]
    cupos = [c for (_, c) in M]
    
    # Verificar que hay materias disponibles
    if not materias:
        return [(est, []) for (est, _) in E], 0.0
    
    total_estados = prod([x + 1 for x in cupos])
    r = len(E)

    # control de tiempo
    tiempo_max = TIEMPO_MAX_SEGUNDOS if tiempo_max is None else tiempo_max
    tiempo_inicio = time.time()

    # DP[j][n]: mínima insatisfacción con j estudiantes y estado n
    DP0 = [0.0] * total_estados  # estado base (0 estudiantes)
    decision = {}

    for j in range(1, r + 1):
        estudiante, msj = E[j - 1]
        nuevaDP = [float('inf')] * total_estados
        
        for n in range(total_estados):
            # comprobar timeout periódicamente
            if tiempo_max is not None and (time.time() - tiempo_inicio) > tiempo_max:
                raise TimeoutError(f"Tiempo máximo de {tiempo_max} segundos excedido antes de hallar una solución óptima")
            cupos_actuales = numero_a_vector(n, cupos)
            
            # Obtener subconjuntos válidos para este estudiante
            subconjuntos = subconjuntos_validos(msj, cupos_actuales, materias)
            
            for A_j in subconjuntos:
                nuevo_cupos = cupos_actuales.copy()
                for (m, _) in A_j:
                    idx = materias.index(m)
                    nuevo_cupos[idx] -= 1

                nuevo_n = vector_a_numero(nuevo_cupos, cupos)
                costo = insatisfaccion_estudiante(msj, A_j) + DP0[nuevo_n]
                
                if costo < nuevaDP[n]:
                    nuevaDP[n] = costo
                    decision[(j, n)] = (nuevo_n, A_j)
        
        DP0 = nuevaDP  # avanzar al siguiente estudiante

    # encontrar el mejor estado final
    costo_optimo = min(DP0) if DP0 else 0.0
    # dividir por r para obtener el promedio
    costo_optimo = costo_optimo / r if r > 0 else 0.0
    estado_optimo = DP0.index(min(DP0)) if DP0 else 0

    # reconstruir solución
    solucion = []
    C = estado_optimo
    for j in range(r, 0, -1):
        if (j, C) in decision:
            nuevo_C, A_j = decision[(j, C)]
            estudiante, _ = E[j - 1]
            solucion.append((estudiante, A_j))
            C = nuevo_C
        else:
            # Si no hay decisión registrada, asignar lista vacía
            estudiante, _ = E[j - 1]
            solucion.append((estudiante, []))
    
    solucion.reverse()
    return solucion, costo_optimo
