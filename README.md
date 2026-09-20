# WaterMarker

Aplicación de escritorio para aplicar marcas de agua de texto a imágenes, desarrollada en PyQt6.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-1.4.5-orange)

## Características

- **Marcas de agua personalizables**: Texto libre con fuente, tamaño, color, ángulo y transparencia ajustables
- **Selector de fuentes**: Diálogo con búsqueda, vista previa y todas las fuentes del sistema
- **Marca de agua repetida (tiled)**: Rasteriza la imagen con el patrón de marca de agua
- **Efectos de texto**: Sombra (offset X/Y) y borde con ancho configurable
- **Modo oscuro/claro**: Tema completo con persistencia
- **Presets**: Guardar y cargar configuraciones de marca de agua
- **Exportar**: PNG con transparencia o JPEG con calidad ajustable
- **Vista previa en tiempo real**: Actualización instantánea al modificar parámetros
- **Barra de estado**: Muestra dimensiones y tamaño del archivo
- **Posición persistente**: Guarda posición y tamaño de la ventana
- **Splash screen**: Pantalla de carga al iniciar

## Instalación

### Dependencias

```bash
pip install PyQt6 Pillow
```

### Ejecutar desde código fuente

```bash
git clone https://github.com/edfasano70/watermarker.git
cd watermarker
python main.py
```

### Paquete .deb (Ubuntu/Debian)

Descargá el `.deb` desde [Releases](https://github.com/edfasano70/watermarker/releases) e instalá:

```bash
sudo dpkg -i watermarker_1.4.5_amd64.deb
```

### Compilar ejecutable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name watermarker --add-data "resources:resources" main.py
```

El ejecutable queda en `dist/watermarker`.

## Estructura del proyecto

```
watermarker/
├── main.py              # Aplicación completa (UI, lógica, config)
├── resources/
│   ├── icons/           # Iconos SVG (naranja #FF9800)
│   ├── logo.png         # Logo de la aplicación
│   ├── splash.png       # imagen del splash screen
│   ├── checkers.png     # Fondo de transparencia
│   └── ...
├── TODO.md              # Lista de tareas
└── README.md
```

## Atajos de teclado

| Acción | Atajo |
|--------|-------|
| Abrir imagen | `Ctrl+O` |
| Guardar imagen | `Ctrl+S` |
| Guardar preset | `Ctrl+Shift+S` |
| Cargar preset | `Ctrl+Shift+O` |
| Salir | `Ctrl+Q` |
| Ayuda | `F1` |

## Configuración

La configuración se guarda en `~/.config/watermarker/config.xml` e incluye:

- Modo oscuro/claro
- Última carpeta abierta
- Parámetros de marca de agua (fuente, tamaño, color, ángulo, transparencia)
- Efectos de texto (sombra/borde)
- Posición y tamaño de ventana

## Tecnologías

- **Python 3.12**
- **PyQt6** - Interfaz gráfica
- **Pillow** - Procesamiento de imágenes
- **PyInstaller** - Empaquetamiento en ejecutable

## Licencia

MIT

## Autor

**EdFasano70** - [GitHub](https://github.com/edfasano70)
