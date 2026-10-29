"""Validaciones del modelo, los campos de Tkinter y el inicio del estudio.

Ejecutar desde la raíz del proyecto con:
    python -m unittest discover -s tests -v
"""

from dataclasses import replace
from decimal import Decimal
from math import inf, nan
import tkinter as tk
import unittest

from app.controlador.controlador import Controlador
from app.modelo.configuracion import Configuracion
from app.modelo.erlang_c import ErlangC
from app.modelo.estudio import validar_agentes
from app.modelo.simulacion import Simulador
from app.planificacion import estimar_trabajo
from app.vista.ventana_principal import VentanaPrincipal, leer_entero


class ValidacionesModelo(unittest.TestCase):
    def test_parametros_fuera_del_dominio(self):
        positivos = ("tasa_llegadas_hora", "atencion_media_minutos", "duracion_minutos")
        no_negativos = ("calentamiento_minutos", "umbral_segundos")
        for campo in positivos + no_negativos:
            invalidos = [-1, -0.1, nan, inf, -inf, True, "5", None]
            if campo in positivos:
                invalidos.append(0)
            for valor in invalidos:
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    replace(Configuracion(), **{campo: valor}).validar()

    def test_meta_es_proporcion_entre_cero_y_uno(self):
        for valor in [0, -0.1, 1, 1.01, nan, inf, True, "0.8"]:
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                replace(Configuracion(), meta_servicio=valor).validar()

    def test_campos_enteros(self):
        for campo, invalidos in {
            "repeticiones": [-1, 0, 1, 2.5, 30.0, True, nan, inf, "30"],
            "semilla": [-1, 0.5, 42.0, True, nan, inf, "42"],
        }.items():
            for valor in invalidos:
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    replace(Configuracion(), **{campo: valor}).validar()

    def test_ceros_permitidos_y_dos_repeticiones(self):
        cfg = replace(Configuracion(), calentamiento_minutos=0, umbral_segundos=0,
                      semilla=0, repeticiones=2)
        cfg.validar()
        self.assertEqual(estimar_trabajo(cfg).nivel, "normal")

    def test_tasas_derivadas_y_ventana_no_representables(self):
        for cambios in [
            {"tasa_llegadas_hora": 5e-324},
            {"atencion_media_minutos": 5e-324},
            {"tasa_llegadas_hora": 1e308, "atencion_media_minutos": 1e308},
            {"calentamiento_minutos": 1e308, "duracion_minutos": 1e308},
            {"calentamiento_minutos": 1e308, "duracion_minutos": 1},
        ]:
            with self.subTest(cambios=cambios), self.assertRaises(ValueError):
                replace(Configuracion(), **cambios).validar()

    def test_agentes_invalidos_en_teoria_simulacion_y_seleccion(self):
        cfg = Configuracion()  # Carga A = 3; se requiere c > 3.
        for agentes in [0, -1, -4, 2.5, 4.0, True, nan, inf, "6", None, 10**400, 3]:
            with self.subTest(agentes=agentes):
                for estrategia in [ErlangC(), Simulador()]:
                    with self.assertRaises(ValueError):
                        estrategia.evaluar(cfg, agentes)
                with self.assertRaises(ValueError):
                    validar_agentes(cfg, [agentes, 6, 8])
        for lista in [[], [4, 6], [4, 6, 8, 10], [4, 4, 6]]:
            with self.subTest(lista=lista), self.assertRaises(ValueError):
                validar_agentes(cfg, lista)
        self.assertEqual(validar_agentes(cfg, [8, 4, 6]), [4, 6, 8])

    def test_limites_de_trabajo(self):
        self.assertEqual(estimar_trabajo(Configuracion()).nivel, "normal")
        self.assertEqual(estimar_trabajo(replace(Configuracion(), tasa_llegadas_hora=20000)).nivel, "alto")
        self.assertEqual(estimar_trabajo(replace(Configuracion(), tasa_llegadas_hora=1200000)).nivel, "bloqueado")
        self.assertEqual(estimar_trabajo(Configuracion(), [1000001, 1000002, 1000003]).nivel, "bloqueado")
        # Enteros aceptados por el campo, pero imposibles de convertir a float.
        for repeticiones in [int(Decimal("9e308")), 10**400]:
            with self.subTest(digitos=len(str(repeticiones))):
                cfg = replace(Configuracion(), repeticiones=repeticiones)
                cfg.validar()
                self.assertEqual(estimar_trabajo(cfg).nivel, "bloqueado")

    def test_lectura_de_enteros_sin_truncamiento(self):
        for texto in ["", " ", "abc", "2.5", "2,5", "NaN", "sNaN", "inf", "-inf", "1e309"]:
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                leer_entero(texto, "Agentes")
        for texto, esperado in [("30.0", 30), ("30,0", 30), (" 42 ", 42),
                                ("9007199254740993", 9007199254740993)]:
            with self.subTest(texto=texto):
                self.assertEqual(leer_entero(texto, "Campo"), esperado)

    def test_repeticiones_extremas_con_llegadas_casi_nulas(self):
        # Pocos eventos esperados no hacen viable recorrer una cantidad
        # desmesurada de repeticiones ni representarla en la barra de avance.
        cfg = replace(Configuracion(), tasa_llegadas_hora=6e-309, repeticiones=10**308)
        cfg.validar()
        self.assertEqual(estimar_trabajo(cfg).nivel, "bloqueado")


class _EstudioEspia:
    def __init__(self):
        self.llamadas = 0

    def ejecutar(self, *args, **kwargs):
        self.llamadas += 1
        raise AssertionError("Una entrada inválida no debe iniciar el estudio")


class ValidacionesInterfaz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.vista = VentanaPrincipal()
        except tk.TclError as error:
            raise unittest.SkipTest(f"Tkinter necesita una pantalla disponible: {error}")
        cls.vista.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.vista.destroy()

    def setUp(self):
        self.vista._cargar_valores_iniciales()
        self.errores = []
        self.vista.mostrar_error = self.errores.append
        self.estudio = _EstudioEspia()
        self.controlador = Controlador(self.vista, self.estudio)

    def comprobar_rechazo(self):
        self.controlador.ejecutar()
        self.assertEqual(len(self.errores), 1, self.errores)
        self.assertTrue(self.errores[0].strip())
        self.assertFalse(self.controlador._ejecutando)
        self.assertEqual(self.estudio.llamadas, 0)
        self.errores.clear()

    def test_campos_invalidos_no_inician_el_estudio(self):
        for campo in self.vista._vars:
            for texto in ["", "abc", "NaN", "inf", "-inf", "-1", "1e999"]:
                with self.subTest(campo=campo, texto=texto):
                    self.vista._cargar_valores_iniciales()
                    self.vista._vars[campo].set(texto)
                    self.comprobar_rechazo()
        for campo, textos in {
            "lambda_minuto": ["0"], "atencion_media_minutos": ["0"],
            "duracion_minutos": ["0"], "meta_servicio_porcentaje": ["0", "100", "101"],
            "repeticiones": ["0", "1", "2.5", "9e308"], "semilla": ["1.5"],
        }.items():
            for texto in textos:
                with self.subTest(campo=campo, texto=texto):
                    self.vista._cargar_valores_iniciales()
                    self.vista._vars[campo].set(texto)
                    self.comprobar_rechazo()

    def test_agentes_manuales_invalidos_no_inician_el_estudio(self):
        for indice in range(3):
            for texto in ["0", "-1", "2.5", "", "abc", "NaN", "inf", "3", "9e308"]:
                with self.subTest(escenario=indice + 1, texto=texto):
                    self.vista._cargar_valores_iniciales()
                    self.vista._modo_agentes.set("manual")
                    self.vista._cambiar_modo()
                    self.vista._agentes_vars[indice].set(texto)
                    self.comprobar_rechazo()
        self.vista._cargar_valores_iniciales()
        self.vista._modo_agentes.set("manual")
        self.vista._agentes_vars[1].set("4")
        self.comprobar_rechazo()

    def test_limites_validos_y_coma_decimal(self):
        for campo, texto in [("calentamiento_minutos", "0"), ("semilla", "0"),
                             ("umbral_segundos", "0"), ("repeticiones", "2"),
                             ("lambda_minuto", "0,5"), ("atencion_media_minutos", "6,0")]:
            with self.subTest(campo=campo, texto=texto):
                self.vista._cargar_valores_iniciales()
                self.vista._vars[campo].set(texto)
                self.vista.obtener_configuracion().validar()

    def test_llegadas_minimas_no_eluden_el_limite_de_repeticiones(self):
        self.vista._vars["lambda_minuto"].set("1e-310")
        self.vista._vars["repeticiones"].set("1e308")
        self.comprobar_rechazo()


if __name__ == "__main__":
    unittest.main()
