# config.py - обновляем разрешения для storeman

USER_ROLES = {
    'admin': ['manage_users', 'view_all', 'import_data', 'manage_resources', 'generate_reports', 'view_resources', 'create_application', 'edit_application', 'view_users', 'manage_templates'],
    'customer': ['create_application', 'view_own_applications', 'edit_own_application'],
    'manager': ['assign_stages', 'view_all_applications', 'assign_executors', 'generate_reports', 'create_application', 'edit_application', 'view_users', 'manage_templates'],  # ДОБАВЛЕНО manage_templates
    'executor': ['view_assigned_stages', 'request_resources', 'complete_stages', 'view_resources'],
    'storeman': ['manage_resources', 'view_resources', 'generate_reports', 'edit_resources']
}
