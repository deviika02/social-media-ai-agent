# 🤖 Social Media Sentiment Analysis AI Agent

## 1. Project Title
Social Media Sentiment Analysis AI Agent

## 2. Project Description
A local Python web application (built with Streamlit) that uses an AI agent
powered by the OpenAI API to analyze social media comments. It detects
sentiment, emotion, positive/negative aspects, topics, keywords, and gives a
plain-English explanation. It supports single-comment analysis, bulk CSV
analysis, and a visual dashboard.

## 3. Problem Statement
Companies and individuals receive huge volumes of social media comments and
reviews. Reading each one manually to understand public opinion is slow and
error-prone. This project automates that process using an AI agent that
understands sarcasm, slang, emojis, and mixed opinions.

## 4. Objectives
- Automatically detect sentiment and emotion in social media comments.
- Extract what people liked and disliked.
- Summarize topics and keywords.
- Process comments individually or in bulk (CSV).
- Visualize results in a simple dashboard.
- Teach beginners how a simple AI agent is structured.

## 5. Features
1. Single comment analysis with structured results.
2. Structured JSON output validated in Python.
3. CSV upload, bulk analysis, and downloadable results.
4. Dashboard with totals and charts (sentiment & emotion distribution).
5. 20-row realistic sample dataset.
6. Robust error handling (missing keys, bad CSVs, API failures, etc).

## 6. AI Agent Explanation — What makes this an "AI Agent"?
A plain API call just sends text and returns whatever comes back, with no
checks. Our `SentimentAgent` (in `agent.py`) instead:
1. **Receives** the task (a comment to analyze).
2. **Plans** the request by combining a detailed system prompt with the input.
3. **Acts** by calling the OpenAI model and requesting a strict JSON format.
4. **Observes** the result — parses the JSON reply.
5. **Validates** every field, filling in safe defaults if anything is missing
   or malformed, instead of blindly trusting the AI.
6. **Handles failures** gracefully (bad key, no internet, rate limits, bad
   JSON) with friendly error messages instead of crashing.
7. **Returns** a clean, guaranteed-shape Python dictionary to the app.

This "receive → plan → act → validate → recover → return" loop is what makes
it an agent rather than a single raw API call.

## 7. Architecture
```
User
 ↓
Streamlit UI (app.py)
 ↓
Sentiment Agent (agent.py)
 ↓
OpenAI API (gpt-4o-mini)
 ↓
Structured JSON response
 ↓
Python Validation (agent.py)
 ↓
Streamlit (app.py)
 ↓
Result / Dashboard
```
- **Streamlit UI**: collects input, shows results, handles CSV upload/download.
- **Sentiment Agent**: builds the prompt, calls the LLM, validates the output.
- **OpenAI API**: the language model that performs the actual analysis.
- **Validation layer**: guarantees the app never crashes on bad AI output.

## 8. Technology Stack
- Python 3
- OpenAI API (`openai` Python SDK)
- Streamlit (frontend/UI)
- Pandas (CSV/data processing)
- Plotly (charts)
- python-dotenv (environment variables)
- CSV (data storage, no database needed)

## 9. Project Structure
```
social-media-ai-agent/
│
├── app.py                     # Streamlit web app (UI)
├── agent.py                   # AI agent logic (SentimentAgent class)
├── requirements.txt           # Python package list
├── .env                       # Your real API key (you create this, never shared)
├── .env.example                # Template showing the required variable name
├── .gitignore                  # Tells Git to ignore .env and other junk
├── README.md                   # This file
│
└── data/
    └── sample_comments.csv     # 20 sample comments for testing
```

## 10. Installation Requirements
- macOS with VS Code installed.
- Python 3.9+ installed.
- An OpenAI account with an API key and available credits.

## 11. Python Installation Check
Open Terminal (or the VS Code integrated terminal) and run:
```bash
python3 --version
```
You should see something like `Python 3.11.x`. If not installed, download it
from https://www.python.org/downloads/.

## 12. Virtual Environment Setup
A virtual environment keeps this project's packages separate from the rest
of your Mac.
```bash
python3 -m venv venv
```
This creates a `venv` folder containing an isolated Python environment.

## 13. Package Installation
Activate the environment first, then install packages:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 14. OpenAI API Key Setup
1. Go to https://platform.openai.com/api-keys.
2. Log in (or sign up) and click "Create new secret key".
3. Copy the key — you will not be able to see it again.

## 15. .env Setup
1. In the project folder, create a new file named exactly `.env`.
2. Paste this into it, replacing the placeholder with your real key:
```
OPENAI_API_KEY=your_actual_key_here
```
3. Save the file. **Never share this file or commit it to GitHub** — it is
   already listed in `.gitignore` so Git will ignore it automatically.

## 16. How to Run
```bash
streamlit run app.py
```
Streamlit will print a local URL (usually `http://localhost:8501`) and should
open it automatically in your browser.

## 17. Expected Output
- A browser tab opens showing "🤖 Social Media Sentiment Analysis AI Agent".
- In the "Analyze Comment" tab, type a comment and click **Analyze Comment**.
- Within a few seconds you'll see the sentiment, emotion, confidence,
  positive/negative aspects, topics, keywords, and an explanation.

## 18. CSV Format
Your CSV must contain a column named exactly `comment`:
```csv
comment
"The product is amazing!"
"Very bad customer service."
"The phone is okay."
```
After analysis, the app adds: `sentiment`, `emotion`, `positive_aspects`,
`negative_aspects`, `topics`, `keywords`, `confidence`, `explanation`.

## 19. How the AI Agent Works
1. You type or upload a comment.
2. `app.py` calls `agent.analyze_comment(comment)`.
3. `agent.py` sends a system prompt + your comment to the OpenAI model,
   requesting a JSON-only response.
4. The model replies with JSON describing the sentiment analysis.
5. `agent.py` parses and validates that JSON (fixing/defaulting any bad
   fields) so the app always receives clean data.
6. `app.py` displays the validated result.

## 20. Explanation of Each File
- **app.py** — The Streamlit UI: tabs, buttons, text areas, charts, CSV
  upload/download, and calls into the agent.
- **agent.py** — The `SentimentAgent` class: the system prompt, the OpenAI
  API call, JSON parsing, and result validation.
- **requirements.txt** — Exact package list needed to run the app.
- **.env / .env.example** — Where your secret API key lives (never hard-coded).
- **data/sample_comments.csv** — Ready-made comments to test the CSV feature.

## 21. Error Handling
The app handles: missing/invalid API key, empty comment, empty CSV, missing
`comment` column, network failures, OpenAI API errors, rate limits, and
invalid/unexpected AI responses — always with a friendly message, never a
raw crash or an exposed API key.

## 22. Security Considerations
- The API key is loaded only from `.env` via `python-dotenv` — never hard-coded.
- `.env` is listed in `.gitignore` so it won't be committed to GitHub.
- Error messages never print your API key.
- Never share your `.env` file or push it to a public repository.

## 23. Limitations
- Requires an internet connection and OpenAI API credits.
- Analysis quality depends on the underlying AI model.
- CSV analysis is capped at 200 rows per run to control API costs.
- No database — results only persist for the current browser session.

## 24. Future Scope
- Add a database (e.g., SQLite) to store historical analyses.
- Support multiple languages.
- Add authentication for multi-user use.
- Compare multiple AI models.

## 25. Possible Improvements
- Batch multiple comments into fewer API calls to reduce cost.
- Add caching so identical comments aren't re-analyzed.
- Add unit tests for `agent.py`.
- Deploy to Streamlit Community Cloud for sharing (optional, not required here).

---

## Data Flow (detailed)

**Single comment:**
```
User enters comment
↓
Streamlit receives comment
↓
app.py sends comment to SentimentAgent
↓
agent.py builds the prompt and calls OpenAI
↓
OpenAI returns structured JSON
↓
agent.py validates the JSON
↓
Result returned to app.py
↓
Streamlit displays the result
```

**CSV:**
```
CSV file
↓
Pandas reads it
↓
Each comment row
↓
SentimentAgent analyzes it
↓
Results appended as new columns
↓
DataFrame shown + Dashboard charts
↓
Download button exports analyzed CSV
```

## Cost Awareness
Every analysis (single comment or each CSV row) makes one call to the OpenAI
API, which may incur a small charge depending on your OpenAI plan/model. The
CSV feature is capped at 200 rows per run to avoid excessive, unintended
usage. Check https://platform.openai.com/usage to monitor your spending.

## Common Errors and Fixes
| Error | Fix |
|---|---|
| `OPENAI_API_KEY is missing` | Create `.env` with a valid key, restart the app. |
| `Invalid OpenAI API key` | Double-check the key was copied correctly, no extra spaces. |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the activated venv. |
| CSV upload fails / missing column error | Make sure the CSV has a column literally named `comment`. |
| App won't start / wrong Python | In VS Code, select the `venv` interpreter (Cmd+Shift+P → "Python: Select Interpreter"). |
| Rate limit error | Wait a bit, or check your OpenAI account's usage/billing limits. |

## Mini Project Viva Preparation (20+ Questions)

1. **What does this project do?**
   It analyzes the sentiment, emotion, and key aspects of social media comments using an AI agent powered by the OpenAI API.

2. **What makes this an "AI agent" and not just an API call?**
   It plans the request, validates and repairs the AI's output, and handles errors — a raw API call does none of that.

3. **Which AI model is used?**
   `gpt-4o-mini`, via the OpenAI Chat Completions API.

4. **Why use `response_format={"type": "json_object"}`?**
   It forces the model to return valid JSON instead of free-form text, making the output reliable and easy to parse.

5. **Where is the API key stored?**
   In a local `.env` file, loaded with `python-dotenv`. It's never hard-coded and never committed to Git.

6. **What is a system prompt?**
   The instruction given to the AI before the user's message, defining its role, rules, and expected output format.

7. **What Python libraries does this project use?**
   `openai`, `streamlit`, `pandas`, `python-dotenv`, `plotly`.

8. **How does the app handle an invalid AI response?**
   `agent.py`'s `_validate_and_clean` method checks every field and substitutes safe defaults if something is missing or wrong.

9. **What sentiment categories does the app support?**
   Positive, Negative, Neutral, Mixed.

10. **What is `temperature` in the API call, and why is it set low (0.3)?**
    It controls randomness; a low value makes results more consistent and predictable, which suits structured analysis.

11. **How does the CSV feature work?**
    Pandas reads the file, checks for a `comment` column, then the agent analyzes each row and new result columns are appended.

12. **How are results downloaded?**
    Via Streamlit's `st.download_button`, which exports the analyzed DataFrame as a CSV.

13. **What charts does the dashboard show?**
    A pie chart of sentiment distribution and a bar chart of emotion distribution, built with Plotly.

14. **What happens if the API key is missing?**
    `SentimentAgent.__init__` raises a clear error, and the app shows a friendly setup message instead of crashing.

15. **How does the app avoid crashing on network failures?**
    `agent.py` wraps API calls in try/except blocks catching connection, authentication, rate-limit, and general API errors.

16. **Why is there a row limit (200) for CSV analysis?**
    To prevent accidentally making an excessive number of paid API calls.

17. **What is `st.session_state` used for here?**
    To keep the analyzed CSV results available across Streamlit reruns (button clicks).

18. **How is sarcasm handled?**
    The system prompt explicitly instructs the model to interpret sarcasm by its real intended meaning, not the literal words.

19. **Why isn't a framework like LangChain used?**
    To keep the agent's logic transparent and easy for a beginner to understand, using plain Python and the OpenAI SDK directly.

20. **What does "confidence" represent?**
    The AI model's self-reported confidence (0 to 1) in its own sentiment analysis.

21. **How would you extend this project to support multiple languages?**
    Update the system prompt to instruct the model to detect and analyze comments in any language, and adjust the UI labels if needed.

22. **What's the difference between `positive_aspects` and `topics`?**
    `positive_aspects` are specific things the user liked; `topics` are general categories the comment relates to (e.g., "Battery", "Delivery").
