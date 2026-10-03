"""
app.py
------
This is the Streamlit web application (the "frontend"). It provides the UI,
collects user input, calls the SentimentAgent to do the AI analysis, and
displays the results in a clean, beginner-friendly way.

Run this file with:
    streamlit run app.py
"""

import os
import io
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

from agent import SentimentAgent

# ---------------------------------------------------------------------------
# STEP 1: Load environment variables from the .env file (this loads your
# OPENAI_API_KEY so the agent can use it).
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# STEP 2: Basic Streamlit page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Social Media Sentiment Analysis AI Agent",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Social Media Sentiment Analysis AI Agent")
st.write("Analyze social-media comments using an AI-powered sentiment analysis agent.")

# ---------------------------------------------------------------------------
# STEP 3: Create the AI agent once and reuse it (cached so it isn't rebuilt
# on every click, which would be wasteful).
# ---------------------------------------------------------------------------
@st.cache_resource
def get_agent():
    return SentimentAgent()


agent = None
agent_error = None
try:
    agent = get_agent()
except ValueError as e:
    # This happens if the API key is missing/invalid in .env
    agent_error = str(e)

if agent_error:
    st.error(f"⚠️ Setup problem: {agent_error}")
    st.info(
        "Create a file named `.env` in the project folder with this line:\n\n"
        "`GEMINI_API_KEY=your_api_key_here`\n\n"
        "Get a free key (no credit card needed) at https://aistudio.google.com/apikey. "
        "Then restart the app."
    )

# ---------------------------------------------------------------------------
# STEP 4: Helper - keeps analyzed CSV results in the session so they survive
# reruns (Streamlit reruns the whole script on every interaction).
# ---------------------------------------------------------------------------
if "csv_results" not in st.session_state:
    st.session_state.csv_results = None

# ---------------------------------------------------------------------------
# STEP 5: Emoji helpers for a nicer UI
# ---------------------------------------------------------------------------
SENTIMENT_EMOJI = {
    "Positive": "🟢",
    "Negative": "🔴",
    "Neutral": "⚪",
    "Mixed": "🟡",
}

EMOTION_EMOJI = {
    "Happy": "😊",
    "Angry": "😠",
    "Sad": "😢",
    "Disappointed": "😞",
    "Excited": "🤩",
    "Satisfied": "🙂",
    "Frustrated": "😤",
    "Neutral": "😐",
}


def display_single_result(result: dict):
    """Displays the result dictionary from the agent in a clean layout."""
    if result.get("error"):
        st.error(f"❌ {result['error']}")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        emoji = SENTIMENT_EMOJI.get(result["sentiment"], "⚪")
        st.metric("Sentiment", f"{emoji} {result['sentiment']}")

    with col2:
        emoji = EMOTION_EMOJI.get(result["emotion"], "🙂")
        st.metric("Emotion", f"{emoji} {result['emotion']}")

    with col3:
        st.metric("Confidence", f"{result['confidence'] * 100:.0f}%")

    st.markdown("---")

    left, right = st.columns(2)
    with left:
        st.subheader("✅ Positive Aspects")
        if result["positive_aspects"]:
            for item in result["positive_aspects"]:
                st.write(f"- {item}")
        else:
            st.write("_None found_")

    with right:
        st.subheader("❌ Negative Aspects")
        if result["negative_aspects"]:
            for item in result["negative_aspects"]:
                st.write(f"- {item}")
        else:
            st.write("_None found_")

    st.subheader("🏷️ Topics")
    st.write(", ".join(result["topics"]) if result["topics"] else "_None found_")

    st.subheader("🔑 Keywords")
    st.write(", ".join(result["keywords"]) if result["keywords"] else "_None found_")

    st.subheader("📝 Explanation")
    st.info(result["explanation"])


# ---------------------------------------------------------------------------
# STEP 6: Tabs for the four main features
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["💬 Analyze Comment", "📊 Analyze CSV", "📈 Dashboard", "ℹ️ About"]
)

# ------------------------- TAB 1: Single Comment -------------------------
with tab1:
    st.subheader("Analyze a single comment")

    comment_input = st.text_area(
        "Enter a social media comment",
        placeholder="Example: The new phone camera is amazing but the battery is terrible.",
        height=120,
    )

    analyze_clicked = st.button("Analyze Comment", type="primary", disabled=(agent is None))

    if analyze_clicked:
        if not comment_input or comment_input.strip() == "":
            st.warning("⚠️ Please enter a comment before clicking Analyze.")
        else:
            with st.spinner("Analyzing comment with AI agent..."):
                result = agent.analyze_comment(comment_input)
            display_single_result(result)

# ------------------------- TAB 2: CSV Upload -------------------------
with tab2:
    st.subheader("Analyze comments from a CSV file")
    st.write(
        "Upload a CSV file with a column named **comment**. "
        "Each row will be analyzed by the AI agent."
    )
    st.caption(
        "⚠️ Cost note: each row makes one API call. Larger CSV files will use more "
        "of your OpenAI account's usage/credits."
    )

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"❌ Could not read the CSV file: {e}")
            df = None

        if df is not None:
            if "comment" not in df.columns:
                st.error("❌ The CSV file must contain a column named 'comment'.")
            elif df.empty:
                st.error("❌ The CSV file is empty.")
            else:
                st.success(f"✅ File loaded with {len(df)} rows.")
                st.dataframe(df.head(5))

                max_rows = 200  # simple safety limit to avoid huge accidental API usage
                if len(df) > max_rows:
                    st.warning(
                        f"⚠️ This file has {len(df)} rows. Only the first {max_rows} "
                        "will be analyzed to keep API usage reasonable."
                    )
                    df = df.head(max_rows)

                if st.button("Analyze CSV", type="primary", disabled=(agent is None)):
                    sentiments, emotions, positives, negatives = [], [], [], []
                    topics_list, keywords_list, confidences, explanations = [], [], [], []

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    total = len(df)
                    for i, row in enumerate(df["comment"]):
                        status_text.text(f"Analyzing comment {i + 1} of {total}...")
                        result = agent.analyze_comment(row)

                        sentiments.append(result["sentiment"])
                        emotions.append(result["emotion"])
                        positives.append("; ".join(result["positive_aspects"]))
                        negatives.append("; ".join(result["negative_aspects"]))
                        topics_list.append("; ".join(result["topics"]))
                        keywords_list.append("; ".join(result["keywords"]))
                        confidences.append(result["confidence"])
                        explanations.append(
                            result["error"] if result.get("error") else result["explanation"]
                        )

                        progress_bar.progress((i + 1) / total)

                    status_text.text("✅ Analysis complete!")

                    df["sentiment"] = sentiments
                    df["emotion"] = emotions
                    df["positive_aspects"] = positives
                    df["negative_aspects"] = negatives
                    df["topics"] = topics_list
                    df["keywords"] = keywords_list
                    df["confidence"] = confidences
                    df["explanation"] = explanations

                    st.session_state.csv_results = df

    if st.session_state.csv_results is not None:
        st.markdown("### Results")
        st.dataframe(st.session_state.csv_results)

        csv_buffer = io.StringIO()
        st.session_state.csv_results.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv_buffer.getvalue(),
            file_name="analyzed_comments.csv",
            mime="text/csv",
        )

# ------------------------- TAB 3: Dashboard -------------------------
with tab3:
    st.subheader("Dashboard")

    if st.session_state.csv_results is None:
        st.info("Upload and analyze a CSV file in the 'Analyze CSV' tab to see the dashboard.")
    else:
        df = st.session_state.csv_results

        total = len(df)
        positive_count = int((df["sentiment"] == "Positive").sum())
        negative_count = int((df["sentiment"] == "Negative").sum())
        neutral_count = int((df["sentiment"] == "Neutral").sum())
        mixed_count = int((df["sentiment"] == "Mixed").sum())

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Comments", total)
        c2.metric("🟢 Positive", positive_count)
        c3.metric("🔴 Negative", negative_count)
        c4.metric("⚪ Neutral", neutral_count)
        c5.metric("🟡 Mixed", mixed_count)

        st.markdown("---")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            sentiment_counts = df["sentiment"].value_counts().reset_index()
            sentiment_counts.columns = ["Sentiment", "Count"]
            fig1 = px.pie(
                sentiment_counts,
                names="Sentiment",
                values="Count",
                title="Sentiment Distribution",
            )
            st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            emotion_counts = df["emotion"].value_counts().reset_index()
            emotion_counts.columns = ["Emotion", "Count"]
            fig2 = px.bar(
                emotion_counts,
                x="Emotion",
                y="Count",
                title="Emotion Distribution",
            )
            st.plotly_chart(fig2, use_container_width=True)

# ------------------------- TAB 4: About -------------------------
with tab4:
    st.subheader("About this project")
    st.markdown(
        """
This app is a **Social Media Sentiment Analysis AI Agent**.

It uses an AI agent (`agent.py`) that:
1. Receives a comment from you.
2. Builds a clear instruction (prompt) for the AI model.
3. Sends it to the OpenAI API and asks for structured JSON output.
4. Validates and cleans the response.
5. Returns the result to be displayed here.

**Tech stack:** Python, Streamlit, OpenAI API, Pandas, Plotly, python-dotenv.

See `README.md` in the project folder for the full explanation, architecture
diagram, and setup instructions.
        """
    )
