"""Evaluación estacionaria M/M/c mediante Erlang-C.

La recurrencia de Erlang-B evita factoriales y potencias grandes. A partir de
B(c, a), se obtiene C(c, a) = B / (1 - rho + rho * B), con rho = a / c.
La condición de estabilidad es c > a; no se modela abandono de llamadas.

Referencia del modelo y la condición de estabilidad:
https://archive.nptel.ac.in/content/storage2/courses/117103017/module3/lec2/1.html
"""

from math import expm1, floor, isfinite

from .configuracion import Configuracion
from .resultados import ResultadoEvaluacion


def _siguiente_erlang_b(carga: float, agentes: int, anterior: float) -> float:
    """B(n, a) = a * B(n-1, a) / (n + a * B(n-1, a))."""
    # Dividir por la carga evita multiplicaciones grandes en la recurrencia.
    return anterior / (agentes / carga + anterior)


def _erlang_b(carga: float, agentes: int) -> float:
    bloqueo = 1.0  # B(0, a).
    for cantidad in range(1, agentes + 1):
        bloqueo = _siguiente_erlang_b(carga, cantidad, bloqueo)
    return bloqueo


class ErlangC:
    """Estrategia teórica, independiente de la simulación y de la interfaz."""

    def evaluar(
        self, configuracion: Configuracion, agentes: int
    ) -> ResultadoEvaluacion:
        """Calcula métricas para un número entero y estable de agentes."""
        configuracion.validar()
        if isinstance(agentes, bool) or not isinstance(agentes, int) or agentes <= 0:
            raise ValueError("La cantidad de agentes debe ser un número entero positivo.")
        try:
            representable = isfinite(agentes)
        except OverflowError:
            representable = False
        if not representable:
            raise ValueError("La cantidad de agentes excede el rango numérico admitido.")
        carga = configuracion.carga_erlangs
        if agentes <= carga:
            raise ValueError(
                f"El sistema no es estable: se requieren más de {carga:g} agentes "
                f"para una carga de {carga:g} erlangs."
            )
        return self._resultado(configuracion, agentes, _erlang_b(carga, agentes))

    def buscar_minimo(self, configuracion: Configuracion) -> int:
        """Devuelve el primer entero estable cuyo nivel de servicio cumple la meta.

        Al incrementar agentes se reutiliza la recurrencia, sin recalcular desde
        cero Erlang-B para cada candidato ni imponer un límite arbitrario.
        """
        configuracion.validar()
        carga = configuracion.carga_erlangs
        agentes = floor(carga) + 1
        bloqueo = _erlang_b(carga, agentes)
        while True:
            resultado = self._resultado(configuracion, agentes, bloqueo)
            if resultado.nivel_servicio >= configuracion.meta_servicio:
                return agentes
            agentes += 1
            bloqueo = _siguiente_erlang_b(carga, agentes, bloqueo)

    @staticmethod
    def _resultado(
        configuracion: Configuracion, agentes: int, bloqueo: float
    ) -> ResultadoEvaluacion:
        carga = configuracion.carga_erlangs
        utilizacion = carga / agentes
        probabilidad_espera = bloqueo / (1.0 - utilizacion + utilizacion * bloqueo)
        capacidad_disponible = (agentes - carga) * configuracion.tasa_servicio_minuto
        if capacidad_disponible <= 0:
            raise ValueError("La capacidad disponible no es representable numéricamente.")

        # Equivale a 1 - C * exp(-(c * mu - lambda) * t). expm1 conserva
        # precisión cuando el umbral o la capacidad disponible son pequeños.
        nivel_servicio = (1.0 - probabilidad_espera) - probabilidad_espera * expm1(
            -capacidad_disponible * configuracion.umbral_minutos
        )
        espera_media = probabilidad_espera / capacidad_disponible
        if not isfinite(espera_media):
            raise ValueError("La espera media excede el rango numérico admitido.")
        return ResultadoEvaluacion(
            metodo="Erlang-C",
            agentes=agentes,
            utilizacion=utilizacion,
            probabilidad_espera=probabilidad_espera,
            nivel_servicio=max(0.0, min(1.0, nivel_servicio)),
            espera_media_minutos=espera_media,
        )
