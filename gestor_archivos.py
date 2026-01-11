import yaml
import shutil
import time
from pathlib import Path
from typing import List, Dict
from threading import Lock
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GestorArchivosEventos:
    """
    Gestiona la escritura segura de eventos evitando corrupción.
    
    Flujo:
    1. Escritura activa en eventos.yaml
    2. PAUSA → copia a eventos_procesamiento.yaml
    3. REAPERTURA escritura en eventos.yaml
    4. Manim lee desde eventos_procesamiento.yaml (estático)
    """
    
    def __init__(self, ruta_base: str = "data"):
        self.ruta_base = Path(ruta_base)
        self.archivo_escritura = self.ruta_base / "eventos.yaml"
        self.archivo_procesamiento = self.ruta_base / "eventos_procesamiento.yaml"
        self.archivo_backup = self.ruta_base / "eventos_backup.yaml"
        
        # Lock para escritura thread-safe
        self.lock_escritura = Lock()
        
        # Estado del sistema
        self.escritura_activa = True
        
        # Crear directorio si no existe
        self.ruta_base.mkdir(parents=True, exist_ok=True)
        
        # Inicializar archivo de escritura si no existe
        if not self.archivo_escritura.exists():
            self._inicializar_archivo_vacio(self.archivo_escritura)
    
    def _inicializar_archivo_vacio(self, archivo: Path):
        """Crea archivo YAML vacío con estructura base"""
        estructura_base = {"eventos": []}
        with open(archivo, 'w', encoding='utf-8') as f:
            yaml.dump(estructura_base, f, allow_unicode=True, sort_keys=False)
        logger.info(f"Archivo inicializado: {archivo}")
    
    def agregar_evento(self, evento: Dict) -> bool:
        """
        Agrega un evento al archivo de escritura activo.
        Thread-safe mediante lock.
        
        Args:
            evento: Dict con keys: timestamp, id_tarjeta, puerta, tipo
        
        Returns:
            bool: True si se agregó exitosamente
        """
        if not self.escritura_activa:
            logger.warning("Escritura pausada. Evento no agregado.")
            return False
        
        # Validar estructura del evento
        campos_requeridos = ['timestamp', 'id_tarjeta', 'puerta', 'tipo']
        if not all(campo in evento for campo in campos_requeridos):
            logger.error(f"Evento inválido. Campos requeridos: {campos_requeridos}")
            return False
        
        with self.lock_escritura:
            try:
                # Leer eventos actuales
                with open(self.archivo_escritura, 'r', encoding='utf-8') as f:
                    datos = yaml.safe_load(f)
                
                if datos is None:
                    datos = {"eventos": []}
                
                # Agregar nuevo evento
                datos['eventos'].append(evento)
                
                # Escribir de vuelta
                with open(self.archivo_escritura, 'w', encoding='utf-8') as f:
                    yaml.dump(datos, f, allow_unicode=True, sort_keys=False)
                
                logger.info(f"Evento agregado: {evento['id_tarjeta']} - {evento['tipo']} - Puerta {evento['puerta']}")
                return True
                
            except Exception as e:
                logger.error(f"Error al agregar evento: {e}")
                return False
    
    def agregar_eventos_lote(self, eventos: List[Dict]) -> int:
        """
        Agrega múltiples eventos en lote.
        
        Returns:
            int: Cantidad de eventos agregados exitosamente
        """
        if not self.escritura_activa:
            logger.warning("Escritura pausada. Lote no agregado.")
            return 0
        
        with self.lock_escritura:
            try:
                # Leer eventos actuales
                with open(self.archivo_escritura, 'r', encoding='utf-8') as f:
                    datos = yaml.safe_load(f)
                
                if datos is None:
                    datos = {"eventos": []}
                
                # Agregar nuevos eventos
                eventos_validos = 0
                for evento in eventos:
                    campos_requeridos = ['timestamp', 'id_tarjeta', 'puerta', 'tipo']
                    if all(campo in evento for campo in campos_requeridos):
                        datos['eventos'].append(evento)
                        eventos_validos += 1
                    else:
                        logger.warning(f"Evento inválido omitido: {evento}")
                
                # Escribir de vuelta
                with open(self.archivo_escritura, 'w', encoding='utf-8') as f:
                    yaml.dump(datos, f, allow_unicode=True, sort_keys=False)
                
                logger.info(f"Lote agregado: {eventos_validos}/{len(eventos)} eventos")
                return eventos_validos
                
            except Exception as e:
                logger.error(f"Error al agregar lote: {e}")
                return 0
    
    def preparar_para_procesamiento(self) -> bool:
        """
        PAUSA escritura → COPIA a procesamiento → REAPERTURA escritura.
        Este es el método clave para lectura segura.
        
        Returns:
            bool: True si la preparación fue exitosa
        """
        with self.lock_escritura:
            try:
                logger.info("=== INICIANDO PREPARACIÓN PARA PROCESAMIENTO ===")
                
                # 1. PAUSAR escritura
                self.escritura_activa = False
                logger.info("✓ Escritura PAUSADA")
                
                # 2. BACKUP del archivo actual (seguridad)
                if self.archivo_escritura.exists():
                    shutil.copy2(self.archivo_escritura, self.archivo_backup)
                    logger.info(f"✓ Backup creado: {self.archivo_backup}")
                
                # 3. COPIAR a archivo de procesamiento
                if self.archivo_escritura.exists():
                    shutil.copy2(self.archivo_escritura, self.archivo_procesamiento)
                    logger.info(f"✓ Copiado a procesamiento: {self.archivo_procesamiento}")
                else:
                    logger.warning("Archivo de escritura no existe. Creando vacío.")
                    self._inicializar_archivo_vacio(self.archivo_procesamiento)
                
                # 4. REINICIAR archivo de escritura (opcional: mantener o limpiar)
                # Opción A: Mantener eventos (acumula histórico)
                # Opción B: Limpiar (solo eventos nuevos post-procesamiento)
                # Aquí usamos Opción A por defecto
                
                # 5. REABRIR escritura
                self.escritura_activa = True
                logger.info("✓ Escritura REABIERTA")
                
                logger.info("=== PREPARACIÓN COMPLETADA ===")
                return True
                
            except Exception as e:
                logger.error(f"Error en preparación: {e}")
                self.escritura_activa = True  # Reabrir en caso de error
                return False
    
    def limpiar_archivo_escritura(self) -> bool:
        """
        Limpia el archivo de escritura (útil después de procesamiento).
        Solo usar si quieres que eventos.yaml no acumule histórico.
        """
        with self.lock_escritura:
            try:
                self._inicializar_archivo_vacio(self.archivo_escritura)
                logger.info("Archivo de escritura limpiado")
                return True
            except Exception as e:
                logger.error(f"Error al limpiar: {e}")
                return False
    
    def contar_eventos(self, archivo: str = "escritura") -> int:
        """
        Cuenta eventos en archivo especificado.
        
        Args:
            archivo: "escritura", "procesamiento" o "backup"
        """
        try:
            if archivo == "escritura":
                ruta = self.archivo_escritura
            elif archivo == "procesamiento":
                ruta = self.archivo_procesamiento
            elif archivo == "backup":
                ruta = self.archivo_backup
            else:
                logger.error(f"Archivo desconocido: {archivo}")
                return 0
            
            if not ruta.exists():
                return 0
            
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = yaml.safe_load(f)
            
            if datos and 'eventos' in datos:
                return len(datos['eventos'])
            return 0
            
        except Exception as e:
            logger.error(f"Error al contar eventos: {e}")
            return 0
    
    def obtener_estado(self) -> Dict:
        """Retorna estado actual del sistema"""
        return {
            "escritura_activa": self.escritura_activa,
            "eventos_escritura": self.contar_eventos("escritura"),
            "eventos_procesamiento": self.contar_eventos("procesamiento"),
            "eventos_backup": self.contar_eventos("backup"),
            "archivo_escritura_existe": self.archivo_escritura.exists(),
            "archivo_procesamiento_existe": self.archivo_procesamiento.exists(),
        }


# EJEMPLO DE USO
if __name__ == "__main__":
    gestor = GestorArchivosEventos()
    
    # Agregar algunos eventos
    eventos_prueba = [
        {
            "timestamp": "2025-01-10T08:00:00",
            "id_tarjeta": "T001234",
            "puerta": 1,
            "tipo": "entrada"
        },
        {
            "timestamp": "2025-01-10T08:05:00",
            "id_tarjeta": "T001235",
            "puerta": 2,
            "tipo": "entrada"
        },
    ]
    
    for evento in eventos_prueba:
        gestor.agregar_evento(evento)
    
    print("\n=== ESTADO INICIAL ===")
    print(gestor.obtener_estado())
    
    # Preparar para procesamiento
    print("\n=== PREPARANDO PARA PROCESAMIENTO ===")
    gestor.preparar_para_procesamiento()
    
    print("\n=== ESTADO POST-PREPARACIÓN ===")
    print(gestor.obtener_estado())
    
    # Agregar más eventos (van al archivo de escritura)
    nuevo_evento = {
        "timestamp": "2025-01-10T08:10:00",
        "id_tarjeta": "T001236",
        "puerta": 1,
        "tipo": "entrada"
    }
    gestor.agregar_evento(nuevo_evento)
    
    print("\n=== ESTADO FINAL ===")
    print(gestor.obtener_estado())
