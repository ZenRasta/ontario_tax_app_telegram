# app/services/llm.py
from __future__ import annotations

import logging

import httpx
import json

from app.core.config import settings  # Use the singleton settings
from app.data_models.results import SummaryMetrics
from app.data_models.scenario import GoalEnum, ScenarioInput, StrategyCodeEnum

# from app.data_models.strategy import get_strategy_meta # If you have strategy descriptions there

logger = logging.getLogger(__name__)

# Pre-defined blurbs or core ideas for each strategy
STRATEGY_CORE_IDEAS = {
    StrategyCodeEnum.BF: "The 'Bracket Filling' strategy aims to smooth out your taxable income each year by withdrawing just enough from your RRSP/RRIF to bring your total taxable income up to a specific target level (e.g., top of a tax bracket or below OAS clawback threshold).",
    StrategyCodeEnum.GM: "The 'Gradual Meltdown' strategy focuses on withdrawing just enough from your RRSP/RRIF each year to meet your inflation-adjusted spending needs, while ensuring CRA minimums are met. Surplus cash is typically reinvested.",
    StrategyCodeEnum.MIN: "The 'RRIF Minimum Only' strategy is a baseline approach where you only withdraw the absolute minimum required by the Canada Revenue Agency (CRA) from your RRIF each year.",
    StrategyCodeEnum.E65: "The 'Early RRIF Conversion at 65' strategy involves converting some or all of your RRSP to a RRIF at age 65 (or earlier if eligible) to take advantage of the $2,000 pension income tax credit and enable pension income splitting with a spouse sooner.",
    StrategyCodeEnum.CD: "This 'CPP/OAS Delay' strategy involves using your RRSP funds to cover living expenses in your earlier retirement years (e.g., 65-70), allowing you to delay starting your Canada Pension Plan (CPP) and Old Age Security (OAS) benefits. By doing so, these government pensions increase significantly for each year you defer them.",
    StrategyCodeEnum.SEQ: "The 'Spousal Income Splitting' strategy aims to reduce your household's overall tax bill by shifting taxable income (like RRIF withdrawals or eligible pension income) from the higher-income spouse to the lower-income spouse, making use of lower tax brackets and potentially doubling up on credits like the pension income amount.",
    StrategyCodeEnum.IO: "The 'Interest-Offset Loan' strategy is an advanced technique where you might take an investment loan and use RRSP/RRIF withdrawals to pay the loan interest. If structured correctly, the loan interest can be tax-deductible, effectively reducing the net taxable amount of your RRIF withdrawals. This typically involves higher complexity and risk.",
    StrategyCodeEnum.LS: "The 'Lump-Sum Withdrawal' strategy involves taking a larger, one-time withdrawal from your RRSP/RRIF in a specific year. This might be done to fund a large purchase, pay off debt, or strategically realize income in a year where your tax bracket might be lower.",
    StrategyCodeEnum.EBX: "The 'Empty-by-X' strategy focuses on systematically depleting your entire RRSP/RRIF balance by a specific target age (e.g., age 85). This often involves withdrawing more than the CRA minimums each year.",
}

STRATEGY_TRADEOFFS = {
    # ... (Populate with typical trade-offs for each strategy) ...
    StrategyCodeEnum.CD: "A key consideration is that you'll be using more of your RRSP funds earlier. While this boosts your guaranteed government pensions later, it means less private capital for growth or unexpected large expenses in your 60s. This strategy is often best if you anticipate a long life expectancy.",
    StrategyCodeEnum.BF: "While this strategy provides predictable tax rates year to year, it might not always result in the absolute lowest lifetime tax bill, especially if your income needs vary significantly or if tax laws change. It prioritizes smoothness over aggressive tax minimization in any single year.",
    StrategyCodeEnum.EBX: "Depleting your RRIF early means you'll pay taxes on that income sooner, potentially at lower average rates if done carefully. However, it also means those funds are no longer growing tax-deferred within the RRIF, and you'll rely more on other income sources or TFSA/non-registered assets in later old age.",
    StrategyCodeEnum.MIN: "Withdrawing only the minimum preserves capital within your RRIF for longer, allowing for more tax-deferred growth. However, this can lead to larger RRIF balances later in life, potentially pushing you into higher tax brackets or increasing OAS clawback when mandatory withdrawals become very high at older ages. It might also mean underspending relative to your needs if the minimum is low.",
}


async def explain_strategy_with_context(  # noqa: C901

    scenario: ScenarioInput,
    strategy_code: StrategyCodeEnum,
    # strategy_name: str, # Can get from StrategyMeta or build from code
    summary_metrics: SummaryMetrics,
    goal: GoalEnum
) -> dict:
    """
    Calls an LLM to produce an explanation of a strategy's outcomes.

    Returns a dictionary with ``summary``, ``key_outcomes`` and ``recommendations``
    keys populated from the LLM response.
    """
    # Check for available API keys - prefer OpenAI, fallback to OpenRouter
    api_key = None
    base_url = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    
    if settings.OPENAI_API_KEY:
        api_key = settings.OPENAI_API_KEY
        model = "gpt-4o-mini"
        logger.info("Using OpenAI API")
    elif settings.OPENROUTER_API_KEY:
        api_key = settings.OPENROUTER_API_KEY
        base_url = settings.OPENROUTER_BASE_URL
        model = settings.OPENROUTER_MODEL
        logger.info(f"Using OpenRouter API with model: {model}")
    
    if not api_key:
        logger.warning(
            "No LLM API key configured (OPENROUTER_API_KEY or OPENAI_API_KEY). LLM explanation disabled, returning placeholder."
        )
        return {
            "summary": "LLM-generated explanation is currently unavailable as no API key is configured.",
            "key_outcomes": [],
            "recommendations": "",
        }

    # Get strategy metadata (label, blurb) if you have it
    # strategy_meta = get_strategy_meta(strategy_code) # Assuming you have this function
    # strategy_label = strategy_meta.label if strategy_meta else strategy_code.value.replace("_", " ").title()
    # Using a simpler name generation for now
    strategy_label = strategy_code.value.replace("_", " ").title()


    # --- Build the prompt ---
    prompt_parts = [
        "You are a friendly and highly experienced Canadian Certified Financial Planner (CFP), specializing in tax-efficient retirement income planning for Ontario residents aged 55 and older.",
        "Your client has provided their financial situation and a retirement goal. You have run a simulation for a specific withdrawal strategy. Your task is to explain the key outcomes of this strategy and its trade-offs in plain, empathetic English, as if you were advising them directly. Focus on what matters most for their stated goal.",
        "Avoid excessive financial jargon. If a term like 'OAS clawback' or 'marginal tax rate' is essential, briefly explain it.",

        "\n--- Client's Situation & Goal ---",
        f"Your client is {scenario.age} years old.",
    ]
    if scenario.spouse:
        prompt_parts.append(f"Their spouse is {scenario.spouse.age} years old.")

    goal_description = goal.value.replace('_', ' ')
    if goal == GoalEnum.MINIMIZE_TAX:
        goal_description = "minimize their lifetime income tax burden"
    elif goal == GoalEnum.MAXIMIZE_SPENDING:
        goal_description = "maximize their sustainable inflation-adjusted spending throughout retirement"
    elif goal == GoalEnum.PRESERVE_ESTATE:
        goal_description = "maximize the value of the estate they leave to heirs, after all taxes"
    elif goal == GoalEnum.SIMPLIFY:
        goal_description = "simplify their financial affairs and tax situation in retirement"
    prompt_parts.append(f"Their primary retirement goal is to {goal_description}.")

    # Briefly mention key assets
    asset_descriptors = []
    if scenario.rrsp_balance >= 50000: # Arbitrary threshold
        asset_descriptors.append(f"an RRSP/RRIF balance of approximately ${scenario.rrsp_balance:,.0f}")
    if scenario.defined_benefit_pension > 0:
        asset_descriptors.append(f"an annual defined benefit pension of ${scenario.defined_benefit_pension:,.0f}")
    if scenario.tfsa_balance >= 20000:
        asset_descriptors.append(f"a TFSA balance of around ${scenario.tfsa_balance:,.0f}")
    if asset_descriptors:
        prompt_parts.append(f"Key financial elements include: {', '.join(asset_descriptors)}.")

    prompt_parts.append(f"\n--- Strategy Explained: {strategy_label} ({strategy_code.value}) ---")
    prompt_parts.append(STRATEGY_CORE_IDEAS.get(strategy_code, "This strategy involves a specific way of drawing income from your retirement accounts."))


    prompt_parts.append("\n--- Key Projected Outcomes for You (based on your goal) ---")
    # Dynamically select and format key metrics
    key_outcomes_for_goal = []
    if goal == GoalEnum.MINIMIZE_TAX:
        key_outcomes_for_goal.append(f"Projected Lifetime Taxes (Present Value): Approx. ${summary_metrics.lifetime_tax_paid_pv:,.0f}. A lower number here aligns well with your goal.")
        key_outcomes_for_goal.append(f"Years in OAS Clawback: This strategy results in about {summary_metrics.years_in_oas_clawback:.0f} years where some of your Old Age Security might be 'clawed back' due to income levels. (The OAS clawback is an extra 15% tax on income above a certain threshold, currently around $91,000).")
        key_outcomes_for_goal.append(f"Average Effective Tax Rate: Your overall average tax rate with this strategy is projected to be around {summary_metrics.average_effective_tax_rate:.1f}%.")
    elif goal == GoalEnum.MAXIMIZE_SPENDING:
        key_outcomes_for_goal.append(f"Average Annual Real Spending: You could comfortably spend approximately ${summary_metrics.average_annual_real_spending:,.0f} per year (in today's dollars, adjusted for inflation) with this approach.")
        if summary_metrics.ruin_probability_pct is not None: # Only if Monte Carlo was run
            key_outcomes_for_goal.append(f"Sustainability: The chance of outliving your financial resources with this spending level is estimated to be very low, around {summary_metrics.ruin_probability_pct:.1f}%.")
        if summary_metrics.cashflow_coverage_ratio is not None:
            key_outcomes_for_goal.append(f"Spending Coverage: On average, your projected after-tax income covers about {summary_metrics.cashflow_coverage_ratio*100:.0f}% of your desired spending.")
    elif goal == GoalEnum.PRESERVE_ESTATE:
        key_outcomes_for_goal.append(f"Projected Net Value to Heirs (Present Value): After all final taxes, this strategy is estimated to leave an estate of approximately ${summary_metrics.net_value_to_heirs_after_final_taxes_pv:,.0f} in today's dollars.")
        key_outcomes_for_goal.append(f"This compares to a nominal (future dollar) value of about ${summary_metrics.final_total_portfolio_value_nominal:,.0f} at the end of the projection.")
    elif goal == GoalEnum.SIMPLIFY:
        key_outcomes_for_goal.append(f"Strategy Complexity: This strategy has a complexity score of {summary_metrics.strategy_complexity_score} out of 5 (where 1 is simplest).")
        if summary_metrics.tax_volatility_score is not None:
             key_outcomes_for_goal.append(f"Tax Bill Smoothness: The year-to-year fluctuation in your tax bill is relatively {'low' if summary_metrics.tax_volatility_score < 5 else 'moderate' if summary_metrics.tax_volatility_score < 10 else 'high'} (volatility score: {summary_metrics.tax_volatility_score:.1f}).")
        else: # Fallback if no volatility score
            prompt_parts.append("This approach generally leads to a straightforward financial management process year to year.")


    if not key_outcomes_for_goal: # Fallback if goal doesn't have specific metrics above
        key_outcomes_for_goal.append(f"With this '{strategy_label}' approach, your projected lifetime tax (in today's dollars) is about ${summary_metrics.lifetime_tax_paid_pv:,.0f}, and you could expect to spend around ${summary_metrics.average_annual_real_spending:,.0f} per year on average.")

    prompt_parts.extend([f"- {outcome}" for outcome in key_outcomes_for_goal])


    prompt_parts.append("\n--- Important Considerations & Trade-offs ---")
    tradeoff = STRATEGY_TRADEOFFS.get(strategy_code)
    if tradeoff:
        prompt_parts.append(tradeoff)
    else:
        prompt_parts.append("Like any financial strategy, this approach has its pros and cons depending on your specific circumstances and how events unfold. For example, changes in tax laws or investment returns could affect the outcome.")

    prompt_parts.append(
        "\nThis explanation is based on the simulation results and the assumptions you provided. It's a good starting point for our discussion."
    )

    prompt_parts.append(
        "\nPlease respond with a JSON object containing these keys:"
        " summary (a detailed paragraph explaining the strategy and its benefits),"
        " key_outcomes (a list of 3-5 specific bullet points about projected outcomes),"
        " recommendations (a detailed paragraph with specific actionable advice)."
        "\n\nIMPORTANT: Return ONLY valid JSON. Do not include any text before or after the JSON object."
    )

    final_prompt = "\n".join(prompt_parts)
    logger.info(f"Generated LLM prompt for strategy {strategy_code.value}, goal {goal.value}. Prompt length: {len(final_prompt)} chars.")
    # logger.debug(f"LLM Prompt: \n{final_prompt}") # Uncomment for full prompt debugging

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": final_prompt}],
                    "temperature": 0.6,
                    "max_tokens": 500,
                },
            )
            resp.raise_for_status()

            response_data = resp.json()
            if response_data.get("choices"):
                content = response_data["choices"][0]["message"].get("content", "")
                logger.info(
                    f"LLM explanation received successfully for {strategy_code.value}."
                )
                try:
                    # Try to parse as JSON first
                    parsed_content = json.loads(content)
                    return parsed_content
                except json.JSONDecodeError:
                    logger.warning(
                        "Failed to parse JSON from LLM response, attempting to extract content: %s", content[:200]
                    )
                    # Try to extract JSON from the content if it's wrapped in other text
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        try:
                            return json.loads(json_match.group())
                        except json.JSONDecodeError:
                            pass
                    
                    # Fallback: try to parse the content manually
                    lines = content.strip().split('\n')
                    summary = ""
                    key_outcomes = []
                    recommendations = ""
                    
                    current_section = None
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if 'summary' in line.lower() or current_section is None:
                            current_section = 'summary'
                            if ':' in line:
                                summary += line.split(':', 1)[1].strip() + " "
                            else:
                                summary += line + " "
                        elif 'outcome' in line.lower() or 'key' in line.lower():
                            current_section = 'outcomes'
                        elif 'recommend' in line.lower():
                            current_section = 'recommendations'
                        elif current_section == 'outcomes' and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                            key_outcomes.append(line.lstrip('•-* '))
                        elif current_section == 'recommendations':
                            recommendations += line + " "
                    
                    return {
                        "summary": summary.strip() or content.strip(),
                        "key_outcomes": key_outcomes or [content.strip()],
                        "recommendations": recommendations.strip() or "Please consult with a financial advisor for personalized advice.",
                    }
            else:
                logger.error(
                    f"LLM response missing expected structure for {strategy_code.value}. Response: {response_data}"
                )
                return {
                    "summary": "Could not generate an explanation due to an unexpected response format from the AI service.",
                    "key_outcomes": [],
                    "recommendations": "",
                }

    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API request failed for {strategy_code.value} with status {e.response.status_code}: {e.response.text}", exc_info=False)
        error_detail = f"AI explanation service returned an error (Status {e.response.status_code})."
        if e.response.status_code == 401:
            error_detail = "AI explanation service authentication failed. Please check API key."
        elif e.response.status_code == 429:
            error_detail = "AI explanation service rate limit exceeded. Please try again later."
        return {
            "summary": f"Could not generate an explanation at this time. ({error_detail})",
            "key_outcomes": [],
            "recommendations": "",
        }
    except httpx.RequestError as e:
        logger.error(f"LLM API request error for {strategy_code.value}: {e}", exc_info=True)
        return {
            "summary": "Could not connect to the AI explanation service. Please check your network connection or try again later.",
            "key_outcomes": [],
            "recommendations": "",
        }
    except Exception as e:
        logger.error(f"Unexpected error during LLM explanation for {strategy_code.value}: {e}", exc_info=True)
        return {
            "summary": "An unexpected error occurred while generating the AI explanation.",
            "key_outcomes": [],
            "recommendations": "",
        }

async def explain_oas_calculator_results(
    total_income: float,
    oas_clawback_amount: float,
    oas_clawback_percentage: float,
    net_oas_amount: float,
    risk_level: str,
    rrif_withdrawals: float,
    cpp_pension: float,
    work_pension: float,
    other_income: float,
    recipient_name: str = ""
) -> dict:
    """
    Calls an LLM to provide AI-powered interpretation of OAS calculator results.
    
    Returns a dictionary with enhanced recommendations and insights.
    """
    # Check for available API keys - prefer OpenAI, fallback to OpenRouter
    api_key = None
    base_url = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    
    if settings.OPENAI_API_KEY:
        api_key = settings.OPENAI_API_KEY
        model = "gpt-4o-mini"
        logger.info("Using OpenAI API for OAS analysis")
    elif settings.OPENROUTER_API_KEY:
        api_key = settings.OPENROUTER_API_KEY
        base_url = settings.OPENROUTER_BASE_URL
        model = settings.OPENROUTER_MODEL
        logger.info(f"Using OpenRouter API for OAS analysis with model: {model}")
    
    if not api_key:
        logger.warning(
            "No LLM API key configured (OPENROUTER_API_KEY or OPENAI_API_KEY). LLM explanation disabled, returning basic recommendations."
        )
        return {
            "ai_summary": "AI-powered analysis is currently unavailable.",
            "strategic_insights": [],
            "personalized_recommendations": "Please consult with a financial advisor for personalized advice.",
            "risk_assessment": f"Your OAS clawback risk level is {risk_level}."
        }

    # Build the prompt for OAS analysis
    prompt_parts = [
        "You are a highly experienced Canadian Certified Financial Planner (CFP) specializing in retirement income tax planning for Ontario residents.",
        f"Your client{' ' + recipient_name if recipient_name else ''} has used an OAS Clawback Calculator and received their results. Your task is to provide expert analysis and actionable recommendations based on their specific situation.",
        "Focus on practical, implementable strategies that can help optimize their retirement income and minimize OAS clawback impact.",
        
        "\n--- Client's OAS Clawback Analysis Results ---",
        f"Total Annual Income: ${total_income:,.0f}",
        f"- RRIF/RRSP Withdrawals: ${rrif_withdrawals:,.0f}",
        f"- CPP Pension: ${cpp_pension:,.0f}",
        f"- Work/Other Pension: ${work_pension:,.0f}",
        f"- Other Income: ${other_income:,.0f}",
        "",
        f"OAS Clawback Analysis:",
        f"- Annual OAS Clawback: ${oas_clawback_amount:,.0f}",
        f"- Clawback Percentage: {oas_clawback_percentage:.1f}% of total OAS benefit",
        f"- Net OAS Benefit: ${net_oas_amount:,.0f} annually",
        f"- Risk Level: {risk_level}",
        "",
        "Context: The 2024 OAS clawback threshold is $90,997. Above this income level, OAS benefits are reduced by 15% of the excess income.",
        
        "\n--- Your Expert Analysis Task ---",
        "Provide a comprehensive analysis that includes:",
        "1. Strategic insights about their current income structure and OAS impact",
        "2. Specific, actionable recommendations to optimize their situation",
        "3. Tax planning strategies they should consider",
        "4. Timing considerations for income management",
        
        "\nConsider strategies such as:",
        "- Income splitting with spouse (if applicable)",
        "- RRIF withdrawal timing and amounts",
        "- Pension income splitting opportunities",
        "- TFSA maximization strategies",
        "- Charitable giving tax benefits",
        "- OAS deferral strategies",
        "- Investment loan strategies (if appropriate)",
        
        "\nPlease respond with a JSON object containing these keys:",
        "- ai_summary: A comprehensive 2-3 sentence overview of their situation and key opportunities",
        "- strategic_insights: A list of 3-4 specific insights about their income structure and tax implications",
        "- personalized_recommendations: A detailed paragraph with specific, actionable advice tailored to their situation",
        "- risk_assessment: A brief assessment of their OAS clawback risk and what it means for their retirement planning",
        
        "\nIMPORTANT: Return ONLY valid JSON. Do not include any text before or after the JSON object. Be specific and actionable in your recommendations."
    ]

    final_prompt = "\n".join(prompt_parts)
    logger.info(f"Generated LLM prompt for OAS calculator analysis. Total income: ${total_income:,.0f}, Clawback: ${oas_clawback_amount:,.0f}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": final_prompt}],
                    "temperature": 0.7,
                    "max_tokens": 800,
                },
            )
            resp.raise_for_status()

            response_data = resp.json()
            if response_data.get("choices"):
                content = response_data["choices"][0]["message"].get("content", "")
                logger.info("LLM OAS analysis received successfully.")
                
                try:
                    # Try to parse as JSON first
                    parsed_content = json.loads(content)
                    return parsed_content
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from LLM response, attempting to extract content")
                    
                    # Try to extract JSON from the content if it's wrapped in other text
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        try:
                            return json.loads(json_match.group())
                        except json.JSONDecodeError:
                            pass
                    
                    # Fallback: create structured response from content
                    return {
                        "ai_summary": f"Based on your total income of ${total_income:,.0f}, you have a {risk_level.lower()} risk OAS clawback situation with ${oas_clawback_amount:,.0f} annual clawback.",
                        "strategic_insights": [
                            f"Your income is ${total_income - 90997:,.0f} {'above' if total_income > 90997 else 'below'} the OAS clawback threshold",
                            f"RRIF withdrawals represent {(rrif_withdrawals/total_income)*100:.1f}% of your total income",
                            f"You're retaining {(net_oas_amount/8560.08)*100:.1f}% of your maximum OAS benefit"
                        ],
                        "personalized_recommendations": content.strip() if content.strip() else "Consider consulting with a financial advisor to explore income splitting strategies, RRIF withdrawal timing optimization, and tax-efficient investment approaches to minimize OAS clawback impact.",
                        "risk_assessment": f"Your {risk_level.lower()} risk level indicates {'minimal impact' if risk_level == 'Low' else 'moderate impact' if risk_level == 'Medium' else 'significant impact'} on your OAS benefits."
                    }
            else:
                logger.error("LLM response missing expected structure for OAS analysis")
                return _get_fallback_oas_analysis(total_income, oas_clawback_amount, risk_level, rrif_withdrawals)

    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API request failed for OAS analysis with status {e.response.status_code}")
        return _get_fallback_oas_analysis(total_income, oas_clawback_amount, risk_level, rrif_withdrawals)
    except Exception as e:
        logger.error(f"Unexpected error during LLM OAS analysis: {e}")
        return _get_fallback_oas_analysis(total_income, oas_clawback_amount, risk_level, rrif_withdrawals)

def _get_fallback_oas_analysis(total_income: float, oas_clawback_amount: float, risk_level: str, rrif_withdrawals: float) -> dict:
    """Fallback analysis when LLM is unavailable"""
    if oas_clawback_amount == 0:
        summary = f"Excellent news! With your total income of ${total_income:,.0f}, you're below the OAS clawback threshold and will receive your full OAS benefit."
        recommendations = "Continue monitoring your income levels to ensure you stay below the clawback threshold. Consider maximizing TFSA contributions and exploring tax-efficient investment strategies."
    else:
        summary = f"With your total income of ${total_income:,.0f}, you're experiencing ${oas_clawback_amount:,.0f} in annual OAS clawback, representing a {risk_level.lower()} risk situation."
        recommendations = "Consider income splitting strategies with your spouse, optimizing RRIF withdrawal timing, and exploring pension income splitting to reduce your overall tax burden and OAS clawback."
    
    return {
        "ai_summary": summary,
        "strategic_insights": [
            f"Your income is ${abs(total_income - 90997):,.0f} {'above' if total_income > 90997 else 'below'} the OAS clawback threshold",
            f"RRIF withdrawals represent {(rrif_withdrawals/total_income)*100:.1f}% of your total income",
            "Income timing and splitting strategies could help optimize your situation"
        ],
        "personalized_recommendations": recommendations,
        "risk_assessment": f"Your {risk_level.lower()} risk level suggests {'minimal' if risk_level == 'Low' else 'moderate' if risk_level == 'Medium' else 'significant'} impact on your retirement income planning."
    }

# Example of how you might call it from an endpoint (conceptual)
# async def get_explanation_endpoint(
#     scenario_input: ScenarioInput,
#     strat_code: StrategyCodeEnum,
#     summary: SummaryMetrics,
#     user_goal: GoalEnum
# ):
#     data = await explain_strategy_with_context(scenario_input, strat_code, summary, user_goal)
#     return data
