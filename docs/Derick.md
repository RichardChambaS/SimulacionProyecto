# D — Estudio, controlador e integración final

## Revisión local actual

Desde el 2026-10-27, los escenarios confirmados del caso son 4, 6 y 8 agentes. La búsqueda del mínimo teórico sigue evaluando todos los enteros estables. Los escenarios 5, 6 y 7 mencionados más abajo pertenecen a comprobaciones anteriores.

El programa de esta copia fue corregido y ampliado el 2026-10-26. README.md y COORDINACION.md describen los contratos vigentes, las tres gráficas, la exportación por repetición, los intervalos t de Student, el progreso y la cancelación. Las entregas y comprobaciones anteriores de este documento se conservan como historial; sus descripciones de interfaces o estadística pueden corresponder a la versión anterior. Esta revisión corresponde a la actualización de main autorizada el 2026-10-27; las notas de entrega anteriores se conservan como historial.


## Mensaje para tu agente

> Soy D. Lee `COORDINACION.md` y `docs/Derick.md` completos. Implementa mi parte de estudio comparativo, controlador único e integración, respetando los contratos y la propiedad de archivos. No implementes por tu cuenta los módulos pendientes de R, M o E y no dupliques sus clases. No crees tests ni inicies otros agentes. Trabaja por commits, marca con `[x]` solo lo comprobado y registra dependencias y entrega final. Completa `main.py` solo después de la entrega explícita de R. Integra las partes disponibles, verifica el flujo completo y actualiza el README; conserva y coordina cualquier cambio ajeno.

## Responsabilidad

Conectar el cálculo teórico, la simulación y la interfaz. Mantener un solo controlador y presentar una conclusión fiel a la evidencia estadística.

Archivos propios: `app/modelo/estudio.py`, `app/controlador/__init__.py`, `app/controlador/controlador.py`, `README.md`, `COORDINACION.md` y este documento. `main.py` pasa a tu cargo después de que R entregue la base.

## Dependencias

Con la base de R puedes preparar `EstudioServicio` y el controlador contra las interfaces acordadas. La ejecución completa requiere que se integren Erlang-C, `Simulador` y `VentanaPrincipal`. Si faltan, registra el bloqueo; no reemplaces las contribuciones de los demás con implementaciones propias.

## Tareas

- [ ] Sincronizar la base de R y crear `feature/d-integracion` desde `main` actualizado.
- [x] Confirmar la entrega de `main.py` por R.
- [x] Implementar `EstudioServicio(teorico, simulador)` con ambas estrategias recibidas por constructor.
- [x] Implementar `ejecutar(configuracion)` para validar, buscar el mínimo teórico, seleccionar tres escenarios estables y evaluar ambos métodos.
- [x] Construir `ResultadoEstudio` sin importar la vista ni el controlador desde el modelo.
- [x] Implementar un único `Controlador(vista, estudio)` y vincular su método `ejecutar()` al botón de la vista.
- [x] Leer y validar la configuración antes de lanzar el trabajo, mostrar errores legibles y prevenir ejecuciones simultáneas.
- [x] Ejecutar el estudio fuera del hilo de Tkinter y recoger su resultado mediante `after()`; modificar widgets solo desde el hilo principal.
- [x] Restaurar el estado de la interfaz tanto en éxito como ante excepciones; gestionar el cierre de ventana durante una ejecución sin actualizar widgets destruidos ni dejar un proceso bloqueado.
- [x] Sincronizar las contribuciones de R, M y E y completar `main.py` con la construcción y conexión de objetos acordadas.
- [x] Verificar desde `python main.py` que los parámetros iniciales producen tabla y gráfica con ambos métodos.
- [x] Verificar el criterio del mínimo teórico, los tres escenarios estables y el tratamiento de resultados simulados no concluyentes.
- [x] Verificar datos inválidos, varias ejecuciones consecutivas, estado ocupado y cierre de la ventana.
- [x] Documentar instalación en entorno virtual, dependencia de Tcl/Tk, ejecución, unidades, supuestos y límites de la conclusión en `README.md`.
- [x] Explicar en el README las responsabilidades MVC y cómo se utiliza Strategy, manteniendo los nombres finales del código.
- [x] Registrar parámetros, resultados observados y limitaciones de la validación integrada, sin afirmar verificaciones no realizadas.
- [ ] Actualizar los hitos de `COORDINACION.md` solo cuando estén comprobados e integrados.
- [ ] Crear commits, abrir PR final y registrar la entrega al equipo.

Si detectas un error en un módulo ajeno, informa al responsable con el caso que lo reproduce. Coordina la corrección antes de editar su archivo. Si el equipo autoriza expresamente una corrección de integración, registra el cambio y su comprobación.

## Commits sugeridos

1. `feat(estudio): comparar teoria y simulacion`.
2. `feat(controlador): conectar ejecucion e interfaz`.
3. `feat(app): completar arranque e integracion`.
4. `docs: documentar ejecucion y validacion final`.

## Entrega final al equipo

- Estado: implementación local de D completa y verificada; pendiente de commit, publicación e integración. No se creó rama nueva, no se hizo commit y no se abrió PR porque esta continuación no recibió autorización explícita para publicar.
- Rama / commits: cambios sin confirmar sobre `main`, que ya contiene la base y la teoría de R, la simulación de M y la vista de E. El árbol de trabajo incluye `app/modelo/estudio.py`, `app/controlador/__init__.py`, `app/controlador/controlador.py`, `main.py`, `README.md`, `COORDINACION.md` y este documento.
- PR: no se abrió en esta continuación.
- PR de R, M y E integrados: la base y la teoría de R están integradas en `main`; la simulación de M figura integrada mediante `7e488e5`; la vista de E está en `c10feeb`. No se consultó el estado remoto de los PR desde este agente.
- Pasos para instalar y ejecutar: crear un entorno virtual, instalar `requirements.txt`, disponer de Tcl/Tk 8.6 y ejecutar `python main.py` desde la raíz. El detalle está en `README.md`.
- Configuración y resultados de la comprobación completa: 30 llamadas/h, atención media de 6 min, meta 80 %, umbral 20 s, 4800 min medidos tras 1000 min de calentamiento, 30 repeticiones y semilla 42. Mínimo teórico 6 agentes; escenarios 5, 6 y 7.
- Incidencias pendientes o limitaciones: no hay bloqueos de código. La conclusión simulada es estadística y no demuestra un mínimo absoluto; el escenario de 5 agentes queda no concluyente. La comprobación se hizo en Linux con Tcl/Tk 8.6; no se probó en Windows ni macOS.
- Siguiente paso: revisar los cambios, crear la rama de integración, confirmar los commits, abrir el PR final y actualizar el estado global de `COORDINACION.md` tras la integración.

## Evidencias de estudio y controlador (2026-10-26)

- `EstudioServicio.ejecutar` valida la configuración, reutiliza `buscar_minimo` de la estrategia teórica, selecciona tres escenarios estables y evalúa ambas estrategias para cada uno.
- Con la configuración inicial el mínimo teórico fue 6 y los escenarios `[5, 6, 7]`. Con una meta del 1 % el mínimo fue 4 y los escenarios `[4, 5, 6]`, porque el agente 3 no supera la carga de 3 erlangs.
- El estudio no importa la vista ni el controlador. `Controlador` es el único punto que conoce ambos lados.
- El botón se deshabilita durante el cálculo. Una segunda llamada a `Controlador.ejecutar()` mientras hay un estudio activo no lanzó otro hilo.
- Se rechazaron antes de iniciar el estudio un texto no numérico, una tasa negativa, una tasa cero y una meta fuera del rango permitido. Una excepción lanzada dentro del hilo de trabajo se mostró como error legible y el botón volvió a `normal` con el estado `Listo`.
- Cerrar la ventana durante un estudio de dos segundos terminó el bucle de Tkinter y el proceso sin esperar al hilo, que es demonio y no actualiza widgets destruidos.
- Dos ejecuciones consecutivas reemplazaron las tres filas de la tabla sin acumular resultados y volvieron a dibujar la gráfica.

## Evidencias de la integración gráfica (2026-10-26)

- Se ejecutó la aplicación real con `VentanaPrincipal`, `Controlador`, `EstudioServicio`, `ErlangC` y `Simulador` sobre Python 3.14.4, Tcl/Tk 8.6 y Matplotlib 3.11.2.
- Tras la ejecución inicial, la tabla mostró tres filas y la gráfica tres líneas (Erlang-C, simulación y meta) más la banda del intervalo simulado.
- El resumen mostró «Mínimo teórico: 6 agentes». El botón pasó de `disabled`/«Calculando...» a `normal`/«Listo».
- `timeout 3 python main.py` abrió la aplicación sin trazas de error y terminó por el timeout, como se esperaba al quedar el bucle de Tkinter activo.

| Agentes | Servicio teórico | Servicio simulado | IC 95 % aproximado | Lectura frente a 80 % |
| --- | --- | --- | --- | --- |
| 5 | 78.87 % | 79.77 % | [78.71 %, 80.82 %] | No concluyente |
| 6 | 91.61 % | 92.09 % | [91.50 %, 92.68 %] | Cumplimiento respaldado |
| 7 | 96.99 % | 97.22 % | [96.90 %, 97.55 %] | Cumplimiento respaldado |

Las comprobaciones se hicieron con código temporal por la entrada estándar de Python y con un entorno virtual temporal. No se añadieron tests ni scripts permanentes al repositorio.

## Bloqueos o cambios de contrato

- Sin bloqueos técnicos. La única limitación del entorno local fue que el `Pillow` del sistema no incluía `ImageTk`; se comprobó la interfaz con un entorno virtual que instaló `matplotlib`, `numpy` y `pillow`, como haría una instalación normal de las dependencias.
- No se modificó ningún archivo de R, M o E.
- Queda pendiente la creación de la rama y de los commits por la instrucción de no publicar sin autorización explícita.
