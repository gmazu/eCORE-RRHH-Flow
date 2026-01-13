# Sistema de Visualizacion de Distribucion Dinamica de Personas

Sistema de dashboards visuales para gestion operativa de personas basado en eventos minimos de control de acceso, desarrollado con Manim Community Edition.

Repositorio: https://github.com/gmazu/eCORE-RRHH-Flow

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Manim](https://img.shields.io/badge/manim-community-orange.svg)

## Tabla de contenidos

- [Descripcion](#descripcion)
- [Demo](#demo)
- [Quick start](#quick-start)
- [Caracteristicas](#caracteristicas)
- [Requisitos](#requisitos)
- [Instalacion](#instalacion)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Configuracion](#configuracion)
- [Gestion de eventos](#gestion-de-eventos)
- [Paneles disponibles](#paneles-disponibles)
- [Uso](#uso)
- [Troubleshooting](#troubleshooting)
- [Licencia](#licencia)

## Descripcion

Sistema visual tipo dashboard que representa la gestion dinamica de personas a partir de eventos minimos de control de acceso. Los unicos datos base son:
- Identificador de persona (ID tarjeta)
- Timestamp exacto
- Tipo de evento (entrada o salida)
- Puerta de acceso

Toda visualizacion es abstracta, funcional y honesta: solo muestra lo que puede inferirse a partir de esos datos y de calculos derivados explicitos. El sistema esta orientado a optimizacion operativa y toma de decisiones, no a vigilancia ni a representacion espacial real.

## Demo

[![Demo](https://img.youtube.com/vi/sUIP_fu_PX8/0.jpg)](https://youtu.be/sUIP_fu_PX8)

## Quick start

### Opcion 1: demo rapida

```bash
# 1) Instalar dependencias
pip install manim pyyaml numpy

# 2) Generar datos de prueba
python src/simulador_eventos.py --modo jornada

# 3) Preparar para procesamiento
python -c "from gestor_archivos import GestorArchivosEventos; GestorArchivosEventos().preparar_para_procesamiento()"

# 4) Renderizar Panel B
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada
```

### Opcion 2: flujo completo

```bash
# 1) Configurar tu sistema
# Editar config/configuracion.yaml con tus zonas y puertas

# 2) Generar eventos (elige un metodo)
python src/simulador_eventos.py --modo jornada
# o
python src/inyector_manual.py

# 3) Preparar datos para Manim
python -c "from gestor_archivos import GestorArchivosEventos; GestorArchivosEventos().preparar_para_procesamiento()"

# 4) Renderizar paneles
manim -pql src/panel_a_definida.py PanelA_DistribucionDefinida
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada
manim -pql src/panel_c_recalculada.py PanelC_DistribucionRecalculada
```

### Generar CSV por hora (24 archivos por dia)

```bash
# Genera data/12012026/*.csv
python src/simulador_eventos.py 12012026

# Sin parametros: genera el dia siguiente por defecto
python src/simulador_eventos.py
```

### Cargar CSV por hora con inyector_manual.py

```bash
python src/inyector_manual.py
# En el menu:
# 2) Ingreso desde CSV
# Ruta: data/12012026/0900.1000.csv
```

### Carga masiva de todos los CSV del dia

```bash
# Carga los 24 archivos horarios del dia
for f in data/12012026/*.csv; do
  python src/inyector_manual.py <<EOF
2
$f
0
EOF
done
```

## Caracteristicas

- 6 paneles especializados para analisis operativo
- Visualizaciones abstractas sin mapas fisicos
- Calculo de distribuciones: definida, observada y recalculada
- Mapa de calor funcional por zonas
- Analisis de evolucion temporal y patrones
- Indicadores derivados para soporte a decisiones
- Configuracion mediante archivos YAML
- Gestion segura de eventos con mecanismo pausa/copia/reanuda
- Simulador de eventos para testing
- Inyector manual para recuperacion de datos

## Requisitos

### Software
- Python 3.8 o superior
- Manim Community Edition v0.18.0+
- FFmpeg (para renderizado de video)
- LaTeX (opcional, para texto matematico)

### Dependencias Python
```
manim>=0.18.0
pyyaml>=6.0
numpy>=1.24.0
```

## Instalacion

```bash
pip install manim pyyaml numpy
manim --version
```

## Estructura del proyecto

```
R2H2-Flow/
├── config/
│   └── configuracion.yaml
├── data/
│   ├── eventos.yaml
│   └── eventos_procesamiento.yaml
├── src/
│   ├── loader.py
│   ├── simulador_eventos.py
│   ├── inyector_manual.py
│   ├── panelA.py
│   ├── panel_b_observada.py
│   ├── panel_c_recalculada.py
│   ├── panel_d_mapa_calor.py
│   ├── panel_e_temporal.py
│   └── panel_f_contexto.py
├── gestor_archivos.py
├── in-out.py
└── README.md
```

## Configuracion

### Archivo `config/configuracion.yaml`

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

reglas_recalculo:
  umbral_desviacion_critica: 0.20
  umbral_sobredimension: 1.30
  umbral_subatencion: 0.70
```

### Archivo `data/eventos.yaml`

```yaml
eventos:
  - timestamp: "2025-01-10T08:45:12"
    id_tarjeta: "T001234"
    puerta: 1
    tipo: "entrada"
```

## Gestion de eventos

### Flujo de archivos

```
eventos.yaml (escritura activa)
    ↓ PAUSA
    ↓ COPIA
eventos_procesamiento.yaml (lectura Manim)
    ↓ REAPERTURA
eventos.yaml (escritura continua)
```

### Gestor de escritura segura

```python
from gestor_archivos import GestorArchivosEventos

gestor = GestorArchivosEventos()

gestor.agregar_evento({
    "timestamp": "2025-01-10T08:00:00",
    "id_tarjeta": "T001234",
    "puerta": 1,
    "tipo": "entrada"
})

gestor.preparar_para_procesamiento()
```

### Simulador de eventos

```bash
python src/simulador_eventos.py --modo jornada
python src/simulador_eventos.py --modo entrada
python src/simulador_eventos.py --modo continuo --duracion 30 --intervalo 10
```

### Inyector manual

```bash
python src/inyector_manual.py
```

Formatos soportados:
- Interactivo (uno a uno)
- CSV: `timestamp,id_tarjeta,puerta,tipo`
- JSON: `{ "eventos": [...] }`
- Lote rapido: `timestamp|id_tarjeta|puerta|tipo`

## Paneles disponibles

- Panel A: `src/panelA.py` (Distribucion Definida)
- Panel B: `src/panel_b_observada.py` (Distribucion Observada)
- Panel C: `src/panel_c_recalculada.py` (Distribucion Recalculada)
- Panel D: `src/panel_d_mapa_calor.py` (Mapa de Calor)
- Panel E: `src/panel_e_temporal.py` (Evolucion Temporal)
- Panel F: `src/panel_f_contexto.py` (Contexto y Decisiones)
- Panel G: `src/panel_g_flow_busy_hour.py` (Flow Busy Hour)

## Uso

### Renderizar panel individual

```bash
manim -pql src/panelA.py PanelA_DistribucionDefinida
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada
manim -pql src/panel_c_recalculada.py PanelC_DistribucionRecalculada
R2H2_FECHA=12012026 manim -pql src/panel_g_flow_busy_hour.py PanelG_FlowBusyHour
```

### Flujo recomendado

```bash
python src/simulador_eventos.py --modo jornada
python -c "from gestor_archivos import GestorArchivosEventos; GestorArchivosEventos().preparar_para_procesamiento()"
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada
```

## Troubleshooting

- Error: "No module named 'manim'" -> `pip install manim`
- Error: "FFmpeg not found" -> instala FFmpeg en tu sistema
- Error: "YAML parse error" -> verifica indentacion con espacios

## Licencia

Licencia pendiente por definir.
