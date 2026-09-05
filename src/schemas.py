from pydantic import BaseModel, Field
from typing import Literal

# Allowed values used across triage and resolution stages
Category = Literal[
    "billing",
    "technical",
    "account",
    "cancellation_refund",
    "order_delivery",
    "general"
]

Priority = Literal["low", "medium", "high", "critical"]

ResolutionType = Literal[
    "self_service",
    "resolve",
    "escalate",
    "request_information"
]

class TicketTriage(BaseModel):
    category: Category = Field(..., description="support ticket category")
    priority: Priority = Field(..., description="urgency of the ticket")
    language: str = Field(..., description="language used in customer ticket")

class BillingAnalysis(BaseModel):
    issue: str = Field(..., description="summary about billing issue")
    amount: str = Field(..., description="money amount mentioned, or 'unknown'")
    transaction_count: int = Field(..., description="number of charges mentioned")
    refund_required: bool = Field(..., description="whether a refund appears needed")

class TechnicalAnalysis(BaseModel):
    issue: str = Field(..., description="short summary of technical issue")
    affected_feature: str = Field(..., description="specific product feature or service affected")
    error_message: str = Field(..., description="error text if mentioned, else 'none'")
    troubleshooting_required: bool = Field(..., description="whether troubleshooting is needed")
    account_status: str = Field(..., description="likely account status, for example active, locked, or unknown")

class AccountAnalysis(BaseModel):
    issue: str = Field(..., description="short summary of the account issue")
    account_problem: str = Field(..., description="specifics of the account or profile issue")
    verification_needed: bool = Field(..., description="whether identity verification is needed")
    account_status: str = Field(..., description="likely account status, for example active, locked, or unknown")

class OrderDeliveryAnalysis(BaseModel):
    issue: str = Field(..., description="short summary of the order or delivery issue")
    order_status: str = Field(..., description="current status of order, otherwise unknown")
    delivery_details: bool = Field(..., description="whether specific tracking / delivery details are present")
    customer_request: str = Field(..., description="what the customer wants")

class CancellationRefundAnalysis(BaseModel):
    request_type: str = Field(..., description="type of cancellation/refund request")
    reason: str = Field(..., description="cancellation reason if provided")
    retention_opportunity: bool = Field(..., description="whether there may be a chance to retain the customer")

class GeneralAnalysis(BaseModel):
    issue: str = Field(..., description="summary of customer issue")
    customer_request: str = Field(..., description="what customer asks for")

class ResolutionDecision(BaseModel):
    resolution_action: str = Field(..., description="recommended action taken for customer issue")
    resolution_type: ResolutionType = Field(..., description="type of action")
    human_required: bool = Field(..., description="whether human is required for resolving the issue")

class TicketResult(BaseModel):
    ticket_id: str
    customer_name: str
    category: str
    priority: str
    language: str
    analysis_type: str
    case_summary: str
    resolution_type: str
    resolution_action: str
    human_required: bool
    response: str
    resolution_reason: str