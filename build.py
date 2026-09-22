import PyInstaller.__main__
import os
import shutil

def build_executable():
    """Construir ejecutable de la aplicación"""
    
    print("=== Construyendo Ejecutable ===\n")
    
    # Limpiar builds anteriores
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Parámetros de PyInstaller
    PyInstaller.__main__.run([
        'app.py',
        '--name=SistemaRendiciones',
        '--onefile',
        '--windowed',
        '--icon=static/images/logo.ico' if os.path.exists('static/images/logo.ico') else '',
        '--add-data=templates:templates',
        '--add-data=static:static',
        '--add-data=.env:.env' if os.path.exists('.env') else '',
        '--hidden-import=pymysql',
        '--hidden-import=flask',
        '--hidden-import=flask_sqlalchemy',
        '--hidden-import=flask_login',
        '--hidden-import=flask_mail',
        '--hidden-import=openpyxl',
        '--hidden-import=pyotp',
        '--hidden-import=qrcode',
        '--collect-all=flask',
        '--collect-all=jinja2',
        '--noconfirm'
    ])
    
    print("\n✓ Ejecutable creado en: dist/SistemaRendiciones.exe")
    print("\nInstrucciones:")
    print("1. Copia la carpeta 'dist' al servidor o equipo de destino")
    print("2. Asegúrate de que MySQL esté instalado y corriendo")
    print("3. Configura el archivo .env con los datos de conexión")
    print("4. Ejecuta SistemaRendiciones.exe")
    print("\nNOTA: El ejecutable necesita acceso a MySQL y las carpetas uploads/")


if __name__ == '__main__':
    build_executable()