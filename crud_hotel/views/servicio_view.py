from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout, QHBoxLayout,
    QLineEdit, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QComboBox
)
from PyQt6.QtCore import QDate
from controllers.servicio_ctrl import ServicioController

class ServicioView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ServicioController()
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.setup_tab_estado_habitaciones()
        self.setup_tab_registrar_consumo()

    # ==========================================
    # PESTAÑA 1: ESTADO DE HABITACIONES
    # ==========================================
    def setup_tab_estado_habitaciones(self):
        tab = QWidget()
        self.tabs.addTab(tab, "Estado de Habitaciones")
        
        main_layout = QVBoxLayout(tab)
        
        # Tabla para listar habitaciones
        self.table_habs = QTableWidget(0, 3)
        self.table_habs.setHorizontalHeaderLabels(['Num Habitación', 'Categoría', 'Estado actual'])
        self.table_habs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_habs.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_habs.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_habs.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        main_layout.addWidget(self.table_habs)
        
        # Opciones de control (Menú desplegable y Botón)
        ctrl_layout = QHBoxLayout()
        
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(['Ocupada', 'Mantenimiento', 'Disponible'])
        
        btn_cambiar = QPushButton("Actualizar Estado")
        btn_cambiar.setStyleSheet("background-color: #f39c12; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_cambiar.clicked.connect(self.handle_cambiar_estado)
        
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(self.combo_estado)
        ctrl_layout.addWidget(btn_cambiar)
        
        main_layout.addLayout(ctrl_layout)
        
        # Cargar datos
        self.cargar_habitaciones()

    def cargar_habitaciones(self):
        try:
            habitaciones = self.controller.obtener_habitaciones()
            
            self.table_habs.setRowCount(len(habitaciones))
            for i, hab in enumerate(habitaciones):
                self.table_habs.setItem(i, 0, QTableWidgetItem(str(hab.numHabitacion)))
                self.table_habs.setItem(i, 1, QTableWidgetItem(hab.categoria))
                self.table_habs.setItem(i, 2, QTableWidgetItem(hab.estadoActual))
                
        except Exception as e:
            QMessageBox.critical(self, "Error al cargar habitaciones", str(e))

    def handle_cambiar_estado(self):
        selected_items = self.table_habs.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Sin selección", "Por favor, seleccione una habitación de la tabla primero.")
            return
            
        row = selected_items[0].row()
        num_hab = int(self.table_habs.item(row, 0).text())
        nuevo_estado = self.combo_estado.currentText()
        
        try:
            self.controller.cambiar_estado_habitacion(num_hab, nuevo_estado)
            QMessageBox.information(self, "Éxito", f"Se actualizó el estado de la Habitación {num_hab} a '{nuevo_estado}'.")
            
            # Recargar la tabla para ver el cambio
            self.cargar_habitaciones()
        except Exception as e:
            QMessageBox.critical(self, "Error de Sistema", str(e))

    # ==========================================
    # PESTAÑA 2: REGISTRAR CONSUMO
    # ==========================================
    def setup_tab_registrar_consumo(self):
        tab = QWidget()
        self.tabs.addTab(tab, "Registrar Consumo Extra")
        
        main_layout = QVBoxLayout(tab)
        form_layout = QFormLayout()
        
        # Inputs para la PK de Reserva e Id de Servicio
        self.txt_id_cliente = QLineEdit()
        self.txt_num_hab = QLineEdit()
        
        self.date_reserva = QDateEdit()
        self.date_reserva.setCalendarPopup(True)
        self.date_reserva.setDate(QDate.currentDate())
        
        self.combo_servicios = QComboBox()
        self.cargar_servicios() # Poblar el combo con los servicios de la BD
        
        form_layout.addRow("ID del Cliente (*):", self.txt_id_cliente)
        form_layout.addRow("Número de Habitación (*):", self.txt_num_hab)
        form_layout.addRow("Fecha inicial de la Reserva (*):", self.date_reserva)
        form_layout.addRow("Servicio Consumido (*):", self.combo_servicios)
        
        main_layout.addLayout(form_layout)
        
        # Botón
        btn_layout = QHBoxLayout()
        btn_registrar_consumo = QPushButton("➕ Registrar Cargo")
        btn_registrar_consumo.setStyleSheet("background-color: #8e44ad; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_registrar_consumo.clicked.connect(self.handle_registrar_consumo)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_registrar_consumo)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

    def cargar_servicios(self):
        try:
            servicios = self.controller.obtener_servicios()
            for srv in servicios:
                # Mostrar el nombre y precio en texto, y almacenar el idServicio internamente en userData
                texto_mostrar = f"{srv.nombreServicio} - ${srv.costo:,.2f}"
                self.combo_servicios.addItem(texto_mostrar, srv.idServicio)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al cargar catálogo de servicios: {e}")

    def handle_registrar_consumo(self):
        try:
            id_cliente = int(self.txt_id_cliente.text())
            num_hab = int(self.txt_num_hab.text())
            fecha_reserva = self.date_reserva.date().toPyDate()
            id_servicio = self.combo_servicios.currentData() # Obtiene el userData interno
            
            if id_servicio is None:
                raise ValueError("No hay ningún servicio seleccionado.")
                
            self.controller.registrar_consumo_extra(id_cliente, num_hab, fecha_reserva, id_servicio)
            
            QMessageBox.information(
                self, "Consumo Guardado",
                f"El cargo extra fue añadido exitosamente a la cuenta de la habitación {num_hab}."
            )
            
            # Limpiar entradas de texto
            self.txt_id_cliente.clear()
            self.txt_num_hab.clear()
            
        except ValueError as ve:
            if "invalid literal" in str(ve):
                QMessageBox.warning(self, "Error de Datos", "Los campos ID Cliente y Habitación deben contener solo números enteros.")
            else:
                QMessageBox.warning(self, "Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error al procesar", str(e))
