from .base import BaseTool, ToolResult, ToolSideEffect
from .registry import tool_registry, ToolRegistry
from .test_tool import TestTool
from .erp_tools import (
    ShippingGetRatesTool,
    ShippingCreateShipmentTool,
    ShippingPrintLabelTool,
    EtaSubmitInvoiceTool,
    EtaCheckStatusTool,
    CustomsGetDeclarationsTool,
    CustomsFileDeclarationTool,
    DocumentsGenerateTool,
    DocumentsUploadTool,
    SearchGlobalTool,
    DashboardGetStatsTool,
    NotificationsSendTool,
    WorkflowGetStateTool,
    WorkflowTransitionTool,
    ResearchPresentResultTool,
)

tool_registry.register(TestTool)
tool_registry.register(ShippingGetRatesTool)
tool_registry.register(ShippingCreateShipmentTool)
tool_registry.register(ShippingPrintLabelTool)
tool_registry.register(EtaSubmitInvoiceTool)
tool_registry.register(EtaCheckStatusTool)
tool_registry.register(CustomsGetDeclarationsTool)
tool_registry.register(CustomsFileDeclarationTool)
tool_registry.register(DocumentsGenerateTool)
tool_registry.register(DocumentsUploadTool)
tool_registry.register(SearchGlobalTool)
tool_registry.register(DashboardGetStatsTool)
tool_registry.register(NotificationsSendTool)
tool_registry.register(WorkflowGetStateTool)
tool_registry.register(WorkflowTransitionTool)
tool_registry.register(ResearchPresentResultTool)
