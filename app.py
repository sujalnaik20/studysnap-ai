"""StudySnap AI: a small Streamlit study assistant with Gemini and Gmail."""


import html
import re
import smtplib
import ssl
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    IMAGE_ANALYSIS_PROMPT,
    SUMMARY_REQUEST_PROMPT,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_IMAGE_MB = 4
EMAIL_SUBJECT = "Your StudySnap AI Revision Summary 📚"

CSS = """
<style>
:root { color-scheme: light; }
html, body, [data-testid="stAppViewContainer"] { background:#f7f7f5; color:#202124; }
.stApp { background:#f7f7f5; color:#202124; }
[data-testid="stHeader"], div[data-testid="stToolbar"] { display:none !important; }
[data-testid="stMainBlockContainer"] {
    max-width:1000px;
    padding:1.1rem 2rem 3.5rem;
}
h1, h2, h3 { color:#202124 !important; letter-spacing:-.025em; }
#MainMenu, footer { visibility:hidden; }
.brand { display:flex; gap:.65rem; align-items:center; }
.brand-mark {
    display:grid; place-items:center; flex:none; width:2rem; height:2rem;
    color:#635bff; font-size:1.7rem; line-height:1;
}
.brand-name { color:#202124; font-size:1rem; font-weight:750; letter-spacing:-.03em; }
.brand-name span { color:#635bff; }
.brand-subtitle { color:#777; font-size:.72rem; margin-top:.08rem; }
.brand-centered { flex-direction:column; justify-content:center; gap:.05rem; }
.brand-centered .brand-mark { width:3.3rem; height:3.3rem; font-size:2.8rem; }
.brand-centered .brand-name { font-size:1.2rem; }
.st-key-onboarding-shell { max-width:100%; padding-top:.8rem; }
.onboarding-intro { text-align:center; margin:.8rem auto .9rem; }
.onboarding-intro h1 {
    margin:0 0 .55rem; font-size:clamp(1.55rem,3vw,2rem);
    font-weight:750; line-height:1.2;
}
.onboarding-intro p { color:#707070; font-size:.95rem; line-height:1.55; margin:0 auto; }
.st-key-onboarding-card {
    max-width:460px; margin:0 auto; padding:1.2rem 1.4rem;
    background:#fff; border:1px solid #e5e5e2; border-radius:15px;
    box-shadow:0 5px 18px rgba(24,24,24,.035);
}
[data-testid="stForm"] {
    background:transparent;
    border:0 !important;
    border-radius:0 !important;
    box-shadow:none;
    padding:0;
}
.st-key-onboarding-card h3 { font-size:1.15rem !important; margin:0 0 .3rem; }
.onboarding-description { color:#737373; font-size:.83rem; line-height:1.5; margin-bottom:1rem; }
[data-testid="stTextInput"] label { color:#272727; font-size:.78rem; font-weight:650; }
[data-testid="stTextInput"] input {
    min-height:2.45rem; background:#fff; color:#202124;
    border:1px solid #dededb; border-radius:9px;
}
[data-testid="stTextInput"] input:focus { border-color:#635bff; box-shadow:0 0 0 1px #635bff; }
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
    border-radius:9px; min-height:2.4rem; font-weight:650;
}
button[kind="primary"], button[kind="primaryFormSubmit"] {
    background:#635bff; border-color:#635bff; color:#fff;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
    background:#5149e8; border-color:#5149e8; color:#fff;
}
.privacy-note { color:#777; font-size:.72rem; text-align:center; margin:.9rem 0 0; }
.onboarding-footer { color:#777; font-size:.72rem; text-align:center; margin:4rem auto 0; }
.st-key-app-header {
    display:flex; align-items:center; justify-content:space-between; min-height:3.5rem;
    border-bottom:1px solid #e8e8e5; margin:0 -2rem 2.2rem; padding:0 2rem .9rem;
}
.user-profile { display:flex; align-items:center; justify-content:flex-end; gap:.55rem; }
.user-avatar {
    display:grid; place-items:center; width:1.8rem; height:1.8rem; border-radius:50%;
    background:#242424; color:#fff; font-size:.75rem; font-weight:700;
}
.user-name { font-size:.82rem; font-weight:650; color:#333; }
.app-intro { margin-bottom:1.3rem; }
.app-intro h1 { font-size:clamp(1.55rem,3vw,2rem); margin:0 0 .35rem; font-weight:750; }
.app-intro p { color:#707070; font-size:.88rem; margin:0; }
.st-key-upload-area {
    background:#fff; border:1px dashed #d9d9d5; border-radius:12px;
    padding:1.2rem 1.5rem 1rem; text-align:center;
}
.upload-title { font-weight:650; color:#303030; font-size:.9rem; margin-bottom:.2rem; }
.upload-subtitle { color:#777; font-size:.75rem; margin-bottom:.65rem; }
[data-testid="stFileUploader"] { max-width:520px; margin:0 auto; text-align:left; }
[data-testid="stFileUploader"] section { border:0; background:transparent; padding:.2rem 0; }
[data-testid="stFileUploader"] small { color:#777; }
[data-testid="stForm"] [data-testid="stFileUploader"] button {
    color:#635bff; border-color:#dedcff; background:#f8f7ff; border-radius:7px;
}
.st-key-suggestions { margin:.75rem 0 1.8rem; }
.st-key-suggestions button {
    min-height:2rem !important; height:auto !important; padding:.25rem .65rem !important;
    border:1px solid #e2e2df !important; border-radius:999px !important;
    background:#fff !important; color:#414141 !important;
    font-size:.72rem !important; font-weight:550 !important;
}
.st-key-suggestions button:hover { border-color:#bcb8ff !important; color:#5149e8 !important; }
.st-key-suggestions button p::first-letter { color:#635bff; }
.conversation-heading {
    display:flex; align-items:center; justify-content:space-between;
    border-bottom:1px solid #e8e8e5; padding-bottom:.75rem; margin-bottom:1.1rem;
}
.conversation-heading strong { font-size:.95rem; color:#292929; }
.ready-status { display:flex; align-items:center; gap:.35rem; color:#666; font-size:.72rem; }
.ready-dot { width:.42rem; height:.42rem; border-radius:50%; background:#635bff; }
[data-testid="stChatMessage"] {
    background:transparent; border:0; border-radius:0;
    padding:.3rem 0; margin-bottom:.65rem;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    max-width:76%; margin-left:auto; background:#fff;
    border:1px solid #e4e4e1; border-radius:12px; padding:.85rem 1rem;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="chatAvatarIcon-user"] {
    display:none;
}
[data-testid="stChatMessage"] p { color:#383838; font-size:.84rem; line-height:1.58; }
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4 { color:#272727 !important; margin-top:1rem; }
[data-testid="stChatMessage"] ul { padding-left:1.2rem; }
[data-testid="stChatMessage"] li::marker { color:#635bff; }
[data-testid="stChatMessage"] img { border-radius:8px; }
.assistant-label {
    display:flex; align-items:center; gap:.45rem; color:#333;
    font-size:.78rem; font-weight:700; margin-bottom:.3rem;
}
.assistant-mark {
    display:grid; place-items:center; width:1.35rem; height:1.35rem;
    border-radius:5px; background:#635bff; color:#fff; font-size:.72rem;
}
.study-tip { border-left:2px solid #635bff; padding:.25rem 0 .25rem .7rem; color:#4d4d4d; }
[data-testid="stExpander"] { background:#fff; border:1px solid #e6e6e3; border-radius:10px; }
[data-testid="stExpander"] summary { color:#303030; }
[data-testid="stBottom"] > div { background:rgba(247,247,245,.96); }
[data-testid="stChatInput"] {
    border:1px solid #dededb; border-radius:11px; background:#fff;
    box-shadow:0 3px 12px rgba(0,0,0,.035);
}
[data-testid="stChatInput"] textarea { color:#252525; }
.st-key-summary-row { margin-top:.55rem; }
.st-key-summary-row [data-testid="stButton"] button {
    min-height:2rem !important; border:1px solid #e1e1de !important;
    border-radius:8px !important; background:#fff !important;
    color:#333 !important; font-size:.75rem !important;
}
[data-testid="stChatInput"] button:last-of-type {
    background:#635bff; border-color:#635bff; border-radius:7px; color:#fff;
}
[data-testid="stChatInput"] button:last-of-type:hover {
    background:#5149e8; border-color:#5149e8; color:#fff;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color:#707070; }
@media (max-width:640px) {
    [data-testid="stMainBlockContainer"] { padding:.5rem 1rem 2.5rem; }
    .st-key-onboarding-shell { padding-top:.4rem; }
    .onboarding-intro { margin:.65rem auto .7rem; }
    .onboarding-intro p { max-width:22rem; font-size:.86rem; }
    .st-key-onboarding-card { width:100%; padding:1rem; }
    .st-key-app-header { margin:0 -1rem 1.55rem; padding:0 1rem .7rem; }
    .brand { gap:.4rem; }
    .brand-mark { width:1.65rem; height:1.65rem; }
    .brand-name { font-size:.88rem; }
    .brand-subtitle { font-size:.65rem; }
    .user-name { font-size:.75rem; }
    .app-intro { margin-bottom:1rem; }
    .st-key-upload-area { padding:.9rem .65rem .7rem; }
    .st-key-suggestions { margin:.6rem 0 1.2rem; }
    .st-key-suggestions [data-testid="stHorizontalBlock"] { flex-wrap:wrap; }
    .st-key-suggestions [data-testid="column"] {
        min-width:47% !important; flex-basis:47% !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { max-width:94%; }
    .onboarding-footer { margin-top:2.6rem; }
    .st-key-summary-row [data-testid="stHorizontalBlock"] { justify-content:flex-end; }
}
</style>
"""


def valid_email(address):
    """Basic structure check; reject whitespace and email header injection."""
    return bool(re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
                             r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
                             r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+",
                             address)) and len(address) <= 254


def read_secret(key):
    """Fail with a useful message, without printing credentials or tracebacks."""
    try:
        value = str(st.secrets[key]).strip()
    except Exception as exc:
        raise ValueError(f"Add {key} to Streamlit secrets before using this feature.") from exc
    if not value or value.startswith("your-"):
        raise ValueError(f"Replace the {key} placeholder in Streamlit secrets.")
    return value


@st.cache_resource
def get_gemini_client():
    # Share only the client. Each student's chat is kept in their session state.
    return genai.Client(
        api_key=read_secret("GEMINI_API_KEY"),
        http_options=types.HttpOptions(timeout=60000),
    )


def create_chat():
    return get_gemini_client().chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )


def init_session():
    defaults = {
        "onboarded": False, "name": "", "email": "", "messages": [],
        "chat": None, "study_turns": 0, "pending_request": None, "pending_error": "",
        "revision_summary": "", "summary_turn": -1, "email_status": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})


def render_message(message):
    with st.chat_message(
        message["role"],
        avatar=":material/auto_stories:" if message["role"] == "assistant" else "👤",
    ):
        if message["role"] == "assistant":
            st.markdown(
                '<div class="assistant-label"><span class="assistant-mark">✦</span>'
                "StudySnap</div>",
                unsafe_allow_html=True,
            )
        if message["kind"] == "image":
            # Header checks cannot detect every malformed image; rendering must be safe too.
            try:
                st.image(message["content"]["data"], caption=message["content"]["name"], width="stretch")
            except Exception:
                st.warning("This image could not be previewed. Please upload a valid JPG or PNG.")
        else:
            st.markdown(message["content"])


def ask_gemini(text, image=None):
    parts = [types.Part.from_text(text=text)]
    if image:
        parts.append(types.Part.from_bytes(data=image["data"], mime_type=image["mime_type"]))
    response = st.session_state.chat.send_message(parts)
    answer = (response.text or "").strip()
    if not answer:
        raise ValueError("Gemini returned no readable answer. Try a clearer image or rephrase your question.")
    return answer


def read_image(upload):
    data = upload.getvalue()
    if not data or len(data) > MAX_IMAGE_MB * 1024 * 1024:
        raise ValueError(f"Please upload a non-empty image smaller than {MAX_IMAGE_MB} MB.")
    extension = upload.name.rsplit(".", 1)[-1].lower()
    if extension not in {"jpg", "jpeg", "png"}:
        raise ValueError("Please use a JPG, JPEG, or PNG image.")
    # Determine the actual MIME type from bytes, rather than trusting browser metadata.
    if data.startswith(b"\x89PNG\r\n\x1a\n") and extension == "png":
        mime_type = "image/png"
    elif data.startswith(b"\xff\xd8\xff") and extension in {"jpg", "jpeg"}:
        mime_type = "image/jpeg"
    else:
        raise ValueError("The file contents do not match its JPG or PNG extension.")
    return {"data": data, "mime_type": mime_type, "name": upload.name}


def send_email(to_address, subject, body):
    if not valid_email(to_address):
        raise ValueError("The recipient email address is invalid.")
    GMAIL_ADDRESS = read_secret("GMAIL_ADDRESS")
    GMAIL_APP_PASSWORD = read_secret("GMAIL_APP_PASSWORD").replace(" ", "")
    if not valid_email(GMAIL_ADDRESS):
        raise ValueError("Check GMAIL_ADDRESS in Streamlit secrets.")
    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30,
                          context=ssl.create_default_context()) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        refused = server.sendmail(GMAIL_ADDRESS, [to_address], message.as_string())
        if refused:
            raise smtplib.SMTPRecipientsRefused(refused)


def brand():
    centered = st.session_state.get("onboarded") is False
    brand_class = "brand brand-centered" if centered else "brand"
    subtitle = "" if centered else '<div class="brand-subtitle">AI study companion</div>'
    st.html(
        f"""
        <div class="{brand_class}">
            <div class="brand-mark">
                <svg viewBox="0 0 40 40" fill="none" aria-hidden="true">
                    <span aria-hidden="true">📄</span>
                </svg>
            </div>
            <div>
                <div class="brand-name">StudySnap<span>AI</span></div>
                {subtitle}
            </div>
        </div>
        """,
    )


def onboarding():
    with st.container(key="onboarding-shell"):
        brand()
        st.markdown("""
        <div class="onboarding-intro">
            <h1>Snap it. Understand it. Revise it.</h1>
            <p>Turn the study material in front of you into explanations you can actually use.</p>
        </div>
        """, unsafe_allow_html=True)
        with st.container(key="onboarding-card"):
            with st.form("onboarding", border=False):
                st.markdown("""
                <h3>Start your study space</h3>
                <div class="onboarding-description">
                    Add your details so your revision summary reaches the right inbox.
                </div>
                """, unsafe_allow_html=True)
                name = st.text_input(
                    "Your name", max_chars=80, placeholder="e.g. Maya Patel",
                    icon=":material/person:",
                )
                email = st.text_input(
                    "Email address", max_chars=254, placeholder="you@example.com",
                    icon=":material/mail:",
                )
                submitted = st.form_submit_button(
                    "Start studying →", type="primary", width="stretch",
                )
            st.markdown(
                '<div class="privacy-note">Your email is only used to send your revision summary.</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            '<div class="onboarding-footer">Made for focused study sessions.</div>',
            unsafe_allow_html=True,
        )
    if submitted:
        name, email = name.strip(), email.strip()
        if not name or not email:
            st.warning("Please enter both your name and email address.")
        elif not valid_email(email):
            st.warning("Please enter a valid email address, such as you@example.com.")
        else:
            try:
                with st.spinner("Getting your study space ready..."):
                    chat = create_chat()
            except ValueError as exc:
                st.error(str(exc))
                return
            except Exception:
                st.error("Couldn't set up Gemini. Please check the API key and try again.")
                return
            st.session_state.update(onboarded=True, name=name, email=email, chat=chat)
            # Escape only the name so it cannot inject formatting into the welcome.
            safe_name = re.sub(r"([\\`*_{}\[\]()#+.!>|~-])", r"\\\1", html.escape(name))
            add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=safe_name))
            st.rerun()


def answer_pending_request():
    request = st.session_state.pending_request
    if not request:
        return
    try:
        with st.spinner("StudySnap is reading your notes..." if request["image"]
                        else "StudySnap is thinking..."):
            answer = ask_gemini(request["text"], request["image"])
    except ValueError as exc:
        st.session_state.pending_error = str(exc)
        return
    except Exception:
        st.session_state.pending_error = (
            "Gemini couldn't answer right now. Check the connection, API key, "
            "model access, or quota, then retry below."
        )
        return
    add_message("assistant", "text", answer)
    st.session_state.study_turns += 1
    st.session_state.pending_request = None
    st.session_state.pending_error = ""
    st.session_state.email_status = ""
    st.rerun()


def submit_study_request(text, image=None):
    if image:
        add_message("user", "image", image)
    if text:
        add_message("user", "text", text)
    st.session_state.pending_request = {"text": text or IMAGE_ANALYSIS_PROMPT, "image": image}
    answer_pending_request()
    st.rerun()


def email_revision_summary():
    # Validate mail configuration first, avoiding a paid AI request if it is missing.
    try:
        read_secret("GMAIL_ADDRESS")
        read_secret("GMAIL_APP_PASSWORD")
    except ValueError as exc:
        st.error(str(exc))
        return
    if st.session_state.summary_turn != st.session_state.study_turns:
        try:
            with st.spinner("Creating your revision summary..."):
                summary = ask_gemini(SUMMARY_REQUEST_PROMPT)
        except ValueError as exc:
            st.error(str(exc))
            return
        except Exception:
            st.error("Gemini couldn't create the summary. Please try again shortly.")
            return
        st.session_state.revision_summary = summary
        st.session_state.summary_turn = st.session_state.study_turns
        st.session_state.email_status = ""
    try:
        with st.spinner("Sending your revision summary..."):
            send_email(st.session_state.email, EMAIL_SUBJECT, st.session_state.revision_summary)
    except smtplib.SMTPAuthenticationError:
        st.error("Gmail sign-in failed. The app owner should check the Gmail address "
                 "and App Password in Streamlit secrets. Use an App Password, "
                 "not a normal Gmail password.")
    except smtplib.SMTPRecipientsRefused:
        st.error("Gmail rejected the recipient address. Your revision summary is still available below.")
    except ValueError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Gmail couldn't send the email. Your summary is saved below. "
                 "You can retry sending it; check your inbox first in case delivery completed.")
    else:
        st.session_state.email_status = "Revision summary sent! Check your inbox 📩"


def study_interface():
    with st.container(key="app-header"):
        header, profile = st.columns([2, 1])
        with header:
            brand()
        with profile:
            initial = html.escape(st.session_state.name[:1].upper())
            display_name = html.escape(st.session_state.name.split()[0])
            st.markdown(
                f'<div class="user-profile"><span class="user-avatar">{initial}</span>'
                f'<span class="user-name">{display_name}</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown("""
    <div class="app-intro">
        <h1>What are you studying today?</h1>
        <p>Upload notes, a textbook page, diagram, or ask a question.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(key="upload-area"):
        st.markdown(
            '<div class="upload-title">Drop your study material here</div>'
            '<div class="upload-subtitle">PNG, JPG or JPEG · up to 4 MB</div>',
            unsafe_allow_html=True,
        )
        with st.form("material_upload", border=False):
            uploaded_material = st.file_uploader(
                "Study material",
                type=["jpg", "jpeg", "png"],
                max_upload_size=MAX_IMAGE_MB,
                label_visibility="collapsed",
            )
            upload_submitted = st.form_submit_button(
                "Study this material →", type="primary", width="content",
            )
    if upload_submitted:
        if uploaded_material is None:
            st.warning("Choose a JPG or PNG image to study.")
        else:
            try:
                image = read_image(uploaded_material)
            except ValueError as exc:
                st.warning(str(exc))
            else:
                submit_study_request("", image)

    suggestions = (
        "Explain this simply",
        "What should I revise?",
        "Give me 5 questions",
        "Explain this diagram",
    )
    with st.container(key="suggestions"):
        suggestion_columns = st.columns(4)
        for column, suggestion in zip(suggestion_columns, suggestions):
            with column:
                if st.button(
                    f"•  {suggestion}",
                    key=f"suggestion_{suggestion}",
                    disabled=bool(st.session_state.pending_request),
                    width="stretch",
                ):
                    submit_study_request(suggestion)

    status = "Thinking" if st.session_state.pending_request else "Ready"
    st.markdown(
        '<div class="conversation-heading"><strong>Study conversation</strong>'
        f'<span class="ready-status"><span class="ready-dot"></span>{status}</span></div>',
        unsafe_allow_html=True,
    )
    if st.session_state.email_status:
        st.success(st.session_state.email_status)
    if st.session_state.revision_summary:
        current = st.session_state.summary_turn == st.session_state.study_turns
        with st.expander("Your revision sheet" if current else "Your previous revision sheet"):
            if not current:
                st.caption("You've studied more since this sheet was created. Send a summary to update it.")
            st.text(st.session_state.revision_summary)
            st.download_button("Download revision sheet", st.session_state.revision_summary,
                               file_name="studysnap-revision.txt", mime="text/plain")
    for message in st.session_state.messages:
        render_message(message)
    if st.session_state.pending_request:
        if st.session_state.pending_error:
            st.error(st.session_state.pending_error)
        st.warning("Your last question hasn't received an answer. Retry it or dismiss it to continue.")
        retry, dismiss = st.columns(2)
        if retry.button("Retry answer", width="stretch"):
            answer_pending_request()
            st.rerun()
        if dismiss.button("Dismiss question", width="stretch"):
            st.session_state.pending_request = None
            st.session_state.pending_error = ""
            st.rerun()
    submission = st.chat_input(
        "Ask anything about your study material...", accept_file=True,
        file_type=["jpg", "jpeg", "png"], max_upload_size=MAX_IMAGE_MB,
        max_chars=12000, disabled=bool(st.session_state.pending_request), key="study_input",
    )
    if submission is not None:
        text = (submission.text or "").strip()
        image = None
        if submission.files:
            try:
                image = read_image(submission.files[0])
            except ValueError as exc:
                st.warning(str(exc))
                return
        if not text and image is None:
            return
        submit_study_request(text, image)

    with st.container(key="summary-row"):
        _, summary_action = st.columns([3, 1])
        with summary_action:
            send_summary = st.button(
                "✉  Email revision summary",
                disabled=st.session_state.study_turns == 0 or bool(st.session_state.pending_request),
                help="Study a topic first, then send a revision sheet to your email.",
                width="content",
            )
        if send_summary:
            email_revision_summary()


def main():
    st.set_page_config(page_title="StudySnap AI", page_icon="📚", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    init_session()
    if not st.session_state.onboarded:
        onboarding()
    else:
        study_interface()


if __name__ == "__main__":
    main()
