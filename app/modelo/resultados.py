"""Contratos de datos compartidos por el modelo, controlador y vista.

Las probabilidades y la utilización son proporciones entre 0 y 1; las esperas
se expresan en minutos. El modelo no depende de Tkinter ni de Matplotlib.
"""

from dataclasses import dataclass

from .configuracion import Configuracion


@dataclass
class ResultadoEvaluacion:
    """Métricas de un escenario, obtenidas por teoría o simulación."""

    metodo: str
    agentes: int
    utilizacion: float
    probabilidad_espera: float
    nivel_servicio: float
    espera_media_minutos: float
    intervalo_servicio_95: tuple[float, float] | None = None
    llamadas_medidas: int | None = None


@dataclass
class ResultadoEscenario:
    """Comparación de ambos métodos para la misma cantidad de agentes."""

    agentes: int
    teorico: ResultadoEvaluacion
    simulado: ResultadoEvaluacion


@dataclass
class ResultadoEstudio:
    """Configuración, mínimo teórico y escenarios evaluados por el estudio."""

    configuracion: Configuracion
    minimo_teorico: int
    escenarios: list[ResultadoEscenario]
