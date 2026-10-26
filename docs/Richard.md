# R — Base del proyecto y Erlang-C

## Mensaje para tu agente

> Soy R. Lee `COORDINACION.md` y `docs/Richard.md` completos. Implementa únicamente mi parte y respeta los contratos y la propiedad de archivos. Primero comprueba la rama y el estado de Git; conserva cambios ajenos. No implementes toda la aplicación, no crees tests ni inicies otros agentes. Entrega la base de contratos antes de continuar la teoría para que M, E y D puedan trabajar. Haz commits por avances coherentes, marca con `[x]` las tareas completadas y comprobadas, y registra la entrega y los bloqueos. Si no existe remoto, prepara el trabajo local y deja la publicación pendiente hasta recibir la URL del equipo.

## Responsabilidad

Establecer la base compartida del modelo e implementar Erlang-C. Eres responsable de que los otros agentes conozcan los nombres, tipos y unidades de los datos.

Archivos propios: `.gitignore`, `app/__init__.py`, `app/modelo/__init__.py`, `app/modelo/configuracion.py`, `app/modelo/resultados.py`, `app/modelo/erlang_c.py` y este documento. Creas `main.py` mínimo en la base; después lo cedes a D y no lo modificas nuevamente.

## Dependencias y primera entrega

Puedes comenzar primero. La publicación requiere que el equipo comparta la URL del repositorio. Usa tu identidad Git; no configures identidades de M, E o D.

- [x] Publicar el commit inicial con los documentos de coordinación una vez disponible el repositorio.
- [x] Crear la rama `feature/r-base-erlang`.
- [x] Preparar `.gitignore` para entorno virtual, cachés de Python y archivos del editor.
- [x] Crear los paquetes base y `main.py` mínimo, sin importar módulos aún inexistentes.
- [x] Implementar `Configuracion`, sus validaciones y propiedades derivadas según `COORDINACION.md`.
- [x] Implementar las tres dataclasses de resultados acordadas.
- [x] Comprobar importaciones, conversiones de unidades y rechazo de entradas inválidas mediante ejecución manual.
- [ ] Integrar esta base en `main` con un PR temprano y registrar la entrega a M, E y D.
- [ ] Registrar que `main.py` queda a cargo de D a partir de esta entrega.

## Teoría

- [ ] Implementar `ErlangC.evaluar(configuracion, agentes)` sin dependencias de la interfaz.
- [ ] Calcular utilización, probabilidad de esperar, nivel de servicio y espera media con unidades consistentes.
- [ ] Usar un cálculo numéricamente estable, por ejemplo recurrencia de Erlang-B para obtener Erlang-C, evitando factoriales enormes.
- [ ] Rechazar escenarios sin estabilidad y valores de agentes inválidos.
- [ ] Implementar `buscar_minimo(configuracion)` desde el primer entero estable.
- [ ] Comprobar manualmente un caso conocido, el rechazo del caso inestable, el cumplimiento del candidato mínimo y el incumplimiento del anterior cuando sea estable.
- [ ] Verificar que la espera media es no negativa y que el nivel de servicio mejora al aumentar agentes manteniendo el resto fijo.
- [ ] Crear el PR de teoría y actualizar esta entrega.

Orientación matemática: con `lambda` y `mu` en minutos, `a = lambda / mu`, `rho = a / c`, `SL(t) = 1 - P(espera) * exp(-(c * mu - lambda) * t)` y `Wq = P(espera) / (c * mu - lambda)`. No confundir probabilidad de esperar con probabilidad de incumplir el umbral.

## Commits sugeridos

1. `docs: repartir trabajo y acordar contratos` — commit inicial de los documentos.
2. `feat(modelo): definir configuracion y contratos` — base que desbloquea al equipo.
3. `feat(teoria): implementar Erlang-C y busqueda minima`.

## Entrega al equipo

- Estado: base implementada y comprobada en la rama de Richard; integración y teoría pendientes.
- Rama: `feature/r-base-erlang`. Commits iniciales publicados: `8396097` (coordinación) y `7f04b71` (estructura). El hash de la base se registrará en la siguiente entrega.
- PR de base / PR de teoría: pendiente.
- Archivos de base terminados: `.gitignore`, `app/__init__.py`, `app/modelo/__init__.py`, `app/modelo/configuracion.py`, `app/modelo/resultados.py` y `main.py` mínimo.
- Comprobaciones manuales con Python 3.12.14: importaciones y dataclasses correctas; 30 llamadas/h = 0.5/min, servicio = 1/6 por minuto, carga = 3 erlangs y umbral = 1/3 de minuto. Se rechazaron 56 entradas inválidas con `ValueError`, incluidos texto, booleanos, NaN, infinitos, valores negativos y valores no representables. La ejecución de `main.py` informa que el arranque gráfico está pendiente. No se crearon archivos de tests.
- Siguiente paso: M, E y D deben sincronizar la base integrada antes de implementar sus partes.

## Bloqueos o cambios de contrato

- Repositorio disponible: https://github.com/RichardChambaS/SimulacionProyecto. No hay bloqueos técnicos. Requiere Python 3.10 o posterior; el comando global `python` de este equipo apunta a Python 2.7, por lo que las comprobaciones se ejecutaron con Python 3.12.14 del entorno de Codex.
