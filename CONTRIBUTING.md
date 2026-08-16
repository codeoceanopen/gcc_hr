# Contributing to GCC HR Compliance

## Development workflow

This app is built in numbered phases (see the brief and CHANGELOG.md):

1. **Core** (Phase 1, shipped) -- country-agnostic foundation: country/company settings, employee compliance profiles, document expiry tracking, the compliance rule engine and scoring, audit logging, the Vue Command Center.
2. **Saudi localization** (Phase 2, shipped) -- Saudi employee identity fields (`Saudi Employee Profile`), Iqama/work permit document types, Saudi compliance rules.
3. **Saudi payroll** (Phase 3, shipped) -- GOSI (`GOSI Settings`/`GOSI Employee Profile`/`GOSI Payroll Calculation`), contract-vs-payroll validation, payroll compliance checks (`Payroll Compliance Check`), EOSB (via seeded `Gratuity Rule`s).
4. **Saudization** (Phase 4, shipped) -- workforce-nationalization tracking (`Saudization Requirement`/`Saudization Profile`), risk engine, what-if simulator.
5. **Government integration** (Phase 5, shipped) -- generate/validate a submission document from data this app already tracks, then track a human's manual filing on the real government portal end to end (`Government Submission Type`/`Government Submission`); no fabricated API calls, per the brief's "Important Government Integration Rule."
6. **Qatar** (Phase 6, shipped) -- second country: identity/documents/rules (`Qatar Employee Profile`, QID-based), Qatarization workforce tracking (`Qatarization Requirement`/`Qatarization Profile`, mirrors Phase 4's shape), EOSB, and two Government Submission Types (Qatarization report, WPS registration worksheet) -- all added without touching Saudi's code, per `gcc_hr/countries/base.py`'s contract.
7. **UAE** (Phase 7, shipped) -- third country: identity/documents/rules (`UAE Employee Profile`, EID-based), Emiratisation workforce tracking (`Emiratisation Requirement`/`Emiratisation Profile`), and two Government Submission Types. EOSB reuses `hrms.regional.united_arab_emirates.setup.setup()` directly rather than seeding a competing `Gratuity Rule` -- the first country where Frappe HR itself already ships usable regional content; see ARCHITECTURE.md's "UAE (Phase 7)" section.
8. **Oman** (Phase 8, shipped) -- fourth country: identity/documents/rules (`Oman Employee Profile`, Resident-Card-based), Omanisation workforce tracking (`Omanisation Requirement`/`Omanisation Profile`), and two Government Submission Types. EOSB is hand-rolled (like Saudi's/Qatar's), since Frappe HR ships no Oman regional package to reuse.
9. **Bahrain** (Phase 9, shipped) -- fifth country: identity/documents/rules (`Bahrain Employee Profile`, CPR-based), Bahrainisation workforce tracking, two Government Submission Types, hand-rolled EOSB. Also tracks `sio_registered` (Bahrain's Social Insurance Organisation unemployment scheme genuinely covers expatriates too, unlike Saudi's GOSI, though this app still only models it as a registration flag, not a contribution calculator) alongside `wps_registered`.
10. **Kuwait** (Phase 10, shipped) -- sixth and last GCC country: identity/documents/rules (`Kuwait Employee Profile`, Civil-ID-based), Kuwaitisation workforce tracking, two Government Submission Types. EOSB mirrors Saudi's multi-slab, resignation-reduction shape (Kuwait Labour Law No. 6/2010 uses the same day-fraction structure as Saudi's), unlike Qatar's/Oman's/Bahrain's single-rule EOSB.

All six GCC countries this app targets are now implemented. Any further country work (not currently planned) would follow the exact same `countries/<slug>/` + top-level `<slug>/` module contract documented in `countries/base.py`.

Before starting a phase: read ARCHITECTURE.md's "country plugin architecture" and "why reuse instead of duplicate" sections first. A new doctype is the *last* resort, not the first -- check whether a standard ERPNext/HRMS doctype (or a Custom Field on one) already covers it.

## Setup

```bash
cd apps/gcc_hr
pre-commit install         # ruff, eslint, prettier, pyupgrade
cd frontend && yarn install
```

## Backend changes

- New doctype JSON: hand-write it under `gcc_hr_core/doctype/<name>/`, or for a country-specific doctype, under a top-level module folder named for that country (e.g. `saudi_arabia/doctype/<name>/` -- note this is a *sibling* of `countries/saudi_arabia/`, not nested under it; see ARCHITECTURE.md's "Why two `saudi_arabia` folders" for why Frappe's module-folder resolution requires the split). Run `bench --site $SITE migrate` to sync.
- Add a `test_<doctype>.py` next to it using `frappe.tests.utils.FrappeTestCase`.
- Register any new `scheduler_events`/`doc_events` in `hooks.py`, with a one-line comment on *why* (mirroring the style already there).

## Frontend changes

- Pages live under `frontend/src/pages/<module>/`. Prefer `createListResource`/`createDocumentResource`/`call()` (frappe-ui) talking directly to `frappe.client.*` over writing a new custom endpoint -- only add one under `gcc_hr/api/` when a page genuinely needs a join/aggregation plain CRUD can't express (see `api/dashboard.py` and `api/compliance.py` for the only two Phase 1 examples, and ARCHITECTURE.md for why).
- Add the page to both `router/index.ts` and `router/nav.ts` (`nav.ts` is the single source of truth for the sidebar).
- `yarn build` regenerates `gcc_hr/www/gcc_hr.html` and `gcc_hr/public/frontend/` automatically (via the `frappe-ui/vite` plugin) -- don't hand-edit either.

## Running tests

```bash
bench --site $SITE set-config allow_tests true   # once
bench --site $SITE run-tests --app gcc_hr
```

If your bench already has non-test setup data (a real Company, in particular), `bench run-tests --app gcc_hr` may crash inside `erpnext.tests.utils`'s legacy test-record preloader with a `DuplicateEntryError` on `Price List "Standard Buying"` -- this is a pre-existing ERPNext test-harness quirk unrelated to `gcc_hr` (its `BootStrapTestData` runs unconditionally at import time and collides with data that already exists from normal site setup). Work around it by running the suite directly instead, **wrapped in a savepoint with `_disable_transaction_control` set** -- without both, test data gets permanently committed to the database (bitten by this twice during this app's own development; see CHANGELOG.md):

```python
# inside `bench --site $SITE console`
import unittest, importlib, frappe

TEST_MODULES = [
    "gcc_hr.gcc_hr_core.compliance_engine.test_engine",
    "gcc_hr.gcc_hr_core.doctype.hr_country_settings.test_hr_country_settings",
    "gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.test_gcc_hr_company_settings",
    "gcc_hr.gcc_hr_core.doctype.hr_compliance_document.test_hr_compliance_document",
    "gcc_hr.gcc_hr_core.doctype.hr_audit_log.test_hr_audit_log",
    "gcc_hr.overrides.test_contract",
    "gcc_hr.api.test_dashboard",
    "gcc_hr.saudi_arabia.doctype.saudi_employee_profile.test_saudi_employee_profile",
    "gcc_hr.countries.saudi_arabia.test_rules",
    "gcc_hr.saudi_arabia.doctype.gosi_settings.test_gosi_settings",
    "gcc_hr.countries.saudi_arabia.test_gosi",
    "gcc_hr.gcc_hr_core.test_payroll",
    "gcc_hr.countries.saudi_arabia.test_saudization",
    "gcc_hr.api.test_saudization",
    "gcc_hr.gcc_hr_core.test_government",
    "gcc_hr.countries.saudi_arabia.test_government",
    "gcc_hr.api.test_government",
    "gcc_hr.gcc_hr_core.test_workforce",
    "gcc_hr.qatar.doctype.qatar_employee_profile.test_qatar_employee_profile",
    "gcc_hr.countries.qatar.test_rules",
    "gcc_hr.countries.qatar.test_qatarization",
    "gcc_hr.countries.qatar.test_government",
    "gcc_hr.api.test_qatarization",
    "gcc_hr.united_arab_emirates.doctype.uae_employee_profile.test_uae_employee_profile",
    "gcc_hr.countries.united_arab_emirates.test_setup",
    "gcc_hr.countries.united_arab_emirates.test_rules",
    "gcc_hr.countries.united_arab_emirates.test_emiratisation",
    "gcc_hr.countries.united_arab_emirates.test_government",
    "gcc_hr.api.test_emiratisation",
    "gcc_hr.oman.doctype.oman_employee_profile.test_oman_employee_profile",
    "gcc_hr.countries.oman.test_rules",
    "gcc_hr.countries.oman.test_omanisation",
    "gcc_hr.countries.oman.test_government",
    "gcc_hr.api.test_omanisation",
    "gcc_hr.bahrain.doctype.bahrain_employee_profile.test_bahrain_employee_profile",
    "gcc_hr.countries.bahrain.test_rules",
    "gcc_hr.countries.bahrain.test_bahrainisation",
    "gcc_hr.countries.bahrain.test_government",
    "gcc_hr.api.test_bahrainisation",
    "gcc_hr.kuwait.doctype.kuwait_employee_profile.test_kuwait_employee_profile",
    "gcc_hr.countries.kuwait.test_rules",
    "gcc_hr.countries.kuwait.test_kuwaitisation",
    "gcc_hr.countries.kuwait.test_government",
    "gcc_hr.countries.kuwait.test_setup",
    "gcc_hr.api.test_kuwaitisation",
]
loader, suite = unittest.TestLoader(), unittest.TestSuite()
for m in TEST_MODULES:
    suite.addTests(loader.loadTestsFromModule(importlib.import_module(m)))

frappe.db.savepoint("gcc_hr_test_run")
frappe.db._disable_transaction_control = 1  # neuter any commit() the code under test calls --
# Never committing means Frappe's own runaway-write safety valve
# (default 200_000 writes/transaction) accumulates across the *whole*
# suite instead of resetting per test, and trips once the suite gets
# large enough (first hit at 133 tests, Phase 7) -- raise it here.
frappe.db.MAX_WRITES_PER_TRANSACTION = 5_000_000
try:                                        # a real commit releases the savepoint, breaking the rollback
    unittest.TextTestRunner(verbosity=2).run(suite)
finally:
    frappe.db._disable_transaction_control = 0
    frappe.db.rollback(save_point="gcc_hr_test_run")
```

## Pull requests

- Regression-test that standard ERPNext/HRMS screens (Employee, Contract, Payroll Entry, Salary Slip) still work -- this app must never modify their behavior for users who haven't touched `gcc_hr`.
- Update CHANGELOG.md.
