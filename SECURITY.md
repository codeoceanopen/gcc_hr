# Security Policy

## Reporting a vulnerability

Please report suspected security issues privately rather than opening a public GitHub issue -- email the maintainer listed in `pyproject.toml` (`app_email` in `gcc_hr/hooks.py`). Include reproduction steps and, if possible, the affected Frappe/ERPNext/HRMS/gcc_hr versions.

## What's in scope

- The `gcc_hr` app's own doctypes, API endpoints (`gcc_hr/api/*.py`), hooks, and the Vue frontend (`frontend/`).
- Not in scope: Frappe/ERPNext/HRMS core (report those upstream at https://github.com/frappe/frappe/security).

## Security posture (Phase 1-10)

- **No secrets in code or fixtures, still true across all six countries this app ships.** `Government Submission Type`/`Government Submission` (Phase 5) store no government API credential, for any country's submission types, because this app never calls a government API -- there's nothing to protect. If a future phase ever integrates a *verified* one, its credentials will use Frappe's `Password` fieldtype (encrypted at rest), never appear in a fixture, and never be committed to Git.
- **`HR Audit Log` is append-only.** No role -- including System Manager -- has `create`/`write`/`delete` permission on it; it's written exclusively by `gcc_hr_core/audit.py:log_action()` via `insert(ignore_permissions=True)`. Compliance/config history can't be edited after the fact.
- **`HR Compliance Check` is immutable history.** No role can create or edit one by hand; every row comes from the compliance engine (`gcc_hr_core/compliance_engine/engine.py:run_compliance_check()`).
- **`Government Submission`'s state machine is enforced server-side, not by the Desk form.** Every transition (`generate`/`validate_submission`/`mark_ready`/`record_manual_submission`/`upload_response`/`complete`) checks the submission's current status in `gcc_hr_core/government.py` before acting; `api/government.py` re-checks write permission itself first, since those functions write via `db_set` (which bypasses the normal permission pipeline).
- **Generated/uploaded government documents are private by default.** `generate()` attaches the generated document via `save_file(..., is_private=1)`, and the response-document upload flow (`FileUploader` with `private: true`) does the same -- both may contain PII (Iqama numbers, salary/workforce breakdowns), so they're only reachable through `Government Submission`'s own doctype permissions, not a public file URL.
- **Role-based access from day one**, not retrofitted -- see PERMISSIONS.md.
- **Company/Employee data isolation** relies on Frappe's own User Permission mechanism rather than a custom, easier-to-get-wrong `permission_query_conditions` implementation.
- **The Vue frontend never contains business logic.** Salary computation, compliance scoring, expiry-status calculation, rule evaluation, and the Government Submission state machine all happen server-side; the SPA only renders what the API returns and calls whitelisted endpoints (`api/dashboard.py`, `api/compliance.py`, `api/saudization.py`, `api/qatarization.py`, `api/emiratisation.py`, `api/omanisation.py`, `api/bahrainisation.py`, `api/kuwaitisation.py`, `api/government.py`) that themselves check permissions (`frappe.only_for`, `frappe.has_permission`) before doing anything.
- **No fabricated government integrations, for any of the six countries.** Nothing in this app calls, or pretends to call, a GOSI/Qiwa/Mudad/Nitaqat/MOHRE/PASI/SIO/LMRA/PAM/WPS API -- see ARCHITECTURE.md's "Government Integration (Phase 5)" section and the per-country sections following it (Phases 6-10) and the brief's own "Important Government Integration Rule." The Government Integration Framework only generates documents from data this app already has and tracks a human's manual filing on the real portal; every `Government Submission Type`, for every country, names the real portal URL rather than implying an API call.

## Dependencies

- Backend: whatever `erpnext`/`hrms`/`frappe` pin in this bench (see the top-level `README.md` for the versions this app was built and tested against).
- Frontend (`frontend/package.json`): `frappe-ui`, `vue`, `vue-router`, `pinia`, `@vueuse/core`, `lucide-vue-next`, `tailwindcss`. Run `yarn audit` / `pip-audit` (the CI Linters workflow already runs the latter) before upgrading.
