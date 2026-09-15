# LexiGuard AI

A Python/Streamlit learning prototype that reads PDF agreements, creates a structured report, checks quoted evidence, and flags possible missing conditions in AI explanations.

## Quick local setup (Windows / VS Code)

Open this folder in VS Code and use Terminal → New Terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` using the example file. Put your own Google Gemini API key in it:

```toml
GEMINI_API_KEY = "your-own-key"
```

Never upload that real secrets file to GitHub or include it in your submission ZIP.

Start the app:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Open http://127.0.0.1:8501 and keep the terminal running. The API key can alternatively be supplied through the `GEMINI_API_KEY` environment variable.

## Demonstration steps

1. Upload `samples/LexiGuard_Test_02_Editing_Agreement.pdf`.
2. Read the privacy notice and select the document-sharing checkbox.
3. Click **Generate report**. Check the summary, eight clause categories, potential concerns, and quote matches.
4. Click **Check explanations** once. It uses one extra AI request and flags potential changes in meaning. Inspect any source evidence and suggested wording; the report is not automatically rewritten.
5. Open **Compare with the first draft** and switch between readable versions.
6. Click **Download current report (.txt)**. The download includes check findings and warnings.
7. Use **Clear document and results** to remove this document from the active app session. The API-attempt counter remains.

For a scanned PDF, first select **Read scanned pages (1 AI request)**. Inspect the extracted text and confirm it before generating the report. If a PDF has garbled embedded text, use **Treat every page as a scan** for documents within the scan limit.

## What is implemented

- Selectable-text PDFs up to 60 pages, 20 MB and 120,000 extracted characters; no silent truncation.
- Optional AI transcription of up to eight scanned pages per document, with physical page numbers preserved.
- Required clause entries: payments, term, renewal, cancellation, early exit fee, confidentiality, changes to terms, liability.
- One draft and one AI review; Python checks field structure and exact quotes after whitespace normalization.
- One conditional quote-correction request when reviewed quotations fail. Invalid replacements are not accepted.
- Optional, separate AI explanation check for missing actors, limits, exceptions and timing conditions. Its evidence is also checked.
- Readable first/current report comparison and UTF-8 text downloads.
- Per-document consent, session-scoped results, clear control, input limits, timeouts, disabled automatic SDK retries, and a 20-request demo-session ceiling.
- Optional shared demo access code using `APP_ACCESS_CODE` in hosting secrets. This is a simple demo gate, not production user management.

## Request and cost behavior

Normal generation makes two API requests; quote correction can add one. Explanation checking adds at most one per generated report. Scan reading adds one per attempt. View changes and downloads do not call Gemini. A complete scanned-document flow therefore normally uses four requests, or five with quote correction. Explicit scan retries count too.

The displayed session counter is a browser-session guard, not an account-wide quota or money cap. Other users/sessions can consume the same owner key. Google project quotas and any charges still apply. Longer inputs and scans consume more tokens. Use a private demo access code and your provider's usage controls when publishing an owner-funded demo.

## Accuracy and privacy limits

This is not legal advice or a production-ready legal review system. AI review can miss errors or introduce them. The explanation checker is also AI and can produce false positives, unsupported suggestions, or miss omissions. Matching a quote does not verify its interpretation or establish that a clause is enforceable.

Scan transcription can misread words, numbers and punctuation. For OCR pages, quote checks compare against the transcription, not an independently verified image. Inspect the original image and transcription. Dense, rotated, handwritten or poor-quality scans may fail.

Text extraction occurs locally first. Selected actions send text and, for scan reading, page images to Google Gemini. The app does not intentionally persist uploaded documents to disk or share report state across sessions; hosting and provider retention policies still apply. Clearing the app cannot retract data already sent to a provider. Use fictional documents for demonstrations and do not assume confidential documents are appropriate for your chosen API tier.

## Automated tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

These tests use mocked AI responses and the bundled fictional samples. They verify orchestration, field/evidence validation, failure paths, isolation and exports. They do not establish model quality on real documents. Live scan-reading and explanation-check accuracy should be evaluated separately on your own permitted samples.

## Deploy to Streamlit Community Cloud

1. Sign in to GitHub and create a repository for this project.
2. Upload `app.py`, `requirements.txt`, `.streamlit/config.toml`, the README and samples. Never upload `.streamlit/secrets.toml`, `.env`, `.venv` or actual credentials.
3. Sign in at https://share.streamlit.io/ and create an app from that repository. Select `app.py` as the entry point and Python 3.12.
4. In the deployment's Advanced settings / Secrets, enter your own `GEMINI_API_KEY` and a private `APP_ACCESS_CODE` for the demo. Share the access code separately with your evaluator.
5. Deploy, wait for dependency installation, then test the generated `.streamlit.app` URL with a fictional sample. Copy that actual URL into your submission; this package does not invent a hosted URL.

If the provider rejects a pinned dependency version, inspect its build log before changing versions. The versions here match the locally available SDK/UI environment; the final cloud build must still be checked.

Official references:
- Streamlit deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit dependencies: https://docs.streamlit.io/deploy/concepts/dependencies
- Gemini structured output: https://ai.google.dev/gemini-api/docs/structured-output
- Gemini image input: https://ai.google.dev/gemini-api/docs/image-understanding
- Model: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite

## Optional container deployment

The included Dockerfile runs Streamlit on port 8501. Supply `GEMINI_API_KEY` and `APP_ACCESS_CODE` through your hosting platform's secret environment settings. Do not bake secrets into the image. A container image/build configuration is not evidence that a cloud deployment has succeeded.
