"""Parámetros compartidos por el cálculo teórico y la simulación.

Requiere Python 3.10 o posterior. La interfaz puede trabajar en horas y
segundos; las propiedades convierten los parámetros a minutos para el modelo.
"""

from dataclasses import dataclass
from math import isfinite
from numbers import Real


def _validar_real(nombre: str, valor: float, *, permitir_cero: bool = False) -> None:
    """Rechaza texto, booleanos, infinitos y valores fuera del dominio."""
    if isinstance(valor, bool) or not isinstance(valor, Real):
        raise ValueError(f"{nombre} debe ser un número real.")
    try:
        finito = isfinite(valor)
    except OverflowError:
        finito = False
    if not finito:
        raise ValueError(f"{nombre} debe ser un número finito representable.")
    if valor < 0 or (valor == 0 and not permitir_cero):
        condicion = "mayor o igual a cero" if permitir_cero else "mayor que cero"
        raise ValueError(f"{nombre} debe ser {condicion}.")


@dataclass
class Configuracion:
    """Entradas del estudio; las probabilidades se expresan como proporciones."""

    tasa_llegadas_hora: float = 30.0
    atencion_media_minutos: float = 6.0
    meta_servicio: float = 0.80
    umbral_segundos: float = 20.0
    duracion_minutos: float = 4800.0
    calentamiento_minutos: float = 1000.0
    repeticiones: int = 30
    semilla: int = 42

    @property
    def tasa_llegadas_minuto(self) -> float:
        return self.tasa_llegadas_hora / 60.0

    @property
    def tasa_servicio_minuto(self) -> float:
        return 1.0 / self.atencion_media_minutos

    @property
    def carga_erlangs(self) -> float:
        return self.tasa_llegadas_minuto / self.tasa_servicio_minuto

    @property
    def umbral_minutos(self) -> float:
        return self.umbral_segundos / 60.0

    def validar(self) -> None:
        """Lanza ValueError con un mensaje legible si la configuración es inválida.

        La validación es explícita para que el controlador pueda informar el
        error antes de ejecutar el estudio. También se comprueba que las tasas
        derivadas puedan representarse con números de punto flotante.
        """
        _validar_real("La tasa de llegadas por hora", self.tasa_llegadas_hora)
        _validar_real("La atención media en minutos", self.atencion_media_minutos)
        _validar_real("La meta de servicio", self.meta_servicio)
        if self.meta_servicio >= 1:
            raise ValueError("La meta de servicio debe estar entre 0 y 1, sin incluirlos.")
        _validar_real("El umbral en segundos", self.umbral_segundos, permitir_cero=True)
        _validar_real("La duración en minutos", self.duracion_minutos)
        _validar_real(
            "El calentamiento en minutos", self.calentamiento_minutos, permitir_cero=True
        )
        if (
            isinstance(self.repeticiones, bool)
            or not isinstance(self.repeticiones, int)
            or self.repeticiones < 2
        ):
            raise ValueError("Las repeticiones deben ser un número entero de al menos 2.")
        if (
            isinstance(self.semilla, bool)
            or not isinstance(self.semilla, int)
            or self.semilla < 0
        ):
            raise ValueError("La semilla debe ser un número entero mayor o igual a cero.")

        _validar_real("La tasa de llegadas por minuto", self.tasa_llegadas_minuto)
        _validar_real("La tasa de servicio por minuto", self.tasa_servicio_minuto)
        _validar_real("La carga ofrecida en erlangs", self.carga_erlangs)
        fin = self.calentamiento_minutos + self.duracion_minutos
        if not isfinite(fin) or fin <= self.calentamiento_minutos:
            raise ValueError("El período de medición no es representable en minutos.")
