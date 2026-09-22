from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# Importar modelos
from .user import User
from .rendicion import Rendicion
from .item_rendicion import ItemRendicion
from .notificacion import Notificacion

__all__ = ['db', 'login_manager', 'User', 'Rendicion', 'ItemRendicion', 'Notificacion']