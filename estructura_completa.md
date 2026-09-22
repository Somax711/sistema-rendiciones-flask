#  Estructura Completa del Proyecto

## Sistema de Rendiciones - Python Flask

---

##  Resumen Ejecutivo

Este documento describe la estructura completa del proyecto **Sistema de Rendiciones** desarrollado en Python Flask como réplica del sistema ASP.NET Core original.

### Características Principales:
-  Sistema de autenticación completo con MFA
-  Gestión de rendiciones con múltiples items
-  Sistema de aprobaciones por roles
-  Notificaciones en tiempo real
-  Reportes y exportación a Excel
-  Dashboard personalizado por rol
-  Subida de comprobantes

---

##  Estructura de Archivos

```
sistema-rendiciones-flask/
│
├──  app.py                           # Aplicación Flask principal
├──  config.py                        # Configuraciones del sistema
├──  requirements.txt                 # Dependencias Python
├──  .env                            # Variables de entorno (crear desde .env.example)
├──  .env.example                    # Plantilla de variables de entorno
├──  .gitignore                      # Archivos a ignorar en Git
│
├──  init_db.py                      # Script de inicialización de BD
├──  create_admin.py                 # Script para crear usuarios admin
├──  build_exe.py                    # Script para crear ejecutable
├──  database_schema.sql             # Estructura completa de BD
│
├──  README.md                       # Documentación principal
├──  INSTALACION_PASO_A_PASO.md     # Guía de instalación detallada
├──  ESTRUCTURA_COMPLETA_PROYECTO.md # Este archivo
│
├──  models/                         # Modelos de Base de Datos
│   ├── __init__.py                   # Inicialización de modelos
│   ├── user.py                       # Modelo Usuario
│   ├── rendicion.py                  # Modelo Rendición
│   ├── item_rendicion.py             # Modelo Item de Rendición
│   └── notificacion.py               # Modelo Notificación
│
├──  routes/                         # Controladores/Rutas
│   ├── __init__.py                   # Registro de blueprints
│   ├── auth.py                       # Autenticación y login
│   ├── dashboard.py                  # Dashboard principal
│   ├── rendiciones.py                # CRUD de rendiciones
│   ├── aprobaciones.py               # Sistema de aprobaciones
│   ├── usuarios.py                   # Gestión de usuarios (admin)
│   ├── reportes.py                   # Generación de reportes
│   └── notificaciones.py             # Sistema de notificaciones
│
├──  templates/                      # Plantillas HTML (Jinja2)
│   ├── layout.html                   # Template base
│   │
│   ├──  auth/                      # Autenticación
│   │   ├── login.html               # Página de login
│   │   ├── recuperar.html           # Recuperar contraseña
│   │   ├── reset_password.html      # Restablecer contraseña
│   │   ├── mfa.html                 # Verificación MFA
│   │   └── perfil.html              # Perfil de usuario
│   │
│   ├──  dashboard/                 # Dashboards
│   │   ├── admin.html               # Dashboard admin
│   │   ├── aprobador.html           # Dashboard aprobador
│   │   └── usuario.html             # Dashboard usuario
│   │
│   ├──  rendiciones/               # Rendiciones
│   │   ├── index.html               # Lista de rendiciones
│   │   ├── crear.html               # Crear rendición
│   │   ├── editar.html              # Editar rendición
│   │   └── detalle.html             # Detalle de rendición
│   │
│   ├──  aprobaciones/              # Aprobaciones
│   │   ├── index.html               # Lista pendientes
│   │   ├── revisar.html             # Revisar rendición
│   │   └── historial.html           # Historial
│   │
│   ├──  usuarios/                  # Usuarios
│   │   ├── index.html               # Lista usuarios
│   │   ├── crear.html               # Crear usuario
│   │   ├── editar.html              # Editar usuario
│   │   └── detalle.html             # Detalle usuario
│   │
│   ├──  reportes/                  # Reportes
│   │   ├── index.html               # Menú reportes
│   │   ├── rendiciones.html         # Reporte rendiciones
│   │   └── estadisticas.html        # Estadísticas
│   │
│   ├──  notificaciones/            # Notificaciones
│   │   └── index.html               # Lista notificaciones
│   │
│   ├──  emails/                    # Templates de email
│   │   ├── reset_password.html      # Email recuperación
│   │   ├── nueva_rendicion.html     # Email nueva rendición
│   │   ├── rendicion_aprobada.html  # Email aprobada
│   │   └── rendicion_rechazada.html # Email rechazada
│   │
│   └──  errors/                    # Páginas de error
│       ├── 403.html                 # Acceso denegado
│       ├── 404.html                 # No encontrado
│       └── 500.html                 # Error servidor
│
├──  static/                         # Archivos estáticos
│   ├──  css/                       # Estilos
│   │   ├── bootstrap.min.css        # Bootstrap 5
│   │   └── custom.css               # Estilos personalizados
│   │
│   ├──  js/                        # JavaScript
│   │   ├── jquery.min.js            # jQuery
│   │   ├── bootstrap.bundle.min.js  # Bootstrap JS
│   │   └── main.js                  # JavaScript principal
│   │
│   └──  images/                    # Imágenes
│       ├── logo.png                 # Logo del sistema
│       └── logo.ico                 # Favicon
│
├──  uploads/                        # Archivos subidos
│   └──  comprobantes/              # Comprobantes de gastos
│       └── .gitkeep                 # Mantener carpeta en Git
│
└──  utils/                          # Utilidades
    ├── __init__.py                   # Exportación de utilidades
    ├── decorators.py                 # Decoradores personalizados
    ├── email.py                      # Envío de emails
    └── filters.py                    # Filtros Jinja2 personalizados
```

---

##  Archivos Principales

### 1. app.py
**Propósito**: Punto de entrada de la aplicación
**Contenido**:
- Configuración de Flask
- Registro de blueprints
- Inicialización de extensiones
- Manejadores de errores
- Comandos CLI

### 2. config.py
**Propósito**: Configuraciones del sistema
**Contenido**:
- Configuración de base de datos
- Configuración de email
- Configuración de sesiones
- Configuración de archivos

### 3. requirements.txt
**Propósito**: Dependencias del proyecto
**Principales librerías**:
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- PyMySQL 1.1.0
- bcrypt 4.1.2
- openpyxl 3.1.2
- pyotp 2.9.0

---

##  Modelos de Base de Datos

### User (Usuario)
- Autenticación y autorización
- Roles: admin, aprobador, usuario
- MFA opcional
- Recuperación de contraseña

### Rendicion (Rendición)
- Información general
- Estados: pendiente → en_revision → aprobada/rechazada → pagada
- Relación con usuario y aprobador
- Cálculo automático de montos

### ItemRendicion (Item de Rendición)
- Gastos individuales
- Comprobantes adjuntos
- Tipos de documento
- Montos en CLP

### Notificacion (Notificación)
- Alertas del sistema
- Estados: leída/no leída
- Tipos: info, success, warning, error

---

##  Rutas Principales

### Autenticación (`/auth`)
- `/auth/login` - Login
- `/auth/logout` - Cerrar sesión
- `/auth/recuperar` - Recuperar contraseña
- `/auth/reset/<token>` - Restablecer contraseña
- `/auth/perfil` - Perfil de usuario
- `/auth/verify-mfa` - Verificación MFA

### Dashboard (`/dashboard`)
- `/dashboard/` - Dashboard según rol

### Rendiciones (`/rendiciones`)
- `/rendiciones/` - Lista de rendiciones
- `/rendiciones/crear` - Crear rendición
- `/rendiciones/<id>` - Ver detalle
- `/rendiciones/<id>/editar` - Editar
- `/rendiciones/<id>/eliminar` - Eliminar
- `/rendiciones/<id>/enviar` - Enviar a revisión

### Aprobaciones (`/aprobaciones`)
- `/aprobaciones/` - Pendientes de aprobación
- `/aprobaciones/<id>/revisar` - Revisar rendición
- `/aprobaciones/<id>/aprobar` - Aprobar
- `/aprobaciones/<id>/rechazar` - Rechazar
- `/aprobaciones/historial` - Historial

### Usuarios (`/usuarios`) - Solo Admin
- `/usuarios/` - Lista de usuarios
- `/usuarios/crear` - Crear usuario
- `/usuarios/<id>/editar` - Editar usuario
- `/usuarios/<id>/eliminar` - Eliminar usuario

### Reportes (`/reportes`) - Admin y Aprobador
- `/reportes/` - Menú de reportes
- `/reportes/rendiciones` - Reporte de rendiciones
- `/reportes/rendiciones/exportar` - Exportar a Excel
- `/reportes/estadisticas` - Estadísticas generales

### Notificaciones (`/notificaciones`)
- `/notificaciones/` - Lista de notificaciones
- `/notificaciones/api/list` - API de notificaciones
- `/notificaciones/<id>/marcar-leida` - Marcar como leída

---

##  Frontend

### Tecnologías
- **Bootstrap 5**: Framework CSS
- **Bootstrap Icons**: Iconos
- **jQuery 3.7**: Manipulación DOM
- **CSS Custom**: Estilos personalizados

### Componentes Principales
- Navbar responsive
- Cards con estadísticas
- Tablas con paginación
- Formularios validados
- Modales
- Alerts/Toasts
- Dropdown de notificaciones

---

##  Seguridad Implementada

### Autenticación
- Contraseñas hasheadas con BCrypt
- Sesiones seguras con Flask-Login
- MFA opcional con PyOTP
- Tokens de recuperación con expiración

### Autorización
- Decoradores de permisos
- Verificación por roles
- Control de acceso a rutas

### Protección de Datos
- Validación de inputs
- Sanitización de datos
- CSRF protection
- Límites de archivos
- Validación de tipos de archivo

---

##  Sistema de Notificaciones

### Tipos
- **In-app**: Notificaciones en el sistema
- **Email**: Notificaciones por correo

### Eventos que Generan Notificaciones
1. Nueva rendición enviada a revisión
2. Rendición aprobada
3. Rendición rechazada
4. Recuperación de contraseña

---

##  Reportes y Exportaciones

### Reportes Disponibles
1. **Reporte de Rendiciones**: Con filtros por fecha, estado, usuario
2. **Estadísticas Generales**: Dashboard con métricas
3. **Detalle de Rendición**: Exportación individual a Excel

### Formato de Exportación
- Excel (.xlsx) con formato profesional
- Headers con estilo
- Datos formateados
- Múltiples hojas si es necesario

---

##  Deployment

### Desarrollo
```bash
python app.py
# Acceder a http://localhost:5000
```

### Producción con Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Ejecutable Windows
```bash
python build_exe.py
# Resultado: dist/SistemaRendiciones.exe
```

### Docker (Ejemplo)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

---

##  Testing

### Usuarios de Prueba
```
Admin:
- Email: admin@primar.cl
- Password: Admin123!

Aprobador:
- Email: aprobador@primar.cl
- Password: Admin123!

Usuario:
- Email: usuario@primar.cl
- Password: Admin123!
```

---

##  Logs y Debugging

### Logs en Desarrollo
Los logs se muestran en consola con nivel DEBUG

### Logs en Producción
Configurar logging a archivo:
```python
import logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

##  Flujo de Trabajo

### Flujo de Rendición
```
1. Usuario crea rendición (estado: pendiente)
2. Usuario agrega items y comprobantes
3. Usuario envía a revisión (estado: en_revision)
4. Aprobador recibe notificación
5. Aprobador revisa y decide
   a. Aprobar (estado: aprobada)
   b. Rechazar (estado: rechazada)
6. Usuario recibe notificación
7. Admin puede marcar como pagada (estado: pagada)
```

---

##  Próximos Pasos Sugeridos

### Mejoras Futuras
1.  API REST completa
2.  Tests automatizados
3.  CI/CD pipeline
4.  Exportación a PDF
5.  Dashboard con gráficos interactivos (Chart.js)
6.  App móvil
7.  Integración con ERP
8.  Firma digital

---

##  Soporte
Para más información, consultar:
- **README.md**: Documentación general
- **INSTALACION_PASO_A_PASO.md**: Guía detallada de instalación
