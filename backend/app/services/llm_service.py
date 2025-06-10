# app/services/llm.py
from __future__ import annotations

import logging

import httpx

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
) -> str:
    """
    Calls an LLM to produce a plain-English explanation of a strategy's
    outcomes given the user's scenario and goals.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set. LLM explanation disabled, returning placeholder.")
        return "LLM-generated explanation is currently unavailable as the API key is not configured."

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
        "\nThis explanation is based on the simulation results and the assumptions you provided. It's a good starting point for our discussion. How does this sound to you?"
    )

    final_prompt = "\n".join(prompt_parts)
    logger.info(f"Generated LLM prompt for strategy {strategy_code.value}, goal {goal.value}. Prompt length: {len(final_prompt)} chars.")
    # logger.debug(f"LLM Prompt: \n{final_prompt}") # Uncomment for full prompt debugging

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}",
                json={
                    "contents": [{"parts": [{"text": final_prompt}]}],
                    "generationConfig": {"temperature": 0.6, "maxOutputTokens": 500},
                },
            )
            resp.raise_for_status()

            response_data = resp.json()
            if response_data.get("candidates"):
                content = (
                    response_data["candidates"][0]["content"]["parts"][0].get("text", "")
                )
                logger.info(
                    f"LLM explanation received successfully for {strategy_code.value}."
                )
                return content.strip()
            else:
                logger.error(
                    f"LLM response missing expected structure for {strategy_code.value}. Response: {response_data}"
                )
                return "Could not generate an explanation due to an unexpected response format from the AI service."

    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API request failed for {strategy_code.value} with status {e.response.status_code}: {e.response.text}", exc_info=False)
        error_detail = f"AI explanation service returned an error (Status {e.response.status_code})."
        if e.response.status_code == 401:
            error_detail = "AI explanation service authentication failed. Please check API key."
        elif e.response.status_code == 429:
            error_detail = "AI explanation service rate limit exceeded. Please try again later."
        return f"Could not generate an explanation at this time. ({error_detail})"
    except httpx.RequestError as e:
        logger.error(f"LLM API request error for {strategy_code.value}: {e}", exc_info=True)
        return "Could not connect to the AI explanation service. Please check your network connection or try again later."
    except Exception as e:
        logger.error(f"Unexpected error during LLM explanation for {strategy_code.value}: {e}", exc_info=True)
        return "An unexpected error occurred while generating the AI explanation."

# Example of how you might call it from an endpoint (conceptual)
# async def get_explanation_endpoint(
#     scenario_input: ScenarioInput,
#     strat_code: StrategyCodeEnum,
#     summary: SummaryMetrics,
#     user_goal: GoalEnum
# ):
#     explanation = await explain_strategy_with_context(scenario_input, strat_code, summary, user_goal)
#     return {"explanation": explanation}
