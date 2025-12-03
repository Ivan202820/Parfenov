# data_manager.py
import json
import os
from typing import Dict, Any

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.users_file = f"{self.data_dir}/users.json"
        self.applications_file = f"{self.data_dir}/applications.json"
        self.resources_file = f"{self.data_dir}/resources.json"
        self._ensure_data_dir()

    def load_stage_templates(self):
        """Загрузка шаблонов этапов"""
        return self.load_data('stage_templates.json', {})

    def save_stage_templates(self, templates):
        """Сохранение шаблонов этапов"""
        self.save_data('stage_templates.json', templates)

    def load_inventories(self):
        """Загрузка инвентаризаций"""
        return self.load_data('inventories.json', {})

    def save_inventories(self, inventories):
        """Сохранение инвентаризаций"""
        self.save_data('inventories.json', inventories)

    def load_stock_receipts(self):
        """Загрузка приходных накладных"""
        return self.load_data('stock_receipts.json', {})
    
    def save_stock_receipts(self, receipts):
        """Сохранение приходных накладных"""
        self.save_data('stock_receipts.json', receipts)

    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return {}
    
    def save_users(self, users):
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=4, default=str)
    
    def load_applications(self):
        try:
            with open(self.applications_file, 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return {}
    
    def save_applications(self, applications):
        with open(self.applications_file, 'w') as f:
            json.dump(applications, f, indent=4, default=str)
    
    def load_resources(self):
        try:
            with open(self.resources_file, 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return {}
    
    def save_resources(self, resources):
        with open(self.resources_file, 'w') as f:
            json.dump(resources, f, indent=4, default=str)
    
    def load_data(self, filename: str, default=None):
        """Универсальный метод загрузки данных"""
        try:
            with open(f"{self.data_dir}/{filename}", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default if default is not None else {}
    
    def save_data(self, filename: str, data):
        """Универсальный метод сохранения данных"""
        with open(f"{self.data_dir}/{filename}", 'w') as f:
            json.dump(data, f, indent=4, default=str)
