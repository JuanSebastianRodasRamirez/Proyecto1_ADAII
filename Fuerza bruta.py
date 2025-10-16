import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from itertools import product, combinations # Para el producto cartesiano de matrices y combinaciones
from typing import List, Iterator, Tuple, Sequence, Optional, Dict
from collections import namedtuple

# --- Inicio: definiciones ---
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
    total = 0
    r = len(E)

    for e, a in zip(E, A):
        total += insatisfaccion_estudiante(e, a)

    return total / r

# --- Fin: definiciones ---

# La búsqueda solo se aborta por tiempo.
# Tiempo máximo fijado a 5 minutos (300s).
TIEMPO_MAX_SEGUNDOS = 5 * 60
import time

def combinaciones_posbiles_materias(materias_solicitadas: Sequence[materia_solicitada]) -> List[Tuple[materia_solicitada, ...]]:
    """
    Genera todas las combinaciones posibles de una lista de materias solicitadas.

    Args:
        materias_solicitadas (list[materia_solicitada]): Materias que un estudiante desea cursar.

    Returns:
        list[list[materia_solicitada]]: Lista con todas las combinaciones no vacías
        de las materias solicitadas.
    """
    combinaciones = []

    for i in range (1, len(materias_solicitadas) + 1):
        combinaciones.extend(combinations(materias_solicitadas, i))

    return combinaciones

def soluciones_posibles(E: List[estudiante]) -> Iterator[Tuple[Tuple[materia_solicitada, ...], ...]]:
    """
    Calcula todas las posibles asignaciones de materias para un grupo de estudiantes.

    Para cada estudiante, obtiene todas las combinaciones de sus materias solicitadas
    y devuelve el producto cartesiano de estas combinaciones, que representa todas
    las soluciones potenciales.

    Args:
        E (list[estudiante]): Lista de estudiantes con sus materias solicitadas.

    Returns:
        list[list[list[materia_solicitada]]]: Todas las combinaciones posibles de asignaciones.
    """
    combinaciones_materias_estudiante = []

    for estudiantes in E:
        materias_estudiante = estudiantes.getMateriasSolicitadas()
        combinaciones_materias_estudiante.append(combinaciones_posbiles_materias(materias_estudiante))

    # Devolvemos el generador (producto cartesiano) sin convertirlo a lista
    # para evitar consumir memoria en casos grandes.
    soluciones_posibles = product(*combinaciones_materias_estudiante)
    return soluciones_posibles

def rocFB(k:int, r:int, M:List[materia], E:List[estudiante], tiempo_max: Optional[float]=None) -> Tuple[List[estudiante], float]:
    """
    Evalúa todas las soluciones posibles para asignar materias y selecciona la mejor.

    Compara cada solución con la actual usando la función de insatisfacción general
    y valida que cumpla con los cupos de las materias. Retorna la asignación que
    minimiza la insatisfacción.

    Args:
        M (list[materia]): Lista de materias con su cupo máximo.
        E (list[estudiante]): Lista de estudiantes y sus materias solicitadas.

    Returns:
        list[estudiante]: Lista de estudiantes con las materias asignadas que cumplen
        los cupos y minimizan la insatisfacción.
    """

    # Obtener las combinaciones por estudiante (listas pequeñas) para:
    #  - estimar el tamaño total de soluciones
    #  - construir una solución inicial sin indexar el producto completo
    combs_por_estudiante = [combinaciones_posbiles_materias(est.getMateriasSolicitadas()) for est in E]

    # Determinar tiempo máximo a usar
    # y usamos el límite fijo de módulo (5 minutos).
    tiempo_max = TIEMPO_MAX_SEGUNDOS

    inicio = time.time()

    soluciones = soluciones_posibles(E)

    # Construir una solución inicial usando la primera combinación de cada estudiante
    A = []
    for i, est in enumerate(E):
        primeras = combs_por_estudiante[i]
        primera = primeras[0] if len(primeras) > 0 else ()
        e = estudiante(est.getCodigo(), primera)
        A.append(e)

    for solucion in soluciones:
        # Comprobar tiempo transcurrido y abortar si excede el máximo
        if tiempo_max is not None and (time.time() - inicio) > tiempo_max:
            raise TimeoutError(f"Tiempo máximo de {tiempo_max} segundos excedido antes de hallar una solución óptima")
        posible_solucion = [] 

        for i, estudiantes in enumerate(E):
            e = estudiante(estudiantes.getCodigo(), solucion[i])
            posible_solucion.append(e)

        insatisfaccion_vieja = insatisfaccion_general(E, A)
        insatisfaccion_nueva = insatisfaccion_general(E, posible_solucion)

        if (es_solucion(M, posible_solucion) and (insatisfaccion_nueva < insatisfaccion_vieja)):
            A = posible_solucion

    return (A, insatisfaccion_general(E, A))
