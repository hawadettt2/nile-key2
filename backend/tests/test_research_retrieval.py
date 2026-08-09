import uuid
import pytest
import asyncio
from typing import Optional

from app.research.retrieval.contracts import (
    ContentProcessor,
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceRetriever,
)
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.retrieval.stubs import StubRetriever, StubProcessor
from app.schemas.research import Source, SourceRegistration, SourceRegistration


def _make_source(source_id=None, source_type="market_data", status="active"):
    return Source(
        source_id=source_id or f"src_{uuid.uuid4().hex[:8]}",
        name=f"Test Source {source_id or 'unknown'}",
        source_type=source_type,
        reference="https://example.com/data",
        metadata={"domains": ["agriculture"]},
        status=status,
    )


# ========== Retrieval Contracts ==========


class CustomRetriever(SourceRetriever):
    def __init__(self, fail_on_source_id=None, delay_seconds=0):
        self.fail_on_source_id = fail_on_source_id
        self.delay_seconds = delay_seconds

    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        if self.fail_on_source_id and source.source_id == self.fail_on_source_id:
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.CONNECTION_FAILURE,
                error="Connection refused",
            )
        if self.delay_seconds:
            import asyncio
            await asyncio.sleep(self.delay_seconds)
        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.SUCCESS,
            content=RetrievedContent(
                source_id=source.source_id,
                raw_content={"query": query, "source": source.name},
                content_type="application/json",
                metadata={"retrieved": True},
            ),
        )


class CustomProcessor(ContentProcessor):
    def __init__(self, fail=False):
        self.fail = fail

    async def process(self, content: RetrievedContent) -> Optional[RetrievedContent]:
        if self.fail:
            raise ValueError("Processing failed")
        content.raw_content["processed"] = True
        return content


class TestRetrievalContracts:
    def test_stub_retriever_returns_success(self):
        retriever = StubRetriever()
        source = _make_source()
        result = asyncio.run(retriever.retrieve(source, "test query"))
        assert result.status == RetrievalStatus.SUCCESS
        assert result.content is not None
        assert result.content.source_id == source.source_id
        assert result.content.raw_content["query"] == "test query"

    def test_custom_retriever_failure(self):
        retriever = CustomRetriever(fail_on_source_id="src_fail")
        source = _make_source(source_id="src_fail")
        result = asyncio.run(retriever.retrieve(source, "test"))
        assert result.status == RetrievalStatus.CONNECTION_FAILURE
        assert result.error is not None
        assert result.content is None

    def test_stub_processor_passthrough(self):
        processor = StubProcessor()
        content = RetrievedContent(source_id="src_1", raw_content={"key": "value"})
        result = asyncio.run(processor.process(content))
        assert result is not None
        assert result.raw_content["key"] == "value"

    def test_custom_processor_modifies_content(self):
        processor = CustomProcessor()
        content = RetrievedContent(source_id="src_1", raw_content={"key": "value"})
        result = asyncio.run(processor.process(content))
        assert result is not None
        assert result.raw_content["processed"] is True

    def test_custom_processor_failure(self):
        processor = CustomProcessor(fail=True)
        content = RetrievedContent(source_id="src_1", raw_content={"key": "value"})
        with pytest.raises(ValueError, match="Processing failed"):
            asyncio.run(processor.process(content))


class TestRetrievalOrchestrator:
    def test_retrieve_sources_success(self):
        retriever = StubRetriever()
        orchestrator = RetrievalOrchestrator(retriever=retriever)
        sources = [_make_source(source_id=f"src_{i}") for i in range(3)]
        results = asyncio.run(orchestrator.retrieve_sources(sources, "test"))
        assert len(results) == 3
        assert all(r.status == RetrievalStatus.SUCCESS for r in results)
        assert all(r.content is not None for r in results)

    def test_retrieve_sources_with_failure(self):
        retriever = CustomRetriever(fail_on_source_id="src_fail")
        orchestrator = RetrievalOrchestrator(retriever=retriever)
        source_fail = _make_source(source_id="src_fail")
        source_ok = _make_source(source_id="src_ok")
        results = asyncio.run(orchestrator.retrieve_sources([source_fail, source_ok], "test"))
        assert len(results) == 2
        assert results[0].status == RetrievalStatus.CONNECTION_FAILURE
        assert results[0].content is None
        assert results[1].status == RetrievalStatus.SUCCESS
        assert results[1].content is not None

    def test_process_results_modifies_content(self):
        retriever = StubRetriever()
        processor = CustomProcessor()
        orchestrator = RetrievalOrchestrator(retriever=retriever, processor=processor)
        sources = [_make_source()]
        results = asyncio.run(orchestrator.retrieve_sources(sources, "test"))
        processed = asyncio.run(orchestrator.process_results(results))
        assert len(processed) == 1
        assert processed[0].content.raw_content["processed"] is True

    def test_process_results_without_processor(self):
        retriever = StubRetriever()
        orchestrator = RetrievalOrchestrator(retriever=retriever)
        sources = [_make_source()]
        results = asyncio.run(orchestrator.retrieve_sources(sources, "test"))
        processed = asyncio.run(orchestrator.process_results(results))
        assert processed == results

    def test_retrieval_result_structure(self):
        retriever = StubRetriever()
        source = _make_source()
        result = asyncio.run(retriever.retrieve(source, "test"))
        data = result.to_dict()
        assert "source_id" in data
        assert "status" in data
        assert "content" in data
        assert "duration_ms" in data
        assert "metadata" in data


# ========== RetrievalStage Integration ==========


class TestRetrievalStageIntegration:
    def test_retrieval_stage_with_orchestrator(self):
        from app.research.orchestrator import (
            ResearchOrchestrator,
            PlanningStage,
            DiscoveryStage,
            RetrievalStage,
            ProcessingStage,
            EvidenceCaptureStage,
            StructuringStage,
        )
        from app.research.sources.registry import SourceRegistry
        from app.research.sources.discovery import SourceDiscovery
        from app.research.retrieval.orchestrator import RetrievalOrchestrator
        from app.research.retrieval.stubs import StubRetriever, StubProcessor

        registry = SourceRegistry()
        source = _make_source(source_id="src_1")
        registry.register(SourceRegistration(source=source))
        discovery = SourceDiscovery(registry=registry)
        retrieval_orchestrator = RetrievalOrchestrator(
            retriever=StubRetriever(),
            processor=StubProcessor(),
        )

        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage())
        orchestrator.register_stage(DiscoveryStage(discovery=discovery))
        orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=retrieval_orchestrator, registry=registry))
        orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
        orchestrator.register_stage(EvidenceCaptureStage())
        orchestrator.register_stage(StructuringStage())

        from app.schemas.research import ResearchRequest
        request = ResearchRequest(goal="test", source_preferences=["src_1"])
        result = asyncio.run(orchestrator.execute(request, "req_1"))
        assert result.status == "completed"
        assert "src_1" in result.sources_consulted

    def test_retrieval_stage_isolates_source_failure(self):
        from app.research.orchestrator import (
            ResearchOrchestrator,
            PlanningStage,
            DiscoveryStage,
            RetrievalStage,
            ProcessingStage,
            EvidenceCaptureStage,
            StructuringStage,
        )
        from app.research.sources.registry import SourceRegistry
        from app.research.sources.discovery import SourceDiscovery
        from app.research.retrieval.orchestrator import RetrievalOrchestrator

        registry = SourceRegistry()
        source_ok = _make_source(source_id="src_ok")
        source_fail = _make_source(source_id="src_fail")
        registry.register(SourceRegistration(source=source_ok))
        registry.register(SourceRegistration(source=source_fail))
        discovery = SourceDiscovery(registry=registry)
        retriever = CustomRetriever(fail_on_source_id="src_fail")
        retrieval_orchestrator = RetrievalOrchestrator(retriever=retriever)

        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage())
        orchestrator.register_stage(DiscoveryStage(discovery=discovery))
        orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=retrieval_orchestrator, registry=registry))
        orchestrator.register_stage(ProcessingStage())
        orchestrator.register_stage(EvidenceCaptureStage())
        orchestrator.register_stage(StructuringStage())

        from app.schemas.research import ResearchRequest
        request = ResearchRequest(goal="test", source_preferences=["src_ok", "src_fail"])
        result = asyncio.run(orchestrator.execute(request, "req_2"))
        assert result.status == "partial"
        assert "src_ok" in result.sources_consulted
        assert "src_fail" in result.sources_failed
