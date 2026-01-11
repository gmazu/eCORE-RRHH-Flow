import sys
from datetime import datetime
from typing import List, Dict
import csv
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gestor_archivos import GestorArchivosEventos
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InyectorManual:
    """
    Permite ingreso manual de eventos (uno a uno o en lote).
    Útil para recuperación manual cuando falla el sistema automático.
    """
    
    def __init__(self, gestor: GestorArchivosEventos):
        self.gestor = gestor
    
    def ingresar_uno_a_uno_interactivo(self):
        """
        Modo interactivo para ingresar eventos de a uno.
        """
        print("\n" + "="*60)
        print("INGRESO MANUAL DE EVENTOS - UNO A UNO")
        print("="*60)
        print("Ingrese 'q' en cualquier campo para salir\n")
        
        eventos_ingresados = 0
        
        while True:
            print(f"\n--- Evento #{eventos_ingresados + 1} ---")
            
            # Timestamp
            timestamp_input = input("Timestamp (YYYY-MM-DDTHH:MM:SS) o 'now': ").strip()
            if timestamp_input.lower() == 'q':
                break
            
            if timestamp_input.lower() == 'now':
                timestamp = datetime.now().isoformat()
            else:
                # Validar formato
                try:
                    datetime.fromisoformat(timestamp_input)
                    timestamp = timestamp_input
                except ValueError:
                    print("❌ Formato de timestamp inválido. Use: 2025-01-10T08:00:00")
                    continue
            
            # ID Tarjeta
            id_tarjeta = input("ID Tarjeta (ej: T001234): ").strip()
            if id_tarjeta.lower() == 'q':
                break
            if not id_tarjeta:
                print("❌ ID Tarjeta no puede estar vacío")
                continue
            
            # Puerta
            puerta_input = input("Puerta (número entero): ").strip()
            if puerta_input.lower() == 'q':
                break
            try:
                puerta = int(puerta_input)
            except ValueError:
                print("❌ Puerta debe ser un número entero")
                continue
            
            # Tipo
            tipo = input("Tipo (entrada/salida): ").strip().lower()
            if tipo == 'q':
                break
            if tipo not in ['entrada', 'salida']:
                print("❌ Tipo debe ser 'entrada' o 'salida'")
                continue
            
            # Crear evento
            evento = {
                "timestamp": timestamp,
                "id_tarjeta": id_tarjeta,
                "puerta": puerta,
                "tipo": tipo
            }
            
            # Confirmar
            print("\nEvento a ingresar:")
            for key, value in evento.items():
                print(f"  {key}: {value}")
            
            confirmar = input("\n¿Confirmar ingreso? (s/n): ").strip().lower()
            if confirmar == 's':
                if self.gestor.agregar_evento(evento):
                    eventos_ingresados += 1
                    print(f"✓ Evento #{eventos_ingresados} ingresado correctamente")
                else:
                    print("❌ Error al ingresar evento")
            else:
                print("Evento descartado")
        
        print(f"\n{'='*60}")
        print(f"Total eventos ingresados: {eventos_ingresados}")
        print(f"{'='*60}\n")
    
    def ingresar_desde_csv(self, ruta_csv: str) -> int:
        """
        Ingresa eventos en lote desde archivo CSV.
        
        Formato esperado del CSV:
        timestamp,id_tarjeta,puerta,tipo
        2025-01-10T08:00:00,T001234,1,entrada
        2025-01-10T08:05:00,T001235,2,entrada
        """
        try:
            ruta = Path(ruta_csv)
            if not ruta.exists():
                logger.error(f"Archivo no encontrado: {ruta_csv}")
                return 0
            
            eventos = []
            
            with open(ruta, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Validar campos
                    if not all(k in row for k in ['timestamp', 'id_tarjeta', 'puerta', 'tipo']):
                        logger.warning(f"Fila inválida omitida: {row}")
                        continue
                    
                    # Convertir puerta a int
                    try:
                        row['puerta'] = int(row['puerta'])
                    except ValueError:
                        logger.warning(f"Puerta inválida en fila: {row}")
                        continue
                    
                    eventos.append(row)
            
            # Ingresar en lote
            cantidad = self.gestor.agregar_eventos_lote(eventos)
            logger.info(f"Eventos desde CSV: {cantidad}/{len(eventos)} ingresados")
            return cantidad
            
        except Exception as e:
            logger.error(f"Error al procesar CSV: {e}")
            return 0
    
    def ingresar_desde_json(self, ruta_json: str) -> int:
        """
        Ingresa eventos en lote desde archivo JSON.
        
        Formato esperado:
        {
            "eventos": [
                {
                    "timestamp": "2025-01-10T08:00:00",
                    "id_tarjeta": "T001234",
                    "puerta": 1,
                    "tipo": "entrada"
                },
                ...
            ]
        }
        """
        try:
            ruta = Path(ruta_json)
            if not ruta.exists():
                logger.error(f"Archivo no encontrado: {ruta_json}")
                return 0
            
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            if 'eventos' not in datos:
                logger.error("JSON debe contener key 'eventos'")
                return 0
            
            eventos = datos['eventos']
            cantidad = self.gestor.agregar_eventos_lote(eventos)
            logger.info(f"Eventos desde JSON: {cantidad}/{len(eventos)} ingresados")
            return cantidad
            
        except Exception as e:
            logger.error(f"Error al procesar JSON: {e}")
            return 0
    
    def ingresar_lote_rapido(self, eventos_texto: str) -> int:
        """
        Ingresa eventos desde texto multilinea.
        
        Formato: timestamp|id_tarjeta|puerta|tipo
        Ejemplo:
        2025-01-10T08:00:00|T001234|1|entrada
        2025-01-10T08:05:00|T001235|2|entrada
        """
        lineas = eventos_texto.strip().split('\n')
        eventos = []
        
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue
            
            partes = linea.split('|')
            if len(partes) != 4:
                logger.warning(f"Línea inválida omitida: {linea}")
                continue
            
            try:
                evento = {
                    "timestamp": partes[0].strip(),
                    "id_tarjeta": partes[1].strip(),
                    "puerta": int(partes[2].strip()),
                    "tipo": partes[3].strip().lower()
                }
                eventos.append(evento)
            except Exception as e:
                logger.warning(f"Error en línea: {linea} - {e}")
                continue
        
        cantidad = self.gestor.agregar_eventos_lote(eventos)
        logger.info(f"Lote rápido: {cantidad}/{len(eventos)} ingresados")
        return cantidad


# CLI
def menu_principal():
    print("\n" + "="*60)
    print("INYECTOR MANUAL DE EVENTOS")
    print("="*60)
    print("1. Ingreso uno a uno (interactivo)")
    print("2. Ingreso desde CSV")
    print("3. Ingreso desde JSON")
    print("4. Ingreso lote rápido (texto)")
    print("5. Ver estado del sistema")
    print("0. Salir")
    print("="*60)


if __name__ == "__main__":
    gestor = GestorArchivosEventos()
    inyector = InyectorManual(gestor)
    
    while True:
        menu_principal()
        opcion = input("\nSeleccione opción: ").strip()
        
        if opcion == '0':
            print("Saliendo...")
            break
        
        elif opcion == '1':
            inyector.ingresar_uno_a_uno_interactivo()
        
        elif opcion == '2':
            ruta = input("Ruta del archivo CSV: ").strip()
            inyector.ingresar_desde_csv(ruta)
        
        elif opcion == '3':
            ruta = input("Ruta del archivo JSON: ").strip()
            inyector.ingresar_desde_json(ruta)
        
        elif opcion == '4':
            print("\nIngrese eventos (formato: timestamp|id_tarjeta|puerta|tipo)")
            print("Termine con una línea vacía:\n")
            lineas = []
            while True:
                linea = input()
                if not linea.strip():
                    break
                lineas.append(linea)
            
            if lineas:
                inyector.ingresar_lote_rapido('\n'.join(lineas))
        
        elif opcion == '5':
            print("\n" + "="*60)
            print("ESTADO DEL SISTEMA")
            print("="*60)
            estado = gestor.obtener_estado()
            for key, value in estado.items():
                print(f"{key}: {value}")
            print("="*60)
        
        else:
            print("❌ Opción inválida")
