from typing import Dict, Any, List, Optional
from datetime import datetime
from shared.models import EventType, UrgencyLevel
from reasoning.uk_finance import UKFinanceLogic

class RiskClassifier:
    """Strategic advisor logic for risk classification. Thinking beyond simple thresholds."""
    
    @staticmethod
    def classify_market_risk(portfolio: Dict[str, Any], market_snapshot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Multi-factor detection: Concentration + Performance.
        An advisor flags even small drops if the client is heavily concentrated.
        """
        sector_performance = market_snapshot.get("sector_performance", {})
        holdings = portfolio.get("holdings", [])
        total_value = portfolio.get("total_value_gbp", 0)
        
        # 1. Check for CONCENTRATION RISK (Regardless of performance)
        sector_exposures = {}
        for holding in holdings:
            sector = holding.get("sector", "Unknown")
            exp = holding.get("exposure_percentage", 0)
            sector_exposures[sector] = sector_exposures.get(sector, 0) + exp

        for sector, exposure in sector_exposures.items():
            if exposure > 0.3: # 30% is a strategic red flag for HNW clients
                return {
                    "event_type": EventType.MARKET_RISK.value,
                    "urgency": (UrgencyLevel.HIGH.value if exposure > 0.45 else UrgencyLevel.MEDIUM.value),
                    "deterministic_classification": {
                        "reason": f"Strategic Concentration Risk: {sector} makes up {exposure*100:.1f}% of total portfolio.",
                        "type": "concentration",
                        "sector": sector,
                        "exposure": exposure
                    }
                }

        # 2. Check for COMBINED RISK (Exposure * Performance)
        for sector, exposure in sector_exposures.items():
            performance = sector_performance.get(sector, 0)
            
            # Sensitivity logic: 
            # If 10% exposed, flag at -4%
            # If 25% exposed, flag at -1.5%
            risk_score = exposure * abs(performance) if performance < 0 else 0
            
            if risk_score > 0.004: # Equivalent to 20% exposure * 2% drop
                return {
                    "event_type": EventType.MARKET_RISK.value,
                    "urgency": (UrgencyLevel.HIGH.value if risk_score > 0.01 else UrgencyLevel.MEDIUM.value),
                    "deterministic_classification": {
                        "reason": f"Sensitivity Alert: {sector} drop ({performance*100:.1f}%) impacting high exposure ({exposure:.1f}%)",
                        "type": "sensitivity",
                        "sector": sector,
                        "performance": performance,
                        "exposure": exposure
                    }
                }
        return None

    @staticmethod
    def classify_tax_opportunity(client: Dict[str, Any], portfolio: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Proactive tax optimization for HNW clients using UKFinanceLogic.
        """
        tax_profile = client.get("tax_profile", {})
        isa_remaining = tax_profile.get("isa_allowance_remaining", 0)
        cash_balance = portfolio.get("cash_balance_gbp", 0)
        total_wealth = portfolio.get("total_value_gbp", 0)
        
        # ISA Optimization
        if UKFinanceLogic.check_isa_optimization(isa_remaining, cash_balance):
            return {
                "event_type": EventType.TAX_OPPORTUNITY.value,
                "urgency": UrgencyLevel.MEDIUM.value,
                "deterministic_classification": {
                    "reason": f"Strategic Tax Opportunity: High cash (£{cash_balance:,.0f}) with unused ISA (£{isa_remaining:,.0f}).",
                    "isa_remaining": isa_remaining,
                    "cash_balance": cash_balance
                }
            }

        # CGT Exposure
        unrealized_gains = portfolio.get("unrealized_gains_gbp", 0)
        if UKFinanceLogic.check_cgt_exposure(unrealized_gains):
            return {
                "event_type": EventType.TAX_OPPORTUNITY.value,
                "urgency": UrgencyLevel.MEDIUM.value,
                "deterministic_classification": {
                    "reason": f"UK CGT Warning: Unrealized gains (£{unrealized_gains:,.0f}) approaching 2024/25 allowance.",
                    "unrealized_gains": unrealized_gains
                }
            }
            
        return None

    @staticmethod
    def classify_pension_allowance(client: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detects pension allowance tapering or looming limits.
        """
        income = client.get("tax_profile", {}).get("estimated_gross_income", 0)
        if income > 200000:
            allowance = UKFinanceLogic.calculate_pension_annual_allowance(income)
            if allowance < 60000:
                return {
                    "event_type": EventType.TAX_OPPORTUNITY.value,
                    "urgency": (UrgencyLevel.HIGH.value if allowance < 20000 else UrgencyLevel.MEDIUM.value),
                    "deterministic_classification": {
                        "reason": f"Pension Tapering: High income (£{income:,.0f}) reduced available allowance to £{allowance:,.0f}.",
                        "income": income,
                        "available_allowance": allowance
                    }
                }
        return None

    @staticmethod
    def classify_compliance_exposure(portfolio: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detects drift from agreed mandates - tighter for conservative clients.
        """
        target_risk = portfolio.get("target_risk_score", 5)
        current_risk = portfolio.get("current_risk_score", 5)
        drift = abs(current_risk - target_risk)
        
        # Strategic logic: Conservative clients (Risk < 4) get flagged at 0.5 drift.
        # Aggressive clients get flagged at 1.5 drift.
        threshold = 0.5 if target_risk < 4 else 1.2
        
        if drift >= threshold:
            return {
                "event_type": EventType.COMPLIANCE_EXPOSURE.value,
                "urgency": (UrgencyLevel.HIGH.value if drift > (threshold * 2) else UrgencyLevel.MEDIUM.value),
                "deterministic_classification": {
                    "reason": f"Mandate Drift: Client target is {target_risk}, currently operating at {current_risk:.1f}",
                    "drift": drift,
                    "target": target_risk,
                    "current": current_risk
                }
            }
        return None

    @staticmethod
    def classify_behavioural_risk(client: Dict[str, Any], market_snapshot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Predicts behavioural friction before it happens.
        """
        profile = client.get("behavioural_profile", {})
        panic_score = profile.get("panic_score", 0)
        sector_performance = market_snapshot.get("sector_performance", {})
        
        # Advisor logic: Flag if the client's "Worst Nightmare" sector is even slightly down.
        nightmare_sector = profile.get("sensitivity_sector", "Energy") 
        perf = sector_performance.get(nightmare_sector, 0)
        
        if (panic_score >= 6 and perf < -0.01) or (perf < -0.04):
            return {
                "event_type": EventType.BEHAVIOURAL_RISK.value,
                "urgency": (UrgencyLevel.HIGH.value if panic_score > 8 else UrgencyLevel.MEDIUM.value),
                "deterministic_classification": {
                    "reason": f"Behavioural Friction: Client has high sensitivity to {nightmare_sector} which is currently down {perf*100:.1f}%",
                    "panic_score": panic_score,
                    "trigger_sector": nightmare_sector,
                    "trigger_performance": perf
                }
            }
        return None

class VulnerabilityAssessor:
    """
    FCA-aligned vulnerability assessment logic.
    Deterministic scoring based on reported life events and engagement logs.
    """
    
    @staticmethod
    def assess(client: Dict[str, Any], memories: List[str]) -> Dict[str, Any]:
        """
        Score 0.0 to 1.0. 
        Higher = more vulnerable.
        """
        score = 0.0
        categories = []
        notes = []
        
        # 1. Check for life event triggers in memory (Simplified string matching)
        vulnerability_keywords = {
            "bereavement": ("Life Event", 0.4),
            "divorce": ("Life Event", 0.3),
            "redundancy": ("Financial Resilience", 0.5),
            "health issue": ("Health", 0.4),
            "long covid": ("Health", 0.3),
            "dementia": ("Health", 0.7),
        }
        
        all_memory_text = " ".join(memories).lower()
        for kw, (cat, weighting) in vulnerability_keywords.items():
            if kw in all_memory_text:
                score += weighting
                if cat not in categories: categories.append(cat)
                notes.append(f"Detected mention of {kw}")
        
        # 2. Check for Financial Resilience
        total_wealth = client.get("total_value_gbp", 0)
        if total_wealth < 10000: # Low buffer
            score += 0.2
            if "Resilience" not in categories: categories.append("Resilience")
            
        return {
            "vulnerability_score": min(1.0, score),
            "vulnerability_category": ", ".join(categories) if categories else "None",
            "vulnerability_notes": "; ".join(notes) if notes else "No indicators found"
        }

