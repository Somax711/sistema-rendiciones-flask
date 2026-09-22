from app import create_app
from models import db, User
import getpass


def create_admin():
    """Crear un usuario administrador personalizado"""
    app = create_app()
    
    with app.app_context():
        print("=== Crear Usuario Administrador ===\n")
        
        nombre = input("Nombre completo: ").strip()
        email = input("Email: ").strip().lower()
        
        # Verificar si el email ya existe
        if User.query.filter_by(email=email).first():
            print(f"\n✗ Error: Ya existe un usuario con el email {email}")
            return
        
        # Solicitar contraseña
        while True:
            password = getpass.getpass("Contraseña (mín. 8 caracteres): ")
            if len(password) < 8:
                print("✗ La contraseña debe tener al menos 8 caracteres")
                continue
            
            password_confirm = getpass.getpass("Confirmar contraseña: ")
            if password != password_confirm:
                print("✗ Las contraseñas no coinciden")
                continue
            
            break
        
        departamento = input("Departamento (opcional): ").strip()
        cargo = input("Cargo (opcional): ").strip()
        
        # Crear usuario
        try:
            admin = User(
                nombre=nombre,
                email=email,
                rol='admin',
                activo=True,
                email_verificado=True,
                departamento=departamento if departamento else None,
                cargo=cargo if cargo else None
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            print("\n✓ Usuario administrador creado exitosamente:")
            print(f"  Nombre: {nombre}")
            print(f"  Email: {email}")
            print(f"  Rol: Administrador")
            
        except Exception as e:
            print(f"\n✗ Error al crear usuario: {str(e)}")
            db.session.rollback()


if __name__ == '__main__':
    create_admin()