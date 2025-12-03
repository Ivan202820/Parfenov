# application_manager.py - обновленный файл
from datetime import datetime
from data_manager import DataManager

class ApplicationManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def create_application(self, contract_number: str, description: str, address: str = "", customer_name: str = "") -> str:
        """
        Создание заявки в системе
        
        Args:
            contract_number: Номер договора
            description: Описание заявки
            address: Адрес заказчика
            customer_name: ФИО заказчика
            
        Returns:
            ID созданной заявки
        """
        applications = self.data_manager.load_applications()
        app_id = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        applications[app_id] = {
            'id': app_id,
            'date': datetime.now().isoformat(),
            'customer_name': customer_name,  # Теперь используем только ФИО
            'contract_number': contract_number,
            'description': description,
            'address': address,
            'status': 'Новая',
            'stages': {}
        }
        
        self.data_manager.save_applications(applications)
        return app_id

    def update_application(self, app_id: str, contract_number: str = None, description: str = None, address: str = None, customer_name: str = None, user=None):
        """Редактирование заявки (только в статусе 'Новая')"""
        applications = self.data_manager.load_applications()
        
        if app_id not in applications:
            raise ValueError("Заявка не найдена")
        
        application = applications[app_id]
        
        # ИСПРАВЛЕНИЕ: Проверяем права с учетом возможного отсутствия customer_name
        if user['role'] == 'customer':
            # Для старых заявок проверяем по логину, для новых - по ФИО
            if 'customer_name' in application:
                if application['customer_name'] != user['full_name']:
                    raise PermissionError("Вы можете редактировать только свои заявки")
            else:
                if application.get('customer') != user['username']:
                    raise PermissionError("Вы можете редактировать только свои заявки")
        
        if user['role'] not in ['customer', 'manager', 'admin']:
            raise PermissionError("Недостаточно прав для редактирования заявки")
        
        # Проверка статуса
        if application['status'] != 'Новая':
            raise ValueError("Редактирование возможно только для заявок со статусом 'Новая'")
        
        # Обновление полей
        if contract_number is not None:
            application['contract_number'] = contract_number
        if description is not None:
            application['description'] = description
        if address is not None:
            application['address'] = address
        if customer_name is not None:
            application['customer_name'] = customer_name
        
        self.data_manager.save_applications(applications)
    
    def update_application_status(self, app_id: str, status: str):
        """Обновление статуса заявки"""
        applications = self.data_manager.load_applications()
        
        if app_id not in applications:
            raise ValueError("Заявка не найдена")
        
        valid_statuses = ['Новая', 'В работе', 'Завершена', 'Отменена']
        if status not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Допустимые значения: {valid_statuses}")
        
        applications[app_id]['status'] = status
        self.data_manager.save_applications(applications)
    
    def get_applications_for_user(self, user) -> dict:
        applications = self.data_manager.load_applications()
        
        if user['role'] == 'customer':
            # ИСПРАВЛЕНИЕ: Обрабатываем случаи, когда поле customer_name отсутствует
            user_apps = {}
            for app_id, app in applications.items():
                # Для старых заявок, где нет customer_name, используем логин для сравнения
                if 'customer_name' in app:
                    if app['customer_name'] == user['full_name']:
                        user_apps[app_id] = app
                else:
                    # Если customer_name отсутствует, проверяем по старому полю customer (логину)
                    if app.get('customer') == user['username']:
                        user_apps[app_id] = app
                        # Дополнительно обновляем заявку, добавляя поле customer_name
                        app['customer_name'] = user['full_name']
            return user_apps
        elif user['role'] in ['manager', 'admin']:
            return applications
        elif user['role'] == 'executor':
            user_apps = {}
            for app_id, application in applications.items():
                for stage_id, stage in application.get('stages', {}).items():
                    if stage.get('executor') == user['username']:
                        user_apps[app_id] = application
                        break
            return user_apps
        else:
            return {}
    
    def get_application(self, app_id: str):
        applications = self.data_manager.load_applications()
        return applications.get(app_id)
    
    def migrate_old_applications(self, users):
        """Миграция старых заявок: добавление поля customer_name"""
        applications = self.data_manager.load_applications()
        updated = False
        
        for app_id, application in applications.items():
            if 'customer_name' not in application and 'customer' in application:
                # Находим пользователя по логину и берем его ФИО
                customer_username = application['customer']
                if customer_username in users:
                    application['customer_name'] = users[customer_username]['full_name']
                    updated = True
        
        if updated:
            self.data_manager.save_applications(applications)
            print("Миграция заявок завершена: добавлено поле customer_name")
