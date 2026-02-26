from datetime import datetime

def _format_time(iso_str, time_only=False) -> str:
    """Format ISO timestamp to display time."""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(str(iso_str).replace("Z", "+00:00"))
        if time_only:
            return dt.strftime("%-I:%M %p")
        return dt.strftime("%-I:%M %p")
    except Exception:
        return str(iso_str)[:16]


def _format_date(iso_str) -> str:
    """Format ISO timestamp to display date."""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(str(iso_str).replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(iso_str)[:10]


def _minutes_until(iso_str) -> int:
    """Calculate minutes until a timestamp."""
    if not iso_str:
        return 0
    try:
        dt = datetime.fromisoformat(str(iso_str).replace("Z", "+00:00"))
        now = datetime.utcnow().replace(tzinfo=dt.tzinfo)
        delta = (dt - now).total_seconds() / 60
        return max(0, int(delta))
    except Exception:
        return 0


def _event_to_text(event_type: str, client_name: str, classification: dict, interpretation: dict) -> str:
    """Generate high-intelligence conversational text for a risk event."""
    classification = classification or {}
    interpretation = interpretation or {}
    
    # 1. PRIORITIZE: LLM-generated personalized headline
    if interpretation.get("headline"):
        return interpretation["headline"]
    
    # 2. FALLBACK: Deterministic reason from classification
    deterministic_reason = classification.get("reason")
    if deterministic_reason:
        # If it's a client-specific reason, ensure name is included if relevant
        if client_name and client_name not in deterministic_reason:
            return f"{client_name}: {deterministic_reason}"
        return deterministic_reason
        
    if classification.get("impact_title"):
        return classification["impact_title"]
        
    if event_type == "market_risk":
        sector = classification.get("sector", "the market")
        return f"{client_name}'s portfolio has breached volatility thresholds due to {sector} exposure."
    elif event_type == "behavioural_risk":
        sector = classification.get("trigger_sector", "market")
        history = classification.get("historical_pattern", "")
        prefix = f"{client_name}: History: {history}" if history else client_name
        return f"{prefix} is about to overreact to today's {sector} volatility."
    elif event_type == "market_interrupt":
        if classification.get("is_macro_grouping"):
            count = classification.get("exposed_count", 0)
            return f"{classification.get('impact_title', 'Market Alert')} ({count} clients exposed)"
        return f"Abnormal market movement detected. {classification.get('reason', '')}"
    elif event_type == "tax_opportunity":
        return f"Strategic Tax optimization window detected for {client_name}."
    elif event_type == "compliance_exposure":
        return f"{client_name}: Mandate Drift detected. Portfolio no longer aligns with agreed risk profile."
    elif event_type == "pension_allowance":
        return f"{client_name}: Pension Tapering risk identified based on estimated gross income."
    elif event_type == "isa_optimization":
        return f"{client_name}: Strategic ISA allowance unused (£20,000 limit)."
    elif event_type == "cgt_exposure":
        return f"{client_name}: Unrealized gains approaching 2024/25 CGT allowance."
    elif event_type == "vulnerability_alert":
        return f"Consumer Duty Alert: {client_name} has high vulnerability indicators."
    elif event_type == "morning_intelligence":
        return f"Morning Intelligence Summary for {client_name}."
    return f"New intelligence for {client_name}."


def _build_chips(event_type: str, classification: dict, urgency: str) -> list:
    """Build intelligence chips for a card."""
    classification = classification or {}
    chips = []
    type_labels = {
        "market_risk": "Market Risk",
        "behavioural_risk": "Behavioural Risk",
        "market_interrupt": "Market Interrupt",
        "tax_opportunity": "Tax Window",
        "compliance_exposure": "Compliance",
        "morning_intelligence": "Morning Brief",
        "pension_allowance": "Pension",
        "isa_optimization": "ISA",
        "cgt_exposure": "CGT",
        "iht_pulse": "IHT",
        "vulnerability_alert": "Vulnerability"
    }
    chips.append(type_labels.get(event_type, event_type.replace("_", " ").title()))
    
    if event_type == "morning_intelligence":
        best_theme = classification.get("best_theme") or {}
        theme_name = best_theme.get("theme")
        if theme_name:
            chips.append(theme_name)
    else:
        # Urgency is often passed as a string/enum now
        urgency_label = str(urgency).replace("UrgencyLevel.", "").title()
        chips.append(f"Urgency: {urgency_label}")
    
    sector = classification.get("sector")
    if sector:
        perf = classification.get("performance")
        if perf is not None:
            chips.append(f"{sector} {perf*100:+.1f}%")
    
    return chips


def _drawer_title(event_type: str) -> str:
    titles = {
        "market_risk": "Market Risk Analysis",
        "behavioural_risk": "Behavioural Risk Intelligence",
        "market_interrupt": "Market Interrupt Alert",
        "tax_opportunity": "Tax Optimisation Window",
        "compliance_exposure": "Compliance Drift Analysis",
        "pension_allowance": "Pension Allowance Check",
        "isa_optimization": "ISA Optimization",
        "cgt_exposure": "CGT Exposure Analysis",
        "iht_pulse": "IHT Planning Pulse",
        "vulnerability_alert": "Consumer Duty Assessment",
        "morning_intelligence": "Morning Intelligence Summary",
    }
    return titles.get(event_type, "Intelligence Detail")
