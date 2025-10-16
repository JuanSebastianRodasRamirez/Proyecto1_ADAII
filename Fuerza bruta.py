import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from itertools import product, combinations # Para el producto cartesiano de matrices y combinaciones
from typing import List, Iterator, Tuple, Sequence, Optional
from definiciones import *

# La búsqueda solo se aborta por tiempo.
# Tiempo máximo obligatorio (segundos) fijado a 5 minutos (300s).
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

    # Determinar tiempo máximo a usar: ignoramos cualquier intento externo de cambiarlo
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
