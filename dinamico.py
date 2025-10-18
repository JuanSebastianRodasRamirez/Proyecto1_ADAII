from math import prod

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
def rocPD(M, E):
    """
    M: lista de tuplas (codigo_materia, cupo)
    E: lista de tuplas (codigo_estudiante, [(materia, prioridad)])
    
    Retorna: (solucion, costo_optimo)
    donde solucion es una lista de (estudiante, A_j) y costo_optimo es float
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

    # DP[j][n]: mínima insatisfacción con j estudiantes y estado n
    DP0 = [0.0] * total_estados  # estado base (0 estudiantes)
    decision = {}

    for j in range(1, r + 1):
        estudiante, msj = E[j - 1]
        nuevaDP = [float('inf')] * total_estados
        
        for n in range(total_estados):
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
