"""
Email Service for sending OAS calculator results and reports

Supports multiple email providers:
- SendGrid (recommended)
- Resend (alternative)
- SMTP (fallback for any provider)
"""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader
from ..core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class EmailResult:
    """Result of email sending operation"""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class OASCalculatorResult:
    """OAS Calculator result for email template"""
    rrif_withdrawals: float
    cpp_pension: float
    work_pension: float
    other_income: float
    total_income: float
    oas_clawback_amount: float
    oas_clawback_percentage: float
    net_oas_amount: float
    effective_tax_rate: float
    risk_level: str
    recommendations: List[str]

class EmailService:
    """Service for sending emails via various providers"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "email"
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
    
    async def send_oas_calculator_results(
        self,
        recipient_email: str,
        calculator_result: OASCalculatorResult,
        recipient_name: Optional[str] = None
    ) -> EmailResult:
        """Send OAS calculator results via email"""
        
        try:
            # Render email template
            template = self.jinja_env.get_template("oas_calculator_results.html")
            html_content = template.render(
                recipient_name=recipient_name or "Valued Client",
                result=calculator_result,
                calculation_date=datetime.now().strftime("%B %d, %Y")
            )
            
            # Render plain text version
            text_template = self.jinja_env.get_template("oas_calculator_results.txt")
            text_content = text_template.render(
                recipient_name=recipient_name or "Valued Client",
                result=calculator_result,
                calculation_date=datetime.now().strftime("%B %d, %Y")
            )
            
            subject = "Your OAS Clawback Analysis Results"
            
            # Try SendGrid first, then fallback to other providers
            if settings.SENDGRID_API_KEY:
                return await self._send_via_sendgrid(
                    recipient_email, subject, html_content, text_content
                )
            elif settings.RESEND_API_KEY:
                return await self._send_via_resend(
                    recipient_email, subject, html_content, text_content
                )
            else:
                logger.error("No email service configured")
                return EmailResult(
                    success=False,
                    error_message="Email service not configured"
                )
                
        except Exception as e:
            logger.error(f"Error sending OAS calculator email: {e}")
            return EmailResult(
                success=False,
                error_message=str(e)
            )
    
    async def _send_via_sendgrid(
        self,
        recipient_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> EmailResult:
        """Send email via SendGrid API"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "personalizations": [{
                            "to": [{"email": recipient_email}],
                            "subject": subject
                        }],
                        "from": {
                            "email": settings.FROM_EMAIL,
                            "name": settings.FROM_NAME or "RRIF Strategy Calculator"
                        },
                        "content": [
                            {
                                "type": "text/plain",
                                "value": text_content
                            },
                            {
                                "type": "text/html",
                                "value": html_content
                            }
                        ]
                    }
                )
                
                if response.status_code == 202:
                    return EmailResult(
                        success=True,
                        message_id=response.headers.get("X-Message-Id")
                    )
                else:
                    logger.error(f"SendGrid error: {response.status_code} - {response.text}")
                    return EmailResult(
                        success=False,
                        error_message=f"SendGrid API error: {response.status_code}"
                    )
                    
        except Exception as e:
            logger.error(f"SendGrid request failed: {e}")
            return EmailResult(
                success=False,
                error_message=f"SendGrid request failed: {str(e)}"
            )
    
    async def _send_via_resend(
        self,
        recipient_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        max_retries: int = 3
    ) -> EmailResult:
        """Send email via Resend API with retry logic"""
        
        import asyncio
        
        for attempt in range(max_retries):
            try:
                # Add small delay between retries to avoid rate limiting
                if attempt > 0:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.resend.com/emails",
                        headers={
                            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "from": f"{settings.FROM_NAME or 'RRIF Calculator'} <{settings.FROM_EMAIL}>",
                            "to": [recipient_email],
                            "subject": subject,
                            "html": html_content,
                            "text": text_content
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Email sent successfully via Resend on attempt {attempt + 1}")
                        return EmailResult(
                            success=True,
                            message_id=result.get("id")
                        )
                    elif response.status_code == 429:  # Rate limited
                        logger.warning(f"Rate limited by Resend on attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            continue
                    else:
                        error_text = response.text
                        logger.error(f"Resend error on attempt {attempt + 1}: {response.status_code} - {error_text}")
                        
                        # Don't retry on client errors (4xx except 429)
                        if 400 <= response.status_code < 500 and response.status_code != 429:
                            return EmailResult(
                                success=False,
                                error_message=f"Resend API error: {response.status_code} - {error_text}"
                            )
                        
                        if attempt < max_retries - 1:
                            continue
                        
                        return EmailResult(
                            success=False,
                            error_message=f"Resend API error after {max_retries} attempts: {response.status_code}"
                        )
                        
            except Exception as e:
                logger.error(f"Resend request failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
                
                return EmailResult(
                    success=False,
                    error_message=f"Resend request failed after {max_retries} attempts: {str(e)}"
                )
        
        return EmailResult(
            success=False,
            error_message=f"Failed to send email after {max_retries} attempts"
        )

# Global email service instance
email_service = EmailService()
