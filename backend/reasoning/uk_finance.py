from typing import Dict, Any, Optional
from datetime import datetime

class UKFinanceLogic:
    """
    Purely deterministic UK financial logic. 
    No LLM decision making here.
    """
    
    @staticmethod
    def calculate_pension_annual_allowance(gross_income: float) -> float:
        """
        Calculates available annual allowance based on UK tapering rules.
        Standard for 2024/25: £60,000.
        Tapering starts at Adjusted Income > £260,000.
        Min allowance: £10,000.
        """
        standard_allowance = 60000.0
        threshold_income = 200000.0 # Threshold for starting to check adjusted income
        adjusted_income_limit = 260000.0
        min_allowance = 10000.0
        
        if gross_income <= adjusted_income_limit:
            return standard_allowance
        
        excess = gross_income - adjusted_income_limit
        reduction = excess / 2.0
        final_allowance = max(min_allowance, standard_allowance - reduction)
        return final_allowance

    @staticmethod
    def check_isa_optimization(isa_remaining: float, cash_balance: float) -> bool:
        """
        Strategic flag: If client has >£5k ISA allowance left and >£10k cash.
        """
        return isa_remaining > 5000 and cash_balance > 10000

    @staticmethod
    def check_cgt_exposure(unrealized_gains: float) -> bool:
        """
        UK CGT allowance 2024/25: £3,000.
        Flag if gains exceed 80% of allowance to allow for strategic selling.
        """
        cgt_allowance = 3000.0
        return unrealized_gains > (cgt_allowance * 0.8)

    @staticmethod
    def check_iht_pulse(total_wealth: float, liquid_assets: float) -> bool:
        """
        Flag if total wealth > £1M (basic IHT threshold + RNRB) and high liquidity (>20% cash).
        """
        iht_threshold = 1000000.0
        return total_wealth > iht_threshold and (liquid_assets / total_wealth) > 0.2
