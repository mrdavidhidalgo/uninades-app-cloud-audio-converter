from services.contracts import file_conversion_scheduler
from services.model.model import ConversionTaskDetail, FileFormat, FileStatus, ConversionTask
from repositorios.db_model import db_model
from typing import List 

class FileConversionScheduler(file_conversion_scheduler.FileConversionScheduler):

    def schedule_conversion_task(self, conversion_task: ConversionTaskDetail) -> None:
        #TODO(d.hidalgo@uniandes.edu.co): Here we need to send message to kafka
        print(f"Send task with id {conversion_task.id} to kafka")
        ...


