# Simulación M/M/c: Erlang-C frente a simulación de eventos discretos

Aplicación de escritorio en Python que determina el mínimo de agentes necesario
para cumplir una meta de nivel de servicio mediante Erlang-C y contrasta el
resultado con una simulación de eventos discretos M/M/c. La interfaz muestra
una tabla comparativa por escenario y una gráfica con los intervalos
aproximados del 95 % de la simulación.

## Requisitos

- Python 3.10 o posterior. La comprobación integrada se realizó con Python 3.14.4.
- Tcl/Tk 8.6 y su enlace para Python (`tkinter`). En Debian/Ubuntu suele
  instalarse con el paquete del sistema `python3-tk`; no se instala con `pip`.
- Las dependencias de `requirements.txt` (`matplotlib`, `numpy` y `scipy`).

## Instalación en un entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En Windows, la activación del entorno es `.venv\Scripts\activate`.

## Ejecución

Desde la raíz del proyecto y con el entorno virtual activo:

```bash
python main.py
```

La ventana permite introducir la demanda, la atención media, la meta de
servicio, el umbral, la duración medida, el calentamiento, las repeticiones y
la semilla. Al pulsar **Ejecutar estudio**, el cálculo se realiza en segundo
plano y la interfaz permanece operativa; al terminar se actualizan la tabla, el
resumen y la gráfica.

## Unidades y supuestos

- Las llegadas se expresan en llamadas por hora y la atención media en minutos.
- La meta de servicio se introduce como porcentaje en la interfaz y se convierte
  a proporción antes de construir `Configuracion`.
- El umbral se introduce en segundos; el modelo trabaja internamente en minutos.
- La duración y el calentamiento se expresan en minutos.
- Las llegadas siguen un proceso de Poisson y los tiempos de atención son
  exponenciales e independientes, con cola FIFO ilimitada y sin abandono.
- Solo se evalúan escenarios estables, es decir, con más agentes que la carga
  ofrecida en erlangs.
- El nivel de servicio es la proporción de llamadas medidas cuya espera es
  menor o igual al umbral. El umbral se incluye exactamente.
- Las llamadas que llegan en `[calentamiento, calentamiento + duración)` se
  consideran medidas. Las llamadas del calentamiento afectan al estado del
  sistema, pero no al denominador del nivel de servicio.
- La utilización simulada incluye la ocupación de servicios iniciados durante
  el calentamiento que continúan dentro del período medido.
- El intervalo del 95 % es una aproximación normal a partir de los niveles de
  servicio de las repeticiones independientes: media ± `1.96 * desviación
  muestral / sqrt(repeticiones)`, acotado a `[0, 1]`. No corrige un
  calentamiento insuficiente ni el error de Monte Carlo.

## Escenarios y lectura de la conclusión

El estudio muestra el mínimo teórico y sus vecinos. Si el agente inmediatamente
inferior es inestable, se muestran el mínimo, el mínimo + 1 y el mínimo + 2.
Para cada escenario se evalúan ambos métodos.

La conclusión simulada se interpreta así:

- **Cumplimiento respaldado** si el límite inferior del intervalo es mayor o
  igual a la meta.
- **Incumplimiento** si el límite superior del intervalo es menor que la meta.
- **No concluyente** en los demás casos.

La simulación solo respalda o no respalda los escenarios evaluados; no demuestra
un mínimo absoluto fuera de ellos. El mínimo anunciado es el mínimo teórico de
Erlang-C.

## Arquitectura MVC y patrón Strategy

- **Modelo** (`app/modelo/`): contiene `Configuracion`, las dataclasses de
  resultados, `ErlangC`, `Simulador` y `EstudioServicio`. No importa Tkinter ni
  módulos de la vista.
- **Vista** (`app/vista/`): `VentanaPrincipal` recoge las entradas y presenta
  tabla, resumen y gráfica. No calcula Erlang-C ni ejecuta simulaciones.
- **Controlador** (`app/controlador/controlador.py`): `Controlador` conecta el
  botón con `EstudioServicio`, valida la configuración, ejecuta el estudio fuera
  del hilo de Tkinter y devuelve el resultado a la interfaz mediante `after()`.
- **Strategy**: `ErlangC` y `Simulador` implementan el mismo método
  `evaluar(configuracion, agentes)`, de modo que `EstudioServicio` puede
  combinarlos sin conocer sus algoritmos. `EstudioServicio` recibe ambas
  estrategias por constructor.
- `main.py` construye las dos estrategias, el estudio, la vista y el
  controlador, y arranca el bucle de Tkinter.

## Archivos principales

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | Arranque y composición MVC |
| `app/modelo/configuracion.py` | Parámetros, conversiones y validación |
| `app/modelo/resultados.py` | Dataclasses compartidas |
| `app/modelo/erlang_c.py` | Teoría estacionaria y búsqueda del mínimo |
| `app/modelo/simulacion.py` | Motor de eventos discretos, repeticiones e intervalo |
| `app/modelo/estudio.py` | Selección de escenarios y comparación |
| `app/vista/ventana_principal.py` | Formulario, tabla, resumen y estados |
| `app/vista/graficos.py` | Gráfica de servicio frente a agentes |
| `app/controlador/controlador.py` | Conecta vista, validación y estudio |

## Comprobación integrada realizada

Fecha: 2026-10-26. Entorno: Python 3.14.4, Tcl/Tk 8.6, entorno virtual con
Matplotlib 3.11.2, Pillow 13.0.0 y NumPy 2.5.4.

Con la configuración inicial (30 llamadas/h, atención media 6 min, meta 80 %,
umbral 20 s, 4800 min medidos tras 1000 min de calentamiento, 30 repeticiones y
semilla 42) el mínimo teórico fue **6 agentes** y los escenarios seleccionados
fueron **5, 6 y 7**.

| Agentes | Servicio teórico | Servicio simulado | IC 95 % aproximado | Lectura frente a 80 % |
| --- | --- | --- | --- | --- |
| 5 | 78.87 % | 79.77 % | [78.71 %, 80.82 %] | No concluyente |
| 6 | 91.61 % | 92.09 % | [91.50 %, 92.68 %] | Cumplimiento respaldado |
| 7 | 96.99 % | 97.22 % | [96.90 %, 97.55 %] | Cumplimiento respaldado |

Se verificaron manualmente la apertura de la ventana, la tabla y la gráfica con
ambos métodos, el estado ocupado, la prevención de ejecuciones simultáneas, la
restauración del botón tras un error, varias ejecuciones consecutivas y el
cierre durante un estudio en curso sin bloquear el proceso. También se comprobó
que con una meta del 1 % el mínimo es 4 y se muestran los escenarios 4, 5 y 6
porque el agente 3 es inestable.

Comandos usados para la comprobación principal:

```bash
python main.py
python -m compileall app main.py
```

No se añadieron archivos de tests ni scripts de comprobación permanentes.

## Limitaciones

- La conclusión estadística depende de la duración, del calentamiento, del
  número de repeticiones y de la semilla. Un intervalo que incluye la meta no
  permite afirmar cumplimiento ni incumplimiento.
- Los escenarios comparten las mismas trayectorias aleatorias para reducir
  ruido en la comparación; no son muestras independientes entre sí.
- El modelo supone estacionariedad, llegadas Poisson, servicios exponenciales
  independientes y cola sin abandono. No representa horarios variables,
  prioridades ni llamadas abandonadas.
- La aplicación se comprobó en Linux con Tcl/Tk 8.6. No se verificó en Windows
  ni macOS.
