# models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum

class ResourceType(Enum):
    EQUIPMENT = "equipment"
    CONSUMABLE = "consumable" 
    MATERIAL = "material"
    TOOL = "tool"
    ELECTRONICS = "electronics"
    CHEMICAL = "chemical"

class UserStatus(Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"

@dataclass
class StageTemplate:
    id: str
    name: str
    description: str
    typical_duration_days: int = 0
    required_resources: List[Dict] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class StagePlan:
    stage_id: str
    name: str
    description: str
    planned_start_date: str = ""
    planned_end_date: str = ""
    actual_start_date: str = ""
    actual_end_date: str = ""
    dependencies: List[str] = field(default_factory=list)
    required_resources: List[Dict] = field(default_factory=list)
    status: str = "planned"  # planned, in_progress, completed
    executor: str = ""

@dataclass
class ResourceTypeDefinition:
    type: ResourceType
    name: str
    description: str
    attributes: List[Dict]

@dataclass
class User:
    username: str
    password_hash: str
    role: str
    full_name: str
    department: str = ""
    status: UserStatus = UserStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Stage:
    id: str
    name: str
    executor: str
    status: str = "assigned"
    requested_resources: List[Dict] = field(default_factory=list)
    report: str = ""

@dataclass
class Application:
    id: str
    date: str
    customer: str
    contract_number: str
    description: str
    status: str = "created"
    stages: Dict[str, Stage] = field(default_factory=dict)

@dataclass
class Resource:
    name: str
    quantity: int
    unit: str
    min_quantity: int = 0
    resource_type: ResourceType = ResourceType.CONSUMABLE
    attributes: Dict[str, Any] = field(default_factory=dict)
    reserved: int = 0  # Зарезервировано под этапы

@dataclass
class StockReceipt:
    id: str
    date: str
    received_by: str
    resources: List[Dict]  # {resource_name, quantity, unit, cost}
    supplier: str = ""
    document_number: str = ""

@dataclass
class Inventory:
    id: str
    date: str
    conducted_by: str
    items: List[Dict] = field(default_factory=list)  # {resource_name, actual_quantity, expected_quantity, difference}
    status: str = "in_progress"  # in_progress, completed

@dataclass
class Report:
    id: str
    type: str
    generated_by: str
    generated_at: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
