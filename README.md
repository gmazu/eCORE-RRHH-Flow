# Sistema de Visualización de Distribución Dinámica de Personas

Sistema de dashboards visuales para gestión operativa de personas basado en eventos mínimos de control de acceso, desarrollado con Manim Community Edition.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Manim](https://img.shields.io/badge/manim-community-orange.svg)

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración](#configuración)
- [Gestión de Eventos](#gestión-de-eventos)
- [Paneles Disponibles](#paneles-disponibles)
- [Uso](#uso)
- [Ejemplos](#ejemplos)
- [Troubleshooting](#troubleshooting)
- [Tests](#tests)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

## Descripción

Sistema visual tipo dashboard que representa la gestión dinámica de personas a partir de eventos mínimos de control de acceso. Los únicos datos base son:
- Identificador de persona (ID tarjeta)
- Timestamp exacto
- Tipo de evento (entrada o salida)
- Puerta de acceso

Toda visualización es **abstracta, funcional y honesta**: solo muestra lo que puede inferirse a partir de esos datos y de cálculos derivados explícitos. El sistema está orientado a **optimización operativa y toma de decisiones**, no a vigilancia ni a representación espacial real.

## Características

- 6 paneles especializados para análisis operativo
- Visualizaciones abstractas sin mapas físicos
- Cálculo de distribuciones: definida, observada y recalculada
- Mapa de calor funcional por zonas
- Análisis de evolución temporal y patrones
- Indicadores derivados para soporte a decisiones
- Configuración mediante archivos YAML
- Sistema modular y extensible
- Gestión de eventos con escritura segura
- Simulador de eventos para testing
- Inyector manual para recuperación de datos

## Requisitos

### Software
- Python 3.8 o superior
- Manim Community Edition v0.18.0+
- FFmpeg (para renderizado de video)
- LaTeX (opcional, para texto matemático)

### Dependencias Python
```
manim>=0.18.0
pyyaml>=6.0
numpy>=1.24.0
```

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/sistema-distribucion-dinamica.git
cd sistema-distribucion-dinamica
```

### 2. Crear entorno virtual (recomendado)

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar Manim Community

```bash
pip install manim
manim --version
```

### 5. Instalar FFmpeg

**Windows:**
```bash
choco install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## Estructura del Proyecto

```
sistema-distribucion-dinamica/
├── data/
│   ├── eventos.yaml                  # Escritura activa (recibe eventos)
│   ├── eventos_procesamiento.yaml    # Copia estática (Manim lee aquí)
│   ├── eventos_backup.yaml           # Backup de seguridad
│   └── configuration.yaml            # Configuración del sistema
├── src/
│   ├── loader.py                     # Motor de carga y procesamiento
│   ├── gestor_archivos.py            # Gestor de escritura segura
│   ├── simulador_eventos.py          # Simulador en tiempo real
│   ├── inyector_manual.py            # Ingreso manual y en lote
│   ├── panel_a_definida.py           # Panel A: Distribución Definida
│   ├── panel_b_observada.py          # Panel B: Distribución Observada
│   ├── panel_c_recalculada.py        # Panel C: Distribución Recalculada
│   ├── panel_d_mapa_calor.py         # Panel D: Mapa de Calor Funcional
│   ├── panel_e_temporal.py           # Panel E: Evolución Temporal
│   └── panel_f_contexto.py           # Panel F: Contexto y Decisiones
├── scripts/
│   ├── render_all.py                 # Renderizar todos los paneles
│   └── generate_sample_data.py       # Generador de datos sintéticos
├── output/                           # Videos generados
├── tests/                            # Tests unitarios
├── docs/                             # Documentación adicional
├── requirements.txt
├── README.md
└── LICENSE
```

## Configuración

### Archivo `configuration.yaml`

Define zonas, mapeo de puertas y reglas:

```yaml
zonas_funcionales:
  DEPTO_A:
    nombre: "Departamento A"
    capacidad_planificada: 40

mapeo_puertas:
  1:
    zonas: ["DEPTO_A", "DEPTO_B"]
    descripcion: "Acceso principal"

asignacion_tarjetas:
  DEPTO_A:
    - "T001234"
    - "T001235"

horarios:
  lunes_viernes:
    entrada: "09:00:00"
    salida: "18:00:00"
    colacion:
      duracion_minutos: 60

reglas_recalculo:
  umbral_desviacion_critica: 0.20
  umbral_sobredimension: 1.30
  umbral_subatencion: 0.70
```

### Archivo `eventos.yaml`

Define los eventos de control de acceso:

```yaml
eventos:
  - timestamp: "2025-01-10T08:45:12"
    id_tarjeta: "T001234"
    puerta: 1
    tipo: "entrada"

  - timestamp: "2025-01-10T18:00:05"
    id_tarjeta: "T001234"
    puerta: 1
    tipo: "salida"
```

**Campos obligatorios:**
- `timestamp`: Formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)
- `id_tarjeta`: Identificador único de tarjeta/persona
- `puerta`: Número entero (1, 2, 3, ...)
- `tipo`: "entrada" o "salida"

---

## Gestión de Eventos

Subsistema de captura, simulación e inyección de eventos garantizando integridad de datos mediante escritura segura.

### Flujo de Archivos

```
eventos.yaml (escritura activa)
    ↓ PAUSA
    ↓ COPIA
eventos_procesamiento.yaml (lectura Manim)
    ↓ REAPERTURA
eventos.yaml (escritura continúa)
```

**Regla de oro:**
- Simulador/Inyector → escriben en `eventos.yaml`
- Manim/Paneles → leen desde `eventos_procesamiento.yaml`
- NUNCA leer/escribir el mismo archivo simultáneamente

### Componente 1: Gestor de Escritura Segura

**`gestor_archivos.py`** - Evita corrupción de datos durante lectura/escritura concurrente.

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
```

**API Principal:**
| Método | Descripción |
|--------|-------------|
| `agregar_evento(evento)` | Agrega evento individual |
| `agregar_eventos_lote(eventos)` | Agrega múltiples eventos |
| `preparar_para_procesamiento()` | Ejecuta pausa→copia→reanuda |
| `obtener_estado()` | Estado actual del sistema |
| `contar_eventos(archivo)` | Cuenta eventos en archivo |

### Componente 2: Simulador de Eventos

**`simulador_eventos.py`** - Genera eventos automáticamente para testing.

**Modos de simulación:**
- **entrada**: Simula horario de llegada (8:30-9:30)
- **salida**: Simula horario de salida (18:00-18:45)
- **jornada**: Simula jornada completa
- **continuo**: Genera eventos aleatorios

```bash
# Simular jornada completa
python simulador_eventos.py --modo jornada

# Simulación continua por 30 minutos
python simulador_eventos.py --modo continuo --duracion 30 --intervalo 10
```

```python
from simulador_eventos import SimuladorEventos

simulador = SimuladorEventos(gestor)
simulador.simular_jornada_completa()
simulador.simular_continuo(intervalo_segundos=5, duracion_minutos=10)
```

### Componente 3: Inyector Manual

**`inyector_manual.py`** - Recuperación manual de eventos.

```bash
python inyector_manual.py
```

**Formatos soportados:**

| Modo | Formato |
|------|---------|
| Interactivo | Uno a uno con prompts |
| CSV | `timestamp,id_tarjeta,puerta,tipo` |
| JSON | `{"eventos": [...]}` |
| Lote rápido | `timestamp\|id_tarjeta\|puerta\|tipo` |

```python
from inyector_manual import InyectorManual

inyector = InyectorManual(gestor)
inyector.ingresar_desde_csv("recuperacion.csv")
inyector.ingresar_desde_json("eventos.json")
```

---

## Paneles Disponibles

### Panel A: Distribución Definida (Planificada)
Visualización de la configuración planificada antes de la jornada operativa.
- **Entrada:** `configuration.yaml` → zonas_funcionales
- **Salida:** Barras horizontales con valores planificados
- **Propósito:** Baseline operativo, referencia estable

### Panel B: Distribución Observada (Real)
Estado real del sistema calculado desde eventos de entrada/salida.
- **Entrada:** `eventos.yaml` procesado por `loader.py`
- **Salida:** Barras actualizables en tiempo real
- **Propósito:** Dato objetivo sin interpretación

### Panel C: Distribución Recalculada (Recomendada)
Sugerencias de ajuste operativo basadas en comparación definida vs observada.
- **Entrada:** Salidas de Panel A + Panel B + reglas_recalculo
- **Salida:** Comparativa con indicadores de cambio
- **Propósito:** Optimización dinámica

### Panel D: Mapa de Calor Funcional
Nivel de ocupación relativa por zona mediante código de colores.
- **Entrada:** Proporciones observado/esperado
- **Salida:** Grid de bloques coloreados
- **Colores:** Verde (completo), Amarillo (parcial), Rojo (déficit)

### Panel E: Evolución Temporal y Ritmo Operativo
Análisis de pulsos, acumulaciones y patrones temporales.
- **Entrada:** Series temporales de eventos
- **Salida:** Gráficos de líneas + acumulación neta

### Panel F: Contexto y Soporte a Decisiones
Indicadores derivados para optimización operativa.
- **Entrada:** Todos los cálculos anteriores
- **Salida:** Cards de métricas + oportunidades
- **Propósito:** Decisiones de contratar, liberar, automatizar

---

## Uso

### Generar todos los paneles

```bash
python scripts/render_all.py
python scripts/render_all.py --quality high   # 1080p
python scripts/render_all.py --quality low    # 480p, más rápido
```

### Generar panel individual

```bash
manim -pql src/panel_a_definida.py PanelA_DistribucionDefinida
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada
manim -pql src/panel_c_recalculada.py PanelC_DistribucionRecalculada
manim -pql src/panel_d_mapa_calor.py PanelD_MapaCalorFuncional
manim -pql src/panel_e_temporal.py PanelE_EvolucionTemporal
manim -pql src/panel_f_contexto.py PanelF_ContextoDecisiones
```

### Parámetros de renderizado

```bash
# -p: Reproducir después de renderizar
# -q: Calidad (l=480p, m=720p, h=1080p, k=4k)
# -s: Guardar última frame como imagen
# -a: Renderizar todas las escenas

manim -pqh src/panel_a_definida.py  # Alta calidad
manim -sql src/panel_b_observada.py # Solo última frame
```

### Flujo de trabajo: Simulación + Procesamiento

```bash
# Terminal 1: Iniciar simulador
python simulador_eventos.py --modo continuo --duracion 60

# Terminal 2: Preparar y renderizar
python -c "from gestor_archivos import GestorArchivosEventos; GestorArchivosEventos().preparar_para_procesamiento()"
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada
```

---

## Ejemplos

### Ejemplo 1: Pipeline completo

```bash
#!/bin/bash
# 1. Generar datos
python simulador_eventos.py --modo jornada

# 2. Preparar para procesamiento
python -c "from gestor_archivos import GestorArchivosEventos; GestorArchivosEventos().preparar_para_procesamiento()"

# 3. Renderizar
python scripts/render_all.py --quality high
```

### Ejemplo 2: Uso programático

```python
from src.loader import SistemaDistribucion

sistema = SistemaDistribucion(
    path_eventos="data/eventos_procesamiento.yaml",
    path_config="data/configuration.yaml"
)

# Consultar estado actual
print(sistema.calcular_distribucion_observada())

# Simular hasta timestamp específico
print(sistema.calcular_distribucion_observada(
    hasta_timestamp="2025-01-10T12:00:00"
))
```

### Ejemplo 3: Generar 1000 eventos rápido

```python
from gestor_archivos import GestorArchivosEventos
from simulador_eventos import SimuladorEventos

gestor = GestorArchivosEventos()
simulador = SimuladorEventos(gestor)

for _ in range(1000):
    evento = simulador.generar_evento()
    if evento:
        gestor.agregar_evento(evento)

print(f"Total eventos: {gestor.contar_eventos('escritura')}")
```

### Ejemplo 4: Importar desde Excel

```python
import pandas as pd
from gestor_archivos import GestorArchivosEventos

df = pd.read_excel("historico.xlsx")
eventos = df.to_dict('records')

gestor = GestorArchivosEventos()
gestor.agregar_eventos_lote(eventos)
```

---

## Troubleshooting

### Error: "No module named 'manim'"
```bash
pip install manim
```

### Error: "FFmpeg not found"
Instalar FFmpeg según instrucciones en [Instalación](#instalación).

### Renderizado lento
```bash
manim -pql archivo.py Escena  # Calidad baja
manim -sql archivo.py Escena  # Solo última frame
```

### Error: "YAML parse error"
Verificar indentación (usar espacios, no tabs).

### Error: "Escritura pausada"
```python
gestor = GestorArchivosEventos()
gestor.escritura_activa = True
```

### Error: "Archivo corrupto"
```bash
cp data/eventos_backup.yaml data/eventos.yaml
```

### Eventos duplicados
El sistema NO filtra duplicados. Evitar:
- Múltiples simuladores simultáneos
- Inyectar el mismo CSV dos veces

### Rendimiento lento en lotes
```python
gestor.agregar_eventos_lote(lista_eventos)  # Rápido
# vs
for e in lista_eventos: gestor.agregar_evento(e)  # Lento
```

---

## Tests

```bash
pytest tests/
pytest tests/test_loader.py
pytest --cov=src tests/
```

---

## Contribuir

1. Fork el proyecto
2. Crea rama: `git checkout -b feature/AmazingFeature`
3. Commit: `git commit -m 'Add AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. Abre Pull Request

**Guías de estilo:**
- Código: PEP 8
- Commits: Conventional Commits
- Documentación: Google Style docstrings

---

## Advertencias

1. **NO ejecutar `preparar_para_procesamiento()` mientras el simulador está activo**
2. **NO editar manualmente `eventos_procesamiento.yaml`**
3. **NO eliminar `eventos_backup.yaml`**
4. **Validar formato de eventos antes de inyección masiva**

---

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE`.

---

**Nota:** Este sistema NO realiza seguimiento individual de personas ni vigilancia. Solo procesa eventos agregados para optimización operativa.
