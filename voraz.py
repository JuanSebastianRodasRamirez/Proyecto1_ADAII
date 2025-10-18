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
# Archivo: voraz.py
# --------------------------------------------------------


"""
Algoritmo voraz adaptativo para la repartición óptima de cupos.
- Primera fase: Asignación greedy ponderada (prioridad, urgencia y escasez)
- Segunda fase: Reajuste local (intercambio de materias entre estudiantes)
"""

def rocV(k, r, M, E):
    # Inicializar cupos disponibles
    cupos = {cod: cupo for cod, cupo in M}
    A = {ej: [] for ej, _ in E}
    solicitudes = []

    # Generar lista de solicitudes (prioridad, estudiante, materia)
    for ej, msj in E:
        for (materia, prioridad) in msj:
            solicitudes.append((prioridad, ej, materia))

    # Funciones auxiliares simples
    def contar_materias(ej):
        for e, ms in E:
            if e == ej:
                return len(ms)
        return 1

    def cupo_de_materia(mat):
        for m, c in M:
            if m == mat:
                return c
        return 1

    # Ordenar por score = prioridad / (cupo * materias_solicitadas)
    solicitudes.sort(
        key=lambda x: -x[0] / (cupo_de_materia(x[2]) * contar_materias(x[1]))
    )

    # Asignación directa (sin reajustes)
    for prioridad, ej, materia in solicitudes:
        if cupos[materia] > 0 and materia not in A[ej]:
            A[ej].append(materia)
            cupos[materia] -= 1

    # Calcular insatisfacción general
    suma_f = 0
    for ej, msj in E:
        pedidas = len(msj)
        asignadas = len(A[ej])
        gamma = 3 * pedidas - 1
        no_asignadas = [(m, p) for (m, p) in msj if m not in A[ej]]
        suma_p = sum(p for _, p in no_asignadas)
        fj = (1 - asignadas / pedidas) * (suma_p / gamma) if pedidas > 0 else 0
        suma_f += fj

    F = suma_f / r if r > 0 else 0
    return A, F
