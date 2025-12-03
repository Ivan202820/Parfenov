# extended_admin.py
from data_manager import DataManager
from models import User, UserStatus
from typing import Dict, List
import hashlib

class ExtendedAdminSystem:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def create_user(self, admin_user, username: str, password: str, role: str, 
                   full_name: str, department: str = ""):
        """Создание пользователя"""
        if admin_user.role != 'admin':
            raise PermissionError("Только администратор может создавать пользователей")
        
        users = self.data_manager.load_users()
        
        if username in users:
            raise ValueError("Пользователь уже существует")
        
        users[username] = User(
            username=username,
            password_hash=self._hash_password(password),
            role=role,
            full_name=full_name,
            department=department,
            status=UserStatus.ACTIVE
        )
        
        self.data_manager.save_users(users)
        return username
    
    def block_user(self, admin_user, username: str):
        """Блокировка пользователя"""
        if admin_user.role != 'admin':
            raise PermissionError("Только администратор может блокировать пользователей")
        
        users = self.data_manager.load_users()
        
        if username not in users:
            raise ValueError("Пользователь не найден")
        
        if users[username].get('role') == 'admin':
            raise PermissionError("Нельзя заблокировать администратора")
        
        # ИСПРАВЛЕНИЕ: Убедимся, что статус сохраняется как строка
        users[username]['status'] = 'blocked'
        self.data_manager.save_users(users)
    
    def unblock_user(self, admin_user, username: str):
        """Разблокировка пользователя"""
        if admin_user.role != 'admin':
            raise PermissionError("Только администратор может разблокировать пользователей")
        
        users = self.data_manager.load_users()
        
        if username not in users:
            raise ValueError("Пользователь не найден")
        
        # ИСПРАВЛЕНИЕ: Убедимся, что статус сохраняется как строка
        users[username]['status'] = 'active'
        self.data_manager.save_users(users)
    
    def delete_user(self, admin_user, username: str):
        """Удаление пользователя"""
        if admin_user.role != 'admin':
            raise PermissionError("Только администратор может удалять пользователей")
        
        users = self.data_manager.load_users()
        
        if username not in users:
            raise ValueError("Пользователь не найден")
        
        if users[username].role == 'admin':
            raise PermissionError("Нельзя удалить администратора")
        
        # Проверяем, нет ли у пользователя активных заявок или этапов
        applications = self.data_manager.load_applications()
        
        # Проверка заявок заказчика
        customer_apps = [app for app in applications.values() if app.customer == username]
        if customer_apps:
            raise ValueError(f"Пользователь является заказчиком в {len(customer_apps)} заявках")
        
        # Проверка этапов исполнителя
        executor_stages = []
        for app in applications.values():
            for stage in app.stages.values():
                if stage.executor == username and stage.status != 'completed':
                    executor_stages.append(f"{app.id}/{stage.id}")
        
        if executor_stages:
            raise ValueError(f"Пользователь является исполнителем в {len(executor_stages)} активных этапах")
        
        del users[username]
        self.data_manager.save_users(users)
    
    def change_user_role(self, admin_user, username: str, new_role: str):
        """Изменение роли пользователя"""
        if admin_user.role != 'admin':
            raise PermissionError("Только администратор может изменять роли пользователей")
        
        users = self.data_manager.load_users()
        
        if username not in users:
            raise ValueError("Пользователь не найден")
        
        if users[username].role == 'admin' and new_role != 'admin':
            raise PermissionError("Нельзя изменить роль администратора")
        
        users[username].role = new_role
        self.data_manager.save_users(users)
    
    def reset_user_password(self, admin_user, username: str, new_password: str):
        """Сброс пароля пользователя"""
        if admin_user.role != 'admin':
            raise PermissionError("Только администратор может сбрасывать пароли")
        
        users = self.data_manager.load_users()
        
        if username not in users:
            raise ValueError("Пользователь не найден")
        
        users[username].password_hash = self._hash_password(new_password)
        self.data_manager.save_users(users)
    
    def get_users_statistics(self):
        """Статистика по пользователям"""
        users = self.data_manager.load_users()
        
        stats = {
            'total_users': len(users),
            'by_role': {},
            'by_status': {
                'active': 0,
                'blocked': 0
            },
            'recent_users': 0
        }
        
        # Статистика по ролям и статусам
        for user in users.values():
            stats['by_role'][user.role] = stats['by_role'].get(user.role, 0) + 1
            
            if user.status == UserStatus.ACTIVE:
                stats['by_status']['active'] += 1
            else:
                stats['by_status']['blocked'] += 1
        
        return stats
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
