import streamlit as st
import pandas as pd
import io
import os
from pathlib import Path
from openai import OpenAI, APIConnectionError, AuthenticationError
from dotenv import load_dotenv

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Review Analyzer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="auto",
)

# ─── Load env (works locally; on Streamlit Cloud use Secrets) ─────────────────
load_dotenv()
API_KEY    = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ─── Prompt loading — always relative to THIS file ────────────────────────────
PROMPTS_DIR = Path(__file__).parent / "prompts"

DEFAULT_PROMPTS = {
    "topic":     "You are an expert at extracting the main topic from customer reviews. Reply with ONE short topic phrase only.",
    "summary":   "You are an expert summarizer. Summarize the customer review in ONE concise sentence.",
    "sentiment": "You are a sentiment classifier. Classify the review as POSITIVE, NEGATIVE, or NEUTRAL. Reply with one word only.",
    "user":      "Customer Review:\n{review}",
}

def _read(path: Path, fallback: str) -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
        return text if text else fallback
    except Exception:
        return fallback

PROMPTS = {
    "topic":     _read(PROMPTS_DIR / "system" / "topic_extraction.txt",   DEFAULT_PROMPTS["topic"]),
    "summary":   _read(PROMPTS_DIR / "system" / "summarize_reviews.txt",  DEFAULT_PROMPTS["summary"]),
    "sentiment": _read(PROMPTS_DIR / "system" / "sentiment_analysis.txt", DEFAULT_PROMPTS["sentiment"]),
    "user":      _read(PROMPTS_DIR / "user"   / "review.txt",             DEFAULT_PROMPTS["user"]),
}

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

:root {
    --bg:       #0B0C10;
    --surface:  #13151C;
    --border:   #1E2130;
    --accent:   #0EA5E9;
    --accent2:  #06B6D4;
    --text:     #E8E9F0;
    --muted:    #6B6F84;
    --positive: #34D399;
    --negative: #F87171;
    --neutral:  #FBBF24;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
h1, h2, h3 { font-family: 'Syne', sans-serif; }

.hero { padding: 2.5rem 0 1.5rem; text-align: center; }
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem; font-weight: 800;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.1; margin-bottom: 0.5rem;
}
.hero-sub { color: var(--muted); font-size: 1rem; font-weight: 300; letter-spacing: 0.04em; }

.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 1.5rem 1.75rem; margin-bottom: 1.25rem;
}
.card-label {
    font-family: 'Syne', sans-serif; font-size: 0.65rem; font-weight: 600;
    letter-spacing: 0.15em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.35rem;
}
.card-value { font-size: 1.9rem; font-weight: 700; font-family: 'Syne', sans-serif; }

.pill {
    display: inline-block; padding: 3px 12px; border-radius: 999px;
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;
}
.pill-positive { background: rgba(52,211,153,.15); color: var(--positive); border: 1px solid rgba(52,211,153,.3); }
.pill-negative { background: rgba(248,113,113,.15); color: var(--negative); border: 1px solid rgba(248,113,113,.3); }
.pill-neutral  { background: rgba(251,191,36,.12);  color: var(--neutral);  border: 1px solid rgba(251,191,36,.25); }

[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important; border-radius: 14px !important;
    background: var(--surface) !important; padding: 1rem !important; transition: border-color .2s;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }
div[data-testid="stCheckbox"] label { color: var(--text) !important; font-size: 0.9rem; }

.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    letter-spacing: 0.03em !important; padding: 0.55rem 1.5rem !important; transition: opacity .2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

[data-testid="stDownloadButton"] > button {
    background: transparent !important; border: 1.5px solid var(--accent) !important;
    color: var(--accent) !important; border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    width: 100% !important; margin-top: 0.5rem !important; transition: background .2s, color .2s !important;
}
[data-testid="stDownloadButton"] > button:hover { background: var(--accent) !important; color: #fff !important; }

[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
iframe { border-radius: 12px !important; }

.sidebar-section {
    font-family: 'Syne', sans-serif; font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted);
    margin: 1.4rem 0 0.6rem; padding-bottom: 0.4rem; border-bottom: 1px solid var(--border);
}
.stProgress > div > div { background: linear-gradient(90deg, var(--accent), var(--accent2)) !important; border-radius: 4px; }
[data-testid="stAlert"] { border-radius: 10px !important; }
#MainMenu, header, footer { visibility: hidden; }
.divider { height: 1px; background: var(--border); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def ask_llm(client: OpenAI, user_content: str, system_content: str,
            model: str = "gpt-4o-mini", temperature: float = 0.5, max_tokens: int = 500) -> str:
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user",   "content": user_content},
            ],
        )
        return resp.choices[0].message.content.strip()
    except AuthenticationError:
        return "Invalid API key."
    except APIConnectionError:
        return "Connection error."
    except Exception as e:
        return f"Error: {e}"


def sentiment_color(val: str) -> str:
    v = str(val).lower()
    if "positive" in v: return "pill pill-positive"
    if "negative" in v: return "pill pill-negative"
    return "pill pill-neutral"


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.5rem;text-align:center;">✦ Review Analyzer</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">API Configuration</div>', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=API_KEY,
        type="password",
        placeholder="sk-...",
        help="On Streamlit Cloud, set this in Settings → Secrets.",
    )
    model_input = st.text_input("Model", value=MODEL_NAME, placeholder="gpt-4o-mini")

    st.markdown('<div class="sidebar-section">Analysis Options</div>', unsafe_allow_html=True)
    need_topic     = st.checkbox("✦ Topic Extraction",   value=True)
    need_summary   = st.checkbox("✦ Review Summary",     value=True)
    need_sentiment = st.checkbox("✦ Sentiment Analysis", value=True)

    st.markdown('<div class="sidebar-section">Row Limit</div>', unsafe_allow_html=True)
    row_limit = st.slider("Max rows to analyze", min_value=1, max_value=100000, value=10,
                          help="Limit rows to control API cost.")
    row_limit = st.number_input("Or type a number directly", min_value=1, max_value=100000,
                                value=row_limit, step=1)


# ─── Main area ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Customer Review Analyzer</div>
    <div class="hero-sub">AI-powered · Topic · Sentiment · Summary</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drop your CSV file here",
    type=["csv"],
    help='The file must contain a column named **review**.',
)
st.markdown('</div>', unsafe_allow_html=True)

# ── File uploaded ──────────────────────────────────────────────────────────────
if uploaded_file:
    try:
        raw_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        st.stop()

    if "review" not in raw_df.columns:
        st.error('The CSV must have a column named **"review"**.')
        st.stop()

    if raw_df.empty:
        st.warning("The uploaded file has no data rows.")
        st.stop()

    total_rows   = len(raw_df)
    analyze_rows = min(row_limit, total_rows)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card"><div class="card-label">Total Reviews</div><div class="card-value">{total_rows}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card"><div class="card-label">To Analyze</div><div class="card-value">{analyze_rows}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card"><div class="card-label">Columns</div><div class="card-value">{len(raw_df.columns)}</div></div>', unsafe_allow_html=True)

    with st.expander("Original Data Preview", expanded=True):
        st.dataframe(raw_df, use_container_width=True, height=220)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if not (need_topic or need_summary or need_sentiment):
        st.warning("Please select at least one analysis option from the sidebar.")
        st.stop()

    run_col, _ = st.columns([1, 3])
    with run_col:
        run = st.button("▶  Run Analysis", use_container_width=True)

    if run:
        if not api_key_input:
            st.error("Please enter your OpenAI API Key in the sidebar.")
            st.stop()

        client   = OpenAI(api_key=api_key_input)
        df_work  = raw_df.head(analyze_rows).copy()
        topics, summaries, sentiments = [], [], []

        st.markdown("#### Analyzing reviews...")
        progress_bar = st.progress(0)
        status_text  = st.empty()

        for i, review in enumerate(df_work["review"]):
            user_prompt = PROMPTS["user"].format(review=review)

            if need_topic:
                status_text.markdown(f'<span style="color:var(--muted);font-size:.85rem;">Row {i+1}/{analyze_rows} · extracting topic...</span>', unsafe_allow_html=True)
                topics.append(ask_llm(client, user_prompt, PROMPTS["topic"], model_input))

            if need_summary:
                status_text.markdown(f'<span style="color:var(--muted);font-size:.85rem;">Row {i+1}/{analyze_rows} · summarizing...</span>', unsafe_allow_html=True)
                summaries.append(ask_llm(client, user_prompt, PROMPTS["summary"], model_input))

            if need_sentiment:
                status_text.markdown(f'<span style="color:var(--muted);font-size:.85rem;">Row {i+1}/{analyze_rows} · classifying sentiment...</span>', unsafe_allow_html=True)
                sentiments.append(ask_llm(client, user_prompt, PROMPTS["sentiment"], model_input))

            progress_bar.progress(min((i + 1) / analyze_rows, 1.0))

        status_text.markdown('<span style="color:var(--positive);font-size:.85rem;">Analysis complete!</span>', unsafe_allow_html=True)

        result_df = df_work.copy()
        if need_topic:     result_df["topic"]     = topics
        if need_summary:   result_df["summary"]   = summaries
        if need_sentiment: result_df["sentiment"] = sentiments

        st.session_state["result_df"] = result_df
        st.session_state["raw_df"]    = raw_df


# ── Show results ───────────────────────────────────────────────────────────────
if "result_df" in st.session_state:
    result_df = st.session_state["result_df"]
    raw_df    = st.session_state["raw_df"]

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### Analysis Results")

    if "sentiment" in result_df.columns:
        sent_counts = result_df["sentiment"].str.upper().str.strip().value_counts()
        chart_cols  = st.columns(len(sent_counts))
        color_map   = {"POSITIVE": "#34D399", "NEGATIVE": "#F87171", "NEUTRAL": "#FBBF24"}
        for idx, (label, count) in enumerate(sent_counts.items()):
            pct       = round(count / len(result_df) * 100)
            col_color = color_map.get(label.upper(), "#7C6EF8")
            with chart_cols[idx]:
                st.markdown(
                    f'<div class="card" style="text-align:center;border-color:{col_color}33;">'
                    f'<div class="card-label">{label}</div>'
                    f'<div class="card-value" style="color:{col_color};">{pct}%</div>'
                    f'<div style="color:var(--muted);font-size:.8rem;">{count} review{"s" if count>1 else ""}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    def render_row(row):
        parts = []
        for col in result_df.columns:
            val = row[col]
            if col == "sentiment":
                cls = sentiment_color(str(val))
                parts.append(f'<td style="padding:8px 12px;"><span class="{cls}">{val}</span></td>')
            else:
                parts.append(f'<td style="color:var(--text);font-size:.85rem;padding:8px 12px;">{val}</td>')
        return "<tr>" + "".join(parts) + "</tr>"

    headers = "".join(
        f'<th style="text-align:left;padding:8px 12px;color:var(--muted);font-family:\'Syne\',sans-serif;'
        f'font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;border-bottom:1px solid var(--border);">'
        f'{c}</th>'
        for c in result_df.columns
    )
    rows_html  = "\n".join(render_row(row) for _, row in result_df.iterrows())
    table_html = f"""
    <div style="overflow-x:auto;border-radius:14px;border:1px solid var(--border);background:var(--surface);margin:1rem 0;">
      <table style="width:100%;border-collapse:collapse;">
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### Download Results")

    dl1, dl2 = st.columns(2)
    with dl1:
        st.markdown("**Analyzed Data** *(with AI columns)*")
        st.download_button("Download Analyzed CSV", data=df_to_csv_bytes(result_df),
                           file_name="analyzed_reviews.csv", mime="text/csv", use_container_width=True)
    with dl2:
        st.markdown("**Original Data** *(unmodified)*")
        st.download_button("Download Original CSV", data=df_to_csv_bytes(raw_df),
                           file_name="original_reviews.csv", mime="text/csv", use_container_width=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 1rem;color:#6B6F84;">
        <div style="font-size:3rem;margin-bottom:1rem;">⬆️</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:600;color:#E8E9F0;margin-bottom:.4rem;">
            Upload a CSV file to get started
        </div>
        <div style="font-size:.875rem;">
            The file must include a <code style="background:#1E2130;padding:2px 7px;border-radius:5px;color:#C084FC;">review</code> column
        </div>
    </div>
    """, unsafe_allow_html=True)
