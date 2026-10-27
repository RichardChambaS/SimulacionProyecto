"""Interfaz del estudio con los símbolos del informe y opciones de ejecución."""

from decimal import Decimal, InvalidOperation
from math import isfinite
from time import monotonic
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.modelo.configuracion import Configuracion
from app.planificacion import estimar_trabajo
from app.vista.graficos import ESPECIFICACIONES, GraficadorServicio


AZUL = "#2458a6"
TEXTO = "#172b46"
GRIS = "#64748b"
FONDO = "#f1f4f8"


def leer_entero(texto, nombre):
    """Acepta enteros exactos sin truncar ni perder precisión con float."""
    try:
        valor = Decimal(texto.strip().replace(",", "."))
    except InvalidOperation as error:
        raise ValueError(f"{nombre} debe ser un número entero.") from error
    if not valor.is_finite() or valor != valor.to_integral_value() or valor.adjusted() > 308:
        raise ValueError(f"{nombre} debe ser un número entero finito representable.")
    return int(valor)


def numero(valor, decimales=2):
    return f"{valor:.{decimales}f}".replace(".", ",")


def cantidad(valor):
    return f"{valor:,.0f}".replace(",", " ") if isfinite(valor) else "demasiados"


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Centro de llamadas · Erlang-C y simulación")
        ancho = min(1200, self.winfo_screenwidth()-60)
        alto = min(820, self.winfo_screenheight()-90)
        self.geometry(f"{ancho}x{alto}+30+30")
        self.minsize(1030, 700)
        self.configure(bg=FONDO)
        self._callback_ejecucion = None
        self._callback_cancelacion = None
        self._callback_exportacion = None
        self._tiene_resultados = False
        self._resultado = None
        self._ocupado = False
        self._cancelando = False
        self._tick_id = None
        self._ayuda_id = None
        self._avance = (0, 0)
        self._entradas = []
        self._controles = []
        self._graficadores = {}
        self._canvases = {}
        self._vars = {}
        self._estilos()
        self._construir_interfaz()
        self._cargar_valores_iniciales()
        self.bind("<MouseWheel>", self._rueda)

    def _estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(".", font=("Segoe UI", 10), foreground=TEXTO)
        estilo.configure("TFrame", background=FONDO)
        estilo.configure("TLabel", background=FONDO)
        estilo.configure("Panel.TFrame", background="white")
        estilo.configure("Panel.TLabel", background="white")
        estilo.configure("Ayuda.TLabel", background="white", foreground=GRIS, font=("Segoe UI", 9))
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 20, "bold"))
        estilo.configure("Seccion.TLabel", background="white", font=("Segoe UI", 12, "bold"))
        estilo.configure("Dato.TLabel", background="white", foreground=AZUL, font=("Segoe UI", 11, "bold"))
        estilo.configure("TButton", padding=(12, 7), background="#e6ecf5", borderwidth=0)
        estilo.map("TButton", background=[("active", "#d6e2f3")])
        estilo.configure("Principal.TButton", background=AZUL, foreground="white", font=("Segoe UI", 10, "bold"))
        estilo.map("Principal.TButton", background=[("disabled", "#bbc8dc"), ("active", "#1c4381")], foreground=[("disabled", "white")])
        estilo.configure("TEntry", padding=6, fieldbackground="white", bordercolor="#d4dce8", lightcolor="#d4dce8")
        estilo.configure("TRadiobutton", background="white", padding=(0, 3))
        estilo.configure("TNotebook", background="white", borderwidth=0)
        estilo.configure("TNotebook.Tab", padding=(12, 7), background="#e9eef6")
        estilo.map("TNotebook.Tab", background=[("selected", "white")], foreground=[("selected", AZUL)])
        estilo.configure("Treeview", rowheight=28, background="white", fieldbackground="white", borderwidth=0)
        estilo.configure("Treeview.Heading", background="#e9eef6", foreground=TEXTO, font=("Segoe UI", 9, "bold"), padding=5, relief="flat", borderwidth=0, lightcolor="#e9eef6", darkcolor="#e9eef6")
        estilo.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", TEXTO)])
        estilo.configure("TProgressbar", background=AZUL, troughcolor="#e8edf5", borderwidth=0, thickness=6)

    def _texto(self, padre, texto, estilo="Panel.TLabel", **opciones):
        w = ttk.Label(padre, text=texto, style=estilo, **opciones)
        w.pack(anchor="w", fill="x")
        return w

    def _construir_interfaz(self):
        cabecera = ttk.Frame(self, padding=(20, 10, 20, 8))
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="Centro de llamadas", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(cabecera, text="Configura el modelo, compara los agentes y explica los resultados.", foreground=GRIS).pack(anchor="w", pady=(3, 0))
        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)
        lateral = ttk.Frame(cuerpo, style="Panel.TFrame", width=350)
        lateral.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        lateral.pack_propagate(False)
        self._lateral_canvas = tk.Canvas(lateral, background="white", highlightthickness=0)
        barra = ttk.Scrollbar(lateral, orient="vertical", command=self._lateral_canvas.yview)
        self._lateral_canvas.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self._lateral_canvas.pack(side="left", fill="both", expand=True)
        contenido = ttk.Frame(self._lateral_canvas, style="Panel.TFrame", padding=16)
        self._lateral_contenido = contenido
        ventana = self._lateral_canvas.create_window((0, 0), window=contenido, anchor="nw")
        contenido.bind("<Configure>", lambda e: self._lateral_canvas.configure(scrollregion=self._lateral_canvas.bbox("all")))
        self._lateral_canvas.bind("<Configure>", lambda e: self._lateral_canvas.itemconfigure(ventana, width=e.width))
        self._texto(contenido, "1. Parámetros del modelo", "Seccion.TLabel")
        self._texto(contenido, "Los mismos símbolos del informe.", "Ayuda.TLabel")
        campos = ttk.Frame(contenido, style="Panel.TFrame")
        campos.pack(fill="x", pady=(12, 0))
        campos.columnconfigure(0, weight=1)
        campos.columnconfigure(1, weight=1)
        for i, (etiqueta, clave) in enumerate([
            ("λ · Llegadas por minuto", "lambda_minuto"),
            ("h · Atención media (min)", "atencion_media_minutos"),
            ("t₀ · Espera máxima (s)", "umbral_segundos"),
            ("S₀ · Meta de servicio (%)", "meta_servicio_porcentaje"),
        ]):
            self._campo(campos, etiqueta, clave, i//2, i%2)
        self._equivalencias = self._texto(contenido, "", "Ayuda.TLabel", wraplength=265)
        self._equivalencias.pack_configure(pady=(6, 10))
        self._derivados = self._texto(contenido, "", "Dato.TLabel", wraplength=265)
        ttk.Separator(contenido).pack(fill="x", pady=16)
        self._texto(contenido, "2. Agentes por escenario", "Seccion.TLabel")
        self._modo_agentes = tk.StringVar(self, "automatico")
        for texto, valor in [("Automático según la demanda", "automatico"), ("Elegir los tres escenarios", "manual")]:
            radio = ttk.Radiobutton(contenido, text=texto, value=valor, variable=self._modo_agentes, command=self._cambiar_modo)
            radio.pack(anchor="w", pady=(4, 0))
            self._controles.append(radio)
        agentes = ttk.Frame(contenido, style="Panel.TFrame")
        self._marco_agentes = agentes
        agentes.pack(fill="x", pady=(8, 0))
        self._agentes_vars = []
        self._agentes_entradas = []
        for i, valor in enumerate((4, 6, 8)):
            agentes.columnconfigure(i, weight=1)
            marco = ttk.Frame(agentes, style="Panel.TFrame")
            marco.grid(row=0, column=i, sticky="ew", padx=(0, 5))
            ttk.Label(marco, text=f"c{i+1}", style="Ayuda.TLabel").pack(anchor="w")
            var = tk.StringVar(self, str(valor))
            entrada = ttk.Entry(marco, textvariable=var, width=6)
            entrada.pack(fill="x")
            self._agentes_vars.append(var)
            self._agentes_entradas.append(entrada)
            var.trace_add("write", self._programar_ayudas)
        self._agentes_ayuda = self._texto(contenido, "", "Ayuda.TLabel", wraplength=265)
        self._agentes_ayuda.pack_configure(pady=(7, 0))
        ttk.Separator(contenido).pack(fill="x", pady=16)
        self._avanzadas_abiertas = False
        self.boton_opciones = ttk.Button(contenido, text="▸ Opciones de simulación", command=self._alternar_opciones)
        self.boton_opciones.pack(fill="x")
        self._opciones = ttk.Frame(contenido, style="Panel.TFrame")
        for i,(etiqueta, clave) in enumerate([
            ("Tiempo medido (min)", "duracion_minutos"),
            ("Tiempo inicial (min)", "calentamiento_minutos"),
            ("R · Repeticiones", "repeticiones"),
            ("Semilla", "semilla"),
        ]):
            self._campo(self._opciones, etiqueta, clave, i//2, i%2)
        self._opciones.columnconfigure(0, weight=1)
        self._opciones.columnconfigure(1, weight=1)
        ttk.Label(self._opciones, text="El tiempo inicial es el calentamiento: se simula, pero no se mide. La semilla permite repetir el experimento.", style="Ayuda.TLabel", wraplength=265).grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self._carga_label = self._texto(contenido, "", "Ayuda.TLabel", wraplength=265)
        self._carga_label.pack_configure(pady=(12, 10))
        self.boton_restaurar = ttk.Button(contenido, text="Restablecer el caso del informe", command=self._cargar_valores_iniciales)
        self.boton_restaurar.pack(fill="x")
        self._controles.append(self.boton_restaurar)

        derecho = ttk.Frame(cuerpo, style="Panel.TFrame", padding=16)
        derecho.grid(row=0, column=1, sticky="nsew")
        acciones = ttk.Frame(derecho, style="Panel.TFrame")
        acciones.pack(fill="x")
        self.boton_ejecutar = ttk.Button(acciones, text="Ejecutar simulación", style="Principal.TButton", command=self._on_ejecutar)
        self.boton_ejecutar.pack(side="left")
        self.boton_cancelar = ttk.Button(acciones, text="Cancelar", state="disabled", command=self._on_cancelar)
        self.boton_cancelar.pack(side="left", padx=8)
        self.boton_exportar = ttk.Button(acciones, text="Exportar", state="disabled", command=self._on_exportar)
        self.boton_exportar.pack(side="right")
        self.etiqueta_estado = ttk.Label(derecho, text="Listo para ejecutar", style="Ayuda.TLabel")
        self.etiqueta_estado.pack(fill="x", pady=(6, 4))
        self.progreso = ttk.Progressbar(derecho, mode="determinate", maximum=90)
        self.progreso.pack(fill="x", pady=(0, 10))
        self._texto(derecho, "Resultados del estudio", "Seccion.TLabel")
        self.etiqueta_resumen = self._texto(derecho, "Ejecuta la simulación para comparar los tres escenarios.", wraplength=700)
        self.etiqueta_resumen.pack_configure(pady=(5, 3))
        self.etiqueta_configuracion = self._texto(derecho, "", "Ayuda.TLabel", wraplength=700)
        self.etiqueta_configuracion.pack_configure(pady=(0, 6))
        marco_tabla = ttk.Frame(derecho, style="Panel.TFrame")
        marco_tabla.pack(fill="x")
        self.tabla = self._crear_tabla(marco_tabla, [
            ("agentes", "c · Agentes", 75), ("servicio", "SL(t₀) · Servicio (%)", 145),
            ("espera", "Wq · Espera (s)", 115), ("uso", "ρ · Utilización (%)", 130),
            ("estado", "Meta", 120),
        ], 3)
        self.tabla.tag_configure("cumple", foreground="#176046")
        self.tabla.tag_configure("no_cumple", foreground="#a13c24")
        self.tabla.tag_configure("revisar", foreground="#966117")
        self._texto(derecho, "Medias simuladas. La lectura de la meta considera el intervalo del 95 %.", "Ayuda.TLabel", wraplength=700).pack_configure(pady=(5, 8))
        self.pestanas = ttk.Notebook(derecho)
        self.pestanas.pack(fill="both", expand=True)
        for metrica, (titulo, _, _) in ESPECIFICACIONES.items():
            marco = ttk.Frame(self.pestanas, style="Panel.TFrame")
            self.pestanas.add(marco, text=titulo)
            graficador = GraficadorServicio(metrica)
            graficador.eje.text(.5, .5, "Las gráficas aparecerán al completar el estudio.", ha="center", va="center", color=GRIS, transform=graficador.eje.transAxes)
            canvas = graficador.obtener_widget_canvas(master=marco)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()
            self._graficadores[metrica] = graficador
            self._canvases[metrica] = canvas
        medidas = ttk.Frame(self.pestanas, style="Panel.TFrame", padding=10)
        self.pestanas.add(medidas, text="Medidas")
        selector = ttk.Frame(medidas, style="Panel.TFrame")
        selector.pack(fill="x", pady=(0, 10))
        ttk.Label(selector, text="Mostrar valores de", style="Panel.TLabel").pack(side="left", padx=(0, 8))
        self._fuente_medidas = tk.StringVar(self, "Simulación")
        combo = ttk.Combobox(selector, textvariable=self._fuente_medidas, values=("Simulación", "Erlang-C"), state="readonly", width=15)
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self._llenar_medidas())
        marco_medidas = ttk.Frame(medidas, style="Panel.TFrame")
        marco_medidas.pack(fill="x")
        self.tabla_medidas = self._crear_tabla(marco_medidas, [
            ("c", "c", 45), ("sl", "SL(t₀) (%)", 95), ("wq", "Wq (s)", 80),
            ("rho", "ρ (%)", 75), ("pc", "P_C (%)", 85), ("lq", "Lq (llamadas)", 120),
        ], 3)
        self._texto(medidas, "SL(t₀): atención dentro del tiempo permitido.\nWq: espera media antes de iniciar la atención.\nρ: utilización de los agentes.\nP_C: probabilidad de tener que esperar.\nLq: llamadas esperando, en promedio.", "Ayuda.TLabel", wraplength=650).pack_configure(pady=(12, 0))
        self._texto(derecho, "El mínimo es teórico (Erlang-C). Wq se muestra en segundos; en las fórmulas se usan minutos.", "Ayuda.TLabel", wraplength=700).pack_configure(side="bottom", before=self.pestanas, pady=(10, 0))
        derecho.bind("<Configure>", self._ajustar_resumen)
        for var in self._vars.values():
            var.trace_add("write", self._programar_ayudas)

    def _campo(self, padre, etiqueta, clave, fila, columna):
        marco = ttk.Frame(padre, style="Panel.TFrame")
        marco.grid(row=fila, column=columna, sticky="ew", padx=(0, 6), pady=(0, 9))
        ttk.Label(marco, text=etiqueta, style="Ayuda.TLabel").pack(anchor="w")
        var = tk.StringVar(self)
        self._vars[clave] = var
        entrada = ttk.Entry(marco, textvariable=var, width=12)
        entrada.pack(fill="x", pady=(3, 0))
        self._entradas.append(entrada)

    @staticmethod
    def _crear_tabla(marco, columnas, altura):
        tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings", height=altura)
        for clave, etiqueta, ancho in columnas:
            tabla.heading(clave, text=etiqueta)
            tabla.column(clave, width=ancho, minwidth=ancho, stretch=True, anchor="center")
        horizontal = ttk.Scrollbar(marco, orient="horizontal", command=tabla.xview)
        def ajustar_barra(inicio, fin):
            horizontal.set(inicio, fin)
            if float(inicio) <= 0 and float(fin) >= 1:
                horizontal.grid_remove()
            else:
                horizontal.grid(row=1, column=0, sticky="ew")
        tabla.configure(xscrollcommand=ajustar_barra)
        tabla.grid(row=0, column=0, sticky="nsew")
        horizontal.grid(row=1, column=0, sticky="ew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        return tabla

    def _rueda(self, evento):
        widget = self.winfo_containing(evento.x_root, evento.y_root)
        while widget is not None:
            if widget is self._lateral_contenido:
                self._lateral_canvas.yview_scroll(-int(evento.delta/120), "units")
                return
            widget = getattr(widget, "master", None)

    def _ajustar_resumen(self, evento):
        for etiqueta in evento.widget.winfo_children():
            if isinstance(etiqueta, ttk.Label):
                etiqueta.configure(wraplength=max(300, evento.width-32))

    def _alternar_opciones(self):
        self._avanzadas_abiertas = not self._avanzadas_abiertas
        if self._avanzadas_abiertas:
            self._opciones.pack(fill="x", before=self._carga_label, pady=(10, 0))
        else:
            self._opciones.pack_forget()
        self.boton_opciones.configure(text=("▾" if self._avanzadas_abiertas else "▸")+" Opciones de simulación")

    def _cargar_valores_iniciales(self):
        cfg = Configuracion()
        for clave, variable in self._vars.items():
            if clave == "lambda_minuto":
                valor = cfg.tasa_llegadas_minuto
            elif clave == "meta_servicio_porcentaje":
                valor = cfg.meta_servicio*100
            else:
                valor = getattr(cfg, clave)
            variable.set(f"{valor:g}".replace(".", ","))
        self._modo_agentes.set("automatico")
        for var, n in zip(self._agentes_vars, (4, 6, 8)):
            var.set(str(n))
        self._cambiar_modo()

    def obtener_configuracion(self):
        valores = {}
        for clave, var in self._vars.items():
            if clave in {"repeticiones", "semilla"}:
                valores[clave] = leer_entero(var.get(), clave.capitalize())
            else:
                try:
                    valores[clave] = float(var.get().strip().replace(",", "."))
                except (ValueError, OverflowError) as error:
                    raise ValueError("Revisa los parámetros: todos los campos deben contener números.") from error
        valores["tasa_llegadas_hora"] = valores.pop("lambda_minuto")*60
        valores["meta_servicio"] = valores.pop("meta_servicio_porcentaje")/100
        if not isfinite(valores["meta_servicio"]) or not 0 < valores["meta_servicio"] < 1:
            raise ValueError("S₀ · La meta debe ser mayor que 0 y menor que 100 %.")
        if not isfinite(valores["tasa_llegadas_hora"]) or valores["tasa_llegadas_hora"] <= 0:
            raise ValueError("λ · Las llegadas por minuto deben ser positivas y finitas.")
        cfg = Configuracion(**valores)
        cfg.validar()
        return cfg

    def obtener_agentes(self):
        if self._modo_agentes.get() == "automatico":
            return None
        return [leer_entero(var.get(), f"Agentes del escenario {i}") for i,var in enumerate(self._agentes_vars, 1)]

    def _cambiar_modo(self):
        manual = self._modo_agentes.get() == "manual"
        if manual:
            self._marco_agentes.pack(fill="x", before=self._agentes_ayuda, pady=(8, 0))
        else:
            self._marco_agentes.pack_forget()
        for entrada in self._agentes_entradas:
            entrada.configure(state="normal" if manual and not self._ocupado else "disabled")
        self._agentes_ayuda.configure(text=("Cada escenario debe cumplir c > A. El mínimo teórico se calcula por separado." if manual else "El programa elige tres escenarios según la demanda. Para el caso del informe: 4, 6 y 8."))
        self._programar_ayudas()

    def _programar_ayudas(self, *_):
        if self._ayuda_id is not None:
            self.after_cancel(self._ayuda_id)
        self._ayuda_id = self.after(180, self._actualizar_ayudas)

    def _actualizar_ayudas(self):
        self._ayuda_id = None
        try:
            cfg = self.obtener_configuracion()
            self._equivalencias.configure(text=f"λ = {numero(cfg.tasa_llegadas_hora, 1)} llamadas/h · t₀ = {numero(cfg.umbral_minutos, 3)} min · S₀ = {numero(cfg.meta_servicio)}")
            self._derivados.configure(text=f"μ = 1/h = {numero(cfg.tasa_servicio_minuto, 3)}/min\nA = λh = {numero(cfg.carga_erlangs)} erlangs")
            carga = estimar_trabajo(cfg, self.obtener_agentes())
            prefijo = "Atención: " if carga.nivel != "normal" else ""
            detalle = ("Reduce los valores antes de ejecutar." if carga.nivel == "bloqueado" else "Puede tardar varios minutos." if carga.nivel == "alto" else "Incluye calentamiento, repeticiones y tres escenarios.")
            self._carga_label.configure(text=f"{prefijo}≈ {cantidad(carga.eventos)} eventos. {detalle}", foreground="#9b4c12" if prefijo else GRIS)
        except (ValueError, OverflowError):
            self._equivalencias.configure(text="Completa los parámetros con valores válidos.")
            self._derivados.configure(text="μ = 1/h     A = λh")
            self._carga_label.configure(text="Revisa los valores antes de ejecutar.", foreground=GRIS)

    def confirmar_carga(self, carga):
        return messagebox.askokcancel("Ejecución grande", f"Se estiman {cantidad(carga.eventos)} eventos.\n\n{carga.mensaje}\n\nPuedes cancelar durante el cálculo. ¿Quieres continuar?", icon="warning", default="cancel", parent=self)

    def vincular_ejecucion(self, callback):
        self._callback_ejecucion = callback

    def vincular_cancelacion(self, callback):
        self._callback_cancelacion = callback

    def vincular_exportacion(self, callback):
        self._callback_exportacion = callback

    def _on_ejecutar(self):
        if self._callback_ejecucion:
            self._callback_ejecucion()

    def _on_cancelar(self):
        if self._callback_cancelacion:
            self._callback_cancelacion()

    def _on_exportar(self):
        if self._callback_exportacion:
            self._callback_exportacion()

    def establecer_ocupado(self, ocupado):
        self._ocupado = ocupado
        self.boton_ejecutar.configure(state="disabled" if ocupado else "normal")
        self.boton_cancelar.configure(state="normal" if ocupado else "disabled")
        self.boton_exportar.configure(state="normal" if self._tiene_resultados and not ocupado else "disabled")
        for entrada in self._entradas+self._controles:
            entrada.configure(state="disabled" if ocupado else "normal")
        self._cambiar_modo()
        if ocupado:
            self._inicio = monotonic()
            self._cancelando = False
            self._avance = (0, leer_entero(self._vars["repeticiones"].get(), "Repeticiones")*3)
            self.progreso.configure(value=0, maximum=self._avance[1])
            self._latido()
        elif self._tick_id is not None:
            self.after_cancel(self._tick_id)
            self._tick_id = None

    def _latido(self):
        self._tick_id = None
        if not self._ocupado:
            return
        segundos = int(monotonic()-self._inicio)
        actual, total = self._avance
        estado = "Deteniendo" if self._cancelando else f"Procesando repetición {min(actual+1, total)} de {total}"
        self.etiqueta_estado.configure(text=f"{estado} · {segundos//60:02d}:{segundos%60:02d} transcurridos")
        self._tick_id = self.after(250, self._latido)

    def mostrar_progreso(self, actual, total):
        self._avance = (actual, total)
        self.progreso.configure(maximum=total, value=actual)

    def mostrar_cancelacion(self):
        self._cancelando = True
        self.boton_cancelar.configure(state="disabled")
        self.etiqueta_estado.configure(text="Deteniendo el estudio…")

    def mostrar_estado(self, texto):
        self.etiqueta_estado.configure(text=texto)

    def mostrar_error(self, mensaje):
        messagebox.showerror("Revisa la configuración", mensaje, parent=self)

    def solicitar_directorio_exportacion(self):
        return filedialog.askdirectory(title="Carpeta para guardar el estudio", parent=self)

    def mostrar_exportacion(self, ruta):
        messagebox.showinfo("Estudio exportado", f"Archivos guardados en:\n{ruta}", parent=self)

    def mostrar_resultados(self, resultado):
        self._resultado = resultado
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        lecturas = {"Cumplimiento respaldado": ("Cumple", "cumple"), "Incumplimiento respaldado": ("No cumple", "no_cumple")}
        for e in resultado.escenarios:
            s = e.simulado
            estado, tag = lecturas.get(e.estado_servicio, ("No concluyente", "revisar"))
            self.tabla.insert("", "end", values=(e.agentes, numero(s.nivel_servicio*100)+" %", numero(s.espera_media_minutos*60), numero(s.utilizacion*100), estado), tags=(tag,))
        cfg = resultado.configuracion
        agentes = ", ".join(str(e.agentes) for e in resultado.escenarios)
        self.etiqueta_resumen.configure(text=f"Mínimo teórico: {resultado.minimo_teorico} agentes. Meta: {cfg.meta_servicio*100:g} % con espera de hasta {cfg.umbral_segundos:g} s.")
        self.etiqueta_configuracion.configure(text=f"Último estudio · c = {agentes} · λ = {numero(cfg.tasa_llegadas_minuto, 3)}/min · h = {cfg.atencion_media_minutos:g} min · R = {cfg.repeticiones}\nMedición {cfg.duracion_minutos:g} min · inicial {cfg.calentamiento_minutos:g} min · semilla {cfg.semilla}")
        self._llenar_medidas()
        for graficador in self._graficadores.values():
            graficador.dibujar(resultado.escenarios, cfg.meta_servicio, cfg.umbral_segundos)
        self._tiene_resultados = True
        self.mostrar_estado("Estudio completado")

    def _llenar_medidas(self):
        for item in self.tabla_medidas.get_children():
            self.tabla_medidas.delete(item)
        if self._resultado is None:
            return
        for e in self._resultado.escenarios:
            v = e.simulado if self._fuente_medidas.get() == "Simulación" else e.teorico
            self.tabla_medidas.insert("", "end", values=(e.agentes, numero(v.nivel_servicio*100), numero(v.espera_media_minutos*60), numero(v.utilizacion*100), numero(v.probabilidad_espera*100), numero(v.longitud_media_cola, 4)))

    def destroy(self):
        for id_ in (self._tick_id, self._ayuda_id):
            if id_ is not None:
                self.after_cancel(id_)
        super().destroy()

    def iniciar(self):
        self.mainloop()
