# Validation results

Validated on 15 September 2026.

- 24 standalone tests in `tests/test_app.py` passed with mocked AI responses.
- 42 earlier regression tests passed against the final app, covering report validation, quote repair, failure paths, comparison, downloads and document changes.
- A real Streamlit AppTest run confirmed clean startup, report rendering, consent, comparison and downloads. Clicking Check explanations made one mocked request, displayed findings, disabled repeat checking and preserved the report; rerunning made no extra request.
- PDF rendering and image-only PDF handling were exercised locally. Scan transcription responses were mocked.

Tests used bundled Python with installed Streamlit/Google SDK packages from the local project. AI responses were mocked to make failure cases reproducible. These checks do not establish legal accuracy, live OCR quality or live provider availability. The Docker image was not built. Cloud deployment is verified separately.
