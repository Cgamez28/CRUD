-- ============================================================
--  Sistema de Gestión Hotelera — Base de Datos PostgreSQL 18
--  Modelo Relacional | Proyecto Final
-- ============================================================

-- Crear y conectar a la base de datos (ejecutar como superusuario)
-- CREATE DATABASE hotel_gestion ENCODING 'UTF8';
-- \c hotel_gestion

-- ============================================================
-- 1. PERSONA
--    Superentidad de la jerarquía Cliente / Empleado.
--    Edad es atributo derivado: se calcula con AGE().
--    numTelefono se normaliza en tabla Telefono (multivaluado).
-- ============================================================
CREATE TABLE persona (
    idPersona     INT            GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    primerNom     VARCHAR(50)    NOT NULL,
    segundoNom    VARCHAR(50)    NULL,
    primerApell   VARCHAR(50)    NOT NULL,
    segundoApell  VARCHAR(50)    NULL,
    calle         VARCHAR(100)   NULL,
    carrera       VARCHAR(100)   NULL,
    complemento   VARCHAR(150)   NULL,
    correo        VARCHAR(100)   NULL,
    fechaNac      DATE           NOT NULL,

    CONSTRAINT chk_persona_fechaNac
        CHECK (fechaNac <= CURRENT_DATE)
);

-- Atributo derivado Edad — vista de conveniencia:
-- SELECT idPersona, DATE_PART('year', AGE(fechaNac))::INT AS edad FROM persona;


-- ============================================================
-- 2. TELEFONO  (atributo multivaluado de Persona)
--    PK compuesta: (idPersona, numTelefono)
-- ============================================================
CREATE TABLE telefono (
    idPersona    INT          NOT NULL,
    numTelefono  VARCHAR(20)  NOT NULL,

    CONSTRAINT pk_telefono PRIMARY KEY (idPersona, numTelefono),
    CONSTRAINT fk_telefono_persona
        FOREIGN KEY (idPersona) REFERENCES persona (idPersona)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- ============================================================
-- 3. CLIENTE  (subentidad de Persona — tabla-por-subclase)
-- ============================================================
CREATE TABLE cliente (
    idPersona  INT  NOT NULL,

    CONSTRAINT pk_cliente PRIMARY KEY (idPersona),
    CONSTRAINT fk_cliente_persona
        FOREIGN KEY (idPersona) REFERENCES persona (idPersona)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- ============================================================
-- 4. AREA
-- ============================================================
CREATE TABLE area (
    idArea      INT           GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombreArea  VARCHAR(100)  NOT NULL,

    CONSTRAINT uq_area_nombre UNIQUE (nombreArea)
);


-- ============================================================
-- 5. EMPLEADO  (subentidad de Persona — tabla-por-subclase)
--    Relación "Asignado a": N empleados → 1 área (FK aquí).
-- ============================================================
CREATE TABLE empleado (
    idPersona  INT          NOT NULL,
    cargo      VARCHAR(80)  NOT NULL,
    idArea     INT          NOT NULL,

    CONSTRAINT pk_empleado PRIMARY KEY (idPersona),
    CONSTRAINT fk_empleado_persona
        FOREIGN KEY (idPersona) REFERENCES persona (idPersona)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_empleado_area
        FOREIGN KEY (idArea) REFERENCES area (idArea)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


-- ============================================================
-- 6. HABITACION
--    numHabitacion es clave natural (número real de habitación,
--    ej. 101, 202). Se conserva su significado semántico con un
--    CHECK > 0 en lugar de IDENTITY, para que el número asignado
--    corresponda al número físico de la habitación en el hotel.
-- ============================================================
CREATE TABLE habitacion (
    numHabitacion  INT              NOT NULL,
    categoria      VARCHAR(50)      NOT NULL,
    estadoActual   VARCHAR(30)      NOT NULL DEFAULT 'Disponible',
    precioNoche    NUMERIC(10, 2)   NOT NULL,

    CONSTRAINT pk_habitacion PRIMARY KEY (numHabitacion),
    CONSTRAINT chk_habitacion_num
        CHECK (numHabitacion > 0),
    CONSTRAINT chk_habitacion_precio
        CHECK (precioNoche > 0),
    CONSTRAINT chk_habitacion_estado
        CHECK (estadoActual IN ('Disponible', 'Ocupada', 'Reservada', 'Mantenimiento'))
);


-- ============================================================
-- 7. RESERVA
--    PK compuesta: (idPersona, numHabitacion, fechaReserva).
--    Esta combinación garantiza que un cliente no pueda hacer
--    dos reservas distintas para la misma habitación en la
--    misma fecha, que es la restricción de negocio correcta.
--    Se elimina idReserva (surrogate) ya que la PK natural
--    es suficiente para identificar unívocamente cada reserva.
--    valorReserva se almacena para soportar descuentos/tarifas.
-- ============================================================
CREATE TABLE reserva (
    idPersona             INT              NOT NULL,
    numHabitacion         INT              NOT NULL,
    fechaReserva          DATE             NOT NULL,
    fechaLlegada          DATE             NOT NULL,
    fechaSalida           DATE             NOT NULL,
    valorReserva          NUMERIC(10, 2)   NOT NULL,
    tiempoMaxCancelacion  INT              NULL DEFAULT 24,   -- horas

    CONSTRAINT pk_reserva
        PRIMARY KEY (idPersona, numHabitacion, fechaReserva),
    CONSTRAINT fk_reserva_cliente
        FOREIGN KEY (idPersona) REFERENCES cliente (idPersona)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_reserva_habitacion
        FOREIGN KEY (numHabitacion) REFERENCES habitacion (numHabitacion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT chk_reserva_llegada
        CHECK (fechaLlegada >= fechaReserva),
    CONSTRAINT chk_reserva_salida
        CHECK (fechaSalida > fechaLlegada),
    CONSTRAINT chk_reserva_valor
        CHECK (valorReserva > 0),
    CONSTRAINT chk_reserva_cancelacion
        CHECK (tiempoMaxCancelacion IS NULL OR tiempoMaxCancelacion >= 0)
);


-- ============================================================
-- 8. SERVICIO
--    Se mantiene idServicio como PK con IDENTITY.
--    Justificación: nombreServicio ya está protegido por
--    UNIQUE, lo que garantiza integridad sin los costos de
--    usar un VARCHAR como clave foránea en la tabla Consumo
--    (mayor espacio en disco, comparaciones más lentas y
--    mayor riesgo ante cambios de nombre del servicio).
-- ============================================================
CREATE TABLE servicio (
    idServicio      INT              GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombreServicio  VARCHAR(100)     NOT NULL,
    detalles        TEXT             NULL,
    costo           NUMERIC(10, 2)   NOT NULL,

    CONSTRAINT uq_servicio_nombre UNIQUE (nombreServicio),
    CONSTRAINT chk_servicio_costo CHECK (costo > 0)
);


-- ============================================================
-- 9. CONSUMO  (agregación Reserva ↔ Servicio)
--    FK hacia reserva actualizada a la nueva PK compuesta
--    (idPersona, numHabitacion, fechaReserva).
--    PK compuesta: (fechaHoraConsumo, idPersona, numHabitacion,
--    fechaReserva) para evitar colisiones si dos reservas
--    distintas registran un consumo en el mismo instante exacto.
-- ============================================================
CREATE TABLE consumo (
    fechaHoraConsumo  TIMESTAMP  NOT NULL,
    idPersona         INT        NOT NULL,
    numHabitacion     INT        NOT NULL,
    fechaReserva      DATE       NOT NULL,
    idServicio        INT        NOT NULL,

    CONSTRAINT pk_consumo
        PRIMARY KEY (fechaHoraConsumo, idPersona, numHabitacion, fechaReserva),
    CONSTRAINT fk_consumo_reserva
        FOREIGN KEY (idPersona, numHabitacion, fechaReserva)
        REFERENCES reserva (idPersona, numHabitacion, fechaReserva)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_consumo_servicio
        FOREIGN KEY (idServicio) REFERENCES servicio (idServicio)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT chk_consumo_fecha
        CHECK (fechaHoraConsumo <= NOW())
);


-- ============================================================
-- ÍNDICES ADICIONALES
-- ============================================================
CREATE INDEX idx_reserva_cliente    ON reserva  (idPersona);
CREATE INDEX idx_reserva_habitacion ON reserva  (numHabitacion);
CREATE INDEX idx_consumo_reserva    ON consumo  (idPersona, numHabitacion, fechaReserva);
CREATE INDEX idx_consumo_servicio   ON consumo  (idServicio);
CREATE INDEX idx_empleado_area      ON empleado (idArea);


-- ============================================================
-- VISTA UTILITARIA — Edad calculada por persona
-- ============================================================
CREATE OR REPLACE VIEW v_persona_edad AS
SELECT
    idPersona,
    CONCAT(primerNom, ' ',
           COALESCE(segundoNom || ' ', ''),
           primerApell,
           COALESCE(' ' || segundoApell, '')) AS nombreCompleto,
    fechaNac,
    DATE_PART('year', AGE(fechaNac))::INT AS edad
FROM persona;


-- ============================================================
-- DATOS DE PRUEBA
-- ============================================================

-- Áreas
INSERT INTO area (nombreArea) VALUES
    ('Recepción'),
    ('Cocina'),
    ('Mantenimiento'),
    ('Spa'),
    ('Administración');

-- Personas
INSERT INTO persona (primerNom, segundoNom, primerApell, segundoApell,
                     calle, carrera, complemento, correo, fechaNac) VALUES
    ('Carlos',  'Andrés',  'Gómez',    'Ruiz',    'Calle 45',  'Carrera 12', 'Apto 302', 'carlos@gmail.com',   '1990-05-14'),
    ('María',   'Isabel',  'Torres',   'López',   'Calle 80',  'Carrera 7',  NULL,       'maria@hotmail.com',  '1985-11-23'),
    ('Juan',    NULL,      'Martínez', 'Peña',    'Calle 12',  'Carrera 30', 'Casa 5',   'juan@yahoo.com',     '1978-03-08'),
    ('Laura',   'Sofía',   'Vargas',   NULL,      'Calle 100', 'Carrera 15', 'Apto 101', 'laura@gmail.com',    '1995-07-30'),
    ('Pedro',   'Luis',    'Ramírez',  'Castro',  'Calle 22',  'Carrera 9',  NULL,       'pedro@empresa.com',  '1982-09-15'),
    ('Ana',     'Lucía',   'Herrera',  'Mora',    'Calle 60',  'Carrera 20', 'Of. 201',  'ana@hotel.com',      '1993-02-28');

-- Teléfonos
INSERT INTO telefono (idPersona, numTelefono) VALUES
    (1, '3101234567'),
    (1, '6012345678'),
    (2, '3209876543'),
    (3, '3154567890'),
    (4, '3001122334'),
    (5, '3187654321'),
    (6, '3112233445');

-- Clientes (idPersona 1-4)
INSERT INTO cliente (idPersona) VALUES (1), (2), (3), (4);

-- Empleados (idPersona 5-6)
INSERT INTO empleado (idPersona, cargo, idArea) VALUES
    (5, 'Recepcionista', 1),
    (6, 'Chef',          2);

-- Habitaciones
INSERT INTO habitacion (numHabitacion, categoria, estadoActual, precioNoche) VALUES
    (101, 'Sencilla',     'Disponible',  150000.00),
    (102, 'Doble',        'Disponible',  250000.00),
    (201, 'Suite',        'Reservada',   450000.00),
    (202, 'Presidencial', 'Disponible',  800000.00),
    (301, 'Sencilla',     'Ocupada',     150000.00);

-- Servicios
INSERT INTO servicio (nombreServicio, detalles, costo) VALUES
    ('Spa',          'Masaje relajante 60 min',            120000.00),
    ('Lavandería',   'Lavado y planchado por prenda',       25000.00),
    ('Room Service', 'Servicio de comida a la habitación',  50000.00),
    ('Transporte',   'Traslado aeropuerto - hotel',         80000.00);

-- Reservas
--   PK: (idPersona, numHabitacion, fechaReserva)
INSERT INTO reserva (idPersona, numHabitacion, fechaReserva, fechaLlegada,
                     fechaSalida, valorReserva, tiempoMaxCancelacion) VALUES
    (1, 201, '2024-03-01', '2024-03-10', '2024-03-15', 2250000.00, 48),
    (2, 102, '2024-04-05', '2024-04-12', '2024-04-14',  500000.00, 24),
    (3, 301, '2024-05-20', '2024-06-01', '2024-06-05',  600000.00, 72),
    (4, 101, '2024-06-10', '2024-06-15', '2024-06-17',  300000.00, 24);

-- Consumos
--   Se reemplaza idReserva por los tres campos de la PK de reserva:
--   (idPersona, numHabitacion, fechaReserva)
INSERT INTO consumo (fechaHoraConsumo, idPersona, numHabitacion, fechaReserva, idServicio) VALUES
    ('2024-03-11 10:00:00', 1, 201, '2024-03-01', 1),   -- Reserva Carlos / Suite 201 → Spa
    ('2024-03-12 14:30:00', 1, 201, '2024-03-01', 3),   -- Reserva Carlos / Suite 201 → Room Service
    ('2024-04-13 09:00:00', 2, 102, '2024-04-05', 2),   -- Reserva María  / Doble 102  → Lavandería
    ('2024-06-02 19:00:00', 3, 301, '2024-05-20', 3),   -- Reserva Juan   / Sencilla 301 → Room Service
    ('2024-06-03 11:00:00', 3, 301, '2024-05-20', 4);   -- Reserva Juan   / Sencilla 301 → Transporte


-- ============================================================
-- CONSULTAS DE VERIFICACIÓN
-- ============================================================

-- Edad de todas las personas
-- SELECT * FROM v_persona_edad;

-- Clientes con sus teléfonos
-- SELECT p.idPersona, p.primerNom, p.primerApell, t.numTelefono
-- FROM persona p
-- JOIN cliente c ON c.idPersona = p.idPersona
-- JOIN telefono t ON t.idPersona = p.idPersona;

-- Reservas con datos de cliente y habitación
-- SELECT r.idPersona,
--        CONCAT(p.primerNom, ' ', p.primerApell) AS cliente,
--        r.numHabitacion, h.categoria,
--        r.fechaReserva, r.fechaLlegada, r.fechaSalida, r.valorReserva
-- FROM reserva r
-- JOIN persona p    ON p.idPersona     = r.idPersona
-- JOIN habitacion h ON h.numHabitacion = r.numHabitacion;

-- Servicios consumidos por reserva
-- SELECT c.idPersona,
--        CONCAT(p.primerNom, ' ', p.primerApell) AS cliente,
--        c.numHabitacion, c.fechaReserva,
--        s.nombreServicio, s.costo, c.fechaHoraConsumo
-- FROM consumo c
-- JOIN persona  p ON p.idPersona    = c.idPersona
-- JOIN servicio s ON s.idServicio   = c.idServicio
-- ORDER BY c.idPersona, c.fechaHoraConsumo;