# extended_resource_manager.py
from data_manager import DataManager
from models import Resource, ResourceType, StockReceipt, Inventory
from datetime import datetime
from typing import Dict, List
import json

class ExtendedResourceManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def request_resources(self, app_id: str, stage_id: str, resource_name: str, quantity: int, user):
        """Запрос ресурсов с резервированием"""
        if user.role != 'executor':
            raise PermissionError("Только исполнитель может запрашивать ресурсы")
        
        applications = self.data_manager.load_applications()
        application = applications.get(app_id)
        
        if not application or stage_id not in application.stages:
            raise ValueError("Этап не найден")
        
        stage = application.stages[stage_id]
        if stage.executor != user.username:
            raise PermissionError("Вы не являетесь исполнителем этого этапа")
        
        if stage.status == 'completed':
            raise ValueError("Нельзя запрашивать ресурсы для завершенного этапа")
        
        resources = self.data_manager.load_resources()
        if resource_name not in resources:
            raise ValueError("Ресурс не найден")
        
        resource = resources[resource_name]
        
        # Проверяем доступность с учетом уже зарезервированных
        available = resource.quantity - resource.reserved
        if available < quantity:
            raise ValueError(f"Недостаточно ресурсов. Доступно: {available}, Запрошено: {quantity}")
        
        # Резервируем ресурсы
        resource.reserved += quantity
        
        # Добавляем запрос в этап
        stage.requested_resources.append({
            'resource': resource_name,
            'quantity': quantity,
            'status': 'requested',
            'requested_by': user.username,
            'request_date': datetime.now().isoformat()
        })
        
        self.data_manager.save_resources(resources)
        self.data_manager.save_applications(applications)
        return True
    
    def allocate_resources(self, app_id: str, stage_id: str, resource_name: str, user):
        """Выделение зарезервированных ресурсов"""
        if user.role not in ['storeman', 'admin']:
            raise PermissionError("Только работник склада или администратор может выделять ресурсы")
        
        applications = self.data_manager.load_applications()
        application = applications.get(app_id)
        
        if not application or stage_id not in application.stages:
            raise ValueError("Этап не найден")
        
        stage = application.stages[stage_id]
        resources = self.data_manager.load_resources()
        
        # Находим запрос ресурсов
        resource_request = None
        request_index = -1
        for i, request in enumerate(stage.requested_resources):
            if (request['resource'] == resource_name and 
                request['status'] == 'requested'):
                resource_request = request
                request_index = i
                break
        
        if not resource_request:
            raise ValueError("Запрос на ресурсы не найден или уже обработан")
        
        resource = resources[resource_name]
        
        # Проверяем, что ресурсы зарезервированы
        if resource.reserved < resource_request['quantity']:
            raise ValueError("Ресурсы не зарезервированы в достаточном количестве")
        
        # Списываем ресурсы и уменьшаем резерв
        resource.quantity -= resource_request['quantity']
        resource.reserved -= resource_request['quantity']
        
        stage.requested_resources[request_index]['status'] = 'allocated'
        stage.requested_resources[request_index]['allocated_by'] = user.username
        stage.requested_resources[request_index]['allocation_date'] = datetime.now().isoformat()
        
        self.data_manager.save_resources(resources)
        self.data_manager.save_applications(applications)
    
    def add_stock_receipt(self, received_by: str, resources: List[Dict], supplier: str = "", document_number: str = ""):
        """Добавление приходной накладной"""
        receipt_id = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        receipt = StockReceipt(
            id=receipt_id,
            date=datetime.now().isoformat(),
            received_by=received_by,
            resources=resources,
            supplier=supplier,
            document_number=document_number
        )
        
        # Обновляем остатки на складе
        stock_resources = self.data_manager.load_resources()
        for item in resources:
            resource_name = item['resource_name']
            quantity = item['quantity']
            
            if resource_name in stock_resources:
                stock_resources[resource_name].quantity += quantity
            else:
                # Создаем новый ресурс
                stock_resources[resource_name] = Resource(
                    name=resource_name,
                    quantity=quantity,
                    unit=item.get('unit', 'шт'),
                    resource_type=ResourceType(item.get('resource_type', 'consumable')),
                    attributes=item.get('attributes', {})
                )
        
        # Сохраняем накладную
        receipts = self.data_manager.load_data('stock_receipts.json', {})
        receipts[receipt_id] = receipt.__dict__
        self.data_manager.save_data('stock_receipts.json', receipts)
        
        self.data_manager.save_resources(stock_resources)
        return receipt_id
    
    def start_inventory(self, conducted_by: str):
        """Начало инвентаризации"""
        inventory_id = f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        resources = self.data_manager.load_resources()
        items = []
        
        for resource_name, resource in resources.items():
            items.append({
                'resource_name': resource_name,
                'expected_quantity': resource.quantity,
                'actual_quantity': None,  # Будет заполнено при проведении
                'difference': 0
            })
        
        inventory = Inventory(
            id=inventory_id,
            date=datetime.now().isoformat(),
            conducted_by=conducted_by,
            items=items
        )
        
        inventories = self.data_manager.load_data('inventories.json', {})
        inventories[inventory_id] = inventory.__dict__
        self.data_manager.save_data('inventories.json', inventories)
        
        return inventory_id
    
    def update_inventory_item(self, inventory_id: str, resource_name: str, actual_quantity: int):
        """Обновление данных инвентаризации"""
        inventories = self.data_manager.load_data('inventories.json', {})
        
        if inventory_id not in inventories:
            raise ValueError("Инвентаризация не найдена")
        
        inventory_data = inventories[inventory_id]
        
        # Находим и обновляем элемент
        for item in inventory_data['items']:
            if item['resource_name'] == resource_name:
                item['actual_quantity'] = actual_quantity
                item['difference'] = actual_quantity - item['expected_quantity']
                break
        
        self.data_manager.save_data('inventories.json', inventories)
    
    def complete_inventory(self, inventory_id: str):
        """Завершение инвентаризации и корректировка остатков"""
        inventories = self.data_manager.load_data('inventories.json', {})
        
        if inventory_id not in inventories:
            raise ValueError("Инвентаризация не найдена")
        
        inventory_data = inventories[inventory_id]
        inventory_data['status'] = 'completed'
        
        # Корректируем остатки на складе
        resources = self.data_manager.load_resources()
        for item in inventory_data['items']:
            if item['resource_name'] in resources and item['actual_quantity'] is not None:
                resources[item['resource_name']].quantity = item['actual_quantity']
        
        self.data_manager.save_data('inventories.json', inventories)
        self.data_manager.save_resources(resources)
    
    def add_resource_with_attributes(self, name: str, quantity: int, unit: str, 
                                   resource_type: ResourceType, attributes: Dict, min_quantity: int = 0):
        """Добавление ресурса с атрибутами"""
        resources = self.data_manager.load_resources()
        resources[name] = Resource(
            name=name,
            quantity=quantity,
            unit=unit,
            min_quantity=min_quantity,
            resource_type=resource_type,
            attributes=attributes
        )
        self.data_manager.save_resources(resources)
    
    def get_stock_receipts(self):
        """Получение всех приходных накладных"""
        return self.data_manager.load_data('stock_receipts.json', {})
    
    def get_inventories(self):
        """Получение всех инвентаризаций"""
        return self.data_manager.load_data('inventories.json', {})
