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
- [ ] Ejecutar las repeticiones con generadores locales y semillas reproducibles distintas por repetición; evitar depender del estado aleatorio global.
- [ ] Resumir las métricas por media entre repeticiones; `llamadas_medidas` será la suma de llamadas medidas de todas ellas.
- [ ] Calcular y devolver el intervalo aproximado del 95 % sobre los niveles de servicio de las repeticiones, según `COORDINACION.md`.
- [x] Gestionar una repetición sin llamadas medidas con un error legible que recomiende ampliar la duración; no dividir para cero ni inventar métricas.
- [x] Comprobar manualmente FIFO, no negatividad de esperas, atención inmediata con agente disponible y orden de eventos simultáneos usando una secuencia controlada temporal.
- [ ] Comprobar que misma configuración y semilla reproducen el resultado y que las repeticiones no reutilizan la misma trayectoria aleatoria.
- [ ] Comparar resultados de una ejecución suficientemente larga con la teoría de R y registrar diferencias; investigar desviaciones relevantes sin ocultarlas ajustando semillas.
- [ ] Crear commits locales por avances coherentes.
- [ ] Publicar la rama y abrir PR: pendiente por instrucción del usuario de no hacer push.
- [ ] Documentar la entrega a D.

Las comprobaciones pueden realizarse desde la consola de Python o con comandos temporales. No incorporar una carpeta de tests ni scripts de pruebas permanentes.

## Commits sugeridos

1. `feat(simulacion): implementar eventos y cola FIFO`.
2. `feat(simulacion): agregar replicas e intervalos`.

## Entrega a D

- Estado: motor de eventos implementado y comprobado localmente; repeticiones y resumen estadístico en preparación.
- Rama: `feature/m-simulacion`, creada desde `origin/main` en `fc9b553`, con la base y la teoría de Richard ya integradas. Los hashes locales se registrarán en la entrega.
- PR: no se abrirá en esta continuación; el usuario solicitó trabajar sin hacer push.
- Motor: secuencias deterministas temporales con un agente y dos agentes; instantes elegidos para comprobar empates, FIFO, calentamiento y límites de la cohorte. Python 3.12.14.
- Comprobaciones manuales del motor, ejecutadas mediante la entrada estándar de Python: siete escenarios controlados correctos y diez escenarios inválidos rechazados con `ValueError`. No se crearon tests ni scripts permanentes.
- Diferencias con Erlang-C y limitaciones estadísticas: pendiente.
- Siguiente paso: D debe conectar `Simulador` con `EstudioServicio` y revisar las métricas en la interfaz.

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