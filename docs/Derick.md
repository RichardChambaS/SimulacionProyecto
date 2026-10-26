# D — Estudio, controlador e integración final

## Mensaje para tu agente

> Soy D. Lee `COORDINACION.md` y `docs/Derick.md` completos. Implementa mi parte de estudio comparativo, controlador único e integración, respetando los contratos y la propiedad de archivos. No implementes por tu cuenta los módulos pendientes de R, M o E y no dupliques sus clases. No crees tests ni inicies otros agentes. Trabaja por commits, marca con `[x]` solo lo comprobado y registra dependencias y entrega final. Completa `main.py` solo después de la entrega explícita de R. Integra las partes disponibles, verifica el flujo completo y actualiza el README; conserva y coordina cualquier cambio ajeno.

## Responsabilidad

Conectar el cálculo teórico, la simulación y la interfaz. Mantener un solo controlador y presentar una conclusión fiel a la evidencia estadística.

Archivos propios: `app/modelo/estudio.py`, `app/controlador/__init__.py`, `app/controlador/controlador.py`, `README.md`, `COORDINACION.md` y este documento. `main.py` pasa a tu cargo después de que R entregue la base.

## Dependencias

Con la base de R puedes preparar `EstudioServicio` y el controlador contra las interfaces acordadas. La ejecución completa requiere que se integren Erlang-C, `Simulador` y `VentanaPrincipal`. Si faltan, registra el bloqueo; no reemplaces las contribuciones de los demás con implementaciones propias.

## Tareas

- [ ] Sincronizar la base de R y crear `feature/d-integracion` desde `main` actualizado.
- [ ] Confirmar la entrega de `main.py` por R.
- [ ] Implementar `EstudioServicio(teorico, simulador)` con ambas estrategias recibidas por constructor.
- [ ] Implementar `ejecutar(configuracion)` para validar, buscar el mínimo teórico, seleccionar tres escenarios estables y evaluar ambos métodos.
- [ ] Construir `ResultadoEstudio` sin importar la vista ni el controlador desde el modelo.
- [ ] Implementar un único `Controlador(vista, estudio)` y vincular su método `ejecutar()` al botón de la vista.
- [ ] Leer y validar la configuración antes de lanzar el trabajo, mostrar errores legibles y prevenir ejecuciones simultáneas.
- [ ] Ejecutar el estudio fuera del hilo de Tkinter y recoger su resultado mediante `after()`; modificar widgets solo desde el hilo principal.
- [ ] Restaurar el estado de la interfaz tanto en éxito como ante excepciones; gestionar el cierre de ventana durante una ejecución sin actualizar widgets destruidos ni dejar un proceso bloqueado.
- [ ] Sincronizar las contribuciones de R, M y E y completar `main.py` con la construcción y conexión de objetos acordadas.
- [ ] Verificar desde `python main.py` que los parámetros iniciales producen tabla y gráfica con ambos métodos.
- [ ] Verificar el criterio del mínimo teórico, los tres escenarios estables y el tratamiento de resultados simulados no concluyentes.
- [ ] Verificar datos inválidos, varias ejecuciones consecutivas, estado ocupado y cierre de la ventana.
- [ ] Documentar instalación en entorno virtual, dependencia de Tcl/Tk, ejecución, unidades, supuestos y límites de la conclusión en `README.md`.
- [ ] Explicar en el README las responsabilidades MVC y cómo se utiliza Strategy, manteniendo los nombres finales del código.
- [ ] Registrar parámetros, resultados observados y limitaciones de la validación integrada, sin afirmar verificaciones no realizadas.
- [ ] Actualizar los hitos de `COORDINACION.md` solo cuando estén comprobados e integrados.
- [ ] Crear commits, abrir PR final y registrar la entrega al equipo.

Si detectas un error en un módulo ajeno, informa al responsable con el caso que lo reproduce. Coordina la corrección antes de editar su archivo. Si el equipo autoriza expresamente una corrección de integración, registra el cambio y su comprobación.

## Commits sugeridos

1. `feat(estudio): comparar teoria y simulacion`.
2. `feat(controlador): conectar ejecucion e interfaz`.
3. `feat(app): completar arranque e integracion`.
4. `docs: documentar ejecucion y validacion final`.

## Entrega final al equipo

- Estado: pendiente.
- Rama / commits: pendiente.
- PR: pendiente.
- PR de R, M y E integrados: pendiente.
- Pasos para instalar y ejecutar: pendiente.
- Configuración y resultados de la comprobación completa: pendiente.
- Incidencias pendientes o limitaciones: pendiente.
- Siguiente paso: revisión del equipo y uso de la versión integrada en `main`.

## Bloqueos o cambios de contrato

- Inicial: esperar la base de R; la comprobación completa también requiere las implementaciones de M y E.
