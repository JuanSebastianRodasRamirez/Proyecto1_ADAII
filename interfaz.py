import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import importlib.util
import sys

from typing import List, Any

# Antes las definiciones venían de `definiciones.py`. Ahora esas definiciones
# están inlinadas en `Fuerza bruta.py`. Inicialmente dejamos aliases a Any y
# los actualizaremos cuando carguemos dinámicamente el módulo de fuerza.
Estudiante: Any = Any
materia: Any = Any
materia_solicitada: Any = Any

PROJECT_DIR = Path(__file__).parent


def load_fuerza_module() -> Any:
    fb_path = PROJECT_DIR / 'Fuerza bruta.py'
    spec = importlib.util.spec_from_file_location('fuerza_bruta_mod', str(fb_path))
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"No se pudo cargar el módulo desde {fb_path}")
    fuerza = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules['fuerza_bruta_mod'] = fuerza
    spec.loader.exec_module(fuerza)  # type: ignore[attr-defined]
    # Exportar referencias útiles al módulo para que la interfaz pueda usarlas
    # (tipos y constructores). Esto permite que funciones como parse_input
    # puedan crear instancias de `materia` / `materia_solicitada`.
    global Estudiante, materia, materia_solicitada
    try:
        Estudiante = getattr(fuerza, 'estudiante')
        materia = getattr(fuerza, 'materia')
        materia_solicitada = getattr(fuerza, 'materia_solicitada')
    except Exception:
        # Si algún nombre falta, dejar los aliases como estaban y seguir
        pass
    return fuerza


def parse_input(text: str):
    """Parsea el texto de entrada según el formato del enunciado.

    Formato esperado:
    k
    codigo,cupo   (k líneas)
    r
    e1,s1         (por cada estudiante: código, número de solicitudes)
    m11,p11       (s1 líneas)
    m12,p12
    ...
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ValueError('Archivo vacío o sin líneas válidas')

    idx = 0
    try:
        k = int(lines[idx]); idx += 1
    except Exception as e:
        raise ValueError('No se pudo leer k (nº de materias) en la primera línea') from e

    # usamos los tipos importados arriba: materia, materia_solicitada, Estudiante

    M = []
    for _ in range(k):
        if idx >= len(lines):
            raise ValueError('Faltan líneas para las materias (M)')
        parts = lines[idx].split(',')
        if len(parts) != 2:
            raise ValueError(f'Formato inválido en materia: {lines[idx]}')
        codigo = int(parts[0]); cupo = int(parts[1])
        M.append(materia(codigo, cupo))
        idx += 1

    if idx >= len(lines):
        raise ValueError('Falta la línea con el número de estudiantes r')
    r = int(lines[idx]); idx += 1

    E = []
    for _ in range(r):
        if idx >= len(lines):
            raise ValueError('Faltan bloques de estudiantes')
        ej_parts = lines[idx].split(',')
        if len(ej_parts) != 2:
            raise ValueError(f'Formato inválido en estudiante header: {lines[idx]}')
        codigo_est = int(ej_parts[0]); s_j = int(ej_parts[1])
        idx += 1
        materias = []
        for _ in range(s_j):
            if idx >= len(lines):
                raise ValueError('Faltan líneas de materias solicitadas para un estudiante')
            mp = lines[idx].split(',')
            if len(mp) != 2:
                raise ValueError(f'Formato inválido en materia solicitada: {lines[idx]}')
            cod = int(mp[0]); pr = int(mp[1])
            materias.append(materia_solicitada(cod, pr))
            idx += 1
        E.append(Estudiante(codigo_est, materias))

    return M, E


from typing import Any as _Any

def format_output(insat: float, A: List[_Any]) -> str:
    """Formatea la salida de acuerdo al enunciado.

    Primera línea: costo (insatisfacción general) con 3 decimales
    Luego para cada estudiante en orden: una línea 'e_j,a_j' (código, cantidad asignadas)
    seguida de a_j líneas, cada una con el código de asignatura asignado.
    """
    out_lines = []
    out_lines.append(f"{insat:.3f}")
    for est in A:
        materias = list(est.getMateriasSolicitadas())
        out_lines.append(f"{est.getCodigo()},{len(materias)}")
        for m in materias:
            out_lines.append(str(m.codigo))

    return '\n'.join(out_lines)


class App:
    def __init__(self, root):
        self.root = root
        root.title('Interfaz - Asignación de materias (Fuerza bruta)')

        frm = tk.Frame(root)
        frm.pack(fill='both', expand=True, padx=8, pady=8)

        btn_frame = tk.Frame(frm)
        btn_frame.pack(fill='x')

        self.open_btn = tk.Button(btn_frame, text='Abrir archivo de prueba', command=self.open_file)
        self.open_btn.pack(side='left')

    # Nota: se eliminó la UI para el límite por combinaciones. La búsqueda
    # ahora sólo se detiene por tiempo (fijo a 300s en el módulo de fuerza bruta).

        tk.Label(btn_frame, text='Tiempo máximo: 5 minutos (300 segundos)').pack(side='left', padx=(8,2))



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

    def open_file(self):
        path = filedialog.askopenfilename(title='Seleccionar archivo de prueba', filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if not path:
            return
        self.current_path = path
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert(tk.END, content)
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
        t = threading.Thread(target=self.process_file_thread, daemon=True)
        t.start()

    def process_file_thread(self):
        # Esta función corre en un hilo aparte
        try:
            # Cargar primero el módulo de fuerza bruta para obtener los
            # constructores/tuplas (`materia`, `materia_solicitada`, `estudiante`)
            fuerza = load_fuerza_module()

            content = self.input_text.get('1.0', tk.END)
            M, E = parse_input(content)
        except Exception as e:
            self.root.after(0, lambda: self.finish_process(error=f'Error al parsear: {e}'))
            return
        try:
            A, insat = fuerza.rocFB(k=0, r=len(E), M=M, E=E)
        except MemoryError as me:
            self.root.after(0, lambda: self.finish_process(error=f'Error de memoria / combinaciones: {me}'))
            return
        except TimeoutError:
            self.root.after(0, lambda: self.finish_process(timeout=True))
            return
        except Exception as e:
            self.root.after(0, lambda: self.finish_process(error=f'Error al ejecutar: {e}'))
            return
        salida = format_output(insat, A)
        self.root.after(0, lambda: self.finish_process(output=salida))

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

    # Nota: calculate_max_limit eliminado porque ya no usamos límite por combinaciones


def get_available_memory_bytes() -> int | None:
    # Intentar psutil
    try:
        import psutil
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
