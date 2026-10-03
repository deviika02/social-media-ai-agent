"""
agent.py
--------
This file contains the "brain" of our application: the SentimentAgent.

WHAT MAKES THIS AN "AI AGENT" (not just an API call)?
An AI agent is a piece of software that:
  1. Receives a goal / task (analyze a comment).
  2. Decides HOW to accomplish that task (builds a specific prompt).
  3. Uses a tool (here, the OpenAI LLM) to do the work.
  4. Checks / validates the result before trusting it (structured output validation).
  5. Handles things going wrong (errors, bad data) and recovers gracefully.
  6. Returns a clean, structured answer that the rest of the app can use.

A plain "API call" would just send text and blindly return whatever came back.
Our SentimentAgent instead plans the request, enforces a strict output format,
validates every field, fills in safe defaults if something is missing, and
reports clear errors. That decision-making + validation loop is the "agent" part.
"""

import os
import json
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError


# ---------------------------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------------------------
# This is the instruction we give the AI model every single time. It tells
# the model exactly what job to do and exactly what format to reply in.
# A strong, detailed system prompt is what makes the AI's output reliable.
SYSTEM_PROMPT = """You are a Social Media Sentiment Analysis AI Agent.

Your job is to carefully read a single social media comment (it may contain
slang, emojis, sarcasm, typos, abbreviations, or mixed opinions) and analyze it.

You must identify:
1. sentiment - one of: "Positive", "Negative", "Neutral", "Mixed"
2. emotion - the single most fitting emotion word describing the writer's
   feeling (for example: Happy, Angry, Sad, Disappointed, Excited, Satisfied,
   Frustrated, Neutral, or another accurate word if none of those fit well).
3. positive_aspects - a list of short phrases describing what the person liked
   (empty list if none).
4. negative_aspects - a list of short phrases describing what the person disliked
   (empty list if none).
5. topics - a list of general topics/categories the comment is about
   (e.g. "Camera", "Battery", "Customer Service", "Delivery", "Price").
6. keywords - a list of 3 to 8 important words or short phrases from the comment.
7. confidence - a number between 0 and 1 representing how confident you are
   in this analysis.
8. explanation - one or two clear, simple sentences explaining your reasoning.

IMPORTANT RULES:
- Sarcasm should be interpreted by its REAL intended meaning, not the literal words.
- Short comments, emojis, and informal language must still be analyzed sensibly.
- If the comment is empty, unclear, or has no real content, set sentiment to
  "Neutral", use empty lists where appropriate, and explain why in "explanation".
- Reply with ONLY a single valid JSON object. No markdown formatting, no code
  fences, no extra commentary, and no text before or after the JSON.

The JSON object must exactly follow this shape:
{
  "sentiment": "Positive" | "Negative" | "Neutral" | "Mixed",
  "emotion": "string",
  "positive_aspects": ["string", ...],
  "negative_aspects": ["string", ...],
  "topics": ["string", ...],
  "keywords": ["string", ...],
  "confidence": 0.0,
  "explanation": "string"
}
"""


class SentimentAgent:
    """
    A simple AI agent that analyzes the sentiment of a social media comment.

    How to use:
        agent = SentimentAgent()
        result = agent.analyze_comment("I love this phone but the battery is bad!")
        print(result["sentiment"])
    """

    def __init__(self):
        # Step 1: Load the API key from the environment (set via .env file).
        # We're using Google's Gemini API here (it has a free tier with no
        # credit card required). Gemini offers an "OpenAI-compatible" endpoint,
        # so we can keep using the same `openai` Python library and code
        # structure — we just point it at Google's servers instead of OpenAI's.
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key or api_key.strip() == "" or api_key == "your_api_key_here":
            # We raise a clear, friendly error instead of a confusing crash.
            raise ValueError(
                "GEMINI_API_KEY is missing. Please create a .env file with your "
                "free Gemini API key. See .env.example for the correct format."
            )

        # Step 2: Create the client, pointed at Gemini's OpenAI-compatible URL.
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        # Step 3: Pick the model to use. gemini-2.5-flash-lite is free, fast,
        # and has the highest free-tier rate limits — great for a learning project.
        self.model = "gemini-3.5-flash-lite"

        # Step 4: Store the system prompt (the agent's "instructions").
        self.system_prompt = SYSTEM_PROMPT

    def analyze_comment(self, comment: str) -> dict:
        """
        This is the main "agent loop" for a single comment:
          1. Understand the task (analyze this comment).
          2. Decide what to send to the LLM (system prompt + comment).
          3. Call the LLM and ask for structured JSON.
          4. Parse and validate the JSON response.
          5. Return clean, safe Python data (a dictionary) to the caller.

        Returns a dictionary. If something goes wrong, the dictionary will
        contain an "error" key explaining what happened, and safe default
        values for every other field so the app never crashes.
        """

        # --- Step A: Basic input validation (the agent checks its own input) ---
        if comment is None or str(comment).strip() == "":
            return self._error_result("The comment is empty. Please enter some text.")

        comment = str(comment).strip()

        try:
            # --- Step B: Ask the LLM to do the analysis ---
            # We use "response_format": {"type": "json_object"} so the model
            # is forced to reply with valid JSON. This is a key technique for
            # getting structured, reliable output from an LLM.
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Analyze this comment:\n\n{comment}"},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  # Lower temperature = more consistent, reliable output
                max_tokens=500,
            )

            raw_text = response.choices[0].message.content

            # --- Step C: Parse the JSON text into a Python dictionary ---
            parsed = json.loads(raw_text)

            # --- Step D: Validate the parsed data before trusting it ---
            validated = self._validate_and_clean(parsed)
            return validated

        # --- Step E: Handle every kind of failure with a friendly message ---
        except AuthenticationError:
            return self._error_result(
                "Invalid Gemini API key. Please check your .env file and make "
                "sure the key is correct."
            )
        except RateLimitError:
            return self._error_result(
                "Gemini free-tier rate limit reached (too many requests too "
                "quickly). Please wait about a minute and try again."
            )
        except APIConnectionError:
            return self._error_result(
                "Could not connect to Gemini. Please check your internet connection."
            )
        except APIError as e:
            return self._error_result(f"Gemini API returned an error: {str(e)}")
        except json.JSONDecodeError:
            return self._error_result(
                "The AI returned a response that was not valid JSON. Please try again."
            )
        except Exception as e:
            # Catch-all so the app never crashes on an unexpected problem.
            return self._error_result(f"Unexpected error: {str(e)}")

    def _validate_and_clean(self, data: dict) -> dict:
        """
        Makes sure every expected field exists and has a sensible type/value.
        If the AI forgot a field or used a wrong type, we fill in a safe default
        instead of letting the app crash. This is the agent "checking its work".
        """

        allowed_sentiments = {"Positive", "Negative", "Neutral", "Mixed"}

        sentiment = data.get("sentiment", "Neutral")
        if sentiment not in allowed_sentiments:
            sentiment = "Neutral"

        emotion = data.get("emotion", "Neutral")
        if not isinstance(emotion, str) or emotion.strip() == "":
            emotion = "Neutral"

        def clean_list(value):
            # Make sure the value is a list of non-empty strings.
            if not isinstance(value, list):
                return []
            return [str(item).strip() for item in value if str(item).strip() != ""]

        positive_aspects = clean_list(data.get("positive_aspects", []))
        negative_aspects = clean_list(data.get("negative_aspects", []))
        topics = clean_list(data.get("topics", []))
        keywords = clean_list(data.get("keywords", []))

        confidence = data.get("confidence", 0.5)
        try:
            confidence = float(confidence)
            confidence = max(0.0, min(1.0, confidence))  # keep it between 0 and 1
        except (ValueError, TypeError):
            confidence = 0.5

        explanation = data.get("explanation", "No explanation provided.")
        if not isinstance(explanation, str) or explanation.strip() == "":
            explanation = "No explanation provided."

        return {
            "sentiment": sentiment,
            "emotion": emotion,
            "positive_aspects": positive_aspects,
            "negative_aspects": negative_aspects,
            "topics": topics,
            "keywords": keywords,
            "confidence": confidence,
            "explanation": explanation,
            "error": None,
        }

    def _error_result(self, message: str) -> dict:
        """
        Returns a safe, default dictionary along with an error message.
        This lets the Streamlit app always know what keys to expect,
        even when something failed.
        """
        return {
            "sentiment": "Neutral",
            "emotion": "Neutral",
            "positive_aspects": [],
            "negative_aspects": [],
            "topics": [],
            "keywords": [],
            "confidence": 0.0,
            "explanation": "",
            "error": message,
        }