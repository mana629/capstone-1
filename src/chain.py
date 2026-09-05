import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate , ChatPromptTemplate
from langchain_core.runnables import  RunnableBranch


from src.schemas import (
     AccountAnalysis,
     BillingAnalysis,
     TechnicalAnalysis,
     OrderDeliveryAnalysis,
     CancellationRefundAnalysis,
     GeneralAnalysis,
     TicketTriage,
     ResolutionDecision
)

PROJRCT_ROOT = Path(__file__).resolve().parent.parent


ANALYSIS_FOCUS = {
    "billing":(""
    "-issue\n"
    "-amount\n"
    "-transaction_count\n"
    "-refund_required"
    ),
    "technical":(""
    "-issue\n"
    "-affected_feature\n"
    "-error_message\n"
    "-troubleshooting_required\n"
    "-account_status"
    ),
    "account":(
    "-issue\n"
    "-account_problem\n"
    "-verification_required\n"
    "-account_status"
    ),
    "order_delivery":(
    "-issue\n"
    "-order_status\n"
    "-delivery_problem\n"
    "-customer_request"
    ),
    "cancellation_refund":(
    "-request_type\n"
    "-reason\n"
    "refund_required\n"
    "-retention_opportunity"
    ),
    "general":(
    "-issue\n"
    "-customer_request\n"
    "- additional_context"
    ) 
}

def load_prompt(file_path):
    """
    Load a prompt template text file from disk.

    Args:
        file_path (str | Path): Path to a .txt prompt file.

    Returns:
        str: The full prompt text.

    Example:
        text = load_prompt("prompts/classification_prompt.txt")
        print(text[:40])
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = PROJRCT_ROOT / path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"prompt not found at {path}")

def create_triage_chain(llm):
    # load prompt
    prompt_txt = load_prompt("prompts/classification_prompt.txt")
    prompt_template = ChatPromptTemplate.from_template(prompt_txt)
    structured_llm = llm.with_structured_output(TicketTriage)
    return prompt_template | structured_llm

def create_analysis_chain(llm, category, schema):
    prompt_txt = load_prompt("prompts/case_analysis_prompt.txt")
    prompt_template = ChatPromptTemplate.from_template(prompt_txt)
    prompt = prompt_template.partial(
        category=category,
        analysis_focus=ANALYSIS_FOCUS[category],
    )
    structured_llm = llm.with_structured_output(schema)
    return prompt | structured_llm 

def create_billing_chain(llm):
    return create_analysis_chain(
        llm=llm,
        category="billing",
        schema=BillingAnalysis
    )

def create_account_chain(llm):
    return create_analysis_chain(
        llm=llm,
        category="account",
        schema=AccountAnalysis
    )

def create_order_delivery_chain(llm):
    return create_analysis_chain(
        llm=llm,
        category="order_delivery",
        schema=OrderDeliveryAnalysis
    )

def create_technical_chain(llm):
    return create_analysis_chain(
        llm=llm,
        category="technical",
        schema=TechnicalAnalysis
    )

def create_cancellation_refund_chain(llm):
    return create_analysis_chain(
        llm=llm,
        category="cancellation_refund",
        schema=CancellationRefundAnalysis
    )

def create_general_chain(llm):
    return create_analysis_chain(
        llm=llm,
        category="general",
        schema=GeneralAnalysis
    )

def create_router(llm):
    billing_chain = create_billing_chain(llm)
    account_chain = create_account_chain(llm)
    order_delivery_chain = create_order_delivery_chain(llm)
    technical_chain = create_technical_chain(llm)
    cancellation_refund_chain = create_cancellation_refund_chain(llm)
    general_chain = create_general_chain(llm)
    
    # route the tickets to specialized chain based on its category
    return RunnableBranch(
        (lambda x: x["category"] == "billing", billing_chain),
        (lambda x: x["category"] == "technical", technical_chain),
        (lambda x: x["category"] == "account", account_chain),
        (lambda x: x["category"] == "cancellation_refund", cancellation_refund_chain),
        (lambda x: x["category"] == "order_delivery", order_delivery_chain),
        general_chain,  # default fallback
    )

def create_resolution_chain(llm):
    """
    Create the final resolution and action-plan chain.
    """
    prompt_txt = load_prompt("prompts/resolution_prompt.txt")
    prompt_template = ChatPromptTemplate.from_template(prompt_txt)
    structured_llm = llm.with_structured_output(ResolutionDecision)
    return prompt_template | structured_llm

def create_response_chain(llm):
    prompt_txt = load_prompt("prompts/response_prompt.txt")
    prompt_template = ChatPromptTemplate.from_template(prompt_txt)
    return prompt_template | llm | StrOutputParser()