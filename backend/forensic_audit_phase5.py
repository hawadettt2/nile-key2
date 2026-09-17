import asyncio
import json
from app.research.query_planner import ResearchQueryPlanner
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.research.orchestrator import ResearchOrchestrator, PlanningStage, DiscoveryStage, RetrievalStage, ProcessingStage, EvidenceCaptureStage, StructuringStage, VerificationStage
from app.research.retrieval.contracts import RetrievedContent, RetrievalResult, RetrievalStatus, SourceRetriever
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.evidence.contracts import DefaultEvidenceCapture
from app.research.result import DefaultResultStructurer
from app.research.retrieval.stubs import StubProcessor
from app.agent.business_intelligence.synthesizer import BusinessIntelligenceSynthesizer
from app.agent.business_intelligence.derivers import EntityDeriver, OpportunityDeriver, RiskDeriver
from app.schemas.research import ResearchRequest, Source, SourceRegistration

class ScenarioRetriever(SourceRetriever):
    async def retrieve(self, source, query, context=None, scope=None):
        if source.source_id == 'un-comtrade':
            raw_content = {'data': [{'reporterCode': '818', 'reporterDesc': 'Egypt', 'partnerCode': '400', 'partnerDesc': 'Jordan', 'flowCode': 'X', 'cmdCode': '07', 'cmdDesc': 'Vegetables', 'refYear': 2025, 'fobvalue': 28496743.65, 'isReported': True}]}
        elif source.source_id == 'regulations':
            raw_content = {'results': [{'id': 'reg-1', 'title': 'Jordan Import Requirements', 'content': 'Strict pesticide residue limits apply. Import permits required.', 'country': 'Jordan', 'category': 'SPS', 'source_url': 'https://example.com/regs', 'confidence': 0.9}]}
        elif source.source_id == 'faostat':
            raw_content = {'results': [{'id': 'fao-1', 'title': 'Egypt Agricultural Export Conditions', 'content': 'Egypt vegetable exports show growing demand in Jordan market.', 'country': 'Egypt', 'category': 'agrifood', 'source_url': 'https://example.com/faostat', 'confidence': 0.85}]}
        else:
            raw_content = {'results': []}
        return RetrievalResult(source_id=source.source_id, status=RetrievalStatus.SUCCESS, content=RetrievedContent(source_id=source.source_id, raw_content=raw_content, content_type='application/json', metadata={'query': query, 'scope': scope or {}}))

def make_registry():
    registry = SourceRegistry()
    registry.register(SourceRegistration(source=Source(source_id='un-comtrade', name='UN Comtrade', source_type='external_trade_intelligence', reference='https://comtrade.un.org', metadata={'capabilities': ['trade_intelligence', 'market_opportunity']}, status='active')))
    registry.register(SourceRegistration(source=Source(source_id='regulations', name='Regulations Knowledge', source_type='regulation', reference='https://example.com/regs', metadata={'capabilities': ['market_access', 'regulatory_sps_tbt', 'rules_of_origin']}, status='active')))
    registry.register(SourceRegistration(source=Source(source_id='faostat', name='FAOSTAT', source_type='external_agrifood_intelligence', reference='https://fao.org', metadata={'capabilities': ['agrifood_intelligence', 'market_opportunity']}, status='active')))
    return registry

async def main():
    registry = make_registry()
    retriever = ScenarioRetriever()
    retrieval_orchestrator = RetrievalOrchestrator(retriever=retriever)
    
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(PlanningStage(planner=ResearchQueryPlanner()))
    orchestrator.register_stage(DiscoveryStage(discovery=SourceDiscovery(registry)))
    orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=retrieval_orchestrator, registry=registry))
    orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
    orchestrator.register_stage(EvidenceCaptureStage(registry=registry, capture=DefaultEvidenceCapture()))
    orchestrator.register_stage(StructuringStage(structurer=DefaultResultStructurer()))
    orchestrator.register_stage(VerificationStage())
    
    goal = 'اريد تصدير الخضروات والفاكهة المصرية الى الاردن'
    result = await orchestrator.execute(ResearchRequest(goal=goal, context={}, scope={}), 'forensic-audit')
    
    synthesizer = BusinessIntelligenceSynthesizer()
    answer = await synthesizer.synthesize(
        mission=type('Mission', (), {'result': {}, 'goal': None})(),
        research_result=result.model_dump(mode='json'),
    )
    
    print('=== EVIDENCE AUDIT ===')
    print('Research findings count:', len(result.findings))
    for f in result.findings:
        dim = f.metadata.get('dimension') if f.metadata else 'unknown'
        print(f'  [{dim}] {f.topic}: {f.content[:60]}...')
        print(f'    Evidence: {len(f.evidence)} items')
        for e in f.evidence:
            print(f'      - source_id={e.source_id}, excerpt={e.content_excerpt[:40]}...')
    print()
    
    print('=== BI OUTPUT AUDIT ===')
    print('Key findings:', len(answer.key_findings))
    for f in answer.key_findings:
        print(f'  [{f.topic[:30]}]: {f.content[:60]}...')
        print(f'    Evidence: {len(f.evidence)} items')
        for e in f.evidence:
            print(f'      - source_id={e.source_id}, excerpt={e.content_excerpt[:40]}...')
    print()
    
    print('=== ENTITIES AUDIT ===')
    for e in answer.entities:
        print(f'  Entity: {e.name} (type={e.entity_type})')
        print(f'    Evidence: {len(e.evidence)} items')
        for ev in e.evidence:
            print(f'      - source_id={ev.source_id}, excerpt={ev.content_excerpt[:40]}...')
    print()
    
    print('=== OPPORTUNITIES AUDIT ===')
    for o in answer.opportunities:
        print(f'  Opportunity: {o.description[:60]}...')
        print(f'    Evidence: {len(o.evidence)} items')
        for e in o.evidence:
            print(f'      - source_id={e.source_id}, excerpt={e.content_excerpt[:40]}...')
    print()
    
    print('=== RISKS AUDIT ===')
    for r in answer.risks:
        print(f'  Risk: {r.description[:60]}...')
        print(f'    Evidence: {len(r.evidence)} items')
        for e in r.evidence:
            print(f'      - source_id={e.source_id}, excerpt={e.content_excerpt[:40]}...')
    print()
    
    print('=== COVERAGE AUDIT ===')
    coverage = answer.provenance.get('coverage', {})
    print('Coverage level:', coverage.get('coverage_level'))
    print('Successful sources:', coverage.get('successful_sources'))
    print('Failed sources:', coverage.get('failed_sources'))
    print('Dimensions covered:', answer.provenance.get('dimensions_covered'))
    print('Unsupported dimensions:', coverage.get('unsupported_dimensions'))
    print('Entries:')
    for entry in coverage.get('entries', []):
        dim = entry.get('dimension')
        source_id = entry.get('source_id')
        status = entry.get('status')
        evidence_count = entry.get('evidence_count')
        print(f'  - {dim} | source={source_id} | status={status} | evidence_count={evidence_count}')

if __name__ == '__main__':
    asyncio.run(main())
