# resource_manager.py
from data_manager import DataManager
from models import ResourceType  # Добавляем импорт
from resource_type_manager import ResourceTypeManager
from datetime import datetime

class ResourceManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.type_manager = ResourceTypeManager()

    def start_inventory(self, user=None):
        """Начало новой инвентаризации"""
        if user and user['role'] not in ['storeman', 'admin']:
            raise PermissionError("Недостаточно прав для проведения инвентаризации")
        
        inventories = self.data_manager.load_inventories()
        resources = self.data_manager.load_resources()
        
        # Создаем ID инвентаризации
        inventory_id = f"inv_{len(inventories) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Создаем элементы инвентаризации на основе текущих ресурсов
        items = []
        for name, resource in resources.items():
            items.append({
                'resource_name': name,
                'expected_quantity': resource['quantity'],
                'actual_quantity': None,  # Будет заполнено при проведении
                'difference': 0,
                'unit': resource['unit'],
                'resource_type': resource.get('resource_type', 'consumable')
            })
        
        # Создаем запись инвентаризации
        inventory = {
            'id': inventory_id,
            'date_started': datetime.now().isoformat(),
            'date_completed': None,
            'conducted_by': user['username'] if user else 'system',
            'status': 'in_progress',
            'items': items,
            'total_items': len(items),
            'items_counted': 0,
            'total_differences': 0,
            'discrepancies_count': 0
        }
        
        # Сохраняем инвентаризацию
        inventories[inventory_id] = inventory
        self.data_manager.save_inventories(inventories)
        
        return inventory_id

    def update_inventory_item(self, inventory_id, resource_name, actual_quantity):
        """Обновление фактического количества для ресурса в инвентаризации"""
        inventories = self.data_manager.load_inventories()
        
        if inventory_id not in inventories:
            raise ValueError("Инвентаризация не найдена")
        
        inventory = inventories[inventory_id]
        
        if inventory['status'] != 'in_progress':
            raise ValueError("Инвентаризация уже завершена")
        
        # Находим и обновляем элемент
        item_updated = False
        for item in inventory['items']:
            if item['resource_name'] == resource_name:
                item['actual_quantity'] = actual_quantity
                item['difference'] = actual_quantity - item['expected_quantity']
                item_updated = True
                break
        
        if not item_updated:
            raise ValueError("Ресурс не найден в инвентаризации")
        
        # Пересчитываем статистику
        self._update_inventory_stats(inventory)
        
        self.data_manager.save_inventories(inventories)
        return True

    def _update_inventory_stats(self, inventory):
        """Обновление статистики инвентаризации"""
        items_counted = 0
        total_differences = 0
        discrepancies_count = 0
        
        for item in inventory['items']:
            if item['actual_quantity'] is not None:
                items_counted += 1
                total_differences += abs(item['difference'])
                if item['difference'] != 0:
                    discrepancies_count += 1
        
        inventory['items_counted'] = items_counted
        inventory['total_differences'] = total_differences
        inventory['discrepancies_count'] = discrepancies_count

    def complete_inventory(self, inventory_id, user=None, update_stock=False):
        """Завершение инвентаризации"""
        if user and user['role'] not in ['storeman', 'admin']:
            raise PermissionError("Недостаточно прав для завершения инвентаризации")
        
        inventories = self.data_manager.load_inventories()
        
        if inventory_id not in inventories:
            raise ValueError("Инвентаризация не найдена")
        
        inventory = inventories[inventory_id]
        
        if inventory['status'] == 'completed':
            raise ValueError("Инвентаризация уже завершена")
        
        # Проверяем, что все ресурсы посчитаны
        if inventory['items_counted'] < inventory['total_items']:
            raise ValueError("Не все ресурсы посчитаны. Завершение невозможно.")
        
        # Обновляем статус
        inventory['status'] = 'completed'
        inventory['date_completed'] = datetime.now().isoformat()
        inventory['completed_by'] = user['username'] if user else 'system'
        
        # Если нужно обновить остатки на складе
        if update_stock:
            resources = self.data_manager.load_resources()
            for item in inventory['items']:
                if item['resource_name'] in resources:
                    resources[item['resource_name']]['quantity'] = item['actual_quantity']
            self.data_manager.save_resources(resources)
            inventory['stock_updated'] = True
        else:
            inventory['stock_updated'] = False
        
        self.data_manager.save_inventories(inventories)
        return True

    def get_inventories(self):
        """Получение всех инвентаризаций"""
        return self.data_manager.load_inventories()

    def get_inventory(self, inventory_id):
        """Получение конкретной инвентаризации"""
        inventories = self.data_manager.load_inventories()
        return inventories.get(inventory_id)

    def get_stock_receipts(self):
        """Получение всех приходных накладных"""
        return self.data_manager.load_stock_receipts()

    def get_stock_receipt(self, receipt_id):
        """Получение конкретной накладной"""
        receipts = self.data_manager.load_stock_receipts()
        return receipts.get(receipt_id)

    def add_stock_receipt(self, resources, supplier="", document_number="", user=None):
        """Добавление приходной накладной с сохранением"""
        if user and user['role'] not in ['storeman', 'admin']:
            raise PermissionError("Недостаточно прав для создания накладных")
        
        # Загружаем текущие накладные
        receipts = self.data_manager.load_stock_receipts()
        
        # Создаем ID накладной
        receipt_id = f"receipt_{len(receipts) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Создаем запись накладной
        receipt = {
            'id': receipt_id,
            'date': datetime.now().isoformat(),
            'created_by': user['username'] if user else 'system',
            'supplier': supplier,
            'document_number': document_number,
            'resources': resources,
            'total_items': len(resources),
            'total_quantity': sum(r['quantity'] for r in resources)
        }
        
        # Обновляем остатки на складе
        current_resources = self.data_manager.load_resources()
        for resource in resources:
            name = resource['name']
            quantity = resource['quantity']
            unit = resource.get('unit', 'шт')
            
            if name in current_resources:
                current_resources[name]['quantity'] += quantity
            else:
                # Создаем новый ресурс с типом по умолчанию
                self.add_resource(
                    name, 
                    quantity, 
                    unit,
                    resource.get('min_quantity', 0),
                    ResourceType.CONSUMABLE,
                    resource.get('attributes', {}),
                    user
                )
        
        # Сохраняем накладную
        receipts[receipt_id] = receipt
        self.data_manager.save_stock_receipts(receipts)
        
        return receipt_id

    def update_resource(self, name: str, quantity: int = None, unit: str = None, 
                       min_quantity: int = None, resource_type: ResourceType = None, 
                       attributes: dict = None, user=None):
        """Обновление ресурса с поддержкой типа и атрибутов"""
        resources = self.data_manager.load_resources()
        
        if name not in resources:
            raise ValueError("Ресурс не найден")
        
        resource = resources[name]
        
        # Обновляем основные поля
        if quantity is not None:
            resource['quantity'] = quantity
        if unit is not None:
            resource['unit'] = unit
        if min_quantity is not None:
            resource['min_quantity'] = min_quantity
        if resource_type is not None:
            resource['resource_type'] = resource_type.value
        if attributes is not None:
            # При изменении типа проверяем атрибуты
            if resource_type and not self.type_manager.validate_attributes(resource_type, attributes):
                required_attrs = [attr['name'] for attr in self.type_manager.get_attributes_for_type(resource_type) 
                                if attr.get('required', False)]
                raise ValueError(f"Не заполнены обязательные атрибуты: {', '.join(required_attrs)}")
            resource['attributes'] = attributes
        
        self.data_manager.save_resources(resources)

    def get_resource_types(self):
        """Получить все типы ресурсов"""
        return self.type_manager.get_all_resource_types()
    
    def get_resource_type_attributes(self, resource_type):
        """Получить атрибуты для типа ресурса"""
        return self.type_manager.get_attributes_for_type(resource_type)

    def is_resource_used(self, resource_name: str) -> bool:
        """Проверяет, используется ли ресурс в каких-либо заявках"""
        applications = self.data_manager.load_applications()
        
        for app_id, application in applications.items():
            for stage_id, stage in application.get('stages', {}).items():
                for request in stage.get('requested_resources', []):
                    if request['resource'] == resource_name:
                        return True
        return False

    def delete_resource(self, name: str, user=None):
        """Удаление ресурса с проверкой использования"""
        resources = self.data_manager.load_resources()
        
        if name not in resources:
            raise ValueError("Ресурс не найден")
        
        # Проверяем, не используется ли ресурс в заявках
        if self.is_resource_used(name):
            raise ValueError(f"Ресурс '{name}' используется в заявках и не может быть удален")
        
        del resources[name]
        self.data_manager.save_resources(resources)

    def get_resource(self, name: str):
        """Получение информации о конкретном ресурсе"""
        resources = self.data_manager.load_resources()
        return resources.get(name)


    def request_resources(self, app_id: str, stage_id: str, resource_name: str, quantity: int, user):
        applications = self.data_manager.load_applications()
        application = applications.get(app_id)
        
        if not application or stage_id not in application.get('stages', {}):
            raise ValueError("Этап не найден")
        
        stage = application['stages'][stage_id]
        if stage.get('executor') != user['username']:
            raise PermissionError("Вы не являетесь исполнителем этого этапа")
        
        if stage.get('status') == 'completed':
            raise ValueError("Нельзя запрашивать ресурсы для завершенного этапа")
        
        resources = self.data_manager.load_resources()
        if resource_name not in resources:
            raise ValueError("Ресурс не найден")
        
        # Добавляем запрос в этап
        if 'requested_resources' not in stage:
            stage['requested_resources'] = []
        
        stage['requested_resources'].append({
            'resource': resource_name,
            'quantity': quantity,
            'status': 'requested',
            'requested_by': user['username'],
            'request_date': datetime.now().isoformat()
        })
        
        self.data_manager.save_applications(applications)
        return True
    
    def allocate_resources(self, app_id: str, stage_id: str, resource_name: str, user):
        applications = self.data_manager.load_applications()
        application = applications.get(app_id)
        
        if not application or stage_id not in application.get('stages', {}):
            raise ValueError("Этап не найден")
        
        stage = application['stages'][stage_id]
        resources = self.data_manager.load_resources()
        
        # Находим запрос ресурсов
        resource_request = None
        request_index = -1
        for i, request in enumerate(stage.get('requested_resources', [])):
            if (request['resource'] == resource_name and 
                request['status'] == 'requested'):
                resource_request = request
                request_index = i
                break
        
        if not resource_request:
            raise ValueError("Запрос на ресурсы не найден или уже обработан")
        
        resource = resources[resource_name]
        if resource['quantity'] < resource_request['quantity']:
            raise ValueError(f"Недостаточно ресурсов на складе. Доступно: {resource['quantity']}, Требуется: {resource_request['quantity']}")
        
        # Выделяем ресурсы
        resource['quantity'] -= resource_request['quantity']
        stage['requested_resources'][request_index]['status'] = 'allocated'
        stage['requested_resources'][request_index]['allocated_by'] = user['username']
        stage['requested_resources'][request_index]['allocation_date'] = datetime.now().isoformat()
        
        self.data_manager.save_resources(resources)
        self.data_manager.save_applications(applications)
    
    def get_pending_resource_requests(self):
        """Получить все запросы ресурсов со статусом 'requested'"""
        applications = self.data_manager.load_applications()
        pending_requests = []
        
        for app_id, application in applications.items():
            for stage_id, stage in application.get('stages', {}).items():
                for request in stage.get('requested_resources', []):
                    if request['status'] == 'requested':
                        pending_requests.append({
                            'app_id': app_id,
                            'stage_id': stage_id,
                            'stage_name': stage['name'],
                            'executor': stage['executor'],
                            'resource': request['resource'],
                            'quantity': request['quantity'],
                            'request_data': request
                        })
        
        return pending_requests
    
    def add_resource(self, name: str, quantity: int, unit: str, min_quantity: int = 0, 
                   resource_type: ResourceType = ResourceType.CONSUMABLE, attributes: dict = None, user=None):
        """Добавление ресурса с типом и атрибутами"""
        resources = self.data_manager.load_resources()
        
        if name in resources:
            raise ValueError("Ресурс с таким названием уже существует")
        
        if attributes is None:
            attributes = {}
        
        # Проверяем обязательные атрибуты
        if not self.type_manager.validate_attributes(resource_type, attributes):
            required_attrs = [attr['name'] for attr in self.type_manager.get_attributes_for_type(resource_type) 
                            if attr.get('required', False)]
            raise ValueError(f"Не заполнены обязательные атрибуты: {', '.join(required_attrs)}")
        
        resources[name] = {
            'name': name,
            'quantity': quantity,
            'unit': unit,
            'min_quantity': min_quantity,
            'resource_type': resource_type.value,
            'attributes': attributes,
            'reserved': 0
        }
        
        self.data_manager.save_resources(resources)
    
    def get_all_resources(self):
        return self.data_manager.load_resources()
