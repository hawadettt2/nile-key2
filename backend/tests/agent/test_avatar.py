import pytest
from unittest.mock import AsyncMock
from typing import Any, Dict
from pydantic import ValidationError

from app.agent.avatar.interface import IntentContent, AvatarRenderer


class ConcreteAvatarRenderer(AvatarRenderer):
    """Concrete implementation for testing."""

    async def render(self, intent_content: IntentContent) -> Dict[str, Any]:
        return {
            "modality": "text",
            "payload": {"message": f"Intent: {intent_content.intent_type}"},
            "metadata": {"renderer": "test"},
        }


class TestIntentContent:
    """Verify IntentContent contract."""

    def test_create_with_all_fields(self):
        intent = IntentContent(
            intent_type="mission_started",
            content={"mission_id": "abc-123"},
            context={"session_id": "session-456"},
            suggested_actions=["view_details"],
        )
        assert intent.intent_type == "mission_started"
        assert intent.content == {"mission_id": "abc-123"}
        assert intent.context == {"session_id": "session-456"}
        assert intent.suggested_actions == ["view_details"]

    def test_intent_type_required(self):
        with pytest.raises(ValidationError):
            IntentContent(
                content={},
                context={},
                suggested_actions=[],
            )

    def test_content_required(self):
        with pytest.raises(ValidationError):
            IntentContent(
                intent_type="test",
                context={},
                suggested_actions=[],
            )

    def test_context_required(self):
        with pytest.raises(ValidationError):
            IntentContent(
                intent_type="test",
                content={},
                suggested_actions=[],
            )

    def test_suggested_actions_required(self):
        with pytest.raises(ValidationError):
            IntentContent(
                intent_type="test",
                content={},
                context={},
            )

    def test_default_suggested_actions_is_empty_list(self):
        intent = IntentContent(
            intent_type="test",
            content={},
            context={},
            suggested_actions=[],
        )
        assert intent.suggested_actions == []

    def test_content_type_must_be_dict(self):
        with pytest.raises(ValidationError):
            IntentContent(
                intent_type="test",
                content="not_a_dict",
                context={},
                suggested_actions=[],
            )

    def test_context_type_must_be_dict(self):
        with pytest.raises(ValidationError):
            IntentContent(
                intent_type="test",
                content={},
                context="not_a_dict",
                suggested_actions=[],
            )

    def test_suggested_actions_type_must_be_list(self):
        with pytest.raises(ValidationError):
            IntentContent(
                intent_type="test",
                content={},
                context={},
                suggested_actions="not_a_list",
            )


class TestAvatarRenderer:
    """Verify AvatarRenderer interface contract."""

    def test_interface_is_abstract(self):
        with pytest.raises(TypeError):
            AvatarRenderer()

    @pytest.mark.asyncio
    async def test_concrete_renderer_implements_render(self):
        renderer = ConcreteAvatarRenderer()
        intent = IntentContent(
            intent_type="test",
            content={"key": "value"},
            context={"session_id": "123"},
            suggested_actions=["action1"],
        )
        result = await renderer.render(intent)
        assert "modality" in result
        assert "payload" in result
        assert "metadata" in result
        assert result["modality"] == "text"

    @pytest.mark.asyncio
    async def test_renderer_receives_intent_content(self):
        renderer = ConcreteAvatarRenderer()
        intent = IntentContent(
            intent_type="mission_completed",
            content={"mission_id": "abc"},
            context={"session_id": "456"},
            suggested_actions=["view"],
        )
        result = await renderer.render(intent)
        assert "Intent: mission_completed" in result["payload"]["message"]


class TestAvatarPackageExports:
    """Verify avatar package exports."""

    def test_import_intent_content(self):
        from app.agent.avatar import IntentContent
        assert IntentContent is not None

    def test_import_avatar_renderer(self):
        from app.agent.avatar import AvatarRenderer
        assert AvatarRenderer is not None

    def test_import_from_interface(self):
        from app.agent.avatar.interface import IntentContent, AvatarRenderer
        assert IntentContent is not None
        assert AvatarRenderer is not None
