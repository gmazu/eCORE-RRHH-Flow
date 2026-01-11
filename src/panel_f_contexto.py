from manim import *
import sys
from pathlib import Path
import shutil

# Agregar src/ al path
sys.path.insert(0, str(Path(__file__).parent))
from loader import SistemaDistribucion


class PanelF_ContextoDecisiones(Scene):
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
            
            # Obtener indicadores
            indicadores = sistema.calcular_indicadores_contexto()
            
            # Obtener distribuciones para análisis
            definida = sistema.calcular_distribucion_definida()
            observada = sistema.calcular_distribucion_observada()
            recalculada = sistema.calcular_distribucion_recalculada()
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar datos: {e}")
            return
        
        # ========================================
        # VERIFICAR DATOS
        # ========================================
        if not indicadores:
            self.mostrar_error("No hay datos para calcular indicadores")
            return
        
        # ========================================
        # TÍTULO DEL PANEL
        # ========================================
        titulo = Text("CONTEXTO Y SOPORTE A DECISIONES", font_size=36, color=WHITE)
        subtitulo = Text("Indicadores Derivados • Optimización Operativa", font_size=20, color=GRAY)
        titulo.to_edge(UP, buff=0.5)
        subtitulo.next_to(titulo, DOWN, buff=0.2)
        
        self.play(Write(titulo), Write(subtitulo))
        self.wait(0.5)
        
        # ========================================
        # MOSTRAR INDICADORES EN CARDS
        # ========================================
        self.mostrar_indicadores_cards(indicadores)
        
        self.wait(1)
        
        # ========================================
        # ANÁLISIS DE DESVIACIONES
        # ========================================
        self.mostrar_desviaciones(definida, observada)
        
        self.wait(1)
        
        # ========================================
        # OPORTUNIDADES DE OPTIMIZACIÓN
        # ========================================
        self.mostrar_oportunidades(definida, observada, recalculada)
        
        # ========================================
        # TIMESTAMP DE ANÁLISIS
        # ========================================
        from datetime import datetime
        timestamp = Text(
            f"ANÁLISIS: {datetime.now().strftime('%H:%M:%S')}",
            font_size=16,
            color="#9B59B6",
            font="monospace"
        )
        timestamp.to_corner(UL, buff=0.5).shift(DOWN*1.2)
        self.play(FadeIn(timestamp))
        
        # ========================================
        # INDICADOR DE ESTADO
        # ========================================
        estado = Text(
            "ORIENTADO A EFICIENCIA • SIN VIGILANCIA",
            font_size=18,
            color="#9B59B6",
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
    
    def mostrar_indicadores_cards(self, indicadores):
        """Muestra indicadores en formato cards (2x3 grid)"""
        
        cards = VGroup()
        
        # Card 1: Cumplimiento Global
        card1 = self.crear_card(
            "CUMPLIMIENTO",
            f"{indicadores['cumplimiento']:.1f}%",
            "#50C878" if indicadores['cumplimiento'] >= 95 else "#F39C12"
        )
        
        # Card 2: Desviación Total
        card2 = self.crear_card(
            "DESVIACIÓN TOTAL",
            f"{indicadores['desviacion_total']} personas",
            "#4A90E2"
        )
        
        # Card 3: Zonas Críticas
        card3 = self.crear_card(
            "ZONAS CRÍTICAS",
            f"{indicadores['zonas_criticas']}",
            "#E74C3C" if indicadores['zonas_criticas'] > 2 else "#F39C12"
        )
        
        # Card 4: Sobredimensionadas
        card4 = self.crear_card(
            "SOBREDIMENSIONADAS",
            f"{indicadores['zonas_sobre']}",
            "#9B59B6"
        )
        
        # Card 5: Subatendidas
        card5 = self.crear_card(
            "SUBATENDIDAS",
            f"{indicadores['zonas_sub']}",
            "#E67E22"
        )
        
        # Card 6: Eficiencia
        card6 = self.crear_card(
            "EFICIENCIA DIST.",
            f"{indicadores['eficiencia_distribucion']}%",
            "#50C878" if indicadores['eficiencia_distribucion'] >= 80 else "#F39C12"
        )
        
        cards.add(card1, card2, card3, card4, card5, card6)
        
        # Organizar en grid
        cards.arrange_in_grid(rows=2, cols=3, buff=0.5)
        cards.shift(UP * 0.3)
        
        # Animar entrada
        self.play(
            LaggedStart(*[FadeIn(card, scale=0.8) for card in cards], lag_ratio=0.1),
            run_time=2
        )
        
        self.cards = cards
    
    def crear_card(self, titulo, valor, color):
        """Crea una card individual con indicador"""
        
        # Rectángulo de card
        ancho = 3.5
        alto = 1.2
        
        rect = Rectangle(
            width=ancho,
            height=alto,
            fill_color=color,
            fill_opacity=0.15,
            stroke_color=color,
            stroke_width=2
        )
        
        # Título
        texto_titulo = Text(titulo, font_size=14, color=GRAY, weight=BOLD)
        texto_titulo.move_to(rect.get_center() + UP * 0.3)
        
        # Valor
        texto_valor = Text(valor, font_size=24, color=color, weight=BOLD)
        texto_valor.move_to(rect.get_center() + DOWN * 0.15)
        
        return VGroup(rect, texto_titulo, texto_valor)
    
    def mostrar_desviaciones(self, definida, observada):
        """Muestra análisis de desviaciones por zona"""
        
        # Panel de análisis
        panel_y = -1.8
        
        titulo_panel = Text(
            "ANÁLISIS DE DESVIACIONES",
            font_size=18,
            color=WHITE,
            weight=BOLD
        )
        titulo_panel.move_to([0, panel_y, 0])
        
        self.play(FadeIn(titulo_panel))
        
        # Calcular desviaciones
        desviaciones_data = []
        
        for zona in definida.keys():
            plan = definida.get(zona, 0)
            obs = observada.get(zona, 0)
            
            if plan == 0:
                continue
            
            porcentaje_desv = ((obs - plan) / plan) * 100
            
            # Clasificar
            if abs(porcentaje_desv) > 20:
                if porcentaje_desv > 0:
                    estado = "SOBREDIMENSIONADA"
                    color = "#9B59B6"
                else:
                    estado = "DÉFICIT"
                    color = "#E74C3C"
                
                desviaciones_data.append((
                    zona,
                    f"{porcentaje_desv:+.1f}%",
                    estado,
                    color
                ))
        
        # Mostrar solo top 3 desviaciones
        desviaciones_data = sorted(
            desviaciones_data,
            key=lambda x: abs(float(x[1].replace('%', '').replace('+', ''))),
            reverse=True
        )[:3]
        
        # Crear tabla
        tabla = VGroup()
        
        for i, (zona, porcentaje, estado, color) in enumerate(desviaciones_data):
            fila = VGroup(
                Text(zona, font_size=12, color=WHITE),
                Text(porcentaje, font_size=12, color=color, weight=BOLD),
                Text(estado, font_size=11, color=color)
            ).arrange(RIGHT, buff=0.5)
            fila.move_to([0, panel_y - 0.35 - i*0.25, 0])
            tabla.add(fila)
        
        if len(tabla) > 0:
            self.play(
                LaggedStart(*[FadeIn(fila, shift=RIGHT*0.2) for fila in tabla], lag_ratio=0.15),
                run_time=1.5
            )
        else:
            sin_desv = Text("Sin desviaciones críticas", font_size=12, color=GRAY, slant=ITALIC)
            sin_desv.move_to([0, panel_y - 0.35, 0])
            self.play(FadeIn(sin_desv))
        
        self.tabla_desviaciones = tabla
    
    def mostrar_oportunidades(self, definida, observada, recalculada):
        """Muestra oportunidades de optimización"""
        
        # Panel de oportunidades
        panel_y = -3.2
        
        titulo_oport = Text(
            "OPORTUNIDADES DE OPTIMIZACIÓN",
            font_size=16,
            color="#F39C12",
            weight=BOLD
        )
        titulo_oport.move_to([0, panel_y, 0])
        
        self.play(FadeIn(titulo_oport))
        
        # Generar oportunidades
        oportunidades = []
        
        for zona in definida.keys():
            plan = definida.get(zona, 0)
            obs = observada.get(zona, 0)
            recalc = recalculada.get(zona, 0)
            
            if plan == 0:
                continue
            
            # Redistribución
            if recalc != obs:
                delta = recalc - obs
                if delta > 0:
                    oportunidades.append(f"• Reforzar {zona} con {delta} personas")
                else:
                    oportunidades.append(f"• Liberar {abs(delta)} personas de {zona}")
            
            # Sobredemanda recurrente
            if obs > plan * 1.5:
                oportunidades.append(f"• Evaluar automatización en {zona}")
        
        # Limitar a 3 oportunidades
        oportunidades = oportunidades[:3]
        
        # Mostrar oportunidades
        oport_group = VGroup()
        
        for i, texto in enumerate(oportunidades):
            oport_text = Text(texto, font_size=11, color=WHITE)
            oport_text.move_to([0, panel_y - 0.3 - i*0.22, 0])
            oport_group.add(oport_text)
        
        if len(oport_group) > 0:
            self.play(
                LaggedStart(*[FadeIn(oport, shift=RIGHT*0.3) for oport in oport_group], lag_ratio=0.2),
                run_time=1.5
            )
            
            # Botón de acción simulado
            boton = VGroup(
                Rectangle(
                    width=3,
                    height=0.4,
                    fill_color="#F39C12",
                    fill_opacity=0.3,
                    stroke_color="#F39C12",
                    stroke_width=2
                ),
                Text("GENERAR PLAN DE AJUSTE", font_size=11, color="#F39C12", weight=BOLD)
            )
            boton[1].move_to(boton[0].get_center())
            boton.next_to(oport_group, DOWN, buff=0.3)
            
            self.play(FadeIn(boton, scale=0.95))
        else:
            sin_oport = Text("Sistema en balance óptimo", font_size=12, color=GRAY, slant=ITALIC)
            sin_oport.move_to([0, panel_y - 0.3, 0])
            self.play(FadeIn(sin_oport))
    
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
