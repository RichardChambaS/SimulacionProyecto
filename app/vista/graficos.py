"""Gráficas compartidas por la ventana y la exportación, sin backend global."""

from matplotlib.figure import Figure

ESPECIFICACIONES = {
    "nivel_servicio": ("Nivel de servicio", "SL(t₀) · Servicio (%)", 100.0),
    "espera_media_minutos": ("Espera media", "Wq · Espera media (s)", 60.0),
    "utilizacion": ("Utilización", "ρ · Utilización (%)", 100.0),
}


def dibujar_comparacion(figura, escenarios, metrica, meta_servicio, umbral_segundos):
    """Dibuja medias e intervalos entre repeticiones en unidades de presentación."""
    escenarios = list(escenarios)
    titulo, etiqueta, factor = ESPECIFICACIONES[metrica]
    figura.clear()
    eje = figura.add_subplot(111)
    agentes = [escenario.agentes for escenario in escenarios]
    teoricos = [getattr(e.teorico, metrica) * factor for e in escenarios]
    simulados = [getattr(e.simulado, metrica) * factor for e in escenarios]
    eje.plot(agentes, teoricos, marker="o", label="Erlang-C", color="#245a81")
    inferiores, superiores = [], []
    for escenario, media in zip(escenarios, simulados):
        intervalo = escenario.simulado.intervalos_95.get(metrica)
        if intervalo is None and metrica == "nivel_servicio":
            intervalo = escenario.simulado.intervalo_servicio_95
        inf, sup = intervalo if intervalo is not None else (media / factor, media / factor)
        inferiores.append(max(0.0, media - inf * factor))
        superiores.append(max(0.0, sup * factor - media))
    eje.errorbar(
        agentes, simulados, yerr=[inferiores, superiores], fmt="s--",
        capsize=4, label="Simulación e IC 95 % aprox.", color="#b75e24",
    )
    if metrica == "nivel_servicio":
        eje.axhline(meta_servicio * 100.0, linestyle=":", color="#526c46",
                    label=f"Meta {meta_servicio * 100:g} %")
        titulo += f" con espera de hasta {umbral_segundos:g} segundos"
    eje.set_title(titulo, fontsize=10)
    eje.set_xlabel("c · Número de agentes", fontsize=9)
    eje.set_ylabel(etiqueta, fontsize=9)
    eje.tick_params(labelsize=9)
    eje.set_xticks(agentes)
    if metrica in {"nivel_servicio", "utilizacion"}:
        eje.set_ylim(0.0, 105.0)
    else:
        eje.set_ylim(bottom=0.0)
    eje.grid(True, alpha=0.25)
    eje.legend(loc="best", fontsize=8, ncol=3, columnspacing=0.8, handlelength=2)
    figura.set_layout_engine("constrained")
    return eje


def crear_figura(resultado, metrica):
    """Crea una figura exportable sin abrir Tkinter."""
    figura = Figure(figsize=(8, 4.8), dpi=130)
    cfg = resultado.configuracion
    dibujar_comparacion(figura, resultado.escenarios, metrica,
                       cfg.meta_servicio, cfg.umbral_segundos)
    return figura


class GraficadorServicio:
    """Una figura y un canvas por pestaña, creados una sola vez."""

    def __init__(self, metrica="nivel_servicio"):
        self.metrica = metrica
        self.figura = Figure(figsize=(7.5, 3.3), dpi=100)
        self.eje = self.figura.add_subplot(111)
        self.eje.set_axis_off()

    def dibujar(self, escenarios, meta_servicio, umbral_segundos):
        self.eje = dibujar_comparacion(
            self.figura, escenarios, self.metrica, meta_servicio, umbral_segundos
        )
        self.figura.canvas.draw_idle()

    def obtener_widget_canvas(self, master):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        return FigureCanvasTkAgg(self.figura, master=master)
