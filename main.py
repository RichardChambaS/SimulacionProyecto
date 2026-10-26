"""Punto de entrada de la aplicación: construye el flujo MVC completo."""

from app.controlador.controlador import Controlador
from app.modelo.erlang_c import ErlangC
from app.modelo.estudio import EstudioServicio
from app.modelo.simulacion import Simulador
from app.vista.ventana_principal import VentanaPrincipal


def main() -> None:
    estudio = EstudioServicio(ErlangC(), Simulador())
    vista = VentanaPrincipal()
    Controlador(vista, estudio)
    vista.iniciar()


if __name__ == "__main__":
    main()
