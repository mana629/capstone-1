import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.chain import(
    create_triage_chain,
    create_router,
    create_resolution_chain,
    create_response_chain
)

from src.schemas import TicketResult

CHAIN_LABELS = {
    "billing":"Billing_Chain",
    "technical":"Technical_Chain",
    "account":"Account_Chain",
    "cancellation_refund":"Cancellation_Refund_Chain",
    "order_delivery":"Order_Delivery_Chain",
    "general":"General_Chain"
}
def build_workflow(llm):
    triage_chain = create_triage_chain(llm)
    router = create_router(llm)
    resolution_chain = create_resolution_chain(llm)
    response_chain = create_response_chain(llm)
    
def process_ticket(ticket,workflow):
    customer_name = ticket["customer_name"]
    ticket_text = ticket["ticket_text"]
    
    triage =workflow["triage_chain"].invoke({
        "customer_name":customer_name,
        "ticket_text":ticket_text
    })

    print(f"Category : {triage.category}")
    print(f"Priority : {triage.priority}")
    print(f"Routing to : {CHAIN_LABELS.get(triage.category, 'general chain')}")

    # ---- Stage 2 + 3: Routing and Case Analysis ----
    # The router looks at "category" and calls the matching analysis chain.
    case_analysis = workflow["router"].invoke({
        "catagory":triage.catagory,
        "ticket":ticket_text,
        "customer_name":customer_name
    })
    # Convert analysis to text so later prompts stay simple and reusable.
    case_analysis_text = case_analysis.model_dump_json(indent=2)
    # ---- Stage 4: Resolution Decision ----
    resolution = workflow["resolution_chain"].invoke({
        "customer_name":customer_name,
        "category":triage.catagory,
        "priority":triage.priority,
        "case_analysis":case_analysis_text,
        "language":triage.language,
        "ticket_text":ticket_text
    })
    
    print(f"Resolution : {resolution.resolution_type}")
    print(f"Human Required : {'yes' if resolution.human_required else 'no'}")

    # ---- Stage 5: Customer Response ----
    response_text = workflow["response_chain"].invoke({
        "customer_name":customer_name,
        "category":triage.catagory,
        "priority":triage.priority,
        "case_analysis":case_analysis_text,
        "language":triage.language,
        "ticket_text":ticket_text,
        "resolution":resolution.resolution_action
    })
    # ---- Stage 6: Build final result ----
    
    result = TicketResult(
        ticket_id=ticket["ticket_id"],
        customer_name=customer_name,
        category=triage.catagory,
        priority=triage.priority,
        language=triage.language,
        analysis_type=triage.analysis_type,
        case_summary=case_analysis_text,
        resolution_type=resolution.resolution_type,
        resolution_action=resolution.resolution_action,
        human_required=resolution.human_required,
        response=response_text,
        resolution_reason=resolution.resolution_reason
    )
    return result





    

     
    
    