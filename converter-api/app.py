from flask import Flask

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
import os
from entrypoints.web import vistas
from entrypoints.events import consumer
# Importamos la BD
from repositorios.db_model.db_model import db

def create_app(): 
    app = Flask(__name__)  #constructor con el nombre de la aplicación

    # BD sin usuario ni contraseña
    host = os.getenv('POSTGRES_HOST','localhost')
    user = os.getenv('POSTGRES_USER','postgres')
    database = os.getenv('POSTGRES_DB','postgres')
    port = os.getenv('POSTGRES_PORT',6379)
    DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}@{host}:{port}/{database}'
    #app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///converter.db'

    # Deshabilitar un flag para que SQlAlchemy no genera track de modificaciones
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #JWT
    app.config['JWT_SECRET_KEY'] = 'frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    app_context = app.app_context()
    app_context.push()



    #Inicializamos la BD
    db.init_app(app)
    db.create_all()

    cors = CORS(app)

    api = Api(app)
    api.add_resource(vistas.VistaHealth, '/health')
    api.add_resource(vistas.VistaSignUp, '/api/auth/signup')
    api.add_resource(vistas.VistaLogin, '/api/auth/login')
    api.add_resource(vistas.VistaTask, '/api/tasks')

    if os.getenv('START_KAFKA_CONSUMER','False') == 'True':
        consumer.start()
    
    
    jwt = JWTManager(app)
    return app

if __name__ == '__main__':
    create_app().run(host="0.0.0.0", port=os.environ.get('PORT', 5000))