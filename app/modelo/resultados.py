"""Contratos de datos compartidos por el modelo, controlador y vista.

Las probabilidades y la utilización son proporciones entre 0 y 1; las esperas
se expresan en minutos. El modelo no depende de Tkinter ni de Matplotlib.
"""

from dataclasses import dataclass, field

from .configuracion import Configuracion


METRICAS = (
    "nivel_servicio", "espera_media_minutos", "utilizacion",
    "probabilidad_espera", "longitud_media_cola",
)


@dataclass
class ResultadoRepeticion:
    """Una repetición, con las dos semillas que permiten reproducirla."""

    indice: int
    semilla_llegadas: str
    semilla_atenciones: str
    utilizacion: float
    probabilidad_espera: float
    nivel_servicio: float
    espera_media_minutos: float
    longitud_media_cola: float
    llamadas_medidas: int


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
    longitud_media_cola: float = 0.0
    intervalos_95: dict[str, tuple[float, float]] = field(default_factory=dict)
    repeticiones: list[ResultadoRepeticion] = field(default_factory=list)


@dataclass
class ComparacionMetrica:
    """Diferencias en la unidad original; el error relativo se expresa en %."""

    teorico: float
    simulado: float
    diferencia: float
    error_absoluto: float
    error_relativo_porcentaje: float | None


@dataclass
class ResultadoEscenario:
    """Comparación de ambos métodos para la misma cantidad de agentes."""

    agentes: int
    teorico: ResultadoEvaluacion
    simulado: ResultadoEvaluacion
    estado_servicio: str = "Sin evaluar"
    comparaciones: dict[str, ComparacionMetrica] = field(default_factory=dict)


@dataclass
class ResultadoEstudio:
    """Configuración, mínimo teórico y escenarios evaluados por el estudio."""

    configuracion: Configuracion
    minimo_teorico: int
    escenarios: list[ResultadoEscenario]
