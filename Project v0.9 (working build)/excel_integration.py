# excel_integration.py
import pandas as pd
from data_manager import DataManager
from models import User, Resource

class ExcelIntegration:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def import_users(self, file_path: str, user):
        if user.role != 'admin':
            raise PermissionError("Только администратор может импортировать пользователей")
        
        df = pd.read_excel(file_path)
        users = self.data_manager.load_users()
        
        for _, row in df.iterrows():
            username = row['username']
            if username not in users:
                users[username] = User(
                    username=username,
                    password_hash=row['password_hash'],
                    role=row['role'],
                    full_name=row['full_name'],
                    department=row.get('department', '')
                )
        
        self.data_manager.save_users(users)
    
    def import_resources(self, file_path: str, user):
        if user.role not in ['storeman', 'admin']:
            raise PermissionError("Только работник склада или администратор может импортировать ресурсы")
        
        df = pd.read_excel(file_path)
        resources = self.data_manager.load_resources()
        
        for _, row in df.iterrows():
            name = row['name']
            resources[name] = Resource(
                name=name,
                quantity=row['quantity'],
                unit=row['unit'],
                min_quantity=row.get('min_quantity', 0)
            )
        
        self.data_manager.save_resources(resources)
