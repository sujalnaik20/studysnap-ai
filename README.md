# StudySnap AI

**Snap it. Understand it. Revise it.**

StudySnap AI is a Streamlit-based AI study assistant that uses Gemini Vision and
Chat to turn photos of notes, diagrams, textbook pages and questions into
easy-to-understand explanations and revision notes.

## Features

- Study material image analysis with Gemini Vision
- AI study chat with context-aware follow-up questions
- Key concepts, definitions, formulas, and revision notes
- Plain-text revision summary delivered through Gmail SMTP
- Downloadable revision sheet and email retry without regenerating the sheet
- Responsive Streamlit interface with text and image attachments
- Session-based conversation history and retry controls for failed answers

## Tech Stack

- Python 3.12 (recommended)
- Streamlit
- Google Gemini through `google-genai`
- Gmail SMTP through Python's built-in `smtplib` and `MIMEText`

Only Streamlit and google-genai are direct external dependencies. The default
model is `gemini-3.5-flash-lite`, a stable model with image input and text output.
To use another supported Gemini text/image model, update `MODEL_NAME` in `app.py`.
See [Gemini model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)
and the [Google GenAI SDK](https://github.com/googleapis/python-genai).

## Local Setup

Open a terminal inside `studysnap-ai` and create a virtual environment:

```bash
python -m venv venv
```

Activate on Windows:

```powershell
venv\Scripts\activate
```

Or on macOS / Linux:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace
all three placeholders with your own credentials. On Windows:

```powershell
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
```

- `GEMINI_API_KEY`: obtain a key from [Google AI Studio](https://aistudio.google.com/apikey).
  Make sure your project has access to the model and sufficient API quota.
- `GMAIL_ADDRESS`: the sender's Gmail address; students can use other email providers.
- `GMAIL_APP_PASSWORD`: the sender's **App Password**, never their normal Gmail password.
  Enable 2-Step Verification, then create an App Password in your Google Account.
  See [Google's App Password instructions](https://support.google.com/accounts/answer/185833).
  App Passwords may be unavailable on some managed or restricted accounts.

**Never commit API keys or Gmail App Passwords.** The real secrets file is
ignored by Git; only the placeholder example belongs in the repository.

Run from the project directory:

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

## How to Use

1. Enter your name and a valid email address; click **Start Studying 🚀**.
2. Type a study question or use the chat input's **+** button to attach one JPG,
   JPEG, or PNG (up to 4 MB). You can submit an image without typing a question.
3. Ask follow-ups such as “Explain the formula” or “Give me five practice questions.”
4. After a successful answer, click **📧 Send Revision Summary**. StudySnap uses
   the same Gemini conversation to prepare the sheet and sends it to your email.
5. View or download the sheet in the revision expander. If sending fails, retry
   with the same button. A new successful study answer makes the next summary refresh.

The summary button is disabled while a study answer is pending or before the
first successful answer. Failed requests have **Retry answer** and **Dismiss
question** controls. A dismissed question stays visible but is not guaranteed
to be part of Gemini's context.

## Streamlit Community Cloud Deployment

1. Push these six project files to a GitHub repository, keeping the real secrets
   file excluded. Using the project contents as the repository root is simplest.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and create an app.
3. Select your repository and branch. Set the entrypoint to `app.py`, or to
   `studysnap-ai/app.py` if you uploaded the folder inside a larger repository.
4. In **Advanced settings**, select Python 3.12 and paste your real
   `GEMINI_API_KEY`, `GMAIL_ADDRESS`, and `GMAIL_APP_PASSWORD` values into **Secrets**
   in the same TOML format as the example.
5. Deploy. Streamlit installs `requirements.txt` automatically. Follow
   [Streamlit's deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
   and [secrets guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).
6. Verify the full flow with your credentials: onboard, upload a clear study
   image, ask a follow-up, request a summary, and check inbox and spam folders.

No database, authentication system, or Node.js build is required.

## Data and Troubleshooting

Name, email, images, and displayed messages live in `st.session_state`; the app
does not write them to disk. The Gemini client is cached, but every student has
a separate chat object. Reruns preserve the chat; browser refreshes, closed
connections, and server restarts can reset it. Google's and Gmail's own data
handling policies also apply: study text and images go to Gemini, and requested
summaries go through the sender's Gmail account to the student's email.

- **Missing credentials:** add secrets locally or in Community Cloud app settings.
- **Gemini error:** check key, quota, network access, and model availability.
  Empty or blocked answers show an error instead of an empty chat bubble.
- **Unclear image:** use a sharper photo with readable text; keep the file under 4 MB.
  Inline images remain in the chat context, so very long sessions with many
  images can reach API request or context limits. Start a fresh session if needed.
- **Gmail sign-in failed:** check the sender address and App Password. Spaces
  in the displayed App Password are removed automatically.
- **Mail connection failed:** check access to `smtp.gmail.com:465` and Gmail limits.
  The sheet stays available to download or resend. Check the inbox before a
  retry because a network interruption can occur after Gmail accepts a message.
- **Message sent but missing:** check spam and the recipient address entered at onboarding.

The app handles service errors without revealing keys or raw tracebacks. Gemini
can make mistakes; verify important formulas and unreadable material against your source.
