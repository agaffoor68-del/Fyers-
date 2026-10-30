from openai import OpenAI
import os
import json
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.db.models.models import AILearningLog, AIConversation
from app.core.indicator_engine import IndicatorEngine

load_dotenv()

logger = logging.getLogger("GrokAgent")


class GrokAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
        )
        self.model = "grok-beta"
        self.indicator_engine = IndicatorEngine()

    # ------------------------------------------------------------------
    # Indicator toolkit for system prompt
    # ------------------------------------------------------------------
    def _get_indicator_toolkit_prompt(self) -> str:
        """Build a system prompt section listing all available indicators
        grouped by category, using get_all_indicators()."""
        all_indicators = self.indicator_engine.get_all_indicators()
        categories = all_indicators.get("categories", {})

        prompt = """
=== AVAILABLE TECHNICAL INDICATORS (pandas_ta toolkit - 100+) ===

You have full access to 130+ technical indicators via pandas_ta.
They are grouped by category below. Each indicator has default parameters
and an 'overlay' flag (True = overlays on price chart, False = sub-chart).

"""

        for cat_name, indicators in categories.items():
            prompt += f"\n{cat_name.upper()}:\n"
            for ind in indicators:
                overlay_tag = "[OVERLAY]" if ind["overlay"] else "[SUB-CHART]"
                params_str = ", ".join(
                    f"{k}={v}" for k, v in ind["default_params"].items()
                ) or "(no params)"
                prompt += (
                    f"  {ind['name']}({params_str}) {overlay_tag} - "
                    f"{ind['description']}\n"
                )

        prompt += """
INDICATOR CONFIG FORMAT:
  {"name": "rsi", "length": 14}
  {"name": "macd", "fast": 12, "slow": 26, "signal": 9}
  {"name": "bbands", "length": 20, "std": 2.0}
  {"name": "ema", "length": 50}

S&R LEVELS:
You can also reference S&R levels calculated separately:
  - pivot_points: P, R1, R2, R3, S1, S2, S3
  - fibonacci: 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%
  - local_resistance: array of {price, strength}
  - local_support: array of {price, strength}

OUTPUT FORMAT (STRICT JSON):
You must output a valid JSON object with these exact keys:
{
  "strategy_name": "string",
  "description": "string",
  "indicators": [{"name": "rsi", "length": 14}, {"name": "supertrend", "length": 10}],
  "rules": "BUY when RSI_14 < 30 AND close > pivot_points.P AND close > supertrend_SUPERT_10_3.0. SELL when RSI_14 > 70 OR close < local_support[0].price.",
  "stop_loss_pct": 2.0,
  "take_profit_pct": 4.0
}

RULES:
1. Output ONLY valid JSON - no markdown code blocks, no explanatory text outside JSON
2. Always include stop_loss_pct and take_profit_pct
3. Reference exact column names from pandas_ta output (e.g., RSI_14, EMA_50, MACD_12_26_9)
4. For S&R, reference: pivot_points.P, pivot_points.R1, etc.
5. NEVER repeat strategies from the failure log below
6. Consider market volatility and slippage in parameter selection
7. Prioritize capital preservation and risk-adjusted returns
8. Learn from past failures
"""
        return prompt

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------
    def get_ai_memory(self, db: Session, limit: int = 5) -> str:
        """Fetch the last N failures from AILearningLog and inject into context"""
        failures = db.query(AILearningLog).order_by(
            AILearningLog.timestamp.desc()
        ).limit(limit).all()

        if not failures:
            return "No previous failures recorded. Learn from first principles."

        memory_context = "=== PREVIOUS FAILURES & LESSONS (DO NOT REPEAT) ===\n\n"
        for i, failure in enumerate(failures, 1):
            memory_context += f"FAILURE #{i}:\n"
            memory_context += f"Strategy: {failure.strategy_used}\n"
            memory_context += f"Mistake Context: {failure.mistake_context}\n"
            memory_context += f"Reason Failed: {failure.reason_failed}\n"
            memory_context += f"Lesson Learned: {failure.lesson_learned}\n"
            memory_context += f"Time: {failure.timestamp}\n"
            memory_context += "-" * 50 + "\n\n"

        return memory_context

    # ------------------------------------------------------------------
    # Strategy generation
    # ------------------------------------------------------------------
    def generate_strategy(
        self, db: Session, market_data=None, user_request=""
    ) -> Dict[str, Any]:
        """
        Generate a strategy JSON from Grok using memory injection and
        the full pandas_ta indicator toolkit.
        """
        memory = self.get_ai_memory(db, limit=5)
        toolkit = self._get_indicator_toolkit_prompt()

        system_prompt = f"""{toolkit}

{memory}

Your objective: Generate profitable, risk-managed trading strategies
with HIGH WIN RATE using the available technical indicators and S&R levels.

Rules:
- Output ONLY valid JSON, no markdown code blocks
- NEVER repeat mistakes from the failure log above
- Always include stop-loss and take-profit
- Consider market volatility and slippage
- Prioritize capital preservation
- Focus on risk-adjusted returns
- Learn from past failures

Current Request: {user_request}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            "Generate a trading strategy as valid JSON. "
                            f"{user_request}"
                        ),
                    },
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            content = response.choices[0].message.content

            # Try to parse JSON from the response
            try:
                cleaned = content.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()

                strategy_json = json.loads(cleaned)
                return {
                    "success": True,
                    "strategy": strategy_json,
                    "raw_response": content,
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Grok JSON: {e}")
                logger.error(f"Raw response: {content}")
                return {
                    "success": False,
                    "error": f"JSON parse error: {str(e)}",
                    "raw_response": content,
                }

        except Exception as e:
            logger.error(f"Error generating strategy: {e}")
            return {"success": False, "error": str(e)}

    def chat(self, db: Session, message: str, session_id: str) -> str:
        """Chat with Grok AI with memory context"""
        memory = self.get_ai_memory(db, limit=3)

        system_prompt = f"""You are Grok AI, the brain of this trading platform.
        You have access to historical failures and must learn from them.

        {self._get_indicator_toolkit_prompt()}

        {memory}

        Be concise, actionable, and focus on profitable trading insights."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                temperature=0.8,
                max_tokens=1500,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def auto_optimize(self, db: Session) -> Dict[str, Any]:
        """Auto-optimize strategies based on memory"""
        memory = self.get_ai_memory(db, limit=5)
        return self.generate_strategy(
            db,
            user_request=(
                "Auto-optimize all active strategies. "
                "Analyze recent failures and generate an improved multi-indicator strategy. "
                f"{memory}"
            ),
        )
