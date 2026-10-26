"""Controlador único entre la ventana y el estudio comparativo.

El estudio se ejecuta en un hilo de trabajo para no bloquear Tkinter. El hilo
solo deposita su resultado en una cola; la interfaz se actualiza desde el hilo
principal mediante ``after()``. El hilo es demonio para que cerrar la ventana
durante un cálculo no impida terminar el proceso.
"""

from __future__ import annotations

import queue
import threading

from app.modelo.configuracion import Configuracion

_INTERVALO_CONSULTA_MS = 100


class Controlador:
    """Vincula el botón de la vista con la ejecución del estudio."""

    def __init__(self, vista, estudio) -> None:
        self._vista = vista
        self._estudio = estudio
        self._ejecutando = False
        self._cerrada = False
        self._resultados: queue.Queue = queue.Queue(maxsize=1)
        self._after_id = None

        self._vista.vincular_ejecucion(self.ejecutar)
        self._vista.protocol("WM_DELETE_WINDOW", self._al_cerrar)

    def ejecutar(self) -> None:
        """Lee y valida la configuración antes de lanzar el estudio."""
        if self._cerrada or self._ejecutando:
            return

        try:
            configuracion = self._vista.obtener_configuracion()
            self._validar(configuracion)
        except ValueError as error:
            self._vista.mostrar_error(str(error))
            return

        self._ejecutando = True
        self._vista.establecer_ocupado(True)
        hilo = threading.Thread(
            target=self._trabajar,
            args=(configuracion,),
            daemon=True,
            name="estudio-servicio",
        )
        hilo.start()
        self._programar_consulta()

    @staticmethod
    def _validar(configuracion: Configuracion) -> None:
        if not isinstance(configuracion, Configuracion):
            raise ValueError("La configuración recibida no es válida.")
        configuracion.validar()

    def _trabajar(self, configuracion: Configuracion) -> None:
        try:
            resultado = self._estudio.ejecutar(configuracion)
        except Exception as error:
            self._resultados.put((False, error))
        else:
            self._resultados.put((True, resultado))

    def _programar_consulta(self) -> None:
        if self._cerrada:
            return
        self._after_id = self._vista.after(
            _INTERVALO_CONSULTA_MS, self._consultar
        )

    def _consultar(self) -> None:
        self._after_id = None
        if self._cerrada:
            return

        try:
            correcto, carga = self._resultados.get_nowait()
        except queue.Empty:
            self._programar_consulta()
            return

        self._ejecutando = False
        try:
            if correcto:
                self._vista.mostrar_resultados(carga)
            else:
                self._vista.mostrar_error(self._mensaje_error(carga))
        finally:
            if not self._cerrada:
                self._vista.establecer_ocupado(False)

    @staticmethod
    def _mensaje_error(error: Exception) -> str:
        detalle = str(error).strip()
        if isinstance(error, ValueError) and detalle:
            return detalle
        if detalle:
            return f"Error inesperado durante el estudio: {detalle}"
        return f"Error inesperado durante el estudio: {type(error).__name__}."

    def _al_cerrar(self) -> None:
        self._cerrada = True
        if self._after_id is not None:
            try:
                self._vista.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self._vista.destroy()
