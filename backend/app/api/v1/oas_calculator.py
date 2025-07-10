"""
OAS Clawback Calculator API Endpoint

Provides a simple API for the OAS clawback calculator modal functionality.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

from ...services.oas_calculator import SimpleOASInput, simple_oas_calculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oas-calculator", tags=["OAS Calculator"])

class OASCalculatorRequest(BaseModel):
    """Request model for OAS clawback calculation"""
    rrif_withdrawals: float = Field(..., ge=0, description="Annual RRIF/RRSP withdrawals in CAD")
    cpp_pension: float = Field(..., ge=0, description="Annual CPP pension income in CAD")
    work_pension: float = Field(..., ge=0, description="Annual work/other pension income in CAD")
    other_income: float = Field(..., ge=0, description="Other annual income in CAD")
    email_address: EmailStr = Field(..., description="Email address to send results")
    recipient_name: Optional[str] = Field("", description="Recipient name for personalization")

    class Config:
        json_schema_extra = {
            "example": {
                "rrif_withdrawals": 25000,
                "cpp_pension": 15000,
                "work_pension": 30000,
                "other_income": 5000,
                "email_address": "user@example.com",
                "recipient_name": "John Smith"
            }
        }

class OASCalculatorResponse(BaseModel):
    """Response model for OAS clawback calculation"""
    success: bool
    message: str
    calculation_result: Optional[dict] = None
    email_sent: bool = False
    email_message_id: Optional[str] = None
    error: Optional[str] = None

@router.post("/calculate", response_model=OASCalculatorResponse)
async def calculate_oas_clawback(
    request: OASCalculatorRequest,
    background_tasks: BackgroundTasks
):
    """
    Calculate OAS clawback and email results
    
    This endpoint:
    1. Calculates OAS clawback based on income inputs
    2. Generates personalized recommendations
    3. Emails the detailed results to the user
    4. Returns a summary of the calculation
    """
    try:
        # Convert request to internal format
        input_data = SimpleOASInput(
            rrif_withdrawals=request.rrif_withdrawals,
            cpp_pension=request.cpp_pension,
            work_pension=request.work_pension,
            other_income=request.other_income,
            email_address=request.email_address,
            recipient_name=request.recipient_name or ""
        )
        
        # Calculate and email results
        result = await simple_oas_calculator.calculate_and_email(input_data)
        
        return OASCalculatorResponse(
            success=result["success"],
            message=result["message"],
            calculation_result=result.get("calculation_result"),
            email_sent=result.get("email_sent", False),
            email_message_id=result.get("email_message_id"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error in OAS calculator endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your calculation: {str(e)}"
        )

@router.get("/parameters")
async def get_oas_parameters():
    """
    Get current OAS parameters for reference
    
    Returns the current year's OAS thresholds and rates.
    """
    try:
        return {
            "year": 2024,
            "max_oas_annual": simple_oas_calculator.MAX_OAS_ANNUAL,
            "clawback_threshold": simple_oas_calculator.CLAWBACK_THRESHOLD,
            "clawback_rate": simple_oas_calculator.CLAWBACK_RATE,
            "description": {
                "max_oas_annual": "Maximum annual OAS benefit (CAD)",
                "clawback_threshold": "Income threshold where OAS clawback begins (CAD)",
                "clawback_rate": "Rate at which OAS is clawed back (15% of excess income)"
            }
        }
    except Exception as e:
        logger.error(f"Error getting OAS parameters: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving OAS parameters"
        )

@router.post("/calculate-only", response_model=dict)
async def calculate_oas_clawback_only(request: OASCalculatorRequest):
    """
    Calculate OAS clawback without sending email
    
    This endpoint only performs the calculation and returns results
    without sending an email. Useful for preview or testing.
    """
    try:
        # Convert request to internal format
        input_data = SimpleOASInput(
            rrif_withdrawals=request.rrif_withdrawals,
            cpp_pension=request.cpp_pension,
            work_pension=request.work_pension,
            other_income=request.other_income,
            email_address=request.email_address,
            recipient_name=request.recipient_name or ""
        )
        
        # Calculate only (no email)
        result = simple_oas_calculator.calculate_clawback(input_data)
        
        return {
            "success": True,
            "total_income": result.total_income,
            "oas_clawback_amount": result.oas_clawback_amount,
            "oas_clawback_percentage": result.oas_clawback_percentage,
            "net_oas_amount": result.net_oas_amount,
            "effective_tax_rate": result.effective_tax_rate,
            "risk_level": result.risk_level,
            "recommendations": result.recommendations,
            "summary": {
                "clawback_status": "No clawback" if result.oas_clawback_amount == 0 
                                 else f"${result.oas_clawback_amount:,.0f} clawback ({result.oas_clawback_percentage:.1f}%)",
                "net_benefit": f"${result.net_oas_amount:,.0f} annual OAS benefit",
                "risk_assessment": f"{result.risk_level} risk level"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in OAS calculator (calculation only): {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while calculating: {str(e)}"
        )
