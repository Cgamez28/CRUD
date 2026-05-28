from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout, QHBoxLayout,
    QLineEdit, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import QDate
from controllers.recepcion_ctrl import RecepcionController

class RecepcionView(QWidget):
    def __init__(self):
        super().__init__()
        # Inyectamos el controlador
        self.controller = RecepcionController()
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Tab Widget principal
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Crear y añadir las pestañas
        self.setup_tab_registrar_cliente()
        self.setup_tab_listado_clientes()
        self.setup_tab_disponibilidad()
        self.setup_tab_reserva()

    # ==========================================
    # PESTAÑA: LISTADO DE CLIENTES
    # ==========================================
    def setup_tab_listado_clientes(self):
        tab = QWidget()
        self.tabs.addTab(tab, "Listado de Clientes")
        
        layout = QVBoxLayout(tab)
        
        btn_actualizar = QPushButton("↻ Refrescar Clientes")
        btn_actualizar.clicked.connect(self.cargar_clientes)
        layout.addWidget(btn_actualizar)
        
        self.table_clientes = QTableWidget(0, 11)
        self.table_clientes.setHorizontalHeaderLabels([
            'ID', 'Primer Nombre', 'Segundo Nombre', 'Primer Apellido', 'Segundo Apellido',
            'Calle', 'Carrera', 'Complemento', 'Correo', 'Teléfono(s)', 'Fecha Nacimiento'
        ])
        self.table_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_clientes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table_clientes)
        
        # Cargar datos
        self.cargar_clientes()

    def cargar_clientes(self):
        try:
            clientes = self.controller.obtener_clientes()
            self.table_clientes.setRowCount(len(clientes))
            for i, cli in enumerate(clientes):
                self.table_clientes.setItem(i, 0, QTableWidgetItem(str(cli.idPersona)))
                self.table_clientes.setItem(i, 1, QTableWidgetItem(cli.primerNom))
                self.table_clientes.setItem(i, 2, QTableWidgetItem(cli.segundoNom or ""))
                self.table_clientes.setItem(i, 3, QTableWidgetItem(cli.primerApell))
                self.table_clientes.setItem(i, 4, QTableWidgetItem(cli.segundoApell or ""))
                self.table_clientes.setItem(i, 5, QTableWidgetItem(cli.calle or ""))
                self.table_clientes.setItem(i, 6, QTableWidgetItem(cli.carrera or ""))
                self.table_clientes.setItem(i, 7, QTableWidgetItem(cli.complemento or ""))
                self.table_clientes.setItem(i, 8, QTableWidgetItem(cli.correo or ""))
                self.table_clientes.setItem(i, 9, QTableWidgetItem(cli.telefonos or "Sin Teléfono"))
                self.table_clientes.setItem(i, 10, QTableWidgetItem(cli.fechaNac.strftime("%Y-%m-%d")))
        except Exception as e:
            QMessageBox.critical(self, "Error al cargar clientes", str(e))

    # ==========================================
    # PESTAÑA 1: REGISTRAR CLIENTE
    # ==========================================
    def setup_tab_registrar_cliente(self):
        tab = QWidget()
        self.tabs.addTab(tab, "Registrar Cliente")
        
        main_layout = QVBoxLayout(tab)
        form_layout = QFormLayout()
        
        # Inputs
        self.txt_pnom = QLineEdit()
        self.txt_snom = QLineEdit()
        self.txt_papell = QLineEdit()
        self.txt_sapell = QLineEdit()
        self.txt_calle = QLineEdit()
        self.txt_carrera = QLineEdit()
        self.txt_comp = QLineEdit()
        self.txt_correo = QLineEdit()
        self.txt_telefono = QLineEdit()
        
        self.date_nac = QDateEdit()
        self.date_nac.setCalendarPopup(True)
        self.date_nac.setDate(QDate.currentDate().addYears(-18)) # Default a alguien mayor de edad

        # Estructurar formulario
        form_layout.addRow("Primer Nombre (*):", self.txt_pnom)
        form_layout.addRow("Segundo Nombre:", self.txt_snom)
        form_layout.addRow("Primer Apellido (*):", self.txt_papell)
        form_layout.addRow("Segundo Apellido:", self.txt_sapell)
        form_layout.addRow("Calle:", self.txt_calle)
        form_layout.addRow("Carrera:", self.txt_carrera)
        form_layout.addRow("Complemento:", self.txt_comp)
        form_layout.addRow("Correo Electrónico:", self.txt_correo)
        form_layout.addRow("Teléfono (Opcional por ahora):", self.txt_telefono)
        form_layout.addRow("Fecha de Nacimiento (*):", self.date_nac)
        
        main_layout.addLayout(form_layout)
        
        # Botón Guardar
        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar Cliente")
        btn_guardar.clicked.connect(self.handle_guardar_cliente)
        btn_guardar.setStyleSheet("background-color: #3498db; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        btn_layout.addStretch()
        btn_layout.addWidget(btn_guardar)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

    def handle_guardar_cliente(self):
        # Validar obligatorios
        if not self.txt_pnom.text().strip() or not self.txt_papell.text().strip():
            QMessageBox.warning(self, "Error de Validación", "El primer nombre y primer apellido son obligatorios.")
            return

        datos_cliente = {
            'primerNom': self.txt_pnom.text().strip(),
            'segundoNom': self.txt_snom.text().strip() or None,
            'primerApell': self.txt_papell.text().strip(),
            'segundoApell': self.txt_sapell.text().strip() or None,
            'calle': self.txt_calle.text().strip() or None,
            'carrera': self.txt_carrera.text().strip() or None,
            'complemento': self.txt_comp.text().strip() or None,
            'correo': self.txt_correo.text().strip() or None,
            'telefono': self.txt_telefono.text().strip() or None,
            'fechaNac': self.date_nac.date().toPyDate()
        }

        try:
            nuevo_cliente = self.controller.registrar_cliente(datos_cliente)
            # NOTA: El teléfono se debería insertar con un DAO de teléfono, lo dejamos preparado para la siguiente iteración
            QMessageBox.information(self, "Éxito", f"Cliente {nuevo_cliente.primerNom} guardado correctamente.\nID asignado: {nuevo_cliente.idPersona}")
            
            # Limpiar campos
            for txt in [self.txt_pnom, self.txt_snom, self.txt_papell, self.txt_sapell, 
                        self.txt_calle, self.txt_carrera, self.txt_comp, self.txt_correo, self.txt_telefono]:
                txt.clear()
        except ValueError as ve:
            QMessageBox.warning(self, "Atención", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", str(e))

    # ==========================================
    # PESTAÑA 2: DISPONIBILIDAD
    # ==========================================
    def setup_tab_disponibilidad(self):
        tab = QWidget()
        self.tabs.addTab(tab, "Disponibilidad")
        
        layout = QVBoxLayout(tab)
        
        # Botón actualizar
        btn_actualizar = QPushButton("↻ Actualizar Habitaciones")
        btn_actualizar.clicked.connect(self.cargar_disponibilidad)
        layout.addWidget(btn_actualizar)
        
        # Tabla
        self.table_habs = QTableWidget(0, 4)
        self.table_habs.setHorizontalHeaderLabels(['Num Habitación', 'Categoría', 'Precio/Noche', 'Estado actual'])
        self.table_habs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_habs.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Solo lectura
        
        layout.addWidget(self.table_habs)
        
        # Cargar datos por primera vez
        self.cargar_disponibilidad()

    def cargar_disponibilidad(self):
        try:
            habitaciones = self.controller.ver_estado_habitaciones()
            # Filtramos solo las disponibles como solicita el dominio
            disponibles = [h for h in habitaciones if h.estadoActual == 'Disponible']
            
            self.table_habs.setRowCount(len(disponibles))
            for i, hab in enumerate(disponibles):
                self.table_habs.setItem(i, 0, QTableWidgetItem(str(hab.numHabitacion)))
                self.table_habs.setItem(i, 1, QTableWidgetItem(hab.categoria))
                self.table_habs.setItem(i, 2, QTableWidgetItem(f"${hab.precioNoche:,.2f}"))
                self.table_habs.setItem(i, 3, QTableWidgetItem(hab.estadoActual))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al cargar habitaciones:\n{e}")

    # ==========================================
    # PESTAÑA 3: CREAR RESERVA
    # ==========================================
    def setup_tab_reserva(self):
        tab = QWidget()
        self.tabs.addTab(tab, "Crear Reserva")
        
        main_layout = QVBoxLayout(tab)
        form_layout = QFormLayout()
        
        # Inputs
        self.txt_id_cliente = QLineEdit()
        self.txt_num_hab = QLineEdit()
        self.txt_valor = QLineEdit()
        
        self.date_llegada = QDateEdit()
        self.date_llegada.setCalendarPopup(True)
        self.date_llegada.setDate(QDate.currentDate())
        
        self.date_salida = QDateEdit()
        self.date_salida.setCalendarPopup(True)
        self.date_salida.setDate(QDate.currentDate().addDays(1))

        form_layout.addRow("ID del Cliente (*):", self.txt_id_cliente)
        form_layout.addRow("Número de Habitación (*):", self.txt_num_hab)
        form_layout.addRow("Fecha de Llegada (*):", self.date_llegada)
        form_layout.addRow("Fecha de Salida (*):", self.date_salida)
        form_layout.addRow("Valor Total Cotizado (*):", self.txt_valor)
        
        main_layout.addLayout(form_layout)
        
        # Botón Confirmar
        btn_layout = QHBoxLayout()
        btn_confirmar = QPushButton("✓ Confirmar Reserva")
        btn_confirmar.clicked.connect(self.handle_crear_reserva)
        btn_confirmar.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        btn_layout.addStretch()
        btn_layout.addWidget(btn_confirmar)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

    def handle_crear_reserva(self):
        try:
            id_cliente = int(self.txt_id_cliente.text())
            num_hab = int(self.txt_num_hab.text())
            valor = float(self.txt_valor.text().replace(',', ''))
            
            f_llegada = self.date_llegada.date().toPyDate()
            f_salida = self.date_salida.date().toPyDate()
            
            reserva = self.controller.crear_reserva(id_cliente, num_hab, f_llegada, f_salida, valor)
            
            QMessageBox.information(self, "Reserva Exitosa", f"Se generó reserva bloqueando la hab. {reserva.numHabitacion} para ID {reserva.idPersona}.")
            
            # Limpiar
            self.txt_id_cliente.clear()
            self.txt_num_hab.clear()
            self.txt_valor.clear()
            
            # Recargar la tabla de disponibilidad si toca su turno (lo hacemos forzosamente)
            self.cargar_disponibilidad()
            
        except ValueError as ve:
            if "invalid literal" in str(ve):
                QMessageBox.warning(self, "Datos inválidos", "Asegúrese de poner números en los campos de ID, Habitación y Valor.")
            else:
                QMessageBox.warning(self, "Regla de Negocio", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error de Sistema", str(e))
