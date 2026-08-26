class ExplorerEngineError(Exception):
    """Base explorer engine error."""


class NodeNotFoundError(ExplorerEngineError):
    """Raised when a requested node does not exist."""


class GraphNotLoadedError(ExplorerEngineError):
    """Raised when an operation is attempted before loading the graph."""


class QueryValidationError(ExplorerEngineError):
    """Raised when a query input fails runtime validation."""
