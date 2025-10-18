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
# Archivo: fuerzabruta.py
# --------------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from itertools import product, combinations 
from typing import List, Iterator, Tuple, Sequence, Optional, Dict
from collections import namedtuple

# --- Inicio: definiciones (tipos y utilidades de dominio) ---
# En esta sección definimos los tipos de datos y funciones puramente
# relacionadas con el modelo del problema (materias, solicitudes y
# métricas de insatisfacción). Estos son independientes del algoritmo
# de búsqueda y sirven como "contrato" que usa el algoritmo principal.

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
        total_prioridades = 0
        for materia_sol in self.materias_solicitadas:
            total_prioridades += materia_sol.prioridad
        return total_prioridades

def es_solucion(M: List[materia], A: List[estudiante]) -> bool:
    # Pasamos M a un diccionario {codigo: cupo}
    cupos_maximos = {mater.codigo: mater.cupo for mater in M}

    # Contamos cuántas veces se solicita cada materia
    conteo_solicitudes: Dict[int, int] = {}

    for estudiante_obj in A:
        for materia_sol in estudiante_obj.getMateriasSolicitadas():
            codigo = materia_sol.codigo
            conteo_solicitudes[codigo] = conteo_solicitudes.get(codigo, 0) + 1
            # Si ya supera el cupo, podemos cortar temprano
            if conteo_solicitudes[codigo] > cupos_maximos.get(codigo, 0):
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

    for estudiante_solicitante, asignacion_estudiante in zip(E, A):
        total += insatisfaccion_estudiante(estudiante_solicitante, asignacion_estudiante)

    return total / r

# --- Fin: definiciones ---

# Control de tiempo de ejecución
# El algoritmo de fuerza bruta es exhaustivo y puede tardar mucho. Para
# evitar ejecuciones indefinidas imponemos un límite de tiempo. Si se
# supera, se lanza TimeoutError. El valor por defecto está fijado a 5
# minutos (300 segundos), pero la función `rocFB` acepta un parámetro
# `tiempo_max` opcional para sustituirlo.
TIEMPO_MAX_SEGUNDOS = 5 * 60
import time

def combinaciones_posbiles_materias(materias_solicitadas: Sequence[materia_solicitada]) -> List[Tuple[materia_solicitada, ...]]:
    """
    Genera todas las combinaciones posibles de una lista de materias solicitadas.

    Args:
        materias_solicitadas (list[materia_solicitada]): Materias que un estudiante desea cursar.

    Returns:
        list[list[materia_solicitada]]: Lista con todas las combinaciones no vacías
        de las materias solicitadas. Cada elemento es una tupla que representa
        un subconjunto de asignaturas que el estudiante podría llegar a
        matricular (sin orden relevante). Esta función solo genera las
        combinaciones por estudiante, sin ninguna consideración de cupo.
    """
    resultado_combinaciones = []

    for tam in range(1, len(materias_solicitadas) + 1):
        resultado_combinaciones.extend(combinations(materias_solicitadas, tam))

    return resultado_combinaciones

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
    combinaciones_por_estudiante = []

    for estudiante_obj in E:
        materias_del_estudiante = estudiante_obj.getMateriasSolicitadas()
        combinaciones_por_estudiante.append(combinaciones_posbiles_materias(materias_del_estudiante))

    # Construye un generador que produce cada asignación combinada posible:
    # para cada estudiante una tupla (una combinación de sus solicitudes).
    # Usamos un generador (producto cartesiano) en lugar de materializar
    # la lista completa en memoria porque el espacio de soluciones puede
    # crecer exponencialmente con el número de estudiantes y solicitudes.
    generador_producto = product(*combinaciones_por_estudiante)
    return generador_producto

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

    # Preparar datos y estado para la búsqueda exhaustiva (fuerza bruta)
    # - `combinaciones_por_estudiante`: listas de opciones por cada estudiante
    # - `cupos_maximos`: cupo total permitido por materia
    # - `tiempo_max`: límite de tiempo para abortar la búsqueda
    # - `cupos_usados`: conteo incremental de cupos ocupados por materias
    # - `asignacion_actual`: asignación parcial construida durante el DFS
    # - `mejor_asignacion` / `mejor_insatisfaccion`: mejor solución encontrada
    combinaciones_por_estudiante = [combinaciones_posbiles_materias(est.getMateriasSolicitadas()) for est in E]

    cupos_maximos = {mater.codigo: mater.cupo for mater in M}

    tiempo_max = TIEMPO_MAX_SEGUNDOS if tiempo_max is None else tiempo_max
    tiempo_inicio = time.time()

    total_estudiantes = len(E)

    # Estado mutable usado por el backtracking
    cupos_usados: Dict[int, int] = {mater.codigo: 0 for mater in M}
    asignacion_actual: List[estudiante] = []
    mejor_asignacion: Optional[List[estudiante]] = None
    mejor_insatisfaccion: Optional[float] = None

    # Comentario general sobre la estrategia:
    # - Esta implementación realiza un recorrido DFS (backtracking) que
    #   intenta todas las combinaciones por estudiante en orden.
    # - Solo realizamos poda de factibilidad: si al añadir una combinación
    #   parcial se supera el cupo de alguna materia, descartamos la rama.
    # - No se añaden heurísticas ni aproximaciones: la búsqueda sigue
    #   siendo exhaustiva sobre el espacio válido, por lo tanto conserva
    #   el carácter de fuerza bruta del algoritmo.
    def busqueda_recursiva(indice_estudiante: int):
        nonlocal mejor_asignacion, mejor_insatisfaccion

        # Comprobar tiempo
        if tiempo_max is not None and (time.time() - tiempo_inicio) > tiempo_max:
            raise TimeoutError(f"Tiempo máximo de {tiempo_max} segundos excedido antes de hallar una solución óptima")

        if indice_estudiante == total_estudiantes:
            # Solución completa: calcular insatisfacción y actualizar mejor
            ins_actual = insatisfaccion_general(E, asignacion_actual)
            if (mejor_insatisfaccion is None) or (ins_actual < mejor_insatisfaccion):
                # Copiar la asignación actual (crear nuevos objetos estudiante)
                mejor_insatisfaccion = ins_actual
                mejor_asignacion = [estudiante(a.getCodigo(), tuple(a.getMateriasSolicitadas())) for a in asignacion_actual]
            return

        # Para el estudiante actual, probar cada combinación posible
        codigo_estudiante = E[indice_estudiante].getCodigo()
        opciones_combinaciones = combinaciones_por_estudiante[indice_estudiante]
        for combinacion_materias in opciones_combinaciones:
            # Construir el conteo de cuántas plazas consume esta combinación
            # y comprobar si al añadirse supera algún cupo máximo. Esta es
            # la poda de factibilidad: si sobrepasa, no exploramos la rama.
            sobrepasa = False
            conteo_combinacion: Dict[int, int] = {}
            for materia_sol in combinacion_materias:
                codigo_materia = materia_sol.codigo
                conteo_combinacion[codigo_materia] = conteo_combinacion.get(codigo_materia, 0) + 1
            for codigo_materia, cantidad in conteo_combinacion.items():
                if cupos_usados.get(codigo_materia, 0) + cantidad > cupos_maximos.get(codigo_materia, 0):
                    sobrepasa = True
                    break
            if sobrepasa:
                continue

            # Aplicar la combinación (incrementar cupos usados)
            for codigo_materia, cantidad in conteo_combinacion.items():
                cupos_usados[codigo_materia] = cupos_usados.get(codigo_materia, 0) + cantidad

            asignacion_actual.append(estudiante(codigo_estudiante, combinacion_materias))

            # Recurrir al siguiente estudiante
            busqueda_recursiva(indice_estudiante + 1)

            # Deshacer cambios (backtrack)
            asignacion_actual.pop()
            for codigo_materia, cantidad in conteo_combinacion.items():
                cupos_usados[codigo_materia] -= cantidad

    # Lanzar la búsqueda exhaustiva
    busqueda_recursiva(0)

    if mejor_asignacion is None:
        # No se encontró ninguna asignación válida (por ejemplo cupos 0)
        return ([], float('inf'))
    return (mejor_asignacion, mejor_insatisfaccion if mejor_insatisfaccion is not None else float('inf'))
