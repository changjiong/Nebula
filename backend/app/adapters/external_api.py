"""
External API Adapter Module

Provides adapter for connecting to external APIs (外部数据接口).
Includes adapters for business registration data, credit reports, etc.
"""

import logging
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.adapters.base import (
    AdapterConfig,
    AdapterError,
    AdapterRequest,
    HTTPAdapter,
)

logger = logging.getLogger(__name__)


class DataSource(str, Enum):
    """External data sources"""
    BUSINESS_REGISTRATION = "business_registration"  # 工商数据
    CREDIT_REPORT = "credit_report"  # 征信报告
    COURT_RECORDS = "court_records"  # 法院公告
    TAX_RECORDS = "tax_records"  # 税务数据
    SOCIAL_INSURANCE = "social_insurance"  # 社保数据


class QueryStatus(str, Enum):
    """Query status"""
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class CompanyInfo(BaseModel):
    """Company basic information from business registration"""
    company_id: str = Field(..., description="Unified social credit code")
    name: str = Field(..., description="Company name")
    legal_representative: str | None = None
    registered_capital: str | None = None
    establishment_date: str | None = None
    status: str | None = None
    company_type: str | None = None
    address: str | None = None
    business_scope: str | None = None
    industry: str | None = None


class CreditReport(BaseModel):
    """Credit report summary"""
    company_id: str
    company_name: str
    credit_score: int | None = None
    credit_rating: str | None = None
    overdue_count: int = 0
    total_debt: float = 0
    report_date: str | None = None
    risk_level: str | None = None


class CourtRecord(BaseModel):
    """Court record information"""
    case_id: str
    company_id: str
    case_type: str | None = None
    court_name: str | None = None
    filing_date: str | None = None
    status: str | None = None
    amount_involved: float | None = None


class ExternalAPIConfig(AdapterConfig):
    """External API specific configuration"""
    api_key: str = ""
    rate_limit_per_minute: int = 60
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600


# Mock Data
MOCK_COMPANIES: dict[str, CompanyInfo] = {
    "91110000100000001A": CompanyInfo(
        company_id="91110000100000001A",
        name="北京示例科技有限公司",
        legal_representative="张三",
        registered_capital="1000万人民币",
        establishment_date="2015-03-15",
        status="存续",
        company_type="有限责任公司",
        address="北京市海淀区中关村大街1号",
        business_scope="技术开发、技术咨询、技术服务",
        industry="科技推广和应用服务业",
    ),
    "91310000200000002B": CompanyInfo(
        company_id="91310000200000002B",
        name="上海金融服务有限公司",
        legal_representative="李四",
        registered_capital="5000万人民币",
        establishment_date="2010-08-20",
        status="存续",
        company_type="有限责任公司",
        address="上海市浦东新区陆家嘴金融中心",
        business_scope="金融信息服务、投资咨询",
        industry="金融业",
    ),
}

MOCK_CREDIT_REPORTS: dict[str, CreditReport] = {
    "91110000100000001A": CreditReport(
        company_id="91110000100000001A",
        company_name="北京示例科技有限公司",
        credit_score=780,
        credit_rating="AA",
        overdue_count=0,
        total_debt=500000,
        report_date="2024-03-01",
        risk_level="低",
    ),
    "91310000200000002B": CreditReport(
        company_id="91310000200000002B",
        company_name="上海金融服务有限公司",
        credit_score=850,
        credit_rating="AAA",
        overdue_count=0,
        total_debt=2000000,
        report_date="2024-03-01",
        risk_level="低",
    ),
}


class ExternalAPIAdapter(HTTPAdapter):
    """
    External API Adapter (外部数据接口适配器)

    Provides unified interface for:
    - Business registration data (工商数据)
    - Credit reports (征信报告)
    - Court records (法院公告)

    Usage:
        adapter = ExternalAPIAdapter(ExternalAPIConfig(mock_mode=True))
        company = adapter.get_company_info("91110000100000001A")
        credit = adapter.get_credit_report("91110000100000001A")
    """

    def __init__(self, config: ExternalAPIConfig | None = None):
        super().__init__(config or ExternalAPIConfig())
        self._ext_config: ExternalAPIConfig = self.config  # type: ignore

    def _build_headers(self) -> dict[str, str]:
        """Build headers with API key"""
        headers = super()._build_headers()
        if self._ext_config.api_key:
            headers["X-API-Key"] = self._ext_config.api_key
        return headers

    # Business Registration APIs
    def get_company_info(self, company_id: str) -> CompanyInfo | None:
        """Get company information by unified social credit code."""
        if self.config.mock_mode:
            logger.info(f"[ExternalAPI] Mock company lookup: {company_id}")
            return MOCK_COMPANIES.get(company_id)

        response = self.call(AdapterRequest(
            endpoint=f"/api/v1/business/company/{company_id}",
            method="GET",
        ))
        return CompanyInfo(**response.data) if response.data else None

    async def async_get_company_info(self, company_id: str) -> CompanyInfo | None:
        """Async version of get_company_info"""
        if self.config.mock_mode:
            return MOCK_COMPANIES.get(company_id)
        response = await self.async_call(AdapterRequest(
            endpoint=f"/api/v1/business/company/{company_id}",
            method="GET",
        ))
        return CompanyInfo(**response.data) if response.data else None

    def search_companies(self, keyword: str, limit: int = 10) -> list[CompanyInfo]:
        """Search companies by keyword."""
        if self.config.mock_mode:
            results = [c for c in MOCK_COMPANIES.values() if keyword.lower() in c.name.lower()]
            return results[:limit]

        response = self.call(AdapterRequest(
            endpoint="/api/v1/business/search",
            method="GET",
            params={"q": keyword, "limit": limit},
        ))
        return [CompanyInfo(**c) for c in (response.data or [])]

    async def async_search_companies(self, keyword: str, limit: int = 10) -> list[CompanyInfo]:
        """Async version of search_companies"""
        if self.config.mock_mode:
            results = [c for c in MOCK_COMPANIES.values() if keyword.lower() in c.name.lower()]
            return results[:limit]
        response = await self.async_call(AdapterRequest(
            endpoint="/api/v1/business/search",
            method="GET",
            params={"q": keyword, "limit": limit},
        ))
        return [CompanyInfo(**c) for c in (response.data or [])]

    # Credit Report APIs
    def get_credit_report(self, company_id: str) -> CreditReport | None:
        """Get credit report for a company."""
        if self.config.mock_mode:
            logger.info(f"[ExternalAPI] Mock credit report: {company_id}")
            return MOCK_CREDIT_REPORTS.get(company_id)

        response = self.call(AdapterRequest(
            endpoint=f"/api/v1/credit/report/{company_id}",
            method="GET",
        ))
        return CreditReport(**response.data) if response.data else None

    async def async_get_credit_report(self, company_id: str) -> CreditReport | None:
        """Async version of get_credit_report"""
        if self.config.mock_mode:
            return MOCK_CREDIT_REPORTS.get(company_id)
        response = await self.async_call(AdapterRequest(
            endpoint=f"/api/v1/credit/report/{company_id}",
            method="GET",
        ))
        return CreditReport(**response.data) if response.data else None

    # Court Records APIs
    def get_court_records(self, company_id: str) -> list[CourtRecord]:
        """Get court records for a company."""
        if self.config.mock_mode:
            return [
                CourtRecord(
                    case_id=f"case-{uuid4().hex[:8]}",
                    company_id=company_id,
                    case_type="民事",
                    court_name="北京市海淀区人民法院",
                    filing_date="2023-06-15",
                    status="已结案",
                    amount_involved=50000,
                )
            ] if company_id in MOCK_COMPANIES else []

        response = self.call(AdapterRequest(
            endpoint=f"/api/v1/court/records/{company_id}",
            method="GET",
        ))
        return [CourtRecord(**r) for r in (response.data or [])]

    async def async_get_court_records(self, company_id: str) -> list[CourtRecord]:
        """Async version of get_court_records"""
        if self.config.mock_mode:
            return [
                CourtRecord(
                    case_id=f"case-{uuid4().hex[:8]}",
                    company_id=company_id,
                    case_type="民事",
                    court_name="北京市海淀区人民法院",
                    filing_date="2023-06-15",
                    status="已结案",
                )
            ] if company_id in MOCK_COMPANIES else []
        response = await self.async_call(AdapterRequest(
            endpoint=f"/api/v1/court/records/{company_id}",
            method="GET",
        ))
        return [CourtRecord(**r) for r in (response.data or [])]

    # Batch Operations
    def batch_get_company_info(self, company_ids: list[str]) -> dict[str, CompanyInfo | None]:
        """Batch get company information."""
        if self.config.mock_mode:
            return {cid: MOCK_COMPANIES.get(cid) for cid in company_ids}

        response = self.call(AdapterRequest(
            endpoint="/api/v1/business/batch",
            method="POST",
            body={"company_ids": company_ids},
        ))
        if response.error:
            raise AdapterError(f"Batch lookup failed: {response.error}")
        result: dict[str, CompanyInfo | None] = {}
        for cid, data in (response.data or {}).items():
            result[cid] = CompanyInfo(**data) if data else None
        return result

    # Health Check
    def health_check(self) -> dict[str, Any]:
        """Check External API service health."""
        if self.config.mock_mode:
            return {"status": "healthy", "sources": list(DataSource), "mock_mode": True}
        response = self.call(AdapterRequest(endpoint="/api/v1/health", method="GET"))
        return {"status": "healthy" if not response.error else "unhealthy", "latency_ms": response.latency_ms}
