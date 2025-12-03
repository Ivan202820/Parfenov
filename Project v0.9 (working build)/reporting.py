# reporting.py
from data_manager import DataManager
from models import Report
from datetime import datetime, timedelta
from typing import Dict, List
import json

class ReportingSystem:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def generate_applications_status_report(self, generated_by: str, filters: Dict = None):
        """Отчет по статусам заявок"""
        applications = self.data_manager.load_applications()
        users = self.data_manager.load_users()
        
        if filters is None:
            filters = {}
        
        # Фильтрация заявок
        filtered_apps = {}
        for app_id, app in applications.items():
            if 'status' in filters and app.status != filters['status']:
                continue
            if 'customer' in filters and app.customer != filters['customer']:
                continue
            if 'date_from' in filters and app.date < filters['date_from']:
                continue
            if 'date_to' in filters and app.date > filters['date_to']:
                continue
            filtered_apps[app_id] = app
        
        # Статистика по статусам
        status_stats = {}
        stage_stats = {}
        for app in filtered_apps.values():
            status_stats[app.status] = status_stats.get(app.status, 0) + 1
            stage_stats[len(app.stages)] = stage_stats.get(len(app.stages), 0) + 1
        
        report_data = {
            'total_applications': len(filtered_apps),
            'status_distribution': status_stats,
            'stages_distribution': stage_stats,
            'applications': {app_id: {
                'date': app.date,
                'customer': app.customer,
                'contract_number': app.contract_number,
                'status': app.status,
                'stages_count': len(app.stages),
                'completed_stages': len([s for s in app.stages.values() if s.status == 'completed'])
            } for app_id, app in filtered_apps.items()}
        }
        
        return self._save_report('applications_status', generated_by, filters, report_data)
    
    def generate_executors_workload_report(self, generated_by: str, period_days: int = 30):
        """Отчет по загрузке исполнителей"""
        applications = self.data_manager.load_applications()
        users = self.data_manager.load_users()
        
        # Фильтрация по периоду
        cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
        
        executors_workload = {}
        
        for app in applications.values():
            if app.date < cutoff_date:
                continue
                
            for stage in app.stages.values():
                executor = stage.executor
                if executor not in executors_workload:
                    executors_workload[executor] = {
                        'total_stages': 0,
                        'completed_stages': 0,
                        'active_stages': 0,
                        'stages': []
                    }
                
                executors_workload[executor]['total_stages'] += 1
                if stage.status == 'completed':
                    executors_workload[executor]['completed_stages'] += 1
                else:
                    executors_workload[executor]['active_stages'] += 1
                
                executors_workload[executor]['stages'].append({
                    'application_id': app.id,
                    'stage_name': stage.name,
                    'status': stage.status,
                    'date': app.date
                })
        
        # Расчет загрузки
        for executor, data in executors_workload.items():
            completion_rate = (data['completed_stages'] / data['total_stages'] * 100) if data['total_stages'] > 0 else 0
            data['completion_rate'] = round(completion_rate, 2)
            data['workload_percentage'] = min(data['active_stages'] * 10, 100)  # Упрощенный расчет
        
        report_data = {
            'period_days': period_days,
            'executors_workload': executors_workload,
            'summary': {
                'total_executors': len(executors_workload),
                'avg_completion_rate': sum(data['completion_rate'] for data in executors_workload.values()) / len(executors_workload) if executors_workload else 0,
                'avg_workload': sum(data['workload_percentage'] for data in executors_workload.values()) / len(executors_workload) if executors_workload else 0
            }
        }
        
        return self._save_report('executors_workload', generated_by, {'period_days': period_days}, report_data)
    
    def generate_resource_usage_report(self, generated_by: str, period_days: int = 30):
        """Отчет по использованию ресурсов"""
        applications = self.data_manager.load_applications()
        resources = self.data_manager.load_resources()
        
        cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
        
        resource_usage = {}
        total_used = 0
        
        for app in applications.values():
            if app.date < cutoff_date:
                continue
                
            for stage in app.stages.values():
                for request in stage.requested_resources:
                    if request['status'] == 'allocated':
                        resource_name = request['resource']
                        quantity = request['quantity']
                        
                        if resource_name not in resource_usage:
                            resource_usage[resource_name] = {
                                'total_used': 0,
                                'applications': set(),
                                'unit': resources[resource_name].unit if resource_name in resources else 'шт'
                            }
                        
                        resource_usage[resource_name]['total_used'] += quantity
                        resource_usage[resource_name]['applications'].add(app.id)
                        total_used += quantity
        
        # Преобразуем множества в списки
        for resource in resource_usage.values():
            resource['applications'] = list(resource['applications'])
            resource['applications_count'] = len(resource['applications'])
        
        report_data = {
            'period_days': period_days,
            'resource_usage': resource_usage,
            'total_resources_used': total_used,
            'most_used_resources': sorted(resource_usage.items(), key=lambda x: x[1]['total_used'], reverse=True)[:10]
        }
        
        return self._save_report('resource_usage', generated_by, {'period_days': period_days}, report_data)
    
    def generate_stock_report(self, generated_by: str):
        """Отчет по остаткам на складе"""
        resources = self.data_manager.load_resources()
        
        stock_data = {}
        low_stock_items = []
        total_value = 0
        
        for name, resource in resources.items():
            stock_data[name] = {
                'quantity': resource.quantity,
                'reserved': resource.reserved,
                'available': resource.quantity - resource.reserved,
                'unit': resource.unit,
                'min_quantity': resource.min_quantity,
                'resource_type': resource.resource_type.value,
                'below_min': resource.quantity < resource.min_quantity
            }
            
            if resource.quantity < resource.min_quantity:
                low_stock_items.append(name)
            
            # Упрощенный расчет "стоимости" - можно расширить
            total_value += resource.quantity
        
        report_data = {
            'stock_data': stock_data,
            'summary': {
                'total_items': len(resources),
                'total_quantity': sum(r.quantity for r in resources.values()),
                'total_reserved': sum(r.reserved for r in resources.values()),
                'total_available': sum(r.quantity - r.reserved for r in resources.values()),
                'low_stock_count': len(low_stock_items),
                'low_stock_items': low_stock_items,
                'estimated_value': total_value
            }
        }
        
        return self._save_report('stock_status', generated_by, {}, report_data)
    
    def _save_report(self, report_type: str, generated_by: str, parameters: Dict, data: Dict):
        """Сохранение отчета"""
        report_id = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        report = Report(
            id=report_id,
            type=report_type,
            generated_by=generated_by,
            generated_at=datetime.now().isoformat(),
            parameters=parameters,
            data=data
        )
        
        reports = self.data_manager.load_data('reports.json', {})
        reports[report_id] = report.__dict__
        self.data_manager.save_data('reports.json', reports)
        
        return report_id
    
    def get_reports(self, report_type: str = None):
        """Получение отчетов"""
        reports = self.data_manager.load_data('reports.json', {})
        
        if report_type:
            return {rid: report for rid, report in reports.items() if report['type'] == report_type}
        return reports
