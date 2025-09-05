# Manual de Usuario – Sistema de Gestión de Librería

Este documento está dividido en dos partes:

1. **Guía amigable para usuarios finales** (uso cotidiano del sistema sin necesidad de conocimientos técnicos).  
2. **Guía técnica** (instalación, configuración y resolución de problemas).

---

## 1. Guía amigable (Usuarios no técnicos)

### Requisitos previos
- Computadora con **Windows** o **Linux**.
- Tener instalado **Python 3.8 o superior** (en la mayoría de los casos ya estará configurado).
- **Cámara web** (opcional, solo para escanear códigos de barras en tiempo real).

### Iniciar el programa
1. Abre la carpeta del proyecto.
2. Haz doble clic en el archivo **`sistema.py`** (en algunos equipos deberás usar clic derecho → *Abrir con → Python*).
3. Espera a que aparezca la ventana principal de la aplicación.

### Pantalla principal
La interfaz está organizada en **pestañas**:
- **Inventario**: administrar los productos.
- **Ventas**: procesar compras y generar facturas.
- **Reportes**: ver estadísticas y gráficos de ventas.
- **Configuración**: datos de la empresa y preferencias del sistema.

### Gestión de inventario
1. Ir a la pestaña **Inventario**.
2. Para añadir un producto:
   - Ingresar el **código de barras** (puede ser escaneado o escrito a mano).
   - Completar **nombre**, **precio**, **cantidad** e **IVA**.
   - Pulsar **Guardar**.
3. Para modificar un producto:
   - Buscarlo en la lista.
   - Seleccionarlo y presionar **Editar**.
4. Para eliminar un producto:
   - Seleccionarlo y pulsar **Eliminar**.

### Realizar una venta
1. Ir a la pestaña **Ventas**.
2. Escanear o escribir el **código de barras** del producto.
3. El producto aparecerá en el carrito:
   - Ajusta la cantidad si es necesario.
   - Repite para añadir más productos.
4. Completa los **datos del cliente** (nombre y DNI/RUC).
5. Selecciona el **método de pago**.
6. Haz clic en **Finalizar venta**:
   - Se descuenta el stock automáticamente.
   - Se genera una **factura PDF** en la carpeta `facturas/`.

### Consultar reportes
1. Ir a la pestaña **Reportes**.
2. Elige el tipo de reporte:
   - Ventas por día.
   - Productos más vendidos.
   - Métodos de pago.
3. Los gráficos aparecerán en pantalla.
4. Puedes **exportar a PDF o CSV** para guardarlos.

### Consejos de uso
- Mantén actualizado tu inventario: registra cada nuevo producto antes de venderlo.
- Revisa los reportes semanalmente para entender mejor tus ventas.
- Haz copias de seguridad periódicas de las carpetas `inventario.csv`, `ventas.csv` y `facturas/`.

---

## 2. Guía técnica (Instalación, configuración y soporte)

### Instalación

#### Opción 1 – Método recomendado (entorno virtual)
```bash
# Clonar el proyecto
git clone https://github.com/tu-usuario/sistema-gestion-libreria.git
cd sistema-gestion-libreria

# Crear entorno virtual
python -m venv .venv
# Activar entorno
# Windows
.venv\Scripts\activate
# Linux
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### Opción 2 – Usando instaladores (pueden estar desactualizados)

- **Windows:** ejecutar `install.bat.`

- **Linux:** ejecutar `chmod +x install.sh && ./install.sh.`

#### Verificación manual de dependencias**
```bash
python check_deps.py
```

#### Ejecución del sistema
```bash
python sistema.py
```

### Archivos principales

- **sistema.py** → aplicación principal.
- **requirements.txt** → dependencias.
- **inventario.csv** → base de datos de productos.
- **ventas.csv** → historial de ventas.
- **config.json** → datos de la empresa y preferencias.
- **facturas/** → carpeta donde se guardan las facturas PDF.

#### Personalización

En `config.json` puedes modificar:

- **Datos de la empresa** (nombre, dirección, CUIT/DNI).
- **Preferencias de facturas** (directorio, prefijo de archivos).
- **Tasas de IVA permitidas.**
- **Tema visual de la interfaz** (ej. arc, plastik).
- **Parámetros de escaneo con cámara** (usar_camara, indice_camara).

### Solución de problemas

- **Tkinter no instalado (Linux):**
```bash
sudo apt-get install python3-tk
```

- **Cámara no detectada:**
  - Cambiar `"indice_camara"` en `config.json` (0, 1, 2…).
  - Verificar que otra aplicación no esté usando la cámara.

- **Error al abrir PDFs generados:**
  - Asegúrate de tener un visor de PDF instalado.

- **Dependencias con errores:**
```bash
python -m pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

#### Recomendaciones de seguridad

- Haz **copias de seguridad** manuales de los archivos `csv` y la carpeta `facturas/`.
- No edites manualmente los archivos CSV a menos que sepas lo que haces.
- Revisa regularmente los logs para detectar problemas.

## 3. Contacto y soporte

Para consultas o reportes de errores:

- Abre un **issue** en el repositorio de GitHub.
- Adjunta capturas o descripciones claras del problema.
- Indica versión de Python y sistema operativo.

---