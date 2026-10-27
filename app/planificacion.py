"""Estimación previa de trabajo para la interfaz; no modifica el experimento."""

from dataclasses import dataclass
from math import isfinite

from app.modelo.configuracion import Configuracion

# VALIDACIÓN PARA QUE NO EXLOTE TODO SI PONEMOS VALORES GRANDES XD
# Límites de uso de la aplicación, no condiciones matemáticas de M/M/c.
AVISO_EVENTOS = 5_000_000
LIMITE_EVENTOS = 1_000_000_000
LIMITE_RECORRIDO_TEORICO = 1_000_000


@dataclass(frozen=True)
class CargaTrabajo:
    eventos: float
    nivel: str
    mensaje: str


def estimar_trabajo(configuracion: Configuracion, agentes=None) -> CargaTrabajo:
    """Cuenta llegadas y finalizaciones esperadas de tres escenarios y R réplicas."""
    cfg = configuracion
    eventos = (cfg.tasa_llegadas_minuto * (cfg.calentamiento_minutos + cfg.duracion_minutos)
               * cfg.repeticiones * 3 * 2)
    recorrido = max(cfg.carga_erlangs, max(agentes, default=0) if agentes else 0)
    if not isfinite(eventos) or eventos > LIMITE_EVENTOS or recorrido > LIMITE_RECORRIDO_TEORICO:
        return CargaTrabajo(eventos, "bloqueado",
            "El estudio supera el límite de trabajo de esta aplicación. Reduce las llegadas, "
            "la duración, el calentamiento, las repeticiones o los agentes manuales. "
            "No se ha iniciado ni se han cambiado tus valores.")
    if eventos > AVISO_EVENTOS:
        return CargaTrabajo(eventos, "alto",
            "Este estudio puede tardar varios minutos. Se procesan las llamadas del "
            f"calentamiento y de la medición en las {cfg.repeticiones} repeticiones y los tres escenarios.")
    return CargaTrabajo(eventos, "normal", "Carga de ejecución habitual.")
