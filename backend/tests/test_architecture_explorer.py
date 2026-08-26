import json
import os
import tempfile
from pathlib import Path

import pytest

from app.architecture_explorer.engine import ArchitectureExplorerEngine
from app.architecture_explorer.exceptions import (
    ExplorerEngineError,
    GraphNotLoadedError,
    NodeNotFoundError,
    QueryValidationError,
)
from app.architecture_explorer.loader import (
    CanonicalGraphLoadError,
    CanonicalGraphValidationError,
)
from app.architecture_explorer.models import (
    CanonicalGraph,
    CanonicalNode,
    EdgeQuery,
    LevelProjection,
    NodeQuery,
    SearchResult,
    TraversalResult,
)


REAL_GRAPH_PATH = Path(__file__).parent.parent.parent / "docs" / "الخريطة المعمارية الكاملة" / "ARCHITECTURE_EXPLORER_V2_CANONICAL_GRAPH.json"


@pytest.fixture(scope="module")
def engine() -> ArchitectureExplorerEngine:
    engine = ArchitectureExplorerEngine(graph_path=str(REAL_GRAPH_PATH))
    engine.load()
    return engine


def _minimal_graph_dict(**overrides):
    data = {
        "artifact": "TEST_GRAPH",
        "version": "0.0-test",
        "purpose": "test",
        "governing_principle": "test",
        "source": {"repository": "test", "branch": "test"},
        "levels": [{"id": "L0", "name": "A", "arabic_meaning": "أ"}, {"id": "L1", "name": "B", "arabic_meaning": "ب"}],
        "nodes": [
            {
                "id": "root",
                "technical_name": "Root",
                "arabic_meaning": "جذر",
                "type": "platform",
                "levels": [0, 1],
                "status": "architectural_root",
                "paths": [],
                "responsibilities": ["R1"],
                "non_responsibilities": ["NR1"],
                "evidence": ["docs/foo.md"],
                "parent_ids": [],
                "tags": ["root"],
                "metadata": {},
            },
            {
                "id": "child_a",
                "technical_name": "Child A",
                "arabic_meaning": "طفل أ",
                "type": "service",
                "levels": [1],
                "status": "implemented_runtime",
                "paths": ["backend/app/services/a.py"],
                "responsibilities": ["RA"],
                "non_responsibilities": ["NRA"],
                "evidence": ["backend/app/services/a.py"],
                "parent_ids": ["root"],
                "tags": ["a"],
                "metadata": {},
            },
            {
                "id": "child_b",
                "technical_name": "Child B",
                "arabic_meaning": "طفل ب",
                "type": "service",
                "levels": [1],
                "status": "implemented_runtime",
                "paths": ["backend/app/services/b.py"],
                "responsibilities": ["RB"],
                "non_responsibilities": ["NRB"],
                "evidence": ["backend/app/services/b.py"],
                "parent_ids": ["root"],
                "tags": ["b"],
                "metadata": {},
            },
        ],
        "edges": [
            {
                "id": "e1",
                "source": "root",
                "target": "child_a",
                "relation_type": "contains",
                "direction": "outbound",
                "status": "architectural",
                "evidence": ["docs/foo.md"],
                "data": {},
                "metadata": {},
            },
            {
                "id": "e2",
                "source": "root",
                "target": "child_b",
                "relation_type": "uses",
                "direction": "outbound",
                "status": "verified",
                "evidence": ["backend/app/services/b.py"],
                "data": {},
                "metadata": {},
            },
        ],
        "agent_runtime_path": {"sequence": [], "evidence": [], "note": ""},
        "classification_rules": {},
        "graph_contract": {},
        "validation": {"state": "test", "validated_domains": [], "remaining_domains": []},
        "next_work": "",
    }
    data.update(overrides)
    return data


class TestCanonicalGraphLoader:
    def test_load_real_graph_success(self):
        loader = ArchitectureExplorerEngine(graph_path=str(REAL_GRAPH_PATH))._loader
        graph = loader.load()
        assert isinstance(graph, CanonicalGraph)
        assert graph.version == "1.2-canonical-graph-evidence"
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0

    def test_load_missing_file_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
            tmp.close()
            missing = tmp.name + ".missing"
        loader = ArchitectureExplorerEngine(graph_path=missing)._loader
        with pytest.raises(CanonicalGraphLoadError):
            loader.load()

    def test_invalid_json_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write("{not valid json")
            tmp_path = tmp.name
        try:
            loader = ArchitectureExplorerEngine(graph_path=tmp_path)._loader
            with pytest.raises(CanonicalGraphLoadError):
                loader.load()
        finally:
            os.remove(tmp_path)

    def test_missing_required_keys_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as tmp:
            json.dump({"artifact": "X"}, tmp)
            tmp_path = tmp.name
        try:
            loader = ArchitectureExplorerEngine(graph_path=tmp_path)._loader
            with pytest.raises(CanonicalGraphValidationError):
                loader.load()
        finally:
            os.remove(tmp_path)

    def test_empty_nodes_raises(self):
        data = _minimal_graph_dict(nodes=[])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as tmp:
            json.dump(data, tmp)
            tmp_path = tmp.name
        try:
            loader = ArchitectureExplorerEngine(graph_path=tmp_path)._loader
            with pytest.raises(CanonicalGraphValidationError):
                loader.load()
        finally:
            os.remove(tmp_path)

    def test_duplicate_node_ids_raises(self):
        data = _minimal_graph_dict(nodes=[
            _minimal_graph_dict()["nodes"][0],
            {**_minimal_graph_dict()["nodes"][0], "id": "root"},
        ])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as tmp:
            json.dump(data, tmp)
            tmp_path = tmp.name
        try:
            loader = ArchitectureExplorerEngine(graph_path=tmp_path)._loader
            with pytest.raises(CanonicalGraphValidationError):
                loader.load()
        finally:
            os.remove(tmp_path)

    def test_duplicate_edge_ids_raises(self):
        data = _minimal_graph_dict(edges=[_minimal_graph_dict()["edges"][0], _minimal_graph_dict()["edges"][0]])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as tmp:
            json.dump(data, tmp)
            tmp_path = tmp.name
        try:
            loader = ArchitectureExplorerEngine(graph_path=tmp_path)._loader
            with pytest.raises(CanonicalGraphValidationError):
                loader.load()
        finally:
            os.remove(tmp_path)

    def test_missing_edge_source_raises(self):
        data = _minimal_graph_dict(edges=[{**_minimal_graph_dict()["edges"][0], "source": "missing"}])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as tmp:
            json.dump(data, tmp)
            tmp_path = tmp.name
        try:
            loader = ArchitectureExplorerEngine(graph_path=tmp_path)._loader
            with pytest.raises(CanonicalGraphValidationError):
                loader.load()
        finally:
            os.remove(tmp_path)

    def test_missing_edge_target_raises(self):
        data = _minimal_graph_dict(edges=[{**_minimal_graph_dict()["edges"][0], "target": "missing"}])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as tmp:
            json.dump(data, tmp)
            tmp_path = tmp.name
        try:
            loader = ArchitectureExplorerEngine(graph_path=tmp_path)._loader
            with pytest.raises(CanonicalGraphValidationError):
                loader.load()
        finally:
            os.remove(tmp_path)


class TestArchitectureExplorerEngine:
    def test_get_node_success(self, engine: ArchitectureExplorerEngine):
        node = engine.get_node("digital_export_manager")
        assert node.id == "digital_export_manager"
        assert node.technical_name == "Digital Export Manager"

    def test_get_node_not_found(self, engine: ArchitectureExplorerEngine):
        with pytest.raises(NodeNotFoundError):
            engine.get_node("does_not_exist")

    def test_get_children(self, engine: ArchitectureExplorerEngine):
        children = engine.get_children("digital_export_manager")
        assert len(children) > 0
        assert all(c.id in {child.id for child in children} for c in children)

    def test_get_parents(self, engine: ArchitectureExplorerEngine):
        parents = engine.get_parents("reasoning")
        assert len(parents) > 0
        assert any(parent.id == "cognitive" for parent in parents)

    def test_query_nodes_by_id(self, engine: ArchitectureExplorerEngine):
        results = engine.query_nodes(NodeQuery(node_id="digital_export_manager"))
        assert len(results) == 1
        assert results[0].id == "digital_export_manager"

    def test_query_nodes_by_type(self, engine: ArchitectureExplorerEngine):
        results = engine.query_nodes(NodeQuery(type="agent_subsystem"))
        assert len(results) > 0

    def test_query_nodes_by_status(self, engine: ArchitectureExplorerEngine):
        results = engine.query_nodes(NodeQuery(status="implemented_runtime"))
        assert len(results) > 0

    def test_query_nodes_by_level(self, engine: ArchitectureExplorerEngine):
        results = engine.query_nodes(NodeQuery(level=2))
        assert len(results) > 0

    def test_query_nodes_by_tag(self, engine: ArchitectureExplorerEngine):
        results = engine.query_nodes(NodeQuery(tag="tool-orchestration"))
        assert len(results) > 0

    def test_query_nodes_by_parent_id(self, engine: ArchitectureExplorerEngine):
        results = engine.query_nodes(NodeQuery(parent_id="cognitive"))
        assert len(results) > 0

    def test_query_nodes_search_english(self, engine: ArchitectureExplorerEngine):
        results = engine.query_nodes(NodeQuery(search_text="Tool"))
        assert len(results) > 0

    def test_query_nodes_search_arabic(self, engine: ArchitectureExplorerEngine):
        results = engine.query_nodes(NodeQuery(search_text="طبقة"))
        assert len(results) > 0

    def test_query_nodes_search_repository_path(self):
        engine = ArchitectureExplorerEngine(graph_path=str(REAL_GRAPH_PATH))
        engine.load()
        results = engine.query_nodes(NodeQuery(search_text="execution_engine/orchestrator.py"))
        assert len(results) > 0

    def test_query_nodes_combined_filters(self, engine: ArchitectureExplorerEngine):
        results = engine.query_nodes(NodeQuery(type="orchestrator", status="implemented_runtime", level=2))
        assert len(results) > 0
        for node in results:
            assert node.type == "orchestrator"
            assert node.status == "implemented_runtime"
            assert 2 in node.levels

    def test_query_edges_by_source(self, engine: ArchitectureExplorerEngine):
        results = engine.query_edges(EdgeQuery(source="digital_export_manager"))
        assert len(results) > 0

    def test_query_edges_by_status(self, engine: ArchitectureExplorerEngine):
        results = engine.query_edges(EdgeQuery(status="verified_runtime"))
        assert len(results) > 0

    def test_outbound_traversal(self, engine: ArchitectureExplorerEngine):
        paths = engine.traverse("digital_export_manager", direction="outbound", max_depth=2)
        assert len(paths) > 0
        assert all(isinstance(p, TraversalResult) for p in paths)
        assert all(p.start_node.id == "digital_export_manager" for p in paths)

    def test_inbound_traversal(self, engine: ArchitectureExplorerEngine):
        paths = engine.traverse("tool_orchestrator", direction="inbound", max_depth=2)
        assert len(paths) > 0

    def test_traversal_relation_filter(self, engine: ArchitectureExplorerEngine):
        paths_all = engine.traverse("digital_export_manager", direction="outbound", max_depth=1)
        paths_filtered = engine.traverse("digital_export_manager", direction="outbound", max_depth=1, relation_filter="uses")
        assert len(paths_filtered) <= len(paths_all)

    def test_search_english(self, engine: ArchitectureExplorerEngine):
        result = engine.search("tool")
        assert isinstance(result, SearchResult)
        assert result.total > 0
        assert result.query == "tool"

    def test_search_arabic(self, engine: ArchitectureExplorerEngine):
        result = engine.search("طبقة")
        assert result.total > 0

    def test_search_limit(self, engine: ArchitectureExplorerEngine):
        result = engine.search("tool", limit=1)
        assert result.total >= 1
        assert len(result.matches) <= 1

    def test_level_projections(self, engine: ArchitectureExplorerEngine):
        for level in range(4):
            projection = engine.project_level(level)
            assert isinstance(projection, LevelProjection)
            assert projection.level == level
            assert len(projection.nodes) > 0
            for node in projection.nodes:
                assert level in node.levels

    def test_l0_projection_contains_root(self, engine: ArchitectureExplorerEngine):
        projection = engine.project_level(0)
        assert any(node.id == "intelligent_operating_platform" for node in projection.nodes)

    def test_l1_projection_contains_dem(self, engine: ArchitectureExplorerEngine):
        projection = engine.project_level(1)
        assert any(node.id == "digital_export_manager" for node in projection.nodes)

    def test_l2_projection_contains_cognitive(self, engine: ArchitectureExplorerEngine):
        projection = engine.project_level(2)
        assert any(node.id == "cognitive" for node in projection.nodes)

    def test_l3_projection_contains_planner(self, engine: ArchitectureExplorerEngine):
        projection = engine.project_level(3)
        assert any(node.id == "task_planner" for node in projection.nodes)

    def test_evidence_resolution(self, engine: ArchitectureExplorerEngine):
        evidence = engine.resolve_evidence("tool_orchestrator")
        assert "node" in evidence
        assert "evidence_paths" in evidence
        assert "supporting_edges" in evidence
        assert isinstance(evidence["evidence_paths"], list)
        assert len(evidence["evidence_paths"]) > 0

    def test_engine_does_not_modify_graph(self, engine: ArchitectureExplorerEngine):
        original_nodes = len(engine.graph.nodes)
        original_edges = len(engine.graph.edges)
        engine.query_nodes(NodeQuery(status="implemented_runtime"))
        engine.traverse("digital_export_manager", max_depth=2)
        engine.search("test")
        engine.project_level(0)
        engine.resolve_evidence("digital_export_manager")
        assert len(engine.graph.nodes) == original_nodes
        assert len(engine.graph.edges) == original_edges

    def test_get_node_evidence(self, engine: ArchitectureExplorerEngine):
        evidence = engine.get_node_evidence("digital_export_manager")
        assert isinstance(evidence, list)
        assert len(evidence) > 0

    def test_get_edge_evidence(self, engine: ArchitectureExplorerEngine):
        evidence = engine.get_edge_evidence("e02")
        assert isinstance(evidence, list)
        assert len(evidence) > 0

    def test_get_agent_runtime_path(self, engine: ArchitectureExplorerEngine):
        path = engine.get_agent_runtime_path()
        assert isinstance(path, list)
        assert len(path) > 0

    def test_get_artifact_metadata(self, engine: ArchitectureExplorerEngine):
        metadata = engine.get_artifact_metadata()
        assert metadata["artifact"] == "ARCHITECTURE_EXPLORER_V2_CANONICAL_GRAPH"
        assert metadata["version"] == "1.2-canonical-graph-evidence"

    def test_to_dict_returns_full_graph(self, engine: ArchitectureExplorerEngine):
        data = engine.to_dict()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == len(engine.graph.nodes)
        assert len(data["edges"]) == len(engine.graph.edges)

    def test_graph_not_loaded_error(self):
        engine = ArchitectureExplorerEngine(graph_path=str(REAL_GRAPH_PATH))
        with pytest.raises(GraphNotLoadedError):
            _ = engine.graph
