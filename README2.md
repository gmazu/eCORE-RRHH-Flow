# README.md - Versión Completa Actualizada

```markdown
# Sistema de Visualización de Distribución Dinámica de Personas

Sistema de dashboards visuales para gestión operativa de personas basado en eventos mínimos de control de acceso, desarrollado con Manim Community Edition.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Manim](https://img.shields.io/badge/manim-community-orange.svg)

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Quick Start](#quick-start)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración](#configuración)
- [Sistema de Gestión de Eventos](#sistema-de-gestión-de-eventos)
- [Uso](#uso)
- [Paneles Disponibles](#paneles-disponibles)
- [Formato de Datos](#formato-de-datos)
- [Ejemplos](#ejemplos)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

## 📖 Descripción

Sistema visual tipo dashboard que representa la gestión dinámica de personas a partir de eventos mínimos de control de acceso. Los únicos datos base son:
- Identificador de persona (ID tarjeta)
- Timestamp exacto
- Tipo de evento (entrada o salida)
- Puerta de acceso

Toda visualización es **abstracta, funcional y honesta**: solo muestra lo que puede inferirse a partir de esos datos y de cálculos derivados explícitos. El sistema está orientado a **optimización operativa y toma de decisiones**, no a vigilancia ni a representación espacial real.

## 🚀 Quick Start

### Opción 1: Demo Rápida (5 minutos)

```bash
# 1. Clonar e instalar
git clone https://github.com/tu-usuario/sistema-distribucion-dinamica.git
cd sistema-distribucion-dinamica
pip install -r requirements.txt

# 2. Generar datos de prueba
python src/simulador_eventos.py --modo jornada

# 3. Preparar para procesamiento
python -c "from src.gestor_archivos import GestorArchivosEventos; GestorArchivosEventos().preparar_para_procesamiento()"

# 4. Renderizar Panel B (el más visual)
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada

# 5. Ver resultado en output/
```

### Opción 2: Pipeline Completo (15 minutos)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar tu sistema (editar archivos)
cp data/ejemplos/configuracion_template.yaml data/configuracion.yaml
# Editar data/configuracion.yaml con tus zonas y puertas

# 3. Generar eventos (elegir método)
# Método A: Simulación
python src/simulador_eventos.py --modo jornada

# Método B: Ingreso manual
python src/inyector_manual.py

# 4. Preparar datos
python scripts/preparar_procesamiento.py

# 5. Renderizar todos los paneles
python scripts/render_all.py --quality medium

# 6. Ver resultados
ls output/*.mp4
```

### Opción 3: Solo Configuración (si ya tienes datos)

```bash
# 1. Colocar tus datos reales
cp tu_archivo_eventos.yaml data/eventos.yaml

# 2. Verificar formato
python scripts/validar_datos.py

# 3. Preparar y renderizar
python scripts/preparar_procesamiento.py
python scripts/render_all.py
```

## ✨ Características

- 🎯 6 paneles especializados para análisis operativo
- 📊 Visualizaciones abstractas sin mapas físicos
- 🔄 Cálculo de distribuciones: definida, observada y recalculada
- 🌡️ Mapa de calor funcional por zonas
- 📈 Análisis de evolución temporal y patrones
- 🎛️ Indicadores derivados para soporte a decisiones
- 📝 Configuración mediante archivos YAML
- 🔌 Sistema modular y extensible
- 🛡️ Gestión segura de eventos con mecanismo pausa/copia/reanuda
- 🤖 Simulador de eventos para testing
- ✍️ Inyector manual para recuperación de datos

## 🔧 Requisitos

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

## 📦 Instalación

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
# Instalación básica
pip install manim

# Verificar instalación
manim --version
```

### 5. Instalar FFmpeg

**Windows:**
```bash
# Usando chocolatey
choco install ffmpeg

# O descargar desde https://ffmpeg.org/download.html
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## 📁 Estructura del Proyecto

```
sistema-distribucion-dinamica/
├── data/
│   ├── eventos.yaml                  # Eventos en escritura activa
│   ├── eventos_procesamiento.yaml    # Eventos para lectura (Manim)
│   ├── eventos_backup.yaml           # Backup automático
│   ├── configuracion.yaml            # Configuración del sistema
│   └── ejemplos/                     # Datos de ejemplo
├── src/
│   ├── gestor_archivos.py            # Gestor de escritura segura
│   ├── simulador_eventos.py          # Generador automático de eventos
│   ├── inyector_manual.py            # Ingreso manual y en lote
│   ├── loader.py                     # Motor de carga y procesamiento
│   ├── panel_a_definida.py           # Panel A: Distribución Definida
│   ├── panel_b_observada.py          # Panel B: Distribución Observada
│   ├── panel_c_recalculada.py        # Panel C: Distribución Recalculada
│   ├── panel_d_mapa_calor.py         # Panel D: Mapa de Calor Funcional
│   ├── panel_e_temporal.py           # Panel E: Evolución Temporal
│   └── panel_f_contexto.py           # Panel F: Contexto y Decisiones
├── scripts/
│   ├── render_all.py                 # Renderizar todos los paneles
│   ├── preparar_procesamiento.py     # Preparar datos para Manim
│   └── validar_datos.py              # Validar formato de datos
├── output/                            # Videos generados (auto-creado)
├── tests/                             # Tests unitarios
├── docs/                              # Documentación adicional
├── requirements.txt                   # Dependencias Python
├── README.md                          # Este archivo
└── LICENSE                            # Licencia del proyecto
```

## ⚙️ Configuración

### 1. Archivo `eventos.yaml`

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

### 2. Archivo `configuracion.yaml`

Define zonas, mapeo y reglas:

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

Ver archivos de ejemplo completos en `data/ejemplos/`.

## 📡 Sistema de Gestión de Eventos

Subsistema de captura, simulación e inyección de eventos con mecanismo de escritura segura.

### 🔑 Componentes Principales

#### 1. `gestor_archivos.py` - Gestor de Escritura Segura

**Propósito:** Evitar corrupción de datos durante lectura/escritura concurrente.

**Mecanismo de seguridad:**
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
from src.gestor_archivos import GestorArchivosEventos

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
# Ahora Manim lee de eventos_procesamiento.yaml sin conflictos
```

**API Principal:**
- `agregar_evento(evento: Dict) -> bool`: Agrega evento individual
- `agregar_eventos_lote(eventos: List[Dict]) -> int`: Agrega múltiples eventos
- `preparar_para_procesamiento() -> bool`: Ejecuta pausa→copia→reanuda
- `obtener_estado() -> Dict`: Estado actual del sistema
- `contar_eventos(archivo: str) -> int`: Cuenta eventos en archivo

---

#### 2. `simulador_eventos.py` - Generador Automático

**Propósito:** Crear eventos **ficticios/sintéticos** automáticamente para testing y demostraciones.

**Diferencia clave:** Los eventos NO son reales, son simulados.

**Modos de simulación:**
- **entrada:** Horario de llegada masiva (8:30-9:30)
- **salida:** Horario de salida masiva (18:00-18:45)
- **jornada:** Jornada completa (entrada + colación + salida)
- **continuo:** Eventos aleatorios durante período definido

**Uso CLI:**
```bash
# Simular jornada completa
python src/simulador_eventos.py --modo jornada

# Simular solo entrada
python src/simulador_eventos.py --modo entrada

# Simulación continua por 30 minutos con eventos cada 10 segundos
python src/simulador_eventos.py --modo continuo --duracion 30 --intervalo 10
```

**Uso programático:**
```python
from src.gestor_archivos import GestorArchivosEventos
from src.simulador_eventos import SimuladorEventos

gestor = GestorArchivosEventos()
simulador = SimuladorEventos(gestor)

# Simular jornada completa
simulador.simular_jornada_completa()

# Simular eventos continuos por 10 minutos
simulador.simular_continuo(intervalo_segundos=5, duracion_minutos=10)
```

---

#### 3. `inyector_manual.py` - Ingreso de Eventos Reales

**Propósito:** Ingresar eventos **reales** que ocurrieron pero NO se capturaron automáticamente (falla en sistema de lectura).

**Diferencia clave:** Los eventos SON reales, solo que se ingresan manualmente.

**Modos de ingreso:**

##### A. Uno a uno (interactivo)
```bash
python src/inyector_manual.py
# Opción 1: Ingreso uno a uno
```

##### B. Desde CSV
```bash
python src/inyector_manual.py
# Opción 2: Ingreso desde CSV
```

Formato CSV:
```csv
timestamp,id_tarjeta,puerta,tipo
2025-01-10T08:00:00,T001234,1,entrada
2025-01-10T08:05:00,T001235,2,entrada
```

##### C. Desde JSON
```bash
python src/inyector_manual.py
# Opción 3: Ingreso desde JSON
```

Formato JSON:
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

##### D. Lote rápido (texto)
```bash
python src/inyector_manual.py
# Opción 4: Ingreso lote rápido

# Formato: timestamp|id_tarjeta|puerta|tipo
2025-01-10T08:00:00|T001234|1|entrada
2025-01-10T08:05:00|T001235|2|entrada
```

---

### 🔄 Flujo de Trabajo Completo

#### Escenario 1: Simulación + Procesamiento

```bash
# Terminal 1: Iniciar simulador
python src/simulador_eventos.py --modo continuo --duracion 60

# Terminal 2: Cuando quieras procesar
python scripts/preparar_procesamiento.py

# Terminal 2: Renderizar paneles
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada
```

#### Escenario 2: Recuperación Manual

```bash
# Falla en sistema automático → ingreso manual
python src/inyector_manual.py

# Opción 2: Desde CSV
# Ruta: eventos_recuperados.csv

# Verificar estado
# Opción 5: Ver estado del sistema
```

#### Escenario 3: Testing Rápido

```python
from src.gestor_archivos import GestorArchivosEventos
from src.simulador_eventos import SimuladorEventos

# Setup
gestor = GestorArchivosEventos()
simulador = SimuladorEventos(gestor)

# Generar datos
simulador.simular_jornada_completa()

# Preparar
gestor.preparar_para_procesamiento()

# Renderizar (ejecutar comandos manim)
```

---

### 📁 Archivos Generados

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

### 🎯 ¿Cuándo usar cada herramienta?

| Situación | Usa |
|-----------|-----|
| Probar el sistema sin datos reales | `simulador_eventos.py` |
| Lector de tarjetas falló, ingresar eventos reales a mano | `inyector_manual.py` |
| Necesito 1000 eventos para testing | `simulador_eventos.py` |
| Recuperar eventos perdidos de un Excel | `inyector_manual.py` |
| Demostración en vivo sin hardware | `simulador_eventos.py` |
| Migrar datos históricos desde otro sistema | `inyector_manual.py` |

---

## 🚀 Uso

### Generar todos los paneles

```bash
# Renderizar todos los paneles en calidad media
python scripts/render_all.py

# Renderizar en alta calidad (1080p)
python scripts/render_all.py --quality high

# Renderizar en baja calidad (480p, más rápido)
python scripts/render_all.py --quality low
```

### Generar panel individual

```bash
# Panel A - Distribución Definida
manim -pql src/panel_a_definida.py PanelA_DistribucionDefinida

# Panel B - Distribución Observada
manim -pql src/panel_b_observada.py PanelB_DistribucionObservada

# Panel C - Distribución Recalculada
manim -pql src/panel_c_recalculada.py PanelC_DistribucionRecalculada

# Panel D - Mapa de Calor
manim -pql src/panel_d_mapa_calor.py PanelD_MapaCalorFuncional

# Panel E - Evolución Temporal
manim -pql src/panel_e_temporal.py PanelE_EvolucionTemporal

# Panel F - Contexto y Decisiones
manim -pql src/panel_f_contexto.py PanelF_ContextoDecisiones
```

### Parámetros de renderizado

```bash
# -p: Reproducir automáticamente después de renderizar
# -q: Calidad (l=low 480p, m=medium 720p, h=high 1080p, k=4k)
# -s: Guardar última frame como imagen
# -a: Renderizar todas las escenas del archivo

# Ejemplos:
manim -pqh src/panel_a_definida.py  # Alta calidad con reproducción
manim -sql src/panel_b_observada.py # Baja calidad, solo última frame
manim -pqm -a src/panel_c_recalculada.py # Media calidad, todas las escenas
```

## 📊 Paneles Disponibles

### Panel A: Distribución Definida (Planificada)
Visualización de la configuración planificada antes de la jornada operativa.
- **Entrada:** `configuracion.yaml` → zonas_funcionales
- **Salida:** Barras horizontales con valores planificados
- **Propósito:** Baseline operativo, referencia estable

### Panel B: Distribución Observada (Real)
Estado real del sistema calculado desde eventos de entrada/salida.
- **Entrada:** `eventos_procesamiento.yaml` procesado por `loader.py`
- **Salida:** Barras actualizables en tiempo real
- **Propósito:** Dato objetivo sin interpretación

### Panel C: Distribución Recalculada (Recomendada)
Sugerencias de ajuste operativo basadas en comparación definida vs observada.
- **Entrada:** Salidas de Panel A + Panel B + reglas_recalculo
- **Salida:** Comparativa con indicadores de cambio
- **Propósito:** Optimización dinámica, no es orden

### Panel D: Mapa de Calor Funcional
Nivel de ocupación relativa por zona mediante código de colores.
- **Entrada:** Proporciones observado/esperado
- **Salida:** Grid de bloques coloreados
- **Propósito:** Lectura inmediata del balance operativo
- **Colores:** Verde (completo), Amarillo (parcial), Rojo (déficit)

### Panel E: Evolución Temporal y Ritmo Operativo
Análisis de pulsos, acumulaciones y patrones temporales.
- **Entrada:** Series temporales de eventos
- **Salida:** Gráficos de líneas + acumulación neta
- **Propósito:** Identificar horarios críticos, alimentar recalculo

### Panel F: Contexto y Soporte a Decisiones
Indicadores derivados para optimización operativa.
- **Entrada:** Todos los cálculos anteriores
- **Salida:** Cards de métricas + oportunidades
- **Propósito:** Decisiones de contratar, liberar, automatizar

## 📄 Formato de Datos

### Estructura mínima de `eventos.yaml`

```yaml
eventos:
  - timestamp: "2025-01-10T08:00:00"
    id_tarjeta: "T000001"
    puerta: 1
    tipo: "entrada"
```

### Validaciones automáticas

El sistema valida:
- ✅ Formato de timestamp ISO 8601
- ✅ Tipos de evento válidos (entrada/salida)
- ✅ Consistencia de IDs de tarjeta
- ✅ Referencias a puertas definidas en configuración
- ✅ Capacidades planificadas coherentes

### Generador de datos sintéticos

Para testing rápido:

```bash
python src/simulador_eventos.py --modo jornada
```

Genera `eventos.yaml` sintético con patrones realistas.

## 💡 Ejemplos

### Ejemplo 1: Análisis de día completo

```bash
# 1. Generar datos del día
python src/simulador_eventos.py --modo jornada

# 2. Preparar para procesamiento
python scripts/preparar_procesamiento.py

# 3. Generar todos los paneles
python scripts/render_all.py --quality high

# 4. Resultados en output/
ls output/
```

### Ejemplo 2: Modo interactivo (desarrollo)

```python
from src.loader import SistemaDistribucion

# Cargar sistema
sistema = SistemaDistribucion(
    path_eventos="data/eventos_procesamiento.yaml",
    path_config="data/configuracion.yaml"
)

# Consultar estado actual
print(sistema.calcular_distribucion_observada())

# Simular hasta timestamp específico
print(sistema.calcular_distribucion_observada(
    hasta_timestamp="2025-01-10T12:00:00"
))

# Obtener indicadores
print(sistema.calcular_indicadores_contexto())
```

### Ejemplo 3: Integración con pipeline CI/CD

```yaml
# .github/workflows/render.yml
name: Render Dashboards

on:
  push:
    paths:
      - 'data/eventos.yaml'

jobs:
  render:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          sudo apt-get install ffmpeg
          pip install -r requirements.txt
      - name: Prepare data
        run: python scripts/preparar_procesamiento.py
      - name: Render panels
        run: python scripts/render_all.py --quality medium
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: dashboards
          path: output/*.mp4
```

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest tests/

# Test específico
pytest tests/test_loader.py

# Con cobertura
pytest --cov=src tests/
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de estilo

- Código: PEP 8
- Commits: Conventional Commits
- Documentación: Markdown + docstrings Google Style

## 🐛 Troubleshooting

### Error: "No module named 'manim'"

```bash
pip install manim
```

### Error: "FFmpeg not found"

Instalar FFmpeg según instrucciones en [Instalación](#instalación).

### Renderizado lento

```bash
# Usar calidad baja para pruebas
manim -pql archivo.py Escena

# O solo última frame
manim -sql archivo.py Escena
```

### Error: "YAML parse error"

Verificar indentación en archivos YAML (usar espacios, no tabs).

### Error: "Escritura pausada"
```python
# Reactivar escritura manualmente
from src.gestor_archivos import GestorArchivosEventos
gestor = GestorArchivosEventos()
gestor.escritura_activa = True
```

### Eventos duplicados
El sistema NO filtra duplicados automáticamente. Evitar:
- Ejecutar múltiples simuladores simultáneos
- Inyectar el mismo archivo CSV dos veces

## 📚 Documentación Adicional

- [Guía de Configuración Avanzada](docs/configuracion_avanzada.md)
- [API Reference](docs/api_reference.md)
- [Algoritmo de Recálculo](docs/algoritmo_recalculo.md)
- [Casos de Uso](docs/casos_de_uso.md)

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👥 Autores

- **Tu Nombre** - *Desarrollo inicial* - [tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Manim Community por la biblioteca de animación
- Comunidad Python por las herramientas de análisis de datos

## 📞 Contacto

Para preguntas o soporte:
- Email: tu-email@ejemplo.com
- Issues: [GitHub Issues](https://github.com/tu-usuario/sistema-distribucion-dinamica/issues)
- Discussions: [GitHub Discussions](https://github.com/tu-usuario/sistema-distribucion-dinamica/discussions)

---

**Nota:** Este sistema NO realiza seguimiento individual de personas ni vigilancia. Solo procesa eventos agregados para optimización operativa.
```

---

# Script adicional: scripts/preparar_procesamiento.py

```python
#!/usr/bin/env python3
"""
Script helper para preparar datos antes de renderizar paneles.
"""

from src.gestor_archivos import GestorArchivosEventos
import sys

def main():
    print("="*60)
    print("PREPARANDO DATOS PARA PROCESAMIENTO")
    print("="*60)
    
    gestor = GestorArchivosEventos()
    
    # Mostrar estado inicial
    estado = gestor.obtener_estado()
    print(f"\nEventos en archivo de escritura: {estado['eventos_escritura']}")
    
    # Preparar
    if gestor.preparar_para_procesamiento():
        print("\n✓ Preparación exitosa")
        print(f"✓ Archivo de procesamiento listo con {gestor.contar_eventos('procesamiento')} eventos")
        print(f"✓ Backup creado con {gestor.contar_eventos('backup')} eventos")
        print("\nAhora puedes ejecutar:")
        print("  python scripts/render_all.py")
        print("  o")
        print("  manim -pql src/panel_X.py PanelX")
        return 0
    else:
        print("\n❌ Error en preparación")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

# Script adicional: scripts/validar_datos.py

```python
#!/usr/bin/env python3
"""
Valida formato de eventos.yaml y configuracion.yaml
"""

import yaml
from pathlib import Path
from datetime import datetime
import sys

def validar_eventos(ruta="data/eventos.yaml"):
    print(f"\n{'='*60}")
    print(f"VALIDANDO: {ruta}")
    print(f"{'='*60}")
    
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = yaml.safe_load(f)
        
        if not datos or 'eventos' not in datos:
            print("❌ Estructura inválida: debe contener key 'eventos'")
            return False
        
        eventos = datos['eventos']
        print(f"✓ Archivo cargado: {len(eventos)} eventos")
        
        campos_requeridos = ['timestamp', 'id_tarjeta', 'puerta', 'tipo']
        errores = 0
        
        for i, evento in enumerate(eventos):
            # Validar campos
            for campo in campos_requeridos:
                if campo not in evento:
                    print(f"❌ Evento #{i+1}: falta campo '{campo}'")
                    errores += 1
            
            # Validar timestamp
            try:
                datetime.fromisoformat(evento['timestamp'])
            except:
                print(f"❌ Evento #{i+1}: timestamp inválido '{evento.get('timestamp')}'")
                errores += 1
            
            # Validar tipo
            if evento.get('tipo') not in ['entrada', 'salida']:
                print(f"❌ Evento #{i+1}: tipo debe ser 'entrada' o 'salida'")
                errores += 1
            
            # Validar puerta
            try:
                int(evento.get('puerta'))
            except:
                print(f"❌ Evento #{i+1}: puerta debe ser número entero")
                errores += 1
        
        if errores == 0:
            print(f"✓ Todos los eventos son válidos")
            return True
        else:
            print(f"\n❌ Se encontraron {errores} errores")
            return False
            
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {ruta}")
        return False
    except Exception as e:
        print(f"❌ Error al validar: {e}")
        return False

def validar_configuracion(ruta="data/configuracion.yaml"):
    print(f"\n{'='*60}")
    print(f"VALIDANDO: {ruta}")
    print(f"{'='*60}")
    
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = yaml.safe_load(f)
        
        # Validar secciones principales
        secciones_requeridas = [
            'zonas_funcionales',
            'mapeo_puertas',
            'asignacion_tarjetas',
            'horarios',
            'reglas_recalculo'
        ]
        
        for seccion in secciones_requeridas:
            if seccion not in datos:
                print(f"❌ Falta sección: {seccion}")
                return False
        
        print(f"✓ Todas las secciones presentes")
        print(f"✓ Zonas definidas: {len(datos['zonas_funcionales'])}")
        print(f"✓ Puertas mapeadas: {len(datos['mapeo_puertas'])}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {ruta}")
        return False
    except Exception as e:
        print(f"❌ Error al validar: {e}")
        return False

def main():
    print("="*60)
    print("VALIDADOR DE DATOS DEL SISTEMA")
    print("="*60)
    
    val_eventos = validar_eventos()
    val_config = validar_configuracion()
    
    print(f"\n{'='*60}")
    print("RESUMEN")
    print(f"{'='*60}")
    print(f"Eventos: {'✓ VÁLIDO' if val_eventos else '❌ INVÁLIDO'}")
    print(f"Configuración: {'✓ VÁLIDO' if val_config else '❌ INVÁLIDO'}")
    
    if val_eventos and val_config:
        print("\n✓ Sistema listo para usar")
        return 0
    else:
        print("\n❌ Corrige los errores antes de continuar")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

**RESUMEN DE LO ACTUALIZADO:**

✅ README principal completo con:
- Quick Start agregado
- Sistema de Gestión de Eventos integrado
- Diferencia clara entre simulador e inyector
- Tabla comparativa de cuándo usar cada herramienta
- Troubleshooting expandido

✅ Scripts helper creados:
- `scripts/preparar_procesamiento.py` - Simplifica el preparar datos
- `scripts/validar_datos.py` - Valida formato antes de procesar

✅ **PENDIENTE:** Actualizar los 6 paneles Manim para que lean desde `loader.py` con datos reales de YAML.

¿Quieres que actualice los paneles ahora o está bien así?
