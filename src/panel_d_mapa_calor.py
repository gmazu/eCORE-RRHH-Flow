from manim import *
import sys
from pathlib import Path
import shutil
import numpy as np

# Agregar src/ al path
sys.path.insert(0, str(Path(__file__).parent))
from loader import SistemaDistribucion


class PanelD_MapaCalorFuncional(Scene):
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
                path_eventos="data",
                path_config="config/configuracion.yaml"
            )
            
            # Obtener datos
            definida = sistema.calcular_distribucion_definida()
            observada = sistema.calcular_distribucion_observada()
            mapa_calor = sistema.calcular_mapa_calor()
            colores_zonas = sistema.config.get('colores_zonas', {})
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar datos: {e}")
            return
        
        # ========================================
        # VERIFICAR DATOS
        # ========================================
        if not mapa_calor:
            self.mostrar_error("No hay datos para generar mapa de calor")
            return
        
        # ========================================
        # TÍTULO DEL PANEL
        # ========================================
        titulo = Text("MAPA DE CALOR FUNCIONAL", font_size=36, color=WHITE)
        subtitulo = Text("Ocupación Relativa por Zona", font_size=20, color=GRAY)
        titulo.to_edge(UP, buff=0.5)
        subtitulo.next_to(titulo, DOWN, buff=0.2)
        
        self.play(Write(titulo), Write(subtitulo))
        self.wait(0.5)
        
        # ========================================
        # PREPARAR DATOS PARA GRID
        # ========================================
        zonas_data = []
        for zona, proporcion in mapa_calor.items():
            zonas_data.append({
                "nombre": zona,
                "esperado": definida.get(zona, 0),
                "observado": observada.get(zona, 0),
                "proporcion": proporcion
            })
        
        # ========================================
        # CREAR GRID DE CALOR
        # ========================================
        self.crear_grid_calor(zonas_data)
        
        self.wait(1)
        
        # ========================================
        # CREAR LEYENDA DE COLORES
        # ========================================
        self.crear_leyenda_calor()
        
        self.wait(1)
        
        # ========================================
        # INDICADOR DE ESTADO
        # ========================================
        estado = Text(
            "LECTURA INMEDIATA • BALANCE OPERATIVO",
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
    
    def obtener_color_calor(self, proporcion):
        """
        Calcula color según proporción de ocupación:
        Verde: >= 90% (ocupación completa)
        Amarillo: 60-90% (ocupación parcial)
        Rojo: < 60% (déficit)
        """
        if proporcion >= 0.9:
            return "#50C878"  # Verde
        elif proporcion >= 0.6:
            # Interpolar entre amarillo y verde
            t = (proporcion - 0.6) / 0.3
            return self.interpolar_color("#F39C12", "#50C878", t)
        else:
            # Interpolar entre rojo y amarillo
            t = proporcion / 0.6
            return self.interpolar_color("#E74C3C", "#F39C12", t)
    
    def interpolar_color(self, color1, color2, t):
        """Interpolación lineal entre dos colores hex"""
        c1 = np.array([int(color1[i:i+2], 16) for i in (1, 3, 5)])
        c2 = np.array([int(color2[i:i+2], 16) for i in (1, 3, 5)])
        c = c1 + t * (c2 - c1)
        return "#" + "".join([f"{int(x):02x}" for x in c])
    
    def crear_grid_calor(self, zonas_data):
        """Crea grid de bloques tipo ecualizador"""
        
        # Configuración del grid
        num_zonas = len(zonas_data)
        
        # Determinar layout (2 filas x N columnas o ajustar dinámicamente)
        if num_zonas <= 4:
            filas = 1
            columnas = num_zonas
        elif num_zonas <= 8:
            filas = 2
            columnas = (num_zonas + 1) // 2
        else:
            filas = 3
            columnas = (num_zonas + 2) // 3
        
        bloque_ancho = 2.5
        bloque_alto = 1.8
        spacing_h = 0.3
        spacing_v = 0.4
        
        total_ancho = columnas * bloque_ancho + (columnas - 1) * spacing_h
        total_alto = filas * bloque_alto + (filas - 1) * spacing_v
        
        inicio_x = -total_ancho / 2 + bloque_ancho / 2
        inicio_y = total_alto / 2 - bloque_alto / 2 - 0.5
        
        self.bloques_dict = {}
        all_bloques = VGroup()
        
        for i, zona in enumerate(zonas_data):
            fila = i // columnas
            col = i % columnas
            
            x = inicio_x + col * (bloque_ancho + spacing_h)
            y = inicio_y - fila * (bloque_alto + spacing_v)
            
            # Crear bloque
            bloque = self.crear_bloque_zona(
                zona["nombre"],
                zona["proporcion"],
                zona["observado"],
                zona["esperado"],
                bloque_ancho,
                bloque_alto
            )
            bloque.move_to([x, y, 0])
            
            all_bloques.add(bloque)
            self.bloques_dict[zona["nombre"]] = bloque
        
        # Animación de entrada
        self.play(
            LaggedStart(
                *[FadeIn(bloque, scale=0.8) for bloque in all_bloques],
                lag_ratio=0.08
            ),
            run_time=2
        )
    
    def crear_bloque_zona(self, nombre, proporcion, observado, esperado, ancho, alto):
        """Crea bloque individual con color según proporción"""
        
        color = self.obtener_color_calor(proporcion)
        
        # Rectángulo base
        rect = Rectangle(
            width=ancho,
            height=alto,
            fill_color=color,
            fill_opacity=0.6,
            stroke_color=color,
            stroke_width=3
        )
        
        # Nombre de zona
        texto_nombre = Text(nombre, font_size=20, color=WHITE, weight=BOLD)
        texto_nombre.move_to(rect.get_center() + UP * 0.4)
        
        # Proporción en porcentaje
        porcentaje = int(proporcion * 100)
        texto_porcentaje = Text(
            f"{porcentaje}%",
            font_size=32,
            color=WHITE,
            weight=BOLD
        )
        texto_porcentaje.move_to(rect.get_center())
        
        # Valores observado/esperado
        texto_valores = Text(
            f"{observado}/{esperado}",
            font_size=16,
            color=GRAY
        )
        texto_valores.move_to(rect.get_center() + DOWN * 0.45)
        
        return VGroup(rect, texto_nombre, texto_porcentaje, texto_valores)
    
    def crear_leyenda_calor(self):
        """Crea leyenda de escala de colores"""
        
        # Leyenda en la parte inferior
        leyenda_y = -3.2
        
        titulo_leyenda = Text("NIVEL DE OCUPACIÓN", font_size=16, color=GRAY)
        titulo_leyenda.move_to([0, leyenda_y, 0])
        
        # Escala de colores
        escala_width = 6
        escala_height = 0.3
        segmentos = 20
        
        escala_group = VGroup()
        
        for i in range(segmentos):
            proporcion = i / (segmentos - 1)
            color = self.obtener_color_calor(proporcion)
            
            seg = Rectangle(
                width=escala_width / segmentos,
                height=escala_height,
                fill_color=color,
                fill_opacity=0.8,
                stroke_width=0
            )
            seg.move_to([
                -escala_width/2 + (i + 0.5) * escala_width/segmentos,
                leyenda_y - 0.4,
                0
            ])
            escala_group.add(seg)
        
        # Etiquetas de la escala
        etiq_deficit = Text("DÉFICIT", font_size=12, color="#E74C3C")
        etiq_deficit.next_to(escala_group, LEFT, buff=0.3)
        
        etiq_parcial = Text("PARCIAL", font_size=12, color="#F39C12")
        etiq_parcial.move_to([0, leyenda_y - 0.4, 0]).shift(DOWN * 0.5)
        
        etiq_completo = Text("COMPLETO", font_size=12, color="#50C878")
        etiq_completo.next_to(escala_group, RIGHT, buff=0.3)
        
        self.play(
            FadeIn(titulo_leyenda),
            LaggedStart(*[FadeIn(seg) for seg in escala_group], lag_ratio=0.02),
            FadeIn(etiq_deficit),
            FadeIn(etiq_parcial),
            FadeIn(etiq_completo),
            run_time=1.5
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
