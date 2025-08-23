from __future__ import annotations

from typing import Optional

from backend.app.core.config import settings
from backend.app.data_models.results import SummaryMetrics
from backend.app.data_models.scenario import GoalEnum, ScenarioInput, StrategyCodeEnum
from backend.app.services.llm_service import explain_strategy_with_context
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


def _load_token() -> str:
    token: Optional[str] = settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    return token


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Welcome to the Ontario Tax Bot! Send a strategy code like BF or GM to get an explanation."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    codes = ", ".join([c.value for c in StrategyCodeEnum])
    await update.message.reply_text(
        "Send one of the strategy codes ({}).".format(codes)
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    text = update.message.text.strip().upper()
    try:
        strategy = StrategyCodeEnum[text]
    except KeyError:
        await update.message.reply_text("Unknown strategy code. Try /help for options.")
        return

    scenario = ScenarioInput(
        age=65,
        rrsp_balance=500_000,
        defined_benefit_pension=0,
        cpp_at_65=8_000,
        oas_at_65=8_000,
        tfsa_balance=0,
        desired_spending=60_000,
        expect_return_pct=5,
        stddev_return_pct=8,
        life_expectancy_years=25,
        goal=GoalEnum.MINIMIZE_TAX,
    )
    summary = SummaryMetrics(
        lifetime_tax_paid_nominal=0,
        lifetime_tax_paid_pv=0,
        average_effective_tax_rate=0,
        average_marginal_tax_rate_on_rrif=0,
        years_in_oas_clawback=0,
        total_oas_clawback_paid_nominal=0,
        tax_volatility_score=0,
        max_sustainable_spending_pv=0,
        average_annual_real_spending=0,
        cashflow_coverage_ratio=0,
        ruin_probability_pct=0,
        years_to_ruin_percentile_10=0,
        final_total_portfolio_value_nominal=0,
        final_total_portfolio_value_pv=0,
        net_value_to_heirs_after_final_taxes_pv=0,
        sequence_risk_score=0,
        strategy_complexity_score=1,
    )
    result = await explain_strategy_with_context(
        scenario=scenario,
        strategy_code=strategy,
        summary_metrics=summary,
        goal=scenario.goal,
    )
    message = result.get("summary") or "No response."
    await update.message.reply_text(message)


def main() -> None:
    application = ApplicationBuilder().token(_load_token()).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.run_polling()


if __name__ == "__main__":
    main()
