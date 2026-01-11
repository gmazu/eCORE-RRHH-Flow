import yaml
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

class SistemaDistribucion:
    """
    Carga eventos y configuración desde YAML.
    Calcula distribuciones: definida, observada, recalculada.
    Alimenta los 6 paneles Manim.
    """
    
    def __init__(self, path_eventos: str, path_config: str):
        self.path_eventos = path_eventos
        self.path_config = path_config
        
        # Cargar archivos
        self.config = self._cargar_yaml(path_config)
        self.eventos = self._cargar_yaml(path_eventos)['eventos']
        
        # Procesar datos
        self.zonas = self.config['zonas_funcionales']
        self.mapeo_puertas = self.config['mapeo_puertas']
        self.asignaciones = self.config['asignacion_tarjetas']
        self.reglas = self.config['reglas_recalculo']
        
    def _cargar_yaml(self, path: str) -> dict:
        """Carga archivo YAML"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def calcular_distribucion_definida(self) -> Dict[str, int]:
        """
        Panel A: Distribución planificada según configuración.
        Retorna dict {zona: cantidad_planificada}
        """
        distribucion = {}
        for zona, datos in self.zonas.items():
            distribucion[zona] = datos['capacidad_planificada']
        return distribucion
    
    def calcular_distribucion_observada(self, hasta_timestamp: str = None) -> Dict[str, int]:
        """
        Panel B: Distribución observada calculada desde eventos.
        Procesa entradas/salidas y retorna presencia actual por zona.
        """
        # Estado actual de cada tarjeta: dentro o fuera
        estado_tarjetas = defaultdict(lambda: "fuera")
        
        # Filtrar eventos hasta timestamp dado
        eventos_filtrados = self.eventos
        if hasta_timestamp:
            eventos_filtrados = [
                e for e in self.eventos 
                if e['timestamp'] <= hasta_timestamp
            ]
        
        # Procesar eventos
        for evento in eventos_filtrados:
            id_tarjeta = evento['id_tarjeta']
            tipo = evento['tipo']
            
            if tipo == "entrada":
                estado_tarjetas[id_tarjeta] = "dentro"
            elif tipo == "salida":
                estado_tarjetas[id_tarjeta] = "fuera"
        
        # Contar presencia por zona
        distribucion = defaultdict(int)
        for zona, tarjetas in self.asignaciones.items():
            for tarjeta in tarjetas:
                if estado_tarjetas[tarjeta] == "dentro":
                    distribucion[zona] += 1
        
        return dict(distribucion)
    
    def calcular_distribucion_recalculada(self) -> Dict[str, int]:
        """
        Panel C: Distribución recalculada (recomendada).
        Compara definida vs observada y propone ajustes.
        """
        definida = self.calcular_distribucion_definida()
        observada = self.calcular_distribucion_observada()
        
        recalculada = {}
        
        for zona in self.zonas.keys():
            plan = definida.get(zona, 0)
            obs = observada.get(zona, 0)
            
            # Lógica simple de recálculo
            if obs == 0 and plan == 0:
                # Zona vacía planificada
                recalculada[zona] = 0
            elif obs < plan * self.reglas['umbral_subatencion']:
                # Subatendida: sugerir refuerzo mínimo
                recalculada[zona] = int(plan * 0.8)
            elif obs > plan * self.reglas['umbral_sobredimension']:
                # Sobredimensionada: sugerir reducción
                recalculada[zona] = int(plan * 1.1)
            else:
                # Dentro de rangos aceptables
                recalculada[zona] = obs
        
        return recalculada
    
    def calcular_mapa_calor(self) -> Dict[str, float]:
        """
        Panel D: Proporciones de ocupación por zona.
        Retorna dict {zona: proporcion_ocupacion}
        """
        definida = self.calcular_distribucion_definida()
        observada = self.calcular_distribucion_observada()
        
        mapa_calor = {}
        for zona in self.zonas.keys():
            plan = definida.get(zona, 0)
            obs = observada.get(zona, 0)
            
            if plan == 0:
                mapa_calor[zona] = 0.0
            else:
                mapa_calor[zona] = obs / plan
        
        return mapa_calor
    
    def calcular_evolucion_temporal(self) -> Tuple[List, List, List]:
        """
        Panel E: Series temporales de entradas/salidas.
        Retorna (timestamps, entradas_acum, salidas_acum)
        """
        # Agrupar por hora
        entradas_por_hora = defaultdict(int)
        salidas_por_hora = defaultdict(int)
        
        for evento in self.eventos:
            ts = datetime.fromisoformat(evento['timestamp'])
            hora = ts.hour
            
            if evento['tipo'] == "entrada":
                entradas_por_hora[hora] += 1
            else:
                salidas_por_hora[hora] += 1
        
        # Ordenar por hora
        horas = sorted(set(list(entradas_por_hora.keys()) + list(salidas_por_hora.keys())))
        entradas = [entradas_por_hora[h] for h in horas]
        salidas = [salidas_por_hora[h] for h in horas]
        
        return horas, entradas, salidas
    
    def calcular_indicadores_contexto(self) -> Dict:
        """
        Panel F: Indicadores derivados para soporte a decisiones.
        """
        definida = self.calcular_distribucion_definida()
        observada = self.calcular_distribucion_observada()
        
        total_plan = sum(definida.values())
        total_obs = sum(observada.values())
        
        # Calcular desviaciones
        zonas_criticas = 0
        zonas_sobre = 0
        zonas_sub = 0
        
        for zona in self.zonas.keys():
            plan = definida.get(zona, 0)
            obs = observada.get(zona, 0)
            
            if plan == 0:
                continue
            
            desv = abs((obs - plan) / plan)
            
            if desv > self.reglas['umbral_desviacion_critica']:
                zonas_criticas += 1
            
            if obs > plan * self.reglas['umbral_sobredimension']:
                zonas_sobre += 1
            
            if obs < plan * self.reglas['umbral_subatencion']:
                zonas_sub += 1
        
        return {
            'cumplimiento': (total_obs / total_plan * 100) if total_plan > 0 else 0,
            'desviacion_total': abs(total_obs - total_plan),
            'zonas_criticas': zonas_criticas,
            'zonas_sobre': zonas_sobre,
            'zonas_sub': zonas_sub,
            'eficiencia_distribucion': 85  # Placeholder para algoritmo real
        }


# EJEMPLO DE USO
if __name__ == "__main__":
    sistema = SistemaDistribucion(
        path_eventos="eventos.yaml",
        path_config="configuracion.yaml"
    )
    
    print("=== DISTRIBUCIÓN DEFINIDA ===")
    print(sistema.calcular_distribucion_definida())
    
    print("\n=== DISTRIBUCIÓN OBSERVADA ===")
    print(sistema.calcular_distribucion_observada())
    
    print("\n=== DISTRIBUCIÓN RECALCULADA ===")
    print(sistema.calcular_distribucion_recalculada())
    
    print("\n=== MAPA DE CALOR ===")
    print(sistema.calcular_mapa_calor())
    
    print("\n=== EVOLUCIÓN TEMPORAL ===")
    horas, entradas, salidas = sistema.calcular_evolucion_temporal()
    print(f"Horas: {horas}")
    print(f"Entradas: {entradas}")
    print(f"Salidas: {salidas}")
    
    print("\n=== INDICADORES DE CONTEXTO ===")
    print(sistema.calcular_indicadores_contexto())
