import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import datetime
import os
import csv
import json
from ttkthemes import ThemedStyle
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2
from PIL import Image, ImageTk
import numpy as np
import logging

# funcion solo de prueba - carga unos datos: cargar_datos_ejemplo
'''
## Función completa para cargar datos de ejemplo en el sistema: [ cargar_datos_ejemplo ]
Los datos incluyen una variedad de escenarios realistas que te permitirán probar todas las funcionalidades del sistema.

### Características de la función:

- Datos realistas: Incluye 20 productos de librería populares con códigos ISBN reales
- Ventas variadas: 20 transacciones con diferentes clientes y métodos de pago
- Configuración completa: Datos de empresa realistas
- Facturas de ejemplo: Genera algunas facturas PDF de demostración
- Manejo de errores: Incluye try-catch y logging de eventos
- Actualización automática: Refresca las interfaces después de cargar los datos

### Uso:

1. Ejecuta el sistema
2. Ve a la pestaña "Configuración"
3. Haz clic en "Cargar Datos de Ejemplo"
4. El sistema se poblará con datos de demostración listos para usar

### Esta función es perfecta para:

- Pruebas del sistema
- Demostraciones a clientes
- Entrenamiento de nuevos usuarios
- Desarrollo y debugging


### Implementación - Cómo integrar la función en tu clase o removerla:

1. Ubicacion de la función dentro de la clase InventorySalesSystem:
<!--
class InventorySalesSystem:
    # ... código existente ...
    
    def cargar_datos_ejemplo(self):
        # Pegar aquí la función completa
        # ... (el código de la función arriba) ...
-->

2. Para agregar un botón en la interfaz para acceder a esta función. Puedes añadirlo en la pestaña de configuración:
<!-- 
    def create_settings_widgets(self):
        ... código existente ...
        
        Botón para cargar datos de ejemplo
        ttk.Button(
            btn_frame,
            text="Cargar Datos de Ejemplo",
            command=self.cargar_datos_ejemplo,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)
-->

# error por resolver:
[{
	"resource": "sistema.py",
	"owner": "python",
	"code": {
		"value": "reportAttributeAccessIssue",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportAttributeAccessIssue.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 8,
	"message": "\"barcode_BarcodeDetector\" is not a known attribute of module \"cv2\"",
	"source": "Pylance",
	"startLineNumber": 37,
	"startColumn": 28,
	"endLineNumber": 37,
	"endColumn": 51,
	"origin": "extHost1"
}]
'''

# Función alternativa para decodificación de códigos de barras usando OpenCV // antes se utilizaba pyzbar
def decode_barcodes_opencv(frame):
    """
    Decodifica códigos de barras usando OpenCV en lugar de pyzbar.
    Implementa detección usando las funciones nativas de OpenCV.
    
    Args:
        frame: Imagen de OpenCV para analizar
        
    Returns:
        list: Lista de códigos de barras detectados
    """
    barcodes = []
    
    try:
        # Método 1: Usar el detector de códigos de barras de OpenCV (si está disponible)
        if hasattr(cv2, 'barcode_BarcodeDetector'):
            detector = cv2.barcode_BarcodeDetector()
            ok, decoded_info, _, _ = detector.detectAndDecode(frame)
            
            if ok and decoded_info:
                for info in decoded_info:
                    if info and info.strip():  # Solo agregar si no está vacío
                        barcodes.append(info.strip())
        
        # Método 2: Búsqueda de patrones simples (como fallback)
        if not barcodes:
            # Convertir a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Aplicar filtros para mejorar la detección
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 150)
            
            # Buscar contornos
            contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contornos que podrían ser códigos de barras (relación de aspecto)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Los códigos de barras suelen tener una relación de aspecto alta
                if aspect_ratio > 2.0 and w > 100 and h > 20:
                    # Esta es una aproximación - en una implementación real
                    # se necesitaría un algoritmo más sofisticado
                    roi = frame[y:y+h, x:x+w]
                    
                    # Aquí podrías agregar OCR básico o otros métodos
                    # Por ahora, simplemente dibujamos el rectángulo
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
    except Exception as e:
        print(f"Error en detección OpenCV: {e}")
    
    return barcodes

class InventorySalesSystem:
    """
    Sistema completo de gestión de inventario y ventas para librería.
    Incluye gestión de productos, ventas, facturación, reportes y configuración.
    
    Características principales:
    - Gestión de inventario con código de barras
    - Sistema de ventas con carrito de compras
    - Escaneo de código de barras por cámara (usando OpenCV)
    - Generación de facturas PDF
    - Reportes gráficos de ventas
    - Sistema de configuración
    """
    
    def __init__(self, root):
        """
        Inicializa el sistema de gestión de librería.
        
        Args:
            root (tk.Tk): Ventana principal de la aplicación
        """
        self.root = root
        self.root.title("Sistema de Gestión de Librería")
        self.root.geometry("1200x700")
        
        # Aplicar tema moderno
        self.style = ThemedStyle(self.root)
        try:
            self.style.set_theme("black")
        except:
            self.style.set_theme("clam")
        
        # Configuración de colores personalizados
        self.style.configure('Accent.TButton', background='#2196F3', foreground='white')
        self.style.configure('Success.TButton', background='#4CAF50', foreground='white')
        self.style.configure('Danger.TButton', background='#F44336', foreground='white')
        self.style.configure('Secondary.TButton', background='#FF9800', foreground='white')
        
        # Configuración de archivos
        self.inventory_file = "inventario.csv"
        self.sales_file = "ventas.csv"
        self.invoices_dir = "facturas"
        self.config_file = "config.json"
        self.create_data_files()
        
        # Variables de estado
        self.current_barcode = ""
        self.cart = []
        self.camera = None
        self.is_scanning = False
        self.report_canvas = None
        self._camera_photos = []  # Para almacenar referencias a imágenes de la cámara
        
        # Crear interfaz
        self.create_notebook()
        self.setup_barcode_reader()
        
        # Cargar datos existentes
        self.load_inventory_data()
        self.load_configuration()

        # Configurar sistema de logging
        self.setup_logging()

    # eliminar cargar_datos_ejemplo
    def cargar_datos_ejemplo(self):
        """
        Carga datos de ejemplo en el sistema para pruebas y demostración.
        Incluye productos de librería, ventas y configuración inicial.
        """
        try:
            # 1. Cargar productos de ejemplo en el inventario
            productos_ejemplo = [
                ['2024-01-15', '10:30:00', '9788418933013', 'El Principito', 50, 15.99, 21],
                ['2024-01-15', '10:32:00', '9788466338141', 'Cien años de soledad', 30, 22.50, 21],
                ['2024-01-15', '10:35:00', '9788498389242', 'Harry Potter y la piedra filosofal', 40, 18.75, 10.5],
                ['2024-01-15', '10:38:00', '9788433915458', '1984', 25, 16.99, 21],
                ['2024-01-15', '10:40:00', '9788408261986', 'Los pilares de la Tierra', 20, 24.99, 21],
                ['2024-01-15', '10:42:00', '9788497593795', 'El código Da Vinci', 35, 19.50, 10.5],
                ['2024-01-15', '10:45:00', '9788466337243', 'Rayuela', 15, 20.99, 21],
                ['2024-01-15', '10:48:00', '9788420471839', 'La sombra del viento', 28, 17.25, 21],
                ['2024-01-15', '10:50:00', '9788408173685', 'Juego de tronos', 22, 26.99, 21],
                ['2024-01-15', '10:52:00', '9788466337922', 'Ficciones', 18, 14.99, 0],
                ['2024-01-15', '10:55:00', '9788490628722', 'El alquimista', 45, 12.99, 10.5],
                ['2024-01-15', '10:58:00', '9788432216060', 'La casa de los espíritus', 32, 21.50, 21],
                ['2024-01-15', '11:00:00', '9788408231941', 'Patria', 27, 23.75, 21],
                ['2024-01-15', '11:02:00', '9788466348003', 'La catedral del mar', 19, 20.25, 21],
                ['2024-01-15', '11:05:00', '9788401021262', 'El nombre del viento', 23, 25.99, 21],
                ['2024-01-15', '11:08:00', '9788490664690', 'Sapiens', 38, 19.99, 10.5],
                ['2024-01-15', '11:10:00', '9788433977432', 'Crimen y castigo', 17, 18.50, 21],
                ['2024-01-15', '11:12:00', '9788466338561', 'Pedro Páramo', 29, 13.99, 0],
                ['2024-01-15', '11:15:00', '9788490323782', 'El laberinto de los espíritus', 21, 27.50, 21],
                ['2024-01-15', '11:18:00', '9788408173722', 'Choque de reyes', 26, 28.25, 21]
            ]
    
            # Escribir productos en el archivo de inventario
            with open(self.inventory_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Fecha', 'Hora', 'Código', 'Producto', 'Cantidad', 'Precio', 'IVA'])
                writer.writerows(productos_ejemplo)
    
            # 2. Cargar ventas de ejemplo
            ventas_ejemplo = [
                ['2024-01-16', '09:15:00', '202401160915001', '9788418933013', 'El Principito', 2, 15.99, 31.98, 'Juan Pérez', '12345678A', 'Efectivo', 6.72],
                ['2024-01-16', '10:30:00', '202401161030002', '9788466338141', 'Cien años de soledad', 1, 22.50, 22.50, 'María García', '87654321B', 'Tarjeta de Crédito', 4.73],
                ['2024-01-16', '11:45:00', '202401161145003', '9788498389242', 'Harry Potter y la piedra filosofal', 3, 18.75, 56.25, 'Carlos López', '11223344C', 'Transferencia', 5.91],
                ['2024-01-16', '14:20:00', '202401161420004', '9788433915458', '1984', 1, 16.99, 16.99, 'Ana Rodríguez', '44332211D', 'Efectivo', 3.57],
                ['2024-01-16', '16:35:00', '202401161635005', '9788408261986', 'Los pilares de la Tierra', 2, 24.99, 49.98, 'Pedro Martínez', '55667788E', 'Tarjeta de Débito', 10.50],
                ['2024-01-17', '09:30:00', '202401170930006', '9788497593795', 'El código Da Vinci', 1, 19.50, 19.50, 'Laura Sánchez', '99887766F', 'Efectivo', 2.05],
                ['2024-01-17', '11:15:00', '202401171115007', '9788466337243', 'Rayuela', 2, 20.99, 41.98, 'Miguel Fernández', '66778899G', 'Tarjeta de Crédito', 8.82],
                ['2024-01-17', '13:40:00', '202401171340008', '9788420471839', 'La sombra del viento', 1, 17.25, 17.25, 'Elena Gómez', '22334455H', 'Transferencia', 3.62],
                ['2024-01-17', '15:20:00', '202401171520009', '9788408173685', 'Juego de tronos', 3, 26.99, 80.97, 'David Torres', '33445566I', 'Efectivo', 17.00],
                ['2024-01-18', '10:00:00', '202401181000010', '9788466337922', 'Ficciones', 2, 14.99, 29.98, 'Sofía Ruiz', '77889900J', 'Tarjeta de Débito', 0.00],
                ['2024-01-18', '12:30:00', '202401181230011', '9788490628722', 'El alquimista', 1, 12.99, 12.99, 'Javier Díaz', '44556677K', 'Efectivo', 1.36],
                ['2024-01-18', '14:45:00', '202401181445012', '9788432216060', 'La casa de los espíritus', 2, 21.50, 43.00, 'Carmen Vargas', '11223344L', 'Tarjeta de Crédito', 9.03],
                ['2024-01-18', '17:00:00', '202401181700013', '9788408231941', 'Patria', 1, 23.75, 23.75, 'Francisco Castro', '55667788M', 'Transferencia', 4.99],
                ['2024-01-19', '09:45:00', '202401190945014', '9788466348003', 'La catedral del mar', 2, 20.25, 40.50, 'Isabel Ortega', '99887766N', 'Efectivo', 8.51],
                ['2024-01-19', '12:15:00', '202401191215015', '9788401021262', 'El nombre del viento', 1, 25.99, 25.99, 'Ricardo Mendoza', '66778899O', 'Tarjeta de Débito', 5.46],
                ['2024-01-19', '15:30:00', '202401191530016', '9788490664690', 'Sapiens', 3, 19.99, 59.97, 'Patricia Silva', '22334455P', 'Efectivo', 6.30],
                ['2024-01-19', '17:45:00', '202401191745017', '9788433977432', 'Crimen y castigo', 1, 18.50, 18.50, 'Roberto Navarro', '33445566Q', 'Tarjeta de Crédito', 3.89],
                ['2024-01-20', '10:20:00', '202401201020018', '9788466338561', 'Pedro Páramo', 2, 13.99, 27.98, 'Mónica Reyes', '77889900R', 'Transferencia', 0.00],
                ['2024-01-20', '13:10:00', '202401201310019', '9788490323782', 'El laberinto de los espíritus', 1, 27.50, 27.50, 'Gabriel Campos', '44556677S', 'Efectivo', 5.78],
                ['2024-01-20', '16:40:00', '202401201640020', '9788408173722', 'Choque de reyes', 2, 28.25, 56.50, 'Verónica Ríos', '11223344T', 'Tarjeta de Débito', 11.87]
            ]
    
            # Escribir ventas en el archivo
            with open(self.sales_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Fecha', 'Hora', 'Número de Factura', 'Código', 'Producto', 'Cantidad', 
                               'Precio Unitario', 'Total', 'Cliente', 'DNI/RUC', 'Método de Pago', 'IVA'])
                writer.writerows(ventas_ejemplo)
    
            # 3. Crear configuración de ejemplo
            config_ejemplo = {
                'company': {
                    'company_name': 'Librería Cervantes',
                    'address': 'Av. de los Libros 123, Madrid',
                    'phone': '+34 91 123 45 67',
                    'tax_id': 'B12345678',
                    'email': 'info@libreriacervantes.es'
                },
                'printing': {
                    'copies': '2',
                    'paper_format': 'A4'
                }
            }
    
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_ejemplo, f, indent=4)
    
            # 4. Crear algunas facturas de ejemplo
            facturas_ejemplo = [
                {
                    'order_number': '202401160915001',
                    'client_name': 'Juan Pérez',
                    'client_id': '12345678A',
                    'payment_method': 'Efectivo',
                    'cart': [
                        {'Código': '9788418933013', 'Producto': 'El Principito', 'Cantidad': 2, 
                         'Precio': 15.99, 'iva': 21}
                    ],
                    'subtotal': 31.98,
                    'iva_total': 6.72,
                    'total': 38.70
                },
                {
                    'order_number': '202401161030002',
                    'client_name': 'María García',
                    'client_id': '87654321B',
                    'payment_method': 'Tarjeta de Crédito',
                    'cart': [
                        {'Código': '9788466338141', 'Producto': 'Cien años de soledad', 'Cantidad': 1, 
                         'Precio': 22.50, 'iva': 21}
                    ],
                    'subtotal': 22.50,
                    'iva_total': 4.73,
                    'total': 27.23
                }
            ]
    
            for factura in facturas_ejemplo:
                pdf_file = self.generate_invoice_pdf(**factura)
    
            # 5. Actualizar las interfaces
            self.load_inventory_data()
            self.load_configuration()
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Datos de ejemplo", 
                               "Se han cargado exitosamente los datos de ejemplo:\n"
                               "- 20 productos en inventario\n"
                               "- 20 ventas de ejemplo\n"
                               "- Configuración de la librería\n"
                               "- Facturas de demostración")
            
            self.log_event("info", "Datos de ejemplo cargados exitosamente")
            
        except Exception as e:
            error_msg = f"Error al cargar datos de ejemplo: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.log_event("error", error_msg)
    # eliminar cargar_datos_ejemplo

    def setup_logging(self):
        """Configura el sistema de logging para registrar eventos"""
        logging.basicConfig(
            filename='sistema.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        logging.info("Sistema de gestión de librería iniciado")
        
    def log_event(self, level, message):
        """
        Registra un evento en el log del sistema.
        
        Args:
            level (str): Nivel del evento (info, warning, error)
            message (str): Mensaje a registrar
        """
        if level == "info":
            logging.info(message)
        elif level == "warning":
            logging.warning(message)
        elif level == "error":
            logging.error(message)
    
    def create_data_files(self):
        """
        Crea los archivos y directorios necesarios para el sistema.
        Si los archivos ya existen, no los sobrescribe.
        """
        # Crear archivo de inventario si no existe
        if not os.path.exists(self.inventory_file):
            with open(self.inventory_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Fecha', 'Hora', 'Código', 'Producto', 'Cantidad', 'Precio', 'IVA'])
        
        # Crear archivo de ventas si no existe
        if not os.path.exists(self.sales_file):
            with open(self.sales_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Fecha', 'Hora', 'Número de Factura', 'Código', 'Producto', 'Cantidad', 
                               'Precio Unitario', 'Total', 'Cliente', 'DNI/RUC', 'Método de Pago', 'IVA'])
        
        # Crear directorio de facturas si no existe
        if not os.path.exists(self.invoices_dir):
            os.makedirs(self.invoices_dir)
            
        # Crear archivo de configuración si no existe
        if not os.path.exists(self.config_file):
            default_config = {
                'company': {
                    'company_name': 'Mi Librería',
                    'address': 'Calle Principal 123',
                    'phone': '+1234567890',
                    'tax_id': '12345678901',
                    'email': 'contacto@milibreria.com'
                },
                'printing': {
                    'copies': '1',
                    'paper_format': 'A4'
                }
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
    
    def create_notebook(self):
        """
        Crea las pestañas del sistema con diseño mejorado.
        Organiza las funcionalidades en pestañas separadas.
        """
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de Ventas
        self.sales_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_tab, text="Ventas")
        self.create_sales_widgets()
        
        # Pestaña de Inventario
        self.inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_tab, text="Inventario")
        self.create_inventory_widgets()
        
        # Pestaña de Reportes
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reportes")
        self.create_reports_widgets()
        
        # Pestaña de Configuración
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Configuración")
        self.create_settings_widgets()
    
    def create_reports_widgets(self):
        """
        Crea la interfaz para el historial y reportes de ventas.
        Incluye tabla de historial y opciones para generar reportes gráficos.
        """
        main_frame = ttk.Frame(self.reports_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Tabla de historial de ventas
        history_frame = ttk.LabelFrame(main_frame, text="Historial de Ventas", padding="10")
        history_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
        # Crear Treeview para mostrar historial de ventas
        self.sales_tree = ttk.Treeview(
            history_frame,
            columns=('Fecha', 'Hora', 'Factura', 'Código', 'Producto', 'Cantidad', 
                    'Precio Unitario', 'Total', 'Cliente', 'DNI/RUC', 'Método de Pago', 'IVA'),
            show='headings',
            height=18
        )
        
        # Configurar columnas del Treeview
        columns = [
            ('Fecha', 90), ('Hora', 70), ('Factura', 100), ('Código', 100),
            ('Producto', 150), ('Cantidad', 80), ('Precio Unitario', 100),
            ('Total', 90), ('Cliente', 120), ('DNI/RUC', 100), 
            ('Método de Pago', 120), ('IVA', 60)
        ]
        
        for col, width in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=width, anchor=tk.W)
        
        self.sales_tree.pack(fill=tk.BOTH, expand=True)
    
        # Botón para recargar historial
        ttk.Button(
            history_frame,
            text="Actualizar Historial",
            command=self.load_sales_history
        ).pack(pady=5)
    
        # Sección de reportes/gráficos
        report_frame = ttk.LabelFrame(main_frame, text="Reportes Gráficos", padding="10")
        report_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
        # Botones para generar diferentes tipos de reportes
        ttk.Button(
            report_frame,
            text="Ventas por Día",
            command=self.show_sales_per_day
        ).pack(pady=5)
    
        ttk.Button(
            report_frame,
            text="Productos Más Vendidos",
            command=self.show_top_products
        ).pack(pady=5)
        
        ttk.Button(
            report_frame,
            text="Métodos de Pago",
            command=self.show_payment_methods
        ).pack(pady=5)
        
        ttk.Button(
            report_frame,
            text="Exportar Reporte",
            command=self.export_report
        ).pack(pady=5)
    
        # Cargar historial al abrir la pestaña
        self.load_sales_history()
    
    def load_sales_history(self):
        """
        Carga el historial de ventas desde el archivo CSV y lo muestra en la tabla.
        """
        # Limpiar tabla existente
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
            
        # Leer y cargar datos desde el archivo CSV
        if os.path.exists(self.sales_file):
            try:
                with open(self.sales_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader, None)  # Saltar encabezado
                    for row in reader:
                        if row:  # Asegurarse de que la fila no esté vacía
                            self.sales_tree.insert('', tk.END, values=row)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el historial: {str(e)}")
    
    def show_sales_per_day(self):
        """
        Genera y muestra un gráfico de ventas por día.
        """
        ventas_por_dia = {}
        if os.path.exists(self.sales_file):
            with open(self.sales_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if not row:
                        continue
                    fecha = row[0]
                    try:
                        total = float(row[7])
                        ventas_por_dia[fecha] = ventas_por_dia.get(fecha, 0) + total
                    except (ValueError, IndexError):
                        continue

        # Graficar con matplotlib si hay datos
        if ventas_por_dia:
            fechas = list(ventas_por_dia.keys())
            totales = list(ventas_por_dia.values())
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(fechas, totales, color='skyblue')
            ax.set_title("Ventas por Día")
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Total ($)")
            plt.xticks(rotation=45)
            plt.tight_layout()

            self.show_report_figure(fig)
        else:
            messagebox.showinfo("Información", "No hay datos de ventas para mostrar.")
    
    def show_top_products(self):
        """
        Genera y muestra un gráfico de los productos más vendidos.
        """
        productos = {}
        if os.path.exists(self.sales_file):
            with open(self.sales_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if not row:
                        continue
                    try:
                        producto = row[4]
                        cantidad = int(row[5])
                        productos[producto] = productos.get(producto, 0) + cantidad
                    except (ValueError, IndexError):
                        continue

        # Graficar con matplotlib si hay datos
        if productos:
            # Obtener los 10 productos más vendidos
            top = sorted(productos.items(), key=lambda x: x[1], reverse=True)[:10]
            nombres = [x[0] for x in top]
            cantidades = [x[1] for x in top]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(nombres, cantidades, color='orange')
            ax.set_title("Top 10 Productos Más Vendidos")
            ax.set_xlabel("Cantidad Vendida")
            plt.tight_layout()

            self.show_report_figure(fig)
        else:
            messagebox.showinfo("Información", "No hay datos de productos para mostrar.")
    
    def show_payment_methods(self):
        """
        Genera y muestra un gráfico de torta de métodos de pago utilizados.
        """
        metodos_pago = {}
        if os.path.exists(self.sales_file):
            with open(self.sales_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if not row or len(row) < 11:
                        continue
                    try:
                        metodo = row[10]
                        total = float(row[7])
                        metodos_pago[metodo] = metodos_pago.get(metodo, 0) + total
                    except (ValueError, IndexError):
                        continue

        if metodos_pago:
            métodos = list(metodos_pago.keys())
            montos = list(metodos_pago.values())
            
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(montos, labels=métodos, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            ax.set_title("Distribución de Métodos de Pago")

            self.show_report_figure(fig)
        else:
            messagebox.showinfo("Información", "No hay datos de métodos de pago para mostrar.")
    
    def export_report(self):
        """
        Exporta el reporte actual a un archivo CSV o PDF.
        """
        # Diálogo para seleccionar ubicación y tipo de archivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        if file_path.endswith('.csv'):
            self.export_csv_report(file_path)
        elif file_path.endswith('.pdf'):
            self.export_pdf_report(file_path)
        else:
            messagebox.showwarning("Formato no compatible", "Por favor seleccione formato CSV o PDF.")
    
    def export_csv_report(self, file_path):
        """
        Exporta el reporte a formato CSV.
        
        Args:
            file_path (str): Ruta del archio donde guardar el reporte
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Escribir encabezados
                writer.writerow(['Fecha', 'Hora', 'Factura', 'Código', 'Producto', 'Cantidad', 
                               'Precio Unitario', 'Total', 'Cliente', 'DNI/RUC', 'Método de Pago', 'IVA'])
                
                # Escribir datos
                for item in self.sales_tree.get_children():
                    values = self.sales_tree.item(item, 'values')
                    writer.writerow(values)
                    
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente a {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte: {str(e)}")
    
    def export_pdf_report(self, file_path):
        """
        Exporta el reporte a formato PDF.
        
        Args:
            file_path (str): Ruta del archivo donde guardar el reporte
        """
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            
            # Encabezado del reporte
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Reporte de Ventas")
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"Fecha de generación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Datos del reporte
            y_position = height - 100
            for item in self.sales_tree.get_children():
                if y_position < 100:  # Nueva página si es necesario
                    c.showPage()
                    y_position = height - 50
                    
                values = self.sales_tree.item(item, 'values')
                if values and len(values) >= 8:
                    texto = f"{values[0]} {values[1]} - {values[4]} - Cant: {values[5]} - Total: ${values[7]}"
                    c.drawString(50, y_position, texto)
                    y_position -= 15
            
            c.save()
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente a {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte: {str(e)}")
    
    def show_report_figure(self, fig):
        """
        Muestra una figura de matplotlib en la pestaña de reportes.
        
        Args:
            fig (matplotlib.figure.Figure): Figura a mostrar
        """
        # Limpiar canvas anterior si existe
        if self.report_canvas:
            self.report_canvas.get_tk_widget().destroy()
            
        # Crear nuevo canvas para la figura
        self.report_canvas = FigureCanvasTkAgg(fig, master=self.reports_tab)
        self.report_canvas.draw()
        self.report_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
    def create_inventory_widgets(self):
        """
        Crea la interfaz de gestión de inventario.
        Incluye formulario de registro y tabla de visualización.
        """
        main_frame = ttk.Frame(self.inventory_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sección de entrada
        input_frame = ttk.LabelFrame(main_frame, text="Registro de Productos", padding="10")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # Entrada para códigos de barras
        ttk.Label(input_frame, text="Código de barras:").pack(anchor=tk.W)
        self.barcode_entry = ttk.Entry(input_frame)
        self.barcode_entry.pack(fill=tk.X)
        self.barcode_entry.focus()
        
        # Botón para simular escaneo
        ttk.Button(
            input_frame,
            text="Simular Escaneo",
            command=self.simulate_barcode_scan,
            style='Secondary.TButton'
        ).pack(pady=5)
        
        # Campos de entrada del formulario
        fields = [
            ("Nombre del Producto:", "product_name"),
            ("Cantidad en Stock:", "quantity", "spinbox"),
            ("Precio Unitario:", "price"),
            ("IVA (%):", "iva", "combobox")
        ]

        self.inventory_entries = {}
        for field in fields:
            frame = ttk.Frame(input_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=field[0]).pack(side=tk.LEFT, padx=(0, 10))
            
            if len(field) > 2 and field[2] == "spinbox":
                entry = ttk.Spinbox(frame, from_=0, to=10000, width=10)
            elif len(field) > 2 and field[2] == "combobox":
                entry = ttk.Combobox(frame, values=["0", "10.5", "21"], width=8, state="readonly")
                entry.set("21")  # Valor por defecto
            else:
                entry = ttk.Entry(frame, width=30)
                
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.inventory_entries[field[1]] = entry

        # Botones de acción
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Eliminar Producto",
            command=self.delete_selected_product,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(
            btn_frame,
            text="Guardar Producto",
            command=self.save_product,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Limpiar Campos",
            command=self.clear_inventory_fields
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            btn_frame,
            text="Actualizar Inventario",
            command=self.load_inventory_data
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Sección de visualización
        display_frame = ttk.LabelFrame(main_frame, text="Inventario Actual", padding="10")
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de búsqueda
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(display_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, padx=5, pady=(0, 8))
        search_entry.insert(0, "Buscar por nombre o código...")
        
        # Vincular evento de búsqueda
        self.search_var.trace('w', self.search_inventory)
        
        # Treeview para mostrar inventario
        self.inventory_tree = ttk.Treeview(
            display_frame,
            columns=('Fecha', 'Hora', 'Código', 'Producto', 'Cantidad', 'Precio', 'IVA'),
            show='headings',
            height=15
        )
        
        # Configurar columnas
        columns = [
            ('Fecha', 90),
            ('Hora', 70),
            ('Código', 120),
            ('Producto', 150),
            ('Cantidad', 80),
            ('Precio', 90),
            ('IVA', 60)
        ]
        
        for col, width in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=width, anchor=tk.W)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Vincular evento de selección
        self.inventory_tree.bind('<<TreeviewSelect>>', self.on_inventory_select)

    def on_inventory_select(self, event):
        """
        Maneja la selección de un producto en la tabla de inventario.
        Carga los datos del producto seleccionado en el formulario.
        
        Args:
            event: Evento de selección
        """
        selected = self.inventory_tree.selection()
        if not selected:
            return
            
        item = self.inventory_tree.item(selected[0])
        values = item['values']
        
        # Rellenar los campos de entrada con los valores seleccionados
        self.barcode_entry.delete(0, tk.END)
        self.barcode_entry.insert(0, values[2])
        
        self.inventory_entries['product_name'].delete(0, tk.END)
        self.inventory_entries['product_name'].insert(0, values[3])
        
        self.inventory_entries['quantity'].delete(0, tk.END)
        self.inventory_entries['quantity'].insert(0, values[4])
        
        self.inventory_entries['price'].delete(0, tk.END)
        self.inventory_entries['price'].insert(0, values[5])
        
        self.inventory_entries['iva'].set(values[6])
    
    def save_product(self):
        """
        Guarda un nuevo producto en el inventario o actualiza uno existente.
        Realiza validaciones de datos antes de guardar.
        """
        # Obtener valores de los campos
        barcode = self.barcode_entry.get().strip()
        product_name = self.inventory_entries["product_name"].get().strip()
        quantity = self.inventory_entries["quantity"].get().strip()
        price = self.inventory_entries["price"].get().strip()
        iva = self.inventory_entries["iva"].get().strip()

        # Validaciones
        if not barcode:
            messagebox.showwarning("Advertencia", "Ingrese un código de barras")
            return

        if not product_name:
            messagebox.showwarning("Advertencia", "Ingrese el nombre del producto")
            return

        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Advertencia", "Ingrese una cantidad válida")
            return

        try:
            price = float(price)
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Advertencia", "Ingrese un precio válido")
            return

        try:
            iva = float(iva) 
            if iva not in (0, 10.5, 21):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Advertencia", "Seleccione una tasa de IVA válida (0, 10.5 o 21)")
            return

        # Leer inventario actual y verificar si el código ya existe
        productos = []
        codigo_ya_existe = False
        campos = ['Fecha', 'Hora', 'Código', 'Producto', 'Cantidad', 'Precio', 'IVA']  

        if os.path.exists(self.inventory_file):
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    productos.append(row)
                    if row['Código'] == barcode:
                        codigo_ya_existe = True

        # Si el código ya existe, preguntar si se desea actualizar
        if codigo_ya_existe:
            respuesta = messagebox.askyesno(
                "Producto existente",
                "El código de barras ya existe. ¿Deseas actualizar los datos del producto?"
            )
            if not respuesta:
                return
                
            # Actualizar producto existente
            for prod in productos:
                if prod['Código'] == barcode:
                    prod['Producto'] = product_name
                    prod['Cantidad'] = quantity
                    prod['Precio'] = price
                    prod['IVA'] = iva  
                    
            # Guardar el inventario actualizado
            with open(self.inventory_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(productos)
                
            self.load_inventory_data()
            self.clear_inventory_fields()
            messagebox.showinfo("Actualizado", "Producto actualizado correctamente")
            return

        # Si no existe, guardar como nuevo producto
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        try:
            with open(self.inventory_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([date_str, time_str, barcode, product_name, quantity, price, iva])  

            self.inventory_tree.insert('', tk.END, values=(date_str, time_str, barcode, product_name, quantity, price, iva))  
            self.clear_inventory_fields()
            messagebox.showinfo("Éxito", "Producto registrado correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el producto: {e}")
    
    def clear_inventory_fields(self):
        """
        Limpia todos los campos del formulario de inventario.
        """
        self.barcode_entry.delete(0, tk.END)
        self.current_barcode = ""
        
        self.inventory_entries["product_name"].delete(0, tk.END)
        self.inventory_entries["quantity"].delete(0, tk.END)
        self.inventory_entries["quantity"].insert(0, "0")
        self.inventory_entries["price"].delete(0, tk.END)
        self.inventory_entries["price"].insert(0, "0.00")
        self.inventory_entries["iva"].set("21")
        
        self.barcode_entry.focus()
    
    def delete_selected_product(self):
        """
        Elimina el producto seleccionado del inventario.
        Solicita confirmación antes de eliminar.
        """
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona un producto", "Selecciona un producto para eliminar.")
            return
            
        # Confirmar eliminación
        resp = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este producto?")
        if not resp:
            return
            
        # Obtener código del producto a eliminar
        codigo = self.inventory_tree.item(selected[0])['values'][2]
        
        # Leer todos los productos y filtrar el que se va a eliminar
        productos = []
        campos = ['Fecha', 'Hora', 'Código', 'Producto', 'Cantidad', 'Precio', 'IVA']
        
        with open(self.inventory_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Código'] != codigo:
                    productos.append(row)
                    
        # Escribir archivo sin el producto eliminado
        with open(self.inventory_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(productos)
            
        self.load_inventory_data()
        self.clear_inventory_fields()
        messagebox.showinfo("Eliminado", "Producto eliminado correctamente.")
    
    def load_inventory_data(self):
        """
        Carga los datos del inventario desde el archivo CSV.
        """
        # Limpiar la tabla
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
    
        # Leer y cargar los datos
        if os.path.exists(self.inventory_file):
            try:
                with open(self.inventory_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.inventory_tree.insert('', tk.END, values=(
                            row['Fecha'], row['Hora'], row['Código'],
                            row['Producto'], row['Cantidad'], row['Precio'], row.get('IVA', '21')
                        ))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(e)}")
    
    def search_inventory(self, *args):
        """
        Busca productos en el inventario según el texto ingresado.
        Filtra por código o nombre de producto.
        
        Args:
            *args: Argumentos del evento de trace
        """
        filtro = self.search_var.get().strip().lower()
        
        # Limpiar la tabla
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
            
        # Leer y mostrar solo los productos que coincidan
        if os.path.exists(self.inventory_file):
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if (filtro in row['Producto'].lower()) or (filtro in row['Código'].lower()):
                        self.inventory_tree.insert('', tk.END, values=(
                            row['Fecha'], row['Hora'], row['Código'],
                            row['Producto'], row['Cantidad'], row['Precio'], row.get('IVA', '21')
                        ))
    
    def create_sales_widgets(self):
        """
        Crea la interfaz mejorada para el módulo de ventas.
        Incluye sección de cliente, escaneo y carrito de compras.
        """
        main_frame = ttk.Frame(self.sales_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        
        # Sección de cliente
        client_frame = ttk.LabelFrame(left_panel, text="Información del Cliente", padding="10")
        client_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(client_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=2)
        self.client_name_entry = ttk.Entry(client_frame)
        self.client_name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(client_frame, text="DNI/RUC:").grid(row=1, column=0, padx=5, pady=2)
        self.client_id_entry = ttk.Entry(client_frame)
        self.client_id_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Sección de escaneo
        scan_frame = ttk.LabelFrame(left_panel, text="Escaneo de Código de Barras", padding="10")
        scan_frame.pack(fill=tk.X, pady=5)
        
        self.camera_canvas = tk.Canvas(scan_frame, width=320, height=240)
        self.camera_canvas.pack()
        
        btn_frame = ttk.Frame(scan_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            btn_frame,
            text="Iniciar Cámara",
            command=self.toggle_camera,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Entrada Manual",
            command=self.manual_barcode_entry
        ).pack(side=tk.LEFT)
        
        # Panel derecho (carrito y total)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Carrito mejorado
        cart_frame = ttk.LabelFrame(right_panel, text="Carrito de Compras", padding="10")
        cart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview con scroll
        tree_frame = ttk.Frame(cart_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cart_tree = ttk.Treeview(
            tree_frame,
            columns=('Código', 'Producto', 'Cantidad', 'Precio', 'Total', 'IVA'),
            show='headings',
            height=10
        )
        
        # Configurar columnas
        columns = [
            ('Código', 100),
            ('Producto', 200),
            ('Cantidad', 80),
            ('Precio', 90),
            ('Total', 90),
            ('IVA', 60)
        ]
        
        for col, width in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=width)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.cart_tree.xview)
        self.cart_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid layout para scrollbars
        self.cart_tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Sección de totales y pago
        totals_frame = ttk.LabelFrame(right_panel, text="Resumen de Venta", padding="10")
        totals_frame.pack(fill=tk.X, pady=5)
        
        # Método de pago
        payment_frame = ttk.Frame(totals_frame)
        payment_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(payment_frame, text="Método de Pago:").pack(side=tk.LEFT)
        self.payment_method = ttk.Combobox(
            payment_frame, 
            values=['Efectivo', 'Tarjeta de Crédito', 'Tarjeta de Débito', 'Transferencia'],
            state='readonly'
        )
        self.payment_method.set('Efectivo')
        self.payment_method.pack(side=tk.LEFT, padx=5)
        
        # Total
        self.subtotal_label = ttk.Label(totals_frame, text="Subtotal: $0.00", font=('Arial', 11))
        self.subtotal_label.pack(fill=tk.X)
        
        self.tax_label = ttk.Label(totals_frame, text="IVA: $0.00", font=('Arial', 11))
        self.tax_label.pack(fill=tk.X)
        
        self.total_label = ttk.Label(
            totals_frame, 
            text="Total: $0.00", 
            font=('Arial', 12, 'bold')
        )
        self.total_label.pack(fill=tk.X)
        
        # Botones de acción
        button_frame = ttk.Frame(right_panel)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="Finalizar Venta",
            command=self.finalize_sale,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancelar Venta",
            command=self.clear_sale,
            style='Danger.TButton'
        ).pack(side=tk.LEFT)
    
    def setup_barcode_reader(self):
        """
        Configura la captura de códigos de barras desde teclado.
        """
        self.root.bind('<Key>', self.process_barcode_input)
    
    def simulate_barcode_scan(self):
        """
        Simula el escaneo de un código de barras (para pruebas).
        """
        barcode = self.barcode_entry.get()
        if barcode:
            self.current_barcode = barcode
            self.process_barcode_input(tk.EventType.KeyPress)
    
    def manual_barcode_entry(self):
        """
        Permite ingresar un código de barras manualmente.
        """
        barcode = simpledialog.askstring("Entrada manual", "Ingrese el código de barras:")
        if barcode:
            self.current_barcode = barcode
            # Simula el evento de presionar Enter para procesar el código
            event = type('Event', (object,), {'keysym': 'Return'})()
            self.process_barcode_input(event)
    
    def process_barcode_input(self, event):
        """
        Procesa la entrada del lector de códigos de barras.
        
        Args:
            event: Evento de teclado
        """
        current_tab = self.notebook.index(self.notebook.select())
        
        # Solo procesar si es una tecla visible o Enter
        if event.keysym == 'Return':
            if self.current_barcode:
                if current_tab == 0:  # Pestaña de ventas
                    self.add_to_cart(self.current_barcode)
                    self.client_name_entry.delete(0, tk.END)
                    self.client_id_entry.delete(0, tk.END)
                elif current_tab == 1:  # Pestaña de inventario
                    self.barcode_entry.delete(0, tk.END)
                    self.barcode_entry.insert(0, self.current_barcode)
                    self.inventory_entries["product_name"].focus()
                
                self.current_barcode = ""
        elif len(event.keysym) == 1:  # Caracteres normales
            self.current_barcode += event.keysym
    
    def toggle_camera(self):
        """Activa o desactiva la cámara para escaneo de códigos de barras."""
        if self.is_scanning:
            self.is_scanning = False
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                self.log_event("info", "Cámara desactivada")
        else:
            try:
                self.camera = cv2.VideoCapture(0)
                if not self.camera.isOpened():
                    messagebox.showerror("Error", "No se puede acceder a la cámara")
                    self.log_event("error", "No se puede acceder a la cámara")
                    return

                self.is_scanning = True
                self.log_event("info", "Cámara activada")
                self.update_camera()
            except Exception as e:
                messagebox.showerror("Error", f"Error al acceder a la cámara: {str(e)}")
                self.log_event("error", f"Error al acceder a la cámara: {str(e)}")
    
    def update_camera(self):
        """
        Actualiza la vista de la cámara y detecta códigos de barras usando OpenCV.
        """
        if self.is_scanning and self.camera is not None:
            ret, frame = self.camera.read()
            if ret:
                # Usar OpenCV para detección de códigos de barras
                decoded_objects = decode_barcodes_opencv(frame)
                
                # Dibujar rectángulo de enfoque (para visualización)
                h, w = frame.shape[:2]
                cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 2)
                
                # Procesar códigos detectados
                for barcode in decoded_objects:
                    self.process_scanned_barcode(barcode)
                
                # Convertir frame para mostrar en tkinter
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (320, 240))
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                
                self.camera_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                
                # Mantener referencia para evitar garbage collection
                self._camera_photos.append(photo)
                
                # Limitar el número de referencias guardadas
                if len(self._camera_photos) > 5:
                    self._camera_photos.pop(0)
            
            # Programar próxima actualización
            self.root.after(10, self.update_camera)
    
    def process_scanned_barcode(self, barcode):
        """
        Procesa el código de barras escaneado por la cámara.
        
        Args:
            barcode (str): Código de barras escaneado
        """
        if barcode and barcode != self.current_barcode:
            self.current_barcode = barcode
            self.add_to_cart(barcode)
    
    def add_to_cart(self, barcode):
        """
        Añade un producto al carrito de compras.
        Verifica disponibilidad de stock.
        
        Args:
            barcode (str): Código de barras del producto a añadir
        """
        # Buscar producto en el inventario
        producto_encontrado = None
        with open(self.inventory_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Código'] == barcode:
                    producto_encontrado = row
                    break

        if not producto_encontrado:
            messagebox.showwarning("No encontrado", "Producto no encontrado en el inventario.")
            return

        # Verificar stock disponible
        stock_disponible = int(producto_encontrado['Cantidad'])

        # Verificar si ya está en el carrito
        for item in self.cart:
            if item['Código'] == barcode:
                if item['Cantidad'] + 1 > stock_disponible:
                    messagebox.showwarning("Sin stock", "No hay suficiente stock para agregar otro.")
                    return
                item['Cantidad'] += 1
                break
        else:
            # Producto nuevo en el carrito
            if stock_disponible < 1:
                messagebox.showwarning("Sin stock", "No hay stock disponible para este producto.")
                return
                
            # Añadir nuevo producto al carrito
            self.cart.append({
                'Código': barcode,
                'Producto': producto_encontrado['Producto'],
                'Cantidad': 1,
                'Precio': float(producto_encontrado['Precio']),
                'iva': float(producto_encontrado.get('IVA', 21))
            })

        self.update_cart_tree()
    
    def update_cart_tree(self):
        """
        Actualiza la visualización del carrito de compras.
        """
        # Limpiar treeview
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Añadir items del carrito
        for item in self.cart:
            total = item['Precio'] * item['Cantidad']
            iva_monto = total * (item['iva'] / 100)
            self.cart_tree.insert('', tk.END, values=(
                item['Código'],
                item['Producto'],
                item['Cantidad'],
                f"${item['Precio']:.2f}",
                f"${total:.2f}",
                f"{item['iva']}%"
            ))
        
        # Actualizar totales
        self.update_totals()
    
    def update_totals(self):
        """
        Calcula y actualiza los totales de la venta.
        """
        subtotal = sum(item['Precio'] * item['Cantidad'] for item in self.cart)
        iva_total = sum((item['Precio'] * item['Cantidad']) * (item['iva']/100) for item in self.cart)
        total = subtotal + iva_total
    
        self.subtotal_label.config(text=f"Subtotal: ${subtotal:.2f}")
        self.tax_label.config(text=f"IVA: ${iva_total:.2f}")
        self.total_label.config(text=f"Total: ${total:.2f}")
    
    def finalize_sale(self):
        """
        Finaliza la venta, guarda los datos y genera factura.
        """
        # Validación de datos del cliente
        nombre = self.client_name_entry.get().strip()
        dni = self.client_id_entry.get().strip()
    
        # Validar nombre
        if not nombre or len(nombre) < 3:
            messagebox.showwarning("Datos incompletos", "Ingrese un nombre de cliente válido (al menos 3 caracteres).")
            return
    
        # Validar DNI
        if not dni or not dni.isdigit() or len(dni) < 7:
            messagebox.showwarning("Datos incompletos", "Ingrese un DNI/RUC válido (solo números, al menos 7 dígitos).")
            return
    
        # Validar carrito
        if not self.cart:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
    
        client_name = nombre
        client_id = dni
        payment_method = self.payment_method.get()
        now = datetime.datetime.now()
        order_number = now.strftime("%Y%m%d%H%M%S")
    
        try:
            # Guardar venta en archivo CSV
            with open(self.sales_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for item in self.cart:
                    total_item = item['Precio'] * item['Cantidad']
                    iva_item = total_item * (item['iva'] / 100)
                    
                    writer.writerow([
                        now.strftime("%Y-%m-%d"),
                        now.strftime("%H:%M:%S"),
                        order_number,
                        item['Código'],
                        item['Producto'],
                        item['Cantidad'],
                        f"{item['Precio']:.2f}",
                        f"{total_item:.2f}",
                        client_name,
                        client_id,
                        payment_method,
                        f"{iva_item:.2f}"
                    ])
            
            # Calcular subtotal, IVA y total
            subtotal = sum(item['Precio'] * item['Cantidad'] for item in self.cart)
            iva_total = sum((item['Precio'] * item['Cantidad']) * (item['iva']/100) for item in self.cart)
            total = subtotal + iva_total
        
            # Generar la factura en PDF
            pdf_file = self.generate_invoice_pdf(
                order_number=order_number,
                client_name=client_name,
                client_id=client_id,
                payment_method=payment_method,
                cart=self.cart,
                subtotal=subtotal,
                iva_total=iva_total,
                total=total
            )
        
            messagebox.showinfo("Éxito", f"Venta registrada\nNúmero de pedido: {order_number}\nFactura PDF generada:\n{pdf_file}")

            self.update_inventory_after_sale()
            self.clear_sale()
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la venta: {str(e)}")

    
    def update_inventory_after_sale(self):
        """Actualiza el inventario después de una venta."""
        try:
            # Leer inventario actual
            productos = []
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    productos.append(row)

            # Actualizar stock
            for item in self.cart:
                for producto in productos:
                    if producto['Código'] == item['Código']:
                        nuevo_stock = int(producto['Cantidad']) - item['Cantidad']
                        producto['Cantidad'] = max(0, nuevo_stock)  # No permitir stock negativo

            # Guardar inventario actualizado
            campos = ['Fecha', 'Hora', 'Código', 'Producto', 'Cantidad', 'Precio', 'IVA']
            with open(self.inventory_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(productos)

            self.log_event("info", f"Inventario actualizado después de la venta")

        except Exception as e:
            self.log_event("error", f"Error al actualizar inventario: {str(e)}")
            messagebox.showerror("Error", f"No se pudo actualizar el inventario: {str(e)}")

    def generate_invoice_pdf(self, order_number, client_name, client_id, payment_method, cart, subtotal, iva_total, total):
        """
        Genera una factura en PDF con los detalles de la venta.
        
        Args:
            order_number (str): Número de orden/factura
            client_name (str): Nombre del cliente
            client_id (str): DNI/RUC del cliente
            payment_method (str): Método de pago
            cart (list): Lista de productos en el carrito
            subtotal (float): Subtotal de la venta
            iva_total (float): Total de IVA
            total (float): Total de la venta
            
        Returns:
            str: Ruta del archivo PDF generado
        """
        now = datetime.datetime.now()
        filename = os.path.join(
            self.invoices_dir,
            f"Factura_{order_number}.pdf"
        )
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Factura")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Fecha: {now.strftime('%Y-%m-%d')}")
        c.drawString(200, height - 70, f"Hora: {now.strftime('%H:%M:%S')}")
        c.drawString(400, height - 70, f"N° Factura: {order_number}")

        # Datos del cliente
        c.drawString(50, height - 100, f"Cliente: {client_name}")
        c.drawString(300, height - 100, f"DNI/RUC: {client_id}")
        c.drawString(50, height - 115, f"Método de Pago: {payment_method}")

        # Tabla de productos
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 145, "Producto")
        c.drawString(220, height - 145, "Cantidad")
        c.drawString(280, height - 145, "P. Unitario")
        c.drawString(370, height - 145, "IVA %")
        c.drawString(420, height - 145, "Total")

        c.setFont("Helvetica", 10)
        y = height - 160
        for item in cart:
            c.drawString(50, y, str(item['Producto']))
            c.drawString(220, y, str(item['Cantidad']))
            c.drawString(280, y, f"${item['Precio']:.2f}")
            c.drawString(370, y, f"{item['iva']:.2f}%")
            c.drawString(420, y, f"${item['Precio'] * item['Cantidad']:.2f}")
            y -= 15
            if y < 80:  # Salto de página si es necesario
                c.showPage()
                y = height - 50

        # Subtotal, IVA y Total
        c.setFont("Helvetica", 10)
        c.drawString(320, y - 10, "Subtotal:")
        c.drawString(420, y - 10, f"${subtotal:.2f}")
        c.drawString(320, y - 25, "IVA:")
        c.drawString(420, y - 25, f"${iva_total:.2f}")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(320, y - 40, "TOTAL:")
        c.drawString(420, y - 40, f"${total:.2f}")

        c.save()
        return filename
    
    def clear_sale(self):
        """
        Limpia el carrito y los campos de la venta actual.
        """
        if self.cart:  # Solo pedir confirmación si hay algo en el carrito
            resp = messagebox.askyesno(
                "Cancelar venta",
                "¿Estás seguro de que deseas cancelar la venta actual? Se perderán los productos agregados al carrito."
            )
            if not resp:
                return
                
        # Limpia el carrito y los campos del cliente
        self.cart.clear()
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        self.client_name_entry.delete(0, tk.END)
        self.client_id_entry.delete(0, tk.END)
        self.payment_method.set('Efectivo')
        self.update_totals()
        self.barcode_entry.focus()
    
    def create_settings_widgets(self):
        """
        Crea la interfaz para la pestaña de configuración.
        Permite configurar datos de la empresa y preferencias.
        """
        main_frame = ttk.Frame(self.settings_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuración de la empresa
        company_frame = ttk.LabelFrame(main_frame, text="Datos de la Empresa", padding="10")
        company_frame.pack(fill=tk.X, pady=5)
        
        settings = [
            ("Nombre de la Empresa:", "company_name"),
            ("Dirección:", "address"),
            ("Teléfono:", "phone"),
            ("RUC:", "tax_id"),
            ("Email:", "email")
        ]
        
        self.settings_entries = {}
        for text, key in settings:
            frame = ttk.Frame(company_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=text, width=20).pack(side=tk.LEFT)
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.settings_entries[key] = entry
        
        # Configuración de impresión
        print_frame = ttk.LabelFrame(main_frame, text="Configuración de Impresión", padding="10")
        print_frame.pack(fill=tk.X, pady=5)
        
        # Copias de factura
        copies_frame = ttk.Frame(print_frame)
        copies_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(copies_frame, text="Copias de factura:", width=20).pack(side=tk.LEFT)
        self.invoice_copies = ttk.Spinbox(copies_frame, from_=1, to=3, width=5)
        self.invoice_copies.pack(side=tk.LEFT)
        
        # Formato de papel
        paper_frame = ttk.Frame(print_frame)
        paper_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(paper_frame, text="Formato de papel:", width=20).pack(side=tk.LEFT)
        self.paper_format = ttk.Combobox(
            paper_frame,
            values=['A4', 'Letter', 'Ticket'],
            state='readonly'
        )
        self.paper_format.set('A4')
        self.paper_format.pack(side=tk.LEFT)
        
        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Guardar Configuración",
            command=self.save_settings,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Restaurar Valores Predeterminados",
            command=self.restore_default_settings
        ).pack(side=tk.LEFT)

        # Botón para cargar datos de ejemplo
        ttk.Button(
            btn_frame,
            text="Cargar Datos de Ejemplo",
            command=self.cargar_datos_ejemplo,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        # Cargar configuración actual
        self.load_configuration()
    
    def load_configuration(self):
        """
        Carga la configuración desde el archivo JSON.
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Cargar datos de la empresa
                company_data = config.get('company', {})
                for key, entry in self.settings_entries.items():
                    if key in company_data:
                        entry.delete(0, tk.END)
                        entry.insert(0, company_data[key])
                
                # Cargar configuración de impresión
                printing_data = config.get('printing', {})
                if 'copies' in printing_data:
                    self.invoice_copies.delete(0, tk.END)
                    self.invoice_copies.insert(0, printing_data['copies'])
                if 'paper_format' in printing_data:
                    self.paper_format.set(printing_data['paper_format'])
                    
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la configuración: {str(e)}")
    
    def save_settings(self):
        """
        Guarda la configuración en un archivo JSON.
        """
        settings = {
            'company': {key: entry.get() for key, entry in self.settings_entries.items()},
            'printing': {
                'copies': self.invoice_copies.get(),
                'paper_format': self.paper_format.get()
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {str(e)}")
    
    def restore_default_settings(self):
        """
        Restaura la configuración por defecto.
        """
        default_settings = {
            'company_name': 'Mi Librería',
            'address': 'Calle Principal #123',
            'phone': '(123) 456-7890',
            'tax_id': '12345678-9',
            'email': 'contacto@milibreria.com'
        }
        
        for key, value in default_settings.items():
            if key in self.settings_entries:
                self.settings_entries[key].delete(0, tk.END)
                self.settings_entries[key].insert(0, value)
        
        self.invoice_copies.delete(0, tk.END)
        self.invoice_copies.insert(0, "1")
        self.paper_format.set('A4')

    def check_dependencies(self):
        """
        Verifica que todas las dependencias estén instaladas correctamente.
        """
        missing_deps = []

        try:
            from ttkthemes import ThemedStyle
        except ImportError:
            missing_deps.append("ttkthemes")

        try:
            from reportlab.pdfgen import canvas
        except ImportError:
            missing_deps.append("reportlab")

        try:
            import cv2
        except ImportError:
            missing_deps.append("opencv-python")

        try:
            from PIL import Image, ImageTk
        except ImportError:
            missing_deps.append("Pillow")

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            missing_deps.append("matplotlib")

        if missing_deps:
            messagebox.showerror(
                "Dependencias faltantes", 
                f"Las siguientes dependencias no están instaladas:\n{', '.join(missing_deps)}\n\n"
                f"Por favor, ejecute: pip install {' '.join(missing_deps)}"
            )
            return False
        return True
    
    def setup_directories(self):
        """
        Configura todos los directorios necesarios para el sistema.
        """
        directories = ["facturas", "backups", "backups/inventario", "backups/ventas", "logs"]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        print("Directorios configurados correctamente")

if __name__ == "__main__":
    # Verificar dependencias
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal temporalmente
    
    app = InventorySalesSystem(root)
    
    if not app.check_dependencies():
        root.destroy()
        exit(1)
        
    app.setup_directories()
    
    # Configurar icono de la aplicación
    try:
        root.iconbitmap("icon.ico")  # Intenta cargar un icono si existe
        # if os.path.exists("icons/logo.ico"):
            # root.iconbitmap("icons/logo.ico")
    except:
        pass  # Si no hay icono, continuar sin él
    
    root.deiconify()  # Mostrar ventana principal
    
    # Estilo moderno
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Accent.TButton', foreground='white', background='#4CAF50')
    style.configure('Success.TButton', foreground='white', background='#2196F3')
    style.configure('Danger.TButton', foreground='white', background='#F44336')
    style.configure('Secondary.TButton', foreground='white', background='#FF9800')
    
    root.mainloop()