# stage_manager.py
from data_manager import DataManager

class StageManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def assign_stage_with_details(self, app_id: str, name: str, description: str, executor: str,
                                planned_start_date: str, planned_end_date: str, 
                                dependencies: list[str], required_resources: list[dict], user):
        """Назначение этапа с детальной информацией"""
        applications = self.data_manager.load_applications()
        if app_id not in applications:
            raise ValueError("Заявка не найдена")
            
        application = applications[app_id]
            
        # Меняем статус заявки на "В работе" при назначении первого этапа
        if not application.get('stages') and application.get('status') == 'Новая':
            application['status'] = 'В работе'
            
        stage_id = f"stage_{len(application.get('stages', {})) + 1}"
            
        if 'stages' not in application:
            application['stages'] = {}
            
        application['stages'][stage_id] = {
            'id': stage_id,
            'name': name,
            'description': description,
            'executor': executor,
            'status': 'assigned',
            'planned_start_date': planned_start_date,
            'planned_end_date': planned_end_date,
            'actual_start_date': '',
            'actual_end_date': '',
            'dependencies': dependencies,
            'required_resources': required_resources,
            'requested_resources': [],
            'report': ''
        }
            
        self.data_manager.save_applications(applications)
        return stage_id

    def update_stage_dates(self, app_id: str, stage_id: str, actual_start_date: str = "", 
                        actual_end_date: str = ""):
        """Обновление фактических дат этапа"""
        applications = self.data_manager.load_applications()
        application = applications.get(app_id)
        
        if not application or stage_id not in application.get('stages', {}):
            raise ValueError("Этап не найден")
        
        stage = application['stages'][stage_id]
        
        if actual_start_date:
            stage['actual_start_date'] = actual_start_date
            if stage['status'] == 'assigned':
                stage['status'] = 'in_progress'
        
        if actual_end_date:
            stage['actual_end_date'] = actual_end_date
            if stage['status'] == 'in_progress':
                stage['status'] = 'completed'
        
        self.data_manager.save_applications(applications)

    def assign_stage(self, app_id: str, stage_description: str, executor: str, user):
        applications = self.data_manager.load_applications()
        if app_id not in applications:
            raise ValueError("Заявка не найдена")
            
        application = applications[app_id]
            
        # Меняем статус заявки на "В работе" при назначении первого этапа
        if not application.get('stages') and application.get('status') == 'Новая':
            application['status'] = 'В работе'
            
        stage_id = f"stage_{len(application.get('stages', {})) + 1}"
            
        if 'stages' not in application:
            application['stages'] = {}
            
        application['stages'][stage_id] = {
            'id': stage_id,
            'name': stage_description,  # Теперь это описание этапа
            'executor': executor,
            'status': 'assigned',
            'requested_resources': [],
            'report': ''
        }
            
        self.data_manager.save_applications(applications)
        return stage_id
    
    def complete_stage(self, app_id: str, stage_id: str, report: str, user):
        applications = self.data_manager.load_applications()
        application = applications.get(app_id)
        
        if not application or stage_id not in application.get('stages', {}):
            raise ValueError("Этап не найдена")
        
        stage = application['stages'][stage_id]
        if stage.get('executor') != user['username'] and user['role'] not in ['manager', 'admin']:
            raise PermissionError("Только назначенный исполнитель может завершать этап")
        
        stage['status'] = "completed"
        stage['report'] = report
        self.data_manager.save_applications(applications)
    
    def get_user_stages(self, user):
        applications = self.data_manager.load_applications()
        user_stages = {}
        
        for app_id, application in applications.items():
            for stage_id, stage in application.get('stages', {}).items():
                if stage.get('executor') == user['username']:
                    if app_id not in user_stages:
                        user_stages[app_id] = {}
                    user_stages[app_id][stage_id] = stage
        
        return user_stages
