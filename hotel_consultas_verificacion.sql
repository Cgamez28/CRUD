-- ============================================================
--  Sistema de Gestión Hotelera — Consultas de Verificación
--  PostgreSQL 18  |  Proyecto Final
-- ============================================================

\c hotel_gestion


-- ============================================================
-- BLOQUE 1 — RECEPCIÓN
--   · Gestiona clientes y reservas (INSERT, UPDATE, SELECT)
--   · Consulta disponibilidad y estado de habitaciones
-- ============================================================

-- ── 1.1  Registrar un nuevo cliente ────────────────────────
INSERT INTO persona (primerNom, segundoNom, primerApell, segundoApell,
                     calle, carrera, complemento, correo, fechaNac)
VALUES ('Sofía', 'Elena', 'Castro', 'Ríos',
        'Calle 34', 'Carrera 8', 'Apto 501',
        'sofia@correo.com', '1998-04-22');

-- El idPersona generado será el mayor de la tabla; lo asignamos a cliente
INSERT INTO cliente (idPersona)
VALUES ((SELECT MAX(idPersona) FROM persona));

INSERT INTO telefono (idPersona, numTelefono)
VALUES ((SELECT MAX(idPersona) FROM persona), '3205551234');


-- ── 1.2  Crear una nueva reserva para ese cliente ──────────
--   PK de reserva: (idPersona, numHabitacion, fechaReserva)
--   No se declara idReserva; la identifica la combinación de estos tres campos.
INSERT INTO reserva (idPersona, numHabitacion, fechaReserva,
                     fechaLlegada, fechaSalida,
                     valorReserva, tiempoMaxCancelacion)
VALUES (
    (SELECT MAX(idPersona) FROM cliente),
    102,
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '5 days',
    CURRENT_DATE + INTERVAL '8 days',
    750000.00,
    48
);


-- ── 1.3  Actualizar datos de contacto de un cliente ────────
UPDATE persona
SET correo = 'sofia.nueva@correo.com',
    calle  = 'Calle 50'
WHERE idPersona = (SELECT MAX(idPersona) FROM cliente);


-- ── 1.4  Consultar todas las reservas de un cliente ────────
--   Se reemplaza r.idReserva por la PK compuesta equivalente.
SELECT
    r.idPersona,
    r.numHabitacion,
    r.fechaReserva,
    CONCAT(p.primerNom, ' ', p.primerApell)  AS cliente,
    h.categoria,
    r.fechaLlegada,
    r.fechaSalida,
    r.valorReserva,
    r.tiempoMaxCancelacion                   AS horas_cancel
FROM reserva r
JOIN persona    p ON p.idPersona     = r.idPersona
JOIN habitacion h ON h.numHabitacion = r.numHabitacion
WHERE p.primerApell = 'Castro'
ORDER BY r.fechaLlegada;


-- ── 1.5  Habitaciones disponibles ahora ────────────────────
SELECT numHabitacion, categoria, precioNoche
FROM habitacion
WHERE estadoActual = 'Disponible'
ORDER BY precioNoche;


-- ── 1.6  Estado completo de todas las habitaciones ─────────
SELECT
    numHabitacion,
    categoria,
    estadoActual,
    precioNoche
FROM habitacion
ORDER BY numHabitacion;


-- ── 1.7  Habitaciones ocupadas con datos del huésped ───────
SELECT
    h.numHabitacion,
    h.categoria,
    h.estadoActual,
    CONCAT(p.primerNom, ' ', p.primerApell) AS huesped,
    r.fechaLlegada,
    r.fechaSalida
FROM habitacion h
JOIN reserva r ON r.numHabitacion = h.numHabitacion
JOIN persona  p ON p.idPersona    = r.idPersona
WHERE h.estadoActual IN ('Ocupada', 'Reservada')
ORDER BY h.numHabitacion;


-- ============================================================
-- BLOQUE 2 — SERVICIO AL HUÉSPED
--   · Consulta y actualiza estado de habitaciones asignadas
--   · Registra consumos adicionales
-- ============================================================

-- ── 2.1  Cambiar estado de habitación (ej: check-in) ───────
UPDATE habitacion
SET estadoActual = 'Ocupada'
WHERE numHabitacion = 102;


-- ── 2.2  Poner habitación en mantenimiento ─────────────────
UPDATE habitacion
SET estadoActual = 'Mantenimiento'
WHERE numHabitacion = 202;


-- ── 2.3  Registrar un consumo adicional (Room Service) ─────
--   Se reemplaza idReserva por los tres campos de la PK compuesta
--   de la reserva más reciente del cliente recién registrado.
INSERT INTO consumo (fechaHoraConsumo, idPersona, numHabitacion, fechaReserva, idServicio)
VALUES (
    NOW(),
    (SELECT MAX(idPersona) FROM cliente),   -- cliente recién creado en 1.1
    102,
    CURRENT_DATE,                           -- fecha con que se creó la reserva en 1.2
    (SELECT idServicio FROM servicio WHERE nombreServicio = 'Room Service')
);


-- ── 2.4  Registrar otro consumo (Spa) ──────────────────────
--   Se identifica la reserva de Carlos (idPersona=1, hab 201, 2024-03-01)
--   con los tres campos de su PK compuesta, en lugar del antiguo idReserva=1.
INSERT INTO consumo (fechaHoraConsumo, idPersona, numHabitacion, fechaReserva, idServicio)
VALUES (
    NOW() - INTERVAL '2 hours',
    1,
    201,
    '2024-03-01',
    (SELECT idServicio FROM servicio WHERE nombreServicio = 'Spa')
);


-- ── 2.5  Ver todos los consumos de una reserva específica ──
--   El JOIN entre consumo y reserva se hace con los tres campos
--   compartidos. El filtro WHERE reemplaza al antiguo WHERE c.idReserva = 1.
SELECT
    c.fechaHoraConsumo,
    s.nombreServicio,
    s.costo,
    CONCAT(p.primerNom, ' ', p.primerApell) AS cliente
FROM consumo c
JOIN servicio s ON s.idServicio     = c.idServicio
JOIN reserva  r ON r.idPersona      = c.idPersona
               AND r.numHabitacion  = c.numHabitacion
               AND r.fechaReserva   = c.fechaReserva
JOIN persona  p ON p.idPersona      = r.idPersona
WHERE c.idPersona     = 1            -- Carlos Gómez
  AND c.numHabitacion = 201          -- Suite 201
  AND c.fechaReserva  = '2024-03-01'
ORDER BY c.fechaHoraConsumo;


-- ── 2.6  Total de cargos extra por reserva ─────────────────
--   GROUP BY ahora usa los tres campos de la PK compuesta de reserva
--   en lugar del antiguo idReserva.
SELECT
    c.idPersona,
    c.numHabitacion,
    c.fechaReserva,
    CONCAT(p.primerNom, ' ', p.primerApell) AS cliente,
    COUNT(c.idServicio)                     AS num_consumos,
    SUM(s.costo)                            AS total_servicios
FROM consumo c
JOIN servicio s ON s.idServicio    = c.idServicio
JOIN reserva  r ON r.idPersona     = c.idPersona
               AND r.numHabitacion = c.numHabitacion
               AND r.fechaReserva  = c.fechaReserva
JOIN persona  p ON p.idPersona     = r.idPersona
GROUP BY c.idPersona, c.numHabitacion, c.fechaReserva,
         p.primerNom, p.primerApell
ORDER BY total_servicios DESC;


-- ============================================================
-- BLOQUE 3 — ADMINISTRACIÓN
--   · Gestiona empleados (INSERT, UPDATE, DELETE, SELECT)
--   · Administra servicios ofrecidos
--   · Consultas generales para análisis
-- ============================================================

-- ── 3.1  Agregar un nuevo empleado ─────────────────────────
INSERT INTO persona (primerNom, primerApell, correo, fechaNac)
VALUES ('Roberto', 'Suárez', 'rsuarez@hotel.com', '1988-07-10');

INSERT INTO empleado (idPersona, cargo, idArea)
VALUES (
    (SELECT MAX(idPersona) FROM persona),
    'Conserje',
    (SELECT idArea FROM area WHERE nombreArea = 'Mantenimiento')
);


-- ── 3.2  Actualizar cargo de un empleado ───────────────────
UPDATE empleado
SET cargo  = 'Jefe de Recepción',
    idArea = (SELECT idArea FROM area WHERE nombreArea = 'Recepción')
WHERE idPersona = 5;


-- ── 3.3  Eliminar un empleado (y su registro en persona) ───
-- Primero eliminamos empleado, luego persona (CASCADE lo hace automático)
DELETE FROM empleado
WHERE idPersona = (SELECT MAX(idPersona) FROM empleado);

DELETE FROM persona
WHERE idPersona = (SELECT MAX(idPersona) FROM persona
                   WHERE idPersona NOT IN (SELECT idPersona FROM cliente)
                     AND idPersona NOT IN (SELECT idPersona FROM empleado));


-- ── 3.4  Listar todos los empleados con su área ────────────
SELECT
    e.idPersona,
    CONCAT(p.primerNom, ' ', p.primerApell) AS empleado,
    e.cargo,
    a.nombreArea                             AS area,
    DATE_PART('year', AGE(p.fechaNac))::INT  AS edad
FROM empleado e
JOIN persona p ON p.idPersona = e.idPersona
JOIN area    a ON a.idArea    = e.idArea
ORDER BY a.nombreArea, e.cargo;


-- ── 3.5  Agregar un nuevo servicio ─────────────────────────
INSERT INTO servicio (nombreServicio, detalles, costo)
VALUES ('Minibar', 'Reposición de minibar en habitación', 35000.00);


-- ── 3.6  Actualizar precio de un servicio ──────────────────
UPDATE servicio
SET costo = 130000.00
WHERE nombreServicio = 'Spa';


-- ── 3.7  Listar todos los servicios disponibles ────────────
SELECT idServicio, nombreServicio, detalles, costo
FROM servicio
ORDER BY costo DESC;


-- ── 3.8  Reporte general: reservas con valor total ─────────
--   Se reemplaza r.idReserva en SELECT y GROUP BY por la PK compuesta.
--   El LEFT JOIN con consumo usa los tres campos compartidos.
SELECT
    CONCAT(p.primerNom, ' ', p.primerApell)     AS cliente,
    h.numHabitacion,
    h.categoria,
    r.fechaReserva,
    r.fechaLlegada,
    r.fechaSalida,
    (r.fechaSalida - r.fechaLlegada)            AS noches,
    r.valorReserva,
    COALESCE(SUM(s.costo), 0)                   AS total_servicios,
    r.valorReserva + COALESCE(SUM(s.costo), 0) AS total_factura
FROM reserva r
JOIN persona    p  ON p.idPersona      = r.idPersona
JOIN habitacion h  ON h.numHabitacion  = r.numHabitacion
LEFT JOIN consumo c  ON c.idPersona     = r.idPersona
                    AND c.numHabitacion = r.numHabitacion
                    AND c.fechaReserva  = r.fechaReserva
LEFT JOIN servicio s ON s.idServicio   = c.idServicio
GROUP BY r.idPersona, r.numHabitacion, r.fechaReserva,
         p.primerNom, p.primerApell,
         h.numHabitacion, h.categoria,
         r.fechaLlegada, r.fechaSalida, r.valorReserva
ORDER BY r.idPersona, r.numHabitacion, r.fechaReserva;


-- ── 3.9  Clientes con más reservas ────────────────────────
--   COUNT(*) reemplaza a COUNT(r.idReserva) ya que no existe esa columna.
SELECT
    CONCAT(p.primerNom, ' ', p.primerApell) AS cliente,
    COUNT(*)                                AS total_reservas,
    SUM(r.valorReserva)                     AS gasto_total
FROM reserva r
JOIN persona p ON p.idPersona = r.idPersona
GROUP BY p.idPersona, p.primerNom, p.primerApell
ORDER BY total_reservas DESC, gasto_total DESC;


-- ── 3.10 Servicio más consumido ────────────────────────────
SELECT
    s.nombreServicio,
    COUNT(c.idServicio) AS veces_consumido,
    SUM(s.costo)        AS ingresos_generados
FROM consumo c
JOIN servicio s ON s.idServicio = c.idServicio
GROUP BY s.idServicio, s.nombreServicio
ORDER BY veces_consumido DESC;


-- ── 3.11 Ocupación por categoría de habitación ─────────────
SELECT
    categoria,
    COUNT(*)                                               AS total_habitaciones,
    COUNT(*) FILTER (WHERE estadoActual = 'Ocupada')       AS ocupadas,
    COUNT(*) FILTER (WHERE estadoActual = 'Disponible')    AS disponibles,
    COUNT(*) FILTER (WHERE estadoActual = 'Reservada')     AS reservadas,
    COUNT(*) FILTER (WHERE estadoActual = 'Mantenimiento') AS mantenimiento
FROM habitacion
GROUP BY categoria
ORDER BY categoria;


-- ── 3.12 Verificar edad de todas las personas (atrib. deriv.)
SELECT
    idPersona,
    CONCAT(primerNom, ' ', primerApell)         AS nombre,
    fechaNac,
    DATE_PART('year', AGE(fechaNac))::INT        AS edad
FROM persona
ORDER BY edad DESC;