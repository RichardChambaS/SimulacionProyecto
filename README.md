# Centro de llamadas con Erlang-C y simulación M/M/c

Aplicación de escritorio en Python para buscar el mínimo teórico de agentes que
cumple una meta de servicio y contrastarlo con una simulación de eventos discretos.
Presenta tres escenarios, cinco medidas comparables, intervalos aproximados del
95 %, tres gráficas y una exportación reproducible.

## Copia de trabajo

Esta revisión se encuentra en la carpeta que contiene este README y main.py.
En el entorno original es SimulacionP1/SimulacionProyecto. La subcarpeta anidada
SimulacionProyecto/ es una copia anterior y no forma parte de la entrega corregida.
No se ha borrado ni actualizado esa copia. El ZIP de entrega excluye esa carpeta,
el entorno virtual y los metadatos Git.

## Ejecutar en Windows

Se requiere Python 3.10 o posterior con Tkinter y Tcl/Tk. No utilizar Python 2.7.
En el equipo revisado ya existe un entorno virtual válido. Desde esta carpeta:

~~~powershell
.\.venv\Scripts\python.exe main.py
~~~

Para una instalación nueva, utilizar un Python 3 instalado y crear el entorno:

~~~powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
~~~

Si no existe el lanzador py, ejecutar la primera instrucción con la ruta del
python.exe de Python 3. El comando global python puede apuntar a otra versión.

En Linux o macOS, crear el entorno con python3 -m venv .venv y utilizar
.venv/bin/python para instalar requirements.txt y ejecutar main.py. En Linux
puede ser necesario instalar el soporte de Tkinter mediante el gestor del sistema.

Matplotlib dibuja las gráficas; SciPy aporta el valor crítico t de Student.
NumPy se instala como dependencia de estas bibliotecas; el motor usa Random
de la biblioteca estándar, no NumPy ni SimPy.

## Uso

1. Revisar λ (llegadas por minuto), h (atención media en minutos), t₀ (espera máxima
   en segundos) y S₀ (meta en porcentaje). Se aceptan coma o punto decimal.
2. Elegir agentes automáticamente o introducir tres cantidades distintas y estables
   en modo manual. Para recuperar el caso 4, 6 y 8, pulsar Restablecer el caso del informe.
3. Abrir Opciones de simulación para revisar tiempo medido, tiempo inicial
   (calentamiento), R (repeticiones) y semilla. Al inicio mantienen los valores anteriores.
4. Pulsar Ejecutar simulación. El estado muestra la repetición actual y el tiempo
   transcurrido; la barra avanza al completar cada repetición.
5. Revisar el resumen y las pestañas Nivel de servicio, Espera media, Utilización
   y Medidas. Esta última muestra las cinco medidas con un selector Simulación/Erlang-C.
6. Pulsar Exportar y elegir una carpeta. Se crea una subcarpeta única.
7. Cancelar permite detener un estudio. Si ya había un estudio completo, se
   conserva para su consulta y exportación. Los estudios incompletos no se exportan.

Los campos permanecen bloqueados durante el cálculo y no se permiten ejecuciones
simultáneas. El resumen identifica la configuración del último estudio completo,
aunque después se cambien las entradas del formulario.

La pantalla presenta medias y una lectura sencilla de la meta. Cumple y No cumple
significan cumplimiento o incumplimiento respaldado por el intervalo del 95 %;
No concluyente significa que el intervalo cruza la meta. Las barras de las gráficas
conservan los intervalos. Las diferencias, errores e intervalos de todas las medidas
se conservan en JSON/CSV, sin añadir esas columnas a la pantalla.

La vista muestra μ = 1/h y A = λh. El mínimo teórico se calcula siempre por separado,
incluso si los escenarios manuales no contienen ese mínimo. Los agentes elegidos
quedan registrados en los escenarios de la exportación.

## Avisos antes de ejecutar

La aplicación estima 2 × λ × (calentamiento + tiempo medido) × R × 3 eventos,
con λ por minuto: una llegada y una finalización por llamada. Es una estimación
de trabajo, no un pronóstico exacto de duración ni una comprobación de precisión.

- Más de 5 millones de eventos esperados: aviso con opción de continuar o cancelar.
- Más de 1000 millones, trabajo no representable, o carga/agentes manuales que
  exigirían recorrer más de un millón de agentes en la teoría: se detiene antes
  de iniciar y se pide reducir los valores. Son límites de uso de esta aplicación,
  no restricciones matemáticas de M/M/c ni requisitos del informe.
- La estimación también bloquea enteros que desbordan el cálculo y más de
  333 333 333 repeticiones por escenario, incluso si hay muy pocas llegadas.
  Cada repetición supone trabajo y el límite no depende solo de las llamadas.
- Los parámetros nunca se reducen automáticamente. La cancelación permanece disponible.

Ejemplo: 20 000 llamadas/h equivalen a 333,333… llamadas/min. Con los demás valores
iniciales se estiman 348 millones de eventos y se solicita confirmación. Introducir
20 000 directamente en λ significa 20 000 por minuto y supera el límite de trabajo.

## Comprobar las validaciones

Desde esta carpeta, con las dependencias instaladas:

~~~powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

La suite comprueba el modelo y los campos de la interfaz: cero y negativos,
enteros y decimales, campos vacíos, texto, valores no finitos, agentes repetidos,
escenarios inestables y límites de trabajo. Los casos de Tkinter necesitan una
pantalla disponible; se omiten expresamente si el entorno no dispone de ella.

## Parámetros y alcance

Los valores del caso son 30 llamadas/hora, 6 minutos de atención media y una meta
del 80 % con espera de hasta 20 segundos. Los valores iniciales de 4800 minutos
medidos, 1000 minutos de calentamiento, 30 repeticiones y semilla 42 son ejemplos
de configuración del programa. El equipo debe justificar o ajustar la configuración
del experimento definitivo; no son requisitos del profesor.

El programa exige al menos dos repeticiones para calcular la variabilidad. Ese
mínimo técnico no garantiza que las estimaciones sean suficientemente precisas.

- Llegadas Poisson, servicios exponenciales independientes y tasas constantes.
- Una cola FIFO ilimitada, agentes equivalentes y sin abandono.
- Cada agente atiende una sola llamada a la vez.
- Las finalizaciones se procesan antes que las llegadas empatadas.
- La comparación estacionaria requiere agentes > carga ofrecida.
- La búsqueda del mínimo teórico recorre los enteros estables hasta cumplir la meta.
- Los escenarios confirmados para el caso son 4, 6 y 8 agentes: dotación inferior,
  mínimo teórico y dotación superior. La demanda y los demás parámetros se mantienen.
- Para otras entradas se muestran mínimo - 2, mínimo y mínimo + 2. Si el primero
  es inestable, se usa mínimo - 1; si también es inestable, se muestran mínimo,
  mínimo + 2 y mínimo + 4. La búsqueda del mínimo sigue evaluando todos los enteros
  estables, incluido 5 en el caso actual.
- En modo manual se comparan las tres cantidades introducidas, ordenadas de menor
  a mayor. Cada una debe satisfacer c > A. La búsqueda del mínimo no cambia.

## Definiciones y medición

El motor trabaja en minutos. La interfaz recibe λ en llamadas por minuto y lo
convierte al campo tasa_llegadas_hora del contrato interno. El umbral se introduce
en segundos y se muestra su equivalencia en minutos; S₀ se convierte de % a proporción.
La vista presenta las esperas en segundos y las proporciones en %.

Las llamadas medidas llegan en [calentamiento, calentamiento + duración).
Las llegadas del calentamiento influyen en el estado, pero no en el denominador de
las medidas por llamada. Al cerrar las llegadas se completa la atención pendiente.

- Nivel de servicio: fracción con espera menor o igual al umbral, incluidos los ceros.
- Espera media: espera de todas las llamadas medidas, incluidas las inmediatas.
- Probabilidad de espera: fracción con espera estrictamente positiva.
- Utilización: integral de agentes ocupados, dividida para duración y agentes.
- Longitud media de cola: integral temporal del número de llamadas esperando,
  dividida para la duración. Incluye el estado heredado del calentamiento.

Utilización y longitud de cola se recortan a la ventana medida. No incluyen el
vaciado posterior. La igualdad Lq = lambda * Wq es estacionaria: una ventana finita
puede producir diferencias por sus fronteras y por la variación aleatoria. Lq se
mide de forma independiente, no se obtiene multiplicando la espera simulada.

## Repeticiones, intervalos y comparación

Cada repetición utiliza dos semillas de texto registradas:
semilla:indice:llegadas y semilla:indice:atenciones, con indice interno desde cero.
Las repeticiones usan semillas distintas. Los escenarios reutilizan las mismas
entradas para reducir ruido en su comparación; no son independientes entre sí.

El resumen es la media entre repeticiones. El conteo de llamadas es la suma.
Para cada una de las cinco medidas se calcula:

media ± t(0.975, R - 1) * desviación muestral / sqrt(R)

Se usa t de Student y se recortan los límites al dominio de la medida. Son
intervalos aproximados: no corrigen sesgo por calentamiento insuficiente y su
precisión debe revisarse. Las llamadas correlacionadas de una repetición no se
consideran muestras independientes.

- Límite inferior del servicio >= meta: cumplimiento respaldado.
- Límite superior del servicio < meta: incumplimiento respaldado.
- En otro caso: no concluyente.

El mínimo anunciado es teórico. Una simulación que respalda un escenario no
demuestra por sí sola un mínimo absoluto. Un escenario no concluyente exige
mayor precisión o una conclusión que reconozca la incertidumbre.

La comparación muestra diferencia = simulado - teórico, error absoluto y error
relativo (%) = 100 * abs(simulado - teórico) / abs(teórico).
Si la referencia es cero, el error relativo queda sin definir.
Las diferencias de proporciones se muestran en puntos porcentuales (pp).

## Archivos exportados

- estudio.json: configuración, versiones, teoría, medias, intervalos y repeticiones.
- comparacion.csv: las cinco medidas por escenario y sus diferencias.
- repeticiones.csv: datos de cada repetición y las dos semillas exactas.
- nivel_servicio.png, espera_media_minutos.png y utilizacion.png: tres gráficas.
- LEEME.txt: unidades y criterios de lectura de los archivos.

Los CSV usan coma, punto decimal y UTF-8 con BOM. JSON y CSV conservan minutos
y proporciones; las imágenes usan segundos y porcentajes.
La fecha de las carpetas y los metadatos se identifica expresamente en UTC.
Cada exportación crea una carpeta única y no sobrescribe un estudio anterior.

## Organización del código

- app/modelo/: configuración, teoría, simulación, datos y comparación.
- app/vista/: formulario, tablas y gráficas.
- app/controlador/: ejecución en segundo plano, progreso, cancelación y exportación.
- app/exportacion.py: serialización de datos y guardado de las tres figuras.
- app/planificacion.py: estimación previa y límites de trabajo de la aplicación.
- main.py: construcción y arranque de los componentes.

La separación MVC y el contrato común evaluar son decisiones de implementación,
no requisitos atribuidos al profesor. No se necesita una clase padre abstracta.

## Verificación de esta revisión

Se ejecutaron 85 comprobaciones temporales con Python 3.14.4 en Windows:
fórmula independiente de Erlang-C, casos controlados de FIFO y empates, medición
por ventana y calentamiento, vaciado final, reproducibilidad, clasificación,
validación de entradas, exportación JSON/CSV/PNG, actualización de las tres gráficas,
conservación de canvas, progreso, cancelación y recuperación ante errores.

Se añadieron 24 comprobaciones de la nueva interfaz: igualdad exacta de todos los
resultados automáticos frente a la versión anterior, conversiones de unidades,
agentes manuales, independencia del mínimo teórico, rechazo de escenarios inestables,
avisos y bloqueo de cargas extremas. Se revisó la presentación en 1200×820 y 1030×700.

Los scripts de comprobación no forman parte del paquete de la aplicación.
Estas pruebas verifican el programa. No sustituyen la elección y justificación
del experimento académico ni la redacción de los resultados.

## Pendientes del informe

La metodología está integrada en ASD_revision_actual.docx y los resultados se
presentan por separado en Resultados_propuesta.docx. Los escenarios 4, 6 y 8 están
confirmados. El equipo debe revisar los demás apartados marcados como propuesta,
justificar la configuración experimental y conservar el estudio definitivo antes
de completar discusión, conclusiones y recomendaciones. Al final se actualizan
el resumen, la declaratoria de IA y la correspondencia entre citas y referencias.
