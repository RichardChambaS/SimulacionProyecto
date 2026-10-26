"""Simulación M/M/c con cola FIFO y calendario de eventos en minutos.

Las llegadas se detienen al terminar el período medido. Luego se vacía el
sistema para observar las esperas de toda la cohorte, sin censurar llamadas.
Los servicios del calentamiento también ocupan agentes durante la medición.
"""

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import isfinite
from random import Random

from .configuracion import Configuracion


_FINALIZACION = 0
_LLEGADA = 1


@dataclass(frozen=True)
class _Llamada:
    llegada: float
    duracion: float
    medida: bool


@dataclass(frozen=True)
class _ResultadoRepeticion:
    utilizacion: float
    probabilidad_espera: float
    nivel_servicio: float
    espera_media_minutos: float
    llamadas_medidas: int


def _validar_escenario(configuracion: Configuracion, agentes: int) -> None:
    configuracion.validar()
    if isinstance(agentes, bool) or not isinstance(agentes, int) or agentes <= 0:
        raise ValueError("La cantidad de agentes debe ser un número entero positivo.")
    try:
        representable = isfinite(agentes)
    except OverflowError:
        representable = False
    if not representable:
        raise ValueError("La cantidad de agentes excede el rango numérico admitido.")
    if agentes <= configuracion.carga_erlangs:
        raise ValueError(
            "El sistema no es estable: la cantidad de agentes debe superar "
            f"la carga de {configuracion.carga_erlangs:g} erlangs."
        )
    fin = configuracion.calentamiento_minutos + configuracion.duracion_minutos
    if not isfinite(fin) or fin <= configuracion.calentamiento_minutos:
        raise ValueError("El período de medición no es representable en minutos.")


def _tiempo_futuro(reloj: float, demora: float) -> float:
    siguiente = reloj + demora
    if not isfinite(siguiente) or demora <= 0 or siguiente <= reloj:
        raise ValueError(
            "Un tiempo de llegada o atención no es representable; "
            "revise la escala de las tasas y de la duración."
        )
    return siguiente


def _simular_repeticion(
    configuracion: Configuracion,
    agentes: int,
    llegadas: Random,
    atenciones: Random,
) -> _ResultadoRepeticion:
    """Ejecuta un escenario validado con dos fuentes aleatorias independientes."""
    inicio = configuracion.calentamiento_minutos
    fin = inicio + configuracion.duracion_minutos
    secuencia = count()
    eventos: list[tuple[float, int, int]] = []
    cola: deque[_Llamada] = deque()
    ocupados = 0
    ocupacion_minutos = 0.0
    medidas = 0
    con_espera = 0
    a_tiempo = 0
    espera_total = 0.0

    def programar_llegada(reloj: float) -> None:
        siguiente = _tiempo_futuro(
            reloj, llegadas.expovariate(configuracion.tasa_llegadas_minuto)
        )
        if siguiente < fin:
            heappush(eventos, (siguiente, _LLEGADA, next(secuencia)))

    def iniciar_atencion(llamada: _Llamada, reloj: float) -> None:
        nonlocal ocupados, ocupacion_minutos, medidas, con_espera, a_tiempo, espera_total
        terminacion = _tiempo_futuro(reloj, llamada.duracion)
        ocupados += 1
        # Se contabiliza solo la parte de cada servicio que cruza [inicio, fin).
        ocupacion_minutos += max(0.0, min(terminacion, fin) - max(reloj, inicio))
        heappush(eventos, (terminacion, _FINALIZACION, next(secuencia)))
        if llamada.medida:
            espera = reloj - llamada.llegada
            medidas += 1
            con_espera += espera > 0.0
            a_tiempo += espera <= configuracion.umbral_minutos
            espera_total += espera

    programar_llegada(0.0)
    while eventos:
        reloj, tipo, _ = heappop(eventos)
        if tipo == _FINALIZACION:
            ocupados -= 1
            if cola:
                iniciar_atencion(cola.popleft(), reloj)
        else:
            # Muestrear el servicio al llegar conserva las mismas llamadas si
            # se compara otro número de agentes con las mismas dos semillas.
            llamada = _Llamada(
                llegada=reloj,
                duracion=atenciones.expovariate(configuracion.tasa_servicio_minuto),
                medida=inicio <= reloj < fin,
            )
            if ocupados < agentes:
                iniciar_atencion(llamada, reloj)
            else:
                cola.append(llamada)
            programar_llegada(reloj)

    if medidas == 0:
        raise ValueError(
            "Una repetición no generó llamadas en el período medido; "
            "amplíe la duración de la simulación."
        )
    return _ResultadoRepeticion(
        utilizacion=ocupacion_minutos / configuracion.duracion_minutos / agentes,
        probabilidad_espera=con_espera / medidas,
        nivel_servicio=a_tiempo / medidas,
        espera_media_minutos=espera_total / medidas,
        llamadas_medidas=medidas,
    )
