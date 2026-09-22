#Sistema de Rendiciones - Flask

Sistema completo de gestión de rendiciones (gastos) desarrollado en Python Flask. 
##  Características

### Autenticación y Seguridad
-  Login con usuario y contraseña
-  Recuperación de contraseña por email
-  Autenticación de dos factores (MFA/2FA) opcional
-  Encriptación de contraseñas con BCrypt
-  Sesiones seguras
-  Login con usuario y contraseña
-  Recuperación de contraseña por email
-  Autenticación de dos factores (MFA/2FA) opcional
-  Encriptación de contraseñas con BCrypt
-  Sesiones seguras

### Gestión de Rendiciones
-  Crear, editar y eliminar rendiciones
-  Múltiples items por rendición
-  Carga de comprobantes (PDF, imágenes)
-  Estados: Pendiente, En Revisión, Aprobada, Rechazada, Pagada
-  Comentarios y observaciones

### Sistema de Aprobaciones
-  Flujo de aprobación con roles
-  Notificaciones automáticas
-  Historial de aprobaciones
-  Flujo de aprobación con roles
-  Notificaciones automáticas
-  Historial de aprobaciones

### Roles de Usuario
- **Admin**: Control total del sistema
- **Aprobador**: Aprobar/rechazar rendiciones
- **Usuario**: Crear y gestionar sus rendiciones

### Reportes
-  Exportación a Excel
-  Reportes por fecha, usuario, estado
-  Dashboard con estadísticas
-  Gráficos y métricas
-  Exportación a Excel
-  Reportes por fecha, usuario, estado
-  Dashboard con estadísticas
-  Gráficos y métricas

##  Instalación Rápida

### Requisitos Previos

```bash
Python 3.9 o superior
MySQL 8.0 o MariaDB 10.5+
pip (gestor de paquetes Python)
```

### Paso 1: Clonar o Descargar

```bash
# Si tienes el código en un ZIP, descomprímelo
# O clona desde repositorio:
git clone [https://github.com/Somax711/sistema_rendiciones]
cd sistema-rendiciones-flask
```

### Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Base de Datos

```sql
-- En MySQL/MariaDB, crear la base de datos:
CREATE DATABASE rendiciones_primar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Paso 5: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus datos
```

### Paso 6: Inicializar Base de Datos

```bash
# Crear tablas y usuario admin
python init_db.py
```

Credenciales por defecto:
- **Email**: admin@primar.cl
- **Contraseña**: Admin1234!

### Paso 7: Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

##  Crear Ejecutable (Opcional)

Para crear un ejecutable standalone de Windows:

```bash
python build_exe.py
```

El ejecutable se creará en `dist/SistemaRendiciones.exe`

##  Estructura del Proyecto

```
sistema-rendiciones-flask/
│
├── app.py                      # Aplicación principal
├── config.py                   # Configuraciones
├── requirements.txt            # Dependencias
├── .env                        # Variables de entorno (crear desde .env.example)
│
├── models/                     # Modelos de datos
│   ├── user.py                # Usuario
│   ├── rendicion.py           # Rendición
│   ├── item_rendicion.py      # Item de rendición
│   └── notificacion.py        # Notificaciones
│
├── routes/                     # Controladores/Rutas
│   ├── auth.py                # Autenticación
│   ├── dashboard.py           # Dashboard
│   ├── rendiciones.py         # CRUD Rendiciones
│   ├── aprobaciones.py        # Aprobaciones
│   ├── usuarios.py            # Gestión usuarios
│   ├── reportes.py            # Reportes
│   └── notificaciones.py      # Notificaciones
│
├── templates/                  # Vistas HTML
│   ├── layout.html            # Template base
│   ├── auth/                  # Login, recuperación
│   ├── dashboard/             # Dashboards por rol
│   ├── rendiciones/           # CRUD rendiciones
│   ├── usuarios/              # Gestión usuarios
│   └── reportes/              # Reportes
│
├── static/                     # Archivos estáticos
│   ├── css/                   # Estilos
│   ├── js/                    # JavaScript
│   └── images/                # Imágenes
│
├── uploads/                    # Archivos subidos
│   └── comprobantes/          # Comprobantes de gastos
│
└── utils/                      # Utilidades
    ├── decorators.py          # Decoradores
    ├── email.py               # Envío de emails
    └── filters.py             # Filtros Jinja2
```

##  Configuración Detallada

### Base de Datos

Editar en `.env`:

```env
DATABASE_URL=mysql+pymysql://usuario:contraseña@host:puerto/base_datos
```

Ejemplos:
```env
# Local
DATABASE_URL=mysql+pymysql://root:mipassword@localhost/rendiciones_primar

# Servidor remoto
DATABASE_URL=mysql+pymysql://admin:pass123@192.168.1.100:3306/rendiciones_primar
```

### Email (para recuperación de contraseña)

#### Gmail

1. Habilitar verificación en dos pasos en tu cuenta Google
2. Crear "Contraseña de aplicación":
   - Cuenta Google → Seguridad → Verificación en dos pasos
   - Contraseñas de aplicaciones
   - Seleccionar "Correo" y copiar la contraseña generada

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=la-contraseña-de-aplicacion-de-16-caracteres
```

#### Otros Proveedores

**Outlook/Hotmail:**
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
```

**Yahoo:**
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
```

##  Gestión de Usuarios

### Crear Usuario Administrador

```bash
python create_admin.py
```

### Crear Usuario desde Código

```python
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    usuario = User(
        nombre='Juan Pérez',
        email='juan@empresa.cl',
        rol='usuario',  # o 'aprobador', 'admin'
        activo=True
    )
    usuario.set_password('MiPassword123!')
    db.session.add(usuario)
    db.session.commit()
```

##  Uso del Sistema

### Como Usuario

1. Login con tus credenciales
2. Dashboard → Nueva Rendición
3. Completar información general
4. Agregar items de gastos con comprobantes
5. Enviar a revisión
6. Recibir notificación de aprobación/rechazo

### Como Aprobador

1. Login con credenciales de aprobador
2. Ir a "Aprobaciones"
3. Revisar rendiciones pendientes
4. Aprobar o rechazar con comentarios
5. Ver historial de aprobaciones

### Como Administrador

- Acceso total al sistema
- Gestión de usuarios
- Reportes completos
- Configuración del sistema

##  Seguridad

### Implementada

-  Contraseñas hasheadas con BCrypt
-  Protección CSRF en todos los formularios
-  Validación de tipos de archivo
-  Sanitización de inputs
-  Sesiones con timeout
-  Headers de seguridad HTTP
-  Contraseñas hasheadas con BCrypt
-  Protección CSRF en todos los formularios
-  Validación de tipos de archivo
-  Sanitización de inputs
-  Sesiones con timeout
-  Headers de seguridad HTTP

### Recomendaciones Producción

1. **HTTPS obligatorio**
2. **Firewall** en puerto MySQL (3306)
3. **Backups automáticos** de base de datos
4. **Cambiar SECRET_KEY** a valor único
5. **Limitar intentos de login**
6. **Monitoreo de logs**

##  Solución de Problemas

### Error: "Can't connect to MySQL server"

```bash
# Verificar que MySQL esté corriendo
# Windows:
net start MySQL

# Linux:
sudo systemctl start mysql
sudo systemctl status mysql
```

### Error: "ModuleNotFoundError"

```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error al subir archivos

```bash
# Verificar permisos de carpeta uploads
# Linux:
chmod 755 uploads/
chown -R www-data:www-data uploads/

# Windows: Verificar permisos de la carpeta
```

### Email no se envía

1. Verificar configuración SMTP
2. Para Gmail, usar "Contraseña de aplicación"
3. Verificar firewall/antivirus
4. Revisar logs en consola

##  Despliegue en Producción

### Opción 1: Con Gunicorn (Linux)

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Con archivo de configuración
gunicorn -c gunicorn_config.py app:app
```

### Opción 2: Con Apache/Nginx (Linux)

Ver documentación de Flask con mod_wsgi o Nginx reverse proxy

### Opción 3: Ejecutable Windows

```bash
python build_exe.py
# Copiar dist/ al servidor
# Ejecutar SistemaRendiciones.exe
```

### Opción 4: Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t sistema-rendiciones .
docker run -p 5000:5000 -d sistema-rendiciones
```


##  Licencia

Este proyecto es privado y propietario.


##  Soporte

Para reportar problemas o solicitar ayuda:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

##  Recursos Adicionales

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)

---
