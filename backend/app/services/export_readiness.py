from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.orchestrator import KnowledgeOrchestrator
from app.agent.llm.provider import llm_registry, LLMProviderRegistry


class ExportReadinessRequest(BaseModel):
    product_id: Optional[int] = Field(default=None, description="Existing product ID")
    hs_code: Optional[str] = Field(default=None, description="HS code for the product")
    product_name: Optional[str] = Field(default=None, description="Product display name")
    target_market: str = Field(description="Target market ISO2 country code")


class ExportReadinessSection(BaseModel):
    title: str
    source: str
    confidence: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
    availability: str = Field(description="available | partial | not_available")
    notes: Optional[str] = None


class ExportReadinessReport(BaseModel):
    report_id: str
    product: Dict[str, Any]
    target_market: str
    sections: List[ExportReadinessSection]
    action_checklist: List[str]
    recommendation: Optional[str] = None
    data_quality_note: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExportReadinessService:
    """Service for Export Readiness Analysis.

    Reuses existing backend capabilities without adding new providers.
    """

    def __init__(
        self,
        knowledge_provider_registry: Optional[KnowledgeProviderRegistry] = None,
        llm_registry_instance: Optional[LLMProviderRegistry] = None,
    ) -> None:
        self._registry = knowledge_provider_registry
        self._llm_registry = llm_registry_instance
        self._orchestrator: Optional[KnowledgeOrchestrator] = None

    def _get_orchestrator(self) -> Optional[KnowledgeOrchestrator]:
        if self._orchestrator is not None:
            return self._orchestrator

        try:
            from main import app
            reasoning_engine = getattr(app.state, "reasoning_engine", None)
            if reasoning_engine is not None:
                orchestrator = getattr(reasoning_engine, "_knowledge_orchestrator", None)
                if orchestrator is not None:
                    self._orchestrator = orchestrator
                    return orchestrator
        except Exception:
            pass

        return None

    async def analyze(
        self,
        request: ExportReadinessRequest,
        user_id: int,
    ) -> ExportReadinessReport:
        from main import knowledge_provider_registry

        registry = self._registry or knowledge_provider_registry
        orchestrator = self._get_orchestrator()
        target_market = request.target_market.upper()
        product_name = request.product_name or request.hs_code or "Unknown product"

        product_summary: Dict[str, Any] = {
            "product_id": request.product_id,
            "hs_code": request.hs_code,
            "name": product_name,
        }

        sections: List[ExportReadinessSection] = []

        # 1) Regulatory Requirements
        regulatory_section = await self._query_regulatory(
            orchestrator=orchestrator,
            registry=registry,
            product_name=product_name,
            target_market=target_market,
        )
        sections.append(regulatory_section)

        # 2) Market Access
        market_access_section = await self._query_market_access(
            orchestrator=orchestrator,
            registry=registry,
            product_name=product_name,
            target_market=target_market,
            hs_code=request.hs_code,
        )
        sections.append(market_access_section)

        # 3) Logistics Profile
        logistics_section = await self._query_logistics(
            registry=registry,
            target_market=target_market,
        )
        sections.append(logistics_section)

        # 4) Historical Trade Context
        trade_context_section = await self._query_trade_context(
            orchestrator=orchestrator,
            registry=registry,
            product_name=product_name,
            target_market=target_market,
        )
        sections.append(trade_context_section)

        # Action checklist
        action_checklist = self._build_action_checklist(sections)

        # Data quality note
        data_quality_note = self._build_data_quality_note(sections)

        # Recommendation via LLM
        recommendation = await self._generate_recommendation(
            product_name=product_name,
            target_market=target_market,
            sections=sections,
        )

        report = ExportReadinessReport(
            report_id=self._generate_report_id(user_id),
            product=product_summary,
            target_market=target_market,
            sections=sections,
            action_checklist=action_checklist,
            recommendation=recommendation,
            data_quality_note=data_quality_note,
        )

        return report

    async def _query_regulatory(
        self,
        orchestrator: Optional[KnowledgeOrchestrator],
        registry: KnowledgeProviderRegistry,
        product_name: str,
        target_market: str,
    ) -> ExportReadinessSection:
        query = f"regulatory requirements {product_name} {target_market}"
        context = {"country": target_market}

        results, source_label = await self._orchestrate_with_fallback(
            orchestrator=orchestrator,
            registry=registry,
            query=query,
            context=context,
            primary_sources=["moaah", "zatca"],
            fallback_sources=["moaah", "zatca", "gccstat"],
        )

        confidence = self._average_confidence(results)

        if results:
            availability = "available" if confidence >= 0.6 else "partial"
        else:
            availability = "not_available"

        return ExportReadinessSection(
            title="Regulatory Requirements",
            source=source_label,
            confidence=confidence,
            data={"results": results} if results else None,
            availability=availability,
            notes=self._regulatory_notes(target_market, results),
        )

    async def _query_market_access(
        self,
        orchestrator: Optional[KnowledgeOrchestrator],
        registry: KnowledgeProviderRegistry,
        product_name: str,
        target_market: str,
        hs_code: Optional[str],
    ) -> ExportReadinessSection:
        query = f"market access duty requirement {product_name} {target_market}"
        context: Dict[str, Any] = {"country": target_market}
        if hs_code:
            context["hs_code"] = hs_code

        results, source_label = await self._orchestrate_with_fallback(
            orchestrator=orchestrator,
            registry=registry,
            query=query,
            context=context,
            primary_sources=["moaah", "zatca", "tradedata"],
            fallback_sources=["moaah", "zatca", "gccstat"],
        )

        confidence = self._average_confidence(results)

        if results:
            availability = "available" if confidence >= 0.6 else "partial"
        else:
            availability = "not_available"

        return ExportReadinessSection(
            title="Market Access Conditions",
            source=source_label,
            confidence=confidence,
            data={"results": results} if results else None,
            availability=availability,
            notes=self._market_access_notes(target_market, results),
        )

    async def _query_logistics(
        self,
        registry: KnowledgeProviderRegistry,
        target_market: str,
    ) -> ExportReadinessSection:
        try:
            result = await registry.query(
                source_id="worldbank-lpi",
                query=f"logistics performance {target_market}",
                context={"country": target_market},
                scope="LP.LPI.OVRL.XQ",
                limit=10,
            )
            results = result.get("results", []) if isinstance(result, dict) else []
            confidence = result.get("confidence") if isinstance(result, dict) else None
        except Exception:
            results = []
            confidence = None

        source_label = "World Bank LPI"
        if results and confidence is not None:
            availability = "available" if confidence >= 0.6 else "partial"
        elif results:
            availability = "available"
        else:
            availability = "not_available"

        return ExportReadinessSection(
            title="Logistics Profile",
            source=source_label,
            confidence=confidence,
            data={"results": results} if results else None,
            availability=availability,
            notes=self._logistics_notes(target_market, results),
        )

    async def _query_trade_context(
        self,
        orchestrator: Optional[KnowledgeOrchestrator],
        registry: KnowledgeProviderRegistry,
        product_name: str,
        target_market: str,
    ) -> ExportReadinessSection:
        query = f"trade statistics export import {product_name} {target_market}"
        context = {"country": target_market, "product": product_name}

        results, source_label = await self._orchestrate_with_fallback(
            orchestrator=orchestrator,
            registry=registry,
            query=query,
            context=context,
            primary_sources=["un-comtrade", "tradedata"],
            fallback_sources=["un-comtrade", "tradedata", "faostat"],
        )

        confidence = self._average_confidence(results)

        if results:
            availability = "available" if confidence >= 0.6 else "partial"
        else:
            availability = "not_available"

        return ExportReadinessSection(
            title="Historical Trade Context",
            source=source_label,
            confidence=confidence,
            data={"results": results} if results else None,
            availability=availability,
            notes=self._trade_context_notes(target_market, results),
        )

    async def _orchestrate_with_fallback(
        self,
        orchestrator: Optional[KnowledgeOrchestrator],
        registry: KnowledgeProviderRegistry,
        query: str,
        context: Dict[str, Any],
        primary_sources: List[str],
        fallback_sources: List[str],
    ) -> tuple[list[Dict[str, Any]], str]:
        if orchestrator is not None:
            try:
                result = await orchestrator.orchestrate(
                    query=query,
                    context=context,
                    sources=primary_sources,
                    limit=10,
                )
                results = result.get("results", [])
                if results:
                    return results, ", ".join(primary_sources)
            except Exception:
                pass

            try:
                result = await orchestrator.orchestrate(
                    query=query,
                    context=context,
                    sources=fallback_sources,
                    limit=10,
                )
                results = result.get("results", [])
                if results:
                    return results, ", ".join(fallback_sources)
            except Exception:
                pass

        return [], "none"

    def _average_confidence(self, results: List[Dict[str, Any]]) -> Optional[float]:
        if not results:
            return None
        confidences = [r.get("confidence") for r in results if isinstance(r, dict) and r.get("confidence") is not None]
        if not confidences:
            return None
        return sum(confidences) / len(confidences)

    async def _generate_recommendation(
        self,
        product_name: str,
        target_market: str,
        sections: List[ExportReadinessSection],
    ) -> Optional[str]:
        provider = self._llm_registry.get_provider("gemini") if self._llm_registry else None
        if provider is None:
            try:
                from main import llm_registry as global_llm_registry
                provider = global_llm_registry.get_provider("gemini")
            except Exception:
                provider = None

        if provider is None:
            return None

        available_sections = [s.title for s in sections if s.availability != "not_available"]
        unavailable_sections = [s.title for s in sections if s.availability == "not_available"]

        prompt = (
            f"Product: {product_name}\n"
            f"Target market: {target_market}\n\n"
            f"Available intelligence sections: {', '.join(available_sections) if available_sections else 'None'}\n"
            f"Unavailable sections: {', '.join(unavailable_sections) if unavailable_sections else 'None'}\n\n"
            "Generate a concise recommendation for the user about exporting this product to this market. "
            "Focus on actionable next steps based on the available data. "
            "If critical data is missing, mention what the user should verify manually."
        )

        system_prompt = (
            "You are an export intelligence assistant. "
            "Provide concise, actionable recommendations for Egyptian exporters. "
            "Do not make up data. If information is missing, say so explicitly."
        )

        try:
            response = await provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                parameters={"temperature": 0.3, "max_output_tokens": 512},
            )
            content = response.content or None
            if content and content.strip():
                return content.strip()
        except RuntimeError:
            pass
        except Exception:
            pass

        return None

    def _build_action_checklist(self, sections: List[ExportReadinessSection]) -> List[str]:
        checklist: List[str] = []

        section_map = {s.title: s for s in sections}

        if "Regulatory Requirements" in section_map:
            if section_map["Regulatory Requirements"].availability == "available":
                checklist.append("Review regulatory requirements from the selected providers.")
            else:
                checklist.append("Verify regulatory requirements manually for the target market.")

        if "Market Access Conditions" in section_map:
            if section_map["Market Access Conditions"].availability == "available":
                checklist.append("Check tariff rates and market access conditions.")
            else:
                checklist.append("Confirm market access conditions manually with the target market authorities.")

        if "Logistics Profile" in section_map:
            if section_map["Logistics Profile"].availability == "available":
                checklist.append("Assess logistics performance and plan shipping accordingly.")
            else:
                checklist.append("Validate logistics options and shipping costs with carriers.")

        if "Historical Trade Context" in section_map:
            if section_map["Historical Trade Context"].availability == "available":
                checklist.append("Review historical trade patterns for this product-market pair.")
            else:
                checklist.append("Research trade history and market demand through alternative sources.")

        checklist.append("Prepare required documentation for export compliance.")
        checklist.append("Confirm commercial and financial terms with the buyer.")

        return checklist

    def _build_data_quality_note(self, sections: List[ExportReadinessSection]) -> str:
        unavailable = [s.title for s in sections if s.availability == "not_available"]
        partial = [s.title for s in sections if s.availability == "partial"]

        notes: List[str] = []
        if unavailable:
            notes.append(f"Unavailable sections: {', '.join(unavailable)}. Manual verification required.")
        if partial:
            notes.append(f"Partial data in: {', '.join(partial)}. Use with caution.")
        if not notes:
            notes.append("All sections populated from available sources. Verify details before execution.")

        return " ".join(notes)

    def _regulatory_notes(self, target_market: str, results: List[Dict[str, Any]]) -> Optional[str]:
        if not results:
            return f"No regulatory data returned for {target_market} from selected providers."
        return None

    def _market_access_notes(self, target_market: str, results: List[Dict[str, Any]]) -> Optional[str]:
        if not results:
            return f"No market access data returned for {target_market} from selected providers."
        return None

    def _logistics_notes(self, target_market: str, results: List[Dict[str, Any]]) -> Optional[str]:
        if not results:
            return f"No logistics data returned for {target_market} from World Bank LPI."
        return None

    def _trade_context_notes(self, target_market: str, results: List[Dict[str, Any]]) -> Optional[str]:
        if not results:
            return f"No trade history returned for {target_market} from selected providers."
        return None

    def _generate_report_id(self, user_id: int) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"export-readiness-{user_id}-{timestamp}"
