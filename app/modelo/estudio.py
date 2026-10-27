"""Estudio comparativo entre la teoría de Erlang-C y la simulación M/M/c.

El módulo organiza las dos estrategias recibidas por constructor y no importa
la vista ni el controlador. La conclusión estadística se deja en los datos
devueltos: cada escenario conserva el intervalo aproximado del 95 % calculado
por la simulación.
"""

from .configuracion import Configuracion
from math import isfinite
from threading import Event
from typing import Callable

from .resultados import METRICAS, ComparacionMetrica, ResultadoEscenario, ResultadoEstudio
from .simulacion import SimulacionCancelada


def validar_agentes(configuracion: Configuracion, agentes) -> list[int]:
    """Valida los tres escenarios opcionales sin modificar el cálculo del modelo."""
    cantidades = list(agentes)
    if len(cantidades) != 3:
        raise ValueError("Introduce tres cantidades de agentes, una por escenario.")
    for cantidad in cantidades:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("Los agentes deben ser números enteros positivos.")
        try:
            finito = isfinite(cantidad)
        except OverflowError:
            finito = False
        if not finito:
            raise ValueError("La cantidad de agentes es demasiado grande.")
        if cantidad <= configuracion.carga_erlangs:
            raise ValueError(
                f"Cada escenario necesita c > A. La carga es A = {configuracion.carga_erlangs:g}; "
                f"{cantidad} agentes no forman un escenario estable."
            )
    if len(set(cantidades)) != 3:
        raise ValueError("Elige tres cantidades de agentes distintas para compararlas.")
    return sorted(cantidades)


def clasificar_servicio(intervalo: tuple[float, float] | None, meta: float) -> str:
    """Clasifica el respaldo del intervalo; una media aislada no es una prueba."""
    if intervalo is None:
        return "Sin intervalo"
    inferior, superior = intervalo
    if inferior >= meta:
        return "Cumplimiento respaldado"
    if superior < meta:
        return "Incumplimiento respaldado"
    return "No concluyente"


def comparar_metricas(teorico, simulado) -> dict[str, ComparacionMetrica]:
    comparaciones = {}
    for metrica in METRICAS:
        referencia = getattr(teorico, metrica)
        estimacion = getattr(simulado, metrica)
        diferencia = estimacion - referencia
        relativo = abs(diferencia) / abs(referencia) * 100.0 if referencia != 0 else None
        comparaciones[metrica] = ComparacionMetrica(
            referencia, estimacion, diferencia, abs(diferencia), relativo
        )
    return comparaciones


class EstudioServicio:
    """Combina una estrategia teórica y otra simulada para un mismo escenario."""

    def __init__(self, teorico, simulador) -> None:
        self._teorico = teorico
        self._simulador = simulador

    def ejecutar(
        self, configuracion: Configuracion, *,
        agentes: list[int] | None = None,
        progreso: Callable[[int, int], None] | None = None,
        cancelar: Event | None = None,
    ) -> ResultadoEstudio:
        """Valida, busca el mínimo teórico y compara tres escenarios estables."""
        configuracion.validar()
        manuales = validar_agentes(configuracion, agentes) if agentes is not None else None
        minimo_teorico = self._teorico.buscar_minimo(configuracion)
        cantidades = manuales if manuales is not None else self._seleccionar_agentes(configuracion, minimo_teorico)

        escenarios = []
        total = len(cantidades) * configuracion.repeticiones
        for numero, agentes in enumerate(cantidades):
            if cancelar is not None and cancelar.is_set():
                raise SimulacionCancelada("Estudio cancelado.")
            teorico = self._teorico.evaluar(configuracion, agentes)
            opciones = {}
            if cancelar is not None:
                opciones["cancelar"] = cancelar
            if progreso is not None:
                base = numero * configuracion.repeticiones
                opciones["progreso"] = lambda completas, base=base: progreso(base + completas, total)
            simulado = self._simulador.evaluar(configuracion, agentes, **opciones)
            escenarios.append(
                ResultadoEscenario(
                    agentes=agentes,
                    teorico=teorico,
                    simulado=simulado,
                    estado_servicio=clasificar_servicio(
                        simulado.intervalo_servicio_95, configuracion.meta_servicio
                    ),
                    comparaciones=comparar_metricas(teorico, simulado),
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
        """Separa dos agentes respecto al mínimo, manteniendo tres casos estables."""
        if minimo_teorico - 2 > configuracion.carga_erlangs:
            return [minimo_teorico - 2, minimo_teorico, minimo_teorico + 2]
        if minimo_teorico - 1 > configuracion.carga_erlangs:
            return [minimo_teorico - 1, minimo_teorico, minimo_teorico + 2]
        return [minimo_teorico, minimo_teorico + 2, minimo_teorico + 4]
