"""Exportación reproducible de datos y figuras de un estudio completado."""

import csv
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import platform
from tempfile import mkdtemp

from app.vista.graficos import ESPECIFICACIONES, crear_figura
#ESTO SI ESTÁ DE MÁS PODEMOS CAMBIAR

def exportar_estudio(resultado, destino):
    """Crea una subcarpeta única y conserva todos los datos del resultado."""
    destino = Path(destino).expanduser().resolve()
    if not destino.is_dir():
        raise ValueError("La carpeta de destino no existe.")
    instante = datetime.now(timezone.utc)
    carpeta = Path(mkdtemp(prefix=instante.strftime("estudio_%Y%m%dT%H%M%SZ_"), dir=destino))
    metadatos = {
        "formato": 1,
        "generado_utc": instante.isoformat(),
        "python": platform.python_version(),
        "bibliotecas": {nombre: version(nombre) for nombre in ("matplotlib", "scipy")},
        "intervalo": "t de Student bilateral del 95 % sobre medias de repeticiones",
        "unidades": "Minutos para tiempos; proporciones para probabilidades y utilización; llamadas para Lq.",
        "advertencia": "Los intervalos son aproximados. El mínimo anunciado es teórico.",
    }
    with (carpeta / "estudio.json").open("w", encoding="utf-8") as archivo:
        json.dump({"metadatos": metadatos, **asdict(resultado)}, archivo,
                  ensure_ascii=False, indent=2, allow_nan=False)

    campos = ["agentes", "metrica", "unidad", "teorico", "simulado", "diferencia",
              "error_absoluto", "error_relativo_porcentaje", "ic95_inferior", "ic95_superior",
              "estado_servicio"]
    with (carpeta / "comparacion.csv").open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        for escenario in resultado.escenarios:
            for metrica, comparacion in escenario.comparaciones.items():
                inf, sup = escenario.simulado.intervalos_95[metrica]
                unidad = "minutos" if metrica == "espera_media_minutos" else (
                    "llamadas" if metrica == "longitud_media_cola" else "proporcion")
                escritor.writerow({"agentes": escenario.agentes, "metrica": metrica,
                                   "unidad": unidad, **asdict(comparacion),
                                   "ic95_inferior": inf, "ic95_superior": sup,
                                   "estado_servicio": escenario.estado_servicio})

    campos_repeticion = ["agentes", "indice", "semilla_llegadas", "semilla_atenciones",
                         "utilizacion", "probabilidad_espera", "nivel_servicio",
                         "espera_media_minutos", "longitud_media_cola", "llamadas_medidas"]
    with (carpeta / "repeticiones.csv").open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos_repeticion)
        escritor.writeheader()
        for escenario in resultado.escenarios:
            for repeticion in escenario.simulado.repeticiones:
                escritor.writerow({"agentes": escenario.agentes, **asdict(repeticion)})

    for metrica in ESPECIFICACIONES:
        figura = crear_figura(resultado, metrica)
        figura.savefig(carpeta / f"{metrica}.png", dpi=170,
                       bbox_inches="tight", pad_inches=0.15)
        figura.clear()
    (carpeta / "LEEME.txt").write_text(
        "ESTUDIO DEL CENTRO DE LLAMADAS\n\n"
        "estudio.json conserva configuración, versiones, teoría, medias, intervalos y cada repetición.\n"
        "comparacion.csv contiene 5 medidas por escenario. repeticiones.csv contiene las semillas exactas.\n"
        "Los CSV usan coma como separador, punto decimal y UTF-8 con BOM.\n\n"
        "Unidades de los datos: tiempos en minutos; probabilidades y utilización entre 0 y 1; "
        "longitud de cola en llamadas. La ventana y las gráficas convierten las esperas a segundos.\n"
        "Diferencia = simulado - teórico. Error relativo (%) = 100 * error absoluto / abs(teórico).\n"
        "Si el valor teórico es cero, el error relativo queda vacío en CSV y null en JSON.\n"
        "La media del resumen es la media entre repeticiones; el conteo suma sus llamadas.\n"
        "Las llamadas medidas llegan en [calentamiento, calentamiento + duración). "
        "Se termina su atención al cerrar las llegadas. Utilización y Lq se miden solo en esa ventana.\n"
        "Los intervalos t de Student son aproximados y no corrigen un calentamiento insuficiente.\n"
        "Cumplimiento respaldado: límite inferior >= meta. Incumplimiento respaldado: "
        "límite superior < meta. En otro caso, no concluyente.\n"
        "La comparación usa entradas comunes entre escenarios; los escenarios no son independientes.\n"
        "Lq es un promedio temporal y Wq corresponde a una cohorte de llegadas; "
        "Lq = lambda * Wq puede diferir en una ventana finita.\n"
        "Esta exportación no escribe el informe académico ni demuestra un mínimo simulado absoluto.\n",
        encoding="utf-8",
    )
    return carpeta
