# Coordinación del proyecto: R, M, E y D

Aplicación de escritorio en Python para determinar el mínimo de agentes que cumple una meta de servicio mediante Erlang-C y contrastarlo con simulación de eventos discretos M/M/c.

## Estado inicial

- [x] División del trabajo y documentos individuales preparados.
- [x] Repositorio GitHub creado y URL compartida por el equipo: https://github.com/RichardChambaS/SimulacionProyecto
- [x] Base y contratos implementados por R e integrados en `main`.
- [ ] Implementación e integración de las cuatro partes terminadas.

Se ha preparado la documentación y la estructura MVC con archivos vacíos. La implementación sigue pendiente. Esta lista describe los hitos; las tareas detalladas se marcan en el documento de cada responsable.

Avance del 2026-10-26: D implementó y comprobó localmente el estudio, el controlador, el arranque y la documentación. Estos cambios aún no tienen commit ni PR, por lo que el hito de integración de las cuatro partes permanece pendiente hasta confirmarlos en `main`.

## Reparto y propiedad de archivos

| Persona | Responsabilidad | Archivos propios |
| --- | --- | --- |
| R | Base, contratos de datos y teoría | `main.py` (arranque final lo completa D), `app/__init__.py`, `app/modelo/__init__.py`, `app/modelo/configuracion.py`, `app/modelo/resultados.py`, `app/modelo/erlang_c.py`, `.gitignore`, `docs/Richard.md` |
| M | Motor de simulación, repeticiones y estadística | `app/modelo/simulacion.py`, `docs/Martina.md` |
| E | Interfaz gráfica y gráficas | `app/vista/__init__.py`, `app/vista/ventana_principal.py`, `app/vista/graficos.py`, `requirements.txt`, `docs/Emilio.md` |
| D | Estudio comparativo, controlador e integración | `app/modelo/estudio.py`, `app/controlador/__init__.py`, `app/controlador/controlador.py`, `README.md`, `docs/Derick.md`, `COORDINACION.md` |

R crea `main.py` como entrada mínima y se lo entrega a D después del primer hito. Desde entonces, solo D lo modifica. No se crearán carpetas ni archivos de tests; la validación será manual y sus evidencias quedarán en cada documento.

## Arquitectura acordada

- **Modelo:** configuración, resultados, teoría, simulación y organización del estudio. No importa Tkinter ni módulos de la vista.
- **Vista:** recoge entradas y muestra resultados. No calcula Erlang-C ni ejecuta simulaciones.
- **Controlador único:** conecta acciones, ejecución del estudio y presentación de resultados.
- **Strategy:** `ErlangC` y `Simulador` comparten el método `evaluar(configuracion, agentes)`. Cada clase implementa su algoritmo. No hace falta añadir una jerarquía de clases abstractas para esta práctica.
- `EstudioServicio` utiliza ambas estrategias para comparar los escenarios.

## Contratos que R debe publicar primero

Estos nombres y unidades deben respetarse. R los implementa; los demás agentes no los redefinen ni crean copias locales. Si necesitan cambiarlos, coordinan el cambio con el equipo antes de hacerlo.

### `Configuracion` en `app/modelo/configuracion.py`

Dataclass con estos campos y valores iniciales:

| Campo | Tipo | Valor inicial / significado |
| --- | --- | --- |
| `tasa_llegadas_hora` | `float` | `30.0` |
| `atencion_media_minutos` | `float` | `6.0` |
| `meta_servicio` | `float` | `0.80`; proporción, no porcentaje entero |
| `umbral_segundos` | `float` | `20.0` |
| `duracion_minutos` | `float` | `4800.0`; período medido, posterior al calentamiento |
| `calentamiento_minutos` | `float` | `1000.0` |
| `repeticiones` | `int` | `30` |
| `semilla` | `int` | `42` |

Los últimos cuatro valores son valores iniciales propuestos para la ejecución, no datos del problema original.

Método `validar() -> None`: lanza `ValueError` con mensaje legible ante entradas inválidas. Las tasas y duración deben ser positivas y finitas, el calentamiento y umbral no negativos, la meta debe cumplir `0 < meta_servicio < 1` y las repeticiones deben ser un entero de al menos 30. La semilla debe ser un entero no negativo. Las cantidades de agentes deben ser enteros positivos.

Propiedades derivadas: `tasa_llegadas_minuto`, `tasa_servicio_minuto`, `carga_erlangs` y `umbral_minutos`. Los cálculos internos utilizan minutos.

### Resultados en `app/modelo/resultados.py`

- `ResultadoEvaluacion`: `metodo: str`, `agentes: int`, `utilizacion: float`, `probabilidad_espera: float`, `nivel_servicio: float`, `espera_media_minutos: float`, `intervalo_servicio_95: tuple[float, float] | None = None`, `llamadas_medidas: int | None = None`.
- `ResultadoEscenario`: `agentes: int`, `teorico: ResultadoEvaluacion`, `simulado: ResultadoEvaluacion`.
- `ResultadoEstudio`: `configuracion: Configuracion`, `minimo_teorico: int`, `escenarios: list[ResultadoEscenario]`.

Son dataclasses. Probabilidades, utilización e intervalos se guardan como proporciones entre 0 y 1; solo la vista los convierte a porcentajes. `metodo` será `Erlang-C` o `Simulación`. La teoría no tiene intervalo de confianza ni conteo de llamadas. La utilización teórica es la carga dividida para el número de agentes; la simulada se estima sobre el período medido, incluyendo la ocupación por llamadas llegadas en el calentamiento.

### Interfaces entre módulos

| Módulo / clase | Interfaz pública |
| --- | --- |
| `erlang_c.ErlangC` | `evaluar(configuracion, agentes) -> ResultadoEvaluacion` y `buscar_minimo(configuracion) -> int` |
| `simulacion.Simulador` | `evaluar(configuracion, agentes) -> ResultadoEvaluacion`; devuelve el resumen de todas las repeticiones |
| `estudio.EstudioServicio` | Constructor `EstudioServicio(teorico, simulador)`; método `ejecutar(configuracion) -> ResultadoEstudio` |
| `vista.VentanaPrincipal` | Constructor sin argumentos; métodos `obtener_configuracion()`, `vincular_ejecucion(callback)`, `establecer_ocupado(ocupado)`, `mostrar_resultados(resultado)`, `mostrar_error(mensaje)` e `iniciar()` |
| `controlador.Controlador` | Constructor `Controlador(vista, estudio)`; método `ejecutar()` vinculado al botón de la vista |

`VentanaPrincipal` hereda de `tkinter.Tk`, de modo que D puede usar `after()` para consultar el trabajo de fondo. `obtener_configuracion()` convierte texto a números y puede lanzar `ValueError`; la validación de dominio sigue en el modelo. `iniciar()` ejecuta el bucle principal de Tkinter. `main.py` crea las dos estrategias, el estudio, la vista y el controlador, y llama a `vista.iniciar()`.

## Reglas matemáticas y estadísticas compartidas

- Llegadas Poisson, atención exponencial independiente, cola FIFO ilimitada y sin abandono.
- No se evalúan resultados estacionarios cuando `agentes <= carga_erlangs`; se informa el error. La búsqueda empieza en `floor(carga_erlangs) + 1`.
- La espera va desde la llegada hasta el inicio de atención. La meta incluye exactamente el umbral: `espera <= umbral_minutos`.
- Cuando hay empate temporal, las finalizaciones se procesan antes de las llegadas; se conserva el orden FIFO.
- Las llamadas medidas son las que llegan en `[calentamiento, calentamiento + duracion)`. Todas deben tener su espera observada, aunque empiecen su atención después del período de llegadas. Las llamadas del calentamiento afectan al estado, pero no al denominador del nivel de servicio.
- M calcula un intervalo aproximado del 95 % a partir de los niveles de servicio de las repeticiones independientes: media ± `1.96 * desviacion_muestral / sqrt(repeticiones)`, acotado a `[0, 1]`. Se etiqueta como aproximado y se reconoce que no corrige un calentamiento insuficiente. No se tratan las llamadas correlacionadas de una sola repetición como muestras independientes.
- D muestra tres escenarios: mínimo teórico y sus vecinos. Si el vecino inferior es inestable, usa mínimo, mínimo + 1 y mínimo + 2.
- El mínimo teórico es el primer entero estable que cumple la meta. Para la simulación: límite inferior del intervalo >= meta indica cumplimiento respaldado; límite superior < meta indica incumplimiento; el resto indica resultado no concluyente. No se anuncia un mínimo simulado demostrado fuera de los escenarios evaluados.

## Orden de trabajo y commits

1. El equipo crea el repositorio GitHub y comparte la URL. Cada integrante usa su propia copia local y su cuenta Git.
2. R publica estos documentos como commit inicial de coordinación. Después crea su rama y entrega primero configuración, resultados, paquetes base y `main.py` mínimo. Integra esa base en `main` mediante un PR temprano.
3. Con la base integrada, M, E y D crean sus ramas desde `main`. R continúa Erlang-C. Las cuatro personas pueden trabajar en paralelo a partir de este punto.
4. Se integran Erlang-C, simulación e interfaz. D actualiza su rama con esos cambios, termina el arranque y verifica la aplicación completa antes de integrar su PR.
5. Cada persona marca únicamente sus tareas realmente terminadas y registra comprobaciones. D actualiza los hitos globales basándose en los documentos individuales y en los cambios integrados.

| Persona | Rama propuesta | Commits de referencia |
| --- | --- | --- |
| R | `feature/r-base-erlang` | `feat(modelo): definir configuracion y contratos`; `feat(teoria): implementar Erlang-C y busqueda minima` |
| M | `feature/m-simulacion` | `feat(simulacion): implementar eventos y cola FIFO`; `feat(simulacion): agregar replicas e intervalos` |
| E | `feature/e-interfaz` | `feat(vista): crear formulario y tabla`; `feat(vista): integrar graficas y estados` |
| D | `feature/d-integracion` | `feat(estudio): comparar teoria y simulacion`; `feat(controlador): conectar ejecucion e interfaz`; `docs: documentar ejecucion y validacion final` |

Para sincronizar: guardar primero el trabajo propio en un commit, ejecutar `git fetch origin`, y luego `git merge origin/main` desde la rama personal. Resolver conflictos entendiendo el contenido y coordinando con su responsable. No usar `push --force`, no sobrescribir trabajo ajeno y no subir `.venv`, cachés ni credenciales. Cada commit debe contener un avance coherente y ejecutable en el nivel correspondiente; no se exige que la GUI esté completa durante los primeros hitos.

## Cómo marcar el visto y entregar al siguiente

- Pendiente: `- [ ] Descripción`.
- Terminado y comprobado: `- [x] Descripción`.
- Bloqueado: dejar `[ ]` y explicar el motivo en el apartado de bloqueos.
- La casilla se marca en el mismo commit que completa la tarea. Si hay una corrección posterior, añadir otra entrada con la comprobación realizada.
- No marcar tareas de otras personas ni declarar integrado algo que solo existe en una rama.
- En cada entrega registrar rama, hash de commit, archivos, forma de comprobar, resultado observado y siguiente paso. Si el hash corresponde al commit que registra la entrega, añadirlo en el siguiente commit documental para evitar autorreferencia.
- Al abrir un PR de GitHub, adjuntar su enlace al documento individual. El visto indica trabajo completo; el estado del PR indica si ya está integrado.

## Inicio para cada agente

Cada persona debe entregar a su agente `COORDINACION.md` y el archivo `docs/<su nombre>.md` de la copia actualizada del repositorio. Los cuatro documentos contienen un mensaje listo para copiar. Ningún agente debe implementar las cuatro partes ni iniciar otros agentes por su cuenta.
