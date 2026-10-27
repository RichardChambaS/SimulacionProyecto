# Centro de llamadas: Erlang-C y simulación de eventos discretos

Aplicación de escritorio en Python para determinar el **número mínimo de agentes** que permite atender al menos el **80 % de las llamadas con una espera de hasta 20 segundos**, y comparar el cálculo de Erlang-C con una simulación M/M/c.

El caso de estudio es hipotético: recibe 30 llamadas por hora, con una atención media de 6 minutos. La meta del 80 % en 20 segundos es un criterio del ejercicio. No se realiza una optimización de costos.

## Funcionalidades

- Cálculo del mínimo teórico mediante Erlang-C y validación de estabilidad.
- Simulación de llegadas, cola FIFO y finalizaciones mediante un calendario de eventos.
- Repeticiones reproducibles con semilla e intervalo aproximado del 95 % para el nivel de servicio.
- Comparación automática de tres cantidades de agentes.
- Interfaz con parámetros configurables, tabla de métricas y gráfica del nivel de servicio.
- Ejecución en segundo plano para mantener la ventana operativa.

La aplicación incluye teoría, simulación e integración gráfica. Las incidencias conocidas de la vista se detallan al final; todavía están pendientes algunas gráficas del informe.

## Requisitos

- **Python 3.10 o posterior**, con `venv` y `pip`. No es compatible con Python 2.7.
- **Tkinter y Tcl/Tk**, necesarios para la ventana y el backend `TkAgg`.
- **Matplotlib**, declarado en [requirements.txt](requirements.txt).

Matplotlib instala sus dependencias, entre ellas NumPy y Pillow. El código del proyecto no importa SciPy ni utiliza directamente NumPy, por lo que no se declaran como dependencias directas. El motor utiliza la biblioteca estándar y no requiere SimPy. Tkinter se proporciona con la instalación de Python o con el sistema operativo; no se instala con `pip`.

## Instalación y ejecución

Clonar el repositorio y entrar a la carpeta:

```bash
git clone https://github.com/RichardChambaS/SimulacionProyecto.git
cd SimulacionProyecto
```

### Windows — PowerShell

Comprobar que el lanzador selecciona Python 3.10 o posterior:

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Estos comandos utilizan directamente el intérprete del entorno virtual y no necesitan activar scripts de PowerShell. Si `py` no está disponible, utilizar la ruta al ejecutable de Python 3 instalado para crear el entorno. No sustituirlo por un comando `python` que apunte a Python 2.7.

### Linux / macOS

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

En Debian/Ubuntu puede ser necesario instalar previamente los paquetes del sistema `python3-venv` y `python3-tk`. Se necesita una sesión gráfica para abrir la interfaz.

### Comprobar Tkinter

En Windows:

```powershell
.\.venv\Scripts\python.exe -m tkinter
```

En Linux/macOS:

```bash
.venv/bin/python -m tkinter
```

Se debe abrir una ventana de demostración; cerrarla antes de ejecutar `main.py`. Si aparece un error sobre `_tkinter`, Tcl/Tk o `init.tcl`, revisar la instalación de Python y su soporte de Tkinter.

## Uso de la aplicación

1. Ejecutar `main.py` desde la raíz del proyecto.
2. Introducir los parámetros o conservar los valores iniciales.
3. Pulsar **Ejecutar estudio**. El botón se deshabilita y aparece **Calculando...**.
4. Al finalizar, revisar el mínimo teórico, las tres filas de resultados y la gráfica.
5. Para comparar otra configuración, modificar los campos y repetir la ejecución.

La tabla muestra utilización, nivel de servicio y espera media de ambos métodos, además del intervalo de servicio y el número total de llamadas medidas de la simulación. Las esperas se muestran en **minutos**. La duración ingresada representa **tiempo simulado**, no tiempo de ejecución del programa.

La versión actual muestra las reglas de interpretación del intervalo en el resumen; la clasificación de cada fila debe hacerse con esas reglas. No incorpora exportación de resultados ni gráficas individuales de espera o utilización.

## Parámetros iniciales

| Parámetro | Valor | Unidad o significado |
| --- | --- | --- |
| Tasa de llegadas | 30 | Llamadas por hora |
| Atención media | 6 | Minutos por llamada |
| Meta de servicio | 80 | Porcentaje en la interfaz; `0.80` en el modelo |
| Umbral de espera | 20 | Segundos; incluye exactamente el umbral |
| Duración medida | 4800 | Minutos posteriores al calentamiento |
| Calentamiento | 1000 | Minutos iniciales excluidos de las métricas de llamadas |
| Repeticiones | 30 | Ejecuciones independientes por escenario; mínimo permitido: 30 |
| Semilla | 42 | Entero no negativo |

La tasa de llegadas equivale a `0.5 llamadas/minuto`; la tasa de servicio por agente, a `1/6 llamadas/minuto`. La carga ofrecida es de **3 erlangs**. Todos los cálculos internos utilizan minutos.

La duración, el calentamiento, las repeticiones y la semilla son valores iniciales ajustables del experimento, no observaciones de una empresa real.

## Modelo y cálculo teórico

El sistema M/M/c supone llegadas Poisson, tiempos entre llegadas y de atención exponenciales e independientes, agentes de igual capacidad y una única cola FIFO ilimitada. Cada agente atiende una llamada a la vez. Las tasas permanecen constantes y no hay abandono, descansos, prioridades ni turnos.

Con `lambda` y `mu` expresadas por minuto, `c` agentes y `t` minutos de espera:

```text
Carga ofrecida:           a = lambda / mu
Utilización teórica:     rho = a / c
Estabilidad:             c > a
Probabilidad de esperar: C = Erlang-C(c, a)
Nivel de servicio:       SL(t) = 1 - C * exp(-(c * mu - lambda) * t)
Espera media en cola:    Wq = C / (c * mu - lambda)
```

`Wq` promedia las llamadas que esperan y las atendidas inmediatamente. La espera termina cuando **comienza** la atención: el umbral no limita la duración de la conversación.

La implementación obtiene Erlang-C mediante una recurrencia de Erlang-B, sin factoriales grandes. Busca desde `floor(a) + 1` y devuelve el primer entero estable que alcanza la meta. Los escenarios mostrados son ese mínimo y sus dos vecinos. Si el vecino inferior es inestable, se utilizan el mínimo y las dos cantidades siguientes. Con la configuración inicial se comparan **5, 6 y 7 agentes**.

## Simulación y tratamiento estadístico

- `heapq` administra el calendario de eventos y `deque` conserva el orden FIFO.
- Cuando coinciden los tiempos, se procesan las finalizaciones antes que las llegadas.
- Cada repetición comienza vacía y atraviesa un calentamiento antes de medir.
- Se miden las llamadas llegadas en `[calentamiento, calentamiento + duración)`. Se conserva el estado del sistema al comenzar la medición.
- Al terminar el período de llegadas se vacía el sistema para observar todas las esperas de la cohorte, incluso si la atención comienza después del corte.
- La utilización es el tiempo ocupado acumulado dentro del período medido dividido entre `agentes * duración`. Incluye servicios iniciados durante el calentamiento que continúan dentro de ese período.
- Las métricas finales son medias entre repeticiones; el conteo de llamadas suma todas las repeticiones.
- Cada repetición utiliza generadores locales distintos para llegadas y servicios. Al comparar cantidades de agentes se reutilizan las mismas trayectorias de llamadas, por lo que los escenarios están relacionados entre sí.

El intervalo aproximado del 95 % se calcula con los niveles de servicio de las repeticiones independientes:

```text
media ± 1.96 * desviación_muestral / sqrt(repeticiones)
```

Sus límites se recortan a `[0, 1]`. El intervalo estima la incertidumbre de Monte Carlo de la media; no elimina esa incertidumbre ni corrige el sesgo de un calentamiento insuficiente. Las llamadas de una repetición no se consideran muestras independientes para calcularlo.

| Condición respecto a la meta | Interpretación |
| --- | --- |
| Límite inferior >= meta | Cumplimiento respaldado por el intervalo |
| Límite superior < meta | Incumplimiento respaldado por el intervalo |
| El intervalo incluye la meta y su límite inferior es menor | No concluyente |

## Resultado reproducido

Comprobación del modelo realizada el **26 de octubre de 2026**, con Python **3.12.14** en Windows y los parámetros iniciales de la tabla anterior:

| Agentes | Servicio teórico | Servicio simulado | IC 95 % aproximado | Lectura frente a 80 % |
| --- | --- | --- | --- | --- |
| 5 | 78.87 % | 79.77 % | [78.71 %, 80.82 %] | No concluyente |
| 6 | 91.61 % | 92.09 % | [91.50 %, 92.68 %] | Cumplimiento respaldado |
| 7 | 96.99 % | 97.22 % | [96.90 %, 97.55 %] | Cumplimiento respaldado |

Se midieron **71 952 llamadas por escenario**, sumadas sobre las 30 repeticiones. Repetir el escenario con la misma configuración y semilla reprodujo el resultado en el mismo entorno.

El **mínimo teórico es 6 agentes**: 5 no alcanzan la meta y 6 sí. La simulación respalda el cumplimiento con 6, pero el intervalo de 5 cruza el 80 %, por lo que no demuestra que 5 incumplan. No se afirma un mínimo simulado concluyente ni un mínimo fuera de los escenarios evaluados.

Los resultados de otra semilla o versión de Python pueden variar. Para reproducir exactamente un experimento deben conservarse los parámetros y las versiones del entorno.

### Verificación realizada

Se instaló `requirements.txt` en un entorno virtual aislado de Windows con Python 3.12.14, Matplotlib 3.11.2, NumPy 2.5.4, Pillow 13.0.0 y Tcl/Tk 8.6.12. `pip check` no detectó dependencias incompatibles.

Se comprobó el estudio completo, la reproducción de un escenario con la misma semilla y la selección de escenarios estables. También se creó la ventana Tkinter y se ejecutó el controlador real: la tabla recibió tres filas, el botón volvió a habilitarse y el bucle de eventos continuó procesando callbacks durante el cálculo. Se reprodujeron las incidencias de conversión de enteros y acumulación de canvas descritas al final. Las comprobaciones se ejecutaron mediante código temporal en consola; no se añadieron archivos de tests.

## Arquitectura y organización

Se utiliza **MVC** con un solo controlador:

- **Modelo:** define parámetros y resultados, calcula Erlang-C, simula eventos y organiza la comparación. No depende de la interfaz gráfica.
- **Vista:** recoge entradas y presenta tabla, resumen y gráfica con Tkinter/ttk y Matplotlib.
- **Controlador:** valida, ejecuta el estudio en un hilo de trabajo y consulta su resultado mediante una cola y `after()`. Las actualizaciones de widgets ocurren en el hilo principal.

El patrón **Strategy** se expresa en `ErlangC` y `Simulador`: ambos implementan `evaluar(configuracion, agentes)`. `EstudioServicio` los recibe por constructor y utiliza ambos para obtener resultados comparables. `main.py` construye y conecta los componentes.

```text
SimulacionProyecto/
├── main.py
├── requirements.txt
├── README.md
├── COORDINACION.md
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── modelo/
│   │   ├── __init__.py
│   │   ├── configuracion.py       # Parámetros, conversiones y validación
│   │   ├── resultados.py          # Dataclasses compartidas
│   │   ├── erlang_c.py            # Teoría y búsqueda del mínimo
│   │   ├── simulacion.py          # Eventos, repeticiones y estadística
│   │   └── estudio.py             # Selección y comparación de escenarios
│   ├── vista/
│   │   ├── __init__.py
│   │   ├── ventana_principal.py   # Formulario, tabla y resumen
│   │   └── graficos.py            # Gráfica del nivel de servicio
│   └── controlador/
│       ├── __init__.py
│       └── controlador.py         # Coordinación y ejecución en segundo plano
└── docs/
    ├── Richard.md
    ├── Martina.md
    ├── Emilio.md
    └── Derick.md
```

## Equipo y trabajo por commits

| Integrante | Responsabilidad | Guía |
| --- | --- | --- |
| Richard | Base, configuración, resultados y Erlang-C | [Richard.md](docs/Richard.md) |
| Martina | Simulación de eventos y repeticiones | [Martina.md](docs/Martina.md) |
| Emilio | Interfaz y gráficas | [Emilio.md](docs/Emilio.md) |
| Derick | Estudio, controlador e integración | [Derick.md](docs/Derick.md) |

Las reglas compartidas están en [COORDINACION.md](COORDINACION.md). Cada integrante registra sus avances mediante commits y marca `[x]` solo las tareas terminadas y comprobadas. Los documentos individuales pueden conservar pendientes administrativos aunque su código ya se haya integrado; consultar también el historial de Git.

## Incidencias conocidas y alcance pendiente

En la revisión del código actual se identificaron estos puntos:

1. **Meta gráfica fija:** la línea de referencia de `graficos.py` usa `0.80` aunque se modifique la meta en el formulario. El cálculo utiliza la meta ingresada; la línea solo coincide con ella cuando es 80 %.
2. **Conversión de enteros:** el formulario convierte repeticiones y semilla mediante `int(float(...))`, por lo que trunca decimales. Introducir enteros exactos. Un valor infinito puede producir una excepción de conversión sin el mensaje de validación esperado.
3. **Actualización del canvas:** el canvas se crea con `master=None`, fuera del marco destinado a la gráfica. La limpieza de ese marco no elimina los canvas anteriores y puede acumular widgets al repetir ejecuciones.
4. **Gráficas del informe:** solo está implementada la gráfica del nivel de servicio. La espera y la utilización aparecen en la tabla; sus gráficas todavía deben incorporarse para cubrir esa parte del alcance académico.

Estas incidencias están documentadas para su corrección; no se modificaron los módulos Python durante esta revisión. El modelo excluye costos, abandono y turnos, y no reproduce una operación real con demanda variable. Cerrar la ventana finaliza la aplicación sin guardar resultados ni esperar al estudio de fondo.

## Fuentes técnicas

- [NPTEL: modelo M/M/c y Erlang-C](https://archive.nptel.ac.in/content/storage2/courses/117103017/module3/lec2/1.html).
- [Python: entornos virtuales](https://docs.python.org/3/library/venv.html).
- [Matplotlib: dependencias](https://matplotlib.org/stable/install/dependencies.html).
