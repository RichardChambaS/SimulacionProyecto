"""Entrada mínima de la base del proyecto; Derick completará el arranque MVC."""

from app.modelo.configuracion import Configuracion


def main() -> None:
    configuracion = Configuracion()
    configuracion.validar()
    print("Base del modelo disponible: configuración y contratos de resultados.")
    print("El arranque de la interfaz y su integración están pendientes de Derick.")


if __name__ == "__main__":
    main()
