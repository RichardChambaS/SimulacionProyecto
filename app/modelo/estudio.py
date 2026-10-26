"""Estudio comparativo entre la teoría de Erlang-C y la simulación M/M/c.

El módulo organiza las dos estrategias recibidas por constructor y no importa
la vista ni el controlador. La conclusión estadística se deja en los datos
devueltos: cada escenario conserva el intervalo aproximado del 95 % calculado
por la simulación.
"""

from .configuracion import Configuracion
from .resultados import ResultadoEscenario, ResultadoEstudio


class EstudioServicio:
    """Combina una estrategia teórica y otra simulada para un mismo escenario."""

    def __init__(self, teorico, simulador) -> None:
        self._teorico = teorico
        self._simulador = simulador

    def ejecutar(self, configuracion: Configuracion) -> ResultadoEstudio:
        """Valida, busca el mínimo teórico y compara tres escenarios estables."""
        configuracion.validar()
        minimo_teorico = self._teorico.buscar_minimo(configuracion)
        cantidades = self._seleccionar_agentes(configuracion, minimo_teorico)

        escenarios = []
        for agentes in cantidades:
            teorico = self._teorico.evaluar(configuracion, agentes)
            simulado = self._simulador.evaluar(configuracion, agentes)
            escenarios.append(
                ResultadoEscenario(
                    agentes=agentes,
                    teorico=teorico,
                    simulado=simulado,
                )
            )

        return ResultadoEstudio(
            configuracion=configuracion,
            minimo_teorico=minimo_teorico,
            escenarios=escenarios,
        )

    @staticmethod
    def _seleccionar_agentes(
        configuracion: Configuracion, minimo_teorico: int
    ) -> list[int]:
        """Elige el mínimo y sus vecinos, evitando un inferior inestable."""
        if minimo_teorico - 1 > configuracion.carga_erlangs:
            return [minimo_teorico - 1, minimo_teorico, minimo_teorico + 1]
        return [minimo_teorico, minimo_teorico + 1, minimo_teorico + 2]
