class DigitalExportManagerException(Exception):
    """Base exception for Digital Export Manager."""
    pass


class DecisionEngineException(DigitalExportManagerException):
    """Raised when the Decision Engine encounters an error."""
    pass


class MissionPlannerException(DigitalExportManagerException):
    """Raised when the Mission Planner encounters an error."""
    pass


class ExecutionEngineException(DigitalExportManagerException):
    """Raised when the Execution Engine encounters an error."""
    pass


class ToolNotFoundException(DigitalExportManagerException):
    """Raised when a required tool is not found."""
    pass


class ToolExecutionException(DigitalExportManagerException):
    """Raised when a tool execution fails."""
    pass


class SessionException(DigitalExportManagerException):
    """Raised when a session operation fails."""
    pass


class ApprovalRequiredException(DigitalExportManagerException):
    """Raised when an operation requires human approval."""
    pass
