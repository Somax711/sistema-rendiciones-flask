from app import create_app
from models import db, User

def init_database():
    app = create_app()
    
    with app.app_context():
        print("Creando tablas...")
        db.create_all()
        print("✓ Tablas creadas exitosamente")
        
        # Verificar si ya existe un admin
        admin = User.query.filter_by(email='admin@primar.cl').first()
        if not admin:
            print("\nCreando usuario administrador por defecto...")
            admin = User(
                nombre='Administrador',
                email='admin@primar.cl',
                rol='admin',
                activo=True,
                email_verificado=True,
                departamento='TI',
                cargo='Administrador del Sistema'
            )
            admin.set_password('Admin123!')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✓ Usuario administrador creado:")
            print("  Email: admin@primar.cl")
            print("  Contraseña: Admin123!")
            print("\n  IMPORTANTE: Cambia esta contraseña después del primer login")
        else:
            print("\n✓ El usuario administrador ya existe")
        
        print("\n✓ Base de datos inicializada correctamente")
        print("\nPuedes iniciar la aplicación con: python app.py")


if __name__ == '__main__':
    init_database()