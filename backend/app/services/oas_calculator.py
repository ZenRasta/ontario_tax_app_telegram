"""
Enhanced Old Age Security (OAS) Calculator Service

Handles comprehensive OAS benefit calculations including:
- Basic OAS pension amounts with residence requirements
- Income-based clawback calculations (OAS Recovery Tax)
- Deferral benefits (up to age 70) with 0.6% monthly bonus
- Guaranteed Income Supplement (GIS) calculations
- Allowance calculations for spouses aged 60-64
- Integration with existing tax calculation system
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import yaml
from pathlib import Path
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@dataclass
class OASBenefitResult:
    """Comprehensive result of OAS benefit calculation"""
    # Basic OAS
    basic_oas_amount: float
    clawback_amount: float
    net_oas_amount: float
    
    # GIS and Allowances
    gis_amount: float
    allowance_amount: float
    total_benefit: float
    
    # Calculation details
    deferral_months: int
    deferral_bonus_rate: float
    age_at_calculation: int
    income_tested_against: float
    years_in_canada: int
    residence_factor: float
    
    # Tax integration
    marginal_tax_rate_on_oas: float
    effective_benefit_rate: float

@dataclass
class OASParameters:
    """OAS calculation parameters for a given year"""
    # Basic OAS amounts (2024 values as baseline)
    max_monthly_oas: float = 713.34
    max_annual_oas: float = 8560.08
    
    # Clawback (Recovery Tax) parameters
    clawback_threshold: float = 90997  # 2024 threshold
    clawback_rate: float = 0.15  # 15% recovery rate
    
    # GIS parameters
    max_monthly_gis_single: float = 1065.47
    max_monthly_gis_married: float = 641.35
    gis_income_threshold: float = 21624
    gis_reduction_rate: float = 0.5  # 50 cents per dollar of income
    
    # Allowance parameters (for spouse aged 60-64)
    max_monthly_allowance: float = 1354.69
    allowance_income_threshold: float = 41760
    
    # Deferral parameters
    deferral_bonus_rate: float = 0.006  # 0.6% per month
    max_deferral_months: int = 60  # 5 years (age 65-70)
    
    # Residence requirements
    full_pension_years: int = 40  # Years after age 18 for full pension
    minimum_residence_years: int = 10  # Minimum to qualify

class OASCalculator:
    """Enhanced calculator for Old Age Security benefits"""
    
    def __init__(self):
        self.parameters_cache = {}
        self._load_oas_parameters()
    
    def _load_oas_parameters(self):
        """Load OAS parameters from configuration files"""
        try:
            # Try to load from existing tax data structure
            tax_data_path = Path(__file__).parent.parent / "data" / "tax_years.yml"
            
            if tax_data_path.exists():
                with open(tax_data_path, 'r') as file:
                    tax_data = yaml.safe_load(file)
                    
                for year, data in tax_data.items():
                    if isinstance(data, dict):
                        # Extract OAS parameters from the tax year data
                        max_annual_oas = data.get('oas_max_benefit_at_65', 8560.08)
                        max_monthly_oas = max_annual_oas / 12
                        
                        self.parameters_cache[year] = OASParameters(
                            max_monthly_oas=max_monthly_oas,
                            max_annual_oas=max_annual_oas,
                            clawback_threshold=data.get('oas_clawback_threshold', 90997),
                            clawback_rate=data.get('oas_clawback_rate', 0.15),
                            max_monthly_gis_single=1065.47,  # Default values - not in tax file
                            max_monthly_gis_married=641.35,
                            gis_income_threshold=21624,
                            deferral_bonus_rate=data.get('oas_deferral_factor_per_month', 0.006),
                            max_deferral_months=60
                        )
                        
                logger.info(f"Tax years data loaded successfully for years: {list(self.parameters_cache.keys())}")
            else:
                logger.warning("Tax years data file not found, using default parameters")
                self._set_default_parameters()
                
        except Exception as e:
            logger.error(f"Error loading OAS parameters: {e}")
            self._set_default_parameters()
    
    def _set_default_parameters(self):
        """Set default OAS parameters for current year"""
        current_year = datetime.now().year
        self.parameters_cache[current_year] = OASParameters()
    
    def get_parameters(self, year: int) -> OASParameters:
        """Get OAS parameters for a specific year with inflation adjustments"""
        if year in self.parameters_cache:
            return self.parameters_cache[year]
        
        # If exact year not found, use the closest available year and adjust for inflation
        available_years = sorted(self.parameters_cache.keys())
        if not available_years:
            self._set_default_parameters()
            return self.parameters_cache[datetime.now().year]
        
        # Use the most recent year available
        base_year = max(y for y in available_years if y <= year) if any(y <= year for y in available_years) else min(available_years)
        base_params = self.parameters_cache[base_year]
        
        # Apply inflation adjustment (approximate 2% annually)
        inflation_factor = (1.02) ** (year - base_year)
        
        adjusted_params = OASParameters(
            max_monthly_oas=base_params.max_monthly_oas * inflation_factor,
            max_annual_oas=base_params.max_annual_oas * inflation_factor,
            clawback_threshold=base_params.clawback_threshold * inflation_factor,
            clawback_rate=base_params.clawback_rate,  # Rate doesn't change
            max_monthly_gis_single=base_params.max_monthly_gis_single * inflation_factor,
            max_monthly_gis_married=base_params.max_monthly_gis_married * inflation_factor,
            gis_income_threshold=base_params.gis_income_threshold * inflation_factor,
            max_monthly_allowance=base_params.max_monthly_allowance * inflation_factor,
            allowance_income_threshold=base_params.allowance_income_threshold * inflation_factor,
            deferral_bonus_rate=base_params.deferral_bonus_rate,
            max_deferral_months=base_params.max_deferral_months
        )
        
        self.parameters_cache[year] = adjusted_params
        return adjusted_params
    
    def calculate_oas_benefit(
        self,
        birth_date: date,
        calculation_date: date,
        annual_income: float,
        years_in_canada: int,
        marital_status: str = "single",
        spouse_income: float = 0.0,
        spouse_age: Optional[int] = None,
        deferral_months: int = 0,
        marginal_tax_rate: float = 0.0
    ) -> OASBenefitResult:
        """
        Calculate comprehensive OAS benefit for a given scenario
        
        Args:
            birth_date: Person's birth date
            calculation_date: Date for calculation
            annual_income: Person's annual income (before OAS)
            years_in_canada: Years of residence in Canada after age 18
            marital_status: "single", "married", "common_law"
            spouse_income: Spouse's annual income (if applicable)
            spouse_age: Spouse's age (for allowance calculations)
            deferral_months: Months OAS was deferred past age 65
            marginal_tax_rate: Current marginal tax rate for benefit analysis
        """
        age = self._calculate_age(birth_date, calculation_date)
        year = calculation_date.year
        params = self.get_parameters(year)
        
        # Check eligibility
        if age < 65 or years_in_canada < params.minimum_residence_years:
            return self._create_zero_result(age, annual_income, years_in_canada, deferral_months)
        
        # Calculate residence factor
        residence_factor = min(years_in_canada, params.full_pension_years) / params.full_pension_years
        
        # Basic OAS calculation
        basic_oas = params.max_annual_oas * residence_factor
        
        # Apply deferral bonus if applicable
        if deferral_months > 0:
            deferral_bonus = min(deferral_months, params.max_deferral_months) * params.deferral_bonus_rate
            basic_oas *= (1 + deferral_bonus)
        
        # Calculate clawback (OAS Recovery Tax)
        clawback = self._calculate_oas_clawback(annual_income, basic_oas, params)
        net_oas = max(0, basic_oas - clawback)
        
        # Calculate GIS if eligible (low income supplement)
        gis_amount = self._calculate_gis(
            annual_income, spouse_income, marital_status, net_oas, params
        )
        
        # Calculate Allowance if spouse is eligible (age 60-64)
        allowance_amount = self._calculate_allowance(
            annual_income, spouse_income, spouse_age, marital_status, net_oas, params
        )
        
        total_benefit = net_oas + gis_amount + allowance_amount
        
        # Calculate effective benefit rate after taxes
        effective_benefit_rate = total_benefit * (1 - marginal_tax_rate) if marginal_tax_rate > 0 else total_benefit
        
        return OASBenefitResult(
            basic_oas_amount=basic_oas,
            clawback_amount=clawback,
            net_oas_amount=net_oas,
            gis_amount=gis_amount,
            allowance_amount=allowance_amount,
            total_benefit=total_benefit,
            deferral_months=deferral_months,
            deferral_bonus_rate=params.deferral_bonus_rate,
            age_at_calculation=age,
            income_tested_against=annual_income,
            years_in_canada=years_in_canada,
            residence_factor=residence_factor,
            marginal_tax_rate_on_oas=marginal_tax_rate,
            effective_benefit_rate=effective_benefit_rate
        )
    
    def _calculate_age(self, birth_date: date, calculation_date: date) -> int:
        """Calculate age in years"""
        return calculation_date.year - birth_date.year - (
            (calculation_date.month, calculation_date.day) < (birth_date.month, birth_date.day)
        )
    
    def _calculate_oas_clawback(self, income: float, oas_amount: float, params: OASParameters) -> float:
        """Calculate OAS clawback (Recovery Tax) based on income"""
        if income <= params.clawback_threshold:
            return 0.0
        
        excess_income = income - params.clawback_threshold
        clawback = excess_income * params.clawback_rate
        return min(clawback, oas_amount)  # Can't clawback more than the benefit
    
    def _calculate_gis(
        self,
        income: float,
        spouse_income: float,
        marital_status: str,
        oas_amount: float,
        params: OASParameters
    ) -> float:
        """Calculate Guaranteed Income Supplement"""
        # GIS is income-tested and reduces with income
        if marital_status.lower() in ["married", "common_law"]:
            max_gis = params.max_monthly_gis_married * 12
            # For couples, combined income minus OAS is tested
            combined_income = income + spouse_income - oas_amount
        else:
            max_gis = params.max_monthly_gis_single * 12
            combined_income = income - oas_amount
        
        if combined_income <= 0:
            return max_gis
        
        # GIS reduces by 50 cents for every dollar of income
        gis_reduction = combined_income * params.gis_reduction_rate
        return max(0, max_gis - gis_reduction)
    
    def _calculate_allowance(
        self,
        income: float,
        spouse_income: float,
        spouse_age: Optional[int],
        marital_status: str,
        oas_amount: float,
        params: OASParameters
    ) -> float:
        """Calculate Allowance for spouse aged 60-64"""
        # Allowance only applies if spouse is 60-64 and married/common-law
        if (not spouse_age or spouse_age < 60 or spouse_age >= 65 or 
            marital_status.lower() not in ["married", "common_law"]):
            return 0.0
        
        combined_income = income + spouse_income - oas_amount
        
        if combined_income <= params.allowance_income_threshold:
            max_allowance = params.max_monthly_allowance * 12
            # Allowance reduces with income similar to GIS
            allowance_reduction = max(0, combined_income) * 0.75  # 75 cents per dollar
            return max(0, max_allowance - allowance_reduction)
        
        return 0.0
    
    def _create_zero_result(self, age: int, income: float, years_in_canada: int, deferral_months: int) -> OASBenefitResult:
        """Create a zero result for ineligible cases"""
        return OASBenefitResult(
            basic_oas_amount=0.0,
            clawback_amount=0.0,
            net_oas_amount=0.0,
            gis_amount=0.0,
            allowance_amount=0.0,
            total_benefit=0.0,
            deferral_months=deferral_months,
            deferral_bonus_rate=0.0,
            age_at_calculation=age,
            income_tested_against=income,
            years_in_canada=years_in_canada,
            residence_factor=0.0,
            marginal_tax_rate_on_oas=0.0,
            effective_benefit_rate=0.0
        )
    
    def calculate_optimal_deferral_strategy(
        self,
        birth_date: date,
        annual_incomes: Dict[int, float],
        years_in_canada: int,
        life_expectancy: int = 85,
        discount_rate: float = 0.02
    ) -> Dict[str, any]:
        """
        Calculate optimal OAS deferral strategy based on lifetime value
        
        Returns analysis of different deferral options (0, 12, 24, 36, 48, 60 months)
        """
        strategies = {}
        
        for deferral_months in [0, 12, 24, 36, 48, 60]:
            total_pv = 0.0
            start_age = 65 + (deferral_months // 12)
            
            for age in range(start_age, life_expectancy + 1):
                year = birth_date.year + age
                calculation_date = date(year, birth_date.month, birth_date.day)
                income = annual_incomes.get(year, 0)
                
                result = self.calculate_oas_benefit(
                    birth_date=birth_date,
                    calculation_date=calculation_date,
                    annual_income=income,
                    years_in_canada=years_in_canada,
                    deferral_months=deferral_months if age == start_age else 0
                )
                
                # Calculate present value
                years_from_now = age - 65
                pv_factor = (1 + discount_rate) ** (-years_from_now)
                total_pv += result.net_oas_amount * pv_factor
            
            strategies[f"defer_{deferral_months}_months"] = {
                "deferral_months": deferral_months,
                "start_age": start_age,
                "lifetime_value_pv": total_pv,
                "monthly_bonus_rate": deferral_months * 0.006 if deferral_months > 0 else 0
            }
        
        # Find optimal strategy
        optimal = max(strategies.values(), key=lambda x: x["lifetime_value_pv"])
        
        return {
            "strategies": strategies,
            "optimal_strategy": optimal,
            "analysis_assumptions": {
                "life_expectancy": life_expectancy,
                "discount_rate": discount_rate,
                "years_in_canada": years_in_canada
            }
        }

@dataclass
class SimpleOASInput:
    """Input data for simple OAS clawback calculator (modal)"""
    rrif_withdrawals: float
    cpp_pension: float
    work_pension: float
    other_income: float
    email_address: str
    recipient_name: str = ""

@dataclass
class SimpleOASResult:
    """Result of simple OAS clawback calculation"""
    total_income: float
    oas_clawback_amount: float
    oas_clawback_percentage: float
    net_oas_amount: float
    effective_tax_rate: float
    recommendations: List[str]
    risk_level: str  # "Low", "Medium", "High"

class SimpleOASClawbackCalculator:
    """Simple OAS Clawback Calculator for the modal interface"""
    
    # 2024 OAS parameters
    MAX_OAS_ANNUAL = 8560.08
    CLAWBACK_THRESHOLD = 90997
    CLAWBACK_RATE = 0.15
    
    def calculate_clawback(self, input_data: SimpleOASInput) -> SimpleOASResult:
        """Calculate OAS clawback based on income inputs"""
        
        # Calculate total income
        total_income = (
            input_data.rrif_withdrawals +
            input_data.cpp_pension +
            input_data.work_pension +
            input_data.other_income
        )
        
        # Calculate OAS clawback
        if total_income <= self.CLAWBACK_THRESHOLD:
            clawback_amount = 0.0
            clawback_percentage = 0.0
        else:
            excess_income = total_income - self.CLAWBACK_THRESHOLD
            clawback_amount = min(excess_income * self.CLAWBACK_RATE, self.MAX_OAS_ANNUAL)
            clawback_percentage = (clawback_amount / self.MAX_OAS_ANNUAL) * 100
        
        # Calculate net OAS amount
        net_oas = self.MAX_OAS_ANNUAL - clawback_amount
        
        # Estimate effective tax rate (simplified)
        effective_tax_rate = self._estimate_effective_tax_rate(total_income)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            total_income, clawback_amount, input_data
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(clawback_percentage)
        
        return SimpleOASResult(
            total_income=total_income,
            oas_clawback_amount=clawback_amount,
            oas_clawback_percentage=clawback_percentage,
            net_oas_amount=net_oas,
            effective_tax_rate=effective_tax_rate,
            recommendations=recommendations,
            risk_level=risk_level
        )
    
    def _estimate_effective_tax_rate(self, total_income: float) -> float:
        """Estimate effective tax rate for Ontario resident"""
        # Simplified tax calculation for Ontario
        if total_income <= 50000:
            return 20.0
        elif total_income <= 75000:
            return 25.0
        elif total_income <= 100000:
            return 30.0
        elif total_income <= 150000:
            return 35.0
        else:
            return 40.0
    
    def _generate_recommendations(
        self, 
        total_income: float, 
        clawback_amount: float, 
        input_data: SimpleOASInput
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if clawback_amount == 0:
            recommendations.append(
                "Great news! Your income is below the OAS clawback threshold. "
                "You'll receive the full OAS benefit."
            )
        elif clawback_amount < self.MAX_OAS_ANNUAL * 0.5:
            recommendations.append(
                "You're experiencing partial OAS clawback. Consider income-splitting "
                "strategies or timing withdrawals to reduce the impact."
            )
        else:
            recommendations.append(
                "You're experiencing significant OAS clawback. Consider deferring "
                "OAS benefits or implementing advanced tax planning strategies."
            )
        
        # RRIF-specific recommendations
        if input_data.rrif_withdrawals > 50000:
            recommendations.append(
                "Your RRIF withdrawals are substantial. Consider converting to a "
                "gradual withdrawal strategy to smooth out your tax burden over time."
            )
        
        # Income splitting recommendations
        if total_income > 100000:
            recommendations.append(
                "With your income level, pension income splitting with a spouse "
                "could significantly reduce your overall tax burden and OAS clawback."
            )
        
        # General tax planning
        recommendations.append(
            "Consider consulting with a financial advisor to explore strategies like "
            "TFSA maximization, charitable giving, or investment loan strategies."
        )
        
        return recommendations
    
    def _determine_risk_level(self, clawback_percentage: float) -> str:
        """Determine risk level based on clawback percentage"""
        if clawback_percentage == 0:
            return "Low"
        elif clawback_percentage < 50:
            return "Medium"
        else:
            return "High"
    
    async def calculate_and_email(self, input_data: SimpleOASInput) -> Dict[str, any]:
        """Calculate OAS clawback and email results with enhanced error handling"""
        import asyncio
        
        try:
            # Import here to avoid circular imports
            from .email_service import OASCalculatorResult, email_service
            
            # Calculate the clawback first (this always works)
            result = self.calculate_clawback(input_data)
            
            # Prepare calculation result for response
            calculation_result = {
                "total_income": result.total_income,
                "oas_clawback_amount": result.oas_clawback_amount,
                "oas_clawback_percentage": result.oas_clawback_percentage,
                "net_oas_amount": result.net_oas_amount,
                "risk_level": result.risk_level,
                "recommendations_count": len(result.recommendations)
            }
            
            # Try to send email with enhanced error handling
            try:
                # Add a small delay to help with rate limiting
                await asyncio.sleep(1)
                
                # Get AI-powered analysis of the results
                try:
                    from .llm_service import explain_oas_calculator_results
                    
                    ai_analysis = await explain_oas_calculator_results(
                        total_income=result.total_income,
                        oas_clawback_amount=result.oas_clawback_amount,
                        oas_clawback_percentage=result.oas_clawback_percentage,
                        net_oas_amount=result.net_oas_amount,
                        risk_level=result.risk_level,
                        rrif_withdrawals=input_data.rrif_withdrawals,
                        cpp_pension=input_data.cpp_pension,
                        work_pension=input_data.work_pension,
                        other_income=input_data.other_income,
                        recipient_name=input_data.recipient_name
                    )
                    
                    # Enhance recommendations with AI insights
                    enhanced_recommendations = result.recommendations.copy()
                    
                    # Add AI-generated insights to recommendations
                    if ai_analysis.get("strategic_insights"):
                        enhanced_recommendations.extend([
                            f"AI Insight: {insight}" for insight in ai_analysis["strategic_insights"]
                        ])
                    
                    # Add AI summary as a recommendation
                    if ai_analysis.get("ai_summary"):
                        enhanced_recommendations.insert(0, f"Expert Analysis: {ai_analysis['ai_summary']}")
                    
                    # Add personalized AI recommendations
                    if ai_analysis.get("personalized_recommendations"):
                        enhanced_recommendations.append(f"Personalized Strategy: {ai_analysis['personalized_recommendations']}")
                    
                    logger.info(f"AI analysis completed for OAS calculator. Enhanced {len(result.recommendations)} basic recommendations to {len(enhanced_recommendations)} AI-enhanced recommendations.")
                    
                except Exception as ai_error:
                    logger.warning(f"AI analysis failed, using basic recommendations: {ai_error}")
                    enhanced_recommendations = result.recommendations
                    ai_analysis = {}
                
                # Prepare email data with enhanced recommendations
                email_result_data = OASCalculatorResult(
                    rrif_withdrawals=input_data.rrif_withdrawals,
                    cpp_pension=input_data.cpp_pension,
                    work_pension=input_data.work_pension,
                    other_income=input_data.other_income,
                    total_income=result.total_income,
                    oas_clawback_amount=result.oas_clawback_amount,
                    oas_clawback_percentage=result.oas_clawback_percentage,
                    net_oas_amount=result.net_oas_amount,
                    effective_tax_rate=result.effective_tax_rate,
                    recommendations=enhanced_recommendations
                )
                
                # Send email with timeout
                email_task = email_service.send_oas_calculator_results(
                    recipient_email=input_data.email_address,
                    calculator_result=email_result_data,
                    recipient_name=input_data.recipient_name
                )
                
                # Wait for email with timeout
                email_result = await asyncio.wait_for(email_task, timeout=45.0)
                
                if email_result.success:
                    return {
                        "success": True,
                        "calculation_result": calculation_result,
                        "email_sent": True,
                        "email_message_id": email_result.message_id,
                        "message": "Calculation completed and results emailed successfully!"
                    }
                else:
                    # Email failed but calculation succeeded
                    logger.warning(f"Email failed for {input_data.email_address}: {email_result.error_message}")
                    return {
                        "success": True,
                        "calculation_result": calculation_result,
                        "email_sent": False,
                        "email_message_id": None,
                        "message": f"Calculation completed successfully. Email delivery failed: {email_result.error_message}. Please try again in a few minutes or contact support.",
                        "error": None
                    }
                    
            except asyncio.TimeoutError:
                logger.error(f"Email timeout for {input_data.email_address}")
                return {
                    "success": True,
                    "calculation_result": calculation_result,
                    "email_sent": False,
                    "email_message_id": None,
                    "message": "Calculation completed successfully. Email delivery timed out. Please try again in a few minutes.",
                    "error": None
                }
                
            except Exception as email_error:
                logger.error(f"Email error for {input_data.email_address}: {email_error}")
                return {
                    "success": True,
                    "calculation_result": calculation_result,
                    "email_sent": False,
                    "email_message_id": None,
                    "message": f"Calculation completed successfully. Email delivery failed: {str(email_error)}. Please try again in a few minutes.",
                    "error": None
                }
            
        except Exception as e:
            logger.error(f"Error in calculate_and_email: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "An error occurred while processing your calculation.",
                "calculation_result": None,
                "email_sent": False,
                "email_message_id": None
            }

# Integration helper for existing tax calculation system
def integrate_oas_with_tax_calculation(
    oas_calculator: OASCalculator,
    birth_date: date,
    calculation_year: int,
    annual_income_before_oas: float,
    years_in_canada: int,
    **kwargs
) -> Tuple[float, float, Dict]:
    """
    Helper function to integrate OAS calculations with existing tax system
    
    Returns: (gross_oas, net_oas_after_clawback, detailed_breakdown)
    """
    calculation_date = date(calculation_year, 12, 31)
    
    result = oas_calculator.calculate_oas_benefit(
        birth_date=birth_date,
        calculation_date=calculation_date,
        annual_income=annual_income_before_oas,
        years_in_canada=years_in_canada,
        **kwargs
    )
    
    detailed_breakdown = {
        "basic_oas": result.basic_oas_amount,
        "clawback": result.clawback_amount,
        "net_oas": result.net_oas_amount,
        "gis": result.gis_amount,
        "total_government_benefits": result.total_benefit,
        "deferral_bonus": result.deferral_months * result.deferral_bonus_rate if result.deferral_months > 0 else 0,
        "residence_factor": result.residence_factor
    }
    
    return result.basic_oas_amount, result.net_oas_amount, detailed_breakdown

# Global instances
oas_calculator = OASCalculator()
simple_oas_calculator = SimpleOASClawbackCalculator()
