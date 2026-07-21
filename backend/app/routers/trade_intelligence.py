from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.routers.auth import get_current_user
from app.schemas.trade_intelligence import (
    AnalysisOutput,
    BuyerAnalysisRequest,
    ComparisonRequest,
    ComparisonOutput,
    ErrorResponse,
    ReportGenerationRequest,
    ReportOutput,
    SupplierAnalysisRequest,
    TrendDetectionRequest,
)
from app.services.trade_intelligence import (
    analyze_buyer,
    analyze_supplier,
    compare_entities,
    detect_trends,
    generate_report,
    perform_analysis,
)

router = APIRouter(prefix="/api/v1/trade-intelligence", tags=["Trade Intelligence"])


def _raise_http_error(result: dict) -> None:
    if not isinstance(result, dict):
        return
    error_code = result.get("error_code")
    if not error_code:
        return
    category = result.get("category", "internal")
    status_map = {
        "not_found": 404,
        "validation": 422,
        "dependency": 503,
        "internal": 500,
        "permission": 403,
    }
    status_code = status_map.get(category, 400)
    raise HTTPException(status_code=status_code, detail=result)


@router.post("/suppliers/analyze", response_model=AnalysisOutput)
async def analyze_supplier_endpoint(
    request: SupplierAnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    result = await analyze_supplier(
        supplier_id=request.supplier_id,
        analysis_type=request.analysis_type,
        date_range=request.date_range if request.date_range else None,
        requested_by=current_user.get("username", "unknown"),
        current_user=current_user,
    )
    _raise_http_error(result)
    return result


@router.post("/buyers/analyze", response_model=AnalysisOutput)
async def analyze_buyer_endpoint(
    request: BuyerAnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    result = await analyze_buyer(
        buyer_id=request.buyer_id,
        analysis_type=request.analysis_type,
        date_range=request.date_range if request.date_range else None,
        requested_by=current_user.get("username", "unknown"),
        current_user=current_user,
    )
    _raise_http_error(result)
    return result


@router.post("/trends/detect", response_model=AnalysisOutput)
async def detect_trends_endpoint(
    request: TrendDetectionRequest,
    current_user: dict = Depends(get_current_user),
):
    result = await detect_trends(
        entity_type=request.entity_type,
        trend_parameters=request.trend_parameters,
        requested_by=current_user.get("username", "unknown"),
        current_user=current_user,
    )
    _raise_http_error(result)
    return result


@router.post("/compare", response_model=ComparisonOutput)
async def compare_entities_endpoint(
    request: ComparisonRequest,
    current_user: dict = Depends(get_current_user),
):
    result = await compare_entities(
        entity_ids=request.entity_ids,
        comparison_criteria=request.comparison_criteria,
        requested_by=current_user.get("username", "unknown"),
        current_user=current_user,
    )
    _raise_http_error(result)
    return result


@router.post("/reports/generate", response_model=ReportOutput)
async def generate_report_endpoint(
    request: ReportGenerationRequest,
    current_user: dict = Depends(get_current_user),
):
    result = await generate_report(
        analysis_ids=request.analysis_ids,
        report_type=request.report_type,
        requested_by=current_user.get("username", "unknown"),
        current_user=current_user,
    )
    _raise_http_error(result)
    return result


@router.post("/perform-analysis")
async def perform_analysis_endpoint(
    parameters: dict,
    current_user: dict = Depends(get_current_user),
    analysis_type: Optional[str] = None,
):
    if not analysis_type:
        raise HTTPException(status_code=422, detail="analysis_type query parameter is required")
    result = await perform_analysis(
        analysis_type=analysis_type,
        parameters=parameters,
        current_user=current_user,
    )
    if isinstance(result, dict) and result.get("error_code"):
        raise HTTPException(status_code=400, detail=result)
    return result
