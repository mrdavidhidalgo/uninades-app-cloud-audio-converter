import enum
from flask_sqlalchemy import SQLAlchemy
import datetime
from marshmallow import fields
from services.model.model import FileFormat, FileStatus
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    mail = db.Column(db.String(80))
    password = db.Column(db.String(10))

class SourceFile(db.Model):
    __tablename__ = "source_file"
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500))
    file_format = db.Column(db.Enum(FileFormat))
    user_owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    task = db.relationship('ConversionTask', cascade='all, delete, delete-orphan')


class ConversionTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_file_id = db.Column(db.Integer, db.ForeignKey('source_file.id'))
    target_file_format = db.Column(db.Enum(FileFormat))
    target_file_path = db.Column(db.String(500))
    status = db.Column(db.Enum(FileStatus))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    duration = db.Column(db.Integer, default = 0)
    
class EnumADiccionario(fields.Field):
    #metodo de la clase
    def  _serialize(self, valor, attr, obj, **kwargs):
        #no serializa los vacios
        if valor is None:
            return None
        #retorna el nombre del enum y el valor
        return {"llave":valor.name, "valor":valor.value}
    
class ConversionTaskSchema(SQLAlchemyAutoSchema):
    tipo = EnumADiccionario(attribute=('target_file_format'))
    class Meta:
        model = ConversionTask
        include_relationships = True
        load_instance = True
        
class SourceFileSchema(SQLAlchemyAutoSchema):
    tipo = EnumADiccionario(attribute=('file_format'))
    class Meta:
        model = SourceFile
        include_relationships = True
        load_instance = True
