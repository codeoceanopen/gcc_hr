# GCC HR Compliance -- Permissions

## Roles

| Role | New in this app? | Purpose |
|---|---|---|
| System Manager | standard Frappe | Full access, including the two doctypes no other role can write. |
| GCC HR Administrator | **new** | Full configuration access (Country/Company Settings, Rules, Thresholds, Score Bands). The app's own "super admin" role, scoped to GCC HR doctypes only -- doesn't imply System Manager. |
| HR Manager | standard HRMS/ERPNext | Read country settings, write company settings, full access to Employee Compliance Profile and Compliance Documents, read Compliance Checks/Rules. |
| HR Officer | **new** | Day-to-day data entry: create/edit Employee Compliance Profile and Compliance Documents. No settings/rules access. |
| Payroll Manager | **new** | Read company settings; write on GOSI Settings/Employee Profile; read on Payroll Compliance Check and GOSI Payroll Calculation (both system-created only). |
| Payroll Officer | **new** | Write on GOSI Employee Profile (day-to-day registration data entry); read on Payroll Compliance Check and GOSI Payroll Calculation. |
| Compliance Manager | **new** | Full read/write on the compliance engine itself: Rules, Score Bands, Document Types, Thresholds. Read-only on the audit log. |
| Compliance Officer | **new** | Runs compliance day-to-day: write on Compliance Documents/Profiles, read on Rules/Checks. Cannot change rule configuration. |
| Government Integration Manager | **new** | Write access on Company Settings' government-integration fields (Phase 1); create/write on `Government Submission Type` and `Government Submission` (Phase 5) -- the role that actually files things with governments, manually, through this app's tracked workflow. |
| Employee | standard Frappe/HRMS | Read-only on their own Employee Compliance Profile / Compliance Documents / Compliance Checks, automatically scoped to their own record by Frappe's User Permission mechanism (a Link field to `Employee` is restricted for any user with a User Permission on `Employee`) -- no custom `permission_query_conditions` needed. |

## Per-doctype permission summary (Phase 1-10)

Exact rows are the source of truth (`gcc_hr_core/doctype/*/*.json`); this is a summary. "create"/"write" columns list which *additional* roles get that right beyond System Manager and GCC HR Administrator, who always have full create/write/delete.

| DocType | create | write | delete | read-only roles |
|---|---|---|---|---|
| HR Country Settings | -- | -- | -- | HR Manager, Compliance Manager |
| GCC HR Company Settings | -- | HR Manager, Government Integration Manager | -- | Payroll Manager |
| Employee Compliance Profile | HR Manager, HR Officer | + Compliance Manager | -- | Compliance Officer, Payroll Manager, Employee (own record only) |
| HR Document Type | Compliance Manager | Compliance Manager | -- | HR Officer |
| HR Compliance Document | HR Manager, HR Officer | + Compliance Manager, Compliance Officer | -- | Employee (own record only) |
| HR Document Expiry Threshold | Compliance Manager | Compliance Manager | -- | -- |
| HR Compliance Rule | Compliance Manager | Compliance Manager | -- | Compliance Officer |
| HR Compliance Check | -- | -- | -- | Compliance Manager, Compliance Officer, HR Manager, Employee (own record only). **Nobody** but System Manager/GCC HR Administrator can create or write -- every row is written exclusively by the compliance engine via `insert(ignore_permissions=True)`, so it stays a true run history. |
| HR Compliance Score Band | Compliance Manager | Compliance Manager | -- | -- |
| HR Audit Log | -- | -- | -- | System Manager, GCC HR Administrator, Compliance Manager. **Nobody** has create/write/delete -- written only by `gcc_hr_core/audit.py:log_action()` via `insert(ignore_permissions=True)`. Truly append-only, covered by `test_hr_audit_log.py`. |
| Saudi Employee Profile (Phase 2) | HR Manager, HR Officer | HR Manager, HR Officer | -- | Compliance Manager (write too), Compliance Officer, Employee (own record only) |
| GOSI Settings (Phase 3) | Payroll Manager | Payroll Manager | -- | Compliance Manager |
| GOSI Employee Profile (Phase 3) | Payroll Manager, Payroll Officer | Payroll Manager, Payroll Officer | -- | Compliance Manager, Employee (own record only) |
| GOSI Payroll Calculation (Phase 3) | -- | -- | -- | Payroll Manager, Payroll Officer, Compliance Manager. **Nobody** but System Manager/GCC HR Administrator can create -- every row is written by `gosi.py:calculate_for_salary_slip()` on Salary Slip submit. |
| Payroll Compliance Check (Phase 3) | -- | -- | -- | Payroll Manager, Payroll Officer, Compliance Manager, HR Manager. **Nobody** but System Manager/GCC HR Administrator can create -- every row is written by `gcc_hr_core/payroll.py:validate_payroll_compliance()` on Payroll Entry submit. |
| Saudization Requirement (Phase 4) | Compliance Manager | Compliance Manager | -- | HR Manager |
| Saudization Profile (Phase 4) | -- | HR Manager, Compliance Manager | -- | Compliance Officer. **Nobody** but System Manager/GCC HR Administrator can create -- every row is written by `countries/saudi_arabia/saudization.py:recalculate()` (daily scheduler job or the "Recalculate Now" API); HR Manager/Compliance Manager can still hand-correct a row's `activity`/`business_size` match keys. |
| Government Submission Type (Phase 5) | Government Integration Manager | Government Integration Manager | -- | -- |
| Government Submission (Phase 5) | Government Integration Manager | Government Integration Manager | -- | HR Manager, Compliance Manager. Unlike the engine-only doctypes above, Government Integration Manager genuinely needs create/write here -- every state transition (generate/validate/mark ready/record submission/upload response/complete) is a human action this role takes, not something a scheduler writes on its own; `api/government.py` re-checks write permission before calling into `gcc_hr_core/government.py`'s `db_set`-based transitions. |
| Qatar Employee Profile (Phase 6) | HR Manager, HR Officer | HR Manager, HR Officer | -- | Compliance Manager (write too), Compliance Officer, Employee (own record only) -- identical shape to Saudi Employee Profile |
| Qatarization Requirement (Phase 6) | Compliance Manager | Compliance Manager | -- | HR Manager |
| Qatarization Profile (Phase 6) | -- | HR Manager, Compliance Manager | -- | Compliance Officer. **Nobody** but System Manager/GCC HR Administrator can create -- every row is written by `countries/qatar/qatarization.py:recalculate()` (daily scheduler job or the "Recalculate Now" API) -- identical shape to Saudization Profile |
| UAE Employee Profile (Phase 7) | HR Manager, HR Officer | HR Manager, HR Officer | -- | Compliance Manager (write too), Compliance Officer, Employee (own record only) -- identical shape to Saudi/Qatar Employee Profile |
| Emiratisation Requirement (Phase 7) | Compliance Manager | Compliance Manager | -- | HR Manager |
| Emiratisation Profile (Phase 7) | -- | HR Manager, Compliance Manager | -- | Compliance Officer. **Nobody** but System Manager/GCC HR Administrator can create -- every row is written by `countries/united_arab_emirates/emiratisation.py:recalculate()` -- identical shape to Saudization/Qatarization Profile |
| Oman Employee Profile (Phase 8) | HR Manager, HR Officer | HR Manager, HR Officer | -- | Compliance Manager (write too), Compliance Officer, Employee (own record only) -- identical shape to the other three countries' Employee Profile |
| Omanisation Requirement (Phase 8) | Compliance Manager | Compliance Manager | -- | HR Manager |
| Omanisation Profile (Phase 8) | -- | HR Manager, Compliance Manager | -- | Compliance Officer. **Nobody** but System Manager/GCC HR Administrator can create -- every row is written by `countries/oman/omanisation.py:recalculate()` -- identical shape to the other three countries' Profile |
| Bahrain Employee Profile (Phase 9) | HR Manager, HR Officer | HR Manager, HR Officer | -- | Compliance Manager (write too), Compliance Officer, Employee (own record only) -- identical shape to the other countries' Employee Profile |
| Bahrainisation Requirement (Phase 9) | Compliance Manager | Compliance Manager | -- | HR Manager |
| Bahrainisation Profile (Phase 9) | -- | HR Manager, Compliance Manager | -- | Compliance Officer. **Nobody** but System Manager/GCC HR Administrator can create -- every row is written by `countries/bahrain/bahrainisation.py:recalculate()` -- identical shape to the other countries' Profile |
| Kuwait Employee Profile (Phase 10) | HR Manager, HR Officer | HR Manager, HR Officer | -- | Compliance Manager (write too), Compliance Officer, Employee (own record only) -- identical shape to the other countries' Employee Profile |
| Kuwaitisation Requirement (Phase 10) | Compliance Manager | Compliance Manager | -- | HR Manager |
| Kuwaitisation Profile (Phase 10) | -- | HR Manager, Compliance Manager | -- | Compliance Officer. **Nobody** but System Manager/GCC HR Administrator can create -- every row is written by `countries/kuwait/kuwaitisation.py:recalculate()` -- identical shape to the other countries' Profile |

## Company / multi-tenant isolation

No custom `permission_query_conditions` or `has_permission` hook exists in this app. Every Phase 1 doctype that should be company-scoped carries a `company` (or `employee`) Link field, and Frappe's own User Permission mechanism already restricts any doctype with such a field for a user who has a User Permission record on `Company`/`Employee` -- the same mechanism ERPNext itself relies on for multi-company isolation. Building a parallel mechanism would duplicate something Frappe already solves generically.

## Secrets

Still no secrets, for any of the six countries this app ships. `Government Submission Type`/`Government Submission` never store a government API credential, because this app never calls a government API -- see ARCHITECTURE.md's "Government Integration (Phase 5)" section and the per-country sections following it (Phases 6-10) and SECURITY.md. If a future phase ever integrates a *verified* government API, its credentials must use Frappe's `Password` fieldtype (encrypted at rest via `encrypt: 1`), never a fixture, and never committed to Git.
