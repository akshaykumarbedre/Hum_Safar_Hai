"""
Financial Tools Module

This module provides a collection of reusable functions for common
financial calculations needed by the Humsafar AI agents.
"""


def calculate_loan_emi(principal: float, annual_rate: float, tenure_years: int) -> float:
    """
    Calculate the Equated Monthly Installment (EMI) for a loan.
    
    Args:
        principal (float): The principal loan amount in currency units
        annual_rate (float): Annual interest rate as a percentage (e.g., 12.5 for 12.5%)
        tenure_years (int): Loan tenure in years
        
    Returns:
        float: Monthly EMI amount
        
    Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    Where:
        P = Principal loan amount
        r = Monthly interest rate (annual_rate / 100 / 12)
        n = Number of monthly installments (tenure_years * 12)
    """
    if principal <= 0 or annual_rate < 0 or tenure_years <= 0:
        raise ValueError("Principal must be positive, annual rate must be non-negative, and tenure must be positive")
    
    # Handle zero interest rate case
    if annual_rate == 0:
        return principal / (tenure_years * 12)
    
    # Convert annual rate to monthly rate
    monthly_rate = annual_rate / 100 / 12
    
    # Calculate number of months
    num_months = tenure_years * 12
    
    # Calculate EMI using the formula
    numerator = principal * monthly_rate * ((1 + monthly_rate) ** num_months)
    denominator = ((1 + monthly_rate) ** num_months) - 1
    
    emi = numerator / denominator
    
    return round(emi, 2)


def calculate_sip_future_value(monthly_investment: float, annual_rate: float, tenure_years: int) -> float:
    """
    Calculate the future value of a Systematic Investment Plan (SIP).
    
    Args:
        monthly_investment (float): Monthly investment amount in currency units
        annual_rate (float): Expected annual rate of return as a percentage (e.g., 12.0 for 12%)
        tenure_years (int): Investment tenure in years
        
    Returns:
        float: Future value of the SIP
        
    Formula: FV = M * [((1+i)^n - 1) / i] * (1+i)
    Where:
        M = Monthly investment amount
        i = Monthly rate of return (annual_rate / 100 / 12)
        n = Number of monthly investments (tenure_years * 12)
    """
    if monthly_investment <= 0 or annual_rate < 0 or tenure_years <= 0:
        raise ValueError("Monthly investment must be positive, annual rate must be non-negative, and tenure must be positive")
    
    # Handle zero interest rate case
    if annual_rate == 0:
        return monthly_investment * tenure_years * 12
    
    # Convert annual rate to monthly rate
    monthly_rate = annual_rate / 100 / 12
    
    # Calculate number of months
    num_months = tenure_years * 12
    
    # Calculate future value using the formula
    compound_factor = (1 + monthly_rate) ** num_months
    annuity_factor = (compound_factor - 1) / monthly_rate
    
    future_value = monthly_investment * annuity_factor * (1 + monthly_rate)
    
    return round(future_value, 2)


def calculate_time_to_reach_goal(target_amount: float, current_principal: float, monthly_investment: float, annual_rate: float) -> float:
    """
    Calculates the number of years required to reach a financial goal via SIP.
    Useful for "When will I reach 1 Cr?" type questions.
    
    Args:
        target_amount (float): Target amount to achieve
        current_principal (float): Current investment value
        monthly_investment (float): Monthly investment amount
        annual_rate (float): Expected annual rate of return as a percentage
        
    Returns:
        float: Number of years required to reach the goal
        
    Formula: Uses iterative approach to solve for n in the SIP future value formula
    """
    if target_amount <= 0 or monthly_investment <= 0 or annual_rate < 0:
        raise ValueError("Target amount and monthly investment must be positive, annual rate must be non-negative")
    
    # If already at or above the target with current principal
    if current_principal >= target_amount:
        return 0.0
    
    # Calculate remaining amount needed
    remaining_amount = target_amount - current_principal
    
    # Handle zero interest rate case
    if annual_rate == 0:
        years_needed = remaining_amount / (monthly_investment * 12)
        return round(years_needed, 2)
    
    # Convert annual rate to monthly rate
    monthly_rate = annual_rate / 100 / 12
    
    # Use iterative approach to find the time
    # Starting with an estimate and refining
    years = 1.0
    max_iterations = 600  # 50 years max
    tolerance = 0.01  # 1% tolerance
    
    for _ in range(max_iterations):
        num_months = years * 12
        
        # Calculate SIP future value
        compound_factor = (1 + monthly_rate) ** num_months
        annuity_factor = (compound_factor - 1) / monthly_rate
        sip_future_value = monthly_investment * annuity_factor * (1 + monthly_rate)
        
        # Add growth of current principal
        current_principal_future = current_principal * compound_factor
        total_future_value = sip_future_value + current_principal_future
        
        # Check if we've reached the target
        if abs(total_future_value - target_amount) / target_amount < tolerance:
            return round(years, 2)
        
        # Adjust years based on whether we're over or under target
        if total_future_value < target_amount:
            years += 0.1
        else:
            years -= 0.05
            
        # Ensure years doesn't go negative
        if years <= 0:
            years = 0.1
    
    # If we couldn't converge, return the last calculated value
    return round(years, 2)


def calculate_required_sip_for_goal(target_amount: float, tenure_years: int, annual_rate: float) -> float:
    """
    Calculates the monthly SIP amount required to reach a target in a given number of years.
    Useful for "How much should I invest monthly to reach 1 Cr in 15 years?" type questions.
    
    Args:
        target_amount (float): Target amount to achieve
        tenure_years (int): Investment tenure in years
        annual_rate (float): Expected annual rate of return as a percentage
        
    Returns:
        float: Required monthly SIP amount
        
    Formula: Derived from SIP future value formula solving for monthly investment
    """
    if target_amount <= 0 or tenure_years <= 0 or annual_rate < 0:
        raise ValueError("Target amount and tenure must be positive, annual rate must be non-negative")
    
    # Handle zero interest rate case
    if annual_rate == 0:
        return round(target_amount / (tenure_years * 12), 2)
    
    # Convert annual rate to monthly rate
    monthly_rate = annual_rate / 100 / 12
    
    # Calculate number of months
    num_months = tenure_years * 12
    
    # Calculate required monthly investment using the formula
    # target_amount = M * [((1+r)^n - 1) / r] * (1+r)
    # Solving for M: M = target_amount / ([((1+r)^n - 1) / r] * (1+r))
    
    compound_factor = (1 + monthly_rate) ** num_months
    annuity_factor = (compound_factor - 1) / monthly_rate
    adjustment_factor = (1 + monthly_rate)
    
    required_monthly_investment = target_amount / (annuity_factor * adjustment_factor)
    
    return round(required_monthly_investment, 2)


def calculate_lumpsum_future_value(principal: float, annual_rate: float, tenure_years: int) -> float:
    """
    Calculates the future value of a single lump-sum investment.
    Useful for projecting FD or one-time stock investments.
    
    Args:
        principal (float): Principal investment amount
        annual_rate (float): Annual rate of return as a percentage
        tenure_years (int): Investment tenure in years
        
    Returns:
        float: Future value of the lump-sum investment
        
    Formula: FV = P * (1 + r)^n
    Where:
        P = Principal amount
        r = Annual interest rate (as decimal)
        n = Number of years
    """
    if principal <= 0 or annual_rate < 0 or tenure_years <= 0:
        raise ValueError("Principal and tenure must be positive, annual rate must be non-negative")
    
    # Handle zero interest rate case
    if annual_rate == 0:
        return principal
    
    # Convert annual rate to decimal
    annual_rate_decimal = annual_rate / 100
    
    # Calculate future value using compound interest formula
    future_value = principal * ((1 + annual_rate_decimal) ** tenure_years)
    
    return round(future_value, 2)