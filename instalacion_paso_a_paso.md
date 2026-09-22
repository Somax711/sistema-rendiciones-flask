## Sistema de Rendiciones - Python Flask

Esta guía te llevará desde cero hasta tener el sistema funcionando completamente.

---

##  Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación de Requisitos Previos](#instalación-de-requisitos-previos)
3. [Configuración del Proyecto](#configuración-del-proyecto)
4. [Configuración de la Base de Datos](#configuración-de-la-base-de-datos)
5. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
6. [Inicialización del Sistema](#inicialización-del-sistema)
7. [Primer Inicio](#primer-inicio)
8. [Verificación del Sistema](#verificación-del-sistema)
9. [Crear Ejecutable (Opcional)](#crear-ejecutable-opcional)
10. [Solución de Problemas](#solución-de-problemas)

---

##  Requisitos del Sistema

### Mínimos:
- **Sistema Operativo**: Windows 10+, Linux, macOS
- **RAM**: 2 GB mínimo, 4 GB recomendado
- **Disco**: 500 MB libres
- **Procesador**: Cualquier procesador moderno

### Software Necesario:
- Python 3.9 o superior
- MySQL 8.0 o MariaDB 10.5+
- Navegador web moderno (Chrome, Firefox, Edge)

---

##  Instalación de Requisitos Previos

### Paso 1: Instalar Python

#### Windows:
1. Descargar Python desde https://www.python.org/downloads/
2. Ejecutar el instalador
3.  **IMPORTANTE**: Marcar "Add Python to PATH"
4. Click en "Install Now"
5. Verificar instalación:
```cmd
python --version
pip --version
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

#### macOS:
```bash
brew install python3
python3 --version
```

### Paso 2: Instalar MySQL

#### Windows:
1. Descargar MySQL Installer desde https://dev.mysql.com/downloads/installer/
2. Ejecutar instalador
3. Seleccionar "Developer Default"
4. Configurar contraseña de root (anotar esta contraseña!)
5. Completar instalación

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

#### macOS:
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

### Paso 3: Verificar MySQL

```bash
# Windows 
mysql -u root -p

# Linux/Mac
sudo mysql -u root -p
```

Deberías ver el prompt de MySQL: `mysql>`

---

##  Configuración del Proyecto

### Paso 1: Crear Carpeta del Proyecto

```bash
# Elegir una ubicación (ejemplo: Documentos)
cd C:\Users\TuUsuario\Documents    # Windows
cd ~/Documents                      # Linux/Mac

# Crear carpeta
mkdir sistema-rendiciones-flask
cd sistema-rendiciones-flask
```

### Paso 2: Copiar Archivos

Copiar todos los archivos del sistema a esta carpeta:

```
sistema-rendiciones-flask/
├── app.py
├── config.py
├── requirements.txt
├── init_db.py
├── create_admin.py
├── build_exe.py
├── .env.example
├── database_schema.sql
├── models/
├── routes/
├── templates/
├── static/
└── utils/
```

### Paso 3: Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

Deberías ver `(venv)` al inicio de tu línea de comandos.

### Paso 4: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto tomará unos minutos. Deberías ver mensajes de instalación exitosa.

---

##  Configuración de la Base de Datos

### Paso 1: Crear Base de Datos

Abrir MySQL:
```bash
mysql -u root -p
# Ingresar la contraseña de root
```

Ejecutar:
```sql
CREATE DATABASE rendiciones_primar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;
```

Deberías ver `rendiciones_primar` en la lista.

### Paso 2: Crear Estructura (Opcional - Método Manual)

Si quieres usar el script SQL completo:
```bash
mysql -u root -p rendiciones_primar < database_schema.sql
```

**O usa el método automático en el Paso de Inicialización →**

Salir de MySQL:
```sql
EXIT;
```

---

##  Configuración de Variables de Entorno

### Paso 1: Crear Archivo .env

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### Paso 2: Editar .env

Abrir `.env` con un editor de texto y modificar:

```env
# Cambiar estos valores:
SECRET_KEY=tu-clave-super-secreta-genera-una-nueva
DATABASE_URL=mysql+pymysql://root:TU_PASSWORD_MYSQL@localhost/rendiciones_primar

# Configuración de Email (si quieres recuperación de contraseña)
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-password-de-aplicacion
```

#### Generar SECRET_KEY segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copiar el resultado al archivo `.env`

#### Configurar Email (Gmail):

1. Ir a Google Account: https://myaccount.google.com/security
2. Activar verificación en dos pasos
3. Ir a "Contraseñas de aplicaciones"
4. Generar nueva contraseña para "Correo"
5. Copiar la contraseña de 16 caracteres al `.env`

---

##  Inicialización del Sistema

### Paso 1: Crear Tablas y Usuario Admin

```bash
python init_db.py
```

Deberías ver:
```
✓ Tablas creadas exitosamente
✓ Usuario administrador creado:
  Email: admin@primar.cl
  Contraseña: Admin123!
```

### Paso 2: Crear Carpetas de Uploads

```bash
# Windows
mkdir uploads
mkdir uploads\comprobantes

# Linux/Mac
mkdir -p uploads/comprobantes
```

---

##  Primer Inicio

### Paso 1: Iniciar la Aplicación

```bash
python app.py
```

Deberías ver:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Paso 2: Abrir en Navegador

Abrir navegador e ir a: **http://localhost:5000**

### Paso 3: Primer Login

Usar credenciales por defecto:
- **Email**: admin@primar.cl
- **Contraseña**: Admin123!

¡Deberías ver el dashboard de administrador! 🎉

---

## ✔️ Verificación del Sistema

### Checklist de Funcionalidades:

- [ ] Login funciona correctamente
- [ ] Dashboard se muestra
- [ ] Puedes crear un nuevo usuario
- [ ] Puedes crear una rendición
- [ ] Puedes subir comprobantes
- [ ] Las notificaciones funcionan
- [ ] Puedes aprobar/rechazar (con usuario aprobador)
- [ ] Los reportes se generan

### Crear Usuario de Prueba:

1. Login como admin
2. Ir a "Usuarios" → "Crear Usuario"
3. Completar datos:
   - Nombre: Usuario Prueba
   - Email: prueba@test.cl
   - Contraseña: Test123!
   - Rol: Usuario
4. Guardar
5. Cerrar sesión
6. Login con el nuevo usuario

### Crear Rendición de Prueba:

1. Login como usuario
2. "Nueva Rendición"
3. Completar datos del periodo
4. Agregar items de gastos
5. Subir comprobantes
6. Guardar
7. Enviar a revisión

---

##  Crear Ejecutable (Opcional)

Para crear un archivo `.exe` standalone:

### Paso 1: Instalar PyInstaller

```bash
pip install pyinstaller
```

### Paso 2: Crear Ejecutable

```bash
python build_exe.py
```

### Paso 3: Ubicar el Ejecutable

El archivo estará en: `dist/SistemaRendiciones.exe`

### Paso 4: Distribuir

Copiar la carpeta `dist/` completa al servidor o equipo destino.

**IMPORTANTE**: 
- Necesita MySQL instalado en el equipo destino
- Configurar `.env` en la carpeta del ejecutable
- Crear carpeta `uploads/`

---

##  Solución de Problemas

### Problema: "ModuleNotFoundError: No module named 'X'"

**Solución**:
```bash
# Asegurarse de que el entorno virtual esté activado
pip install -r requirements.txt
```

### Problema: "Can't connect to MySQL server"

**Solución**:
1. Verificar que MySQL esté corriendo:
   ```bash
   # Windows
   net start MySQL
   
   # Linux
   sudo systemctl start mysql
   ```

2. Verificar credenciales en `.env`

3. Probar conexión manual:
   ```bash
   mysql -u root -p
   ```

### Problema: "Access denied for user 'root'@'localhost'"

**Solución**:
Verificar contraseña en `.env`:
```env
DATABASE_URL=mysql+pymysql://root:TU_PASSWORD_CORRECTA@localhost/rendiciones_primar
```

### Problema: Email no se envía

**Solución**:
1. Usar "Contraseña de aplicación" de Gmail, no tu contraseña normal
2. Verificar que la verificación en dos pasos esté activada
3. Revisar configuración en `.env`

### Problema: Error al subir archivos

**Solución**:
```bash
# Verificar que exista la carpeta
mkdir -p uploads/comprobantes

# Linux: Verificar permisos
chmod 755 uploads/
```

### Problema: Página en blanco después de login

**Solución**:
1. Abrir consola del navegador (F12)
2. Ver errores en "Console"
3. Verificar que todos los archivos estáticos existan
4. Reiniciar la aplicación

### Problema: "Port 5000 is already in use"

**Solución**:
Cambiar puerto en `app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

---

##  Obtener Ayuda

Si encuentras problemas no listados aquí:

1. **Verificar logs**: La aplicación muestra errores en la consola
2. **Revisar README.md**: Documentación completa
3. **Crear issue**: En el repositorio del proyecto
4. **Contactar soporte**: Al equipo de desarrollo

---

##  Próximos Pasos

Una vez que el sistema esté funcionando:

1. **Cambiar contraseña de admin**: Por seguridad
2. **Crear usuarios reales**: Para tu equipo
3. **Configurar email**: Para notificaciones
4. **Personalizar**: Logo, colores, etc.
5. **Configurar backups**: De la base de datos
6. **Desplegar en producción**: Si es necesario

---

##  Lista de Verificación Final

Antes de usar en producción:

- [ ] SECRET_KEY cambiada a valor único
- [ ] Contraseña de admin cambiada
- [ ] Email configurado correctamente
- [ ] Backups de BD configurados
- [ ] SSL/HTTPS configurado (en producción)
- [ ] Firewall configurado
- [ ] Usuarios de prueba eliminados
- [ ] Permisos de archivos verificados

---