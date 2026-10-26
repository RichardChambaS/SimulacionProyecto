# E — Interfaz gráfica y gráficas

## Mensaje para tu agente

> Soy E. Lee `COORDINACION.md` y `docs/Emilio.md` completos. Comprueba que la base de R esté integrada y sincroniza mi rama. Implementa únicamente la vista, las gráficas y `requirements.txt`. No calcules teoría ni simulación en la interfaz y respeta los métodos públicos acordados con D. No crees tests ni inicies otros agentes. Haz commits por avances coherentes, marca con `[x]` las tareas completadas y comprobadas y registra cómo se verificó la interfaz y qué necesita D para conectarla. Conserva los cambios y archivos de los demás.

## Responsabilidad

Construir una ventana clara con Tkinter/ttk y gráficas integradas de Matplotlib. La vista muestra los resultados recibidos; el controlador decide qué ejecutar.

Archivos propios: `app/vista/__init__.py`, `app/vista/ventana_principal.py`, `app/vista/graficos.py`, `requirements.txt` y este documento.

## Dependencias

Necesitas la configuración y las dataclasses de R. Puedes trabajar antes de que la simulación y el controlador estén completos. Para comprobar la vista aisladamente puedes construir datos de ejemplo temporales; no dejar resultados ficticios conectados al flujo final de la aplicación.

## Tareas

- [ ] Sincronizar la base de R y crear `feature/e-interfaz` desde `main` actualizado.
- [ ] Implementar `VentanaPrincipal` como subclase de `tkinter.Tk` con la interfaz pública de `COORDINACION.md`.
- [ ] Crear campos con valores iniciales para demanda, atención, meta, umbral, duración, calentamiento, repeticiones y semilla.
- [ ] Mostrar claramente las unidades; representar la meta como porcentaje en pantalla y convertirla a proporción al crear `Configuracion`.
- [ ] Implementar `obtener_configuracion()` con conversión numérica y mensajes legibles ante texto inválido.
- [ ] Implementar `vincular_ejecucion(callback)` para que D conecte el botón sin que la vista conozca el controlador.
- [ ] Implementar `establecer_ocupado(ocupado)` para deshabilitar el botón durante el cálculo y mostrar progreso indeterminado.
- [ ] Implementar `mostrar_error(mensaje)` y `iniciar()`.
- [ ] Crear una tabla con agentes, utilización teórica y simulada, servicio teórico y simulado, intervalo del 95 % y espera media teórica y simulada.
- [ ] Mostrar el mínimo teórico y el estado estadístico de cada escenario según las reglas comunes; nunca presentar una ejecución aleatoria como prueba de un mínimo absoluto.
- [ ] Integrar una gráfica del servicio frente al número de agentes, con ambas series, intervalos para la simulación y línea de la meta.
- [ ] Actualizar tabla y gráfica al repetir una ejecución sin acumular widgets o figuras anteriores.
- [ ] Añadir Matplotlib a `requirements.txt`; no añadir `tkinter` como paquete de pip. Registrar en la entrega la versión con la que se comprobó.
- [ ] Comprobar manualmente la apertura, conversión de unidades, entradas inválidas, redimensionado y actualización de resultados con datos temporales.
- [ ] Comprobar con D que la ventana permanece operativa durante la simulación y que el botón vuelve a habilitarse si ocurre un error.
- [ ] Crear commits, abrir PR y documentar la entrega a D.

Toda modificación de widgets ocurre en el hilo de la interfaz. La ejecución en segundo plano y la consulta de su resultado corresponden a D; no añadir otro hilo de simulación en la vista.

## Commits sugeridos

1. `feat(vista): crear formulario y tabla`.
2. `feat(vista): integrar graficas y estados`.

## Entrega a D

- Estado: pendiente.
- Rama / commits: pendiente.
- PR: pendiente.
- Versiones y forma de abrir la vista para comprobarla: pendiente.
- Acciones de comprobación y resultados observados: pendiente.
- Limitaciones de presentación pendientes: pendiente.
- Siguiente paso: D debe crear la ventana desde `main.py`, vincular el controlador y comprobar el flujo completo.

## Bloqueos o cambios de contrato

- Inicial: esperar a que R integre configuración y resultados en `main`.
