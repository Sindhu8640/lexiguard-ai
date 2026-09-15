# LexiGuard AI — Project report

## Problem
Legal documents can be long and difficult to understand. Readers need help finding key obligations and conditions without treating a simplified summary as a substitute for the source.

## Proposed solution
LexiGuard is an AI-assisted PDF analysis workflow that produces a summary, important clauses and potential concerns with page references. It combines AI generation with deterministic validation and a bounded correction step.

## Architecture
Streamlit provides the interface. pypdf extracts selectable text. For scans, pypdfium2 renders pages in memory and Gemini transcribes the images. Pydantic defines required report and checking fields. Gemini generates the first draft and reviews it. Python checks quoted wording against the extracted page text. Failed quotations can trigger one additional repair request. A separate explanation checker looks for potentially omitted or changed conditions and proposes wording for human review.

The conditional branch is explicit: a quote failure can cause a correction action; matching quotes skip that action. The tool does not have unrestricted autonomy, execute document instructions, browse links in documents or make legal decisions.

## Data flow
PDF upload → local extraction or optional scan transcription → user-approved AI draft → AI review → Python field/quote checks → optional single quote repair → optional explanation assessment → readable comparison and text export.

## Tests and evaluation
Two fictional agreements provide contrasting terms. The first includes automatic renewal, an additional early exit fee, confidentiality and a liability limitation. The second changes parties, fee basis and cancellation conditions; it explicitly excludes automatic renewal and an additional exit fee, and omits three other categories.

In guided user testing, the app displayed a quote mismatch when AI inserted an ellipsis. The user also confirmed matching quotes in a two-request run and correct identification of explicit negative provisions versus omitted categories in the second sample. A manual explanation review found that cancellation wording compressed a timing condition; this motivated the separate explanation checker.

Automated tests simulate responses to test validation and control flow. Their passing results are not a measure of legal accuracy. New OCR and explanation-check model quality requires live evaluation after setup/deployment.

## Limitations and future work
AI and OCR errors remain possible. Exact quote checks validate wording and page placement only. Explanation findings are probabilistic and may be wrong. The UI preserves uncertainty and does not automatically accept suggested rewrites. The demonstration has explicit file/context/request limits and is not an exhaustive legal-analysis product.

Production work would require a representative evaluation corpus, stronger authentication and account-level abuse controls, privacy/compliance review, provider and retention decisions, monitoring, accessibility testing, and professional review of the intended use.

## Submission items
Source code, pinned dependencies, sample PDFs, a sample checklist, offline tests, local/deployment instructions, and a container configuration are included. Add the actual live URL only after the cloud deployment succeeds and has been tested.
