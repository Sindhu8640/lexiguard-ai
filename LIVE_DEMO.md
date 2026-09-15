# LexiGuard AI live demonstration

- Website: [Open LexiGuard AI](https://lexiguard-ai-msjeudb7fxxxxvp8mafojv.streamlit.app/)
- Source: [Sindhu8640/lexiguard-ai](https://github.com/Sindhu8640/lexiguard-ai)
- Verification on 15 September 2026: cloud startup and the access-code gate were verified. A fresh run with the second fictional sample completed two generation requests, matched all 11 quotation entries and completed one explanation-check request. The counter showed 3/20; repeat explanation checking was disabled and the report was preserved. Readable comparison and the download control were visible. An earlier cloud session also displayed completed scan transcription and a report with 13 matching quotation entries.
- Known limitation observed live: the checker reported "No explanation issues detected" even though a concern used "work finished" without preserving the delivered-work condition and fee cap. This is a false-negative example. The workflow runs, but its explanations still need human comparison with the original PDF.

## Demonstrate the project

1. Open the website. If asked, enter the private demo access code supplied separately by the project owner.
2. Upload `samples/LexiGuard_Test_02_Editing_Agreement.pdf` from this package.
3. Read the sharing notice and select the consent checkbox, then click **Generate report**.
4. Inspect the summary, clauses, concerns and quotation checks. Compare the cancellation conditions with page 1 of the sample PDF.
5. Click **Check explanations** once and inspect any findings or suggested wording.
6. Open **Compare with the first draft**, then use **Download current report (.txt)** to save the current report and checking results.
7. Click **Clear document and results** when finished.

Use the included fictional agreements for the demonstration. Generation depends on the configured Gemini key and available provider quota. Matching quotations and AI checking results do not establish legal accuracy. A private demo code and the API key must stay out of the submission ZIP and public repository.
