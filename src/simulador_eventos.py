import time
import random
from datetime import datetime, timedelta
from typing import List
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gestor_archivos import GestorArchivosEventos
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimuladorEventos:
    """
    Simula eventos de entrada/salida en tiempo real.
    Útil para testing y demostraciones.
    """
    
    def __init__(self, gestor: GestorArchivosEventos):
        self.gestor = gestor
        
        # Pool de tarjetas simuladas
        self.tarjetas_activas = [
            "T001234", "T001235", "T001236", "T001237", "T001238",
            "T002001", "T002002", "T002003", "T002004", "T002005",
            "T003100", "T003101", "T003102", "T003103", "T003104",
        ]
        
        # Puertas disponibles
        self.puertas = [1, 2, 3]
        
        # Estado interno: qué tarjetas están dentro
        self.tarjetas_dentro = set()
    
    def generar_evento(self, timestamp: datetime = None) -> dict:
        """
        Genera un evento aleatorio realista.
        
        - Si tarjeta está fuera → genera entrada
        - Si tarjeta está dentro → puede generar salida (probabilidad)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        tarjeta = random.choice(self.tarjetas_activas)
        puerta = random.choice(self.puertas)
        
        # Decidir tipo de evento según estado
        if tarjeta in self.tarjetas_dentro:
            # Está dentro: 30% probabilidad de salir
            if random.random() < 0.3:
                tipo = "salida"
                self.tarjetas_dentro.remove(tarjeta)
            else:
                # No hace nada este ciclo
                return None
        else:
            # Está fuera: siempre entra
            tipo = "entrada"
            self.tarjetas_dentro.add(tarjeta)
        
        return {
            "timestamp": timestamp.isoformat(),
            "id_tarjeta": tarjeta,
            "puerta": puerta,
            "tipo": tipo
        }
    
    def simular_horario_entrada(self, hora_inicio: str = "08:30", duracion_minutos: int = 60):
        """
        Simula horario de entrada masiva (ej: 8:30-9:30 AM).
        """
        logger.info(f"=== SIMULANDO HORARIO ENTRADA: {hora_inicio} ({duracion_minutos} min) ===")
        
        base_time = datetime.now().replace(
            hour=int(hora_inicio.split(':')[0]),
            minute=int(hora_inicio.split(':')[1]),
            second=0
        )
        
        eventos_generados = 0
        
        for minuto in range(duracion_minutos):
            # Simular 1-3 eventos por minuto en horario peak
            eventos_por_minuto = random.randint(1, 3)
            
            for _ in range(eventos_por_minuto):
                timestamp = base_time + timedelta(
                    minutes=minuto,
                    seconds=random.randint(0, 59)
                )
                
                evento = self.generar_evento(timestamp)
                if evento:
                    self.gestor.agregar_evento(evento)
                    eventos_generados += 1
                    time.sleep(0.1)  # Pausa breve para simular tiempo real
        
        logger.info(f"Horario entrada completado: {eventos_generados} eventos")
    
    def simular_horario_salida(self, hora_inicio: str = "18:00", duracion_minutos: int = 45):
        """
        Simula horario de salida masiva (ej: 18:00-18:45).
        """
        logger.info(f"=== SIMULANDO HORARIO SALIDA: {hora_inicio} ({duracion_minutos} min) ===")
        
        base_time = datetime.now().replace(
            hour=int(hora_inicio.split(':')[0]),
            minute=int(hora_inicio.split(':')[1]),
            second=0
        )
        
        eventos_generados = 0
        
        # Forzar que todas las tarjetas dentro salgan
        tarjetas_por_salir = list(self.tarjetas_dentro.copy())
        
        for minuto in range(duracion_minutos):
            if not tarjetas_por_salir:
                break
            
            # Sacar 1-2 personas por minuto
            eventos_por_minuto = min(random.randint(1, 2), len(tarjetas_por_salir))
            
            for _ in range(eventos_por_minuto):
                if not tarjetas_por_salir:
                    break
                
                tarjeta = tarjetas_por_salir.pop(0)
                timestamp = base_time + timedelta(
                    minutes=minuto,
                    seconds=random.randint(0, 59)
                )
                
                evento = {
                    "timestamp": timestamp.isoformat(),
                    "id_tarjeta": tarjeta,
                    "puerta": random.choice(self.puertas),
                    "tipo": "salida"
                }
                
                self.gestor.agregar_evento(evento)
                self.tarjetas_dentro.discard(tarjeta)
                eventos_generados += 1
                time.sleep(0.1)
        
        logger.info(f"Horario salida completado: {eventos_generados} eventos")
    
    def simular_jornada_completa(self):
        """
        Simula una jornada laboral completa:
        - Entrada 08:30-09:30
        - Salida colación 13:00-14:00
        - Entrada colación 14:00-14:30
        - Salida 18:00-18:45
        """
        logger.info("=== INICIANDO SIMULACIÓN JORNADA COMPLETA ===")
        
        # Entrada mañana
        self.simular_horario_entrada(hora_inicio="08:30", duracion_minutos=60)
        
        logger.info(f"Personas dentro después de entrada: {len(self.tarjetas_dentro)}")
        time.sleep(2)
        
        # Salida colación
        self.simular_horario_salida(hora_inicio="13:00", duracion_minutos=30)
        
        logger.info(f"Personas dentro después de salida colación: {len(self.tarjetas_dentro)}")
        time.sleep(2)
        
        # Retorno colación
        tarjetas_en_colacion = [t for t in self.tarjetas_activas if t not in self.tarjetas_dentro]
        for tarjeta in tarjetas_en_colacion[:int(len(tarjetas_en_colacion) * 0.8)]:  # 80% vuelve
            evento = {
                "timestamp": datetime.now().replace(hour=14, minute=random.randint(0, 30)).isoformat(),
                "id_tarjeta": tarjeta,
                "puerta": random.choice(self.puertas),
                "tipo": "entrada"
            }
            self.gestor.agregar_evento(evento)
            self.tarjetas_dentro.add(tarjeta)
            time.sleep(0.1)
        
        logger.info(f"Personas dentro después de retorno colación: {len(self.tarjetas_dentro)}")
        time.sleep(2)
        
        # Salida tarde
        self.simular_horario_salida(hora_inicio="18:00", duracion_minutos=45)
        
        logger.info(f"Personas dentro al final del día: {len(self.tarjetas_dentro)}")
        logger.info("=== SIMULACIÓN JORNADA COMPLETA FINALIZADA ===")
    
    def simular_continuo(self, intervalo_segundos: int = 5, duracion_minutos: int = 10):
        """
        Simula eventos continuos durante un período.
        """
        logger.info(f"=== SIMULACIÓN CONTINUA: {duracion_minutos} minutos ===")
        
        fin = time.time() + (duracion_minutos * 60)
        eventos_generados = 0
        
        while time.time() < fin:
            evento = self.generar_evento()
            if evento:
                self.gestor.agregar_evento(evento)
                eventos_generados += 1
            
            time.sleep(intervalo_segundos)
        
        logger.info(f"Simulación continua finalizada: {eventos_generados} eventos")


# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de eventos de control de acceso")
    parser.add_argument(
        '--modo',
        choices=['entrada', 'salida', 'jornada', 'continuo'],
        default='jornada',
        help='Modo de simulación'
    )
    parser.add_argument(
        '--duracion',
        type=int,
        default=10,
        help='Duración en minutos (para modo continuo)'
    )
    parser.add_argument(
        '--intervalo',
        type=int,
        default=5,
        help='Intervalo entre eventos en segundos (para modo continuo)'
    )
    
    args = parser.parse_args()
    
    # Inicializar gestor y simulador
    gestor = GestorArchivosEventos()
    simulador = SimuladorEventos(gestor)
    
    # Ejecutar según modo
    if args.modo == 'entrada':
        simulador.simular_horario_entrada()
    elif args.modo == 'salida':
        simulador.simular_horario_salida()
    elif args.modo == 'jornada':
        simulador.simular_jornada_completa()
    elif args.modo == 'continuo':
        simulador.simular_continuo(
            intervalo_segundos=args.intervalo,
            duracion_minutos=args.duracion
        )
    
    # Mostrar estado final
    print("\n=== ESTADO FINAL DEL SISTEMA ===")
    print(gestor.obtener_estado())
