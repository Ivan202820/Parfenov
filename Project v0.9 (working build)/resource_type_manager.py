# resource_type_manager.py - создаем файл

from models import ResourceType, ResourceTypeDefinition
from typing import Dict, List

class ResourceTypeManager:
    def __init__(self):
        self.resource_types = self._initialize_resource_types()
    
    def _initialize_resource_types(self) -> Dict[ResourceType, ResourceTypeDefinition]:
        """Инициализация типов ресурсов с их атрибутами"""
        return {
            ResourceType.EQUIPMENT: ResourceTypeDefinition(
                type=ResourceType.EQUIPMENT,
                name="Оборудование",
                description="Стационарное оборудование и техника",
                attributes=[
                    {'name': 'inventory_number', 'label': 'Инвентарный номер', 'type': 'text', 'required': True},
                    {'name': 'serial_number', 'label': 'Серийный номер', 'type': 'text', 'required': False},
                    {'name': 'model', 'label': 'Модель', 'type': 'text', 'required': False},
                    {'name': 'manufacturer', 'label': 'Производитель', 'type': 'text', 'required': False},
                    {'name': 'purchase_date', 'label': 'Дата приобретения', 'type': 'date', 'required': False},
                    {'name': 'warranty_months', 'label': 'Гарантия (мес.)', 'type': 'number', 'required': False}
                ]
            ),
            ResourceType.CONSUMABLE: ResourceTypeDefinition(
                type=ResourceType.CONSUMABLE,
                name="Расходные материалы",
                description="Материалы одноразового использования",
                attributes=[
                    {'name': 'batch_number', 'label': 'Номер партии', 'type': 'text', 'required': False},
                    {'name': 'supplier', 'label': 'Поставщик', 'type': 'text', 'required': False},
                    {'name': 'expiry_date', 'label': 'Срок годности', 'type': 'date', 'required': False},
                    {'name': 'storage_conditions', 'label': 'Условия хранения', 'type': 'text', 'required': False}
                ]
            ),
            ResourceType.MATERIAL: ResourceTypeDefinition(
                type=ResourceType.MATERIAL,
                name="Материалы",
                description="Сырье и материалы для производства",
                attributes=[
                    {'name': 'quality_grade', 'label': 'Сорт/Качество', 'type': 'text', 'required': False},
                    {'name': 'batch_number', 'label': 'Номер партии', 'type': 'text', 'required': False},
                    {'name': 'supplier', 'label': 'Поставщик', 'type': 'text', 'required': False},
                    {'name': 'specifications', 'label': 'Технические характеристики', 'type': 'text', 'required': False}
                ]
            ),
            ResourceType.TOOL: ResourceTypeDefinition(
                type=ResourceType.TOOL,
                name="Инструменты",
                description="Ручной и механизированный инструмент",
                attributes=[
                    {'name': 'inventory_number', 'label': 'Инвентарный номер', 'type': 'text', 'required': True},
                    {'name': 'condition', 'label': 'Состояние', 'type': 'text', 'required': False},
                    {'name': 'last_maintenance', 'label': 'Последнее обслуживание', 'type': 'date', 'required': False},
                    {'name': 'maintenance_interval', 'label': 'Интервал обслуживания (дн.)', 'type': 'number', 'required': False}
                ]
            ),
            ResourceType.ELECTRONICS: ResourceTypeDefinition(
                type=ResourceType.ELECTRONICS,
                name="Электроника",
                description="Электронные компоненты и устройства",
                attributes=[
                    {'name': 'model', 'label': 'Модель', 'type': 'text', 'required': False},
                    {'name': 'manufacturer', 'label': 'Производитель', 'type': 'text', 'required': False},
                    {'name': 'specifications', 'label': 'Технические характеристики', 'type': 'text', 'required': False},
                    {'name': 'compatibility', 'label': 'Совместимость', 'type': 'text', 'required': False}
                ]
            ),
            ResourceType.CHEMICAL: ResourceTypeDefinition(
                type=ResourceType.CHEMICAL,
                name="Химикаты",
                description="Химические вещества и реактивы",
                attributes=[
                    {'name': 'safety_class', 'label': 'Класс опасности', 'type': 'text', 'required': True},
                    {'name': 'storage_conditions', 'label': 'Условия хранения', 'type': 'text', 'required': True},
                    {'name': 'expiry_date', 'label': 'Срок годности', 'type': 'date', 'required': False},
                    {'name': 'msds_number', 'label': 'Номер MSDS', 'type': 'text', 'required': False}
                ]
            )
        }
    
    def get_resource_type_definition(self, resource_type: ResourceType) -> ResourceTypeDefinition:
        """Получить определение типа ресурса"""
        return self.resource_types.get(resource_type)
    
    def get_all_resource_types(self) -> List[ResourceTypeDefinition]:
        """Получить все типы ресурсов"""
        return list(self.resource_types.values())
    
    def get_attributes_for_type(self, resource_type: ResourceType) -> List[Dict]:
        """Получить атрибуты для типа ресурса"""
        definition = self.get_resource_type_definition(resource_type)
        return definition.attributes if definition else []
    
    def validate_attributes(self, resource_type: ResourceType, attributes: Dict) -> bool:
        """Проверить корректность атрибутов для типа ресурса"""
        required_attrs = [attr['name'] for attr in self.get_attributes_for_type(resource_type) 
                         if attr.get('required', False)]
        
        for req_attr in required_attrs:
            if req_attr not in attributes or not attributes[req_attr]:
                return False
        return True