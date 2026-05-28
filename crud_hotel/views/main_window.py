from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PyQt6.QtCore import Qt

from views.recepcion_view import RecepcionView
from views.servicio_view import ServicioView
from views.admin_view import AdminView


# ==========================================
# VENTANA PRINCIPAL (CONTENEDOR)
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión Hotelera")
        self.resize(1000, 600)
        
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Widget Central que contendrá el Sidebar y el StackedWidget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ------------------------------------
        # 1. PANEL LATERAL (SIDEBAR)
        # ------------------------------------
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("Sidebar")
        sidebar_frame.setFixedWidth(250)
        
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(15)

        # Título del menú
        lbl_menu = QLabel("ROLES")
        lbl_menu.setObjectName("MenuTitle")
        lbl_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(lbl_menu)

        # Botones de navegación
        self.btn_recepcion = QPushButton("🧑‍💼 Recepción")
        self.btn_servicio = QPushButton("🧹 Servicio / Manten.")
        self.btn_admin = QPushButton("📊 Administración")

        # Configurar cursores
        self.btn_recepcion.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_servicio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_admin.setCursor(Qt.CursorShape.PointingHandCursor)

        sidebar_layout.addWidget(self.btn_recepcion)
        sidebar_layout.addWidget(self.btn_servicio)
        sidebar_layout.addWidget(self.btn_admin)
        sidebar_layout.addStretch() # Empuja los botones hacia arriba

        # ------------------------------------
        # 2. ÁREA CENTRAL (QStackedWidget)
        # ------------------------------------
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("CentralArea")
        
        # Instanciar vistas
        self.view_recepcion = RecepcionView()
        self.view_servicio = ServicioView()
        self.view_admin = AdminView()
        
        # Añadir al stacked widget
        self.stacked_widget.addWidget(self.view_recepcion)
        self.stacked_widget.addWidget(self.view_servicio)
        self.stacked_widget.addWidget(self.view_admin)

        # Añadir Sidebar y StackedWidget al layout principal
        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(self.stacked_widget)

        # ------------------------------------
        # 3. INTERCONEXIÓN DE SEÑALES (ROUTING)
        # ------------------------------------
        self.btn_recepcion.clicked.connect(lambda: self.switch_view(0))
        self.btn_servicio.clicked.connect(lambda: self.switch_view(1))
        self.btn_admin.clicked.connect(lambda: self.switch_view(2))

    def switch_view(self, index: int):
        """Cambia el widget visible en el panel central."""
        self.stacked_widget.setCurrentIndex(index)

    def apply_styles(self):
        """Aplica estilos CSS para darle un look moderno y limpio."""
        self.setStyleSheet("""
            /* Estilos generales */
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            /* Sidebar */
            #Sidebar {
                background-color: #2c3e50;
                border-right: 1px solid #1a252f;
            }
            #MenuTitle {
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            
            /* Botones del Sidebar */
            QPushButton {
                background-color: transparent;
                color: #bdc3c7;
                border: none;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                text-align: left;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
                color: #ffffff;
            }
            
            /* Títulos de las vistas centrales (temporal) */
            QLabel {
                font-size: 28px;
                color: #2c3e50;
            }
        """)
