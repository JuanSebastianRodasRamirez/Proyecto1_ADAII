from collections import namedtuple
from typing import List, Sequence, Dict

materia = namedtuple("materia", ["codigo", "cupo"])
materia_solicitada = namedtuple("materia_solicitada", ["codigo", "prioridad"])

class estudiante:
    """
    Representa un estudiante, con su lista de materias solicitadas.

    Atributos:
        codigo (int): identificador del estudiante (ej).
        materias_solicitadas (list[materia_solicitada]): materias solicitadas (ms_j).
    """
    def __init__(self, codigo_estudiante: int, materias_solicitadas: Sequence[materia_solicitada]):
        self.codigo = codigo_estudiante
        self.materias_solicitadas = materias_solicitadas

    def getCodigo(self):
        # Devuelve el código del estudiante.
        return self.codigo

    def getMateriasSolicitadas(self):
        # Devuelve la lista de materias solicitadas por el estudiante.
        return self.materias_solicitadas

    def totalMaterias(self):
        # Devuelve el número total de materias solicitadas (|ms_j|).
        return len(self.materias_solicitadas)

    def sumaPrioridades(self):
        # Devuelve la suma de las prioridades p_jl de todas
        # las materias solicitadas por el estudiante.
        suma = 0
        for i in self.materias_solicitadas:
            suma += i.prioridad
        return suma

def es_solucion(M: List[materia], A: List[estudiante]) -> bool:
    """
    Verifica si la asignación de estudiantes respeta los cupos de las materias.

    Recorre todas las solicitudes de los estudiantes y cuenta cuántas veces
    aparece cada materia. Si alguna supera el cupo definido en `M`, devuelve False.

    Args:
        M (list[materia]): Lista de materias con su código y cupo máximo.
        A (list[estudiante]): Lista de estudiantes con las materias solicitadas.

    Returns:
        bool: True si ninguna materia excede su cupo, False en caso contrario.
    """
    # Pasamos M a un diccionario {codigo: cupo}
    cupo_max = {mat.codigo: mat.cupo for mat in M}

    # Contamos cuántas veces se solicita cada materia
    solicitudes: Dict[int, int] = {}

    for est in A:
        for m in est.getMateriasSolicitadas():
            solicitudes[m.codigo] = solicitudes.get(m.codigo, 0) + 1
            # Si ya supera el cupo, podemos cortar temprano
            if solicitudes[m.codigo] > cupo_max.get(m.codigo, 0):
                return False

    return True

def insatisfaccion_estudiante(estudiante: estudiante, asignacion: estudiante) -> float:
    """
    Calcula la insatisfacción f_j de un estudiante j según la fórmula:

        f_j = (1 - |ma_j| / |ms_j|) *
              ( Σ { p_jl : (s_jl, p_jl) ∈ ms_j ∧ (s_jl, p_jl) ∉ ma_j } / y(|ms_j|) )

    Args:
        estudiante: objeto estudiante con las materias solicitadas (ms_j).
        asignacion: objeto estudiante con las materias asignadas (ma_j).

    Returns:
        float: valor de insatisfacción del estudiante j.
    """
    total_materias_solicitadas = estudiante.totalMaterias()
    total_materias_asignadas = asignacion.totalMaterias()

    # Si se asignaron todas las materias solicitadas, la insatisfacción es 0
    if total_materias_solicitadas == total_materias_asignadas:
        return 0

    # Porcentaje de materias solicitadas que no fueron asignadas
    factor_izquierda = 1 - (total_materias_asignadas / total_materias_solicitadas)

    prioridades_no_matriculadas = estudiante.sumaPrioridades() - asignacion.sumaPrioridades()
    funcion_gamma = (3 * total_materias_solicitadas) - 1

    # División de prioridades no asignadas / γ(|ms_j|)
    factor_derecha = prioridades_no_matriculadas / funcion_gamma

    return factor_izquierda * factor_derecha


def insatisfaccion_general(E: List[estudiante], A: List[estudiante]) -> float:
    """
    Calcula la insatisfacción general de los estudiantes:

        F_{M,E}(A) = (Σ f_j) / r

    Args:
        E: lista de objetos estudiante con materias solicitadas.
        A: lista de objetos estudiante con materias asignadas,
                           en el mismo orden que 'estudiantes'.

    Returns:
        float: promedio de insatisfacción de todos los estudiantes (F_{M,E}(A)).
    """
    total = 0
    r = len(E)

    for e, a in zip(E, A):
        total += insatisfaccion_estudiante(e, a)

    return total / r
