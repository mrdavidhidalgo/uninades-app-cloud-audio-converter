import abc

from services.model.model import ConversionTaskDetail, ConversionTask, FileFormat
from typing import List

class FileConversionScheduler(abc.ABC):
    
    @abc.abstractmethod
    def schedule_conversion_task(self, conversion_task: ConversionTaskDetail)-> None:
        ...