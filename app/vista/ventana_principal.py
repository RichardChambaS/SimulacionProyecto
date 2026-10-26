"""Ventana principal con Tkinter para el estudio de Erlang-C vs simulación."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.modelo.configuracion import Configuracion
from app.vista.graficos import GraficadorServicio


class VentanaPrincipal(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Simulación M/M/c - Erlang-C vs Simulación de Eventos Discretos")
        self.geometry("980x720")
        self.minsize(880, 640)

        self._callback_ejecucion = None
        self._graficador = GraficadorServicio()
        self._canvas = None

        self._construir_interfaz()
        self._cargar_valores_iniciales()

    def _construir_interfaz(self) -> None:
        marco_parametros = ttk.LabelFrame(self, text="Parámetros")
        marco_parametros.pack(fill="x", padx=10, pady=(10, 5))

        self._vars = {
            "tasa_llegadas_hora": tk.StringVar(),
            "atencion_media_minutos": tk.StringVar(),
            "meta_servicio_porcentaje": tk.StringVar(),
            "umbral_segundos": tk.StringVar(),
            "duracion_minutos": tk.StringVar(),
            "calentamiento_minutos": tk.StringVar(),
            "repeticiones": tk.StringVar(),
            "semilla": tk.StringVar(),
        }

        campos = [
            ("Llegadas (llamadas/hora)", "tasa_llegadas_hora"),
            ("Atención media (minutos)", "atencion_media_minutos"),
            ("Meta de servicio (%)", "meta_servicio_porcentaje"),
            ("Umbral (segundos)", "umbral_segundos"),
            ("Duración medida (minutos)", "duracion_minutos"),
            ("Calentamiento (minutos)", "calentamiento_minutos"),
            ("Repeticiones", "repeticiones"),
            ("Semilla", "semilla"),
        ]

        for i, (etiqueta, clave) in enumerate(campos):
            fila = i // 4
            col = i % 4
            frame_campo = ttk.Frame(marco_parametros)
            frame_campo.grid(row=fila, column=col, padx=6, pady=4, sticky="ew")
            ttk.Label(frame_campo, text=etiqueta).pack(anchor="w")
            ttk.Entry(frame_campo, textvariable=self._vars[clave]).pack(fill="x")

        marco_parametros.columnconfigure((0, 1, 2, 3), weight=1)

        marco_accion = ttk.Frame(self)
        marco_accion.pack(fill="x", padx=10, pady=5)
        self.boton_ejecutar = ttk.Button(
            marco_accion, text="Ejecutar estudio", command=self._on_ejecutar
        )
        self.boton_ejecutar.pack(side="left")
        self.etiqueta_estado = ttk.Label(marco_accion, text="Listo")
        self.etiqueta_estado.pack(side="left", padx=10)

        marco_tabla = ttk.LabelFrame(self, text="Comparación por escenarios")
        marco_tabla.pack(fill="both", expand=True, padx=10, pady=5)

        columnas = (
            "agentes",
            "util_teor",
            "util_sim",
            "serv_teor",
            "serv_sim",
            "ic95",
            "espera_teor",
            "espera_sim",
            "llamadas",
        )
        self.tabla = ttk.Treeview(
            marco_tabla, columns=columnas, show="headings", height=6
        )
        encabezados = [
            ("agentes", "Agentes"),
            ("util_teor", "Util. teórica"),
            ("util_sim", "Util. simulada"),
            ("serv_teor", "Servicio teórico"),
            ("serv_sim", "Servicio simulado"),
            ("ic95", "IC 95% sim. (aprox.)"),
            ("espera_teor", "Espera teórica (min)"),
            ("espera_sim", "Espera simulada (min)"),
            ("llamadas", "Llamadas medidas"),
        ]
        for col, texto in encabezados:
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=110, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=5, pady=5)

        marco_resumen = ttk.LabelFrame(self, text="Resumen")
        marco_resumen.pack(fill="x", padx=10, pady=5)
        self.etiqueta_resumen = ttk.Label(
            marco_resumen,
            text="Mínimo teórico: - | Escenarios mostrados según reglas del estudio.",
        )
        self.etiqueta_resumen.pack(anchor="w", padx=5, pady=3)

        marco_grafica = ttk.LabelFrame(self, text="Nivel de servicio vs número de agentes")
        marco_grafica.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self._canvas_frame = ttk.Frame(marco_grafica)
        self._canvas_frame.pack(fill="both", expand=True)
        self._actualizar_canvas()

    def _cargar_valores_iniciales(self) -> None:
        cfg = Configuracion()
        self._vars["tasa_llegadas_hora"].set(str(cfg.tasa_llegadas_hora))
        self._vars["atencion_media_minutos"].set(str(cfg.atencion_media_minutos))
        self._vars["meta_servicio_porcentaje"].set(str(cfg.meta_servicio * 100.0))
        self._vars["umbral_segundos"].set(str(cfg.umbral_segundos))
        self._vars["duracion_minutos"].set(str(cfg.duracion_minutos))
        self._vars["calentamiento_minutos"].set(str(cfg.calentamiento_minutos))
        self._vars["repeticiones"].set(str(cfg.repeticiones))
        self._vars["semilla"].set(str(cfg.semilla))

    def _actualizar_canvas(self) -> None:
        for widget in self._canvas_frame.winfo_children():
            widget.destroy()
        canvas = self._graficador.obtener_widget_canvas()
        self._canvas = canvas
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def obtener_configuracion(self) -> Configuracion:
        try:
            tasa_hora = float(self._vars["tasa_llegadas_hora"].get())
            atencion_min = float(self._vars["atencion_media_minutos"].get())
            meta_porcentaje = float(self._vars["meta_servicio_porcentaje"].get())
            umbral_seg = float(self._vars["umbral_segundos"].get())
            duracion_min = float(self._vars["duracion_minutos"].get())
            calentamiento_min = float(self._vars["calentamiento_minutos"].get())
            repeticiones = int(float(self._vars["repeticiones"].get()))
            semilla = int(float(self._vars["semilla"].get()))
        except ValueError as exc:
            raise ValueError("Los valores introducidos no son numéricos válidos.") from exc

        meta_proporcion = meta_porcentaje / 100.0
        configuracion = Configuracion(
            tasa_llegadas_hora=tasa_hora,
            atencion_media_minutos=atencion_min,
            meta_servicio=meta_proporcion,
            umbral_segundos=umbral_seg,
            duracion_minutos=duracion_min,
            calentamiento_minutos=calentamiento_min,
            repeticiones=repeticiones,
            semilla=semilla,
        )
        return configuracion

    def vincular_ejecucion(self, callback) -> None:
        self._callback_ejecucion = callback

    def _on_ejecutar(self) -> None:
        if self._callback_ejecucion is not None:
            self._callback_ejecucion()

    def establecer_ocupado(self, ocupado: bool) -> None:
        if ocupado:
            self.boton_ejecutar.config(state="disabled")
            self.etiqueta_estado.config(text="Calculando...")
            self.config(cursor="watch")
        else:
            self.boton_ejecutar.config(state="normal")
            self.etiqueta_estado.config(text="Listo")
            self.config(cursor="")

    def mostrar_error(self, mensaje: str) -> None:
        messagebox.showerror("Error", mensaje)

    def mostrar_resultados(self, resultado) -> None:
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for escenario in resultado.escenarios:
            teorico = escenario.teorico
            simulado = escenario.simulado
            if simulado.intervalo_servicio_95 is not None:
                inf, sup = simulado.intervalo_servicio_95
                ic_texto = f"[{inf*100:.2f}%, {sup*100:.2f}%]"
            else:
                ic_texto = "-"
            llamadas = simulado.llamadas_medidas if simulado.llamadas_medidas is not None else "-"
            self.tabla.insert(
                "",
                "end",
                values=(
                    escenario.agentes,
                    f"{teorico.utilizacion*100:.1f}%",
                    f"{simulado.utilizacion*100:.1f}%",
                    f"{teorico.nivel_servicio*100:.2f}%",
                    f"{simulado.nivel_servicio*100:.2f}%",
                    ic_texto,
                    f"{teorico.espera_media_minutos:.4f}",
                    f"{simulado.espera_media_minutos:.4f}",
                    llamadas,
                ),
            )

        self.etiqueta_resumen.config(
            text=f"Mínimo teórico: {resultado.minimo_teorico} agentes | "
            "Ver reglas: cumplimiento respaldado si límite inferior del IC >= meta; "
            "incumplimiento si límite superior < meta."
        )

        self._graficador.dibujar(resultado.escenarios)
        self._actualizar_canvas()

    def iniciar(self) -> None:
        self.mainloop()
