import pytest
from app.agent.tools.erp_tools import ResearchPresentResultTool


class TestResearchPresentResultTool:
    """Tests for ResearchPresentResultTool business-answer transformation."""

    def setup_method(self):
        self.tool = ResearchPresentResultTool()

    @pytest.mark.asyncio
    async def test_transforms_research_result_to_business_answer(self):
        research_result = {
            "goal": "market study for Egyptian fruits in Jordan",
            "status": "completed",
            "findings": [
                {
                    "topic": "market demand",
                    "content": "High demand for Egyptian oranges in Jordan",
                    "confidence": 0.9,
                    "evidence": [
                        {"source_id": "src1", "source_url": "http://example.com/1", "content_excerpt": "Jordan imports 40% of oranges from Egypt"}
                    ],
                }
            ],
            "sources_consulted": ["src1", "src2"],
            "sources_failed": [],
            "errors": None,
            "created_at": "2026-01-01T00:00:00Z",
            "completed_at": "2026-01-01T00:01:00Z",
            "metadata": {"request_id": "req_123"},
        }

        result = await self.tool.execute({}, {"research_result": research_result})
        assert result.status == "success"
        data = result.data
        assert data["goal"] == "market study for Egyptian fruits in Jordan"
        assert data["status"] == "completed"
        assert "summary" in data
        assert "market demand: High demand for Egyptian oranges in Jordan" in data["summary"]
        assert len(data["findings"]) == 1
        assert data["findings"][0]["topic"] == "market demand"
        assert data["sources_consulted"] == ["src1", "src2"]
        assert data["sources_failed"] == []

    @pytest.mark.asyncio
    async def test_business_answer_excludes_internal_wp34_fields(self):
        research_result = {
            "request_id": "req_123",
            "status": "completed",
            "goal": "market study",
            "findings": [],
            "sources_consulted": [],
            "sources_failed": [],
            "errors": None,
            "created_at": "2026-01-01T00:00:00Z",
            "completed_at": "2026-01-01T00:01:00Z",
            "metadata": {"internal": "data"},
        }

        result = await self.tool.execute({}, {"research_result": research_result})
        assert result.status == "success"
        data = result.data
        assert "request_id" not in data
        assert "created_at" not in data
        assert "completed_at" not in data
        assert "metadata" not in data

    @pytest.mark.asyncio
    async def test_business_answer_handles_empty_findings(self):
        research_result = {
            "goal": "market study",
            "status": "completed",
            "findings": [],
            "sources_consulted": [],
            "sources_failed": [],
        }

        result = await self.tool.execute({}, {"research_result": research_result})
        assert result.status == "success"
        data = result.data
        assert data["goal"] == "market study"
        assert data["summary"] == "market study"

    @pytest.mark.asyncio
    async def test_business_answer_handles_invalid_input(self):
        result = await self.tool.execute({}, {"research_result": "not a dict"})
        assert result.status == "error"
        assert "Invalid research result" in result.error

    @pytest.mark.asyncio
    async def test_business_answer_includes_sources_in_findings(self):
        research_result = {
            "goal": "market study",
            "status": "completed",
            "findings": [
                {
                    "topic": "demand",
                    "content": "High demand",
                    "confidence": 0.9,
                    "evidence": [
                        {"source_id": "src1", "source_url": "http://example.com/1", "content_excerpt": "excerpt text"}
                    ],
                }
            ],
            "sources_consulted": ["src1"],
            "sources_failed": [],
        }

        result = await self.tool.execute({}, {"research_result": research_result})
        assert result.status == "success"
        data = result.data
        assert len(data["findings"]) == 1
        assert data["findings"][0]["sources"][0]["source_id"] == "src1"
        assert data["findings"][0]["sources"][0]["source_url"] == "http://example.com/1"
        assert data["findings"][0]["sources"][0]["excerpt"] == "excerpt text"
