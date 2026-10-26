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
- [x] Integrar esta base en `main` con un PR temprano y registrar la entrega a M, E y D.
- [x] Registrar que `main.py` queda a cargo de D a partir de esta entrega.

## Teoría

- [x] Implementar `ErlangC.evaluar(configuracion, agentes)` sin dependencias de la interfaz.
- [x] Calcular utilización, probabilidad de esperar, nivel de servicio y espera media con unidades consistentes.
- [x] Usar un cálculo numéricamente estable, por ejemplo recurrencia de Erlang-B para obtener Erlang-C, evitando factoriales enormes.
- [x] Rechazar escenarios sin estabilidad y valores de agentes inválidos.
- [x] Implementar `buscar_minimo(configuracion)` desde el primer entero estable.
- [x] Comprobar manualmente un caso conocido, el rechazo del caso inestable, el cumplimiento del candidato mínimo y el incumplimiento del anterior cuando sea estable.
- [x] Verificar que la espera media es no negativa y que el nivel de servicio mejora al aumentar agentes manteniendo el resto fijo.
- [ ] Crear el PR de teoría y actualizar esta entrega.

Orientación matemática: con `lambda` y `mu` en minutos, `a = lambda / mu`, `rho = a / c`, `SL(t) = 1 - P(espera) * exp(-(c * mu - lambda) * t)` y `Wq = P(espera) / (c * mu - lambda)`. No confundir probabilidad de esperar con probabilidad de incumplir el umbral.

## Commits sugeridos

1. `docs: repartir trabajo y acordar contratos` — commit inicial de los documentos.
2. `feat(modelo): definir configuracion y contratos` — base que desbloquea al equipo.
3. `feat(teoria): implementar Erlang-C y busqueda minima`.

## Entrega al equipo

- Estado: base integrada en `main` mediante el PR #1; teoría implementada y comprobada, pendiente de publicar su PR.
- Rama: `feature/r-base-erlang`. Commits: `8396097` (coordinación), `7f04b71` (estructura), `3a4b546` (configuración y contratos); la base se integró en `35f1fe6`. El hash de teoría se registrará en la siguiente entrega.
- PR de base: https://github.com/RichardChambaS/SimulacionProyecto/pull/1 (integrado). PR de teoría: pendiente.
- Archivos de base terminados: `.gitignore`, `app/__init__.py`, `app/modelo/__init__.py`, `app/modelo/configuracion.py`, `app/modelo/resultados.py` y `main.py` mínimo.
- Comprobaciones manuales con Python 3.12.14: importaciones y dataclasses correctas; 30 llamadas/h = 0.5/min, servicio = 1/6 por minuto, carga = 3 erlangs y umbral = 1/3 de minuto. Se rechazaron 56 entradas inválidas con `ValueError`, incluidos texto, booleanos, NaN, infinitos, valores negativos y valores no representables. La ejecución de `main.py` informa que el arranque gráfico está pendiente. No se crearon archivos de tests.
- Entrega de `main.py`: desde la integración del PR #1 queda exclusivamente a cargo de Derick. Richard no lo volverá a modificar. M, E y D ya pueden sincronizar `main` e implementar sus partes contra los contratos publicados.

## Bloqueos o cambios de contrato

- Repositorio disponible: https://github.com/RichardChambaS/SimulacionProyecto. No hay bloqueos técnicos. Requiere Python 3.10 o posterior; el comando global `python` de este equipo apunta a Python 2.7, por lo que las comprobaciones se ejecutaron con Python 3.12.14 del entorno de Codex.

## Comprobación de la teoría (2026-10-26)

- Python 3.12.14, sin dependencias externas ni archivos de tests.
- 108 escenarios contrastados con la fórmula directa de estados de M/M/c usando `Decimal` con 80 dígitos; se compararon probabilidad de esperar, nivel de servicio y espera media. Cargas de 0.01 a 1000 erlangs, con 12 cantidades estables de agentes para cada carga.
- Caso M/M/1 independiente: 6 llamadas/h, atención media de 6 minutos, un agente; probabilidad de esperar 0.6 y espera media de 9 minutos.
- Búsqueda del mínimo comprobada en 15 combinaciones de meta (0.01, 0.5, 0.8, 0.99 y 0.999999) y umbral (0, 20 y 3600 segundos), incluyendo el incumplimiento del entero anterior cuando es estable.
- Diez entradas de agentes inválidas o inestables rechazadas con `ValueError`, incluidos booleanos, valores no enteros y enteros fuera del rango representable.
- Aumento del servicio y reducción de la espera al aumentar agentes verificados en los escenarios de comparación. Con umbral cero, el servicio es la probabilidad de atención inmediata.

| Agentes | Utilización | Probabilidad de esperar | Servicio en hasta 20 s | Espera media (min) |
| --- | --- | --- | --- | --- |
| 4 | 0.75 | 0.509433962 | 51.809612 % | 3.056603774 |
| 5 | 0.60 | 0.236151603 | 78.868226 % | 0.708454810 |
| 6 | 0.50 | 0.099143207 | 91.607709 % | 0.198286414 |
| 7 | 0.428571429 | 0.037645236 | 96.985605 % | 0.056467854 |

Resultado inicial: mínimo teórico de **6 agentes**. Este resultado pertenece al modelo estacionario; la comparación con simulación sigue pendiente de Martina y Derick.

Para comprobar las conversiones y el resultado desde una consola con Python 3.10 o posterior:

```python
from app.modelo.configuracion import Configuracion
from app.modelo.erlang_c import ErlangC

configuracion = Configuracion()
configuracion.validar()
modelo = ErlangC()
print(modelo.buscar_minimo(configuracion))  # 6
print(modelo.evaluar(configuracion, 5))
print(modelo.evaluar(configuracion, 6))
```

Referencia conceptual de Erlang-C y de la estabilidad M/M/c: [NPTEL, Basics of Queueing](https://archive.nptel.ac.in/content/storage2/courses/117103017/module3/lec2/1.html).