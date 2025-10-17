import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import importlib.util
import sys

from typing import List, Any

# Inicialmente dejamos aliases a Any y los actualizaremos 
# cuando carguemos dinámicamente el módulo de fuerza.

Estudiante: Any = Any
materia: Any = Any
materia_solicitada: Any = Any

PROJECT_DIR = Path(__file__).parent


def load_fuerza_module() -> Any:
    # Intentar varios nombres posibles del archivo que contiene el módulo
    candidates = [
        PROJECT_DIR / 'fuerzabruta.py',
        PROJECT_DIR / 'Fuerza bruta.py',
        PROJECT_DIR / 'fuerza_bruta.py',
        PROJECT_DIR / 'fuerzaBruta.py',
    ]
    fuerza = None
    for fb_path in candidates:
        if not fb_path.exists():
            continue
        spec = importlib.util.spec_from_file_location('fuerza_bruta_mod', str(fb_path))
        if spec is None or spec.loader is None:
            continue
        fuerza = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        sys.modules['fuerza_bruta_mod'] = fuerza
        spec.loader.exec_module(fuerza)  # type: ignore[attr-defined]
        break
    if fuerza is None:
        raise FileNotFoundError('No se encontró el módulo de Fuerza Bruta en el proyecto')

    # Exportar referencias útiles al módulo para que la interfaz pueda usarlas
    # (tipos y constructores). Esto permite que funciones como parse_input
    # puedan crear instancias de `materia` / `materia_solicitada` sin depender
    # de un módulo separado `definiciones.py`. Se usa carga dinámica para
    # evitar importar el módulo en el nivel superior y para resolver las
    # dependencias en tiempo de ejecución (útil cuando el módulo principal
    # fue modificado/inyectado en el proyecto).
    global Estudiante, materia, materia_solicitada
    try:
        Estudiante = getattr(fuerza, 'estudiante')
        materia = getattr(fuerza, 'materia')
        materia_solicitada = getattr(fuerza, 'materia_solicitada')
    except Exception:
        # Si algún nombre falta, dejar los aliases como estaban y seguir
        pass
    return fuerza


def load_pd_module() -> Any:
    """Carga el módulo de programación dinámica"""
    candidates = [
        PROJECT_DIR / 'dinamico.py',
        PROJECT_DIR / 'roc_pd.py',
        PROJECT_DIR / 'dinamico_pd.py',
    ]
    pd_mod = None
    for pd_path in candidates:
        if not pd_path.exists():
            continue
        spec = importlib.util.spec_from_file_location('roc_pd_mod', str(pd_path))
        if spec is None or spec.loader is None:
            continue
        pd_mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        sys.modules['roc_pd_mod'] = pd_mod
        spec.loader.exec_module(pd_mod)  # type: ignore[attr-defined]
        break
    if pd_mod is None:
        raise FileNotFoundError('No se encontró el módulo de Programación Dinámica en el proyecto')
    return pd_mod


def load_voraz_module() -> Any:
    """Carga el módulo voraz (voraz.py)"""
    vz_path = PROJECT_DIR / 'voraz.py'
    spec = importlib.util.spec_from_file_location('voraz_mod', str(vz_path))
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"No se pudo cargar el módulo voraz desde {vz_path}")
    vz_mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules['voraz_mod'] = vz_mod
    spec.loader.exec_module(vz_mod)  # type: ignore[attr-defined]
    return vz_mod


def parse_input_fb(text: str):
    """Parsea el texto de entrada según el formato del enunciado para Fuerza Bruta.

    Formato esperado:
    k
    codigo,cupo   (k líneas)
    r
    e1,s1         (por cada estudiante: código, número de solicitudes)
    m11,p11       (s1 líneas)
    m12,p12
    ...
    """
    lineas = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lineas:
        raise ValueError('Archivo vacío o sin líneas válidas')
    indice = 0
    try:
        num_materias = int(lineas[indice]); indice += 1
    except Exception as e:
        raise ValueError('No se pudo leer k (nº de materias) en la primera línea') from e

    M = []
    for _ in range(num_materias):
        if indice >= len(lineas):
            raise ValueError('Faltan líneas para las materias (M)')
        partes = lineas[indice].split(',')
        if len(partes) != 2:
            raise ValueError(f'Formato inválido en materia: {lineas[indice]}')
        codigo = int(partes[0]); cupo = int(partes[1])
        M.append(materia(codigo, cupo))
        indice += 1

    if indice >= len(lineas):
        raise ValueError('Falta la línea con el número de estudiantes r')
    num_estudiantes = int(lineas[indice]); indice += 1

    E = []
    for _ in range(num_estudiantes):
        if indice >= len(lineas):
            raise ValueError('Faltan bloques de estudiantes')
        partes_header = lineas[indice].split(',')
        if len(partes_header) != 2:
            raise ValueError(f'Formato inválido en estudiante header: {lineas[indice]}')
        codigo_estudiante = int(partes_header[0]); numero_solicitudes = int(partes_header[1])
        indice += 1
        lista_materias = []
        for _ in range(numero_solicitudes):
            if indice >= len(lineas):
                raise ValueError('Faltan líneas de materias solicitadas para un estudiante')
            partes_mp = lineas[indice].split(',')
            if len(partes_mp) != 2:
                raise ValueError(f'Formato inválido en materia solicitada: {lineas[indice]}')
            codigo_materia = int(partes_mp[0]); prioridad = int(partes_mp[1])
            lista_materias.append(materia_solicitada(codigo_materia, prioridad))
            indice += 1
        E.append(Estudiante(codigo_estudiante, lista_materias))

    return M, E


def parse_input_pd(text: str):
    """Parsea el texto de entrada para Programación Dinámica.
    Retorna M, E en el formato que espera rocPD."""
    lineas = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lineas:
        raise ValueError('Archivo vacío o sin líneas válidas')
    
    indice = 0
    try:
        num_materias = int(lineas[indice]); indice += 1
    except Exception as e:
        raise ValueError('No se pudo leer k (nº de materias) en la primera línea') from e

    M = []
    for _ in range(num_materias):
        if indice >= len(lineas):
            raise ValueError('Faltan líneas para las materias (M)')
        partes = lineas[indice].split(',')
        if len(partes) != 2:
            raise ValueError(f'Formato inválido en materia: {lineas[indice]}')
        codigo = int(partes[0]); cupo = int(partes[1])
        M.append((codigo, cupo))
        indice += 1

    if indice >= len(lineas):
        raise ValueError('Falta la línea con el número de estudiantes r')
    num_estudiantes = int(lineas[indice]); indice += 1

    E = []
    for _ in range(num_estudiantes):
        if indice >= len(lineas):
            raise ValueError('Faltan bloques de estudiantes')
        partes_header = lineas[indice].split(',')
        if len(partes_header) != 2:
            raise ValueError(f'Formato inválido en estudiante header: {lineas[indice]}')
        codigo_estudiante = int(partes_header[0]); numero_solicitudes = int(partes_header[1])
        indice += 1
        msj = []
        for _ in range(numero_solicitudes):
            if indice >= len(lineas):
                raise ValueError('Faltan líneas de materias solicitadas para un estudiante')
            partes_mp = lineas[indice].split(',')
            if len(partes_mp) != 2:
                raise ValueError(f'Formato inválido en materia solicitada: {lineas[indice]}')
            codigo_materia = int(partes_mp[0]); prioridad = int(partes_mp[1])
            msj.append((codigo_materia, prioridad))
            indice += 1
        E.append((codigo_estudiante, msj))

    return M, E


from typing import Any as _Any

def format_output_fb(insat: float, A: List[_Any]) -> str:
    """Formatea la salida de acuerdo al enunciado para Fuerza Bruta.

    Primera línea: costo (insatisfacción general) con 3 decimales
    Luego para cada estudiante en orden: una línea 'e_j,a_j' (código, cantidad asignadas)
    seguida de a_j líneas, cada una con el código de asignatura asignado.
    """
    lineas_salida = []
    lineas_salida.append(f"{insat:.3f}")
    for estudiante_asignado in A:
        materias_asignadas = list(estudiante_asignado.getMateriasSolicitadas())
        lineas_salida.append(f"{estudiante_asignado.getCodigo()},{len(materias_asignadas)}")
        for materia_asig in materias_asignadas:
            lineas_salida.append(str(materia_asig.codigo))

    return '\n'.join(lineas_salida)


def format_output_pd(insat: float, solucion: List[_Any], E: List[_Any]) -> str:
    """Formatea la salida de acuerdo al enunciado para Programación Dinámica."""
    lineas_salida = []
    lineas_salida.append(f"{insat:.6f}")
    
    # Crear mapa de asignaciones
    asign_map = {est: [m for (m, _) in A] for (est, A) in solucion}
    
    for est, _ in E:
        asign = asign_map.get(est, [])
        lineas_salida.append(f"{est},{len(asign)}")
        for m in asign:
            lineas_salida.append(str(m))

    return '\n'.join(lineas_salida)


def write_generic_output(filename: str, content: str) -> Path:
    """Escribe el contenido (string) en un archivo dentro de PROJECT_DIR y retorna la Path.

    filename: nombre de archivo relativo (por ejemplo 'salida_dinamica1.txt')
    content: contenido ya formateado como texto
    """
    out_path = PROJECT_DIR / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return out_path


class App:
    def __init__(self, root):
        self.root = root
        root.title('Interfaz - Asignación de materias')

        frm = tk.Frame(root)
        frm.pack(fill='both', expand=True, padx=8, pady=8)

        # Frame para controles superiores
        control_frame = tk.Frame(frm)
        control_frame.pack(fill='x', pady=(0, 8))

        # Selector de algoritmo
        algorithm_frame = tk.Frame(control_frame)
        algorithm_frame.pack(fill='x')

        tk.Label(algorithm_frame, text='Algoritmo:', font=('Arial', 10, 'bold')).pack(side='left')
        
        self.algorithm_var = tk.StringVar(value='pd')
        
        pd_radio = tk.Radiobutton(algorithm_frame, text='Programación Dinámica', 
                                 variable=self.algorithm_var, value='pd',
                                 command=self.on_algorithm_change)
        pd_radio.pack(side='left', padx=10)
        
        fb_radio = tk.Radiobutton(algorithm_frame, text='Fuerza Bruta', 
                                 variable=self.algorithm_var, value='fb',
                                 command=self.on_algorithm_change)
        fb_radio.pack(side='left', padx=10)

        vz_radio = tk.Radiobutton(algorithm_frame, text='Voraz',
                                 variable=self.algorithm_var, value='vz',
                                 command=self.on_algorithm_change)
        vz_radio.pack(side='left', padx=10)

        # Frame para botones
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill='x', pady=(8, 0))

        self.open_btn = tk.Button(btn_frame, text='Abrir archivo de prueba', command=self.open_file)
        self.open_btn.pack(side='left')

        self.time_label = tk.Label(btn_frame, text='Tiempo máximo: 5 minutos (300 segundos)')
        self.time_label.pack(side='left', padx=(8,2))

        self.run_btn = tk.Button(btn_frame, text='Procesar y obtener solución', command=self.start_process_thread)
        self.run_btn.pack(side='left', padx=8)

        # Texto animado de carga
        self.loading_label = tk.Label(btn_frame, text='', font=('Arial', 11, 'bold'))
        self.loading_label.pack(side='left', padx=(12,0))
        self._loading_anim_id = None

        text_frame = tk.PanedWindow(frm, orient='horizontal')
        text_frame.pack(fill='both', expand=True, pady=8)

        self.input_text = tk.Text(text_frame, width=60)
        text_frame.add(self.input_text)

        self.output_text = tk.Text(text_frame, width=60)
        text_frame.add(self.output_text)

        self.current_path = None

    def on_algorithm_change(self):
        """Se ejecuta cuando cambia la selección del algoritmo"""
        algorithm = self.algorithm_var.get()
        if algorithm == 'pd':
            self.root.title('Interfaz - Asignación de materias (Programación Dinámica)')
        elif algorithm == 'fb':
            self.root.title('Interfaz - Asignación de materias (Fuerza Bruta)')
        elif algorithm == 'vz':
            self.root.title('Interfaz - Asignación de materias (Voraz)')
        else:
            self.root.title('Interfaz - Asignación de materias')

    def open_file(self):
        ruta_archivo = filedialog.askopenfilename(title='Seleccionar archivo de prueba', filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if not ruta_archivo:
            return
        self.current_path = ruta_archivo
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert(tk.END, contenido)
        self.output_text.delete('1.0', tk.END)

    def start_process_thread(self):
        # Deshabilitar botones y limpiar salida
        self.run_btn.config(state='disabled')
        self.open_btn.config(state='disabled')
        self.output_text.delete('1.0', tk.END)
        # Iniciar animación de 'Cargando...'
        self._loading_anim_state = 0
        self.animate_loading()
        # Lanzar el cálculo en un hilo aparte
        import threading
        hilo_proceso = threading.Thread(target=self.process_file_thread, daemon=True)
        hilo_proceso.start()

    def process_file_thread(self):
        # Esta función corre en un hilo aparte
        algorithm = self.algorithm_var.get()
        contenido = self.input_text.get('1.0', tk.END)
        
        try:
            if algorithm == 'fb':
                # Fuerza Bruta
                fuerza = load_fuerza_module()
                M, E = parse_input_fb(contenido)
                asignacion, insat = fuerza.rocFB(k=len(M), r=len(E), M=M, E=E)
                salida_formateada = format_output_fb(insat, asignacion)
            elif algorithm == 'vz':
                # Voraz
                voraz = load_voraz_module()
                M, E = parse_input_pd(contenido)
                A, F = voraz.rocV(len(M), len(E), M, E)
                # Formatear salida del voraz similar a la especificación
                partes = [f"{F:.6f}"]
                for est, ms in E:
                    asignadas = A.get(est, [])
                    partes.append(f"{est},{len(asignadas)}")
                    for m in asignadas:
                        partes.append(str(m))
                salida_formateada = '\n'.join(partes)
            else:
                # Programación Dinámica
                pd_mod = load_pd_module()
                M, E = parse_input_pd(contenido)
                solucion, insat = pd_mod.rocPD(M, E)
                salida_formateada = format_output_pd(insat, solucion, E)
        except MemoryError as me:
            msg = f'Error de memoria / combinaciones: {me}'
            self.root.after(0, lambda m=msg: self.finish_process(error=m))
            return
        except TimeoutError:
            self.root.after(0, lambda: self.finish_process(timeout=True))
            return
        except Exception as e:
            msg = f'Error al parsear/ejecutar: {e}'
            # Capture message in default arg so the variable doesn't become unbound
            self.root.after(0, lambda m=msg: self.finish_process(error=m))
            return
        
        # Escribir salida en archivo según algoritmo
        try:
            if algorithm == 'fb':
                out_name = 'salida_fuerzabruta1.txt'
            elif algorithm == 'vz':
                out_name = 'salida_voraz1.txt'
            else:
                out_name = 'salida_dinamica1.txt'
            out_path = write_generic_output(out_name, salida_formateada)
            salida_formateada = salida_formateada + '\n\nArchivo escrito en: ' + str(out_path)
        except Exception as e:
            # No hacemos fallar el flujo por error de IO; mostramos el error
            salida_formateada = salida_formateada + f"\n\n(Advertencia: no se pudo escribir archivo: {e})"

        self.root.after(0, lambda: self.finish_process(output=salida_formateada))

    def finish_process(self, output=None, error=None, timeout=False):
        # Detener animación de 'Cargando...'
        if self._loading_anim_id:
            self.root.after_cancel(self._loading_anim_id)
            self._loading_anim_id = None
        self.loading_label.config(text='')
        self.run_btn.config(state='normal')
        self.open_btn.config(state='normal')
        if error:
            messagebox.showerror('Error', error)
            return
        if timeout:
            messagebox.showerror('No se encontró solución', 'No se encontró solución en menos de 5 minutos')
            return
        if output is not None:
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.END, output)

    def animate_loading(self):
        # Animar el texto 'Cargando...' con puntos
        estados = ['Cargando   ', 'Cargando.  ', 'Cargando.. ', 'Cargando...']
        self.loading_label.config(text=estados[self._loading_anim_state % 4])
        self._loading_anim_state = (self._loading_anim_state + 1) % 4
        self._loading_anim_id = self.root.after(400, self.animate_loading)


def get_available_memory_bytes() -> int | None:
    # Intentar psutil
    try:
        import psutil  # type: ignore
        vm = psutil.virtual_memory()
        return int(vm.available)
    except Exception:
        pass

    # Fallback Windows API
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ('dwLength', ctypes.c_uint),
                ('dwMemoryLoad', ctypes.c_uint),
                ('ullTotalPhys', ctypes.c_ulonglong),
                ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong),
                ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong),
                ('ullAvailVirtual', ctypes.c_ulonglong),
                ('sullAvailExtendedVirtual', ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        return int(stat.ullAvailPhys)
    except Exception:
        return None


def main():
    root = tk.Tk()
    app = App(root)
    root.geometry('1100x600')
    root.mainloop()


if __name__ == '__main__':
    main()
