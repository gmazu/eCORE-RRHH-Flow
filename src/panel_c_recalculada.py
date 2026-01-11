from manim import *
import sys
from pathlib import Path
import shutil

# Agregar src/ al path
sys.path.insert(0, str(Path(__file__).parent))
from loader import SistemaDistribucion


class PanelC_DistribucionRecalculada(Scene):
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
            
            # Obtener las tres distribuciones
            definida = sistema.calcular_distribucion_definida()
            observada = sistema.calcular_distribucion_observada()
            recalculada = sistema.calcular_distribucion_recalculada()
            colores_zonas = sistema.config.get('colores_zonas', {})
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar datos: {e}")
            return
        
        # ========================================
        # VERIFICAR DATOS
        # ========================================
        if not definida or not observada or not recalculada:
            self.mostrar_error("No hay datos suficientes para recalcular")
            return
        
        # ========================================
        # TÍTULO DEL PANEL
        # ========================================
        titulo = Text("DISTRIBUCIÓN RECALCULADA", font_size=36, color=WHITE)
        subtitulo = Text("Ajuste Operativo Sugerido", font_size=20, color=GRAY)
        titulo.to_edge(UP, buff=0.5)
        subtitulo.next_to(titulo, DOWN, buff=0.2)
        
        self.play(Write(titulo), Write(subtitulo))
        self.wait(0.5)
        
        # ========================================
        # PREPARAR DATOS PARA VISUALIZACIÓN
        # ========================================
        zonas_nombres = list(definida.keys())
        colores_default = ["#4A90E2", "#50C878", "#9B59B6", "#E67E22", "#E74C3C", "#F39C12"]
        
        colores = []
        for i, zona in enumerate(zonas_nombres):
            color = colores_zonas.get(zona, colores_default[i % len(colores_default)])
            colores.append(color)
        
        # Convertir a listas ordenadas
        definida_vals = [definida.get(z, 0) for z in zonas_nombres]
        observada_vals = [observada.get(z, 0) for z in zonas_nombres]
        recalculada_vals = [recalculada.get(z, 0) for z in zonas_nombres]
        
        # ========================================
        # CREAR VISUALIZACIÓN COMPARATIVA
        # ========================================
        self.crear_visualizacion_comparativa(
            zonas_nombres,
            definida_vals,
            observada_vals,
            recalculada_vals,
            colores
        )
        
        self.wait(2)
        
        # ========================================
        # MOSTRAR ACCIONES SUGERIDAS
        # ========================================
        self.mostrar_acciones_sugeridas(
            zonas_nombres,
            observada_vals,
            recalculada_vals,
            colores
        )
        
        self.wait(2)
        
        # ========================================
        # TIMESTAMP DE RECÁLCULO
        # ========================================
        from datetime import datetime
        timestamp_recalculo = Text(
            f"RECALCULO: {datetime.now().strftime('%H:%M:%S')}",
            font_size=18,
            color="#F39C12",
            font="monospace"
        )
        timestamp_recalculo.to_corner(UL, buff=0.5).shift(DOWN*1.2)
        self.play(FadeIn(timestamp_recalculo))
        
        # ========================================
        # INDICADOR DE ESTADO
        # ========================================
        estado = Text(
            "OPTIMIZACIÓN DINÁMICA • NO ES ORDEN",
            font_size=18,
            color="#F39C12",
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
    
    def crear_visualizacion_comparativa(self, zonas, definida, observada, recalculada, colores):
        """Crea visualización con tres columnas comparativas"""
        
        # Headers de columnas
        header_y = 2.2
        h1 = Text("DEFINIDA", font_size=16, color=GRAY)
        h2 = Text("OBSERVADA", font_size=16, color=GRAY)
        h3 = Text("RECALCULADA", font_size=16, color="#F39C12", weight=BOLD)
        
        h1.move_to([-3.5, header_y, 0])
        h2.move_to([0, header_y, 0])
        h3.move_to([3.5, header_y, 0])
        
        self.play(FadeIn(h1), FadeIn(h2), FadeIn(h3))
        
        # Crear filas por zona
        spacing = 0.75
        inicio_y = 1.5
        
        all_elements = VGroup()
        
        for i, zona in enumerate(zonas):
            y_pos = inicio_y - i * spacing
            
            # Etiqueta de zona
            label = Text(zona, font_size=18, color=WHITE)
            label.move_to([-6, y_pos, 0])
            all_elements.add(label)
            
            # Valor definida
            v1 = self.crear_circulo_valor(definida[i], colores[i], 0.5)
            v1.move_to([-3.5, y_pos, 0])
            all_elements.add(v1)
            
            # Valor observada
            v2 = self.crear_circulo_valor(observada[i], colores[i], 0.6)
            v2.move_to([0, y_pos, 0])
            all_elements.add(v2)
            
            # Valor recalculada (destacada)
            v3 = self.crear_circulo_valor(recalculada[i], colores[i], 0.8, destacar=True)
            v3.move_to([3.5, y_pos, 0])
            all_elements.add(v3)
            
            # Flecha de ajuste si hay cambio
            if recalculada[i] != observada[i]:
                delta = recalculada[i] - observada[i]
                flecha = self.crear_indicador_cambio(delta, [2, y_pos, 0])
                all_elements.add(flecha)
        
        # Animar entrada
        self.play(
            LaggedStart(*[FadeIn(elem) for elem in all_elements], lag_ratio=0.05),
            run_time=2
        )
    
    def crear_circulo_valor(self, valor, color, opacidad, destacar=False):
        """Crea círculo con valor numérico"""
        radio = 0.28
        circulo = Circle(
            radius=radio,
            fill_color=color,
            fill_opacity=opacidad,
            stroke_color=color if not destacar else "#F39C12",
            stroke_width=3 if destacar else 2
        )
        
        if destacar:
            texto = Text(
                str(valor),
                font_size=20,
                color=WHITE,
                weight=BOLD
            )
        else:
            texto = Text(
                str(valor),
                font_size=20,
                color=WHITE
            )
        texto.move_to(circulo.get_center())
        
        return VGroup(circulo, texto)
    
    def crear_indicador_cambio(self, delta, posicion):
        """Crea indicador visual de cambio (↑↓)"""
        if delta > 0:
            simbolo = "↑"
            color = "#50C878"
            texto = f"+{delta}"
        else:
            simbolo = "↓"
            color = "#E74C3C"
            texto = f"{delta}"
        
        grupo = VGroup(
            Text(simbolo, font_size=20, color=color),
            Text(texto, font_size=14, color=color)
        ).arrange(RIGHT, buff=0.1)
        
        grupo.move_to(posicion)
        return grupo
    
    def mostrar_acciones_sugeridas(self, zonas, observada, recalculada, colores):
        """Muestra panel con acciones operativas sugeridas"""
        
        # Identificar acciones
        acciones = []
        for i, zona in enumerate(zonas):
            delta = recalculada[i] - observada[i]
            if delta > 0:
                acciones.append(f"{zona}: REFORZAR +{delta}")
            elif delta < 0:
                acciones.append(f"{zona}: LIBERAR {delta}")
        
        if not acciones:
            return
        
        # Panel de acciones
        panel_y = -2.3
        titulo_acciones = Text(
            "ACCIONES SUGERIDAS",
            font_size=18,
            color="#F39C12",
            weight=BOLD
        )
        titulo_acciones.move_to([0, panel_y, 0])
        
        self.play(FadeIn(titulo_acciones))
        
        # Listar acciones (máximo 3)
        acciones_text = VGroup()
        for j, accion in enumerate(acciones[:3]):
            texto = Text(accion, font_size=14, color=WHITE)
            texto.move_to([0, panel_y - 0.4 - j*0.3, 0])
            acciones_text.add(texto)
        
        self.play(
            LaggedStart(
                *[FadeIn(t, shift=RIGHT*0.3) for t in acciones_text],
                lag_ratio=0.15
            )
        )
    
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
