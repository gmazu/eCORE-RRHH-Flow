from manim import *
import sys
from pathlib import Path
import shutil

# Agregar src/ al path
sys.path.insert(0, str(Path(__file__).parent))
from loader import SistemaDistribucion


class PanelB_DistribucionObservada(Scene):
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
            
            distribucion_observada = sistema.calcular_distribucion_observada("2025-01-10T10:00:00")
            colores_zonas = sistema.config.get('colores_zonas', {})
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar datos: {e}")
            return
        
        # ========================================
        # PREPARAR DATOS PARA VISUALIZACIÓN
        # ========================================
        zonas_data = []
        colores_default = ["#4A90E2", "#50C878", "#9B59B6", "#E67E22", "#E74C3C", "#F39C12"]
        
        for i, (zona_nombre, cantidad) in enumerate(distribucion_observada.items()):
            color = colores_zonas.get(zona_nombre, colores_default[i % len(colores_default)])
            
            zonas_data.append({
                "nombre": zona_nombre,
                "personas": cantidad,
                "color": color
            })
        
        if not zonas_data:
            self.mostrar_error("No hay zonas con eventos observados")
            return
        
        # ========================================
        # TÍTULO DEL PANEL
        # ========================================
        titulo = Text("DISTRIBUCIÓN OBSERVADA", font_size=36, color=WHITE)
        subtitulo = Text("Estado Real del Sistema", font_size=20, color=GRAY)
        titulo.to_edge(UP, buff=0.5)
        subtitulo.next_to(titulo, DOWN, buff=0.2)
        
        self.play(Write(titulo), Write(subtitulo))
        self.wait(0.5)
        
        # ========================================
        # TIMESTAMP ACTUAL
        # ========================================
        from datetime import datetime
        timestamp_actual = datetime.now().strftime("%H:%M:%S")
        self.timestamp = Text(timestamp_actual, font_size=20, color="#4A90E2", font="monospace")
        self.timestamp.to_corner(UL, buff=0.5).shift(DOWN*1.2)
        self.play(FadeIn(self.timestamp))
        
        # ========================================
        # CREAR BARRAS HORIZONTALES
        # ========================================
        barras_group = VGroup()
        labels_group = VGroup()
        valores_group = VGroup()
        
        max_personas = max([z["personas"] for z in zonas_data]) if zonas_data else 1
        bar_width_scale = 5.0
        bar_height = 0.5
        spacing = 0.9
        
        num_zonas = len(zonas_data)
        inicio_y = min(2.0, 1.5)
        
        self.barras_dict = {}
        self.valores_dict = {}
        
        for i, zona in enumerate(zonas_data):
            # Etiqueta de zona
            label = Text(zona["nombre"], font_size=24, color=WHITE)
            
            # Barra de personas
            width = (zona["personas"] / max_personas) * bar_width_scale if max_personas > 0 else 0.1
            barra = Rectangle(
                width=width,
                height=bar_height,
                fill_color=zona["color"],
                fill_opacity=0.7,
                stroke_color=zona["color"],
                stroke_width=2
            )
            
            # Valor numérico
            valor = Text(f"{zona['personas']}", font_size=28, color=WHITE, weight=BOLD)
            
            # Posicionamiento
            y_pos = inicio_y - i * spacing
            label.move_to([-5.5, y_pos, 0])
            barra.move_to([-2.5 + width/2, y_pos, 0])
            valor.next_to(barra, RIGHT, buff=0.3)
            
            barras_group.add(barra)
            labels_group.add(label)
            valores_group.add(valor)
            
            # Guardar referencias para actualización
            self.barras_dict[zona["nombre"]] = barra
            self.valores_dict[zona["nombre"]] = valor
        
        # ========================================
        # ANIMACIÓN DE ENTRADA
        # ========================================
        self.play(
            LaggedStart(*[FadeIn(label) for label in labels_group], lag_ratio=0.08)
        )
        self.play(
            LaggedStart(*[GrowFromEdge(barra, LEFT) for barra in barras_group], lag_ratio=0.12)
        )
        self.play(
            LaggedStart(*[FadeIn(valor) for valor in valores_group], lag_ratio=0.08)
        )
        
        # ========================================
        # TOTAL OBSERVADO
        # ========================================
        total_inicial = sum([z["personas"] for z in zonas_data])
        linea_separadora = Line(LEFT * 6, RIGHT * 6, color=GRAY).shift(DOWN * (inicio_y - num_zonas * spacing + 0.5))
        self.total_text = Text(f"TOTAL OBSERVADO: {total_inicial} personas", font_size=26, color=WHITE)
        self.total_text.next_to(linea_separadora, DOWN, buff=0.3)
        
        self.play(Create(linea_separadora))
        self.play(FadeIn(self.total_text))
        
        # ========================================
        # SIMULACIÓN DE CAMBIOS (opcional)
        # ========================================
        # Aquí podrías agregar lógica para mostrar cambios en tiempo real
        # Por ahora, solo mostramos el estado actual estático
        
        # ========================================
        # INDICADOR DE ESTADO
        # ========================================
        estado = Text("DATO OBJETIVO SIN INTERPRETACIÓN", font_size=18, color="#50C878", slant=ITALIC)
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
    
    def preparar_datos_automaticamente(self):
        """
        Auto-prepara datos si eventos_procesamiento.yaml no existe.
        """
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
