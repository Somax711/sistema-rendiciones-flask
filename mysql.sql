CREATE USER 'rendiciones_user'@'localhost'
IDENTIFIED WITH mysql_native_password
BY 'Admin1234';
CREATE DATABASE IF NOT EXISTS sistema_rendiciones
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON sistema_rendiciones.* 
TO 'rendiciones_user'@'localhost';
FLUSH PRIVILEGES;
USE sistema_rendiciones;
DROP TABLE IF EXISTS item_rendicion;
DROP TABLE IF EXISTS rendicion;
DROP TABLE IF EXISTS notificacion;
DROP TABLE IF EXISTS user;
