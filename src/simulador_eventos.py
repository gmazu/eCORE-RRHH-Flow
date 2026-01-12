import time
import random
import csv
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple
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


def _parse_fecha_ddmmyyyy(fecha_str: str) -> date:
    try:
        return datetime.strptime(fecha_str, "%d%m%Y").date()
    except ValueError as exc:
        raise ValueError("Formato de fecha invalido, use DDMMYYYY (ej: 12012026)") from exc


def _random_datetime(
    rng: random.Random,
    base_date: date,
    start_h: int,
    start_m: int,
    end_h: int,
    end_m: int,
) -> datetime:
    start = datetime(base_date.year, base_date.month, base_date.day, start_h, start_m, 0)
    end = datetime(base_date.year, base_date.month, base_date.day, end_h, end_m, 59)
    delta = int((end - start).total_seconds())
    return start + timedelta(seconds=rng.randint(0, max(delta, 0)))


def _split_by_hour(eventos: List[Tuple[datetime, Dict]]) -> Dict[int, List[Dict]]:
    por_hora = {h: [] for h in range(24)}
    for dt, evento in eventos:
        por_hora[dt.hour].append(evento)
    return por_hora


def _escribir_csv_por_hora(base_dir: Path, eventos_por_hora: Dict[int, List[Dict]]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    headers = ["timestamp", "id_tarjeta", "puerta", "tipo"]
    for hora in range(24):
        hora_fin = (hora + 1) % 24
        nombre = f"{hora:02d}00.{hora_fin:02d}00.csv"
        ruta = base_dir / nombre
        with open(ruta, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for evento in sorted(eventos_por_hora[hora], key=lambda e: e["timestamp"]):
                writer.writerow(evento)


def generar_archivos_diarios(fecha_str: str, base_data: Path = Path("data")) -> Path:
    base_date = _parse_fecha_ddmmyyyy(fecha_str)
    rng = random.Random(int(base_date.strftime("%Y%m%d")))

    empleados = [f"T{num:03d}" for num in range(1, 101)]
    guardia = "T101"
    cocina = "T102"
    aseo = "T103"

    max_ausentes = max(0, int(len(empleados) * 0.05))
    ausentes = set(rng.sample(empleados, rng.randint(0, max_ausentes)))
    presentes = [t for t in empleados if t not in ausentes]

    eventos: List[Tuple[datetime, Dict]] = []

    def add_evento(dt: datetime, tarjeta: str, puerta: int, tipo: str) -> None:
        eventos.append((
            dt,
            {
                "timestamp": dt.isoformat(),
                "id_tarjeta": tarjeta,
                "puerta": puerta,
                "tipo": tipo,
            },
        ))

    # Guardias y personal fuera de horario
    add_evento(_random_datetime(rng, base_date, 0, 5, 0, 40), guardia, 1, "entrada")
    add_evento(_random_datetime(rng, base_date, 6, 0, 6, 20), guardia, 4, "salida")
    add_evento(_random_datetime(rng, base_date, 21, 5, 21, 25), guardia, 1, "entrada")
    add_evento(_random_datetime(rng, base_date, 23, 0, 23, 30), guardia, 4, "salida")

    add_evento(_random_datetime(rng, base_date, 7, 0, 7, 30), cocina, 1, "entrada")
    add_evento(_random_datetime(rng, base_date, 16, 0, 16, 20), cocina, 4, "salida")
    add_evento(_random_datetime(rng, base_date, 20, 30, 21, 0), aseo, 1, "entrada")
    add_evento(_random_datetime(rng, base_date, 22, 0, 22, 30), aseo, 4, "salida")

    # Llegadas 09:00 - 13:00
    rng.shuffle(presentes)
    llegada_mayoria = int(len(presentes) * rng.uniform(0.65, 0.8))
    grupo_mayoria = presentes[:llegada_mayoria]
    grupo_tarde = presentes[llegada_mayoria:]
    llegada_por_tarjeta: Dict[str, datetime] = {}

    for tarjeta in grupo_mayoria:
        dt = _random_datetime(rng, base_date, 9, 0, 9, 59)
        add_evento(dt, tarjeta, rng.choice([1, 2, 3]), "entrada")
        llegada_por_tarjeta[tarjeta] = dt

    for tarjeta in grupo_tarde:
        hora = rng.choices([10, 11, 12], weights=[0.5, 0.3, 0.2], k=1)[0]
        dt = _random_datetime(rng, base_date, hora, 0, hora, 55)
        add_evento(dt, tarjeta, rng.choice([1, 2, 3]), "entrada")
        llegada_por_tarjeta[tarjeta] = dt

    # Salidas cortas entre 09 y 13
    salida_corta = rng.sample(presentes, k=max(1, int(len(presentes) * 0.08)))
    for tarjeta in salida_corta:
        llegada = llegada_por_tarjeta.get(tarjeta)
        if not llegada:
            continue
        inicio = llegada + timedelta(minutes=30)
        fin = datetime(base_date.year, base_date.month, base_date.day, 12, 30, 0)
        if inicio >= fin:
            continue
        dt_salida = inicio + timedelta(seconds=rng.randint(0, int((fin - inicio).total_seconds())))
        dt_entrada = dt_salida + timedelta(minutes=rng.randint(10, 45))
        add_evento(dt_salida, tarjeta, 4, "salida")
        add_evento(dt_entrada, tarjeta, rng.choice([1, 2, 3]), "entrada")

    # Colacion
    casino_pct = rng.uniform(0.5, 0.8)
    fuera_pct = rng.uniform(0.1, 0.25)
    casino_count = int(len(presentes) * casino_pct)
    fuera_count = int(len(presentes) * fuera_pct)
    rng.shuffle(presentes)
    grupo_casino = presentes[:casino_count]
    grupo_fuera = presentes[casino_count:casino_count + fuera_count]

    for tarjeta in grupo_casino:
        dt = _random_datetime(rng, base_date, 13, 0, 13, 50)
        add_evento(dt, tarjeta, 5, "entrada")

    for tarjeta in grupo_fuera:
        dt_salida = _random_datetime(rng, base_date, 13, 0, 13, 40)
        add_evento(dt_salida, tarjeta, 4, "salida")
        dt_entrada = _random_datetime(rng, base_date, 14, 0, 14, 45)
        add_evento(dt_entrada, tarjeta, rng.choice([1, 2, 3]), "entrada")
        if rng.random() < 0.7:
            dt_piso = dt_entrada + timedelta(minutes=rng.randint(1, 8))
            add_evento(dt_piso, tarjeta, 6, "entrada")

    # Salida final
    overtime_count = max(1, int(len(presentes) * rng.uniform(0.02, 0.05)))
    overtime = set(rng.sample(presentes, k=overtime_count))
    for tarjeta in presentes:
        if tarjeta in overtime:
            dt_salida = _random_datetime(rng, base_date, 19, 30, 21, 30)
        else:
            dt_salida = _random_datetime(rng, base_date, 18, 0, 18, 45)

        if rng.random() < 0.6:
            dt_piso = dt_salida - timedelta(minutes=rng.randint(2, 8))
            add_evento(dt_piso, tarjeta, 7, "salida")
        add_evento(dt_salida, tarjeta, 4, "salida")

    eventos.sort(key=lambda item: item[0])
    eventos_por_hora = _split_by_hour(eventos)

    destino = base_data / base_date.strftime("%d%m%Y")
    _escribir_csv_por_hora(destino, eventos_por_hora)
    logger.info("Archivos diarios generados en %s", destino)
    return destino


# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de eventos de control de acceso")
    parser.add_argument(
        "fecha",
        nargs="?",
        help="Fecha DDMMYYYY para generar CSV por hora (ej: 12012026)"
    )
    parser.add_argument(
        '--modo',
        choices=['entrada', 'salida', 'jornada', 'continuo'],
        default=None,
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

    if args.fecha or len(sys.argv) == 1:
        if args.fecha:
            fecha = args.fecha
        else:
            fecha = (date.today() + timedelta(days=1)).strftime("%d%m%Y")
        generar_archivos_diarios(fecha)
        sys.exit(0)

    # Inicializar gestor y simulador
    gestor = GestorArchivosEventos()
    simulador = SimuladorEventos(gestor)

    # Ejecutar según modo
    modo = args.modo or "jornada"
    if modo == 'entrada':
        simulador.simular_horario_entrada()
    elif modo == 'salida':
        simulador.simular_horario_salida()
    elif modo == 'jornada':
        simulador.simular_jornada_completa()
    elif modo == 'continuo':
        simulador.simular_continuo(
            intervalo_segundos=args.intervalo,
            duracion_minutos=args.duracion
        )
    
    # Mostrar estado final
    print("\n=== ESTADO FINAL DEL SISTEMA ===")
    print(gestor.obtener_estado())
