# stage_template_manager.py
from data_manager import DataManager
from models import StageTemplate
from datetime import datetime

class StageTemplateManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def create_template(self, name: str, description: str, typical_duration_days: int, 
                       required_resources: list[dict], dependencies: list[str], user):
        """Создание шаблона этапа"""
        templates = self.data_manager.load_stage_templates()
        template_id = f"template_{len(templates) + 1}_{datetime.now().strftime('%Y%m%d')}"
        
        template = StageTemplate(
            id=template_id,
            name=name,
            description=description,
            typical_duration_days=typical_duration_days,
            required_resources=required_resources,
            dependencies=dependencies,
            created_by=user['username'],
            created_at=datetime.now().isoformat()
        )
        
        templates[template_id] = template.__dict__
        self.data_manager.save_stage_templates(templates)
        return template_id
    
    def get_templates(self):
        """Получение всех шаблонов"""
        return self.data_manager.load_stage_templates()
    
    def get_template(self, template_id):
        """Получение конкретного шаблона"""
        templates = self.data_manager.load_stage_templates()
        return templates.get(template_id)
    
    def update_template(self, template_id: str, **kwargs):
        """Обновление шаблона"""
        templates = self.data_manager.load_stage_templates()
        
        if template_id not in templates:
            raise ValueError("Шаблон не найден")
        
        for key, value in kwargs.items():
            if key in templates[template_id]:
                templates[template_id][key] = value
        
        self.data_manager.save_stage_templates(templates)
    
    def delete_template(self, template_id: str):
        """Удаление шаблона"""
        templates = self.data_manager.load_stage_templates()
        
        if template_id not in templates:
            raise ValueError("Шаблон не найден")
        
        del templates[template_id]
        self.data_manager.save_stage_templates(templates)
    
    def apply_template_to_stage(self, template_id: str, stage_data: dict) -> dict:
        """Применение шаблона к этапу"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError("Шаблон не найден")
        
        # Копируем данные из шаблона
        stage_data['name'] = template['name']
        stage_data['description'] = template['description']
        stage_data['required_resources'] = template['required_resources'].copy()
        stage_data['dependencies'] = template['dependencies'].copy()
        
        # Рассчитываем даты если указана типичная длительность
        if template['typical_duration_days'] > 0 and stage_data.get('planned_start_date'):
            from datetime import datetime, timedelta
            start_date = datetime.fromisoformat(stage_data['planned_start_date'])
            end_date = start_date + timedelta(days=template['typical_duration_days'])
            stage_data['planned_end_date'] = end_date.isoformat()
        
        return stage_data