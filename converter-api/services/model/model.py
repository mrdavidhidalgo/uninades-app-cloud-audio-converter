from datetime import datetime
from pydantic import BaseModel, validator
import re
import enum
from typing import Dict, Any, Optional

class FileStatus(enum.Enum):
    UPLOADED = 1
    PROCESSED = 2

class FileFormat(enum.Enum):
    MP3 = "MP3"
    ACC = "ACC"
    OGG = "OGG"
    WAV = "WAV"
    WMA = "WMA"

class User(BaseModel):
    id : Optional[str]
    username : str
    mail : str
    password : str
    name: str

    @validator('mail')
    def mail_must_be_valid(cls, mail: str):
        regex = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        if not re.match(regex,mail):
            raise ValueError("Mail must be valid") 

        return mail

class ConversionTaskDetail(BaseModel):
    id: str
    source_file_path : str
    source_file_format: FileFormat
    target_file_format : FileFormat
    state : FileStatus
    #date : datetime.date<
        
class ConversionTask(BaseModel):
    user : str
    source_file_path : str
    source_file_format: FileFormat
    target_file_format : FileFormat

    """
    @validator('source_file_format')
    def source_file_format_must_be_different_from_target_file_format(
        cls, source_file_format: FileFormat, values: Dict[str, Any]
    )-> FileFormat:
 
        target_file_format: FileFormat = values["target_file_format"]
        if target_file_format is source_file_format:
            raise ValueError("Source file format must be different from target file format")

        return source_file_format

    """