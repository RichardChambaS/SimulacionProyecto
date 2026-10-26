# M — Simulación de eventos discretos

## Mensaje para tu agente

> Soy M. Lee `COORDINACION.md` y `docs/Martina.md` completos. Comprueba que la base de R esté integrada y sincroniza mi rama. Implementa únicamente `app/modelo/simulacion.py` y actualiza `docs/Martina.md`. Respeta los contratos de configuración y resultados; no dupliques las clases de R ni implementes interfaz, teoría o controlador. No crees tests ni inicies otros agentes. Haz commits por avances coherentes, marca con `[x]` solo tareas comprobadas y registra los resultados, bloqueos y la entrega a D. Si falta una dependencia compartida, indícala sin modificar archivos ajenos.

## Responsabilidad

Implementar `Simulador.evaluar(configuracion, agentes) -> ResultadoEvaluacion`, incluyendo las repeticiones y el intervalo aproximado del nivel de servicio. El resultado debe ser reproducible mediante la semilla.

Archivos propios: `app/modelo/simulacion.py` y este documento. Puedes usar funciones o clases internas en el mismo módulo para mantener la estructura simple.

## Dependencias

Necesitas `Configuracion` y las dataclasses de resultados implementadas por R. No necesitas esperar a la interfaz ni al cálculo de Erlang-C para construir el motor. Para la comparación final, sincroniza la teoría cuando se integre.

## Tareas

- [x] Sincronizar la base de R y crear `feature/m-simulacion` desde `main` actualizado.
- [x] Validar configuración, cantidad de agentes y estabilidad antes de simular.
- [x] Crear el calendario de eventos con `heapq`, contador para desempates y prioridad de finalización sobre llegada.
- [x] Implementar llegadas exponenciales, tiempos de servicio exponenciales independientes y cola FIFO con `deque`.
- [x] Asignar agentes libres inmediatamente y respetar las llamadas que ya esperaban.
- [x] Aplicar el calentamiento sin reiniciar el estado de la cola o los agentes al comenzar la medición.
- [x] Medir la cohorte de llegadas del período definido y observar todas sus esperas, incluso después del corte de llegadas.
- [x] Acumular ocupación real sobre el período medido, recortando los intervalos a sus límites; incluir servicios iniciados durante el calentamiento.
- [x] Calcular por repetición el nivel de servicio, la proporción que espera y la espera media.
- [x] Ejecutar las repeticiones con generadores locales y semillas reproducibles distintas por repetición; evitar depender del estado aleatorio global.
- [x] Resumir las métricas por media entre repeticiones; `llamadas_medidas` será la suma de llamadas medidas de todas ellas.
- [x] Calcular y devolver el intervalo aproximado del 95 % sobre los niveles de servicio de las repeticiones, según `COORDINACION.md`.
- [x] Gestionar una repetición sin llamadas medidas con un error legible que recomiende ampliar la duración; no dividir para cero ni inventar métricas.
- [x] Comprobar manualmente FIFO, no negatividad de esperas, atención inmediata con agente disponible y orden de eventos simultáneos usando una secuencia controlada temporal.
- [x] Comprobar que misma configuración y semilla reproducen el resultado y que las repeticiones no reutilizan la misma trayectoria aleatoria.
- [x] Comparar resultados de una ejecución suficientemente larga con la teoría de R y registrar diferencias; investigar desviaciones relevantes sin ocultarlas ajustando semillas.
- [x] Crear commits locales por avances coherentes.
- [ ] Publicar la rama y abrir PR: pendiente por instrucción del usuario de no hacer push.
- [x] Documentar la entrega a D.

Las comprobaciones pueden realizarse desde la consola de Python o con comandos temporales. No incorporar una carpeta de tests ni scripts de pruebas permanentes.

## Commits sugeridos

1. `feat(simulacion): implementar eventos y cola FIFO`.
2. `feat(simulacion): agregar replicas e intervalos`.

## Entrega a D

- Estado: implementación de Martina completada y comprobada localmente. No publicada ni integrada en `main`, por instrucción del usuario de no hacer push.
- Rama: `feature/m-simulacion`, creada desde `origin/main` en `fc9b553`, con la base y la teoría de Richard ya integradas. Primer commit local: `ad7cb27` (`feat(simulacion): implementar eventos y cola FIFO`). Segundo commit local: `06de533` (`feat(simulacion): agregar replicas e intervalos`). Este registro final se guarda en un commit documental posterior.
- PR: no se abrirá en esta continuación; el usuario solicitó trabajar sin hacer push.
- Configuración de comparación: 30 llamadas/h, atención media de 6 min, meta 0.80 en 20 s, duración medida de 4800 min después de 1000 min de calentamiento, 30 repeticiones y semilla 42. Se evaluaron 4, 5 y 6 agentes. Motor: secuencias controladas temporales con uno y dos agentes. Python 3.12.14.
- Comprobaciones manuales del motor, ejecutadas mediante la entrada estándar de Python: siete escenarios controlados correctos y diez escenarios inválidos rechazados con `ValueError`. No se crearon tests ni scripts permanentes.
- Diferencias de nivel de servicio simulado menos teórico: +1.135491, +0.899524 y +0.480353 puntos porcentuales para 4, 5 y 6 agentes. Los valores teóricos quedaron dentro de los tres intervalos aproximados del 95 %. Los escenarios comparten trayectorias para facilitar la comparación; dentro de cada escenario las 30 repeticiones usan fuentes distintas. El intervalo no elimina el error de Monte Carlo ni un posible sesgo por calentamiento insuficiente.
- Siguiente paso: conservar estos commits locales. Cuando el usuario autorice publicar, subir `feature/m-simulacion`, abrir un PR y entregar su enlace a Derick. Derick conectará `Simulador` con `EstudioServicio` y comprobará las métricas en la interfaz. Si continúa en esta misma copia local antes de publicar, debe integrar explícitamente los commits de Martina en su rama; cambiar de rama no incorpora automáticamente su trabajo.

## Bloqueos o cambios de contrato

- La base de Richard y Erlang-C ya están integrados en `origin/main` (`fc9b553`). Sin bloqueos de dependencias. Publicación y PR quedan pendientes por instrucción expresa del usuario: «sin pushear». No se modificarán archivos de Richard, Emilio o Derick.

## Evidencias del motor (2026-10-26)

- FIFO: tres llamadas con servicios distintos; las dos llamadas en cola esperaron 3.5 minutos cada una. Espera media `7/3`, ocupación `4.75/6` y cumplimiento del umbral exacto de 210 segundos.
- Empate temporal: una extracción controlada del calendario confirmó finalización antes de llegada en el instante 2.5. La llamada ya en cola mantuvo la prioridad.
- Corte de llegadas: con un período de dos minutos se contabilizaron dos llamadas, aunque la segunda comenzó su atención en el minuto 4.5. La utilización fue 0.75, excluyendo servicio posterior al corte.
- Calentamiento: un servicio iniciado antes del minuto 2 mantuvo ocupado al agente durante la medición; no se reinició el estado. Dos llamadas medidas, espera media 1.25 y utilización 1.0.
- Límites de cohorte: se incluyó una llegada exactamente al comienzo de medición y se excluyó una llegada exactamente al final. La ocupación de servicios previos al calentamiento no se sumó fuera del período.
- Atención paralela: dos agentes atendieron inmediatamente las dos primeras llamadas; la tercera esperó 1.5 minutos. Utilización 0.5625.
- Cohorte vacía: error legible que solicita ampliar la duración, incluso si hubo llamadas durante el calentamiento.
- Se rechazaron siete cantidades de agentes inválidas, un escenario inestable y dos períodos de medición no representables.
## Evidencias de repeticiones y estadística (2026-10-26)

- `Simulador.evaluar(configuracion, agentes)` devuelve el `ResultadoEvaluacion` acordado, sin dependencias externas.
- Semillas internas identificadas por semilla base, índice de repetición y fuente (`llegadas` o `atenciones`). Se comprobaron 60 estados iniciales distintos en las dos fuentes de las 30 repeticiones.
- Misma configuración y semilla: mismo resultado completo. Cambiar la semilla a 43 produjo otro resultado; la comparación de la tabla mantuvo la semilla 42 original. El estado del generador aleatorio global no cambió.
- Las medias de utilización, probabilidad de esperar, servicio y espera coincidieron con el resumen manual de las 30 repeticiones. El conteo sumó 71952 llamadas medidas por escenario.
- Se comprobó la fórmula del intervalo con la desviación muestral entre repeticiones: media ± 1.96 × desviación / raíz de 30, recortada a [0, 1].
- Los tres escenarios usaron la misma cohorte y los mismos servicios muestreados al llegar. Esto reduce ruido en las comparaciones; no convierte los escenarios entre sí en muestras independientes.
- La API pública rechazó ocho cantidades de agentes inválidas o inestables y tres configuraciones inválidas. Para una duración de `1e-10` minutos informó «Repetición 1» y pidió ampliar la duración al no haber llamadas medidas.

| Agentes | Servicio teórico | Servicio simulado | Intervalo aproximado 95 % | Interpretación frente a 80 % |
| --- | --- | --- | --- | --- |
| 4 | 51.809612 % | 52.945103 % | [51.299048 %, 54.591159 %] | Incumplimiento |
| 5 | 78.868226 % | 79.767750 % | [78.712025 %, 80.823475 %] | No concluyente |
| 6 | 91.607709 % | 92.088063 % | [91.498411 %, 92.677716 %] | Cumplimiento respaldado |

| Agentes | Espera media teórica (min) | Espera media simulada (min) | Utilización simulada |
| --- | --- | --- | --- |
| 4 | 3.056603774 | 2.863042458 | 0.744341679 |
| 5 | 0.708454810 | 0.661301137 | 0.595466873 |
| 6 | 0.198286414 | 0.182826710 | 0.496188010 |

La simulación respalda el cumplimiento con 6 agentes en estos escenarios. El mínimo teórico sigue siendo 6 según Erlang-C; no se afirma que la simulación haya demostrado un mínimo absoluto, ya que el resultado de 5 agentes es no concluyente.

Comprobación breve desde una consola de Python 3.10 o posterior, en la raíz del proyecto:

```python
from app.modelo.configuracion import Configuracion
from app.modelo.simulacion import Simulador

resultado = Simulador().evaluar(Configuracion(), 6)
print(resultado)
```

Las verificaciones se ejecutaron con código temporal por la entrada estándar de Python. No se añadieron carpetas de tests ni scripts permanentes de comprobación. La instrucción actual del usuario es **continuar sin hacer push**; no crear un PR ni publicar estos cambios hasta una nueva indicación.