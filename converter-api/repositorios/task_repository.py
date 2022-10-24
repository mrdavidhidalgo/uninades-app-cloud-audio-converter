from services.contracts import task_repository
from services.model.model import ConversionTaskDetail, FileDetail, FileFormat, FileStatus, ConversionTask, ConversionTaskDetailEncoder
from repositorios.db_model import db_model
from typing import List, Optional

from sqlalchemy import or_

class TaskRepository(task_repository.TaskRepository):

    def build_task_detail(self, source_file : db_model.SourceFile, task : db_model.ConversionTask)-> ConversionTaskDetail:
        return ConversionTaskDetail(id = task.id, 
                                    source_file_path=source_file.file_path, 
                                    source_file_format=source_file.file_format, 
                                    target_file_format=task.target_file_format, 
                                    state = task.status)

    def build(self, source_file : db_model.SourceFile)->List[ConversionTaskDetail]:
        
        data = [self.build_task_detail(source_file=source_file, task = conversion) for conversion in source_file.task]
        return data
        
        

    def get_conversion_tasks_by_user_id(self, user_id: str) -> List[ConversionTaskDetail]:
        
        data : List[ConversionTaskDetail] = []
        
        print(f"Filtrando por usuario {user_id}")
        
        for source in db_model.SourceFile.query.filter(db_model.SourceFile.user_owner == int(user_id)):
            data.extend(self.build(source_file=source))
        
        return data
            
    def register_conversion_task(self, conversion_task: ConversionTask) -> str:
        
        source_file = db_model.SourceFile(file_path = conversion_task.source_file_path, 
                            file_format = conversion_task.source_file_format, 
                            user_owner = conversion_task.user)

        db_model.db.session.add(source_file)
        db_model.db.session.commit()

        persisted_source_file = db_model.SourceFile.query.filter(db_model.SourceFile.file_path == source_file.file_path).first()
        
        conversion_task = db_model.ConversionTask(source_file_id = persisted_source_file.id, 
                                target_file_format = conversion_task.target_file_format, 
                                status = db_model.FileStatus.UPLOADED
                                )

        db_model.db.session.add(conversion_task)
        db_model.db.session.commit()
        
        return conversion_task.id

    def get_conversion_task_by_id(self, task_id: str, user_id: str)-> Optional[ConversionTaskDetail]: 
        
        source_file : db_model.SourceFile = db_model.db.session.query(db_model.SourceFile).join(db_model.ConversionTask).filter(db_model.SourceFile.user_owner == user_id, db_model.ConversionTask.id == task_id).first()
        if source_file is None:
            return None

        conversion_task: db_model.ConversionTask = source_file.task[0]
        
        return ConversionTaskDetail(id = task_id, 
                                    source_file_path=source_file.file_path,
                                    source_file_format=source_file.file_format,
                                    target_file_format=conversion_task.target_file_format, 
                                    state = conversion_task.status,
                                    target_file_path=conversion_task.target_file_path)
        

    def change_target_file_format(self, task_id: str, target_file_format: FileFormat ) -> ConversionTaskDetail:
        return ConversionTaskDetail(id = task_id, 
                                    source_file_path="/pepe3.txt", 
                                    source_file_format=FileFormat.MP3, 
                                    target_file_format=target_file_format, 
                                    state = FileStatus.UPLOADED)

    def delete_conversion_task_by_id(self, task_id: str)-> None: 
        
        conversion_task : db_model.ConversionTask = db_model.ConversionTask.query.get(task_id)
        
        db_model.db.session.delete(conversion_task)
        
        source_file = db_model.SourceFile.query.get(conversion_task.source_file_id)
        db_model.db.session.delete(source_file)
        
        db_model.db.session.commit()

    def update_conversion_task(self, task_id: str,target_file_path: str, state : FileStatus ) -> None: 
        conversion_task : db_model.ConversionTask = db_model.ConversionTask.query.filter(db_model.ConversionTask.id == int(task_id)).first()
        conversion_task.target_file_path = target_file_path
        conversion_task.status = state
        
        db_model.db.session.add(conversion_task)
        db_model.db.session.commit()
        
    def update_target_format_to_task(self, task_id: str, state : FileStatus, new_file_format = FileFormat ) -> None: 
        conversion_task : db_model.ConversionTask = db_model.ConversionTask.query.filter(db_model.ConversionTask.id == int(task_id)).first()
        conversion_task.target_file_format = new_file_format
        conversion_task.status = state  
        
        db_model.db.session.add(conversion_task)
        db_model.db.session.commit()
        
    def get_file_path_by_user_and_file_name(self, file_name: str, user_id: str ) -> Optional[FileDetail]: 
        
        source_file : db_model.SourceFile = db_model.db.session.query(db_model.SourceFile).join(db_model.ConversionTask).filter(db_model.SourceFile.user_owner == user_id, or_(db_model.SourceFile.file_path == file_name, db_model.ConversionTask.target_file_path == file_name)).first()
        if source_file is None:
            return None
        
        conversion_task: db_model.ConversionTask = source_file.task[0]
        
        file_path = source_file.file_path if file_name == source_file.file_path else conversion_task.target_file_path

        return FileDetail(file_path=file_path, is_converted=False if file_name == source_file.file_path else True)
        