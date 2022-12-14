from flask import Flask

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
import os
from entrypoints.web import vistas
from entrypoints.events import kafka_consumer, gcp_pubsub_subscriber
# Importamos la BD
from repositorios.db_model.db_model import db
from datetime import timedelta


def app(): 
    #constructor con el nombre de la aplicación
    app = Flask(__name__) 
    # BD sin usuario ni contraseña
    host = os.getenv('POSTGRES_HOST','db')
    #host = os.getenv('POSTGRES_HOST','localhost')
    user = os.getenv('POSTGRES_USER','postgres')
    database = os.getenv('POSTGRES_DB','postgres')
    password = os.getenv('POSTGRES_PASSWORD','postgres')
    #port = os.getenv('POSTGRES_PORT',6379)
    port = os.getenv('POSTGRES_PORT',5432)
    DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI

    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///converter.db'

    # Deshabilitar un flag para que SQlAlchemy no genera track de modificaciones
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #JWT
    app.config['JWT_SECRET_KEY'] = 'frase-secreta'
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
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
    api.add_resource(vistas.VistaTasks, '/api/tasks')
    api.add_resource(vistas.VistaTask, '/api/tasks/<int:task_id>')
    api.add_resource(vistas.VistaFiles, '/api/files/<string:file_name>')
    



    if os.getenv('START_KAFKA_CONSUMER','False') == 'True':
        gcp_pubsub_subscriber.start()
        #kafka_consumer.start()
        
    
    
    
    jwt = JWTManager(app)
    return app

app = app()
if __name__ == '__main__':
    app.run()