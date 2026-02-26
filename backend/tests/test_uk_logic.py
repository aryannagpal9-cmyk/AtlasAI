import pytest
from backend.reasoning.uk_finance import UKFinanceLogic

def test_pension_annual_allowance_standard():
    # Income <= £260,000 should get £60,000
    assert UKFinanceLogic.calculate_pension_annual_allowance(150000) == 60000.0
    assert UKFinanceLogic.calculate_pension_annual_allowance(260000) == 60000.0

def test_pension_annual_allowance_tapered():
    # Income £300,000 (Excess 40k, Reduc 20k) -> £40,000
    assert UKFinanceLogic.calculate_pension_annual_allowance(300000) == 40000.0
    
    # Income £360,000 (Excess 100k, Reduc 50k) -> £10,000
    assert UKFinanceLogic.calculate_pension_annual_allowance(360000) == 10000.0

def test_isa_optimization():
    # Remaining > 5k and Cash > 10k -> True
    assert UKFinanceLogic.check_isa_optimization(6000, 15000) is True
    # Remaining < 5k -> False
    assert UKFinanceLogic.check_isa_optimization(4000, 15000) is False
    # Cash < 10k -> False
    assert UKFinanceLogic.check_isa_optimization(6000, 8000) is False

def test_cgt_exposure():
    # Gains > 2.4k (80% of 3k) -> True
    assert UKFinanceLogic.check_cgt_exposure(2500) is True
    # Gains < 2.4k -> False
    assert UKFinanceLogic.check_cgt_exposure(2300) is False
