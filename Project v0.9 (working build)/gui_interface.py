# gui_interface.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from main_system import MainSystem
from datetime import datetime
import threading
from models import ResourceType  # ДОБАВЛЕНО: импорт ResourceType

class GUIInterface:
    def __init__(self):
        self.system = MainSystem()
        self.root = tk.Tk()
        self.root.title("Система управления заявками")
        self.root.geometry("1000x700")
        self.current_user = None
        self.setup_styles()
        self.show_login_screen()

    def show_advanced_assign_stages(self):
        """Расширенное назначение этапов с шаблонами и планированием"""
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Расширенное назначение этапов", 
                style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        # Кнопки управления шаблонами
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(buttons_frame, text="Управление шаблонами", 
                command=self.show_stage_templates_management).pack(side=tk.LEFT, padx=5)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Вкладки для разных способов назначения этапов
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка 1: Быстрое назначение (старый функционал)
        quick_frame = ttk.Frame(notebook, padding=10)
        notebook.add(quick_frame, text="Быстрое назначение")
        self.create_quick_assign_tab(quick_frame)
        
        # Вкладка 2: Назначение по шаблону
        template_frame = ttk.Frame(notebook, padding=10)
        notebook.add(template_frame, text="По шаблону")
        self.create_template_assign_tab(template_frame)
        
        # Вкладка 3: Расширенное назначение
        advanced_frame = ttk.Frame(notebook, padding=10)
        notebook.add(advanced_frame, text="Расширенное назначение")
        self.create_advanced_assign_tab(advanced_frame)

    def create_template_assign_tab(self, parent):
        """Вкладка назначения этапов по шаблону"""
        applications = self.system.get_my_applications()
        
        if not applications:
            ttk.Label(parent, text="Нет доступных заявок").pack(pady=50)
            return
        
        # Получаем шаблоны
        try:
            templates = self.system.get_stage_templates()
        except:
            templates = {}
        
        if not templates:
            ttk.Label(parent, text="Нет доступных шаблонов этапов").pack(pady=50)
            ttk.Button(parent, text="Создать шаблон", 
                    command=self.show_create_stage_template).pack(pady=10)
            return
        
        # Получаем список исполнителей
        try:
            executors = self.system.get_executors()
        except:
            executors = []
        
        if not executors:
            ttk.Label(parent, text="Нет доступных исполнителей").pack(pady=50)
            return
        
        # Список заявок
        ttk.Label(parent, text="Выберите заявку:").pack(anchor=tk.W, pady=5)
        
        app_options = []
        for app_id, application in applications.items():
            if application.get('status') in ['Новая', 'В работе']:
                contract = application.get('contract_number', 'Без договора')
                description_preview = application.get('description', '')[:30] + "..." if len(application.get('description', '')) > 30 else application.get('description', '')
                display_text = f"{contract} - {description_preview}"
                app_options.append((display_text, app_id))
        
        app_var = tk.StringVar()
        app_combobox = ttk.Combobox(parent, textvariable=app_var, 
                                values=[opt[0] for opt in app_options], state="readonly")
        app_combobox.pack(fill=tk.X, pady=5)
        
        if app_options:
            app_combobox.current(0)
        
        # Выбор шаблона
        ttk.Label(parent, text="Выберите шаблон:").pack(anchor=tk.W, pady=5)
        
        template_options = []
        for template_id, template in templates.items():
            display_text = f"{template['name']} - {template['description'][:30]}..."
            template_options.append((display_text, template_id))
        
        template_var = tk.StringVar()
        template_combobox = ttk.Combobox(parent, textvariable=template_var, 
                                        values=[opt[0] for opt in template_options], state="readonly")
        template_combobox.pack(fill=tk.X, pady=5)
        
        if template_options:
            template_combobox.current(0)
        
        # Информация о выбранном шаблоне
        template_info_label = ttk.Label(parent, text="", wraplength=400)
        template_info_label.pack(anchor=tk.W, pady=5)
        
        def update_template_info(*args):
            selected_index = template_combobox.current()
            if selected_index >= 0:
                template_id = template_options[selected_index][1]
                template = templates[template_id]
                info_text = f"Описание: {template['description']}\n"
                if template.get('typical_duration_days', 0) > 0:
                    info_text += f"Типичная длительность: {template['typical_duration_days']} дней\n"
                if template.get('required_resources'):
                    info_text += f"Ресурсы: {len(template['required_resources'])} позиций\n"
                if template.get('dependencies'):
                    info_text += f"Зависимости: {len(template['dependencies'])} этапов"
                template_info_label.config(text=info_text)
        
        template_var.trace('w', update_template_info)
        if template_options:
            update_template_info()
        
        # Исполнитель
        ttk.Label(parent, text="Исполнитель:").pack(anchor=tk.W, pady=5)
        executor_var = tk.StringVar()
        executor_combobox = ttk.Combobox(parent, textvariable=executor_var, 
                                        values=executors, state="readonly")
        executor_combobox.pack(fill=tk.X, pady=5)
        
        if executors:
            executor_combobox.current(0)
        
        # Планируемая дата начала
        ttk.Label(parent, text="Планируемая дата начала (YYYY-MM-DD):").pack(anchor=tk.W, pady=5)
        start_date_entry = ttk.Entry(parent)
        start_date_entry.pack(fill=tk.X, pady=5)
        start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        def add_stage_from_template():
            selected_app_index = app_combobox.current()
            selected_template_index = template_combobox.current()
            
            if selected_app_index < 0:
                messagebox.showerror("Ошибка", "Выберите заявку")
                return
            
            if selected_template_index < 0:
                messagebox.showerror("Ошибка", "Выберите шаблон")
                return
                
            app_id = app_options[selected_app_index][1]
            template_id = template_options[selected_template_index][1]
            executor = executor_var.get()
            planned_start_date = start_date_entry.get()
            
            if not executor:
                messagebox.showerror("Ошибка", "Выберите исполнителя")
                return
            
            try:
                stage_id = self.system.assign_stage_with_template(
                    app_id, template_id, executor, planned_start_date
                )
                messagebox.showinfo("Успех", f"Этап создан по шаблону: {stage_id}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                
        ttk.Button(parent, text="Создать этап по шаблону", 
                command=add_stage_from_template).pack(pady=10)

    def create_advanced_assign_tab(self, parent):
        """Вкладка расширенного назначения этапов с полным контролем"""
        applications = self.system.get_my_applications()
        
        if not applications:
            ttk.Label(parent, text="Нет доступных заявок").pack(pady=50)
            return
        
        # Получаем список исполнителей
        try:
            executors = self.system.get_executors()
        except:
            executors = []
        
        if not executors:
            ttk.Label(parent, text="Нет доступных исполнителей").pack(pady=50)
            return
        
        # Список заявок
        ttk.Label(parent, text="Выберите заявку:").pack(anchor=tk.W, pady=5)
        
        app_options = []
        for app_id, application in applications.items():
            if application.get('status') in ['Новая', 'В работе']:
                contract = application.get('contract_number', 'Без договора')
                description_preview = application.get('description', '')[:30] + "..." if len(application.get('description', '')) > 30 else application.get('description', '')
                display_text = f"{contract} - {description_preview}"
                app_options.append((display_text, app_id))
        
        if not app_options:
            ttk.Label(parent, text="Нет заявок для назначения этапов").pack(pady=50)
            return
        
        app_var = tk.StringVar()
        app_combobox = ttk.Combobox(parent, textvariable=app_var, 
                                values=[opt[0] for opt in app_options], state="readonly")
        app_combobox.pack(fill=tk.X, pady=5)
        app_combobox.current(0)
        
        # Основная форма
        form_frame = ttk.LabelFrame(parent, text="Детали этапа", padding=15)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Название этапа
        ttk.Label(form_frame, text="Название этапа*:").grid(row=0, column=0, sticky=tk.W, pady=8)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, pady=8, padx=5, sticky=tk.W)
        
        # Описание этапа
        ttk.Label(form_frame, text="Подробное описание*:").grid(row=1, column=0, sticky=tk.W, pady=8)
        description_text = tk.Text(form_frame, width=40, height=4)
        description_text.grid(row=1, column=1, pady=8, padx=5, sticky=tk.W)
        
        # Исполнитель
        ttk.Label(form_frame, text="Исполнитель*:").grid(row=2, column=0, sticky=tk.W, pady=8)
        executor_var = tk.StringVar()
        executor_combobox = ttk.Combobox(form_frame, textvariable=executor_var, 
                                        values=executors, state="readonly", width=37)
        executor_combobox.grid(row=2, column=1, pady=8, padx=5, sticky=tk.W)
        executor_combobox.current(0)
        
        # Плановые даты
        dates_frame = ttk.LabelFrame(form_frame, text="Плановые даты выполнения", padding=10)
        dates_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        ttk.Label(dates_frame, text="Начало (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, pady=5)
        start_date_entry = ttk.Entry(dates_frame, width=15)
        start_date_entry.grid(row=0, column=1, pady=5, padx=5)
        start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(dates_frame, text="Окончание (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20,0))
        end_date_entry = ttk.Entry(dates_frame, width=15)
        end_date_entry.grid(row=0, column=3, pady=5, padx=5)
        # По умолчанию - окончание через 7 дней
        from datetime import timedelta
        default_end = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        end_date_entry.insert(0, default_end)
        
        # Зависимости от других этапов
        dependencies_frame = ttk.LabelFrame(form_frame, text="Зависимости от других этапов", padding=10)
        dependencies_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        ttk.Label(dependencies_frame, text="Этап зависит от (ID этапов через запятую):").pack(anchor=tk.W, pady=5)
        dependencies_entry = ttk.Entry(dependencies_frame, width=60)
        dependencies_entry.pack(fill=tk.X, pady=5)
        
        # Подсказка по зависимостям
        help_label = ttk.Label(dependencies_frame, 
                            text="Пример: stage_1, stage_2. Оставьте пустым, если этап не зависит от других.",
                            font=("Arial", 9), foreground="gray")
        help_label.pack(anchor=tk.W, pady=2)
        
        # Секция для ресурсов
        resources_frame = ttk.LabelFrame(form_frame, text="Плановые ресурсы для этапа", padding=10)
        resources_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        # Таблица ресурсов
        columns = ("Ресурс", "Количество", "Единица", "Примечание")
        resources_tree = ttk.Treeview(resources_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            resources_tree.heading(col, text=col)
        
        resources_tree.column("Ресурс", width=150)
        resources_tree.column("Примечание", width=200)
        
        scrollbar = ttk.Scrollbar(resources_frame, orient=tk.VERTICAL, command=resources_tree.yview)
        resources_tree.configure(yscrollcommand=scrollbar.set)
        
        resources_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления ресурсами
        resource_buttons = ttk.Frame(resources_frame)
        resource_buttons.pack(fill=tk.X, pady=5)
        
        def add_resource_to_stage():
            """Добавление ресурса в этап"""
            resource_dialog = tk.Toplevel(parent)
            resource_dialog.title("Добавление ресурса в этап")
            resource_dialog.geometry("500x300")
            resource_dialog.transient(parent)
            resource_dialog.grab_set()
            
            ttk.Label(resource_dialog, text="Добавление ресурса в этап", 
                    style="Header.TLabel").pack(pady=10)
            
            form_frame = ttk.Frame(resource_dialog, padding=20)
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            # Название ресурса
            ttk.Label(form_frame, text="Ресурс*:").grid(row=0, column=0, sticky=tk.W, pady=5)
            resource_name_entry = ttk.Entry(form_frame, width=30)
            resource_name_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
            
            # Количество
            ttk.Label(form_frame, text="Количество*:").grid(row=1, column=0, sticky=tk.W, pady=5)
            resource_quantity_entry = ttk.Entry(form_frame, width=30)
            resource_quantity_entry.insert(0, "1")
            resource_quantity_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
            
            # Единица измерения
            ttk.Label(form_frame, text="Единица измерения*:").grid(row=2, column=0, sticky=tk.W, pady=5)
            resource_unit_entry = ttk.Entry(form_frame, width=30)
            resource_unit_entry.insert(0, "шт")
            resource_unit_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
            
            # Примечание
            ttk.Label(form_frame, text="Примечание:").grid(row=3, column=0, sticky=tk.W, pady=5)
            resource_notes_entry = ttk.Entry(form_frame, width=30)
            resource_notes_entry.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
            
            def add_resource():
                name = resource_name_entry.get().strip()
                quantity = resource_quantity_entry.get().strip()
                unit = resource_unit_entry.get().strip()
                notes = resource_notes_entry.get().strip()
                
                if not name or not quantity or not unit:
                    messagebox.showerror("Ошибка", "Заполните обязательные поля (ресурс, количество, единица)")
                    return
                
                try:
                    quantity = int(quantity)
                    if quantity <= 0:
                        messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
                        return
                        
                    resources_tree.insert("", tk.END, values=(name, quantity, unit, notes))
                    resource_dialog.destroy()
                except ValueError:
                    messagebox.showerror("Ошибка", "Количество должно быть числом")
            
            buttons_frame = ttk.Frame(form_frame)
            buttons_frame.grid(row=4, column=0, columnspan=2, pady=15)
            
            ttk.Button(buttons_frame, text="Добавить", 
                    command=add_resource).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Отмена", 
                    command=resource_dialog.destroy).pack(side=tk.LEFT, padx=5)
            
            resource_name_entry.focus()
        
        def remove_resource_from_stage():
            """Удаление ресурса из этапа"""
            selection = resources_tree.selection()
            if selection:
                resources_tree.delete(selection)
            else:
                messagebox.showinfo("Информация", "Выберите ресурс для удаления")
        
        def edit_selected_resource():
            """Редактирование выбранного ресурса"""
            selection = resources_tree.selection()
            if not selection:
                messagebox.showinfo("Информация", "Выберите ресурс для редактирования")
                return
            
            item = selection[0]
            values = resources_tree.item(item, 'values')
            
            resource_dialog = tk.Toplevel(parent)
            resource_dialog.title("Редактирование ресурса")
            resource_dialog.geometry("500x300")
            resource_dialog.transient(parent)
            resource_dialog.grab_set()
            
            ttk.Label(resource_dialog, text="Редактирование ресурса", 
                    style="Header.TLabel").pack(pady=10)
            
            form_frame = ttk.Frame(resource_dialog, padding=20)
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(form_frame, text="Ресурс*:").grid(row=0, column=0, sticky=tk.W, pady=5)
            resource_name_entry = ttk.Entry(form_frame, width=30)
            resource_name_entry.insert(0, values[0])
            resource_name_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
            
            ttk.Label(form_frame, text="Количество*:").grid(row=1, column=0, sticky=tk.W, pady=5)
            resource_quantity_entry = ttk.Entry(form_frame, width=30)
            resource_quantity_entry.insert(0, values[1])
            resource_quantity_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
            
            ttk.Label(form_frame, text="Единица измерения*:").grid(row=2, column=0, sticky=tk.W, pady=5)
            resource_unit_entry = ttk.Entry(form_frame, width=30)
            resource_unit_entry.insert(0, values[2])
            resource_unit_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
            
            ttk.Label(form_frame, text="Примечание:").grid(row=3, column=0, sticky=tk.W, pady=5)
            resource_notes_entry = ttk.Entry(form_frame, width=30)
            resource_notes_entry.insert(0, values[3] if len(values) > 3 else "")
            resource_notes_entry.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
            
            def update_resource():
                name = resource_name_entry.get().strip()
                quantity = resource_quantity_entry.get().strip()
                unit = resource_unit_entry.get().strip()
                notes = resource_notes_entry.get().strip()
                
                if not name or not quantity or not unit:
                    messagebox.showerror("Ошибка", "Заполните обязательные поля")
                    return
                
                try:
                    quantity = int(quantity)
                    if quantity <= 0:
                        messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
                        return
                        
                    resources_tree.item(item, values=(name, quantity, unit, notes))
                    resource_dialog.destroy()
                except ValueError:
                    messagebox.showerror("Ошибка", "Количество должно быть числом")
            
            buttons_frame = ttk.Frame(form_frame)
            buttons_frame.grid(row=4, column=0, columnspan=2, pady=15)
            
            ttk.Button(buttons_frame, text="Сохранить", 
                    command=update_resource).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Отмена", 
                    command=resource_dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(resource_buttons, text="Добавить ресурс", 
                command=add_resource_to_stage).pack(side=tk.LEFT, padx=5)
        ttk.Button(resource_buttons, text="Редактировать ресурс", 
                command=edit_selected_resource).pack(side=tk.LEFT, padx=5)
        ttk.Button(resource_buttons, text="Удалить ресурс", 
                command=remove_resource_from_stage).pack(side=tk.LEFT, padx=5)
        
        def create_advanced_stage():
            """Создание этапа с расширенными параметрами"""
            selected_app_index = app_combobox.current()
            if selected_app_index < 0:
                messagebox.showerror("Ошибка", "Выберите заявку")
                return
                
            app_id = app_options[selected_app_index][1]
            name = name_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            executor = executor_var.get()
            planned_start_date = start_date_entry.get().strip()
            planned_end_date = end_date_entry.get().strip()
            dependencies_str = dependencies_entry.get().strip()
            
            # Валидация обязательных полей
            if not name or not description or not executor:
                messagebox.showerror("Ошибка", "Заполните обязательные поля (название, описание, исполнитель)")
                return
            
            # Валидация дат
            try:
                if planned_start_date:
                    datetime.strptime(planned_start_date, "%Y-%m-%d")
                if planned_end_date:
                    datetime.strptime(planned_end_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
                return
            
            # Собираем ресурсы из таблицы
            required_resources = []
            for item in resources_tree.get_children():
                values = resources_tree.item(item, 'values')
                resource_data = {
                    'name': values[0],
                    'quantity': int(values[1]),
                    'unit': values[2]
                }
                if len(values) > 3 and values[3]:
                    resource_data['notes'] = values[3]
                required_resources.append(resource_data)
            
            # Обрабатываем зависимости
            dependencies = []
            if dependencies_str:
                dependencies = [dep.strip() for dep in dependencies_str.split(',') if dep.strip()]
            
            try:
                stage_id = self.system.assign_stage_with_details(
                    app_id, name, description, executor, planned_start_date, 
                    planned_end_date, dependencies, required_resources
                )
                messagebox.showinfo("Успех", f"Этап создан с расширенными параметрами!\nID: {stage_id}")
                
                # Очистка формы
                name_entry.delete(0, tk.END)
                description_text.delete("1.0", tk.END)
                start_date_entry.delete(0, tk.END)
                start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                end_date_entry.delete(0, tk.END)
                end_date_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
                dependencies_entry.delete(0, tk.END)
                
                # Очистка таблицы ресурсов
                for item in resources_tree.get_children():
                    resources_tree.delete(item)
                    
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        # Кнопка создания этапа
        create_button_frame = ttk.Frame(form_frame)
        create_button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(create_button_frame, text="Создать расширенный этап", 
                command=create_advanced_stage, style="Accent.TButton").pack(pady=10)

    def show_stage_templates_management(self):
        """Управление шаблонами этапов"""
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Управление шаблонами этапов", 
                style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        ttk.Button(header_frame, text="Создать шаблон", 
                command=self.show_create_stage_template).pack(side=tk.RIGHT)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        try:
            templates = self.system.get_stage_templates()
            
            if not templates:
                # Если шаблонов нет, показываем сообщение и кнопку создания
                no_templates_frame = ttk.Frame(main_frame)
                no_templates_frame.pack(fill=tk.BOTH, expand=True)
                
                ttk.Label(no_templates_frame, text="Шаблоны не найдены", 
                        style="Header.TLabel").pack(pady=20)
                ttk.Label(no_templates_frame, text="Создайте первый шаблон этапа для типовых работ").pack(pady=10)
                ttk.Button(no_templates_frame, text="Создать шаблон", 
                        command=self.show_create_stage_template, width=20).pack(pady=20)
                return
                
            # Таблица шаблонов
            tree_frame = ttk.Frame(main_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ("ID", "Название", "Описание", "Длительность", "Ресурсы", "Зависимости", "Создал")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
                
            tree.column("Название", width=150)
            tree.column("Описание", width=200)
            tree.column("ID", width=120)
            
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            for template_id, template in templates.items():
                tree.insert("", tk.END, values=(
                    template_id,
                    template['name'],
                    template['description'][:50] + "..." if len(template['description']) > 50 else template['description'],
                    f"{template.get('typical_duration_days', 0)} дн.",
                    len(template.get('required_resources', [])),
                    len(template.get('dependencies', [])),
                    template.get('created_by', '')
                ), tags=(template_id,))
                
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def on_item_double_click(event):
                item = tree.selection()[0]
                template_id = tree.item(item, "tags")[0]
                self.show_edit_stage_template(template_id)
                
            tree.bind("<Double-1>", on_item_double_click)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить шаблоны: {str(e)}")

    def show_create_stage_template(self):
        """Создание нового шаблона этапа"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Создание шаблона этапа")
        dialog.geometry("920x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Создание шаблона этапа", 
                style="Title.TLabel").pack(pady=10)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Название шаблона
        ttk.Label(main_frame, text="Название шаблона*:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(main_frame, width=40)
        name_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Описание шаблона
        ttk.Label(main_frame, text="Описание*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        description_text = tk.Text(main_frame, width=40, height=4)
        description_text.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Типичная длительность
        ttk.Label(main_frame, text="Типичная длительность (дней):").grid(row=2, column=0, sticky=tk.W, pady=5)
        duration_entry = ttk.Entry(main_frame, width=40)
        duration_entry.insert(0, "0")
        duration_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Секция для ресурсов
        resources_frame = ttk.LabelFrame(main_frame, text="Необходимые ресурсы", padding=10)
        resources_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        # Таблица ресурсов
        columns = ("Ресурс", "Количество", "Единица")
        resources_tree = ttk.Treeview(resources_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            resources_tree.heading(col, text=col)
        
        resources_tree.column("Ресурс", width=200)
        
        scrollbar = ttk.Scrollbar(resources_frame, orient=tk.VERTICAL, command=resources_tree.yview)
        resources_tree.configure(yscrollcommand=scrollbar.set)
        
        resources_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления ресурсами
        resource_buttons = ttk.Frame(resources_frame)
        resource_buttons.pack(fill=tk.X, pady=5)
        
        def add_resource_to_template():
            """Добавление ресурса в шаблон"""
            resource_dialog = tk.Toplevel(dialog)
            resource_dialog.title("Добавление ресурса")
            resource_dialog.geometry("400x200")
            resource_dialog.transient(dialog)
            resource_dialog.grab_set()
            
            ttk.Label(resource_dialog, text="Добавление ресурса в шаблон", 
                    style="Header.TLabel").pack(pady=10)
            
            form_frame = ttk.Frame(resource_dialog, padding=20)
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(form_frame, text="Ресурс:").grid(row=0, column=0, sticky=tk.W, pady=5)
            resource_name_entry = ttk.Entry(form_frame, width=20)
            resource_name_entry.grid(row=0, column=1, pady=5, padx=5)
            
            ttk.Label(form_frame, text="Количество:").grid(row=1, column=0, sticky=tk.W, pady=5)
            resource_quantity_entry = ttk.Entry(form_frame, width=20)
            resource_quantity_entry.insert(0, "1")
            resource_quantity_entry.grid(row=1, column=1, pady=5, padx=5)
            
            ttk.Label(form_frame, text="Единица:").grid(row=2, column=0, sticky=tk.W, pady=5)
            resource_unit_entry = ttk.Entry(form_frame, width=20)
            resource_unit_entry.insert(0, "шт")
            resource_unit_entry.grid(row=2, column=1, pady=5, padx=5)
            
            def add_resource():
                name = resource_name_entry.get()
                quantity = resource_quantity_entry.get()
                unit = resource_unit_entry.get()
                
                if not name or not quantity:
                    messagebox.showerror("Ошибка", "Заполните название и количество ресурса")
                    return
                
                try:
                    quantity = int(quantity)
                    resources_tree.insert("", tk.END, values=(name, quantity, unit))
                    resource_dialog.destroy()
                except ValueError:
                    messagebox.showerror("Ошибка", "Количество должно быть числом")
            
            ttk.Button(form_frame, text="Добавить", 
                    command=add_resource).grid(row=3, column=0, columnspan=2, pady=10)
        
        def remove_resource_from_template():
            """Удаление ресурса из шаблона"""
            selection = resources_tree.selection()
            if selection:
                resources_tree.delete(selection)
        
        ttk.Button(resource_buttons, text="Добавить ресурс", 
                command=add_resource_to_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(resource_buttons, text="Удалить ресурс", 
                command=remove_resource_from_template).pack(side=tk.LEFT, padx=5)
        
        # Секция для зависимостей (опционально)
        dependencies_frame = ttk.LabelFrame(main_frame, text="Зависимости от других этапов (опционально)", padding=10)
        dependencies_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        ttk.Label(dependencies_frame, text="ID этапов-зависимостей (через запятую):").pack(anchor=tk.W, pady=5)
        dependencies_entry = ttk.Entry(dependencies_frame, width=60)
        dependencies_entry.pack(fill=tk.X, pady=5)
        
        def create_template():
            """Создание шаблона"""
            name = name_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            duration_str = duration_entry.get().strip()
            dependencies_str = dependencies_entry.get().strip()
            
            if not name or not description:
                messagebox.showerror("Ошибка", "Заполните название и описание шаблона")
                return
            
            try:
                duration = int(duration_str) if duration_str else 0
            except ValueError:
                messagebox.showerror("Ошибка", "Длительность должна быть числом")
                return
            
            # Собираем ресурсы из таблицы
            required_resources = []
            for item in resources_tree.get_children():
                values = resources_tree.item(item, 'values')
                required_resources.append({
                    'name': values[0],
                    'quantity': int(values[1]),
                    'unit': values[2]
                })
            
            # Обрабатываем зависимости
            dependencies = []
            if dependencies_str:
                dependencies = [dep.strip() for dep in dependencies_str.split(',') if dep.strip()]
            
            try:
                template_id = self.system.create_stage_template(
                    name, description, duration, required_resources, dependencies
                )
                messagebox.showinfo("Успех", f"Шаблон создан!\nID: {template_id}")
                dialog.destroy()
                # Обновляем список шаблонов
                self.show_stage_templates_management()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        # Кнопки сохранения/отмены
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить шаблон", 
                command=create_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Устанавливаем фокус на поле названия
        name_entry.focus()

    def show_edit_stage_template(self, template_id):
        """Редактирование шаблона этапа"""
        try:
            template = self.system.get_stage_template(template_id)
            
            if not template:
                messagebox.showerror("Ошибка", "Шаблон не найден")
                return
            
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Редактирование шаблона: {template['name']}")
            dialog.geometry("700x600")
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text=f"Редактирование шаблона: {template['name']}", 
                    style="Title.TLabel").pack(pady=10)
            
            main_frame = ttk.Frame(dialog, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Название шаблона
            ttk.Label(main_frame, text="Название шаблона*:").grid(row=0, column=0, sticky=tk.W, pady=5)
            name_entry = ttk.Entry(main_frame, width=40)
            name_entry.insert(0, template['name'])
            name_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
            
            # Описание шаблона
            ttk.Label(main_frame, text="Описание*:").grid(row=1, column=0, sticky=tk.W, pady=5)
            description_text = tk.Text(main_frame, width=40, height=4)
            description_text.insert(tk.END, template['description'])
            description_text.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
            
            # Типичная длительность
            ttk.Label(main_frame, text="Типичная длительность (дней):").grid(row=2, column=0, sticky=tk.W, pady=5)
            duration_entry = ttk.Entry(main_frame, width=40)
            duration_entry.insert(0, str(template.get('typical_duration_days', 0)))
            duration_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
            
            # Секция для ресурсов
            resources_frame = ttk.LabelFrame(main_frame, text="Необходимые ресурсы", padding=10)
            resources_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
            
            # Таблица ресурсов
            columns = ("Ресурс", "Количество", "Единица")
            resources_tree = ttk.Treeview(resources_frame, columns=columns, show="headings", height=6)
            
            for col in columns:
                resources_tree.heading(col, text=col)
            
            resources_tree.column("Ресурс", width=200)
            
            scrollbar = ttk.Scrollbar(resources_frame, orient=tk.VERTICAL, command=resources_tree.yview)
            resources_tree.configure(yscrollcommand=scrollbar.set)
            
            # Заполняем существующие ресурсы
            for resource in template.get('required_resources', []):
                resources_tree.insert("", tk.END, values=(
                    resource['name'],
                    resource['quantity'],
                    resource.get('unit', 'шт')
                ))
            
            resources_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Кнопки управления ресурсами (такие же как в создании)
            resource_buttons = ttk.Frame(resources_frame)
            resource_buttons.pack(fill=tk.X, pady=5)
            
            def add_resource_to_template():
                # Такая же реализация как в show_create_stage_template
                resource_dialog = tk.Toplevel(dialog)
                resource_dialog.title("Добавление ресурса")
                resource_dialog.geometry("400x200")
                resource_dialog.transient(dialog)
                resource_dialog.grab_set()
                
                ttk.Label(resource_dialog, text="Добавление ресурса в шаблон", 
                        style="Header.TLabel").pack(pady=10)
                
                form_frame = ttk.Frame(resource_dialog, padding=20)
                form_frame.pack(fill=tk.BOTH, expand=True)
                
                ttk.Label(form_frame, text="Ресурс:").grid(row=0, column=0, sticky=tk.W, pady=5)
                resource_name_entry = ttk.Entry(form_frame, width=20)
                resource_name_entry.grid(row=0, column=1, pady=5, padx=5)
                
                ttk.Label(form_frame, text="Количество:").grid(row=1, column=0, sticky=tk.W, pady=5)
                resource_quantity_entry = ttk.Entry(form_frame, width=20)
                resource_quantity_entry.insert(0, "1")
                resource_quantity_entry.grid(row=1, column=1, pady=5, padx=5)
                
                ttk.Label(form_frame, text="Единица:").grid(row=2, column=0, sticky=tk.W, pady=5)
                resource_unit_entry = ttk.Entry(form_frame, width=20)
                resource_unit_entry.insert(0, "шт")
                resource_unit_entry.grid(row=2, column=1, pady=5, padx=5)
                
                def add_resource():
                    name = resource_name_entry.get()
                    quantity = resource_quantity_entry.get()
                    unit = resource_unit_entry.get()
                    
                    if not name or not quantity:
                        messagebox.showerror("Ошибка", "Заполните название и количество ресурса")
                        return
                    
                    try:
                        quantity = int(quantity)
                        resources_tree.insert("", tk.END, values=(name, quantity, unit))
                        resource_dialog.destroy()
                    except ValueError:
                        messagebox.showerror("Ошибка", "Количество должно быть числом")
                
                ttk.Button(form_frame, text="Добавить", 
                        command=add_resource).grid(row=3, column=0, columnspan=2, pady=10)
            
            def remove_resource_from_template():
                selection = resources_tree.selection()
                if selection:
                    resources_tree.delete(selection)
            
            ttk.Button(resource_buttons, text="Добавить ресурс", 
                    command=add_resource_to_template).pack(side=tk.LEFT, padx=5)
            ttk.Button(resource_buttons, text="Удалить ресурс", 
                    command=remove_resource_from_template).pack(side=tk.LEFT, padx=5)
            
            # Секция для зависимостей
            dependencies_frame = ttk.LabelFrame(main_frame, text="Зависимости от других этапов (опционально)", padding=10)
            dependencies_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
            
            ttk.Label(dependencies_frame, text="ID этапов-зависимостей (через запятую):").pack(anchor=tk.W, pady=5)
            dependencies_entry = ttk.Entry(dependencies_frame, width=60)
            dependencies_entry.insert(0, ", ".join(template.get('dependencies', [])))
            dependencies_entry.pack(fill=tk.X, pady=5)
            
            def update_template():
                """Обновление шаблона"""
                name = name_entry.get().strip()
                description = description_text.get("1.0", tk.END).strip()
                duration_str = duration_entry.get().strip()
                dependencies_str = dependencies_entry.get().strip()
                
                if not name or not description:
                    messagebox.showerror("Ошибка", "Заполните название и описание шаблона")
                    return
                
                try:
                    duration = int(duration_str) if duration_str else 0
                except ValueError:
                    messagebox.showerror("Ошибка", "Длительность должна быть числом")
                    return
                
                # Собираем ресурсы из таблицы
                required_resources = []
                for item in resources_tree.get_children():
                    values = resources_tree.item(item, 'values')
                    required_resources.append({
                        'name': values[0],
                        'quantity': int(values[1]),
                        'unit': values[2]
                    })
                
                # Обрабатываем зависимости
                dependencies = []
                if dependencies_str:
                    dependencies = [dep.strip() for dep in dependencies_str.split(',') if dep.strip()]
                
                try:
                    self.system.update_stage_template(
                        template_id,
                        name=name,
                        description=description,
                        typical_duration_days=duration,
                        required_resources=required_resources,
                        dependencies=dependencies
                    )
                    messagebox.showinfo("Успех", "Шаблон успешно обновлен!")
                    dialog.destroy()
                    # Обновляем список шаблонов
                    self.show_stage_templates_management()
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))
            
            def delete_template():
                """Удаление шаблона"""
                if messagebox.askyesno("Подтверждение", 
                                    f"Вы уверены, что хотите удалить шаблон '{template['name']}'?"):
                    try:
                        self.system.delete_stage_template(template_id)
                        messagebox.showinfo("Успех", "Шаблон удален!")
                        dialog.destroy()
                        self.show_stage_templates_management()
                    except Exception as e:
                        messagebox.showerror("Ошибка", str(e))
            
            # Кнопки сохранения/отмены/удаления
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
            
            ttk.Button(buttons_frame, text="Сохранить изменения", 
                    command=update_template).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Удалить шаблон", 
                    command=delete_template, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Отмена", 
                    command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить шаблон: {str(e)}")


    def create_quick_assign_tab(self, parent):
        """Вкладка быстрого назначения этапов"""
        applications = self.system.get_my_applications()
        
        if not applications:
            ttk.Label(parent, text="Нет доступных заявок").pack(pady=50)
            return
        
        # Получаем список исполнителей
        try:
            executors = self.system.get_executors()
        except:
            executors = []
        
        if not executors:
            ttk.Label(parent, text="Нет доступных исполнителей").pack(pady=50)
            return
        
        # Список заявок
        ttk.Label(parent, text="Выберите заявку:").pack(anchor=tk.W, pady=5)
        
        app_options = []
        for app_id, application in applications.items():
            if application.get('status') in ['Новая', 'В работе']:
                contract = application.get('contract_number', 'Без договора')
                description_preview = application.get('description', '')[:30] + "..." if len(application.get('description', '')) > 30 else application.get('description', '')
                display_text = f"{contract} - {description_preview}"
                app_options.append((display_text, app_id))
        
        app_var = tk.StringVar()
        app_combobox = ttk.Combobox(parent, textvariable=app_var, 
                                values=[opt[0] for opt in app_options], state="readonly")
        app_combobox.pack(fill=tk.X, pady=5)
        
        if app_options:
            app_combobox.current(0)
        
        # Форма добавления этапа
        form_frame = ttk.LabelFrame(parent, text="Добавить этап", padding=10)
        form_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_frame, text="Описание этапа:").grid(row=0, column=0, sticky=tk.W, pady=5)
        stage_name_entry = ttk.Entry(form_frame, width=30)
        stage_name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Исполнитель:").grid(row=1, column=0, sticky=tk.W, pady=5)
        executor_var = tk.StringVar()
        executor_combobox = ttk.Combobox(form_frame, textvariable=executor_var, 
                                        values=executors, state="readonly", width=27)
        executor_combobox.grid(row=1, column=1, pady=5, padx=5)
        
        if executors:
            executor_combobox.current(0)
        
        def add_stage():
            selected_app_index = app_combobox.current()
            if selected_app_index < 0:
                messagebox.showerror("Ошибка", "Выберите заявку")
                return
                
            app_id = app_options[selected_app_index][1]
            stage_description = stage_name_entry.get()
            executor = executor_var.get()
            
            if not stage_description or not executor:
                messagebox.showerror("Ошибка", "Заполните описание этапа и выберите исполнителя")
                return
                
            try:
                stage_id = self.system.assign_stage(app_id, stage_description, executor)
                messagebox.showinfo("Успех", f"Этап создан: {stage_id}")
                stage_name_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                
        ttk.Button(form_frame, text="Добавить этап", 
                command=add_stage).grid(row=2, column=0, columnspan=2, pady=10)

    def show_stock_receipts_list(self):
        """Просмотр списка всех приходных накладных"""
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Приходные накладные", 
                style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        # Кнопка создания новой накладной
        if self.current_user['role'] in ['storeman', 'admin']:
            ttk.Button(header_frame, text="Создать накладную", 
                    command=self.show_stock_receipt).pack(side=tk.RIGHT)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        try:
            receipts = self.system.get_stock_receipts()
            
            if not receipts:
                ttk.Label(main_frame, text="Накладные не найдены").pack(pady=50)
                return
                
            # Таблица накладных
            tree_frame = ttk.Frame(main_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ("ID", "Дата", "Поставщик", "Документ", "Позиций", "Общее кол-во", "Создал")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
                
            tree.column("ID", width=150)
            tree.column("Дата", width=120)
            tree.column("Поставщик", width=150)
            tree.column("Документ", width=120)
            
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            for receipt_id, receipt in receipts.items():
                tree.insert("", tk.END, values=(
                    receipt_id,
                    receipt['date'][:10],
                    receipt.get('supplier', ''),
                    receipt.get('document_number', ''),
                    receipt['total_items'],
                    receipt['total_quantity'],
                    receipt.get('created_by', '')
                ), tags=(receipt_id,))
                
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def on_item_double_click(event):
                item = tree.selection()[0]
                receipt_id = tree.item(item, "tags")[0]
                self.show_stock_receipt_details(receipt_id)
                
            tree.bind("<Double-1>", on_item_double_click)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить накладные: {str(e)}")

    def show_stock_receipt_details(self, receipt_id):
        """Просмотр деталей накладной"""
        receipt = self.system.get_stock_receipt(receipt_id)
        
        if not receipt:
            messagebox.showerror("Ошибка", "Накладная не найдена")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Накладная {receipt_id}")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(main_frame, text=f"Приходная накладная {receipt_id}", 
                style="Title.TLabel").pack(pady=10)
        
        # Информация о накладной
        info_frame = ttk.LabelFrame(main_frame, text="Информация о накладной", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"Дата создания: {receipt['date']}").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Создал: {receipt.get('created_by', '')}").grid(row=0, column=1, sticky=tk.W, pady=2, padx=20)
        ttk.Label(info_frame, text=f"Поставщик: {receipt.get('supplier', '')}").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Номер документа: {receipt.get('document_number', '')}").grid(row=1, column=1, sticky=tk.W, pady=2, padx=20)
        ttk.Label(info_frame, text=f"Количество позиций: {receipt['total_items']}").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Общее количество: {receipt['total_quantity']}").grid(row=2, column=1, sticky=tk.W, pady=2, padx=20)
        
        # Таблица ресурсов
        ttk.Label(main_frame, text="Ресурсы:", style="Header.TLabel").pack(anchor=tk.W, pady=10)
        
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("Ресурс", "Количество", "Единица", "Тип")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            
        tree.column("Ресурс", width=200)
        tree.column("Тип", width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        for resource in receipt['resources']:
            tree.insert("", tk.END, values=(
                resource['name'],
                resource['quantity'],
                resource.get('unit', 'шт'),
                resource.get('resource_type', 'consumable')
            ))
            
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка закрытия
        ttk.Button(main_frame, text="Закрыть", 
                command=dialog.destroy).pack(pady=10)

    def setup_styles(self):
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        
        # Добавляем стиль для опасных кнопок (удаление)
        style.configure("Danger.TButton", foreground="white", background="#d9534f")
        style.map("Danger.TButton",
                 background=[('active', '#c9302c'), ('pressed', '#ac2925')])
        
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Система управления заявками", 
                 style="Title.TLabel").pack(pady=20)
        
        login_frame = ttk.Frame(main_frame)
        login_frame.pack(pady=50)
        
        ttk.Label(login_frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.login_entry = ttk.Entry(login_frame, width=20)
        self.login_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(login_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=20, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)
        
        buttons_frame = ttk.Frame(login_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Войти", 
                  command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Выход", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Тестовые данные
        test_frame = ttk.LabelFrame(main_frame, text="Тестовые учетные записи", padding=10)
        test_frame.pack(pady=20)
        
        test_accounts = [
            "admin / admin123 (Администратор)",
            "customer1 / pass123 (Заказчик)",
            "manager1 / pass123 (Руководитель)", 
            "executor1 / pass123 (Исполнитель)",
            "storeman1 / pass123 (Кладовщик)"
        ]
        
        for account in test_accounts:
            ttk.Label(test_frame, text=account).pack(anchor=tk.W)
            
        self.login_entry.focus()
        # ИСПРАВЛЕНИЕ: Привязываем Enter к методу login с правильной сигнатурой
        self.password_entry.bind('<Return>', self.login)


    def login(self, event=None):  # Добавим параметр event для обработки нажатия Enter
        username = self.login_entry.get()
        password = self.password_entry.get()
        
        try:
            if self.system.login(username, password):
                self.current_user = self.system.get_current_user()
                self.show_main_menu()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
        except PermissionError as e:
            # Создаем красивое окно для уведомления о блокировке
            self.show_blocked_user_dialog(str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def show_blocked_user_dialog(self, message):
        """Показывает диалоговое окно с уведомлением о блокировке"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Учетная запись заблокирована")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Центрируем диалоговое окно
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Стилизация
        dialog.configure(bg='#ffebee')  # Светло-красный фон
        
        # Иконка блокировки (используем эмодзи или текст)
        lock_label = ttk.Label(dialog, text="🔒", font=("Arial", 24), background='#ffebee')
        lock_label.pack(pady=10)
        
        # Сообщение
        message_label = ttk.Label(dialog, text=message, font=("Arial", 12), 
                                 background='#ffebee', wraplength=350, justify=tk.CENTER)
        message_label.pack(pady=5, padx=20)
        
        # Дополнительная информация
        info_label = ttk.Label(dialog, text="Для разблокировки обратитесь к администратору системы.", 
                              font=("Arial", 10), background='#ffebee', foreground='#666')
        info_label.pack(pady=5)
        
        # Кнопка OK
        ok_button = ttk.Button(dialog, text="OK", command=dialog.destroy, width=15)
        ok_button.pack(pady=15)
        
        # Устанавливаем фокус на кнопку OK
        ok_button.focus_set()
        
        # Привязываем нажатие Enter к закрытию диалога
        dialog.bind('<Return>', lambda e: dialog.destroy())


    def show_main_menu(self):
        self.clear_window()
        
        # Верхняя панель
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        user_info = f"{self.current_user['full_name']} ({self.current_user['role']})"
        ttk.Label(header_frame, text=user_info, style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Выйти", 
                  command=self.show_login_screen).pack(side=tk.RIGHT)
        
        # Основное меню
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(main_frame, text="Главное меню", 
                 style="Title.TLabel").pack(pady=20)
        
        # Кнопки меню в зависимости от роли
        if self.current_user['role'] == 'admin':
            self.create_admin_menu(main_frame)
        elif self.current_user['role'] == 'customer':
            self.create_customer_menu(main_frame)
        elif self.current_user['role'] == 'manager':
            self.create_manager_menu(main_frame)
        elif self.current_user['role'] == 'executor':
            self.create_executor_menu(main_frame)
        elif self.current_user['role'] == 'storeman':
            self.create_storeman_menu(main_frame)

    def create_admin_menu(self, parent):
        buttons = [
            ("Управление пользователями", self.show_user_management),
            ("Просмотр всех заявок", self.show_all_applications),
            ("Импорт из Excel", self.show_import_menu),
            ("Просмотр ресурсов", self.show_resources),
            ("Редактировать ресурс", self.show_edit_resource),
            ("Удалить ресурс", self.show_delete_resource),  # Новая кнопка
            ("Отчеты", self.show_reports_menu)
        ]

    def show_delete_resource(self):
        """Прямой доступ к удалению ресурса для администратора"""
        self.show_edit_resource()  # Используем тот же диалог, но акцентируем на удалении
        
        for text, command in buttons:
            ttk.Button(parent, text=text, command=command, 
                      width=30).pack(pady=10)
            
    def create_customer_menu(self, parent):
        buttons = [
            ("Создать заявку", self.create_application_dialog),
            ("Мои заявки", self.show_my_applications)
        ]
        
        for text, command in buttons:
            ttk.Button(parent, text=text, command=command,
                      width=30).pack(pady=10)
                  
    def create_executor_menu(self, parent):
        buttons = [
            ("Мои этапы", self.show_my_stages),
            ("Запросить ресурсы", self.show_request_resources),
            ("Завершить этап", self.show_complete_stage)
        ]
        
        for text, command in buttons:
            ttk.Button(parent, text=text, command=command,
                      width=30).pack(pady=10)
            
    def create_storeman_menu(self, parent):
        buttons = [
            ("Просмотр ресурсов", self.show_resources),
            ("Добавить ресурс", self.show_add_resource),
            ("Редактировать ресурс", self.show_edit_resource),
            ("Выделить ресурсы", self.show_allocate_resources),
            ("Приходная накладная", self.show_stock_receipt),
            ("Просмотр накладных", self.show_stock_receipts_list),  # Новая кнопка
            ("Инвентаризация", self.show_inventory),
            ("Отчет по складу", self.show_stock_report)
        ]
        
        for text, command in buttons:
            ttk.Button(parent, text=text, command=command,
                    width=30).pack(pady=10)
    
    # ===== РАЗДЕЛ ЗАЯВОК =====

    def create_application_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Создание заявки")
        dialog.geometry("500x450")  # Увеличили высоту для нового поля
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Создание новой заявки", 
                 style="Title.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Номер договора:").grid(row=0, column=0, sticky=tk.W, pady=5)
        contract_entry = ttk.Entry(form_frame, width=30)
        contract_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="ФИО заказчика:").grid(row=1, column=0, sticky=tk.W, pady=5)  # Новое поле
        customer_name_entry = ttk.Entry(form_frame, width=30)
        customer_name_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, pady=5)
        description_text = tk.Text(form_frame, width=40, height=8)
        description_text.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Адрес заказчика:").grid(row=3, column=0, sticky=tk.W, pady=5)
        address_entry = ttk.Entry(form_frame, width=30)
        address_entry.grid(row=3, column=1, pady=5, padx=5)
                
        def create_app():
            contract = contract_entry.get()
            customer_name = customer_name_entry.get()  # Новое поле
            description = description_text.get("1.0", tk.END).strip()
            address = address_entry.get()
            
            if not contract or not description or not customer_name:  # Проверяем новое поле
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
                
            try:
                app_id = self.system.create_application(contract, description, address, customer_name)
                messagebox.showinfo("Успех", f"Заявка создана!\nID: {app_id}")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Создать", command=create_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)


    def show_my_applications(self):
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                  command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Мои заявки", 
                 style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        applications = self.system.get_my_applications()
        
        if not applications:
            ttk.Label(main_frame, text="Заявки не найдены").pack(pady=50)
            return
            
        # Таблица заявок
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Дата", "Договор", "Описание", "Статус", "Этапы")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        tree.column("Описание", width=200)
        tree.column("ID", width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        for app_id, application in applications.items():
            tree.insert("", tk.END, values=(
                app_id,
                application['date'][:10],
                application['contract_number'],
                application['description'][:50] + "..." if len(application['description']) > 50 else application['description'],
                application['status'],
                len(application['stages'])
            ), tags=(app_id,))
            
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Двойной клик для просмотра деталей
        def on_item_double_click(event):
            item = tree.selection()[0]
            app_id = tree.item(item, "tags")[0]
            self.show_application_details(app_id)
            
        tree.bind("<Double-1>", on_item_double_click)

    def show_all_applications(self):
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                  command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Все заявки", 
                 style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        if self.current_user['role'] in ['manager', 'admin']:
            ttk.Button(header_frame, text="Назначить этапы", 
                      command=self.show_assign_stages).pack(side=tk.RIGHT, padx=5)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        applications = self.system.get_my_applications()
        
        if not applications:
            ttk.Label(main_frame, text="Заявки не найдены").pack(pady=50)
            return
            
        # Таблица заявок
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # ИЗМЕНЕНИЕ: Убрали столбец "Заказчик" (логин), добавили "ФИО заказчика"
        if self.current_user['role'] in ['manager', 'admin']:
            columns = ("ID", "Дата", "ФИО заказчика", "Договор", "Описание", "Адрес", "Статус", "Этапы")
        else:
            columns = ("ID", "Дата", "Договор", "Описание", "Адрес", "Статус", "Этапы")
            
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        tree.column("Описание", width=200)
        tree.column("ID", width=150)
        tree.column("Адрес", width=150)
        tree.column("ФИО заказчика", width=150)  # Новый столбец
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        for app_id, application in applications.items():
            # ИЗМЕНЕНИЕ: Используем customer_name вместо customer
            address_display = application.get('address', 'Не указан')
            if len(address_display) > 30:
                address_display = address_display[:30] + "..."
                
            customer_name_display = application.get('customer_name', 'Не указано')
            if len(customer_name_display) > 30:
                customer_name_display = customer_name_display[:30] + "..."
                
            if self.current_user['role'] in ['manager', 'admin']:
                values = (
                    app_id,
                    application['date'][:10],
                    customer_name_display,  # Используем ФИО вместо логина
                    application['contract_number'],
                    application['description'][:50] + "..." if len(application['description']) > 50 else application['description'],
                    address_display,
                    application['status'],
                    len(application['stages'])
                )
            else:
                values = (
                    app_id,
                    application['date'][:10],
                    application['contract_number'],
                    application['description'][:50] + "..." if len(application['description']) > 50 else application['description'],
                    address_display,
                    application['status'],
                    len(application['stages'])
                )
                
            tree.insert("", tk.END, values=values, tags=(app_id,))
            
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def on_item_double_click(event):
            item = tree.selection()[0]
            app_id = tree.item(item, "tags")[0]
            self.show_application_details(app_id)
            
        tree.bind("<Double-1>", on_item_double_click)

    def show_application_details(self, app_id):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Детали заявки {app_id}")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        
        application = self.system.app_manager.get_application(app_id)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Основная информация
        info_frame = ttk.LabelFrame(main_frame, text="Информация о заявке", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        # ИЗМЕНЕНИЕ: Добавлено отображение ФИО заказчика вместо логина
        ttk.Label(info_frame, text=f"ID: {application['id']}").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Дата: {application['date']}").grid(row=0, column=1, sticky=tk.W, pady=2, padx=20)
        ttk.Label(info_frame, text=f"Договор: {application['contract_number']}").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"ФИО заказчика: {application.get('customer_name', 'Не указано')}").grid(row=1, column=1, sticky=tk.W, pady=2, padx=20)
        ttk.Label(info_frame, text=f"Статус: {application['status']}").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Адрес: {application.get('address', 'Не указан')}").grid(row=2, column=1, sticky=tk.W, pady=2, padx=20)
        
        ttk.Label(info_frame, text="Описание:").grid(row=3, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(info_frame, width=80, height=4)
        desc_text.insert(tk.END, application['description'])
        desc_text.config(state=tk.DISABLED)
        desc_text.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        # Кнопки действий (для менеджера и администратора)
        if self.current_user['role'] in ['manager', 'admin'] and application['status'] == 'Новая':
            actions_frame = ttk.Frame(info_frame)
            actions_frame.grid(row=5, column=0, columnspan=2, pady=10)
            
            ttk.Button(actions_frame, text="Редактировать заявку", 
                      command=lambda: self.show_edit_application_dialog(app_id)).pack(side=tk.LEFT, padx=5)
            ttk.Button(actions_frame, text="Отменить заявку", 
                      command=lambda: self.cancel_application(app_id)).pack(side=tk.LEFT, padx=5)
        
        # Этапы
        if application['stages']:
            stages_frame = ttk.LabelFrame(main_frame, text="Этапы выполнения", padding=10)
            stages_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            columns = ("ID", "Название", "Исполнитель", "Статус", "Ресурсы", "Отчет")
            tree = ttk.Treeview(stages_frame, columns=columns, show="headings", height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                
            tree.column("Название", width=150)
            tree.column("Отчет", width=200)
            
            scrollbar = ttk.Scrollbar(stages_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            for stage_id, stage in application['stages'].items():
                resources = ", ".join([f"{r['resource']}({r['quantity']})" for r in stage['requested_resources']])
                tree.insert("", tk.END, values=(
                    stage_id,
                    stage['name'],
                    stage['executor'],
                    stage['status'],
                    resources,
                    stage['report'] or ""
                ))
                
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_edit_application_dialog(self, app_id):
        """Диалог редактирования заявки"""
        application = self.system.app_manager.get_application(app_id)
        
        if not application:
            messagebox.showerror("Ошибка", "Заявка не найдена")
            return
            
        if application['status'] != 'Новая':
            messagebox.showerror("Ошибка", "Редактирование возможно только для заявок со статусом 'Новая'")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Редактирование заявки {app_id}")
        dialog.geometry("500x450")  # Увеличили высоту для нового поля
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Редактирование заявки {app_id}", 
                 style="Title.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Номер договора:").grid(row=0, column=0, sticky=tk.W, pady=5)
        contract_entry = ttk.Entry(form_frame, width=30)
        contract_entry.insert(0, application['contract_number'])
        contract_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="ФИО заказчика:").grid(row=1, column=0, sticky=tk.W, pady=5)  # Новое поле
        customer_name_entry = ttk.Entry(form_frame, width=30)
        customer_name_entry.insert(0, application.get('customer_name', ''))
        customer_name_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, pady=5)
        description_text = tk.Text(form_frame, width=40, height=8)
        description_text.insert(tk.END, application['description'])
        description_text.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Адрес заказчика:").grid(row=3, column=0, sticky=tk.W, pady=5)
        address_entry = ttk.Entry(form_frame, width=30)
        address_entry.insert(0, application.get('address', ''))
        address_entry.grid(row=3, column=1, pady=5, padx=5)
                
        def save_changes():
            contract = contract_entry.get()
            customer_name = customer_name_entry.get()  # Новое поле
            description = description_text.get("1.0", tk.END).strip()
            address = address_entry.get()
            
            if not contract or not description or not customer_name:  # Проверяем новое поле
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
                
            try:
                self.system.update_application(app_id, contract, description, address, customer_name)
                messagebox.showinfo("Успех", "Заявка успешно обновлена!")
                dialog.destroy()
                # Обновляем отображение деталей заявки
                self.show_application_details(app_id)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)


    def cancel_application(self, app_id):
        """Отмена заявки"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите отменить эту заявку?"):
            try:
                self.system.cancel_application(app_id)
                messagebox.showinfo("Успех", "Заявка успешно отменена!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def show_complete_application(self):
        """Завершение заявки"""
        applications = self.system.get_my_applications()
        
        if not applications:
            messagebox.showinfo("Информация", "Нет доступных заявок")
            return
            
        # Создаем диалог выбора заявки для завершения
        dialog = tk.Toplevel(self.root)
        dialog.title("Завершение заявки")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Завершение заявки", 
                 style="Title.TLabel").pack(pady=10)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Выберите заявку для завершения:").pack(anchor=tk.W, pady=5)
        
        # Список заявок, которые можно завершить (не отмененные и не завершенные)
        available_apps = []
        for app_id, app in applications.items():
            if app['status'] in ['Новая', 'В работе']:
                available_apps.append((f"{app_id} - {app['contract_number']} ({app['status']})", app_id))
        
        if not available_apps:
            ttk.Label(main_frame, text="Нет заявок для завершения").pack(pady=20)
            ttk.Button(main_frame, text="Закрыть", command=dialog.destroy).pack(pady=10)
            return
            
        app_var = tk.StringVar()
        app_combobox = ttk.Combobox(main_frame, textvariable=app_var, 
                                   values=[opt[0] for opt in available_apps], state="readonly")
        app_combobox.pack(fill=tk.X, pady=5)
        app_combobox.current(0)
        
        def complete_app():
            selected_index = app_combobox.current()
            if selected_index < 0:
                messagebox.showerror("Ошибка", "Выберите заявку")
                return
                
            selected_app_id = available_apps[selected_index][1]
            
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите завершить эту заявку?"):
                try:
                    self.system.complete_application(selected_app_id)
                    messagebox.showinfo("Успех", "Заявка успешно завершена!")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Завершить заявку", 
                  command=complete_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def show_edit_application(self):
        """Просмотр и редактирование заявок"""
        applications = self.system.get_my_applications()
        
        if not applications:
            messagebox.showinfo("Информация", "Нет доступных заявок")
            return
            
        # Создаем диалог выбора заявки для редактирования
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование заявки")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Редактирование заявки", 
                 style="Title.TLabel").pack(pady=10)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Выберите заявку для редактирования:").pack(anchor=tk.W, pady=5)
        
        # Список заявок со статусом "Новая"
        new_apps = []
        for app_id, app in applications.items():
            if app['status'] == 'Новая':
                new_apps.append((f"{app_id} - {app['contract_number']}", app_id))
        
        if not new_apps:
            ttk.Label(main_frame, text="Нет заявок со статусом 'Новая' для редактирования").pack(pady=20)
            ttk.Button(main_frame, text="Закрыть", command=dialog.destroy).pack(pady=10)
            return
            
        app_var = tk.StringVar()
        app_combobox = ttk.Combobox(main_frame, textvariable=app_var, 
                                   values=[opt[0] for opt in new_apps], state="readonly")
        app_combobox.pack(fill=tk.X, pady=5)
        app_combobox.current(0)
        
        def edit_app():
            selected_index = app_combobox.current()
            if selected_index < 0:
                messagebox.showerror("Ошибка", "Выберите заявку")
                return
                
            selected_app_id = new_apps[selected_index][1]
            dialog.destroy()
            self.show_edit_application_dialog(selected_app_id)
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Редактировать", 
                  command=edit_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    # ===== РАЗДЕЛ ЭТАПОВ =====

    def show_assign_stages(self):
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Назначение этапов", 
                style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        applications = self.system.get_my_applications()
        
        if not applications:
            ttk.Label(main_frame, text="Нет доступных заявок").pack(pady=50)
            return
        
        # Получаем список исполнителей с отладочной информацией
        try:
            # Используем новый метод get_executors
            executors = self.system.get_executors()
            print(f"Отладка: Найдено исполнителей: {executors}")  # Отладочная информация
    
        except Exception as e:
            print(f"Отладка: Ошибка при получении исполнителей: {e}")  # Отладочная информация
            messagebox.showerror("Ошибка", f"Не удалось загрузить список исполнителей: {str(e)}")
            executors = []
        
        if not executors:
            # Более информативное сообщение
            error_frame = ttk.Frame(main_frame)
            error_frame.pack(pady=50)
            
            ttk.Label(error_frame, text="Нет доступных исполнителей", 
                    style="Header.TLabel").pack(pady=10)
            ttk.Label(error_frame, text="Возможные причины:", 
                    font=("Arial", 10)).pack(pady=5)
            ttk.Label(error_frame, text="• Нет пользователей с ролью 'executor'", 
                    font=("Arial", 9)).pack()
            ttk.Label(error_frame, text="• Все исполнители заблокированы", 
                    font=("Arial", 9)).pack()
            ttk.Label(error_frame, text="• Ошибка доступа к данным пользователей", 
                    font=("Arial", 9)).pack()
            
            if self.current_user['role'] == 'admin':
                ttk.Button(error_frame, text="Управление пользователями", 
                        command=self.show_user_management).pack(pady=10)
            return
        
        # Список заявок - теперь по номеру договора
        ttk.Label(main_frame, text="Выберите заявку:").pack(anchor=tk.W, pady=5)
        
        # Создаем список для combobox: "Договор - ID - Описание"
        app_options = []
        for app_id, application in applications.items():
            if application.get('status') in ['Новая', 'В работе']:
                contract = application.get('contract_number', 'Без договора')
                description_preview = application.get('description', '')[:30] + "..." if len(application.get('description', '')) > 30 else application.get('description', '')
                display_text = f"{contract} - {description_preview}"
                app_options.append((display_text, app_id))
        
        if not app_options:
            ttk.Label(main_frame, text="Нет заявок для назначения этапов").pack(pady=50)
            return
        
        app_var = tk.StringVar()
        app_combobox = ttk.Combobox(main_frame, textvariable=app_var, 
                                values=[opt[0] for opt in app_options], state="readonly")
        app_combobox.pack(fill=tk.X, pady=5)
        app_combobox.current(0)
        
        # Форма добавления этапа
        form_frame = ttk.LabelFrame(main_frame, text="Добавить этап", padding=10)
        form_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_frame, text="Описание этапа:").grid(row=0, column=0, sticky=tk.W, pady=5)
        stage_name_entry = ttk.Entry(form_frame, width=30)
        stage_name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Исполнитель:").grid(row=1, column=0, sticky=tk.W, pady=5)
        executor_var = tk.StringVar()
        executor_combobox = ttk.Combobox(form_frame, textvariable=executor_var, 
                                        values=executors, state="readonly", width=27)
        executor_combobox.grid(row=1, column=1, pady=5, padx=5)
        executor_combobox.current(0)
        
        def add_stage():
            selected_app_index = app_combobox.current()
            if selected_app_index < 0:
                messagebox.showerror("Ошибка", "Выберите заявку")
                return
                
            app_id = app_options[selected_app_index][1]
            stage_description = stage_name_entry.get()
            executor = executor_var.get()
            
            if not stage_description or not executor:
                messagebox.showerror("Ошибка", "Заполните описание этапа и выберите исполнителя")
                return
                
            try:
                stage_id = self.system.assign_stage(app_id, stage_description, executor)
                messagebox.showinfo("Успех", f"Этап создан: {stage_id}")
                stage_name_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                
        ttk.Button(form_frame, text="Добавить этап", 
                command=add_stage).grid(row=2, column=0, columnspan=2, pady=10)

    def show_my_stages(self):
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                  command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Мои этапы", 
                 style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        stages = self.system.get_my_stages()
        
        if not stages:
            ttk.Label(main_frame, text="Этапы не найдены").pack(pady=50)
            return
            
        # Таблица этапов
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Заявка", "Этап", "Название", "Статус", "Ресурсы", "Отчет")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            
        tree.column("Название", width=150)
        tree.column("Отчет", width=200)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        for app_id, app_stages in stages.items():
            application = self.system.app_manager.get_application(app_id)
            # ИСПРАВЛЕНИЕ: используем словарный доступ к данным заявки
            print(f"Заявка: {app_id}")
            print(f"Договор: {application['contract_number']}")
            print(f"Описание: {application['description']}")
            for stage_id, stage in app_stages.items():
                # ИСПРАВЛЕНИЕ: используем словарный доступ к данным этапа
                resources = ", ".join([f"{r['resource']}({r['quantity']})" for r in stage['requested_resources']])
                tree.insert("", tk.END, values=(
                    app_id,
                    stage_id,
                    stage['name'],  # Было: stage.name
                    stage['status'],  # Было: stage.status
                    resources,
                    stage['report'] or ""  # Было: stage.report
             ))
                
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_request_resources(self):
        """Диалог запроса ресурсов для исполнителя с выпадающим списком ресурсов"""
        stages = self.system.get_my_stages()
        
        if not stages:
            messagebox.showinfo("Информация", "У вас нет активных этапов для запроса ресурсов.")
            return
            
        # Собираем все этапы, которые еще не завершены
        stage_options = []
        for app_id, app_stages in stages.items():
            for stage_id, stage in app_stages.items():
                if stage['status'] != 'completed':
                    stage_options.append((f"{app_id} - {stage['name']}", app_id, stage_id))
        
        if not stage_options:
            messagebox.showinfo("Информация", "У вас нет активных этапов для запроса ресурсов.")
            return

        # Получаем список доступных ресурсов
        try:
            resources = self.system.get_resources()
            resource_names = list(resources.keys())
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список ресурсов: {str(e)}")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Запрос ресурсов")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Запрос ресурсов", 
                style="Title.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Выбор этапа
        ttk.Label(form_frame, text="Этап:").grid(row=0, column=0, sticky=tk.W, pady=5)
        stage_var = tk.StringVar()
        stage_combobox = ttk.Combobox(form_frame, textvariable=stage_var, 
                                    values=[opt[0] for opt in stage_options], state="readonly")
        stage_combobox.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W+tk.E)
        stage_combobox.current(0)
        
        # Ресурс - ЗАМЕНА: теперь выпадающий список
        ttk.Label(form_frame, text="Ресурс:").grid(row=1, column=0, sticky=tk.W, pady=5)
        resource_var = tk.StringVar()
        resource_combobox = ttk.Combobox(form_frame, textvariable=resource_var, 
                                    values=resource_names, state="readonly")
        resource_combobox.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W+tk.E)
        
        if resource_names:
            resource_combobox.current(0)
        
        # Информация о выбранном ресурсе
        resource_info_label = ttk.Label(form_frame, text="", foreground="blue")
        resource_info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        def update_resource_info(*args):
            """Обновление информации о выбранном ресурсе"""
            selected_resource = resource_var.get()
            if selected_resource and selected_resource in resources:
                resource = resources[selected_resource]
                info_text = f"Доступно: {resource['quantity']} {resource['unit']}"
                if resource.get('min_quantity', 0) > 0:
                    info_text += f" (мин. запас: {resource['min_quantity']})"
                resource_info_label.config(text=info_text)
            else:
                resource_info_label.config(text="")
        
        # Привязываем обновление информации к выбору ресурса
        resource_var.trace('w', update_resource_info)
        
        # Инициализируем информацию для текущего выбранного ресурса
        if resource_names:
            update_resource_info()
        
        # Количество
        ttk.Label(form_frame, text="Количество:").grid(row=3, column=0, sticky=tk.W, pady=5)
        quantity_entry = ttk.Entry(form_frame, width=30)
        quantity_entry.grid(row=3, column=1, pady=5, padx=5)
        
        def request_resource():
            selected_index = stage_combobox.current()
            if selected_index < 0:
                messagebox.showerror("Ошибка", "Выберите этап")
                return
                
            app_id = stage_options[selected_index][1]
            stage_id = stage_options[selected_index][2]
            resource_name = resource_var.get()
            quantity_str = quantity_entry.get()
            
            if not resource_name:
                messagebox.showerror("Ошибка", "Выберите ресурс")
                return
                
            if not quantity_str:
                messagebox.showerror("Ошибка", "Введите количество")
                return
                
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
                    return
                    
                # Проверяем доступность ресурса
                if resource_name in resources:
                    available = resources[resource_name]['quantity']
                    if quantity > available:
                        messagebox.showerror("Ошибка", 
                                        f"Недостаточно ресурсов. Доступно: {available}")
                        return
                
                self.system.request_resources(app_id, stage_id, resource_name, quantity)
                messagebox.showinfo("Успех", "Ресурс успешно запрошен")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Количество должно быть целым числом")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Запросить", 
                command=request_resource).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def show_complete_stage(self):
        stages = self.system.get_my_stages()
        
        if not stages:
            messagebox.showinfo("Информация", "У вас нет активных этапов")
            return
            
        # Диалог завершения этапа
        dialog = tk.Toplevel(self.root)
        dialog.title("Завершение этапа")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Завершение этапа", 
                 style="Title.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Выбор этапа
        ttk.Label(form_frame, text="Выберите этап:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        stage_options = []
        for app_id, app_stages in stages.items():
            for stage_id, stage in app_stages.items():
                if stage['status'] != 'completed':
                    stage_options.append((f"{app_id} - {stage['name']}", app_id, stage_id))
        
        stage_var = tk.StringVar()
        if stage_options:
            stage_combobox = ttk.Combobox(form_frame, textvariable=stage_var, 
                                         values=[opt[0] for opt in stage_options], state="readonly")
            stage_combobox.current(0)
        else:
            stage_combobox = ttk.Combobox(form_frame, textvariable=stage_var, state="readonly")
            stage_combobox['values'] = ['Нет доступных этапов']
            stage_combobox.current(0)
            
        stage_combobox.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W+tk.E)
        
        # Отчет
        ttk.Label(form_frame, text="Отчет о выполнении:").grid(row=1, column=0, sticky=tk.W, pady=5)
        report_text = tk.Text(form_frame, width=50, height=10)
        report_text.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W+tk.E)
        
        def complete_stage():
            if not stage_options:
                messagebox.showerror("Ошибка", "Нет доступных этапов")
                return
                
            selected_index = stage_combobox.current()
            if selected_index < 0:
                messagebox.showerror("Ошибка", "Выберите этап")
                return
                
            app_id = stage_options[selected_index][1]
            stage_id = stage_options[selected_index][2]
            report = report_text.get("1.0", tk.END).strip()
            
            if not report:
                messagebox.showerror("Ошибка", "Заполните отчет о выполнении")
                return
                
            try:
                self.system.complete_stage(app_id, stage_id, report)
                messagebox.showinfo("Успех", "Этап успешно завершен")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Завершить этап", 
                  command=complete_stage).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    # ===== РАЗДЕЛ РЕСУРСОВ =====

    def show_resources(self):
        self.clear_window()
        self.current_screen = 'resources'
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                  command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Ресурсы на складе", 
                 style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(buttons_frame, text="Добавить ресурс", 
                  command=self.show_add_resource).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Редактировать ресурс", 
                  command=self.show_edit_resource).pack(side=tk.LEFT, padx=5)
        
        if self.current_user['role'] == 'admin':
            ttk.Button(buttons_frame, text="Удалить ресурс", 
                      command=self.show_edit_resource, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        resources = self.system.get_resources()
        
        if not resources:
            ttk.Label(main_frame, text="Ресурсы не найдены").pack(pady=50)
            return
            
        # Таблица ресурсов с типом
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Название", "Тип", "Количество", "Единица", "Мин. запас", "Статус")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        tree.column("Название", width=200)
        tree.column("Тип", width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Получаем mapping типов для отображения
        resource_types = {rt.type.value: rt for rt in self.system.get_resource_types()}
        
        for name, resource in resources.items():
            # Определяем статус ресурса
            status = "Норма"
            if resource['quantity'] <= resource.get('min_quantity', 0):
                status = "Низкий запас"
            elif resource['quantity'] == 0:
                status = "Отсутствует"
            
            # Получаем читаемое название типа
            resource_type_value = resource.get('resource_type', 'consumable')
            type_display = resource_types[resource_type_value].name if resource_type_value in resource_types else resource_type_value
            
            tree.insert("", tk.END, values=(
                name,
                type_display,
                resource['quantity'],
                resource['unit'],
                resource.get('min_quantity', 0),
                status
            ), tags=(name,))
            
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def on_item_double_click(event):
            selection = tree.selection()
            if selection:
                item = selection[0]
                resource_name = tree.item(item, "values")[0]
                self.show_edit_resource_dialog(resource_name)
                
        tree.bind("<Double-1>", on_item_double_click)

    def show_add_resource(self):
        """Диалог добавления ресурса с выбором типа и атрибутами"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление ресурса")
        dialog.geometry("600x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Добавление нового ресурса", 
                 style="Title.TLabel").pack(pady=10)
        
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        form_frame = ttk.Frame(scrollable_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Основные поля
        ttk.Label(form_frame, text="Название ресурса*:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Количество*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        quantity_entry = ttk.Entry(form_frame, width=30)
        quantity_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Единица измерения*:").grid(row=2, column=0, sticky=tk.W, pady=5)
        unit_entry = ttk.Entry(form_frame, width=30)
        unit_entry.insert(0, "шт")
        unit_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Минимальный запас:").grid(row=3, column=0, sticky=tk.W, pady=5)
        min_quantity_entry = ttk.Entry(form_frame, width=30)
        min_quantity_entry.insert(0, "0")
        min_quantity_entry.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Тип ресурса - ДОБАВЛЯЕМ ВЫБОР ТИПА
        ttk.Label(form_frame, text="Тип ресурса*:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Получаем доступные типы ресурсов
        try:
            resource_types = self.system.get_resource_types()
            type_names = [f"{rt.type.value} - {rt.name}" for rt in resource_types]
        except Exception as e:
            print(f"Ошибка при получении типов ресурсов: {e}")
            # Если не удалось получить типы, используем значения по умолчанию
            resource_types = []
            type_names = ["consumable - Расходные материалы"]
        
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, 
                                 values=type_names, state="readonly", width=27)
        type_combo.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)
        
        if type_names:
            type_combo.current(0)  # Выбираем первый тип по умолчанию
        
        # Фрейм для атрибутов
        attributes_frame = ttk.LabelFrame(form_frame, text="Атрибуты ресурса", padding=10)
        attributes_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        # Словарь для хранения полей атрибутов
        attribute_entries = {}
        
        def update_attributes(*args):
            """Обновить поля атрибутов при изменении типа ресурса"""
            # Очищаем фрейм атрибутов
            for widget in attributes_frame.winfo_children():
                widget.destroy()
            
            attribute_entries.clear()
            
            if not type_names:
                ttk.Label(attributes_frame, text="Нет доступных типов ресурсов").pack()
                return
            
            # Получаем выбранный тип
            selected_type_str = type_var.get().split(' - ')[0]
            
            try:
                # Находим соответствующий ResourceType
                selected_resource_type = None
                for rt in resource_types:
                    if rt.type.value == selected_type_str:
                        selected_resource_type = rt.type
                        break
                
                if selected_resource_type is None:
                    selected_resource_type = ResourceType.CONSUMABLE
                
                # Получаем атрибуты для выбранного типа
                attributes = self.system.get_resource_type_attributes(selected_resource_type)
                
                if not attributes:
                    ttk.Label(attributes_frame, text="Для этого типа ресурса не определены атрибуты").pack()
                    return
                
                # Создаем поля для каждого атрибута
                for i, attr in enumerate(attributes):
                    label_text = attr['label']
                    if attr.get('required', False):
                        label_text += "*"
                    
                    ttk.Label(attributes_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
                    
                    if attr['type'] == 'text':
                        entry = ttk.Entry(attributes_frame, width=30)
                        entry.grid(row=i, column=1, pady=2, padx=5, sticky=tk.W)
                    elif attr['type'] == 'number':
                        entry = ttk.Entry(attributes_frame, width=30)
                        entry.grid(row=i, column=1, pady=2, padx=5, sticky=tk.W)
                    elif attr['type'] == 'date':
                        entry = ttk.Entry(attributes_frame, width=30)
                        entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                        entry.grid(row=i, column=1, pady=2, padx=5, sticky=tk.W)
                    
                    attribute_entries[attr['name']] = entry
                    
            except Exception as e:
                print(f"Ошибка при обновлении атрибутов: {e}")
                ttk.Label(attributes_frame, text="Ошибка при загрузке атрибутов").pack()
        
        # Привязываем обновление атрибутов к изменению типа
        type_var.trace('w', update_attributes)
        
        # Инициализируем атрибуты для текущего типа
        if type_names:
            update_attributes()
        
        def add_resource():
            try:
                name = name_entry.get().strip()
                quantity_str = quantity_entry.get().strip()
                unit = unit_entry.get().strip()
                min_quantity_str = min_quantity_entry.get().strip() or "0"
                
                # Проверяем обязательные поля
                if not name or not quantity_str or not unit:
                    messagebox.showerror("Ошибка", "Заполните обязательные поля (помеченные *)")
                    return
                
                # Проверяем числовые значения
                try:
                    quantity = int(quantity_str)
                    min_quantity = int(min_quantity_str)
                except ValueError:
                    messagebox.showerror("Ошибка", "Количество и минимальный запас должны быть числами")
                    return
                
                if quantity < 0 or min_quantity < 0:
                    messagebox.showerror("Ошибка", "Количество и минимальный запас не могут быть отрицательными")
                    return
                
                # Получаем выбранный тип
                if not type_names:
                    messagebox.showerror("Ошибка", "Не удалось определить тип ресурса")
                    return
                
                selected_type_str = type_var.get().split(' - ')[0]
                
                # Находим соответствующий ResourceType
                selected_resource_type = None
                for rt in resource_types:
                    if rt.type.value == selected_type_str:
                        selected_resource_type = rt.type
                        break
                
                if selected_resource_type is None:
                    selected_resource_type = ResourceType.CONSUMABLE
                
                # Собираем атрибуты
                attributes = {}
                for attr_name, entry_widget in attribute_entries.items():
                    value = entry_widget.get().strip()
                    if value:
                        attributes[attr_name] = value
                
                # Проверяем обязательные атрибуты
                required_attrs = [attr['name'] for attr in self.system.get_resource_type_attributes(selected_resource_type) 
                                if attr.get('required', False)]
                
                for req_attr in required_attrs:
                    if req_attr not in attributes or not attributes[req_attr]:
                        messagebox.showerror("Ошибка", f"Заполните обязательный атрибут: {req_attr}")
                        return
                
                # Добавляем ресурс
                self.system.add_resource(name, quantity, unit, min_quantity, selected_resource_type, attributes)
                messagebox.showinfo("Успех", f"Ресурс '{name}' успешно добавлен")
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("Ошибка", f"Ошибка в числовых полях: {e}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        # Кнопки
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Добавить ресурс", 
                  command=add_resource).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Настройка прокрутки
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Обновляем прокрутку
        dialog.update()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Устанавливаем фокус на поле названия
        name_entry.focus()

    def show_allocate_resources(self):
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                  command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Выделение ресурсов", 
                 style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        try:
            pending_requests = self.system.get_pending_resource_requests()
        except:
            pending_requests = []
        
        if not pending_requests:
            ttk.Label(main_frame, text="Нет запросов на ресурсы").pack(pady=50)
            return
            
        # Таблица запросов
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Заявка", "Этап", "Исполнитель", "Ресурс", "Количество")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        tree.column("Заявка", width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        for request in pending_requests:
            tree.insert("", tk.END, values=(
                request['app_id'],
                request['stage_name'],
                request['executor'],
                request['resource'],
                request['quantity']  # Уже правильно - словарный доступ
            ))
            
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def allocate_selected():
            selection = tree.selection()
            if not selection:
                messagebox.showinfo("Информация", "Выберите запрос для выделения")
                return
                
            item = selection[0]
            app_id, stage_id, resource = tree.item(item, "tags")
            
            try:
                self.system.allocate_resources(app_id, stage_id, resource)
                messagebox.showinfo("Успех", "Ресурсы успешно выделены")
                # Обновляем список
                self.show_allocate_resources()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                
        ttk.Button(main_frame, text="Выделить выбранные ресурсы", 
                  command=allocate_selected).pack(pady=10)

    # ===== АДМИНИСТРАТИВНЫЕ ФУНКЦИИ =====
    # Замените метод show_user_management на этот:

    def show_user_management(self):
        """Управление пользователями - полный интерфейс"""
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Управление пользователями", 
                style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(buttons_frame, text="Добавить пользователя", 
                command=self.show_add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Обновить список", 
                command=self.show_user_management).pack(side=tk.LEFT, padx=5)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        try:
            users = self.system.get_all_users()
            
            if not users:
                ttk.Label(main_frame, text="Пользователи не найдены").pack(pady=50)
                return
                
            # Таблица пользователей
            tree_frame = ttk.Frame(main_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ("Логин", "ФИО", "Роль", "Отдел", "Статус")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
                
            tree.column("ФИО", width=200)
            tree.column("Отдел", width=150)
            
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            for username, user_data in users.items():
                tree.insert("", tk.END, values=(
                    username,
                    user_data['full_name'],
                    user_data['role'],
                    user_data.get('department', ''),
                    user_data.get('status', 'active')
                ), tags=(username,))
                
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Кнопки действий с выбранным пользователем
            actions_frame = ttk.Frame(main_frame)
            actions_frame.pack(fill=tk.X, pady=10)
            
            def edit_selected():
                selection = tree.selection()
                if not selection:
                    messagebox.showinfo("Информация", "Выберите пользователя для редактирования")
                    return
                    
                username = tree.item(selection[0], "tags")[0]
                self.show_edit_user(username)
                
            def delete_selected():
                selection = tree.selection()
                if not selection:
                    messagebox.showinfo("Информация", "Выберите пользователя для удаления")
                    return
                    
                username = tree.item(selection[0], "tags")[0]
                
                # Нельзя удалить самого себя
                if username == self.current_user['username']:
                    messagebox.showerror("Ошибка", "Нельзя удалить свою собственную учетную запись")
                    return
                    
                if messagebox.askyesno("Подтверждение", 
                                    f"Вы уверены, что хотите удалить пользователя {username}?"):
                    try:
                        self.system.delete_user(username)
                        messagebox.showinfo("Успех", f"Пользователь {username} удален")
                        self.show_user_management()  # Обновляем список
                    except Exception as e:
                        messagebox.showerror("Ошибка", str(e))
            
            ttk.Button(actions_frame, text="Редактировать", 
                    command=edit_selected).pack(side=tk.LEFT, padx=5)
            ttk.Button(actions_frame, text="Удалить", 
                    command=delete_selected).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список пользователей: {str(e)}")

    def show_edit_user(self, username):
        """Диалог редактирования пользователя"""
        try:
            users = self.system.get_all_users()
            user_data = users.get(username)
            
            if not user_data:
                messagebox.showerror("Ошибка", "Пользователь не найден")
                return
                
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Редактирование пользователя: {username}")
            dialog.geometry("500x350")
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text=f"Редактирование: {username}", 
                    style="Title.TLabel").pack(pady=10)
            
            form_frame = ttk.Frame(dialog, padding=20)
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            # Поля формы
            ttk.Label(form_frame, text="ФИО*:").grid(row=0, column=0, sticky=tk.W, pady=5)
            fullname_entry = ttk.Entry(form_frame, width=30)
            fullname_entry.insert(0, user_data['full_name'])
            fullname_entry.grid(row=0, column=1, pady=5, padx=5)
            
            ttk.Label(form_frame, text="Роль*:").grid(row=1, column=0, sticky=tk.W, pady=5)
            role_var = tk.StringVar(value=user_data['role'])
            role_combobox = ttk.Combobox(form_frame, textvariable=role_var, 
                                        values=["customer", "manager", "executor", "storeman", "admin"],
                                        state="readonly")
            role_combobox.grid(row=1, column=1, pady=5, padx=5)
            
            ttk.Label(form_frame, text="Отдел:").grid(row=2, column=0, sticky=tk.W, pady=5)
            department_entry = ttk.Entry(form_frame, width=30)
            department_entry.insert(0, user_data.get('department', ''))
            department_entry.grid(row=2, column=1, pady=5, padx=5)
            
            ttk.Label(form_frame, text="Статус:").grid(row=3, column=0, sticky=tk.W, pady=5)
            status_var = tk.StringVar(value=user_data.get('status', 'active'))
            status_combobox = ttk.Combobox(form_frame, textvariable=status_var, 
                                        values=["active", "blocked"],
                                        state="readonly")
            status_combobox.grid(row=3, column=1, pady=5, padx=5)
            
            def save_changes():
                new_full_name = fullname_entry.get().strip()
                new_role = role_var.get()
                new_department = department_entry.get().strip()
                new_status = status_var.get()
                
                if not new_full_name or not new_role:
                    messagebox.showerror("Ошибка", "Заполните обязательные поля (ФИО и Роль)")
                    return
                    
                try:
                    # Обновляем данные пользователя
                    self.system.update_user(
                        username,
                        full_name=new_full_name,
                        role=new_role,
                        department=new_department,
                        status=new_status
                    )
                    messagebox.showinfo("Успех", "Данные пользователя обновлены")
                    dialog.destroy()
                    self.show_user_management()  # Обновляем список
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))
                    
            def reset_password():
                """Диалог сброса пароля"""
                password_dialog = tk.Toplevel(dialog)
                password_dialog.title("Сброс пароля")
                password_dialog.geometry("400x200")
                password_dialog.transient(dialog)
                password_dialog.grab_set()
                
                ttk.Label(password_dialog, text=f"Сброс пароля для: {username}", 
                        style="Header.TLabel").pack(pady=10)
                
                password_frame = ttk.Frame(password_dialog, padding=20)
                password_frame.pack(fill=tk.BOTH, expand=True)
                
                ttk.Label(password_frame, text="Новый пароль*:").grid(row=0, column=0, sticky=tk.W, pady=5)
                new_password_entry = ttk.Entry(password_frame, width=25, show="*")
                new_password_entry.grid(row=0, column=1, pady=5, padx=5)
                
                ttk.Label(password_frame, text="Подтверждение*:").grid(row=1, column=0, sticky=tk.W, pady=5)
                confirm_password_entry = ttk.Entry(password_frame, width=25, show="*")
                confirm_password_entry.grid(row=1, column=1, pady=5, padx=5)
                
                def do_reset_password():
                    new_password = new_password_entry.get()
                    confirm_password = confirm_password_entry.get()
                    
                    if not new_password or not confirm_password:
                        messagebox.showerror("Ошибка", "Заполните оба поля пароля")
                        return
                        
                    if new_password != confirm_password:
                        messagebox.showerror("Ошибка", "Пароли не совпадают")
                        return
                        
                    if len(new_password) < 4:
                        messagebox.showerror("Ошибка", "Пароль должен содержать минимум 4 символа")
                        return
                        
                    try:
                        # Для сброса пароля нам нужно перерегистрировать пользователя
                        # В реальной системе должен быть отдельный метод для сброса пароля
                        self.system.auth.register_user(
                            username, 
                            new_password, 
                            user_data['role'], 
                            user_data['full_name'], 
                            user_data.get('department', '')
                        )
                        messagebox.showinfo("Успех", "Пароль успешно изменен")
                        password_dialog.destroy()
                    except Exception as e:
                        messagebox.showerror("Ошибка", str(e))
                        
                ttk.Button(password_frame, text="Сбросить пароль", 
                        command=do_reset_password).grid(row=2, column=0, columnspan=2, pady=10)
                
                new_password_entry.focus()
            
            buttons_frame = ttk.Frame(form_frame)
            buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)
            
            ttk.Button(buttons_frame, text="Сохранить", 
                    command=save_changes).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Сбросить пароль", 
                    command=reset_password).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Отмена", 
                    command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные пользователя: {str(e)}")

    def show_add_user(self):
        """Диалог добавления пользователя"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление пользователя")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Добавление пользователя", 
                style="Title.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поля формы
        fields = []
        
        ttk.Label(form_frame, text="Логин*:").grid(row=0, column=0, sticky=tk.W, pady=5)
        login_entry = ttk.Entry(form_frame, width=30)
        login_entry.grid(row=0, column=1, pady=5, padx=5)
        fields.append(('login', login_entry))
        
        ttk.Label(form_frame, text="Пароль*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(form_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, pady=5, padx=5)
        fields.append(('password', password_entry))
        
        ttk.Label(form_frame, text="Подтверждение пароля*:").grid(row=2, column=0, sticky=tk.W, pady=5)
        confirm_password_entry = ttk.Entry(form_frame, width=30, show="*")
        confirm_password_entry.grid(row=2, column=1, pady=5, padx=5)
        fields.append(('confirm_password', confirm_password_entry))
        
        ttk.Label(form_frame, text="ФИО*:").grid(row=3, column=0, sticky=tk.W, pady=5)
        fullname_entry = ttk.Entry(form_frame, width=30)
        fullname_entry.grid(row=3, column=1, pady=5, padx=5)
        fields.append(('full_name', fullname_entry))
        
        ttk.Label(form_frame, text="Роль*:").grid(row=4, column=0, sticky=tk.W, pady=5)
        role_var = tk.StringVar()
        role_combobox = ttk.Combobox(form_frame, textvariable=role_var, 
                                    values=["customer", "manager", "executor", "storeman", "admin"],
                                    state="readonly")
        role_combobox.grid(row=4, column=1, pady=5, padx=5)
        role_combobox.current(0)
        fields.append(('role', role_combobox))
        
        ttk.Label(form_frame, text="Отдел:").grid(row=5, column=0, sticky=tk.W, pady=5)
        department_entry = ttk.Entry(form_frame, width=30)
        department_entry.grid(row=5, column=1, pady=5, padx=5)
        fields.append(('department', department_entry))
        
        def add_user():
            # Собираем данные
            data = {}
            for field_name, widget in fields:
                if field_name == 'role':
                    data[field_name] = widget.get()
                else:
                    data[field_name] = widget.get().strip()
            
            # Валидация
            if not all([data['login'], data['password'], data['full_name'], data['role']]):
                messagebox.showerror("Ошибка", "Заполните обязательные поля (помечены *)")
                return
                
            if data['password'] != data['confirm_password']:
                messagebox.showerror("Ошибка", "Пароли не совпадают")
                return
                
            if len(data['password']) < 4:
                messagebox.showerror("Ошибка", "Пароль должен содержать минимум 4 символа")
                return
                
            try:
                self.system.register_user(
                    data['login'], 
                    data['password'], 
                    data['role'], 
                    data['full_name'], 
                    data.get('department', '')
                )
                messagebox.showinfo("Успех", "Пользователь успешно добавлен")
                dialog.destroy()
                # Обновляем список пользователей, если мы в режиме управления
                if hasattr(self, 'show_user_management'):
                    self.show_user_management()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Добавить", 
                command=add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Устанавливаем фокус на первое поле
        login_entry.focus()

    def show_import_menu(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Импорт данных")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Импорт данных из Excel", 
                 style="Title.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(form_frame, text="Импорт пользователей", 
                  command=lambda: self.import_data('users'),
                  width=30).pack(pady=10)
        ttk.Button(form_frame, text="Импорт ресурсов", 
                  command=lambda: self.import_data('resources'),
                  width=30).pack(pady=10)
                  
        ttk.Button(form_frame, text="Закрыть", 
                  command=dialog.destroy).pack(pady=10)
        
    def import_data(self, data_type):
        # В реальной реализации здесь будет диалог выбора файла
        messagebox.showinfo("Информация", f"Функционал импорта {data_type} в разработке")
        
    def run(self):
        # Инициализация тестовых данных
        self.initialize_test_data()
        self.root.mainloop()
        
    def initialize_test_data(self):
        """Инициализация тестовых данных при первом запуске"""
        try:
            # Создаем администратора если его нет
            self.system.auth.register_user("admin", "admin123", "admin", "Администратор Системы")
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
                except:
                    pass  # Пользователь уже существует
            
            # Добавляем тестовые ресурсы
            try:
                self.system.add_resource("Ноутбук", 10, "шт", 2)
                self.system.add_resource("Монитор", 15, "шт", 3)
                self.system.add_resource("Клавиатура", 20, "шт", 5)
            except:
                pass
            
        except Exception as e:
            print(f"Ошибка инициализации: {e}")
  
    def create_admin_menu(self, parent):
        buttons = [
            ("Управление пользователями", self.show_user_management),
            ("Просмотр всех заявок", self.show_all_applications),
            ("Импорт из Excel", self.show_import_menu),
            ("Просмотр ресурсов", self.show_resources),
            ("Редактировать ресурс", self.show_edit_resource),  # Новая кнопка для админа
            ("Отчеты", self.show_reports_menu)
        ]
        
        for text, command in buttons:
            ttk.Button(parent, text=text, command=command, 
                      width=30).pack(pady=10)

    def show_edit_resource(self):
        """Выбор ресурса для редактирования"""
        resources = self.system.get_resources()
        
        if not resources:
            messagebox.showinfo("Информация", "Нет доступных ресурсов для редактирования")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование ресурса")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Выберите ресурс для редактирования", 
                 style="Title.TLabel").pack(pady=10)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Ресурс:").pack(anchor=tk.W, pady=5)
        
        # Список ресурсов
        resource_names = list(resources.keys())
        resource_var = tk.StringVar()
        resource_combo = ttk.Combobox(main_frame, textvariable=resource_var, 
                                     values=resource_names, state="readonly", width=40)
        resource_combo.pack(fill=tk.X, pady=5)
        resource_combo.current(0)
        
        def edit_selected():
            selected_resource = resource_var.get()
            if not selected_resource:
                messagebox.showerror("Ошибка", "Выберите ресурс")
                return
            
            dialog.destroy()
            self.show_edit_resource_dialog(selected_resource)
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Редактировать", 
                  command=edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def show_edit_resource_dialog(self, resource_name):
        """Диалог редактирования ресурса с типами и атрибутами"""
        resource = self.system.get_resource(resource_name)
        
        if not resource:
            messagebox.showerror("Ошибка", "Ресурс не найден")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Редактирование ресурса: {resource_name}")
        dialog.geometry("600x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Редактирование: {resource_name}", 
                 style="Title.TLabel").pack(pady=10)
        
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        form_frame = ttk.Frame(scrollable_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Проверяем, используется ли ресурс
        is_used = self.system.is_resource_used(resource_name)
        
        if is_used:
            warning_frame = ttk.Frame(form_frame)
            warning_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
            
            warning_label = ttk.Label(warning_frame, 
                                    text="⚠️ Этот ресурс используется в заявках",
                                    foreground="orange", font=("Arial", 10, "bold"))
            warning_label.pack(anchor=tk.W)
        
        # Основные поля
        ttk.Label(form_frame, text="Название:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_label = ttk.Label(form_frame, text=resource_name, font=("Arial", 10, "bold"))
        name_label.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Количество:").grid(row=2, column=0, sticky=tk.W, pady=5)
        quantity_var = tk.StringVar(value=str(resource['quantity']))
        quantity_entry = ttk.Entry(form_frame, textvariable=quantity_var, width=30)
        quantity_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Единица измерения:").grid(row=3, column=0, sticky=tk.W, pady=5)
        unit_var = tk.StringVar(value=resource['unit'])
        unit_entry = ttk.Entry(form_frame, textvariable=unit_var, width=30)
        unit_entry.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Минимальный запас:").grid(row=4, column=0, sticky=tk.W, pady=5)
        min_quantity_var = tk.StringVar(value=str(resource.get('min_quantity', 0)))
        min_quantity_entry = ttk.Entry(form_frame, textvariable=min_quantity_var, width=30)
        min_quantity_entry.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Тип ресурса
        ttk.Label(form_frame, text="Тип ресурса:").grid(row=5, column=0, sticky=tk.W, pady=5)
        resource_types = self.system.get_resource_types()
        type_names = [f"{rt.type.value} - {rt.name}" for rt in resource_types]
        
        # Текущий тип ресурса - ИСПРАВЛЕНИЕ: используем value для сравнения
        current_type_value = resource.get('resource_type', 'consumable')
        current_type_display = None
        
        for rt in resource_types:
            if rt.type.value == current_type_value:
                current_type_display = f"{rt.type.value} - {rt.name}"
                break
        
        if current_type_display is None:
            current_type_display = type_names[0]  # По умолчанию первый тип
        
        type_var = tk.StringVar(value=current_type_display)
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, values=type_names, state="readonly", width=27)
        type_combo.grid(row=5, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Фрейм для атрибутов
        attributes_frame = ttk.LabelFrame(form_frame, text="Атрибуты ресурса", padding=10)
        attributes_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        attribute_entries = {}
        current_attributes = resource.get('attributes', {})
        
        def update_attributes(*args):
            """Обновить поля атрибутов при изменении типа ресурса"""
            for widget in attributes_frame.winfo_children():
                widget.destroy()
            
            attribute_entries.clear()
            
            selected_type_str = type_var.get().split(' - ')[0]
            
            # Находим соответствующий ResourceType
            selected_resource_type = None
            for rt in resource_types:
                if rt.type.value == selected_type_str:
                    selected_resource_type = rt.type
                    break
            
            if selected_resource_type is None:
                selected_resource_type = ResourceType.CONSUMABLE
            
            attributes = self.system.get_resource_type_attributes(selected_resource_type)
            
            if not attributes:
                ttk.Label(attributes_frame, text="Для этого типа ресурса не определены атрибуты").pack()
                return
            
            for i, attr in enumerate(attributes):
                label_text = attr['label']
                if attr.get('required', False):
                    label_text += "*"
                
                ttk.Label(attributes_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
                
                # Значение по умолчанию - текущее значение атрибута или пустое
                current_value = current_attributes.get(attr['name'], '')
                
                if attr['type'] == 'text':
                    entry = ttk.Entry(attributes_frame, width=30)
                    entry.insert(0, current_value)
                    entry.grid(row=i, column=1, pady=2, padx=5, sticky=tk.W)
                elif attr['type'] == 'number':
                    entry = ttk.Entry(attributes_frame, width=30)
                    entry.insert(0, current_value)
                    entry.grid(row=i, column=1, pady=2, padx=5, sticky=tk.W)
                elif attr['type'] == 'date':
                    entry = ttk.Entry(attributes_frame, width=30)
                    entry.insert(0, current_value or datetime.now().strftime("%Y-%m-%d"))
                    entry.grid(row=i, column=1, pady=2, padx=5, sticky=tk.W)
                
                attribute_entries[attr['name']] = entry
        
        type_var.trace('w', update_attributes)
        update_attributes()  # Инициализация
        
        def save_changes():
            try:
                quantity = int(quantity_var.get())
                unit = unit_var.get().strip()
                min_quantity = int(min_quantity_var.get() or 0)
                
                selected_type_str = type_var.get().split(' - ')[0]
                
                # Находим соответствующий ResourceType
                selected_resource_type = None
                for rt in resource_types:
                    if rt.type.value == selected_type_str:
                        selected_resource_type = rt.type
                        break
                
                if selected_resource_type is None:
                    selected_resource_type = ResourceType.CONSUMABLE
                
                # Собираем атрибуты
                attributes = {}
                for attr_name, entry_widget in attribute_entries.items():
                    value = entry_widget.get().strip()
                    if value:
                        attributes[attr_name] = value
                
                if not unit:
                    messagebox.showerror("Ошибка", "Единица измерения не может быть пустой")
                    return
                
                if quantity < 0 or min_quantity < 0:
                    messagebox.showerror("Ошибка", "Количество не может быть отрицательным")
                    return
                
                self.system.update_resource(
                    resource_name,
                    quantity=quantity,
                    unit=unit,
                    min_quantity=min_quantity,
                    resource_type=selected_resource_type,
                    attributes=attributes
                )
                
                messagebox.showinfo("Успех", f"Ресурс '{resource_name}' успешно обновлен")
                dialog.destroy()
                
                if hasattr(self, 'current_screen') and self.current_screen == 'resources':
                    self.show_resources()
                    
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте правильность числовых полей")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        def delete_resource():
            # Удаление доступно только администраторам
            if self.current_user['role'] == 'admin':
                if not is_used:
                    if messagebox.askyesno("Подтверждение удаления", 
                                          f"Вы уверены, что хотите удалить ресурс '{resource_name}'?\n\nЭто действие нельзя отменить."):
                        try:
                            self.system.delete_resource(resource_name)
                            messagebox.showinfo("Успех", f"Ресурс '{resource_name}' успешно удален")
                            dialog.destroy()
                            
                            # Обновляем отображение ресурсов
                            if hasattr(self, 'current_screen') and self.current_screen == 'resources':
                                self.show_resources()
                        except Exception as e:
                            messagebox.showerror("Ошибка", str(e))
                else:
                    messagebox.showwarning("Невозможно удалить", 
                                          f"Ресурс '{resource_name}' используется в заявках и не может быть удален.\n\nВы можете установить количество в 0, но удаление невозможно.")
            else:
                messagebox.showwarning("Недостаточно прав", 
                                      "У вас недостаточно прав для удаления ресурсов. Обратитесь к администратору.")
        
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить изменения", 
                  command=save_changes).pack(side=tk.LEFT, padx=5)
        
        # Кнопка удаления показывается только администраторам
        if self.current_user['role'] == 'admin':
            ttk.Button(buttons_frame, text="Удалить ресурс", 
                      command=delete_resource, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Настройка прокрутки
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Обновляем прокрутку
        dialog.update()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def create_manager_menu(self, parent):
        buttons = [
            ("Создать заявку", self.create_application_dialog),
            ("Просмотр заявок", self.show_all_applications),
            ("Назначение этапов", self.show_advanced_assign_stages),  # ИЗМЕНЕНО: расширенное назначение
            ("Управление шаблонами", self.show_stage_templates_management),  # ДОБАВЛЕНО
            ("Отчет по заявкам", self.show_applications_report)
        ]
        
        for text, command in buttons:
            ttk.Button(parent, text=text, command=command,
                    width=30).pack(pady=10)
    
    # Новые методы для расширенного функционала
    
    def show_stock_receipt(self):
        """Диалог приходной накладной с сохранением"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Приходная накладная")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Приходная накладная", 
                style="Title.TLabel").pack(pady=10)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поля накладной
        ttk.Label(main_frame, text="Поставщик:").grid(row=0, column=0, sticky=tk.W, pady=5)
        supplier_entry = ttk.Entry(main_frame, width=30)
        supplier_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Номер документа:").grid(row=1, column=0, sticky=tk.W, pady=5)
        doc_entry = ttk.Entry(main_frame, width=30)
        doc_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Таблица ресурсов
        ttk.Label(main_frame, text="Ресурсы:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        resources_frame = ttk.Frame(main_frame)
        resources_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=tk.W+tk.E)
        
        columns = ("Ресурс", "Количество", "Единица")
        tree = ttk.Treeview(resources_frame, columns=columns, show="headings", height=5)
        
        for col in columns:
            tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(resources_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления ресурсами
        resource_buttons = ttk.Frame(main_frame)
        resource_buttons.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(resource_buttons, text="Добавить ресурс", 
                command=lambda: self.add_resource_to_receipt(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(resource_buttons, text="Удалить ресурс", 
                command=lambda: self.remove_resource_from_receipt(tree)).pack(side=tk.LEFT, padx=5)
        
        def create_receipt():
            supplier = supplier_entry.get()
            doc_number = doc_entry.get()
            
            # Собираем ресурсы из таблицы
            resources = []
            for item in tree.get_children():
                values = tree.item(item, 'values')
                resources.append({
                    'name': values[0],
                    'quantity': int(values[1]),
                    'unit': values[2]
                })
            
            if not resources:
                messagebox.showerror("Ошибка", "Добавьте хотя бы один ресурс")
                return
            
            try:
                receipt_id = self.system.add_stock_receipt(resources, supplier, doc_number)
                messagebox.showinfo("Успех", f"Накладная создана!\nID: {receipt_id}")
                dialog.destroy()
                # Показываем список накладных после создания
                self.show_stock_receipts_list()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        ttk.Button(main_frame, text="Создать накладную", 
                command=create_receipt).grid(row=5, column=0, columnspan=2, pady=20)

    def add_stock_receipt(self, resources, supplier="", document_number=""):
        """Упрощенная версия - добавление приходной накладной с поддержкой типов"""
        if not self.has_permission('manage_resources'):
            raise PermissionError("Недостаточно прав")
        
        # Обновляем остатки
        current_resources = self.get_resources()
        for resource in resources:
            name = resource['name']
            quantity = resource['quantity']
            unit = resource.get('unit', 'шт')
            resource_type = ResourceType(resource.get('resource_type', 'consumable'))
            
            if name in current_resources:
                current_resources[name]['quantity'] += quantity
                # Обновляем тип если он изменился
                if 'resource_type' in resource:
                    current_resources[name]['resource_type'] = resource_type.value
            else:
                # Создаем новый ресурс с типом
                self.add_resource(
                    name, 
                    quantity, 
                    unit,
                    resource.get('min_quantity', 0),
                    resource_type,
                    resource.get('attributes', {})
                )
        
        receipt_id = f"receipt_{len(current_resources) + 1}"
        return receipt_id

    def add_resource_to_receipt(self, tree):
        """Добавление ресурса в накладную с поддержкой типов"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление ресурса")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Добавление ресурса", 
                 style="Header.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=20)
        name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Тип:").grid(row=1, column=0, sticky=tk.W, pady=5)
        resource_types = self.system.get_resource_types()
        type_names = [f"{rt.type.value} - {rt.name}" for rt in resource_types]
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, 
                                 values=type_names, state="readonly", width=17)
        type_combo.grid(row=1, column=1, pady=5, padx=5)
        type_combo.current(0)
        
        ttk.Label(form_frame, text="Количество:").grid(row=2, column=0, sticky=tk.W, pady=5)
        quantity_entry = ttk.Entry(form_frame, width=20)
        quantity_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Единица:").grid(row=3, column=0, sticky=tk.W, pady=5)
        unit_entry = ttk.Entry(form_frame, width=20)
        unit_entry.insert(0, "шт")
        unit_entry.grid(row=3, column=1, pady=5, padx=5)
        
        def add_resource():
            name = name_entry.get()
            quantity = quantity_entry.get()
            unit = unit_entry.get()
            selected_type_str = type_var.get().split(' - ')[0]
            
            if not name or not quantity:
                messagebox.showerror("Ошибка", "Заполните название и количество")
                return
            
            try:
                quantity = int(quantity)
                
                # Находим соответствующий ResourceType
                selected_resource_type = None
                for rt in resource_types:
                    if rt.type.value == selected_type_str:
                        selected_resource_type = rt.type
                        break
                
                if selected_resource_type is None:
                    selected_resource_type = ResourceType.CONSUMABLE
                
                tree.insert("", tk.END, values=(
                    name, 
                    quantity, 
                    unit, 
                    selected_resource_type.value  # Добавляем тип в значения
                ))
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Количество должно быть числом")
        
        ttk.Button(form_frame, text="Добавить", 
                  command=add_resource).grid(row=4, column=0, columnspan=2, pady=10)

    def remove_resource_from_receipt(self, tree):
        """Удаление ресурса из накладной"""
        selection = tree.selection()
        if selection:
            tree.delete(selection)
    
    def show_inventory(self):
        """Главный экран инвентаризации - список инвентаризаций"""
        self.clear_window()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(header_frame, text="Назад", 
                command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Инвентаризации склада", 
                style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        # Кнопка начала новой инвентаризации
        ttk.Button(header_frame, text="Начать новую инвентаризацию", 
                command=self.start_new_inventory).pack(side=tk.RIGHT)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        try:
            inventories = self.system.get_inventories()
            
            if not inventories:
                ttk.Label(main_frame, text="Инвентаризации не проводились").pack(pady=50)
                return
                
            # Таблица инвентаризаций
            tree_frame = ttk.Frame(main_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ("ID", "Дата начала", "Статус", "Провел", "Ресурсов", "Посчитано", "Расхождения")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
                
            tree.column("ID", width=150)
            tree.column("Дата начала", width=120)
            
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            for inventory_id, inventory in inventories.items():
                status_display = "В процессе" if inventory['status'] == 'in_progress' else "Завершена"
                date_display = inventory['date_started'][:10]
                
                tree.insert("", tk.END, values=(
                    inventory_id,
                    date_display,
                    status_display,
                    inventory['conducted_by'],
                    inventory['total_items'],
                    inventory['items_counted'],
                    inventory['discrepancies_count']
                ), tags=(inventory_id,))
                
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def on_item_double_click(event):
                item = tree.selection()[0]
                inventory_id = tree.item(item, "tags")[0]
                self.show_inventory_details(inventory_id)
                
            tree.bind("<Double-1>", on_item_double_click)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить инвентаризации: {str(e)}")

    def start_new_inventory(self):
        """Начало новой инвентаризации"""
        try:
            inventory_id = self.system.start_inventory()
            messagebox.showinfo("Успех", f"Новая инвентаризация начата!\nID: {inventory_id}")
            # Переходим к редактированию новой инвентаризации
            self.show_inventory_details(inventory_id)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось начать инвентаризацию: {str(e)}")

    def show_inventory_details(self, inventory_id):
        """Просмотр и редактирование инвентаризации"""
        inventory = self.system.get_inventory(inventory_id)
        
        if not inventory:
            messagebox.showerror("Ошибка", "Инвентаризация не найдена")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Инвентаризация {inventory_id}")
        dialog.geometry("900x700")
        dialog.transient(self.root)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(main_frame, text=f"Инвентаризация {inventory_id}", 
                style="Title.TLabel").pack(pady=10)
        
        # Информация об инвентаризации
        info_frame = ttk.LabelFrame(main_frame, text="Информация об инвентаризации", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        status_display = "В процессе" if inventory['status'] == 'in_progress' else "Завершена"
        ttk.Label(info_frame, text=f"Статус: {status_display}").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Дата начала: {inventory['date_started']}").grid(row=0, column=1, sticky=tk.W, pady=2, padx=20)
        ttk.Label(info_frame, text=f"Проводит: {inventory['conducted_by']}").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        if inventory['status'] == 'completed':
            ttk.Label(info_frame, text=f"Дата завершения: {inventory['date_completed']}").grid(row=1, column=1, sticky=tk.W, pady=2, padx=20)
            ttk.Label(info_frame, text=f"Завершил: {inventory.get('completed_by', '')}").grid(row=2, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(info_frame, text=f"Всего ресурсов: {inventory['total_items']}").grid(row=2, column=1, sticky=tk.W, pady=2, padx=20)
        ttk.Label(info_frame, text=f"Посчитано: {inventory['items_counted']}").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Расхождения: {inventory['discrepancies_count']}").grid(row=3, column=1, sticky=tk.W, pady=2, padx=20)
        
        # Таблица ресурсов для инвентаризации
        ttk.Label(main_frame, text="Ресурсы:", style="Header.TLabel").pack(anchor=tk.W, pady=10)
        
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("Ресурс", "Ожидаемое", "Фактическое", "Разница", "Единица", "Статус")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            
        tree.column("Ресурс", width=200)
        tree.column("Статус", width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        for item in inventory['items']:
            actual = item['actual_quantity'] if item['actual_quantity'] is not None else "Не посчитано"
            difference = item['difference']
            
            # Определяем статус
            if item['actual_quantity'] is None:
                status = "Не посчитан"
                color = "orange"
            elif difference == 0:
                status = "Совпадает"
                color = "green"
            else:
                status = "Расхождение"
                color = "red"
            
            tree.insert("", tk.END, values=(
                item['resource_name'],
                item['expected_quantity'],
                actual,
                difference,
                item['unit'],
                status
            ), tags=(color, item['resource_name']))
            
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Настраиваем цвета строк
        tree.tag_configure("green", foreground="green")
        tree.tag_configure("red", foreground="red")
        tree.tag_configure("orange", foreground="orange")
        
        # Фрейм для кнопок
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        if inventory['status'] == 'in_progress':
            # Кнопка редактирования выбранного ресурса
            def edit_selected_item():
                selection = tree.selection()
                if not selection:
                    messagebox.showinfo("Информация", "Выберите ресурс для редактирования")
                    return
                    
                item = selection[0]
                resource_name = tree.item(item, "tags")[1]
                self.edit_inventory_item(dialog, inventory_id, resource_name, inventory)
                
            ttk.Button(buttons_frame, text="Внести фактическое количество", 
                    command=edit_selected_item).pack(side=tk.LEFT, padx=5)
            
            # Кнопка завершения инвентаризации
            def complete_inv():
                if inventory['items_counted'] < inventory['total_items']:
                    if not messagebox.askyesno("Подтверждение", 
                                            "Не все ресурсы посчитаны. Завершить инвентаризацию?"):
                        return
                
                # Спросить об обновлении остатков
                update_stock = messagebox.askyesno("Обновление остатков", 
                                                "Обновить остатки на складе по результатам инвентаризации?")
                
                try:
                    self.system.complete_inventory(inventory_id, update_stock)
                    messagebox.showinfo("Успех", "Инвентаризация завершена!")
                    dialog.destroy()
                    self.show_inventory()  # Обновляем список
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))
                    
            ttk.Button(buttons_frame, text="Завершить инвентаризацию", 
                    command=complete_inv).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Закрыть", 
                command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_inventory_item(self, parent_dialog, inventory_id, resource_name, inventory):
        """Диалог редактирования фактического количества ресурса"""
        # Находим элемент в инвентаризации
        item_data = None
        for item in inventory['items']:
            if item['resource_name'] == resource_name:
                item_data = item
                break
        
        if not item_data:
            messagebox.showerror("Ошибка", "Ресурс не найден")
            return
            
        dialog = tk.Toplevel(parent_dialog)
        dialog.title(f"Редактирование: {resource_name}")
        dialog.geometry("400x250")
        dialog.transient(parent_dialog)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"Ресурс: {resource_name}", 
                style="Header.TLabel").pack(pady=10)
        
        ttk.Label(main_frame, text=f"Ожидаемое количество: {item_data['expected_quantity']} {item_data['unit']}").pack(pady=5)
        
        ttk.Label(main_frame, text="Фактическое количество:").pack(pady=10)
        
        quantity_var = tk.StringVar(value=str(item_data['actual_quantity']) if item_data['actual_quantity'] is not None else "")
        quantity_entry = ttk.Entry(main_frame, textvariable=quantity_var, width=20)
        quantity_entry.pack(pady=5)
        
        def save_quantity():
            try:
                actual_quantity = int(quantity_var.get())
                if actual_quantity < 0:
                    messagebox.showerror("Ошибка", "Количество не может быть отрицательным")
                    return
                    
                self.system.update_inventory_item(inventory_id, resource_name, actual_quantity)
                messagebox.showinfo("Успех", "Количество обновлено!")
                dialog.destroy()
                parent_dialog.destroy()  # Закрываем родительский диалог
                self.show_inventory_details(inventory_id)  # Переоткрываем с обновленными данными
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        ttk.Button(main_frame, text="Сохранить", 
                command=save_quantity).pack(pady=15)
        
        ttk.Button(main_frame, text="Отмена", 
                command=dialog.destroy).pack()
        
        quantity_entry.focus()

    def show_stock_report(self):
        """Отчет по складу"""
        try:
            report_data = self.system.generate_stock_report()
            
            dialog = tk.Toplevel(self.root)
            dialog.title("Отчет по складу")
            dialog.geometry("700x500")
            dialog.transient(self.root)
            
            main_frame = ttk.Frame(dialog, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Отчет по складу", 
                     style="Title.TLabel").pack(pady=10)
            
            # Сводная информация
            summary_frame = ttk.LabelFrame(main_frame, text="Сводка", padding=10)
            summary_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(summary_frame, 
                     text=f"Всего позиций: {report_data['total_items']}").pack(anchor=tk.W)
            ttk.Label(summary_frame, 
                     text=f"Общее количество: {report_data['total_quantity']}").pack(anchor=tk.W)
            
            if report_data['low_stock']:
                ttk.Label(summary_frame, 
                         text=f"Позиций с низким запасом: {len(report_data['low_stock'])}",
                         foreground="red").pack(anchor=tk.W)
            
            # Таблица ресурсов
            tree_frame = ttk.Frame(main_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            columns = ("Ресурс", "Количество", "Единица", "Мин. запас", "Статус")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
            
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            for name, resource in report_data['resources'].items():
                status = "Норма"
                if resource['quantity'] < resource.get('min_quantity', 0):
                    status = "Низкий запас"
                
                tree.insert("", tk.END, values=(
                    name,
                    resource['quantity'],  # Было: resource.quantity
                    resource.get('unit', 'шт'),  # Было: resource.unit
                    resource.get('min_quantity', 0),  # Было: resource.min_quantity
                    status
                ))
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def show_applications_report(self):
        """Отчет по заявкам"""
        try:
            report_data = self.system.generate_applications_status_report()
            
            dialog = tk.Toplevel(self.root)
            dialog.title("Отчет по заявкам")
            dialog.geometry("500x400")
            dialog.transient(self.root)
            
            main_frame = ttk.Frame(dialog, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Отчет по заявкам", 
                     style="Title.TLabel").pack(pady=10)
            
            ttk.Label(main_frame, text=report_data['summary']).pack(pady=5)
            ttk.Label(main_frame, text=f"Всего заявок: {report_data['total']}").pack(pady=5)
            
            # Статистика по статусам
            stats_frame = ttk.LabelFrame(main_frame, text="Статистика по статусам", padding=10)
            stats_frame.pack(fill=tk.X, pady=10)
            
            for status, count in report_data['by_status'].items():
                ttk.Label(stats_frame, text=f"{status}: {count}").pack(anchor=tk.W)
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def show_reports_menu(self):
        """Меню отчетов для администратора"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Система отчетности")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Система отчетности", 
                 style="Title.TLabel").pack(pady=10)
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(form_frame, text="Отчет по заявкам", 
                  command=self.show_applications_report,
                  width=30).pack(pady=10)
        ttk.Button(form_frame, text="Отчет по складу", 
                  command=self.show_stock_report,
                  width=30).pack(pady=10)
        
        ttk.Button(form_frame, text="Закрыть", 
                  command=dialog.destroy).pack(pady=20)

if __name__ == "__main__":
    app = GUIInterface()
    app.run()