# extended_main_system.py
from main_system import MainSystem

class ExtendedMainSystem(MainSystem):
    def __init__(self):
        super().__init__()
        # Временно упрощаем - добавляем расширенные функции позже
    
    def add_stock_receipt(self, resources, supplier="", document_number=""):
        """Упрощенная версия - добавление приходной накладной"""
        if not self.has_permission('manage_resources'):
            raise PermissionError("Недостаточно прав")
        
        # Создаем простую запись о поступлении
        receipt_id = f"receipt_{len(self.resource_manager.get_all_resources()) + 1}"
        
        # Обновляем остатки
        current_resources = self.get_resources()
        for resource in resources:
            name = resource['name']
            quantity = resource['quantity']
            
            if name in current_resources:
                current_resources[name]['quantity'] += quantity
            else:
                # Создаем новый ресурс
                self.add_resource(
                    name, 
                    quantity, 
                    resource.get('unit', 'шт'),
                    resource.get('min_quantity', 0)
                )
        
        return receipt_id
    
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

# Создаем алиас для обратной совместимости
MainSystem = ExtendedMainSystem
