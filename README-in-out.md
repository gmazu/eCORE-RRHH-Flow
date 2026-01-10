# README - Sistema de Gestión de Eventos

Subsistema de captura, simulación e inyección de eventos de control de acceso para el Sistema de Visualización de Distribución Dinámica.

## 📋 Descripción

Este módulo gestiona el ciclo completo de eventos desde su captura/generación hasta su disponibilidad para procesamiento, garantizando integridad de datos mediante un mecanismo de escritura segura.

## 🔑 Componentes

### 1. `gestor_archivos.py` - Gestor de Escritura Segura

**Propósito:** Evitar corrupción de datos durante lectura/escritura concurrente.

**Mecanismo:**
```
eventos.yaml (escritura activa)
    ↓ PAUSA
    ↓ COPIA
eventos_procesamiento.yaml (lectura Manim)
    ↓ REAPERTURA
eventos.yaml (escritura activa continúa)
```

**Uso básico:**
```python
from gestor_archivos import GestorArchivosEventos

gestor = GestorArchivosEventos()

# Agregar evento individual
evento = {
    "timestamp": "2025-01-10T08:00:00",
    "id_tarjeta": "T001234",
    "puerta": 1,
    "tipo": "entrada"
}
gestor.agregar_evento(evento)

# Preparar para procesamiento (antes de ejecutar Manim)
gestor.preparar_para_procesamiento()

# Ahora Manim puede leer de eventos_procesamiento.yaml sin conflictos
```

**API Principal:**
- `agregar_evento(evento: Dict) -> bool`: Agrega evento individual
- `agregar_eventos_lote(eventos: List[Dict]) -> int`: Agrega múltiples eventos
- `preparar_para_procesamiento() -> bool`: Ejecuta pausa→copia→reanuda
- `obtener_estado() -> Dict`: Estado actual del sistema
- `contar_eventos(archivo: str) -> int`: Cuenta eventos en archivo especificado

---

### 2. `simulador_eventos.py` - Simulador en Tiempo Real

**Propósito:** Generar eventos automáticamente para testing y demostraciones.

**Modos de simulación:**
- **Entrada:** Simula horario de llegada masiva (8:30-9:30)
- **Salida:** Simula horario de salida masiva (18:00-18:45)
- **Jornada:** Simula jornada completa (entrada + colación + salida)
- **Continuo:** Genera eventos aleatorios durante período definido

**Uso CLI:**
```bash
# Simular jornada completa
python simulador_eventos.py --modo jornada

# Simular solo entrada
python simulador_eventos.py --modo entrada

# Simulación continua por 30 minutos con eventos cada 10 segundos
python simulador_eventos.py --modo continuo --duracion 30 --intervalo 10
```

**Uso programático:**
```python
from gestor_archivos import GestorArchivosEventos
from simulador_eventos import SimuladorEventos

gestor = GestorArchivosEventos()
simulador = SimuladorEventos(gestor)

# Simular jornada completa
simulador.simular_jornada_completa()

# Simular eventos continuos por 10 minutos
simulador.simular_continuo(intervalo_segundos=5, duracion_minutos=10)
```

**Características:**
- Pool de 15 tarjetas simuladas
- 3 puertas disponibles
- Lógica realista: si está dentro puede salir, si está fuera entra
- Timestamps coherentes con horarios laborales

---

### 3. `inyector_manual.py` - Ingreso Manual y en Lote

**Propósito:** Recuperación manual de eventos cuando falla sistema automático.

**Modos de ingreso:**

#### A. Uno a uno (interactivo)
```bash
python inyector_manual.py
# Opción 1: Ingreso uno a uno
```

Solicita campos:
- Timestamp (formato ISO o 'now')
- ID Tarjeta
- Puerta (número)
- Tipo (entrada/salida)

#### B. Desde CSV
```bash
python inyector_manual.py
# Opción 2: Ingreso desde CSV
```

Formato CSV esperado:
```csv
timestamp,id_tarjeta,puerta,tipo
2025-01-10T08:00:00,T001234,1,entrada
2025-01-10T08:05:00,T001235,2,entrada
2025-01-10T18:00:00,T001234,1,salida
```

#### C. Desde JSON
```bash
python inyector_manual.py
# Opción 3: Ingreso desde JSON
```

Formato JSON esperado:
```json
{
  "eventos": [
    {
      "timestamp": "2025-01-10T08:00:00",
      "id_tarjeta": "T001234",
      "puerta": 1,
      "tipo": "entrada"
    }
  ]
}
```

#### D. Lote rápido (texto)
```bash
python inyector_manual.py
# Opción 4: Ingreso lote rápido

# Formato: timestamp|id_tarjeta|puerta|tipo
2025-01-10T08:00:00|T001234|1|entrada
2025-01-10T08:05:00|T001235|2|entrada
2025-01-10T18:00:00|T001234|1|salida
```

**API programática:**
```python
from gestor_archivos import GestorArchivosEventos
from inyector_manual import InyectorManual

gestor = GestorArchivosEventos()
inyector = InyectorManual(gestor)

# Desde CSV
inyector.ingresar_desde_csv("recuperacion_eventos.csv")

# Desde JSON
inyector.ingresar_desde_json("eventos_perdidos.json")

# Lote rápido
eventos_texto = """
2025-01-10T08:00:00|T001234|1|entrada
2025-01-10T08:05:00|T001235|2|entrada
"""
inyector.ingresar_lote_rapido(eventos_texto)
```

---

## 🔄 Flujo de Trabajo Completo

### Escenario 1: Simulación + Procesamiento

```bash
# Terminal 1: Iniciar simulador
python simulador_eventos.py --modo continuo --duracion 60

# Terminal 2: Cuando quieras procesar
python -c "from gestor_archivos import GestorArchivosEventos; g = GestorArchivosEventos(); g.preparar_para_procesamiento()"

# Terminal 2: Renderizar paneles (leen desde eventos_procesamiento.yaml)
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada
```

### Escenario 2: Recuperación Manual

```bash
# Falla en sistema automático → ingreso manual
python inyector_manual.py

# Opción 2: Desde CSV
# Ruta: eventos_recuperados.csv

# Verificar estado
# Opción 5: Ver estado del sistema
```

### Escenario 3: Testing Rápido

```python
from gestor_archivos import GestorArchivosEventos
from simulador_eventos import SimuladorEventos

# Setup
gestor = GestorArchivosEventos()
simulador = SimuladorEventos(gestor)

# Generar datos
simulador.simular_jornada_completa()

# Preparar
gestor.preparar_para_procesamiento()

# Renderizar
# (ejecutar comandos manim)
```

---

## 📁 Archivos Generados

```
data/
├── eventos.yaml                  # Escritura activa (recibe eventos en tiempo real)
├── eventos_procesamiento.yaml    # Copia estática (Manim lee desde aquí)
└── eventos_backup.yaml           # Backup de seguridad
```

**Regla de oro:**
- Simulador/Inyector → escriben en `eventos.yaml`
- Manim/Paneles → leen desde `eventos_procesamiento.yaml`
- NUNCA leer/escribir el mismo archivo simultáneamente

---

## ⚙️ Configuración

### Variables de entorno (opcional)

```bash
# Directorio base para archivos de datos
export EVENTOS_DIR="data"

# Nivel de logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

### Archivos de configuración

El sistema utiliza `configuracion.yaml` para:
- Validar IDs de tarjeta contra asignaciones
- Validar números de puerta
- Aplicar reglas de horarios

---

## 🔍 Troubleshooting

### Error: "Escritura pausada"
```python
# Reactivar escritura manualmente
gestor = GestorArchivosEventos()
gestor.escritura_activa = True
```

### Error: "Archivo corrupto"
```bash
# Restaurar desde backup
cp data/eventos_backup.yaml data/eventos.yaml
```

### Eventos duplicados
El sistema NO filtra duplicados automáticamente. Responsabilidad del usuario evitar:
- Ejecutar múltiples simuladores simultáneos
- Inyectar el mismo archivo CSV dos veces

### Rendimiento lento
```python
# Para lotes grandes, usar agregar_eventos_lote() en vez de bucle
gestor.agregar_eventos_lote(lista_eventos)  # ✓ Rápido
# vs
for e in lista_eventos: gestor.agregar_evento(e)  # ✗ Lento
```

---

## 📊 Monitoreo

### Ver estado del sistema

```python
from gestor_archivos import GestorArchivosEventos

gestor = GestorArchivosEventos()
estado = gestor.obtener_estado()

print(f"Escritura activa: {estado['escritura_activa']}")
print(f"Eventos en escritura: {estado['eventos_escritura']}")
print(f"Eventos en procesamiento: {estado['eventos_procesamiento']}")
```

### Logging

Todos los componentes usan logging estándar de Python:
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Ver todos los eventos
```

---

## 🧪 Testing

```bash
# Test unitario del gestor
python -m pytest tests/test_gestor_archivos.py

# Test de simulador
python -m pytest tests/test_simulador.py

# Test de inyector
python -m pytest tests/test_inyector.py

# Test de integración completa
python -m pytest tests/test_integracion.py
```

---

## 🚀 Ejemplos Rápidos

### Ejemplo 1: Generar 1000 eventos rápido
```python
from gestor_archivos import GestorArchivosEventos
from simulador_eventos import SimuladorEventos
import time

gestor = GestorArchivosEventos()
simulador = SimuladorEventos(gestor)

# Desactivar delays para velocidad
for _ in range(1000):
    evento = simulador.generar_evento()
    if evento:
        gestor.agregar_evento(evento)

print(f"Total eventos: {gestor.contar_eventos('escritura')}")
```

### Ejemplo 2: Importar histórico desde Excel
```python
import pandas as pd
from gestor_archivos import GestorArchivosEventos

# Leer Excel
df = pd.read_excel("historico.xlsx")

# Convertir a formato requerido
eventos = df.to_dict('records')

# Inyectar
gestor = GestorArchivosEventos()
gestor.agregar_eventos_lote(eventos)
```

### Ejemplo 3: Pipeline automatizado
```bash
#!/bin/bash
# pipeline.sh

# 1. Generar datos
python simulador_eventos.py --modo jornada

# 2. Preparar para procesamiento
python -c "from gestor_archivos import GestorArchivosEventos; GestorArchivosEventos().preparar_para_procesamiento()"

# 3. Renderizar todos los paneles
python scripts/render_all.py --quality high

# 4. Limpiar archivo de escritura (opcional)
python -c "from gestor_archivos import GestorArchivosEventos; GestorArchivosEventos().limpiar_archivo_escritura()"
```

---

## ⚠️ Advertencias

1. **NO ejecutar `preparar_para_procesamiento()` mientras el simulador está activo** → puede causar pérdida de eventos en tránsito
2. **NO editar manualmente eventos_procesamiento.yaml** → es generado automáticamente
3. **NO eliminar eventos_backup.yaml** → es tu red de seguridad
4. **Validar formato de eventos** antes de inyección masiva → eventos inválidos son descartados silenciosamente

---

## 📝 Notas de Implementación

- **Thread-safe:** Usa `threading.Lock` para escritura concurrente
- **Atomicidad:** Operaciones de archivo usan `shutil.copy2` para garantizar integridad
- **Validación:** Campos requeridos validados antes de escritura
- **Logging:** Eventos importantes registrados para auditoría
- **Backups:** Backup automático antes de cada `preparar_para_procesamiento()`

---

## 🔗 Integración con Paneles Manim

Los paneles deben modificarse para leer desde `eventos_procesamiento.yaml`:

```python
# En cada panel_X.py
from src.loader import SistemaDistribucion

sistema = SistemaDistribucion(
    path_eventos="data/eventos_procesamiento.yaml",  # ← Archivo estático
    path_config="data/configuracion.yaml"
)

# Usar datos del sistema
distribucion = sistema.calcular_distribucion_observada()
```

---

**Versión:** 1.0  
**Última actualización:** 2025-01-10  
**Compatibilidad:** Python 3.8+
