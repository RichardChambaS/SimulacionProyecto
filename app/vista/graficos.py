"""Utilidades de graficación para la vista."""

from __future__ import annotations

from typing import Iterable

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure


class GraficadorServicio:
    """Genera la gráfica de nivel de servicio frente a número de agentes."""

    def __init__(self) -> None:
        self.figura = Figure(figsize=(6.2, 4.2), dpi=100)
        self.eje = self.figura.add_subplot(111)
        self.figura.tight_layout()

    def dibujar(self, escenarios: Iterable) -> None:
        self.eje.clear()

        agentes_teoricos = []
        servicio_teorico = []
        agentes_simulados = []
        servicio_simulado = []
        inferiores = []
        superiores = []

        for escenario in escenarios:
            agentes_teoricos.append(escenario.agentes)
            servicio_teorico.append(escenario.teorico.nivel_servicio)
            agentes_simulados.append(escenario.agentes)
            servicio_simulado.append(escenario.simulado.nivel_servicio)
            if escenario.simulado.intervalo_servicio_95 is not None:
                inf, sup = escenario.simulado.intervalo_servicio_95
                inferiores.append(inf)
                superiores.append(sup)
            else:
                inferiores.append(escenario.simulado.nivel_servicio)
                superiores.append(escenario.simulado.nivel_servicio)

        if agentes_teoricos:
            self.eje.plot(
                agentes_teoricos,
                servicio_teorico,
                marker="o",
                label="Erlang-C",
                linestyle="-",
            )
        if agentes_simulados:
            self.eje.plot(
                agentes_simulados,
                servicio_simulado,
                marker="s",
                label="Simulación",
                linestyle="--",
            )
            if inferiores and superiores:
                self.eje.fill_between(
                    agentes_simulados,
                    inferiores,
                    superiores,
                    alpha=0.15,
                    label="IC 95% simulado (aprox.)",
                )

        self.eje.axhline(0.8, linestyle=":", label="Meta (0.80)")
        self.eje.set_xlabel("Número de agentes")
        self.eje.set_ylabel("Nivel de servicio (proporción)")
        self.eje.set_ylim(0.0, 1.05)
        self.eje.grid(True, alpha=0.3)
        self.eje.legend(loc="lower right")
        self.figura.canvas.draw_idle()

    def obtener_widget_canvas(self):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        return FigureCanvasTkAgg(self.figura, master=None)
