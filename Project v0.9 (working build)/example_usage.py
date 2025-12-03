# example_usage.py
from main_system import MainSystem
from authentication import Authentication

def initialize_system(system):
    """Инициализация тестовых данных"""
    # Создаем администратора
    try:
        system.auth.register_user("admin", "admin123", "admin", "Администратор Системы")
        print("Администратор создан")
    except Exception as e:
        print(f"Администратор уже существует: {e}")
    
    # Создаем тестовых пользователей
    test_users = [
        ("customer1", "pass123", "customer", "Иванов Иван", "ООО 'Ромашка'"),
        ("manager1", "pass123", "manager", "Петров Петр", "Отдел разработки"),
        ("executor1", "pass123", "executor", "Сидоров Алексей", "Отдел разработки"),
        ("storeman1", "pass123", "storeman", "Кузнецова Мария", "Склад")
    ]
    
    for username, password, role, full_name, department in test_users:
        try:
            system.auth.register_user(username, password, role, full_name, department)
            print(f"Пользователь {username} создан")
        except Exception as e:
            print(f"Пользователь {username} уже существует: {e}")

def demo_customer_workflow(system):
    """Демонстрация работы заказчика"""
    print("\n=== Работа заказчика ===")
    if system.login("customer1", "pass123"):
        # Создание заявки
        app_id = system.create_application("Д-001", "Разработка веб-сайта")
        print(f"Создана заявка: {app_id}")
        
        # Просмотр своих заявок
        apps = system.get_my_applications()
        print("Мои заявки:", list(apps.keys()))
        
        system.logout()

def demo_manager_workflow(system):
    """Демонстрация работы руководителя"""
    print("\n=== Работа руководителя ===")
    if system.login("manager1", "pass123"):
        # Просмотр всех заявок
        apps = system.get_my_applications()
        print("Доступные заявки:", list(apps.keys()))
        
        # Назначение этапов
        if apps:
            app_id = list(apps.keys())[0]
            stage1_id = system.assign_stage(app_id, "Проектирование", "executor1")
            stage2_id = system.assign_stage(app_id, "Разработка", "executor1")
            print(f"Назначены этапы: {stage1_id}, {stage2_id}")
        
        system.logout()

def demo_executor_workflow(system):
    """Демонстрация работы исполнителя"""
    print("\n=== Работа исполнителя ===")
    if system.login("executor1", "pass123"):
        # Просмотр назначенных этапов
        stages = system.get_my_stages()
        print("Мои этапы:", stages)
        
        # Запрос ресурсов
        if stages:
            app_id = list(stages.keys())[0]
            stage_id = list(stages[app_id].keys())[0]
            system.request_resources(app_id, stage_id, "Ноутбук", 1)
            print("Запрошен ресурс: Ноутбук")
        
        system.logout()

def demo_storeman_workflow(system):
    """Демонстрация работы кладовщика"""
    print("\n=== Работа кладовщика ===")
    if system.login("storeman1", "pass123"):
        # Добавление ресурсов
        system.add_resource("Ноутбук", 5, "шт", 2)
        system.add_resource("Монитор", 10, "шт", 3)
        print("Ресурсы добавлены на склад")
        
        # Выделение ресурсов
        apps = system.get_my_applications()
        if apps:
            app_id = list(apps.keys())[0]
            app = apps[app_id]
            for stage_id, stage in app.stages.items():
                for request in stage.requested_resources:
                    if request['status'] == 'requested':
                        system.allocate_resources(app_id, stage_id, request['resource'])
                        print(f"Выделен ресурс: {request['resource']}")
        
        system.logout()

if __name__ == "__main__":
    system = MainSystem()
    
    # Инициализация системы
    initialize_system(system)
    
    # Демонстрация рабочих процессов
    demo_customer_workflow(system)
    demo_manager_workflow(system)
    demo_executor_workflow(system)
    demo_storeman_workflow(system)
    
    print("\n=== Демонстрация завершена ===")
