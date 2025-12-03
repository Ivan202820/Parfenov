# main_system.py
from data_manager import DataManager
from authentication import Authentication
from application_manager import ApplicationManager
from stage_manager import StageManager
from resource_manager import ResourceManager
from resource_type_manager import ResourceTypeManager  # Добавляем если используется
from config import USER_ROLES
from models import ResourceType  # Добавляем импорт ResourceType
from stage_template_manager import StageTemplateManager

class MainSystem:
    def __init__(self):
        self.data_manager = DataManager()
        self.auth = Authentication(self.data_manager)
        self.app_manager = ApplicationManager(self.data_manager)
        self.stage_manager = StageManager(self.data_manager)
        self.resource_manager = ResourceManager(self.data_manager)
        self.template_manager = StageTemplateManager(self.data_manager)
        
        # Миграция старых заявок при инициализации системы
        self.migrate_old_data()

    def assign_stage_with_details(self, app_id: str, name: str, description: str, executor: str,
                                planned_start_date: str, planned_end_date: str, 
                                dependencies: list[str], required_resources: list[dict]):
        """Назначение этапа с детальной информацией"""
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        
        return self.stage_manager.assign_stage_with_details(
            app_id, name, description, executor, planned_start_date, planned_end_date,
            dependencies, required_resources, self.auth.current_user
        )

    def update_stage_dates(self, app_id: str, stage_id: str, actual_start_date: str = "", 
                        actual_end_date: str = ""):
        """Обновление фактических дат этапа"""
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        
        self.stage_manager.update_stage_dates(app_id, stage_id, actual_start_date, actual_end_date)

    def create_stage_template(self, name: str, description: str, typical_duration_days: int,
                            required_resources: list[dict], dependencies: list[str]):
        """Создание шаблона этапа"""
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        
        return self.template_manager.create_template(
            name, description, typical_duration_days, required_resources, dependencies, self.auth.current_user
        )

    def get_stage_templates(self):
        """Получение всех шаблонов"""
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        
        return self.template_manager.get_templates()

    def get_stage_template(self, template_id):
        """Получение конкретного шаблона"""
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        
        return self.template_manager.get_template(template_id)

    def update_stage_template(self, template_id: str, **kwargs):
        """Обновление шаблона"""
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        
        self.template_manager.update_template(template_id, **kwargs)

    def delete_stage_template(self, template_id: str):
        """Удаление шаблона"""
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        
        self.template_manager.delete_template(template_id)

    def assign_stage_with_template(self, app_id: str, template_id: str, executor: str, 
                                planned_start_date: str = ""):
        """Назначение этапа с использованием шаблона"""
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        
        # Создаем базовые данные этапа
        stage_data = {
            'executor': executor,
            'planned_start_date': planned_start_date,
            'status': 'assigned'
        }
        
        # Применяем шаблон
        stage_data = self.template_manager.apply_template_to_stage(template_id, stage_data)
        
        # Создаем этап через стандартный менеджер
        stage_id = self.stage_manager.assign_stage(app_id, stage_data['name'], executor, self.auth.current_user)
        
        # Обновляем этап дополнительными данными из шаблона
        applications = self.data_manager.load_applications()
        if app_id in applications and stage_id in applications[app_id].get('stages', {}):
            stage = applications[app_id]['stages'][stage_id]
            stage.update({
                'description': stage_data['description'],
                'planned_start_date': stage_data.get('planned_start_date', ''),
                'planned_end_date': stage_data.get('planned_end_date', ''),
                'dependencies': stage_data.get('dependencies', []),
                'required_resources': stage_data.get('required_resources', [])
            })
            self.data_manager.save_applications(applications)
        
        return stage_id

    def start_inventory(self):
        """Начало инвентаризации"""
        if not self.has_permission('manage_resources'):
            raise PermissionError("Недостаточно прав")
        
        return self.resource_manager.start_inventory(self.auth.current_user)

    def update_inventory_item(self, inventory_id, resource_name, actual_quantity):
        """Обновление элемента инвентаризации"""
        if not self.has_permission('manage_resources'):
            raise PermissionError("Недостаточно прав")
        
        return self.resource_manager.update_inventory_item(inventory_id, resource_name, actual_quantity)

    def complete_inventory(self, inventory_id, update_stock=False):
        """Завершение инвентаризации"""
        if not self.has_permission('manage_resources'):
            raise PermissionError("Недостаточно прав")
        
        return self.resource_manager.complete_inventory(inventory_id, self.auth.current_user, update_stock)

    def get_inventories(self):
        """Получение всех инвентаризаций"""
        if not self.has_permission('view_resources'):
            raise PermissionError("Недостаточно прав")
        
        return self.resource_manager.get_inventories()

    def get_inventory(self, inventory_id):
        """Получение конкретной инвентаризации"""
        if not self.has_permission('view_resources'):
            raise PermissionError("Недостаточно прав")
        
        return self.resource_manager.get_inventory(inventory_id)

    def migrate_old_data(self):
        """Миграция старых данных"""
        try:
            users = self.data_manager.load_users()
            self.app_manager.migrate_old_applications(users)
        except Exception as e:
            print(f"Ошибка при миграции данных: {e}")

    def has_permission(self, permission: str) -> bool:
        if not self.auth.current_user:
            return False
        return permission in USER_ROLES.get(self.auth.current_user.get('role', ''), [])
    
    # Методы аутентификации
    def login(self, username: str, password: str) -> bool:
        return self.auth.login(username, password)
    
    def logout(self):
        self.auth.logout()
    
    def get_current_user(self):
        return self.auth.current_user
    
    # Методы управления пользователями (только для admin)
    def register_user(self, username: str, password: str, role: str, full_name: str, department: str = ""):
        if not self.has_permission('manage_users'):
            raise PermissionError("Недостаточно прав")
        self.auth.register_user(username, password, role, full_name, department)
    
    # Методы заявок

    def get_my_applications(self):
        if not self.auth.current_user:
            return {}
        return self.app_manager.get_applications_for_user(self.auth.current_user)
    
    def get_application(self, app_id: str):
        return self.app_manager.get_application(app_id)
    
    # Методы этапов
    def assign_stage(self, app_id: str, stage_name: str, executor: str):
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        return self.stage_manager.assign_stage(
            app_id, stage_name, executor, self.auth.current_user
        )
    
    def complete_stage(self, app_id: str, stage_id: str, report: str):
        if not self.has_permission('complete_stages'):
            raise PermissionError("Недостаточно прав")
        self.stage_manager.complete_stage(
            app_id, stage_id, report, self.auth.current_user
        )
    
    def get_my_stages(self):
        if not self.has_permission('view_assigned_stages'):
            return {}
        return self.stage_manager.get_user_stages(self.auth.current_user)
    
    # Методы ресурсов
    def request_resources(self, app_id: str, stage_id: str, resource_name: str, quantity: int):
        if not self.has_permission('request_resources'):
            raise PermissionError("Недостаточно прав")
        self.resource_manager.request_resources(
            app_id, stage_id, resource_name, quantity, self.auth.current_user
        )
    
    def allocate_resources(self, app_id: str, stage_id: str, resource_name: str):
        if not self.has_permission('manage_resources'):
            raise PermissionError("Недостаточно прав")
        self.resource_manager.allocate_resources(
            app_id, stage_id, resource_name, self.auth.current_user
        )
    
    def add_resource(self, name: str, quantity: int, unit: str, min_quantity: int = 0, 
                   resource_type: ResourceType = ResourceType.CONSUMABLE, attributes: dict = None):
        """Добавление ресурса с типом и атрибутами"""
        if not self.has_permission('manage_resources') and not self.has_permission('edit_resources'):
            raise PermissionError("Недостаточно прав для управления ресурсами")
        
        self.resource_manager.add_resource(
            name, quantity, unit, min_quantity, resource_type, attributes, self.auth.current_user
        )

    def delete_resource(self, name: str):
        """Удаление ресурса"""
        # Разрешаем удаление ресурсов только администраторам
        if not self.has_permission('manage_resources'):
            raise PermissionError("Недостаточно прав для удаления ресурсов")
        
        self.resource_manager.delete_resource(name, self.auth.current_user)

    def is_resource_used(self, name: str) -> bool:
        """Проверка использования ресурса"""
        return self.resource_manager.is_resource_used(name)

    def update_resource(self, name: str, quantity: int = None, unit: str = None, 
                       min_quantity: int = None, resource_type: ResourceType = None, 
                       attributes: dict = None):
        """Обновление ресурса с типом и атрибутами"""
        if not self.has_permission('manage_resources') and not self.has_permission('edit_resources'):
            raise PermissionError("Недостаточно прав для управления ресурсами")
        
        self.resource_manager.update_resource(
            name, quantity, unit, min_quantity, resource_type, attributes, self.auth.current_user
        )

    def get_resource_types(self):
        """Получить все типы ресурсов"""
        return self.resource_manager.get_resource_types()
    
    def get_resource_type_attributes(self, resource_type: ResourceType):
        """Получить атрибуты для типа ресурса"""
        return self.resource_manager.get_resource_type_attributes(resource_type)

    def get_resources(self):
        """Получение всех ресурсов"""
        # Разрешаем просмотр ресурсов исполнителям, кладовщикам и администраторам
        if not self.has_permission('view_resources') and self.auth.current_user['role'] != 'executor':
            raise PermissionError("Недостаточно прав для просмотра ресурсов")
        return self.resource_manager.get_all_resources()

    def get_resource(self, name: str):
        """Получение информации о ресурсе"""
        if not self.has_permission('view_resources'):
            raise PermissionError("Недостаточно прав для просмотра ресурсов")
        
        return self.resource_manager.get_resource(name)
    
    def get_pending_resource_requests(self):
        if not self.has_permission('manage_resources'):
            raise PermissionError("Недостаточно прав")
        return self.resource_manager.get_pending_resource_requests()
    
    # Расширенные методы
    def add_stock_receipt(self, resources, supplier="", document_number=""):
        """Добавление приходной накладной"""
        if not self.has_permission('manage_resources'):
            raise PermissionError("Недостаточно прав")
        
        return self.resource_manager.add_stock_receipt(
            resources, supplier, document_number, self.auth.current_user
        )

    def get_stock_receipts(self):
        """Получение всех накладных"""
        if not self.has_permission('view_resources'):
            raise PermissionError("Недостаточно прав")
        
        return self.resource_manager.get_stock_receipts()

    def get_stock_receipt(self, receipt_id):
        """Получение конкретной накладной"""
        if not self.has_permission('view_resources'):
            raise PermissionError("Недостаточно прав")
        
        return self.resource_manager.get_stock_receipt(receipt_id)
    
    def generate_applications_status_report(self):
        """Упрощенный отчет по статусам заявок"""
        if not self.auth.current_user:
            raise PermissionError("Необходима авторизация")
        
        applications = self.get_my_applications()
        
        report_data = {
            'total': len(applications),
            'by_status': {},
            'summary': f"Отчет по заявкам пользователя {self.auth.current_user['username']}"
        }
        
        for app_id, app in applications.items():
            status = app['status']
            report_data['by_status'][status] = report_data['by_status'].get(status, 0) + 1
        
        return report_data
    
    def generate_stock_report(self):
        """Упрощенный отчет по складу"""
        if not self.has_permission('view_resources'):
            raise PermissionError("Недостаточно прав")
        
        resources = self.get_resources()
        
        report_data = {
            'total_items': len(resources),
            'total_quantity': sum(r['quantity'] for r in resources.values()),
            'low_stock': [],
            'resources': resources
        }
        
        # Находим ресурсы с низким запасом
        for name, resource in resources.items():
            if resource['quantity'] < resource.get('min_quantity', 0):
                report_data['low_stock'].append({
                    'name': name,
                    'current': resource['quantity'],
                    'min_required': resource.get('min_quantity', 0)
                })
        
        return report_data
    
    # В класс MainSystem добавьте эти методы:

    def get_executors(self):
        """Получить только исполнителей"""
        if not self.auth.current_user:
            raise PermissionError("Необходима авторизация")
        
        # Разрешаем менеджерам и администраторам просматривать исполнителей
        if self.auth.current_user['role'] not in ['manager', 'admin']:
            raise PermissionError("Недостаточно прав")
        
        all_users = self.data_manager.load_users()
        executors = []
        
        for username, user_data in all_users.items():
            if (user_data.get('role') == 'executor' and 
                user_data.get('status') != 'blocked'):
                executors.append(username)
        
        return executors

    def get_all_users(self):
        """Получить всех пользователей (для менеджера и администратора)"""
        # Используем self.auth.current_user вместо self.current_user
        if not self.auth.current_user:
            raise PermissionError("Необходима авторизация")
        
        if self.auth.current_user['role'] not in ['manager', 'admin']:
            raise PermissionError("Недостаточно прав для просмотра пользователей")
        
        return self.data_manager.load_users()

    def delete_user(self, username: str):
        """Удаление пользователя (только для администратора)"""
        if not self.has_permission('manage_users'):
            raise PermissionError("Недостаточно прав")
        
        # Нельзя удалить текущего пользователя
        if self.auth.current_user and self.auth.current_user['username'] == username:
            raise ValueError("Нельзя удалить самого себя")
        
        self.auth.delete_user(username)

    def update_user(self, username: str, **kwargs):
        """Обновление данных пользователя (только для администратора)"""
        if not self.has_permission('manage_users'):
            raise PermissionError("Недостаточно прав")
        
        users = self.data_manager.load_users()
        if username not in users:
            raise ValueError("Пользователь не найден")
        
        # Обновляем только переданные поля
        for key, value in kwargs.items():
            if key in users[username] and key != 'username':  # Нельзя менять логин
                users[username][key] = value
        
        self.data_manager.save_users(users)
        
    def create_application(self, contract_number: str, description: str, address: str = "", customer_name: str = "") -> str:
        """
        Создание новой заявки
        
        Args:
            contract_number: Номер договора
            description: Описание заявки
            address: Адрес заказчика (опционально)
            customer_name: ФИО заказчика (обязательно)
            
        Returns:
            ID созданной заявки
        """
        # Разрешаем создание заявок заказчикам и руководителям
        if not self.has_permission('create_application') and self.auth.current_user['role'] != 'manager':
            raise PermissionError("Недостаточно прав")
        
        # Для заказчика используем его ФИО как customer_name
        if self.auth.current_user['role'] == 'customer' and not customer_name:
            customer_name = self.auth.current_user['full_name']
        
        # Проверяем, что customer_name указан
        if not customer_name:
            raise ValueError("ФИО заказчика обязательно для заполнения")
        
        return self.app_manager.create_application(
            contract_number,
            description,
            address,
            customer_name
        )
    
    def update_application(self, app_id: str, contract_number: str = None, description: str = None, address: str = None, customer_name: str = None):
        """Редактирование заявки"""
        if not self.auth.current_user:
            raise PermissionError("Необходима авторизация")
        
        self.app_manager.update_application(
            app_id, contract_number, description, address, customer_name, self.auth.current_user
        )
    
    def cancel_application(self, app_id: str):
        """Отмена заявки"""
        if not self.auth.current_user:
            raise PermissionError("Необходима авторизация")
        
        applications = self.app_manager.get_applications_for_user(self.auth.current_user)
        if app_id not in applications:
            raise PermissionError("Заявка не найдена или нет прав доступа")
        
        # Проверяем права: заказчик, руководитель или администратор
        if self.auth.current_user['role'] not in ['customer', 'manager', 'admin']:
            raise PermissionError("Недостаточно прав для отмены заявки")
        
        self.app_manager.update_application_status(app_id, 'Отменена')
    
    def complete_application(self, app_id: str):
        """Завершение заявки (только для руководителя и администратора)"""
        if not self.has_permission('assign_stages'):
            raise PermissionError("Недостаточно прав")
        
        self.app_manager.update_application_status(app_id, 'Завершена')

if __name__ == "__main__":
    from gui_interface import GUIInterface
    print("Запуск графического интерфейса...")
    app = GUIInterface()
    app.run()
