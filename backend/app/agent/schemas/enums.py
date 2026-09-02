from enum import Enum


class MissionType(str, Enum):
    CREATE_SHIPMENT = "CREATE_SHIPMENT"
    SUBMIT_INVOICE = "SUBMIT_INVOICE"
    FILE_CUSTOMS = "FILE_CUSTOMS"
    GENERATE_DOCUMENT = "GENERATE_DOCUMENT"
    SEARCH_ENTITIES = "SEARCH_ENTITIES"
    GET_DASHBOARD = "GET_DASHBOARD"
    SEND_NOTIFICATION = "SEND_NOTIFICATION"
    TRANSITION_WORKFLOW = "TRANSITION_WORKFLOW"
    RESEARCH = "RESEARCH"


class MissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING_APPROVAL = "pending_approval"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionMode(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
