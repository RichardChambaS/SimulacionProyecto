# M — Simulación de eventos discretos

## Mensaje para tu agente

> Soy M. Lee `COORDINACION.md` y `docs/Martina.md` completos. Comprueba que la base de R esté integrada y sincroniza mi rama. Implementa únicamente `app/modelo/simulacion.py` y actualiza `docs/Martina.md`. Respeta los contratos de configuración y resultados; no dupliques las clases de R ni implementes interfaz, teoría o controlador. No crees tests ni inicies otros agentes. Haz commits por avances coherentes, marca con `[x]` solo tareas comprobadas y registra los resultados, bloqueos y la entrega a D. Si falta una dependencia compartida, indícala sin modificar archivos ajenos.

## Responsabilidad

Implementar `Simulador.evaluar(configuracion, agentes) -> ResultadoEvaluacion`, incluyendo las repeticiones y el intervalo aproximado del nivel de servicio. El resultado debe ser reproducible mediante la semilla.

Archivos propios: `app/modelo/simulacion.py` y este documento. Puedes usar funciones o clases internas en el mismo módulo para mantener la estructura simple.

## Dependencias

Necesitas `Configuracion` y las dataclasses de resultados implementadas por R. No necesitas esperar a la interfaz ni al cálculo de Erlang-C para construir el motor. Para la comparación final, sincroniza la teoría cuando se integre.

## Tareas

- [ ] Sincronizar la base de R y crear `feature/m-simulacion` desde `main` actualizado.
- [ ] Validar configuración, cantidad de agentes y estabilidad antes de simular.
- [ ] Crear el calendario de eventos con `heapq`, contador para desempates y prioridad de finalización sobre llegada.
- [ ] Implementar llegadas exponenciales, tiempos de servicio exponenciales independientes y cola FIFO con `deque`.
- [ ] Asignar agentes libres inmediatamente y respetar las llamadas que ya esperaban.
- [ ] Aplicar el calentamiento sin reiniciar el estado de la cola o los agentes al comenzar la medición.
- [ ] Medir la cohorte de llegadas del período definido y observar todas sus esperas, incluso después del corte de llegadas.
- [ ] Acumular ocupación real sobre el período medido, recortando los intervalos a sus límites; incluir servicios iniciados durante el calentamiento.
- [ ] Calcular por repetición el nivel de servicio, la proporción que espera y la espera media.
- [ ] Ejecutar las repeticiones con generadores locales y semillas reproducibles distintas por repetición; evitar depender del estado aleatorio global.
- [ ] Resumir las métricas por media entre repeticiones; `llamadas_medidas` será la suma de llamadas medidas de todas ellas.
- [ ] Calcular y devolver el intervalo aproximado del 95 % sobre los niveles de servicio de las repeticiones, según `COORDINACION.md`.
- [ ] Gestionar una repetición sin llamadas medidas con un error legible que recomiende ampliar la duración; no dividir para cero ni inventar métricas.
- [ ] Comprobar manualmente FIFO, no negatividad de esperas, atención inmediata con agente disponible y orden de eventos simultáneos usando una secuencia controlada temporal.
- [ ] Comprobar que misma configuración y semilla reproducen el resultado y que las repeticiones no reutilizan la misma trayectoria aleatoria.
- [ ] Comparar resultados de una ejecución suficientemente larga con la teoría de R y registrar diferencias; investigar desviaciones relevantes sin ocultarlas ajustando semillas.
- [ ] Crear commits, abrir PR y documentar la entrega a D.

Las comprobaciones pueden realizarse desde la consola de Python o con comandos temporales. No incorporar una carpeta de tests ni scripts de pruebas permanentes.

## Commits sugeridos

1. `feat(simulacion): implementar eventos y cola FIFO`.
2. `feat(simulacion): agregar replicas e intervalos`.

## Entrega a D

- Estado: pendiente.
- Rama / commits: pendiente.
- PR: pendiente.
- Configuración utilizada para comprobar: pendiente.
- Comandos o acciones de comprobación y resultados observados: pendiente.
- Diferencias con Erlang-C y limitaciones estadísticas: pendiente.
- Siguiente paso: D debe conectar `Simulador` con `EstudioServicio` y revisar las métricas en la interfaz.

## Bloqueos o cambios de contrato

- Inicial: esperar a que R integre configuración y resultados en `main`.
