# cli_interface.py
from main_system import MainSystem
from getpass import getpass
import os

class CLIInterface:
    def __init__(self):
        self.system = MainSystem()
        self.current_user = None
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_menu(self, title, options):
        print(f"\n{'='*50}")
        print(f" {title}")
        print(f"{'='*50}")
        for key, option in options.items():
            print(f" {key}. {option}")
        print(f"{'='*50}")
    
    def login_screen(self):
        self.clear_screen()
        print("=== СИСТЕМА УПРАВЛЕНИЯ ЗАЯВКАМИ ===")
        print("\nВход в систему:")
        
        username = input("Логин: ")
        password = getpass("Пароль: ")
        
        try:
            if self.system.login(username, password):
                self.current_user = self.system.get_current_user()
                print(f"\n✓ Успешный вход! Добро пожаловать, {self.current_user['full_name']}")
                input("\nНажмите Enter для продолжения...")
                return True
            else:
                print("\n✗ Ошибка: Неверный логин или пароль")
                input("\nНажмите Enter для продолжения...")
                return False
        except PermissionError as e:
            print(f"\n🚫 {e}")
            print("   Для разблокировки обратитесь к администратору системы.")
            input("\nНажмите Enter для продолжения...")
            return False
    
    def admin_menu(self):
        while True:
            self.clear_screen()
            print(f"Администратор: {self.current_user.full_name}")
            
            options = {
                '1': 'Управление пользователями',
                '2': 'Просмотр всех заявок',
                '3': 'Импорт данных из Excel',
                '4': 'Просмотр ресурсов',
                '0': 'Выход'
            }
            self.print_menu("МЕНЮ АДМИНИСТРАТОРА", options)
            
            choice = input("Выберите действие: ")
            
            if choice == '1':
                self.manage_users()
            elif choice == '2':
                self.view_applications()
            elif choice == '3':
                self.import_data_menu()
            elif choice == '4':
                self.view_resources()
            elif choice == '0':
                break
            else:
                print("Неверный выбор")
                input("Нажмите Enter для продолжения...")
    
    def customer_menu(self):
        while True:
            self.clear_screen()
            print(f"Заказчик: {self.current_user.full_name}")
            
            options = {
                '1': 'Создать заявку',
                '2': 'Мои заявки',
                '0': 'Выход'
            }
            self.print_menu("МЕНЮ ЗАКАЗЧИКА", options)
            
            choice = input("Выберите действие: ")
            
            if choice == '1':
                self.create_application()
            elif choice == '2':
                self.view_my_applications()
            elif choice == '0':
                break
            else:
                print("Неверный выбор")
                input("Нажмите Enter для продолжения...")
    
    def manager_menu(self):
        while True:
            self.clear_screen()
            print(f"Руководитель: {self.current_user.full_name}")
            
            options = {
                '1': 'Создать заявку',        # Новая опция для руководителя
                '2': 'Просмотр заявок',
                '3': 'Назначить этапы',
                '4': 'Редактировать заявку',  # Новая опция
                '5': 'Завершить заявку',      # Новая опция
                '0': 'Выход'
            }
            self.print_menu("МЕНЮ РУКОВОДИТЕЛЯ", options)
            
            choice = input("Выберите действие: ")
            
            if choice == '1':
                self.create_application()
            elif choice == '2':
                self.view_applications()
            elif choice == '3':
                self.assign_stages()
            elif choice == '4':
                self.edit_application()
            elif choice == '5':
                self.complete_application()
            elif choice == '0':
                break
            else:
                print("Неверный выбор")
                input("Нажмите Enter для продолжения...")
    
    def executor_menu(self):
        while True:
            self.clear_screen()
            print(f"Исполнитель: {self.current_user.full_name}")
            
            options = {
                '1': 'Мои этапы',
                '2': 'Запросить ресурсы',
                '3': 'Завершить этап',
                '0': 'Выход'
            }
            self.print_menu("МЕНЮ ИСПОЛНИТЕЛЯ", options)
            
            choice = input("Выберите действие: ")
            
            if choice == '1':
                self.view_my_stages()
            elif choice == '2':
                self.request_resources()
            elif choice == '3':
                self.complete_stage()
            elif choice == '0':
                break
            else:
                print("Неверный выбор")
                input("Нажмите Enter для продолжения...")
    
    def storeman_menu(self):
        while True:
            self.clear_screen()
            print(f"Кладовщик: {self.current_user.full_name}")
            
            options = {
                '1': 'Просмотр ресурсов',
                '2': 'Добавить ресурс',
                '3': 'Редактировать ресурс',  # Доступно для storeman
                '4': 'Выделить ресурсы',
                '5': 'Импорт ресурсов из Excel',
                '0': 'Выход'
            }
            
            # Администраторы видят дополнительную опцию удаления
            if self.current_user.role == 'admin':
                options = {
                    '1': 'Просмотр ресурсов',
                    '2': 'Добавить ресурс',
                    '3': 'Редактировать ресурс',
                    '4': 'Удалить ресурс',
                    '5': 'Выделить ресурсы',
                    '6': 'Импорт ресурсов из Excel',
                    '0': 'Выход'
                }
            
            self.print_menu("МЕНЮ КЛАДОВЩИКА", options)
            
            choice = input("Выберите действие: ")
            
            if choice == '1':
                self.view_resources()
            elif choice == '2':
                self.add_resource()
            elif choice == '3':
                self.edit_resource()  # Доступно для storeman
            elif choice == '4' and self.current_user.role == 'admin':
                self.delete_resource_cli()  # Только для admin
            elif (choice == '4' and self.current_user.role != 'admin') or (choice == '5' and self.current_user.role == 'admin'):
                self.allocate_resources()
            elif (choice == '5' and self.current_user.role != 'admin') or (choice == '6' and self.current_user.role == 'admin'):
                self.import_resources_excel()
            elif choice == '0':
                break
            else:
                print("Неверный выбор")
                input("Нажмите Enter для продолжения...")

    def delete_resource_cli(self):
        self.clear_screen()
        print("=== УДАЛЕНИЕ РЕСУРСА ===")
        
        resources = self.system.get_resources()
        
        if not resources:
            print("Ресурсы не найдены")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Доступные ресурсы:")
        resource_list = list(resources.keys())
        for i, name in enumerate(resource_list, 1):
            resource = resources[name]
            print(f"{i}. {name}: {resource['quantity']} {resource['unit']} (мин: {resource.get('min_quantity', 0)})")
        
        try:
            choice = int(input("\nВыберите номер ресурса для удаления: ")) - 1
            
            if 0 <= choice < len(resource_list):
                resource_name = resource_list[choice]
                
                # Проверяем, используется ли ресурс
                if self.system.is_resource_used(resource_name):
                    print(f"\n❌ Невозможно удалить: ресурс '{resource_name}' используется в заявках")
                    print("   Вы можете установить количество в 0, но удаление невозможно.")
                    input("\nНажмите Enter для продолжения...")
                    return
                
                confirm = input(f"\nВы уверены, что хотите удалить ресурс '{resource_name}'? (y/n): ")
                if confirm.lower() == 'y':
                    try:
                        self.system.delete_resource(resource_name)
                        print(f"✅ Ресурс '{resource_name}' успешно удален!")
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")
                else:
                    print("Удаление отменено.")
            else:
                print("Неверный выбор")
                
        except ValueError:
            print("Ошибка: Введите номер ресурса")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")

    def edit_resource(self):
        self.clear_screen()
        print("=== РЕДАКТИРОВАНИЕ РЕСУРСА ===")
        
        resources = self.system.get_resources()
        
        if not resources:
            print("Ресурсы не найдены")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Доступные ресурсы:")
        for i, name in enumerate(resources.keys(), 1):
            resource = resources[name]
            print(f"{i}. {name}: {resource.quantity} {resource.unit} (мин: {resource.min_quantity})")
        
        try:
            choice = int(input("\nВыберите номер ресурса для редактирования: ")) - 1
            resource_names = list(resources.keys())
            
            if 0 <= choice < len(resource_names):
                resource_name = resource_names[choice]
                resource = resources[resource_name]
                
                print(f"\nРедактирование ресурса: {resource_name}")
                print(f"Текущие значения: {resource.quantity} {resource.unit} (мин: {resource.min_quantity})")
                
                print("\nВведите новые значения (оставьте пустым, чтобы не менять):")
                
                quantity_str = input(f"Количество [{resource.quantity}]: ")
                unit = input(f"Единица измерения [{resource.unit}]: ")
                min_quantity_str = input(f"Минимальный запас [{resource.min_quantity}]: ")
                
                # Подготавливаем параметры для обновления
                update_params = {}
                
                if quantity_str:
                    try:
                        update_params['quantity'] = int(quantity_str)
                    except ValueError:
                        print("Ошибка: Количество должно быть числом")
                        return
                
                if unit:
                    update_params['unit'] = unit
                
                if min_quantity_str:
                    try:
                        update_params['min_quantity'] = int(min_quantity_str)
                    except ValueError:
                        print("Ошибка: Минимальный запас должен быть числом")
                        return
                
                if update_params:
                    try:
                        self.system.update_resource(resource_name, **update_params)
                        print("Ресурс успешно обновлен!")
                    except Exception as e:
                        print(f"Ошибка: {e}")
                else:
                    print("Изменения не внесены")
            else:
                print("Неверный выбор")
                
        except ValueError:
            print("Ошибка: Введите номер ресурса")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")

    def manage_users(self):
        self.clear_screen()
        print("=== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ===")
        
        options = {
            '1': 'Добавить пользователя',
            '2': 'Удалить пользователя',
            '0': 'Назад'
        }
        self.print_menu("УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ", options)
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            self.add_user()
        elif choice == '2':
            self.delete_user()
    
    def add_user(self):
        print("\n--- ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ---")
        username = input("Логин: ")
        password = getpass("Пароль: ")
        full_name = input("ФИО: ")
        
        print("Роли: customer, manager, executor, storeman, admin")
        role = input("Роль: ")
        department = input("Отдел: ")
        
        try:
            self.system.register_user(username, password, role, full_name, department)
            print(f"Пользователь {username} успешно создан!")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def delete_user(self):
        print("\n--- УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ---")
        username = input("Логин пользователя для удаления: ")
        
        try:
            self.system.auth.delete_user(username)
            print(f"Пользователь {username} удален!")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def create_application(self):
        self.clear_screen()
        print("=== СОЗДАНИЕ ЗАЯВКИ ===")
        
        contract_number = input("Номер договора: ")
        customer_name = input("ФИО заказчика: ")  # Новое поле
        description = input("Описание: ")
        address = input("Адрес заказчика: ")
        
        try:
            app_id = self.system.create_application(contract_number, description, address, customer_name)
            print(f"Заявка создана! ID: {app_id}")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")

    def edit_application(self):
        self.clear_screen()
        print("=== РЕДАКТИРОВАНИЕ ЗАЯВКИ ===")
        
        applications = self.system.get_my_applications()
        
        if not applications:
            print("Заявки не найдены")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Ваши заявки со статусом 'Новая':")
        new_apps = {}
        for app_id, application in applications.items():
            if application.get('status') == 'Новая':
                print(f"ID: {app_id}")
                print(f"Договор: {application['contract_number']}")
                print(f"Описание: {application['description']}")
                print(f"Адрес: {application.get('address', 'Не указан')}")
                print("-" * 30)
                new_apps[app_id] = application
        
        if not new_apps:
            print("Нет заявок со статусом 'Новая' для редактирования")
            input("\nНажмите Enter для продолжения...")
            return
        
        app_id = input("Введите ID заявки для редактирования: ")
        
        if app_id not in new_apps:
            print("Заявка не найдена или недоступна для редактирования")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("\nОставьте поле пустым, чтобы не изменять значение:")
        contract_number = input(f"Новый номер договора [{new_apps[app_id]['contract_number']}]: ")
        description = input(f"Новое описание [{new_apps[app_id]['description']}]: ")
        address = input(f"Новый адрес [{new_apps[app_id].get('address', '')}]: ")
        
        try:
            self.system.update_application(
                app_id,
                contract_number if contract_number else None,
                description if description else None,
                address if address else None
            )
            print("Заявка успешно обновлена!")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")

    def customer_menu(self):
        while True:
            self.clear_screen()
            print(f"Заказчик: {self.current_user.full_name}")
            
            options = {
                '1': 'Создать заявку',
                '2': 'Мои заявки',
                '3': 'Редактировать заявку',  # Новая опция
                '4': 'Отменить заявку',       # Новая опция
                '0': 'Выход'
            }
            self.print_menu("МЕНЮ ЗАКАЗЧИКА", options)
            
            choice = input("Выберите действие: ")
            
            if choice == '1':
                self.create_application()
            elif choice == '2':
                self.view_my_applications()
            elif choice == '3':
                self.edit_application()
            elif choice == '4':
                self.cancel_application()
            elif choice == '0':
                break
            else:
                print("Неверный выбор")
                input("Нажмите Enter для продолжения...")

    def cancel_application(self):
        self.clear_screen()
        print("=== ОТМЕНА ЗАЯВКИ ===")
        
        applications = self.system.get_my_applications()
        
        if not applications:
            print("Заявки не найдены")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Ваши заявки:")
        for app_id, application in applications.items():
            if application.get('status') in ['Новая', 'В работе']:
                print(f"ID: {app_id}")
                print(f"Договор: {application['contract_number']}")
                print(f"Описание: {application['description']}")
                print(f"Статус: {application['status']}")
                print("-" * 30)
        
        app_id = input("Введите ID заявки для отмены: ")
        
        try:
            self.system.cancel_application(app_id)
            print("Заявка успешно отменена!")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")

    def complete_application(self):
        self.clear_screen()
        print("=== ЗАВЕРШЕНИЕ ЗАЯВКИ ===")
        
        applications = self.system.get_my_applications()
        
        if not applications:
            print("Заявки не найдены")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Доступные заявки:")
        for app_id, application in applications.items():
            if application.get('status') in ['Новая', 'В работе']:
                print(f"ID: {app_id}")
                print(f"Договор: {application['contract_number']}")
                print(f"Описание: {application['description']}")
                print(f"Статус: {application['status']}")
                print("-" * 30)
        
        app_id = input("Введите ID заявки для завершения: ")
        
        try:
            self.system.complete_application(app_id)
            print("Заявка успешно завершена!")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")

    def view_my_applications(self):
        self.clear_screen()
        print("=== МОИ ЗАЯВКИ ===")
        
        applications = self.system.get_my_applications()
        
        if not applications:
            print("Заявки не найдены")
        else:
            for app_id, application in applications.items():
                print(f"\nID: {app_id}")
                print(f"Дата: {application['date']}")
                print(f"Договор: {application['contract_number']}")
                print(f"ФИО заказчика: {application.get('customer_name', 'Не указано')}")  # Новое поле
                print(f"Описание: {application['description']}")
                print(f"Адрес: {application.get('address', 'Не указан')}")
                print(f"Статус: {application['status']}")
                print(f"Этапы: {len(application.get('stages', {}))}")
                print("-" * 30)
        
        input("\nНажмите Enter для продолжения...")
    
    def view_applications(self):
        self.clear_screen()
        print("=== ВСЕ ЗАЯВКИ ===")
        
        applications = self.system.get_my_applications()
        
        if not applications:
            print("Заявки не найдены")
        else:
            for app_id, application in applications.items():
                print(f"\nID: {app_id}")
                print(f"Дата: {application['date']}")
                print(f"ФИО заказчика: {application.get('customer_name', 'Не указано')}")  # Используем ФИО вместо логина
                print(f"Договор: {application['contract_number']}")
                print(f"Описание: {application['description']}")
                print(f"Адрес: {application.get('address', 'Не указан')}")
                print(f"Статус: {application['status']}")
                
                if application['stages']:
                    print("Этапы:")
                    for stage_id, stage in application['stages'].items():
                        print(f"  - {stage['name']}: {stage['status']} (Исполнитель: {stage['executor']})")
                print("-" * 50)
        
        input("\nНажмите Enter для продолжения...")
    
    def assign_stages(self):
        self.clear_screen()
        print("=== НАЗНАЧЕНИЕ ЭТАПОВ ===")
        
        applications = self.system.get_my_applications()
        
        if not applications:
            print("Нет доступных заявок")
            input("\nНажмите Enter для продолжения...")
            return
        
        # Получаем исполнителей
        try:
            all_users = self.system.get_all_users()
            executors = [username for username, user_data in all_users.items() 
                        if user_data.get('role') == 'executor']
        except:
            executors = []
        
        if not executors:
            print("Нет доступных исполнителей")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Доступные заявки (по номеру договора):")
        app_options = {}
        for app_id, application in applications.items():
            if application.get('status') in ['Новая', 'В работе']:
                contract = application.get('contract_number', 'Без договора')
                print(f"{contract}: {application.get('description', '')[:50]}...")
                app_options[contract] = app_id
        
        if not app_options:
            print("Нет заявок для назначения этапов")
            input("\nНажмите Enter для продолжения...")
            return
        
        contract_number = input("\nВведите номер договора заявки: ")
        
        if contract_number not in app_options:
            print("Заявка с таким номером договора не найдена")
            input("\nНажмите Enter для продолжения...")
            return
        
        app_id = app_options[contract_number]
        
        while True:
            print(f"\nИсполнители: {', '.join(executors)}")
            stage_description = input("Описание этапа (или 'stop' для завершения): ")
            if stage_description.lower() == 'stop':
                break
            
            print("Доступные исполнители:")
            for i, executor in enumerate(executors, 1):
                print(f"{i}. {executor}")
            
            try:
                executor_choice = int(input("Выберите номер исполнителя: ")) - 1
                if 0 <= executor_choice < len(executors):
                    executor = executors[executor_choice]
                else:
                    print("Неверный выбор исполнителя")
                    continue
            except ValueError:
                print("Введите номер исполнителя")
                continue
            
            try:
                stage_id = self.system.assign_stage(app_id, stage_description, executor)
                print(f"Этап создан: {stage_id}")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    # cli_interface.py - обновим метод view_my_stages
    def view_my_stages(self):
        self.clear_screen()
        print("=== МОИ ЭТАПЫ ===")
        
        stages = self.system.get_my_stages()
        
        if not stages:
            print("Этапы не найдены")
        else:
            for app_id, app_stages in stages.items():
                application = self.system.app_manager.get_application(app_id)
                print(f"\nЗаявка: {app_id}")
                print(f"Договор: {application.contract_number}")
                print(f"Описание: {application.description}")
                for stage_id, stage in app_stages.items():
                    print(f"  Этап: {stage.name}")
                    print(f"    ID: {stage_id}")
                    print(f"    Статус: {stage.status}")
                    print(f"    Отчет: {stage.report or 'Нет отчета'}")
                    if stage.requested_resources:
                        print("    Запрошенные ресурсы:")
                        for i, resource in enumerate(stage.requested_resources, 1):
                            print(f"      {i}. {resource['resource']}: {resource['quantity']} (Статус: {resource['status']})")
                    else:
                        print("    Запрошенные ресурсы: Нет")
                    print("    " + "-" * 20)
        
        input("\nНажмите Enter для продолжения...")
    
    def request_resources(self):
        self.clear_screen()
        print("=== ЗАПРОС РЕСУРСОВ ===")
        
        stages = self.system.get_my_stages()
        
        if not stages:
            print("Нет доступных этапов")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Ваши этапы:")
        stage_list = []
        for app_id, app_stages in stages.items():
            for stage_id, stage in app_stages.items():
                if stage.status != 'completed':
                    print(f"{stage_id}: {stage.name} (Заявка: {app_id})")
                    stage_list.append((app_id, stage_id, stage))
        
        if not stage_list:
            print("Все этапы завершены")
            input("\nНажмите Enter для продолжения...")
            return
        
        stage_id = input("\nВведите ID этапа: ")
        
        # Находим выбранный этап
        selected_stage = None
        selected_app_id = None
        for app_id, st_id, stage in stage_list:
            if st_id == stage_id:
                selected_stage = stage
                selected_app_id = app_id
                break
        
        if not selected_stage:
            print("Этап не найден")
            input("\nНажмите Enter для продолжения...")
            return
        
        # Получаем список ресурсов
        try:
            resources = self.system.get_resources()
            resource_names = list(resources.keys())
            
            if not resource_names:
                print("Нет доступных ресурсов на складе")
                input("\nНажмите Enter для продолжения...")
                return
                
            print("\nДоступные ресурсы:")
            for i, name in enumerate(resource_names, 1):
                resource = resources[name]
                print(f"{i}. {name}: {resource.quantity} {resource.unit}")
            
            try:
                resource_choice = int(input("\nВыберите номер ресурса: ")) - 1
                if 0 <= resource_choice < len(resource_names):
                    resource_name = resource_names[resource_choice]
                else:
                    print("Неверный выбор ресурса")
                    return
            except ValueError:
                print("Ошибка: Введите номер ресурса")
                return
        
        except Exception as e:
            print(f"Ошибка при получении ресурсов: {e}")
            return
        
        quantity = int(input("Количество: "))
        
        try:
            self.system.request_resources(selected_app_id, stage_id, resource_name, quantity)
            print("Ресурс запрошен успешно!")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")

    def complete_stage(self):
        self.clear_screen()
        print("=== ЗАВЕРШЕНИЕ ЭТАПА ===")
        
        stages = self.system.get_my_stages()
        
        if not stages:
            print("Нет доступных этапов")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Ваши этапы:")
        stage_list = []
        for app_id, app_stages in stages.items():
            for stage_id, stage in app_stages.items():
                if stage.status != 'completed':
                    print(f"{stage_id}: {stage.name} (Заявка: {app_id})")
                    stage_list.append((app_id, stage_id, stage))
        
        if not stage_list:
            print("Все этапы завершены")
            input("\nНажмите Enter для продолжения...")
            return
        
        stage_id = input("\nВведите ID этапа: ")
        
        # Находим выбранный этап
        selected_stage = None
        selected_app_id = None
        for app_id, st_id, stage in stage_list:
            if st_id == stage_id:
                selected_stage = stage
                selected_app_id = app_id
                break
        
        if not selected_stage:
            print("Этап не найден")
            input("\nНажмиte Enter для продолжения...")
            return
        
        report = input("Отчет о выполнении: ")
        
        try:
            self.system.complete_stage(selected_app_id, stage_id, report)
            print("Этап завершен успешно!")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def view_resources(self):
        self.clear_screen()
        print("=== РЕСУРСЫ НА СКЛАДЕ ===")
        
        resources = self.system.get_resources()
        
        if not resources:
            print("Ресурсы не найдены")
        else:
            for name, resource in resources.items():
                print(f"{name}: {resource.quantity} {resource.unit} (мин: {resource.min_quantity})")
        
        input("\nНажмите Enter для продолжения...")
    
    def add_resource(self):
        self.clear_screen()
        print("=== ДОБАВЛЕНИЕ РЕСУРСА ===")
        
        name = input("Название ресурса: ")
        quantity = int(input("Количество: "))
        unit = input("Единица измерения: ")
        min_quantity = int(input("Минимальный запас: ") or 0)
        
        # Выбор типа ресурса
        print("\nТипы ресурсов:")
        resource_types = self.system.get_resource_types()
        for i, rt in enumerate(resource_types, 1):
            print(f"{i}. {rt.name} - {rt.description}")
        
        try:
            type_choice = int(input("\nВыберите тип ресурса: ")) - 1
            if 0 <= type_choice < len(resource_types):
                resource_type = resource_types[type_choice].type
                
                # Ввод атрибутов
                print("\nВвод атрибутов (оставьте пустым для пропуска):")
                attributes = {}
                type_attributes = self.system.get_resource_type_attributes(resource_type)
                
                for attr in type_attributes:
                    value = input(f"{attr['label']}{'*' if attr.get('required', False) else ''}: ")
                    if value.strip():
                        attributes[attr['name']] = value.strip()
                
                self.system.add_resource(name, quantity, unit, min_quantity, resource_type, attributes)
                print("Ресурс добавлен успешно!")
            else:
                print("Неверный выбор типа")
                
        except ValueError:
            print("Ошибка: Введите номер типа")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    # cli_interface.py - заменим метод allocate_resources
    def allocate_resources(self):
        self.clear_screen()
        print("=== ВЫДЕЛЕНИЕ РЕСУРСОВ ===")
    
        try:
            # Получаем все pending запросы через новый метод
            pending_requests = self.system.get_pending_resource_requests()
        
            if not pending_requests:
                print("Нет запросов на ресурсы со статусом 'requested'")
                input("\nНажмите Enter для продолжения...")
                return
        
            print("Запросы на ресурсы:")
            for i, request in enumerate(pending_requests, 1):
                print(f"{i}. Заявка: {request['app_id']}")
                print(f"   Этап: {request['stage_name']} (ID: {request['stage_id']})")
                print(f"   Исполнитель: {request['executor']}")
                print(f"   Ресурс: {request['resource']}, Количество: {request['quantity']}")
                print("   " + "-" * 40)
        
            try:
                choice = int(input("\nВыберите запрос для выделения (номер): ")) - 1
                if 0 <= choice < len(pending_requests):
                    request = pending_requests[choice]
                
                    # Проверяем доступность ресурсов
                    resources = self.system.get_resources()
                    resource_name = request['resource']
                
                    if resource_name not in resources:
                        print(f"Ошибка: Ресурс '{resource_name}' не найден на складе")
                    elif resources[resource_name].quantity < request['quantity']:
                        available = resources[resource_name].quantity
                        print(f"Ошибка: Недостаточно ресурсов. Доступно: {available}, Запрошено: {request['quantity']}")
                    else:
                        # Выделяем ресурсы
                        self.system.allocate_resources(
                            request['app_id'], 
                            request['stage_id'], 
                            request['resource']
                        )
                        print("Ресурсы выделены успешно!")
                else:
                    print("Неверный выбор")
            except ValueError:
                print("Ошибка: Введите номер запроса")
    
        except Exception as e:
            print(f"Ошибка при получении запросов: {e}")
    
        input("\nНажмите Enter для продолжения...")
        self.clear_screen()
        print("=== ВЫДЕЛЕНИЕ РЕСУРСОВ ===")
        
        # Находим заявки с запрошенными ресурсами
        applications = self.system.get_my_applications()
        pending_requests = []
        
        for app_id, application in applications.items():
            for stage_id, stage in application.stages.items():
                for request in stage.requested_resources:
                    if request['status'] == 'requested':
                        pending_requests.append({
                            'app_id': app_id,
                            'stage_id': stage_id,
                            'stage_name': stage.name,
                            'resource': request['resource'],
                            'quantity': request['quantity']
                        })
        
        if not pending_requests:
            print("Нет запросов на ресурсы")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Запросы на ресурсы:")
        for i, request in enumerate(pending_requests, 1):
            print(f"{i}. Заявка {request['app_id']}, Этап: {request['stage_name']}")
            print(f"   Ресурс: {request['resource']}, Количество: {request['quantity']}")
        
        try:
            choice = int(input("\nВыберите запрос для выделения: ")) - 1
            if 0 <= choice < len(pending_requests):
                request = pending_requests[choice]
                self.system.allocate_resources(request['app_id'], request['stage_id'], request['resource'])
                print("Ресурсы выделены успешно!")
            else:
                print("Неверный выбор")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def import_data_menu(self):
        self.clear_screen()
        print("=== ИМПОРТ ДАННЫХ ===")
        
        options = {
            '1': 'Импорт пользователей',
            '2': 'Импорт ресурсов',
            '0': 'Назад'
        }
        self.print_menu("ИМПОРТ ДАННЫХ ИЗ EXCEL", options)
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            file_path = input("Путь к файлу Excel: ")
            try:
                self.system.import_users_from_excel(file_path)
                print("Пользователи импортированы успешно!")
            except Exception as e:
                print(f"Ошибка: {e}")
        elif choice == '2':
            file_path = input("Путь к файлу Excel: ")
            try:
                self.system.import_resources_from_excel(file_path)
                print("Ресурсы импортированы успешно!")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def import_resources_excel(self):
        self.clear_screen()
        print("=== ИМПОРТ РЕСУРСОВ ИЗ EXCEL ===")
        
        file_path = input("Путь к файлу Excel: ")
        try:
            self.system.import_resources_from_excel(file_path)
            print("Ресурсы импортированы успешно!")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def main_loop(self):
        # Инициализация тестовых данных
        self.initialize_test_data()
        
        while True:
            if not self.current_user:
                if not self.login_screen():
                    continue
            
            # Роутинг по ролям
            if self.current_user.role == 'admin':
                self.admin_menu()
            elif self.current_user.role == 'customer':
                self.customer_menu()
            elif self.current_user.role == 'manager':
                self.manager_menu()
            elif self.current_user.role == 'executor':
                self.executor_menu()
            elif self.current_user.role == 'storeman':
                self.storeman_menu()
            
            # Выход из системы после выхода из меню
            self.current_user = None
            self.system.logout()
            
            cont = input("\nВыйти из системы? (y/n): ")
            if cont.lower() == 'y':
                break
    
    def initialize_test_data(self):
        """Инициализация тестовых данных при первом запуске"""
        try:
            # Создаем администратора если его нет
            self.system.auth.register_user("admin", "admin123", "admin", "Администратор Системы")
            print("Создан администратор: admin/admin123")
        except:
            pass  # Администратор уже существует
        
        try:
            # Создаем тестовых пользователей
            test_users = [
                ("customer1", "pass123", "customer", "Иванов Иван", "ООО 'Ромашка'"),
                ("manager1", "pass123", "manager", "Петров Петр", "Отдел разработки"),
                ("executor1", "pass123", "executor", "Сидоров Алексей", "Отдел разработки"),
                ("storeman1", "pass123", "storeman", "Кузнецова Мария", "Склад")
            ]
            
            for username, password, role, full_name, department in test_users:
                try:
                    self.system.auth.register_user(username, password, role, full_name, department)
                    print(f"Создан пользователь: {username}/{password}")
                except:
                    pass  # Пользователь уже существует
            
            # Добавляем тестовые ресурсы
            try:
                self.system.add_resource("Ноутбук", 10, "шт", 2)
                self.system.add_resource("Монитор", 15, "шт", 3)
                self.system.add_resource("Клавиатура", 20, "шт", 5)
                print("Добавлены тестовые ресурсы")
            except:
                pass
            
        except Exception as e:
            print(f"Ошибка инициализации: {e}")

if __name__ == "__main__":
    interface = CLIInterface()
    interface.main_loop()
