-- ================================================
-- SISTEMA DE RENDICIONES - ESTRUCTURA DE BASE DE DATOS
-- MySQL / MariaDB
-- ================================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS sistema_rendiciones
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE rendiciones_user;

-- ================================================
-- TABLA: usuarios
-- ================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'aprobador', 'usuario') NOT NULL DEFAULT 'usuario',
    
    -- Estado y seguridad
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    email_verificado BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- MFA
    mfa_habilitado BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret VARCHAR(32) NULL,
    
    -- Recuperación de contraseña
    token_recuperacion VARCHAR(100) NULL,
    token_recuperacion_expira DATETIME NULL,
    
    -- Auditoría
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ultimo_login DATETIME NULL,
    
    -- Información adicional
    telefono VARCHAR(20) NULL,
    departamento VARCHAR(100) NULL,
    cargo VARCHAR(100) NULL,
    
    INDEX idx_email (email),
    INDEX idx_rol (rol),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- TABLA: rendiciones
-- ================================================
CREATE TABLE IF NOT EXISTS rendiciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_rendicion VARCHAR(50) NOT NULL UNIQUE,
    
    -- Usuario que crea la rendición
    usuario_id INT NOT NULL,
    
    -- Información de la rendición
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    descripcion TEXT NULL,
    proyecto VARCHAR(100) NULL,
    centro_costo VARCHAR(100) NULL,
    
    -- Estado
    estado ENUM('pendiente', 'en_revision', 'aprobada', 'rechazada', 'pagada') 
           NOT NULL DEFAULT 'pendiente',
    
    -- Montos
    monto_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    monto_aprobado DECIMAL(10, 2) NULL,
    
    -- Aprobación
    aprobador_id INT NULL,
    fecha_aprobacion DATETIME NULL,
    comentarios_aprobador TEXT NULL,
    
    -- Auditoría
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fecha_envio DATETIME NULL,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (aprobador_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    
    INDEX idx_numero (numero_rendicion),
    INDEX idx_usuario (usuario_id),
    INDEX idx_estado (estado),
    INDEX idx_aprobador (aprobador_id),
    INDEX idx_fecha_creacion (fecha_creacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- TABLA: items_rendicion
-- ================================================
CREATE TABLE IF NOT EXISTS items_rendicion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rendicion_id INT NOT NULL,
    
    -- Información del gasto
    fecha_gasto DATE NOT NULL,
    tipo_gasto VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    proveedor VARCHAR(200) NULL,
    
    -- Montos
    monto DECIMAL(10, 2) NOT NULL,
    moneda VARCHAR(3) NOT NULL DEFAULT 'CLP',
    
    -- Documento
    numero_documento VARCHAR(50) NULL,
    tipo_documento ENUM('boleta', 'factura', 'recibo', 'otro') 
                   NOT NULL DEFAULT 'boleta',
    
    -- Archivo comprobante
    comprobante VARCHAR(255) NULL,
    comprobante_original VARCHAR(255) NULL,
    
    -- Auditoría
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (rendicion_id) REFERENCES rendiciones(id) ON DELETE CASCADE,
    
    INDEX idx_rendicion (rendicion_id),
    INDEX idx_fecha_gasto (fecha_gasto),
    INDEX idx_tipo_gasto (tipo_gasto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- TABLA: notificaciones
-- ================================================
CREATE TABLE IF NOT EXISTS notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    
    -- Contenido
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo ENUM('info', 'success', 'warning', 'error') 
         NOT NULL DEFAULT 'info',
    
    -- Referencia a rendición
    rendicion_id INT NULL,
    
    -- Estado
    leida BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_lectura DATETIME NULL,
    
    -- Auditoría
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (rendicion_id) REFERENCES rendiciones(id) ON DELETE CASCADE,
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_leida (leida),
    INDEX idx_fecha_creacion (fecha_creacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- DATOS INICIALES
-- ================================================

-- Usuario Administrador por defecto
-- Email: admin@primar.cl
-- Contraseña: Admin123!
-- Password hash generado con bcrypt
INSERT INTO usuarios (nombre, email, password_hash, rol, activo, email_verificado, departamento, cargo)
VALUES (
    'Administrador',
    'admin@primar.cl',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lXPQ3nnZPCyi',
    'admin',
    TRUE,
    TRUE,
    'TI',
    'Administrador del Sistema'
) ON DUPLICATE KEY UPDATE email=email;

-- Usuarios de ejemplo para pruebas
INSERT INTO usuarios (nombre, email, password_hash, rol, activo, email_verificado, departamento, cargo)
VALUES 
(
    'Carlos Aprobador',
    'aprobador@primar.cl',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lXPQ3nnZPCyi',
    'aprobador',
    TRUE,
    TRUE,
    'Finanzas',
    'Jefe de Finanzas'
),
(
    'María Usuario',
    'usuario@primar.cl',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lXPQ3nnZPCyi',
    'usuario',
    TRUE,
    TRUE,
    'Ventas',
    'Ejecutivo de Ventas'
) ON DUPLICATE KEY UPDATE email=email;

-- ================================================
-- VISTAS ÚTILES
-- ================================================

-- Vista de resumen de rendiciones por usuario
CREATE OR REPLACE VIEW vista_resumen_rendiciones AS
SELECT 
    u.id AS usuario_id,
    u.nombre AS usuario_nombre,
    COUNT(r.id) AS total_rendiciones,
    SUM(CASE WHEN r.estado = 'pendiente' THEN 1 ELSE 0 END) AS pendientes,
    SUM(CASE WHEN r.estado = 'en_revision' THEN 1 ELSE 0 END) AS en_revision,
    SUM(CASE WHEN r.estado = 'aprobada' THEN 1 ELSE 0 END) AS aprobadas,
    SUM(CASE WHEN r.estado = 'rechazada' THEN 1 ELSE 0 END) AS rechazadas,
    COALESCE(SUM(CASE WHEN r.estado IN ('aprobada', 'pagada') THEN r.monto_aprobado ELSE 0 END), 0) AS monto_total_aprobado
FROM usuarios u
LEFT JOIN rendiciones r ON u.id = r.usuario_id
GROUP BY u.id, u.nombre;

-- Vista de estadísticas generales
CREATE OR REPLACE VIEW vista_estadisticas_generales AS
SELECT 
    COUNT(DISTINCT u.id) AS total_usuarios,
    COUNT(DISTINCT r.id) AS total_rendiciones,
    COUNT(DISTINCT CASE WHEN r.estado = 'en_revision' THEN r.id END) AS pendientes_aprobacion,
    COALESCE(SUM(CASE WHEN r.estado IN ('aprobada', 'pagada') THEN r.monto_aprobado ELSE 0 END), 0) AS monto_total_aprobado,
    COALESCE(SUM(CASE WHEN r.estado = 'en_revision' THEN r.monto_total ELSE 0 END), 0) AS monto_pendiente
FROM usuarios u
LEFT JOIN rendiciones r ON u.id = r.usuario_id;

-- ================================================
-- PROCEDIMIENTOS ALMACENADOS
-- ================================================

DELIMITER //

-- Procedimiento para aprobar rendición
CREATE PROCEDURE sp_aprobar_rendicion(
    IN p_rendicion_id INT,
    IN p_aprobador_id INT,
    IN p_comentarios TEXT
)
BEGIN
    DECLARE v_usuario_id INT;
    
    -- Actualizar rendición
    UPDATE rendiciones
    SET estado = 'aprobada',
        aprobador_id = p_aprobador_id,
        fecha_aprobacion = NOW(),
        comentarios_aprobador = p_comentarios,
        monto_aprobado = monto_total
    WHERE id = p_rendicion_id;
    
    -- Obtener usuario de la rendición
    SELECT usuario_id INTO v_usuario_id
    FROM rendiciones
    WHERE id = p_rendicion_id;
    
    -- Crear notificación
    INSERT INTO notificaciones (usuario_id, titulo, mensaje, tipo, rendicion_id)
    SELECT 
        v_usuario_id,
        'Rendición Aprobada',
        CONCAT('Tu rendición ', numero_rendicion, ' ha sido aprobada'),
        'success',
        p_rendicion_id
    FROM rendiciones
    WHERE id = p_rendicion_id;
END //

DELIMITER ;

-- ================================================
-- TRIGGERS (Opcional)
-- ================================================

DELIMITER //

CREATE TRIGGER trg_actualizar_monto_total_insert
AFTER INSERT ON items_rendicion
FOR EACH ROW
BEGIN
    UPDATE rendiciones
    SET monto_total = (
        SELECT COALESCE(SUM(monto), 0)
        FROM items_rendicion
        WHERE rendicion_id = NEW.rendicion_id
    )
    WHERE id = NEW.rendicion_id;
END //

CREATE TRIGGER trg_actualizar_monto_total_update
AFTER UPDATE ON items_rendicion
FOR EACH ROW
BEGIN
    UPDATE rendiciones
    SET monto_total = (
        SELECT COALESCE(SUM(monto), 0)
        FROM items_rendicion
        WHERE rendicion_id = NEW.rendicion_id
    )
    WHERE id = NEW.rendicion_id;
END //

CREATE TRIGGER trg_actualizar_monto_total_delete
AFTER DELETE ON items_rendicion
FOR EACH ROW
BEGIN
    UPDATE rendiciones
    SET monto_total = (
        SELECT COALESCE(SUM(monto), 0)
        FROM items_rendicion
        WHERE rendicion_id = OLD.rendicion_id
    )
    WHERE id = OLD.rendicion_id;
END //

DELIMITER ;

-- ================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ================================================

-- Índices compuestos para consultas frecuentes
CREATE INDEX idx_rendiciones_usuario_estado ON rendiciones(usuario_id, estado);
CREATE INDEX idx_rendiciones_estado_fecha ON rendiciones(estado, fecha_creacion);
CREATE INDEX idx_notificaciones_usuario_leida ON notificaciones(usuario_id, leida);

-- ================================================
-- PERMISOS (Ajustar según necesidad)
-- ================================================

-- Crear usuario de aplicación (ejemplo)
-- CREATE USER 'rendiciones_app'@'localhost' IDENTIFIED BY 'password_seguro';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON rendiciones_primar.* TO 'rendiciones_app'@'localhost';
-- FLUSH PRIVILEGES;

-- ================================================
-- FIN DEL SCRIPT
-- ================================================

SELECT 'Base de datos creada exitosamente' AS Mensaje;