## Sistema de Rendiciones Flask
### 1. Preparar Entorno

```bash
# Crear carpeta y entrar
mkdir sistema-rendiciones && cd sistema-rendiciones

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Instalar Dependencias 

```bash
pip install -r requirements.txt
```

### 3. Configurar Base de Datos 

```bash
# Conectar a MySQL
mysql -u root -p

# Crear base de datos
CREATE DATABASE rendiciones_primar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 4. Configurar Variables de Entorno 

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env (cambiar password de MySQL)
# Windows: notepad .env
# Linux/Mac: nano .env
```

Contenido mínimo del `.env`:
```env
SECRET_KEY=mi-clave-secreta-temporal
DATABASE_URL=mysql+pymysql://root:Admin1234@localhost/rendiciones_primar
FLASK_ENV=development
```

### 5. Inicializar Sistema

```bash
python init_db.py
```

### 6. Iniciar

```bash
python app.py
```

Abrir navegador: **http://localhost:5000**

**Login**:
- Email: `admin@primar.cl`
- Password: `Admin1234!`

---

##  Verificación Rápida

### ¿Funcionó?
- [ ] Ves la página de login
- [ ] Puedes hacer login
- [ ] Ves el dashboard
- [ ] Puedes crear una rendición

### ¿No funcionó?

**Error de MySQL:**
```bash
# Verificar que MySQL esté corriendo
# Windows:
net start MySQL

# Linux:
sudo systemctl start mysql
```

**Error de módulos:**
```bash
pip install -r requirements.txt
```

**Puerto 5000 ocupado:**
Cambiar puerto en `app.py` línea final:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```
---

##  Checklist Post-Instalación

Después de que funcione:

1. **Cambiar contraseña de admin**
   - Login → Mi Perfil → Cambiar Contraseña

2. **Crear tu primer usuario**
   - Usuarios → Crear Usuario

3. **Crear rendición de prueba**
   - Nueva Rendición → Agregar Items → Guardar

4. **Configurar email (opcional)**
   - Editar `.env` con tus credenciales SMTP

---

##  Próximos Pasos

1. Lee `README.md` para documentación completa
2. Lee `INSTALACION_PASO_A_PASO.md` para guía detallada
3. Lee `ESTRUCTURA_COMPLETA_PROYECTO.md` para entender la arquitectura

---

##  Comandos Útiles

```bash
# Ver logs
python app.py

# Crear usuario admin adicional
python create_admin.py

# Crear ejecutable
python build_exe.py

# Reiniciar base de datos ( borra todo)
python init_db.py
```

---

##  Ayuda Rápida

**Olvidé la contraseña de admin:**

```bash
# Recrear usuario admin
python init_db.py

# Esto recreará el usuario con password: Admin1234!
```

**No puedo subir archivos:**
```bash
# Crear carpetas necesarias
mkdir -p uploads/comprobantes
```

**Error "Access Denied" en MySQL:**
```bash
# Verificar password en .env

##  Acceso desde Otros Dispositivos

Si quieres acceder desde otro dispositivo en tu red:

1. Averiguar tu IP:
   ```bash
   # Windows:
   ipconfig
   # Linux/Mac:
   ifconfig
   ```

2. Abrir en otro dispositivo:
   ```
   http://TU_IP:5000
   ```

   Ejemplo: `http://192.168.1.100:5000`

---

##  ¡Listo!

El sistema está funcionando. Ahora puedes:

-  Crear rendiciones
-  Gestionar usuarios
-  Aprobar/rechazar gastos
-  Generar reportes
-  Exportar a Excel

**Necesitas más ayuda?** → Consulta la documentación completa en README.md