"""
ETA Engine Pydantic Schemas
- Invoice schemas matching ETA Schema v1.0
- Receipt schemas matching ETA Receipt Schema v1.2
"""

from pydantic import BaseModel, Field, validator, confloat, conint
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import re


# ========== Common Types ==========

class IssuerAddress(BaseModel):
    branchId: str
    country: str = "EG"
    governate: str
    regionCity: str
    street: str
    buildingNumber: str
    postalCode: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    landmark: Optional[str] = None
    additionalInformation: Optional[str] = None


class ReceiverAddress(BaseModel):
    country: str
    governate: str
    regionCity: str
    street: str
    buildingNumber: str
    postalCode: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    landmark: Optional[str] = None
    additionalInformation: Optional[str] = None


class Issuer(BaseModel):
    id: str  # Tax registration number
    type: str = "B"  # B=Business, P=Person, F=Foreign
    name: str
    address: IssuerAddress


class Receiver(BaseModel):
    type: str  # B, P, F
    id: Optional[str] = None
    name: str
    address: ReceiverAddress

    @validator("id", pre=True)
    def strip_non_alphanumeric(cls, v):
        if v is not None:
            return re.sub(r"[^A-Za-z0-9]", "", str(v))
        return v


class Signature(BaseModel):
    signatureType: str = "I"
    value: str


# ========== Invoice Types (ETA v1.0) ==========

class TaxTotals(BaseModel):
    taxType: str
    amount: float


class TaxableItem(BaseModel):
    taxType: str
    subType: str
    amount: float
    rate: float = 14.0


class Discount(BaseModel):
    rate: float = 0.0
    amount: float = 0.0


class UnitValue(BaseModel):
    currencySold: str = "EGP"
    amountEGP: float
    amountSold: Optional[float] = None
    currencyExchangeRate: Optional[float] = None


class InvoiceLine(BaseModel):
    description: str
    itemType: str = "EGS"  # GS1 or EGS
    itemCode: str
    internalCode: Optional[str] = None
    unitType: str
    quantity: float
    salesTotal: float
    netTotal: float
    total: float
    discount: Discount
    taxableItems: List[TaxableItem]
    unitValue: UnitValue
    valueDifference: float = 0.0
    totalTaxableFees: float = 0.0
    itemsDiscount: float = 0.0

    @validator("itemType")
    def validate_item_type(cls, v):
        allowed = ["GS1", "EGS"]
        if v not in allowed:
            raise ValueError(f"itemType must be one of {allowed}")
        return v


class Payment(BaseModel):
    bankName: Optional[str] = None
    bankAddress: Optional[str] = None
    bankAccountNo: Optional[str] = None
    bankAccountIBAN: Optional[str] = None
    swiftCode: Optional[str] = None
    terms: Optional[str] = None

    @validator("swiftCode")
    def validate_swift(cls, v):
        if v and not re.match(r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$", v):
            raise ValueError("Invalid SWIFT/BIC code format")
        return v


class Delivery(BaseModel):
    approach: Optional[str] = None
    packaging: Optional[str] = None
    dateValidity: Optional[str] = None
    exportPort: Optional[str] = None
    countryOfOrigin: Optional[str] = None
    grossWeight: Optional[float] = None
    netWeight: Optional[float] = None
    terms: Optional[str] = None


class InvoiceSubmit(BaseModel):
    """ETA Invoice submission payload matching Schema v1.0"""
    issuer: Issuer
    receiver: Receiver
    documentType: str = "I"
    documentTypeVersion: str = "1.0"
    dateTimeIssued: str
    taxpayerActivityCode: str
    internalID: str
    invoiceLines: List[InvoiceLine]
    totalDiscountAmount: float
    totalSalesAmount: float
    netAmount: float
    totalAmount: float
    taxTotals: List[TaxTotals]
    signatures: List[Signature] = []
    extraDiscountAmount: float = 0.0
    totalItemsDiscountAmount: float = 0.0
    purchaseOrderReference: Optional[str] = None
    purchaseOrderDescription: Optional[str] = None
    salesOrderReference: Optional[str] = None
    salesOrderDescription: Optional[str] = None
    proformaInvoiceNumber: Optional[str] = None
    payment: Optional[Payment] = None
    delivery: Optional[Delivery] = None


# ========== Receipt Types (ETA v1.2) ==========

class SingleTaxableItems(BaseModel):
    taxType: str = Field(..., pattern=r"^T[1-9]|T1[0-2]$")
    subType: str = Field(..., pattern=r"^V0[0-9]{2}$")
    amount: float
    rate: conint(ge=0, le=100)


class SingleItemData(BaseModel):
    internalCode: str
    description: str
    itemType: str = "EGS"
    itemCode: str
    unitType: str
    quantity: float
    unitPrice: float
    netSale: float
    taxableItems: List[SingleTaxableItems]
    totalSale: float
    total: float


class ReceiptSeller(BaseModel):
    rin: str  # Tax registration number
    companyTradeName: str
    branchCode: str
    deviceSerialNumber: str
    syndicateLicenseNumber: Optional[str] = None
    activityCode: str
    branchAddress: ReceiverAddress


class ReceiptBuyer(BaseModel):
    type: str  # B, P, F
    id: Optional[str] = None
    name: str
    mobileNumber: Optional[str] = None
    paymentNumber: Optional[str] = None

    @validator("id", pre=True)
    def strip_non_alphanumeric(cls, v):
        if v is not None:
            return re.sub(r"[^A-Za-z0-9]", "", str(v))
        return v


class ReceiptHeader(BaseModel):
    dateTimeIssued: str
    receiptNumber: str
    uuid: str
    previousUUID: Optional[str] = None
    referenceOldUUID: Optional[str] = None
    currency: str = "EGP"
    sOrderNameCode: Optional[str] = None
    orderdeliveryMode: str = "FC"
    grossWeight: Optional[float] = None
    netWeight: Optional[float] = None

    @validator("orderdeliveryMode")
    def validate_delivery_mode(cls, v):
        allowed = ["FC", "TO", "TC"]
        if v not in allowed:
            raise ValueError(f"orderdeliveryMode must be one of {allowed}")
        return v


class ReceiptDocumentType(BaseModel):
    receiptType: str = "s"
    typeVersion: str = "1.2"


class SingleTaxTotal(BaseModel):
    taxType: str
    amount: float


class ReceiptSubmit(BaseModel):
    """ETA Receipt submission payload matching Schema v1.2"""
    header: ReceiptHeader
    documentType: ReceiptDocumentType
    seller: ReceiptSeller
    buyer: ReceiptBuyer
    itemData: List[SingleItemData]
    totalSales: float
    netAmount: float
    totalAmount: float
    taxTotals: List[SingleTaxTotal]
    paymentMethod: str
    contractor: Optional[Dict[str, Any]] = None
    beneficiary: Optional[Dict[str, Any]] = None


class ReceiptsResponse(BaseModel):
    receipts: List[ReceiptSubmit]


# ========== Connector / Config ==========

class ETAAuthConfig(BaseModel):
    """OAuth2 client credentials configuration"""
    client_id: str
    client_secret: str
    environment: str = "Pre-Production"  # Pre-Production or Production
    pos_serial: Optional[str] = None
    pos_os_version: Optional[str] = None

    @property
    def base_url(self) -> str:
        if self.environment == "Production":
            return "https://api.invoicing.eta.gov.eg/api/v1"
        return "https://api.preprod.invoicing.eta.gov.eg/api/v1"

    @property
    def token_url(self) -> str:
        if self.environment == "Production":
            return "https://id.eta.gov.eg/connect/token"
        return "https://id.preprod.eta.gov.eg/connect/token"


class ETASubmissionMode(str):
    Manual = "Manual"
    Batch = "Batch"
    Live = "Live"


# ========== Status Enums ==========

class InvoiceStatus(str):
    Draft = "draft"
    Submitted = "Submitted"
    Valid = "Valid"
    Invalid = "Invalid"
    Rejected = "Rejected"
    Cancelled = "Cancelled"


class ReceiptSubmissionStatus(str):
    Started = "Started"
    PartiallySucceeded = "Partially Succeeded"
    Failed = "Failed"
    Completed = "Completed"
