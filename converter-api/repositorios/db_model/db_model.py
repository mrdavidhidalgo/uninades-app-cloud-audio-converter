import enum
from flask_sqlalchemy import SQLAlchemy
import datetime
from services.model.model import FileFormat, FileStatus

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    username = db.Column(db.String(20))
    mail = db.Column(db.String(80))
    password = db.Column(db.String(10))

class SourceFile(db.Model):
    __tablename__ = "source_file"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    file_path = db.Column(db.String(500))
    file_format = db.Enum(FileFormat)
    user_owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    task = db.relationship('ConversionTask', cascade='all, delete, delete-orphan')


class ConversionTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_file_id = db.Column(db.Integer, db.ForeignKey('source_file.id'))
    target_file_format = db.Enum(FileFormat)
    status = db.Enum(FileStatus)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
