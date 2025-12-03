# authentication.py
import hashlib
from data_manager import DataManager
from datetime import datetime  # Добавьте этот импорт, если его нет

class Authentication:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username: str, password: str) -> bool:
        users = self.data_manager.load_users()
        user = users.get(username)
        
        # Проверяем существование пользователя, пароль и статус
        if user and user.get('password_hash') == self.hash_password(password):
            # ДОБАВЛЕНО: Проверка статуса пользователя
            if user.get('status') == 'blocked':
                raise PermissionError("Учетная запись заблокирована. Обратитесь к администратору.")
            
            self.current_user = user
            return True
        return False
    
    def logout(self):
        self.current_user = None
    
    # В authentication.py обновите метод register_user:

    def register_user(self, username: str, password: str, role: str, full_name: str, department: str = ""):
        users = self.data_manager.load_users()
        
        if username in users:
            # Если пользователь существует, обновляем его данные
            users[username].update({
                'password_hash': self.hash_password(password),
                'role': role,
                'full_name': full_name,
                'department': department,
                'status': 'active'  # При обновлении сбрасываем статус на активный
            })
        else:
            # Создаем нового пользователя
            users[username] = {
                'username': username,
                'password_hash': self.hash_password(password),
                'role': role,
                'full_name': full_name,
                'department': department,
                'status': 'active',  # По умолчанию активный
                'created_at': datetime.now().isoformat()  # ИСПРАВЛЕНО: было datename
            }
        
        self.data_manager.save_users(users)
    
    def delete_user(self, username: str):
        users = self.data_manager.load_users()
        if username not in users:
            raise ValueError("Пользователь не найден")
        
        del users[username]
        self.data_manager.save_users(users)
