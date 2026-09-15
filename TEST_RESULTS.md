# Validation results

Validated on 15 September 2026.

- 24 standalone tests in `tests/test_app.py` passed with mocked AI responses.
- 42 earlier regression tests passed against the final app, covering report validation, quote repair, failure paths, comparison, downloads and document changes.
- A real Streamlit AppTest run confirmed clean startup, report rendering, consent, comparison and downloads. Clicking Check explanations made one mocked request, displayed findings, disabled repeat checking and preserved the report; rerunning made no extra request.
- PDF rendering and image-only PDF handling were exercised locally. Scan transcription responses were mocked.
- Streamlit Community Cloud startup and the access-code gate were verified at the URL in `LIVE_DEMO.md`. A fresh selectable-text run of sample 02 completed two generation requests and matched all 11 quotation entries. The separate explanation check made one request, bringing the counter to 3/20; its button then disabled and the report was preserved. Readable comparison and the download control were visible. An earlier deployed session displayed completed scan transcription and a report with 13 of 13 matching quotation entries.
- Known false negative observed live: the explanation checker returned "No explanation issues detected" while a concern described "work finished" without retaining the delivered-work condition and fee cap. This demonstrates that a successful check result does not establish explanation accuracy. Source comparison remains necessary.

Offline tests used bundled Python with installed Streamlit/Google SDK packages from the local project. Their AI responses were mocked to make failure cases reproducible. Live checks used the deployed app and configured provider. These checks establish the observed sample workflow behavior, not legal accuracy, general OCR quality or continued provider availability. The Docker image was not built.
