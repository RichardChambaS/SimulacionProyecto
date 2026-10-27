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
from app.modelo.simulacion import SimulacionCancelada
from app.exportacion import exportar_estudio
from app.modelo.estudio import validar_agentes
from app.planificacion import estimar_trabajo

_INTERVALO_CONSULTA_MS = 100


class Controlador:
    """Vincula el botón de la vista con la ejecución del estudio."""

    def __init__(self, vista, estudio) -> None:
        self._vista = vista
        self._estudio = estudio
        self._ejecutando = False
        self._cerrada = False
        self._resultados: queue.Queue = queue.Queue()
        self._after_id = None
        self._cancelar = threading.Event()
        self._ultimo_resultado = None

        self._vista.vincular_ejecucion(self.ejecutar)
        self._vista.vincular_cancelacion(self.cancelar)
        self._vista.vincular_exportacion(self.exportar)
        self._vista.protocol("WM_DELETE_WINDOW", self._al_cerrar)

    def ejecutar(self) -> None:
        """Lee y valida la configuración antes de lanzar el estudio."""
        if self._cerrada or self._ejecutando:
            return

        try:
            configuracion = self._vista.obtener_configuracion()
            self._validar(configuracion)
            agentes = self._vista.obtener_agentes()
            if agentes is not None:
                agentes = validar_agentes(configuracion, agentes)
            carga = estimar_trabajo(configuracion, agentes)
            if carga.nivel == "bloqueado":
                raise ValueError(carga.mensaje)
            if carga.nivel == "alto" and not self._vista.confirmar_carga(carga):
                return
        except ValueError as error:
            self._vista.mostrar_error(str(error))
            return

        self._ejecutando = True
        self._cancelar.clear()
        self._vista.establecer_ocupado(True)
        hilo = threading.Thread(
            target=self._trabajar,
            args=(configuracion, agentes),
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

    def _trabajar(self, configuracion: Configuracion, agentes=None) -> None:
        try:
            opciones = {"agentes": agentes} if agentes is not None else {}
            resultado = self._estudio.ejecutar(
                configuracion, cancelar=self._cancelar,
                progreso=lambda actual, total: self._resultados.put(("progreso", (actual, total))),
                **opciones,
            )
        except SimulacionCancelada:
            self._resultados.put(("cancelado", None))
        except Exception as error:
            self._resultados.put(("error", error))
        else:
            self._resultados.put(("resultado", resultado))

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

        while True:
            try:
                tipo, carga = self._resultados.get_nowait()
            except queue.Empty:
                self._programar_consulta()
                return
            if tipo == "progreso":
                self._vista.mostrar_progreso(*carga)
                continue
            self._ejecutando = False
            try:
                if tipo == "resultado":
                    self._vista.mostrar_resultados(carga)
                    self._ultimo_resultado = carga
                elif tipo == "cancelado":
                    self._vista.mostrar_estado("Estudio cancelado")
                else:
                    self._vista.mostrar_estado("El estudio no se completó")
                    self._vista.mostrar_error(self._mensaje_error(carga))
            except Exception as error:
                self._vista.mostrar_estado("No se pudieron presentar los resultados")
                self._vista.mostrar_error(self._mensaje_error(error))
            finally:
                if not self._cerrada:
                    self._vista.establecer_ocupado(False)
            return

    def cancelar(self) -> None:
        if self._ejecutando:
            self._cancelar.set()
            self._vista.mostrar_cancelacion()

    def exportar(self) -> None:
        if self._cerrada or self._ejecutando or self._ultimo_resultado is None:
            return
        destino = self._vista.solicitar_directorio_exportacion()
        if not destino:
            return
        try:
            carpeta = exportar_estudio(self._ultimo_resultado, destino)
        except Exception as error:
            self._vista.mostrar_error(self._mensaje_error(error))
        else:
            self._vista.mostrar_exportacion(carpeta)

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
        self._cancelar.set()
        if self._after_id is not None:
            try:
                self._vista.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self._vista.destroy()
