# GCC HR Compliance -- Database (Phase 1-10)

## Doctypes introduced by this app

Under Frappe module **"GCC HR Core"** (`gcc_hr/gcc_hr_core/doctype/`), except: `Saudi Employee Profile`, `GOSI Settings`, `GOSI Employee Profile`, `GOSI Payroll Calculation`, `Saudization Requirement`, `Saudization Profile` (module **"Saudi Arabia"**, `gcc_hr/saudi_arabia/doctype/`); `Qatar Employee Profile`, `Qatarization Requirement`, `Qatarization Profile` (module **"Qatar"**, `gcc_hr/qatar/doctype/`, Phase 6); `UAE Employee Profile`, `Emiratisation Requirement`, `Emiratisation Profile` (module **"United Arab Emirates"**, `gcc_hr/united_arab_emirates/doctype/`, Phase 7); `Oman Employee Profile`, `Omanisation Requirement`, `Omanisation Profile` (module **"Oman"**, `gcc_hr/oman/doctype/`, Phase 8); `Bahrain Employee Profile`, `Bahrainisation Requirement`, `Bahrainisation Profile` (module **"Bahrain"**, `gcc_hr/bahrain/doctype/`, Phase 9); `Kuwait Employee Profile`, `Kuwaitisation Requirement`, `Kuwaitisation Profile` (module **"Kuwait"**, `gcc_hr/kuwait/doctype/`, Phase 10) -- see ARCHITECTURE.md's "Why two `saudi_arabia` folders" (the same split applies to each country's module). `Government Submission Type`/`Government Submission` (Phase 5) are country-agnostic, so they stay in "GCC HR Core" even though they're populated by each of the six countries' packages independently.

| DocType | Autoname | Key fields |
|---|---|---|
| `HR Country Settings` | `field:country` (so the docname *is* the country name) | country (Link Country, unique), country_code, currency, language, is_active, compliance_engine_enabled, government_integration_enabled |
| `GCC HR Company Settings` | `field:company` | company (Link Company, unique), country (Link HR Country Settings), payroll_frequency/processing_day/cutoff_day, government_integration_enabled, api_environment, integration_status, compliance_alert_email, hr_manager/compliance_officer/payroll_manager (Link User) |
| `Employee Compliance Profile` | `field:employee` | employee (Link Employee, unique), company/country (derived), nationality, national_id, passport_number/expiry (fetched from Employee), employment_type, contract (Link Contract), basic/housing/transport/other/total salary (fetched from Contract's custom fields), compliance_score, compliance_status, last/next_compliance_check |
| `HR Document Type` | `format:{country}-{document_type_name}` | country, document_type_name, requires_expiry, requires_government_verification, is_active |
| `HR Compliance Document` | naming series `HR-DOC-.YYYY.-` | employee, company/country (derived), document_type, document_number, issue_date, expiry_date, status (Valid/Expiring Soon/Expired), days_remaining, government_verified |
| `HR Document Expiry Threshold` | random hash | label, threshold_days, severity, country (optional), document_type (optional), is_active |
| `HR Compliance Rule` | `field:rule_code` | rule_code (unique), rule_name, country, category, severity, enabled, check_method (dotted Python path), effective_from/to |
| `HR Compliance Check` | naming series `HR-CHK-.YYYY.-` | employee, company/country, check_date, compliance_score, status, passed_rules/warnings/critical_issues, `results` (Table -> HR Compliance Check Result) |
| `HR Compliance Check Result` | child table | rule (Link HR Compliance Rule), category/severity (fetched), result (Passed/Failed/Skipped), message, recommended_action |
| `HR Compliance Score Band` | random hash | status_label, min_score, max_score, compliance_status, color, country (optional) |
| `HR Audit Log` | random hash | timestamp, user, action, company, employee, reference_doctype/name (Dynamic Link), old_value/new_value (JSON text), reason, source |
| `Saudi Employee Profile` (Phase 2) | `field:employee` | employee (Link Employee, unique), nationality_status (Saudi/Non-Saudi), profession, sponsor, iqama_number/expiry, border_number, visa_number/type, work_permit_number/expiry, gosi_registration_number (identity reference only -- see GOSI Employee Profile for the authoritative registration record), qiwa_contract_status |
| `GOSI Settings` (Phase 3) | random hash | applicable_employee_category (Saudi/Non-Saudi), effective_from/to, employee_contribution_rate, employer_contribution_rate, contribution_floor/ceiling |
| `GOSI Employee Profile` (Phase 3) | `field:employee` | employee (Link Employee, unique), registration_status (Not Registered/Pending/Registered), gosi_number, registration_date, status (Active/Suspended -- whether contributions should currently be calculated) |
| `GOSI Payroll Calculation` (Phase 3) | naming series `HR-GOSI-.YYYY.-` | employee, salary_slip (Link Salary Slip, unique), gosi_settings (Link GOSI Settings, the row actually applied), basic_salary, eligible_allowances, contribution_base, employee_contribution, employer_contribution, total_contribution |
| `Payroll Compliance Check` (Phase 3) | naming series `HR-PCC-.YYYY.-` | payroll_entry (Link Payroll Entry), company (derived), check_date, total_employees, passed, warnings, critical, status (Passed/Warnings/Blocked), `employees` (Table -> Payroll Compliance Check Employee) |
| `Payroll Compliance Check Employee` (Phase 3) | child table | employee, employee_name (fetched), compliance_check (Link HR Compliance Check), status/critical_issues (fetched from compliance_check) |
| `Saudization Requirement` (Phase 4) | random hash | company (optional override), activity/business_size (optional match keys), target_percentage, effective_from/to |
| `Saudization Profile` (Phase 4) | `field:company` | company (Link Company, unique), activity, business_size, employee_count, saudi_employee_count, non_saudi_employee_count, saudi_percentage, target_percentage, gap, compliance_status (Compliant/At Risk/Non-Compliant), last_calculation |
| `Government Submission Type` (Phase 5) | `field:submission_type_code` | submission_type_code (unique), submission_type_name, country, category, reference_doctype, generate_method/validate_method (dotted Python paths), portal_url, portal_instructions, is_active |
| `Government Submission` (Phase 5) | naming series `GOV-SUB-.YYYY.-` | company, submission_type, status (Draft/Generated/Validated/Ready for Submission/Submitted/Response Uploaded/Completed), outcome (Accepted/Rejected), reference_doctype/name (Dynamic Link), generated_document (Attach)/generated_on, validation_errors/validated_on, submitted_on/submitted_by/government_reference_number, response_document (Attach)/response_uploaded_on, notes |
| `Qatar Employee Profile` (Phase 6) | `field:employee` | employee (Link Employee, unique), nationality_status (Qatari/Non-Qatari), profession, sponsor, qid_number/expiry, border_number, visa_number/type, work_permit_number/expiry, wps_registered (Check), wps_bank_name |
| `Qatarization Requirement` (Phase 6) | random hash | company (optional override), activity/business_size (optional match keys), target_percentage, effective_from/to |
| `Qatarization Profile` (Phase 6) | `field:company` | company (Link Company, unique), activity, business_size, employee_count, qatari_employee_count, non_qatari_employee_count, qatari_percentage, target_percentage, gap, compliance_status (Compliant/At Risk/Non-Compliant), last_calculation |
| `UAE Employee Profile` (Phase 7) | `field:employee` | employee (Link Employee, unique), nationality_status (Emirati/Non-Emirati), profession, sponsor, eid_number/expiry, border_number, visa_number/type, work_permit_number/expiry, wps_registered (Check), wps_bank_name |
| `Emiratisation Requirement` (Phase 7) | random hash | company (optional override), activity/business_size (optional match keys), target_percentage, effective_from/to |
| `Emiratisation Profile` (Phase 7) | `field:company` | company (Link Company, unique), activity, business_size, employee_count, emirati_employee_count, non_emirati_employee_count, emirati_percentage, target_percentage, gap, compliance_status (Compliant/At Risk/Non-Compliant), last_calculation |
| `Oman Employee Profile` (Phase 8) | `field:employee` | employee (Link Employee, unique), nationality_status (Omani/Non-Omani), profession, sponsor, resident_card_number/expiry, border_number, visa_number/type, work_permit_number/expiry, pasi_registered (Check), wps_registered (Check) |
| `Omanisation Requirement` (Phase 8) | random hash | company (optional override), activity/business_size (optional match keys), target_percentage, effective_from/to |
| `Omanisation Profile` (Phase 8) | `field:company` | company (Link Company, unique), activity, business_size, employee_count, omani_employee_count, non_omani_employee_count, omani_percentage, target_percentage, gap, compliance_status (Compliant/At Risk/Non-Compliant), last_calculation |
| `Bahrain Employee Profile` (Phase 9) | `field:employee` | employee (Link Employee, unique), nationality_status (Bahraini/Non-Bahraini), profession, sponsor, cpr_number/expiry, border_number, visa_number/type, work_permit_number/expiry, sio_registered (Check), wps_registered (Check) |
| `Bahrainisation Requirement` (Phase 9) | random hash | company (optional override), activity/business_size (optional match keys), target_percentage, effective_from/to |
| `Bahrainisation Profile` (Phase 9) | `field:company` | company (Link Company, unique), activity, business_size, employee_count, bahraini_employee_count, non_bahraini_employee_count, bahraini_percentage, target_percentage, gap, compliance_status (Compliant/At Risk/Non-Compliant), last_calculation |
| `Kuwait Employee Profile` (Phase 10) | `field:employee` | employee (Link Employee, unique), nationality_status (Kuwaiti/Non-Kuwaiti), profession, sponsor, civil_id_number/expiry, border_number, visa_number/type, work_permit_number/expiry, wps_registered (Check) |
| `Kuwaitisation Requirement` (Phase 10) | random hash | company (optional override), activity/business_size (optional match keys), target_percentage, effective_from/to |
| `Kuwaitisation Profile` (Phase 10) | `field:company` | company (Link Company, unique), activity, business_size, employee_count, kuwaiti_employee_count, non_kuwaiti_employee_count, kuwaiti_percentage, target_percentage, gap, compliance_status (Compliant/At Risk/Non-Compliant), last_calculation |

## Relationships

```
Company ──1:1── GCC HR Company Settings ──N:1── HR Country Settings
Employee ──1:1── Employee Compliance Profile ──N:1── HR Country Settings
Employee Compliance Profile ──N:1── Contract (party_type=Employee)
Employee Compliance Profile ──1:N── HR Compliance Document ──N:1── HR Document Type
HR Country Settings ──1:N── HR Document Type, HR Compliance Rule, HR Document Expiry Threshold, HR Compliance Score Band
Employee Compliance Profile ──1:N── HR Compliance Check ──1:N── HR Compliance Check Result ──N:1── HR Compliance Rule
Employee ──1:1── Saudi Employee Profile   (only when the employee's company's country is Saudi Arabia)
Employee ──1:1── GOSI Employee Profile
Employee ──1:N── GOSI Payroll Calculation ──1:1── Salary Slip
                                          ──N:1── GOSI Settings (whichever row was effective on the slip's posting date)
Payroll Entry ──1:1── Payroll Compliance Check ──1:N── Payroll Compliance Check Employee ──N:1── HR Compliance Check
Company ──1:1── Saudization Profile   (counts derived from Saudi Employee Profile.nationality_status, not stored redundantly)
Company/Activity/Business Size ──N:1── Saudization Requirement (matched by specificity, see ARCHITECTURE.md)
Government Submission ──N:1── Government Submission Type
Government Submission ──N:1── Company
Government Submission ──N:1── (reference_doctype, e.g. Saudization Profile or GOSI Employee Profile, via Dynamic Link)
Employee ──1:1── Qatar Employee Profile   (only when the employee's company's country is Qatar)
Company ──1:1── Qatarization Profile   (counts derived from Qatar Employee Profile.nationality_status, not stored redundantly)
Company/Activity/Business Size ──N:1── Qatarization Requirement (matched by specificity, same shape as Saudization Requirement)
Employee ──1:1── UAE Employee Profile   (only when the employee's company's country is United Arab Emirates)
Company ──1:1── Emiratisation Profile   (counts derived from UAE Employee Profile.nationality_status, not stored redundantly)
Company/Activity/Business Size ──N:1── Emiratisation Requirement (matched by specificity, same shape as Saudization Requirement)
Employee ──1:1── Oman Employee Profile   (only when the employee's company's country is Oman)
Company ──1:1── Omanisation Profile   (counts derived from Oman Employee Profile.nationality_status, not stored redundantly)
Company/Activity/Business Size ──N:1── Omanisation Requirement (matched by specificity, same shape as Saudization Requirement)
Employee ──1:1── Bahrain Employee Profile   (only when the employee's company's country is Bahrain)
Company ──1:1── Bahrainisation Profile   (counts derived from Bahrain Employee Profile.nationality_status, not stored redundantly)
Company/Activity/Business Size ──N:1── Bahrainisation Requirement (matched by specificity, same shape as Saudization Requirement)
Employee ──1:1── Kuwait Employee Profile   (only when the employee's company's country is Kuwait)
Company ──1:1── Kuwaitisation Profile   (counts derived from Kuwait Employee Profile.nationality_status, not stored redundantly)
Company/Activity/Business Size ──N:1── Kuwaitisation Requirement (matched by specificity, same shape as Saudization Requirement)
```

## Standard doctypes extended, not duplicated

- **Contract** (`erpnext.crm`) -- 11 Custom Fields added via `fixtures/custom_field.json`: `gcc_basic_salary`, `gcc_housing_allowance`, `gcc_transport_allowance`, `gcc_other_allowances`, `gcc_total_salary` (computed), `gcc_probation_period`, `gcc_notice_period`, `gcc_working_hours`, `gcc_annual_leave_days`, plus two layout Section/Column Break fields. `Employee Compliance Profile.basic_salary` etc. `fetch_from` these rather than storing salary twice.
- **Employee** (`erpnext`) -- zero new fields. `Employee Compliance Profile` is looked up by `employee` name (which *is* the Employee's docname, since `Employee Compliance Profile` is autonamed `field:employee`).
- **Gratuity** / **Gratuity Rule** / **Gratuity Rule Slab** (`hrms.payroll`) -- 4 `Gratuity Rule` rows seeded for KSA EOSB (Phase 3, see below) + 1 for Qatar EOSB (Phase 6, see below) + 1 for Oman EOSB (Phase 8, see below) + 1 for Bahrain EOSB (Phase 9, see below) + 4 for Kuwait EOSB (Phase 10, mirroring Saudi's 4-row shape, see below); no new fields, no new doctype. UAE's 3 EOSB `Gratuity Rule` rows (Phase 7) aren't seeded by this app at all -- `countries/united_arab_emirates/setup.py` calls `hrms.regional.united_arab_emirates.setup.setup()` directly and fixes up two field bugs on the rows it creates, rather than seeding a competing rule (see ARCHITECTURE.md's "UAE (Phase 7)" section). HR creates a `Gratuity` record and picks the applicable seeded rule, same as any other Frappe HR company.
- **Salary Slip** / **Payroll Entry** (`hrms.payroll`) -- zero new fields; extended via `doc_events` (`Salary Slip.on_submit`, `Payroll Entry.before_submit`, Phase 3) rather than any schema change.

## Seed data

`gcc_hr/install.py:after_install()` (idempotent, runs once, not re-synced on migrate -- these are user-editable settings):
- 6 `HR Country Settings` rows (Saudi Arabia, Qatar, UAE, Oman, Bahrain, Kuwait) -- all `is_active=1`, all `compliance_engine_enabled=0` until each country's rules are seeded starting Phase 2.
- 6 `HR Document Expiry Threshold` rows: 90/60/30/14 days -> Warning, 7 days -> Critical, 0 days -> Blocking.
- 4 `HR Compliance Score Band` rows: 90-100 Excellent/Compliant, 75-89 Compliant, 50-74 Warning, 0-49 Critical.

`gcc_hr/patches/v0_0/setup_saudi_arabia.py` (Phase 2), `v0_1/extend_saudi_arabia_payroll.py` (Phase 3), `v0_2/extend_saudi_arabia_saudization.py` (Phase 4) and `v0_3/extend_saudi_arabia_government.py` (Phase 5), all running once via `bench migrate`'s patch mechanism (`patches.txt`'s `[post_model_sync]` section) and all just re-invoking the same idempotent `countries/saudi_arabia/setup.py:setup()` -- v0_1/v0_2/v0_3 exist only because Frappe patches don't re-run just because the function they call gained new seed data. Together they seed:
- 10 `HR Document Type` rows (Iqama, Passport, Work Permit, Employment Contract, National ID, Health Certificate, Professional License, Driving License, Visa, Other).
- 7 `HR Compliance Rule` rows: 4 from Phase 2 (Iqama/work-permit/passport expiry, non-Saudi-Iqama-on-file) + 3 from Phase 3 (contract active, contract-vs-payroll salary match, GOSI registered).
- 4 `Gratuity Rule` rows for KSA EOSB (Phase 3): full award, and three resignation bands (1/3 at 2-5 years, 2/3 at 5-10, full at 10+).
- 2 `GOSI Settings` rows (Phase 3): Saudi and Non-Saudi categories, effective 2024-07-01, explicitly labelled as an illustrative starting point -- see the doctype's own `description` field.
- 1 global-fallback `Saudization Requirement` row (Phase 4): blank company/activity/business_size, 25% target, effective 2024-01-01, likewise labelled illustrative.
- 2 `Government Submission Type` rows (Phase 5): `SA_NITAQAT_REPORT` and `SA_GOSI_REGISTRATION`, each pointing at a `countries/saudi_arabia/government.py` generate/validate function pair and a real government portal URL -- neither claims to call an actual API.
- Flips `HR Country Settings("Saudi Arabia").compliance_engine_enabled` to 1.
- `v0_0` also backfills `Saudi Employee Profile` for any employee already at a company whose `GCC HR Company Settings.country` was Saudi Arabia before that patch existed; `v0_2` likewise backfills a `Saudization Profile` per such company.

`gcc_hr/patches/v0_4/setup_qatar.py` (Phase 6) is Qatar's own first patch, running `countries/qatar/setup.py:setup()` and backfilling both `Qatar Employee Profile` and `Qatarization Profile` for companies already on Qatar -- combining what were three separate Saudi patches into one, since Qatar's whole localization/payroll/workforce package ships in a single phase. It seeds:
- 10 `HR Document Type` rows (QID, Passport, Work Permit, Employment Contract, National ID, Health Certificate, Professional License, Driving License, Visa, Other).
- 7 `HR Compliance Rule` rows: QID/work-permit/passport expiry, non-Qatari-QID-on-file, contract active, contract-vs-payroll salary match, WPS registered.
- 1 `Gratuity Rule` row for Qatar EOSB: a single standard/full-service rate (21/30 of basic wage per year), explicitly not modelling any resignation-specific reduction -- see ARCHITECTURE.md's "Qatar (Phase 6)" section.
- 1 global-fallback `Qatarization Requirement` row: blank company/activity/business_size, 15% target, effective 2024-01-01, labelled illustrative (even more explicitly than Saudization's, since Qatar has no Nitaqat-equivalent public quota system).
- 2 `Government Submission Type` rows: `QAT_QATARIZATION_REPORT` and `QAT_WPS_REPORT`.
- Flips `HR Country Settings("Qatar").compliance_engine_enabled` to 1.

`gcc_hr/patches/v0_5/setup_uae.py` (Phase 7) is UAE's own first patch, running `countries/united_arab_emirates/setup.py:setup()` and backfilling both `UAE Employee Profile` and `Emiratisation Profile` for companies already on UAE -- same shape as v0_4. It seeds:
- 10 `HR Document Type` rows (EID, Passport, Work Permit, Employment Contract, National ID, Health Certificate, Professional License, Driving License, Visa, Other).
- 7 `HR Compliance Rule` rows: EID/work-permit/passport expiry, non-Emirati-EID-on-file, contract active, contract-vs-payroll salary match, WPS registered.
- **No new `Gratuity Rule` rows of its own** -- calls `hrms.regional.united_arab_emirates.setup.setup()` to create hrms's own 3 UAE EOSB rules ("Rule Under Limited Contract (UAE)", "...on termination (UAE)", "...on resignation (UAE)"), then fixes up two field bugs on those rows (see "Standard doctypes extended, not duplicated" above and ARCHITECTURE.md's "UAE (Phase 7)" section).
- 1 global-fallback `Emiratisation Requirement` row: blank company/activity/business_size, 10% target, effective 2024-01-01, labelled illustrative.
- 2 `Government Submission Type` rows: `UAE_EMIRATISATION_REPORT` and `UAE_WPS_REPORT`.
- Flips `HR Country Settings("United Arab Emirates").compliance_engine_enabled` to 1.

`gcc_hr/patches/v0_6/setup_oman.py` (Phase 8) is Oman's own first patch, running `countries/oman/setup.py:setup()` and backfilling both `Oman Employee Profile` and `Omanisation Profile` for companies already on Oman -- same shape as v0_4/v0_5. It seeds:
- 10 `HR Document Type` rows (Resident Card, Passport, Work Permit, Employment Contract, National ID, Health Certificate, Professional License, Driving License, Visa, Other).
- 7 `HR Compliance Rule` rows: resident-card/work-permit/passport expiry, non-Omani-resident-card-on-file, contract active, contract-vs-payroll salary match, PASI registered.
- 1 `Gratuity Rule` row for Oman EOSB: 15 days' wage per year for the first 3 years, 1 month's wage per year after -- hand-rolled, since hrms ships no Oman regional package to reuse (unlike UAE's).
- 1 global-fallback `Omanisation Requirement` row: blank company/activity/business_size, 15% target, effective 2024-01-01, labelled illustrative.
- 2 `Government Submission Type` rows: `OM_OMANISATION_REPORT` and `OM_PASI_REGISTRATION`.
- Flips `HR Country Settings("Oman").compliance_engine_enabled` to 1.

`gcc_hr/patches/v0_7/setup_bahrain.py` (Phase 9) is Bahrain's own first patch, running `countries/bahrain/setup.py:setup()` and backfilling both `Bahrain Employee Profile` and `Bahrainisation Profile` for companies already on Bahrain -- same shape as v0_4 through v0_6. It seeds:
- 10 `HR Document Type` rows (CPR, Passport, Work Permit, Employment Contract, National ID, Health Certificate, Professional License, Driving License, Visa, Other).
- 7 `HR Compliance Rule` rows: CPR/work-permit/passport expiry, non-Bahraini-CPR-on-file, contract active, contract-vs-payroll salary match, SIO registered.
- 1 `Gratuity Rule` row for Bahrain EOSB: half a month's wage per year for the first 3 years, 1 month's wage per year after -- hand-rolled, since hrms ships no Bahrain regional package to reuse. Numerically identical slabs to Oman's rule (independent laws, coincidentally the same thresholds).
- 1 global-fallback `Bahrainisation Requirement` row: blank company/activity/business_size, 20% target, effective 2024-01-01, labelled illustrative.
- 2 `Government Submission Type` rows: `BAH_BAHRAINISATION_REPORT` and `BAH_SIO_REGISTRATION`.
- Flips `HR Country Settings("Bahrain").compliance_engine_enabled` to 1.

`gcc_hr/patches/v0_8/setup_kuwait.py` (Phase 10) is Kuwait's own first patch, running `countries/kuwait/setup.py:setup()` and backfilling both `Kuwait Employee Profile` and `Kuwaitisation Profile` for companies already on Kuwait -- same shape as v0_4 through v0_7. It seeds:
- 10 `HR Document Type` rows (Civil ID, Passport, Work Permit, Employment Contract, National ID, Health Certificate, Professional License, Driving License, Visa, Other).
- 7 `HR Compliance Rule` rows: Civil-ID/work-permit/passport expiry, non-Kuwaiti-Civil-ID-on-file, contract active, contract-vs-payroll salary match, WPS registered.
- **4 `Gratuity Rule` rows for Kuwait EOSB**, not 1 -- mirrors Saudi's multi-slab, resignation-reduction shape (full award + three resignation bands) rather than Qatar/Oman/Bahrain's single-rule shape, since Kuwait Labour Law No. 6/2010 uses the same day-fraction/resignation-band structure Saudi's does. Hand-rolled, since hrms ships no Kuwait regional package.
- 1 global-fallback `Kuwaitisation Requirement` row: blank company/activity/business_size, 20% target, effective 2024-01-01, labelled illustrative.
- 2 `Government Submission Type` rows: `KWT_KUWAITISATION_REPORT` and `KWT_WPS_REPORT`.
- Flips `HR Country Settings("Kuwait").compliance_engine_enabled` to 1.

`fixtures/*.json` (re-synced on every `bench migrate` across every site this app is installed on):
- `role.json` -- the 7 new custom roles (see PERMISSIONS.md).
- `custom_field.json` -- Contract's GCC fields (above).
- `notification.json` -- 6 `Notification` records (document expiry at 90/30/7 days, document expired, compliance score dropped to critical, contract expiring in 30 days).

## Indexes / performance

- `HR Country Settings.country` and `GCC HR Company Settings.company` are `unique=1` (indexed by Frappe automatically).
- `HR Compliance Rule.rule_code` is `unique=1`.
- The daily scheduler jobs (`run_daily_expiry_sweep`, `run_daily_compliance_sweep`, `run_daily_workforce_nationalization_recalculation`) use `frappe.get_all(...)` with explicit `fields`/`filters` (never `SELECT *`), and only re-save documents whose computed status actually changed -- see ARCHITECTURE.md's "compliance engine" section.
