from manim import *
import sys
from pathlib import Path
import shutil
import numpy as np

# Agregar src/ al path
sys.path.insert(0, str(Path(__file__).parent))
from loader import SistemaDistribucion


class PanelE_EvolucionTemporal(Scene):
    def construct(self):
        # Configuración de fondo oscuro
        self.camera.background_color = "#1a1a1a"
        
        # ========================================
        # AUTO-PREPARACIÓN DE DATOS
        # ========================================
        self.preparar_datos_automaticamente()
        
        # ========================================
        # CARGAR DATOS REALES DESDE LOADER
        # ========================================
        try:
            sistema = SistemaDistribucion(
                path_eventos="data/eventos_procesamiento.yaml",
                path_config="config/configuracion.yaml"
            )
            
            # Obtener evolución temporal
            horas, entradas, salidas = sistema.calcular_evolucion_temporal()
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar datos: {e}")
            return
        
        # ========================================
        # VERIFICAR DATOS
        # ========================================
        if not horas or len(horas) == 0:
            self.mostrar_error("No hay eventos para mostrar evolución temporal")
            return
        
        # ========================================
        # TÍTULO DEL PANEL
        # ========================================
        titulo = Text("EVOLUCIÓN TEMPORAL", font_size=36, color=WHITE)
        subtitulo = Text("Ritmo Operativo • Pulsos y Acumulaciones", font_size=20, color=GRAY)
        titulo.to_edge(UP, buff=0.5)
        subtitulo.next_to(titulo, DOWN, buff=0.2)
        
        self.play(Write(titulo), Write(subtitulo))
        self.wait(0.5)
        
        # ========================================
        # EJES TEMPORALES
        # ========================================
        self.crear_ejes_temporales(horas)
        
        # ========================================
        # GRÁFICO DE FLUJOS
        # ========================================
        self.graficar_flujos(horas, entradas, salidas)
        
        self.wait(1)
        
        # ========================================
        # GRÁFICO DE ACUMULACIÓN NETA
        # ========================================
        self.graficar_acumulacion(horas, entradas, salidas)
        
        self.wait(1)
        
        # ========================================
        # MARCAR HORARIOS CRÍTICOS
        # ========================================
        self.marcar_horarios_criticos(horas, entradas, salidas)
        
        # ========================================
        # INDICADOR DE ESTADO
        # ========================================
        estado = Text(
            "SISTEMA VIVO • PATRÓN IDENTIFICABLE",
            font_size=18,
            color="#4A90E2",
            slant=ITALIC
        )
        estado.to_corner(DR, buff=0.5)
        self.play(FadeIn(estado, shift=UP*0.2))
        
        self.wait(3)
        
        # ========================================
        # FADE OUT FINAL
        # ========================================
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )
    
    def crear_ejes_temporales(self, horas):
        """Crea eje horizontal de tiempo"""
        
        # Eje horizontal (tiempo)
        eje_x = Line(LEFT * 6, RIGHT * 6, color=GRAY)
        eje_x.shift(DOWN * 0.5)
        
        # Marcas de hora
        marcas_hora = VGroup()
        num_horas = len(horas)
        
        for i, hora in enumerate(horas):
            x_pos = -6 + i * (12 / max(num_horas - 1, 1))
            marca = Line(UP * 0.1, DOWN * 0.1, color=GRAY)
            marca.move_to([x_pos, -0.5, 0])
            
            # Etiqueta solo para algunas horas (evitar saturación)
            if i % max(1, num_horas // 6) == 0 or i == num_horas - 1:
                label = Text(f"{int(hora)}:00", font_size=12, color=GRAY)
                label.next_to(marca, DOWN, buff=0.2)
                marcas_hora.add(marca, label)
            else:
                marcas_hora.add(marca)
        
        self.play(Create(eje_x), FadeIn(marcas_hora))
        self.eje_x = eje_x
        self.marcas_hora = marcas_hora
        self.num_horas = num_horas
    
    def graficar_flujos(self, horas, entradas, salidas):
        """Grafica líneas de entradas y salidas"""
        
        # Escalar datos
        max_valor = max(max(entradas) if entradas else 1, max(salidas) if salidas else 1)
        escala_y = 2.0 / max(max_valor, 1)
        
        # Crear puntos para entradas
        puntos_entradas = []
        for i, hora in enumerate(horas):
            x = -6 + i * (12 / max(self.num_horas - 1, 1))
            y = -0.5 + entradas[i] * escala_y
            puntos_entradas.append([x, y, 0])
        
        # Crear puntos para salidas
        puntos_salidas = []
        for i, hora in enumerate(horas):
            x = -6 + i * (12 / max(self.num_horas - 1, 1))
            y = -0.5 + salidas[i] * escala_y
            puntos_salidas.append([x, y, 0])
        
        # Línea de entradas (verde)
        linea_entradas = VMobject(color="#50C878", stroke_width=3)
        linea_entradas.set_points_as_corners(puntos_entradas)
        
        # Línea de salidas (rojo)
        linea_salidas = VMobject(color="#E74C3C", stroke_width=3)
        linea_salidas.set_points_as_corners(puntos_salidas)
        
        # Puntos destacados
        dots_entradas = VGroup(*[
            Dot(point=punto, color="#50C878", radius=0.06)
            for punto in puntos_entradas
        ])
        
        dots_salidas = VGroup(*[
            Dot(point=punto, color="#E74C3C", radius=0.06)
            for punto in puntos_salidas
        ])
        
        # Leyenda
        leyenda_entradas = VGroup(
            Line(LEFT * 0.3, RIGHT * 0.3, color="#50C878", stroke_width=3),
            Text("ENTRADAS", font_size=14, color="#50C878")
        ).arrange(RIGHT, buff=0.2)
        leyenda_entradas.to_corner(UL, buff=0.8).shift(DOWN * 1.5)
        
        leyenda_salidas = VGroup(
            Line(LEFT * 0.3, RIGHT * 0.3, color="#E74C3C", stroke_width=3),
            Text("SALIDAS", font_size=14, color="#E74C3C")
        ).arrange(RIGHT, buff=0.2)
        leyenda_salidas.next_to(leyenda_entradas, DOWN, buff=0.2, aligned_edge=LEFT)
        
        # Animaciones
        self.play(
            Create(linea_entradas),
            LaggedStart(*[GrowFromCenter(dot) for dot in dots_entradas], lag_ratio=0.05),
            run_time=1.5
        )
        self.play(FadeIn(leyenda_entradas))
        
        self.play(
            Create(linea_salidas),
            LaggedStart(*[GrowFromCenter(dot) for dot in dots_salidas], lag_ratio=0.05),
            run_time=1.5
        )
        self.play(FadeIn(leyenda_salidas))
        
        self.linea_entradas = linea_entradas
        self.linea_salidas = linea_salidas
        self.puntos_entradas = puntos_entradas
        self.puntos_salidas = puntos_salidas
    
    def graficar_acumulacion(self, horas, entradas, salidas):
        """Grafica acumulación neta a lo largo del tiempo"""
        
        # Calcular acumulación neta
        acumulacion = [0]
        for i in range(len(entradas)):
            acumulacion.append(acumulacion[-1] + entradas[i] - salidas[i])
        
        # Escalar
        max_abs = max(abs(min(acumulacion)), abs(max(acumulacion)))
        escala_y = 1.5 / max(max_abs, 1)
        
        # Crear puntos
        puntos_acum = []
        horas_extendidas = [horas[0] - 1] + list(horas) if horas else [0]
        
        for i, hora in enumerate(horas_extendidas):
            if i < len(horas_extendidas):
                x = -6 + i * (12 / max(self.num_horas, 1))
            else:
                x = 6
            y = -2.8 + acumulacion[i] * escala_y
            puntos_acum.append([x, y, 0])
        
        # Línea base (cero)
        linea_cero = DashedLine(LEFT * 6, RIGHT * 6, color=GRAY, stroke_width=1.5)
        linea_cero.move_to([0, -2.8, 0])
        
        # Área bajo/sobre la curva
        area_acum = VMobject(fill_color="#4A90E2", fill_opacity=0.3, stroke_width=0)
        puntos_area = puntos_acum + [[6, -2.8, 0], [-6, -2.8, 0]]
        area_acum.set_points_as_corners(puntos_area)
        
        # Línea de acumulación
        linea_acum = VMobject(color="#4A90E2", stroke_width=4)
        linea_acum.set_points_as_corners(puntos_acum)
        
        # Etiqueta
        label_acum = Text("ACUMULACIÓN NETA", font_size=14, color="#4A90E2", weight=BOLD)
        label_acum.move_to([0, -2.2, 0])
        
        # Animaciones
        self.play(Create(linea_cero))
        self.play(FadeIn(label_acum))
        self.play(DrawBorderThenFill(area_acum), run_time=1.5)
        self.play(Create(linea_acum), run_time=1.5)
        
        self.linea_acum = linea_acum
        self.acumulacion = acumulacion
    
    def marcar_horarios_criticos(self, horas, entradas, salidas):
        """Identifica y marca horarios pico"""
        
        if not entradas or not salidas:
            return
        
        # Identificar hora pico de entradas
        max_entrada = max(entradas)
        max_entrada_idx = entradas.index(max_entrada)
        x_max_entrada = -6 + max_entrada_idx * (12 / max(self.num_horas - 1, 1))
        y_max_entrada = self.puntos_entradas[max_entrada_idx][1]
        
        # Identificar hora pico de salidas
        max_salida = max(salidas)
        max_salida_idx = salidas.index(max_salida)
        x_max_salida = -6 + max_salida_idx * (12 / max(self.num_horas - 1, 1))
        y_max_salida = self.puntos_salidas[max_salida_idx][1]
        
        # Marcador pico entradas
        marcador_entrada = VGroup(
            Circle(radius=0.15, color="#50C878", stroke_width=3, fill_opacity=0),
            Text("PICO", font_size=10, color="#50C878", weight=BOLD)
        )
        marcador_entrada[1].next_to(marcador_entrada[0], UP, buff=0.1)
        marcador_entrada.move_to([x_max_entrada, y_max_entrada, 0])
        
        # Marcador pico salidas
        marcador_salida = VGroup(
            Circle(radius=0.15, color="#E74C3C", stroke_width=3, fill_opacity=0),
            Text("PICO", font_size=10, color="#E74C3C", weight=BOLD)
        )
        marcador_salida[1].next_to(marcador_salida[0], UP, buff=0.1)
        marcador_salida.move_to([x_max_salida, y_max_salida, 0])
        
        self.play(
            GrowFromCenter(marcador_entrada),
            GrowFromCenter(marcador_salida),
            run_time=0.8
        )
        
        # Texto de observación
        observacion = Text(
            f"Pico entradas: {int(horas[max_entrada_idx])}:00 ({entradas[max_entrada_idx]} eventos)",
            font_size=12,
            color=GRAY
        )
        observacion.to_edge(DOWN, buff=0.8)
        
        self.play(FadeIn(observacion, shift=UP * 0.2))
    
    def preparar_datos_automaticamente(self):
        """Auto-prepara datos si eventos_procesamiento.yaml no existe"""
        ruta_eventos = Path("data/eventos.yaml")
        ruta_procesamiento = Path("data/eventos_procesamiento.yaml")
        
        if not ruta_procesamiento.exists():
            if ruta_eventos.exists():
                print("⚙️  Auto-preparando datos...")
                shutil.copy2(ruta_eventos, ruta_procesamiento)
                print(f"✓ Copiado {ruta_eventos} → {ruta_procesamiento}")
            else:
                print(f"⚠️  Advertencia: No se encontró {ruta_eventos}")
    
    def mostrar_error(self, mensaje: str):
        """Muestra mensaje de error si falla la carga de datos"""
        error_text = Text(
            f"ERROR: {mensaje}",
            font_size=24,
            color=RED
        )
        self.play(Write(error_text))
        self.wait(3)
