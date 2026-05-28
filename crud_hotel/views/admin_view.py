from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout, QHBoxLayout,
    QLineEdit, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QGroupBox
)
from PyQt6.QtCore import QDate
from controllers.admin_ctrl import AdminController

class AdminView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = AdminController()
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.setup_tab_empleados()
        self.setup_tab_reporte_ocupacion()
        self.setup_tab_reporte_clientes()

    # ==========================================
    # PESTAÑA 1: GESTIÓN EMPLEADOS
    # ==========================================
    def setup_tab_empleados(self):
        tab = QWidget()
        self.tabs.addTab(tab, "Gestión RR.HH")
        
        main_layout = QHBoxLayout(tab)
        
        # --- Panel Izquierdo: Formulario Nuevo Empleado ---
        group_box = QGroupBox("Contratar Empleado")
        form_layout = QFormLayout()
        
        self.txt_pnom = QLineEdit()
        self.txt_snom = QLineEdit()
        self.txt_papell = QLineEdit()
        self.txt_sapell = QLineEdit()
        self.txt_correo = QLineEdit()
        self.txt_telefono = QLineEdit()
        self.date_nac = QDateEdit()
        self.date_nac.setCalendarPopup(True)
        self.date_nac.setDate(QDate.currentDate().addYears(-20))
        
        self.txt_cargo = QLineEdit()
        self.txt_id_area = QLineEdit()
        
        form_layout.addRow("Primer Nombre (*):", self.txt_pnom)
        form_layout.addRow("Segundo Nombre:", self.txt_snom)
        form_layout.addRow("Primer Apellido (*):", self.txt_papell)
        form_layout.addRow("Segundo Apellido:", self.txt_sapell)
        form_layout.addRow("Correo Electrónico:", self.txt_correo)
        form_layout.addRow("Teléfono:", self.txt_telefono)
        form_layout.addRow("Fecha de Nacimiento:", self.date_nac)
        form_layout.addRow("Cargo a Ocupar (*):", self.txt_cargo)
        form_layout.addRow("ID Área Asignada (*):", self.txt_id_area)
        
        btn_layout = QHBoxLayout()
        btn_contratar = QPushButton("Registrar Empleado")
        btn_contratar.setStyleSheet("background-color: #2980b9; color: white; padding: 6px; font-weight: bold;")
        btn_contratar.clicked.connect(self.handle_contratar_empleado)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_contratar)
        
        group_layout = QVBoxLayout()
        group_layout.addLayout(form_layout)
        group_layout.addLayout(btn_layout)
        group_layout.addStretch()
        group_box.setLayout(group_layout)
        
        main_layout.addWidget(group_box, 1) # 1 Parte de la relación de aspecto
        
        # --- Panel Derecho: Tabla Empleados ---
        right_panel = QVBoxLayout()
        self.table_empleados = QTableWidget(0, 6)
        self.table_empleados.setHorizontalHeaderLabels(['ID', 'Nombre Completo', 'Correo', 'Teléfono(s)', 'Cargo', 'ID Área'])
        self.table_empleados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_empleados.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        right_panel.addWidget(self.table_empleados)
        main_layout.addLayout(right_panel, 2) # 2 Partes (Doble de ancho que el form)
        
        # Cargar empleados por primera vez
        self.cargar_empleados()

    def cargar_empleados(self):
        try:
            empleados = self.controller.obtener_todos_empleados()
            self.table_empleados.setRowCount(len(empleados))
            for i, emp in enumerate(empleados):
                # Formatear el nombre completo ignorando los nulos
                nombre_comp = f"{emp.primerNom} {emp.segundoNom or ''} {emp.primerApell} {emp.segundoApell or ''}".strip()
                nombre_comp = " ".join(nombre_comp.split()) # Quita dobles espacios si algún valor era None
                
                self.table_empleados.setItem(i, 0, QTableWidgetItem(str(emp.idPersona)))
                self.table_empleados.setItem(i, 1, QTableWidgetItem(nombre_comp))
                self.table_empleados.setItem(i, 2, QTableWidgetItem(emp.correo or "N/A"))
                self.table_empleados.setItem(i, 3, QTableWidgetItem(emp.telefonos or "Sin Teléfono"))
                self.table_empleados.setItem(i, 4, QTableWidgetItem(emp.cargo))
                self.table_empleados.setItem(i, 5, QTableWidgetItem(str(emp.idArea)))
        except Exception as e:
            QMessageBox.critical(self, "Error al cargar empleados", str(e))

    def handle_contratar_empleado(self):
        if not self.txt_pnom.text().strip() or not self.txt_papell.text().strip() or not self.txt_cargo.text().strip():
            QMessageBox.warning(self, "Validación", "Los campos Nombre, Apellido y Cargo son obligatorios.")
            return
            
        try:
            datos_empleado = {
                'primerNom': self.txt_pnom.text().strip(),
                'segundoNom': self.txt_snom.text().strip() or None,
                'primerApell': self.txt_papell.text().strip(),
                'segundoApell': self.txt_sapell.text().strip() or None,
                'calle': None, 'carrera': None, 'complemento': None, # Omitidos por la vista para limpieza
                'correo': self.txt_correo.text().strip() or None,
                'telefono': self.txt_telefono.text().strip() or None,
                'fechaNac': self.date_nac.date().toPyDate()
            }
            
            cargo = self.txt_cargo.text().strip()
            id_area = int(self.txt_id_area.text().strip())
            
            nuevo_emp = self.controller.contratar_empleado(datos_empleado, cargo, id_area)
            QMessageBox.information(self, "Contratación Exitosa", f"Empleado {nuevo_emp.primerNom} añadido en el Área {id_area} con ID {nuevo_emp.idPersona}.")
            
            # Limpiar forma
            self.txt_pnom.clear(); self.txt_snom.clear(); self.txt_papell.clear()
            self.txt_sapell.clear(); self.txt_correo.clear(); self.txt_telefono.clear()
            self.txt_cargo.clear(); self.txt_id_area.clear()
            
            # Actualizar tabla
            self.cargar_empleados()
            
        except ValueError as ve:
            if "invalid literal" in str(ve):
                QMessageBox.warning(self, "Dato Inválido", "El ID Área debe ser un número entero (Ej: 1 = Recepción, 2 = Cocina).")
            else:
                QMessageBox.warning(self, "Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error al generar contrato", str(e))

    # ==========================================
    # PESTAÑA 2: REPORTE OCUPACIÓN
    # ==========================================
    def setup_tab_reporte_ocupacion(self):
        tab = QWidget()
        self.tabs.addTab(tab, "Reporte de Ocupación")
        layout = QVBoxLayout(tab)
        
        btn_generar = QPushButton("Generar Reporte de Eficiencia Habitacional")
        btn_generar.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-size: 14px; font-weight: bold;")
        btn_generar.clicked.connect(self.cargar_reporte_ocupacion)
        layout.addWidget(btn_generar)
        
        self.table_ocupacion = QTableWidget(0, 3)
        self.table_ocupacion.setHorizontalHeaderLabels(['Categoría', 'Estado Actual', 'Cantidad Habitaciones'])
        self.table_ocupacion.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_ocupacion.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table_ocupacion)

    def cargar_reporte_ocupacion(self):
        try:
            datos = self.controller.reporte_ocupacion()
            self.table_ocupacion.setRowCount(len(datos))
            for i, row in enumerate(datos):
                self.table_ocupacion.setItem(i, 0, QTableWidgetItem(row['categoria']))
                self.table_ocupacion.setItem(i, 1, QTableWidgetItem(row['estadoactual']))
                self.table_ocupacion.setItem(i, 2, QTableWidgetItem(str(row['cantidad'])))
        except Exception as e:
            QMessageBox.critical(self, "Error DB", f"Falló la construcción del cruce analítico:\n{e}")

    # ==========================================
    # PESTAÑA 3: TOP CLIENTES
    # ==========================================
    def setup_tab_reporte_clientes(self):
        tab = QWidget()
        self.tabs.addTab(tab, "Top Mejores Clientes")
        layout = QVBoxLayout(tab)
        
        btn_generar = QPushButton("Lanzar Reporte Financiero de Clientes")
        btn_generar.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; font-size: 14px; font-weight: bold;")
        btn_generar.clicked.connect(self.cargar_reporte_clientes)
        layout.addWidget(btn_generar)
        
        self.table_top = QTableWidget(0, 4)
        self.table_top.setHorizontalHeaderLabels(['Nombre', 'Apellido', 'Total Hosted (Reservas)', 'Facturación Base Histórica'])
        self.table_top.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_top.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table_top)

    def cargar_reporte_clientes(self):
        try:
            datos = self.controller.reporte_clientes_frecuentes()
            self.table_top.setRowCount(len(datos))
            for i, row in enumerate(datos):
                self.table_top.setItem(i, 0, QTableWidgetItem(row['primernom']))
                self.table_top.setItem(i, 1, QTableWidgetItem(row['primerapell']))
                self.table_top.setItem(i, 2, QTableWidgetItem(str(row['total_reservas'])))
                # Formateo contable a moneda
                valor_hist = float(row['valor_historico_dejado'] or 0.0)
                self.table_top.setItem(i, 3, QTableWidgetItem(f"${valor_hist:,.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Error DB", f"Falló el pipeline de agregación:\n{e}")
