# GCC HR Compliance -- Architecture

GCC HR Compliance is a Frappe app (`apps/gcc_hr`) whose primary UI is a
dedicated Vue 3 SPA (`apps/gcc_hr/frontend`), the same shape as this bench's
other custom app, `qcore`. Frappe/ERPNext/Frappe HR provide auth, the
database/ORM, background jobs, realtime, payroll, and the doctypes this app
extends; GCC HR Compliance adds the country-plugin architecture, the
compliance engine, and the business doctypes on top -- without modifying any
ERPNext/Frappe HR core file.

## Why a separate app, and why reuse instead of duplicate

The brief this app implements is explicit: "Don't build another HR system.
Build the compliance and localization layer that makes Frappe HR
production-ready for GCC businesses." Concretely that means:

- `gcc_hr` never edits a file under `apps/frappe`, `apps/erpnext` or
  `apps/hrms`. Every extension point is a hook (`doc_events`,
  `scheduler_events`, `override_doctype_dashboards`), a Custom Field/Property
  Setter (fixtures), or a new doctype of our own.
- Where a standard doctype already models what the brief asks for, GCC HR
  Compliance extends it instead of building a parallel one:
  - **Contract** (`erpnext.crm`, generic `party_type` incl. "Employee",
    submittable, fulfilment checklist, amendment chain) gets GCC salary
    breakdown fields (`gcc_basic_salary`, `gcc_housing_allowance`,
    `gcc_transport_allowance`, `gcc_other_allowances`, `gcc_total_salary`,
    `gcc_probation_period`, `gcc_notice_period`, `gcc_working_hours`,
    `gcc_annual_leave_days`) via `fixtures/custom_field.json`, and a
    `doc_events["Contract"]["validate"]` hook
    (`gcc_hr.overrides.contract.compute_total_salary`) that sums the
    allowances -- instead of a parallel "GCC Employment Contract" doctype.
  - **Gratuity** / **Gratuity Rule** / **Gratuity Rule Slab**
    (`hrms.payroll`, a configurable, slab-based, submittable EOSB engine
    that already posts through Salary Slip) is the EOSB engine. Saudi's
    EOSB rules (Phase 3) will be seeded as `Gratuity Rule` records by
    `countries/saudi_arabia/setup.py`, the same way
    `hrms/regional/united_arab_emirates/setup.py` seeds UAE's -- not a new
    "EOSB Calculation" doctype.
  - Standard `Employee`, `Salary Slip`, `Payroll Entry`, `Attendance`,
    `Leave Application`/`Leave Allocation`/`Holiday List` are read from and
    linked to, never forked. `Employee` itself gets zero new fields --
    Saudi-specific identity (Iqama, GOSI no., sponsor, ...) lives on a
    dedicated linked doctype (Phase 2), per the brief's own instruction not
    to "pollute the standard Employee DocType."

## Repository layout

```
gcc_hr/
  gcc_hr/
    hooks.py, modules.txt              modules.txt: "GCC HR Core" (Phase 1)
    gcc_hr_core/                       Frappe module "GCC HR Core"
      doctype/
        hr_country_settings/           one row per GCC country, master data
        gcc_hr_company_settings/       one row per Company, activates a country
        employee_compliance_profile/   one row per Employee, auto-created
        hr_document_type/              configurable document-type catalog
        hr_compliance_document/        tracked documents (Iqama, passport, ...)
        hr_document_expiry_threshold/  configurable expiry thresholds
        hr_compliance_rule/            configurable compliance rules
        hr_compliance_check/           compliance engine run history
        hr_compliance_check_result/    child table of hr_compliance_check
        hr_compliance_score_band/      configurable score -> status bands
        hr_audit_log/                  append-only audit trail
        government_submission_type/    configurable generate/validate dotted-path config,
                                       one row per submission kind (Phase 5)
        government_submission/         one row per filing, tracks the manual-submission
                                       state machine end to end (Phase 5)
      compliance_engine/
        engine.py                      rule evaluation, scoring, HR Compliance Check creation
        expiry_engine.py               document-expiry status + daily sweep
        scoring.py                     score calculation + score-band lookup
      payroll.py                       Salary Slip/Payroll Entry hooks (Phase 3) -- generic
                                       country dispatch + Payroll Compliance Check creation
      workforce.py                    daily workforce-nationalization recalculation dispatch
                                       (Phase 4) -- generic get_country_attr() shape as
                                       payroll.py, looks up a submodule literally named
                                       `workforce_nationalization` (renamed in Phase 6 --
                                       see "Qatar (Phase 6)" for why it used to say
                                       "saudization")
      government.py                   Government Submission state machine (Phase 5) --
                                       generate/validate/mark_ready/record_manual_submission/
                                       upload_response/complete, see "Government Integration"
      doctype/payroll_compliance_check/, payroll_compliance_check_employee/  (Phase 3)
      audit.py                         log_action() / log_doc_change() helpers
    countries/                         country plugin packages (business logic only,
                                       no doctypes -- see "Why two saudi_arabia folders")
      __init__.py                      get_country_module()/get_country_attr() dispatcher
      base.py                          documents the per-country contract (no runtime import)
      saudi_arabia/                    setup.py, employee.py, rules.py, payroll.py, gosi.py
                                       (Phase 3), saudization.py (Phase 4),
                                       government.py (Phase 5),
                                       workforce_nationalization.py (Phase 6, thin re-export
                                       of saudization.py -- see "Qatar (Phase 6)"), test_*.py
      qatar/                          setup.py, employee.py, rules.py, qatarization.py,
                                       government.py, workforce_nationalization.py (thin
                                       re-export of qatarization.py), test_*.py (Phase 6)
      united_arab_emirates/          setup.py (reuses hrms's own regional Gratuity Rules --
                                       see "UAE (Phase 7)"), employee.py, rules.py,
                                       emiratisation.py, government.py,
                                       workforce_nationalization.py (thin re-export of
                                       emiratisation.py), test_*.py (Phase 7)
      oman/                           setup.py, employee.py, rules.py, omanisation.py,
                                       government.py, workforce_nationalization.py (thin
                                       re-export of omanisation.py), test_*.py (Phase 8) --
                                       hand-rolled EOSB, like Saudi/Qatar (hrms has no Oman
                                       regional package to reuse)
      bahrain/                        setup.py, employee.py, rules.py, bahrainisation.py,
                                       government.py, workforce_nationalization.py (thin
                                       re-export of bahrainisation.py), test_*.py (Phase 9) --
                                       hand-rolled EOSB, like Saudi/Qatar/Oman
      kuwait/                         setup.py, employee.py, rules.py, kuwaitisation.py,
                                       government.py, workforce_nationalization.py (thin
                                       re-export of kuwaitisation.py), test_*.py (Phase 10) --
                                       hand-rolled EOSB, but mirrors Saudi's multi-slab
                                       resignation-reduction shape rather than Qatar/Oman/
                                       Bahrain's single-rule shape (see "Kuwait (Phase 10)")
    saudi_arabia/                      Frappe module "Saudi Arabia" (Phase 2-4) -- doctypes only
      doctype/
        saudi_employee_profile/         Iqama/work-permit/sponsor/GOSI-no./Qiwa-status (Phase 2)
        gosi_settings/                  effective-dated contribution rates (Phase 3)
        gosi_employee_profile/          registration status/number per Employee (Phase 3)
        gosi_payroll_calculation/       one immutable row per Salary Slip (Phase 3)
        saudization_requirement/        effective-dated target % by company/activity/size (Phase 4)
        saudization_profile/            one row per company, recalculated daily (Phase 4)
    qatar/                             Frappe module "Qatar" (Phase 6) -- doctypes only,
                                       mirrors the "Saudi Arabia" module's shape
      doctype/
        qatar_employee_profile/         QID/work-permit/sponsor/WPS profile
        qatarization_requirement/       effective-dated target % by company/activity/size
        qatarization_profile/           one row per company, recalculated daily
    united_arab_emirates/              Frappe module "United Arab Emirates" (Phase 7) --
                                       doctypes only, mirrors the "Qatar" module's shape
      doctype/
        uae_employee_profile/           EID/work-permit/sponsor/WPS profile
        emiratisation_requirement/      effective-dated target % by company/activity/size
        emiratisation_profile/          one row per company, recalculated daily
    oman/                               Frappe module "Oman" (Phase 8) -- doctypes only,
                                       mirrors the "Qatar"/"United Arab Emirates" modules' shape
      doctype/
        oman_employee_profile/          Resident Card/work-permit/sponsor/PASI+WPS profile
        omanisation_requirement/        effective-dated target % by company/activity/size
        omanisation_profile/            one row per company, recalculated daily
    bahrain/                            Frappe module "Bahrain" (Phase 9) -- doctypes only,
                                       mirrors the "Oman" module's shape
      doctype/
        bahrain_employee_profile/       CPR/work-permit/sponsor/SIO+WPS profile
        bahrainisation_requirement/     effective-dated target % by company/activity/size
        bahrainisation_profile/         one row per company, recalculated daily
    kuwait/                             Frappe module "Kuwait" (Phase 10) -- doctypes only,
                                       mirrors the "Oman"/"Bahrain" modules' shape
      doctype/
        kuwait_employee_profile/        Civil ID/work-permit/sponsor/WPS profile
        kuwaitisation_requirement/      effective-dated target % by company/activity/size
        kuwaitisation_profile/          one row per company, recalculated daily
    overrides/
      contract.py                     Contract.validate hook (total salary)
      dashboard.py                    Employee dashboard "Connections" entry
      test_contract.py
    api/
      dashboard.py                    Command Center summary (the one aggregation endpoint)
      compliance.py                   run_compliance_check_for_employee (backs the [Run
                                       Compliance Check] button; everything else on the
                                       SPA's pages is plain frappe.client.* CRUD)
      saudization.py                  recalculate_now() + simulate() (Phase 4) -- the What-If
                                       Simulator's projection can't be expressed as plain CRUD
      government.py                   thin, permission-checked wrappers around
                                       gcc_hr_core/government.py's state machine (Phase 5) --
                                       needed because that module uses db_set, which bypasses
                                       the normal permission pipeline
      qatarization.py                 recalculate_now() + simulate() (Phase 6) -- identical
                                       shape to saudization.py, one per country rather than
                                       one generic endpoint (see "Qatar (Phase 6)")
      emiratisation.py                recalculate_now() + simulate() (Phase 7) -- identical
                                       shape to qatarization.py/saudization.py
      omanisation.py                  recalculate_now() + simulate() (Phase 8) -- identical
                                       shape to the other three
      bahrainisation.py               recalculate_now() + simulate() (Phase 9) -- identical shape
      kuwaitisation.py                recalculate_now() + simulate() (Phase 10) -- identical shape
    install.py                        after_install: seeds HR Country Settings (6 countries),
                                       default expiry thresholds, default score bands
    patches/
      v0_0/setup_saudi_arabia.py       runs countries/saudi_arabia/setup.py + backfills
                                       Saudi Employee Profile for companies already
                                       pointed at Saudi Arabia before Phase 2 shipped
      v0_1/extend_saudi_arabia_payroll.py  re-runs setup.py (idempotent) to backfill Phase 3's
                                       new rules/Gratuity Rules/GOSI Settings for sites that
                                       already applied v0_0
      v0_2/extend_saudi_arabia_saudization.py  re-runs setup.py again for Phase 4's
                                       Saudization Requirement, and backfills a Saudization
                                       Profile per company already on Saudi Arabia
      v0_3/extend_saudi_arabia_government.py  re-runs setup.py again for Phase 5's two
                                       seeded Government Submission Type rows
      v0_4/setup_qatar.py             Qatar's own first patch (Phase 6) -- combines what were
                                       three separate Saudi patches (localization/payroll/
                                       workforce) into one, since Qatar ships all of it at once
      v0_5/setup_uae.py               UAE's own first patch (Phase 7), same shape as v0_4
      v0_6/setup_oman.py              Oman's own first patch (Phase 8), same shape as v0_4
      v0_7/setup_bahrain.py           Bahrain's own first patch (Phase 9), same shape as v0_4
      v0_8/setup_kuwait.py            Kuwait's own first patch (Phase 10), same shape as v0_4
    fixtures/
      role.json                       7 new custom roles (see PERMISSIONS.md)
      custom_field.json               Contract's GCC salary/contract-term fields
      notification.json               Document/contract expiry + compliance-score alerts
    www/
      gcc_hr.py, gcc_hr.html          SPA entrypoint (auth-gated, boots the Vue app)

frontend/
  src/
    components/
      layout/                        AppShell, Sidebar
      ui/                            PageHeader, StatusBadge
      employees/                     SaudiProfileCard (shown on Employee Detail when
                                     the employee's company country is Saudi Arabia),
                                     QatarProfileCard (same, for Qatar, Phase 6),
                                     UAEProfileCard (same, for UAE, Phase 7),
                                     OmanProfileCard (same, for Oman, Phase 8),
                                     BahrainProfileCard (same, for Bahrain, Phase 9),
                                     KuwaitProfileCard (same, for Kuwait, Phase 10)
    pages/
      Dashboard.vue                  Command Center (calls api/dashboard.py)
      employees/                     EmployeeList, EmployeeDetail
      documents/                     DocumentList
      compliance/                    RuleList, CheckList
      settings/                      CountrySettings, CompanySettings
      contracts/                     ContractList (Phase 3)
      payroll/                       PayrollComplianceList, PayrollComplianceDetail (Phase 3)
      saudi/                         GOSI.vue (Phase 3), Saudization.vue (Phase 4)
      government/                    SubmissionList.vue, SubmissionDetail.vue (Phase 5) --
                                     country-agnostic; every other country's submission types
                                     (Phase 6-10) show up here with zero new frontend code
      qatar/                         Qatarization.vue (Phase 6)
      uae/                           Emiratisation.vue (Phase 7)
      oman/                          Omanisation.vue (Phase 8)
      bahrain/                       Bahrainisation.vue (Phase 9)
      kuwait/                        Kuwaitisation.vue (Phase 10)
    router/                          nav.ts (single source of nav items + CURRENT_PHASE), index.ts
    stores/                          session (Pinia)
    utils/                           format.ts (status -> badge tone mappings)
    types/                           frappe-ui.d.ts (ambient types -- see "Frontend" below)
```

Qatar (Phase 6) proved the pattern: its whole package -- `countries/qatar/`
(business logic) plus a sibling `qatar/` module (doctypes only) -- was added
without editing a single line of Saudi's business logic. UAE (Phase 7)
proved it a second time, and additionally proved the pattern can *reuse*
another app's regional setup when one already exists (see "UAE (Phase 7)"
below). Oman (Phase 8) and Bahrain (Phase 9) proved it a third and fourth
time, back to hand-rolled EOSB (hrms has no Oman or Bahrain regional
package). Kuwait (Phase 10) -- the sixth and last GCC country this app
targets -- proved the pattern once more, and additionally proved a
country's `setup.py` can mirror a *different* country's internal shape
(Saudi's multi-slab EOSB, not Oman's/Qatar's single-rule shape) without any
change to either country's actual code. `countries/base.py` documents the
exact per-country contract.

## Country plugin architecture

Nothing in `gcc_hr_core` (or any other country package) ever imports a
specific country's package directly. `gcc_hr/countries/__init__.py` provides
the dispatcher:

```python
def get_country_module(country: str, submodule: str):
    try:
        return frappe.get_module(f"gcc_hr.countries.{frappe.scrub(country)}.{submodule}")
    except ImportError:
        return None   # country not yet implemented -- core still works
```

This mirrors HRMS's own (narrower) mechanism --
`hrms/overrides/company.py:run_regional_setup()` dynamically imports
`hrms.regional.<country>.setup.setup()` on `Company.on_update` when the
country changes (guarded by `frappe.flags.country_change`). GCC HR
Compliance's version is keyed off `GCC HR Company Settings.country` instead
(see `GCCHRCompanySettings.run_country_setup()`) and is used for the whole
country interface (rules, employee fields, payroll, GOSI, Saudization, ...),
not just tax-calculation hooks. `countries/saudi_arabia/setup.py` (added in
Phase 2) seeds Saudi's `HR Document Type`/`HR Compliance Rule` rows and
enables its compliance engine; for every other country the dispatch is
still a verified no-op (`test_gcc_hr_company_settings.py:test_country_change_dispatch_is_a_safe_noop_when_country_module_missing`
covers this against whichever country doesn't have a `setup.py` yet).
Phase 6 confirmed this: Qatar's whole package (`countries/qatar/setup.py`
and its other submodules) was added with zero changes to Saudi's business
logic. The one real change needed was inside `gcc_hr_core` itself, not
Saudi's code -- see "Qatar (Phase 6)" below for the one hardcoded name this
dispatch pattern had quietly picked up. Phase 7 (UAE) needed zero further
core changes -- the `workforce_nationalization` rename already generalized
the one thing that wasn't -- and additionally showed the dispatch pattern
composing with *another app's* regional mechanism: UAE's `setup()` calls
`hrms.regional.united_arab_emirates.setup.setup()` directly for EOSB rather
than hand-rolling a competing rule, see "UAE (Phase 7)" below. Phases 8-10
(Oman, Bahrain, Kuwait) likewise needed zero core changes each, all three
hand-rolling their own EOSB rule (hrms has no regional package for any of
them) -- confirming the dispatch pattern's genericity isn't a one-off, and
that reuse-vs-hand-roll is a per-country decision, not something the
framework needs to know about. All six GCC countries this app targets now
ship through the identical, unmodified dispatch mechanism first written for
Saudi Arabia alone in Phase 1.

### Why two `saudi_arabia` folders

`gcc_hr/countries/saudi_arabia/` (a plain Python package: `setup.py`,
`employee.py`, `rules.py`) and `gcc_hr/saudi_arabia/` (a Frappe *module*
folder: `doctype/saudi_employee_profile/`) are siblings, not nested -- this
looks redundant but isn't optional. Frappe resolves a module's doctype
folder as `<app>/<app>/<scrubbed_module_name>/`, always directly under the
app's own top-level package, never through an arbitrary subpackage. A
`modules.txt` entry of "Saudi Arabia" therefore *must* live at
`gcc_hr/gcc_hr/saudi_arabia/`, full stop -- putting the doctype under
`gcc_hr/gcc_hr/countries/saudi_arabia/doctype/` instead would make Frappe
try to import it as `gcc_hr.saudi_arabia.doctype....` anyway (module
resolution is by module name, not by whatever folder the JSON happens to
sit in) and fail. Non-doctype country logic has no such constraint -- it's
just importable Python -- so it stays under `countries/<slug>/` per the
brief's own requested layout. Every country's doctypes (Qatar's Phase 6
through Kuwait's Phase 10) needed the exact same split -- a bare top-level
module folder plus `countries/<slug>/` for business logic -- confirming
this isn't a Saudi-specific quirk but Frappe's actual module-resolution
rule. (Phase 6 hit `bench migrate` failing with `ModuleNotFoundError` from
forgetting to add the country to `modules.txt` before creating its first
doctype JSON; Phase 7 and Phase 8 both added the `modules.txt` entry up
front and still hit the identical error on the first migrate attempt each
time, resolved only by `bench clear-cache` -- Frappe's own module-list
resolution can apparently cache stale state mid-session. Phase 9/10 finally
found the preventive fix: run `bench clear-cache` *before* the first
migrate attempt after adding a new module, rather than reacting to the
failure after the fact -- and, sure enough, no `ModuleNotFoundError` that
time. See each phase's CHANGELOG.md "Bugs found" note.)

## The compliance engine

`HR Compliance Rule` rows are configuration: country, category, severity,
effective dates, enabled -- but the actual predicate ("is this Iqama
expiring") is still a Python callable, referenced by dotted path
(`check_method`), because that genuinely needs code. What's configurable is
*which* rules run, *when* (effective_from/effective_to), and *how severe* a
failure is -- never hard-coded in the engine itself. See
`gcc_hr_core/compliance_engine/engine.py`.

`run_compliance_check(employee)`:
1. Loads the employee's `Employee Compliance Profile` and its country.
2. Loads that country's enabled, currently-effective `HR Compliance Rule`s.
3. Calls each rule's `check_method(employee, profile, rule)` ->
   `(result, message, recommended_action)`.
4. Scores the run (`scoring.py`: 100 minus a severity-weighted deduction per
   failed rule) and maps the score to a status via `HR Compliance Score
   Band` (country-specific or global; falls back to the brief's own
   90-100/75-89/50-74/0-49 bands if none are configured yet).
5. Writes an `HR Compliance Check` (+ `HR Compliance Check Result` rows) --
   immutable history, no role has `write` on it -- and updates the
   `Employee Compliance Profile`'s score/status.
6. Logs the run to `HR Audit Log`.

`scheduler_events.daily` runs this for every employee whose company's
country has `compliance_engine_enabled`, and separately sweeps every `HR
Compliance Document` for expiry-status changes
(`expiry_engine.run_daily_expiry_sweep`) -- through the document's full
`save()` lifecycle, not a raw `db.set_value`, so the fixture `Notification`
records (Days Before / Value Change triggers) still fire.

## Payroll (Phase 3)

Two separate hooks, both extending standard Frappe HR payroll rather than
wrapping it:

- **`Salary Slip.on_submit`** -> `gcc_hr_core/payroll.py:sync_country_payroll()`,
  a generic dispatcher (same `get_country_attr()` mechanism as country
  setup) that calls `get_country_attr(country, "payroll",
  "on_salary_slip_submit")`. Saudi's implementation
  (`countries/saudi_arabia/payroll.py`) calls `gosi.py:calculate_for_salary_slip()`,
  which no-ops unless the employee has an *Active*, *Registered* `GOSI
  Employee Profile` -- then looks up the effective `GOSI Settings` row for
  their Saudi/Non-Saudi category on the slip's posting date, applies
  floor/ceiling capping, and writes one immutable `GOSI Payroll
  Calculation`.
- **`Payroll Entry.before_submit`** -> `gcc_hr_core/payroll.py:validate_payroll_compliance()`
  runs `run_compliance_check()` (the same engine from the section above, no
  parallel logic) for every employee in the run, records one `Payroll
  Compliance Check` with a per-employee breakdown, and -- only if `GCC HR
  Company Settings.payroll_compliance_required` is on and at least one
  employee has a Critical/Blocking issue -- blocks the submission with
  `frappe.throw`. The check is always written either way, so a company that
  turns the hard block off still gets a full audit trail of what would have
  blocked.

EOSB reuses HRMS's own `Gratuity`/`Gratuity Rule` slab engine outright --
`countries/saudi_arabia/setup.py` seeds 4 `Gratuity Rule` rows for KSA
Labour Law Art. 84 (full award vs. three resignation-tenure bands), the
same pattern `hrms/regional/united_arab_emirates/setup.py` uses for UAE's
equivalent. There is no `EOSB Calculation` doctype in this app; HR creates
a `Gratuity` record and picks the applicable rule, same workflow as any
other Frappe HR company.

## Saudization (Phase 4)

`Saudization Requirement` rows are matched by specificity, most specific
first -- exact company override, then Activity+Business Size, then a
global fallback (all three blank) -- exactly the same effective-dating
shape as `GOSI Settings`' lookup, just with one more specificity tier
(`saudization.py:get_applicable_target()`). No universal percentage is
ever assumed, per instruction; the seeded row is the global fallback only,
explicitly labelled illustrative.

`Saudization Profile` counts come from the *existing* `Saudi Employee
Profile.nationality_status` field (Phase 2) -- Saudization doesn't
introduce a second, competing source of nationality data. Only `Active`
employees count (`get_workforce_counts()`), matching how Nitaqat itself
only counts the current workforce.

The What-If Simulator (`saudization.py:simulate()`) is deliberately a pure
function: it reads the current counts, applies hire/terminate deltas
in-memory, and returns a projection -- it never calls `.save()` or
`.insert()` on anything. `test_saudization.py:test_simulate_does_not_touch_real_data`
asserts the real counts are byte-for-byte identical before and after a
simulation, which is the actual guarantee that matters here, not just "the
math is right."

**A discovered footgun, not specific to this feature but caught here**:
Frappe auto-fills any field literally named `company` with the current
user's default company whenever it's absent from an insert. For a doctype
like `Saudization Requirement` where "blank company" is a meaningful,
intentional state (global/activity-matched, not company-specific), this
silently breaks that state for anyone filling the Desk form by hand and
not noticing the pre-filled value -- so `saudization_requirement.js` clears
it on new documents, and the seeder passes `"company": ""` explicitly
rather than omitting the key.

**A testing lesson, general to this app, caught here**: `FrappeTestCase`
only rolls back once, at *class* teardown (`addClassCleanup(_rollback_db)`
in Frappe's own `deprecation_dumpster.py`) -- there is no per-test-method
savepoint/rollback, in `bench run-tests` or otherwise. `test_saudization.py`
originally shared one `TEST_COMPANY` across the whole `TestSaudization`
class; several test methods both created `Employee` rows in it *and*
asserted an exact `get_workforce_counts()`/`recalculate()` total, which only
passed by accident of alphabetical test-method ordering leaving that
company empty until each assertion ran. Fixed by giving every
count-asserting test its own company via a `_make_company()` helper --
the general rule for this codebase going forward: a test that creates
`Employee`/other shared-scope records *and* asserts an exact count must
isolate its scope (company, or a uniquely-named parent record), never lean
on execution order or an empty shared fixture.

## Government Integration (Phase 5)

The brief's "Important Government Integration Rule" is explicit: never
fabricate a government API. No GCC government currently exposes a verified,
public API for GOSI/Qiwa/Nitaqat/Muqeem-type submissions, so this framework
never pretends to call one. Instead it automates the part that doesn't
require one -- generating the submission document from data this app
already has, and validating it -- and tracks the part a human still does by
hand on the real portal: submit, then come back and record what happened.
That's the generate / validate / manual-submit / upload-response /
track-status shape README.md describes.

**Configuration, not code, decides what gets generated.** `Government
Submission Type` holds `generate_method`/`validate_method` as dotted Python
paths, resolved with `frappe.get_attr()` -- the exact same shape as `HR
Compliance Rule.check_method` (`compliance_engine/engine.py`). Adding a new
submission kind (a different country's registration form, a different
report) never touches `gcc_hr_core/government.py`; it's a new config row
plus a new generate/validate function in that country's package.

**The state machine is enforced in `gcc_hr_core/government.py`, not the
Desk form.** `Government Submission` moves through Draft -> Generated ->
Validated -> Ready for Submission -> Submitted -> Response Uploaded ->
Completed, and every transition function (`generate()`, `validate_submission()`,
`mark_ready()`, `record_manual_submission()`, `upload_response()`,
`complete()`) checks the current status before acting -- a submission can
never be marked Ready for Submission with unresolved validation errors, or
Submitted before anyone has actually validated it, because nothing (not
even a Desk user hand-editing the form) reaches those functions without
going through the ones before them. Like the rest of this app's engine-
written fields (`Saudization Profile`'s counts, `GOSI Payroll
Calculation`), transitions write via `db_set` rather than `save()`, so
`api/government.py` re-checks write permission itself before calling in --
the same reason `api/saudization.py` checks permission before calling
`recalculate()`.

**Both seeded Saudi submission types are grounded in data this app already
tracks, not a fabricated integration.** `SA_NITAQAT_REPORT`
(`countries/saudi_arabia/government.py:generate_nitaqat_report()`) turns the
existing `Saudization Profile` (Phase 4) into a CSV a human files at the
real Nitaqat portal; its validator refuses a submission built from a
Saudization Profile recalculated more than 30 days ago. `SA_GOSI_REGISTRATION`
turns `GOSI Employee Profile` (Phase 3) into a worksheet of who still needs
registering at gosi.gov.sa. Neither claims this app can
register anyone with GOSI or file a Nitaqat report itself -- see each
`Government Submission Type`'s own `portal_url`/`portal_instructions`
fields, always shown to the user before they can record a submission as
filed.

## Qatar (Phase 6)

The second country. Qatar's package mirrors Saudi's exactly in shape
(`Qatar Employee Profile`, `Qatarization Requirement`/`Qatarization
Profile`, `countries/qatar/{setup,employee,rules,qatarization,
government}.py`) but is grounded in what's actually distinct about Qatar,
not a copy-paste of Saudi's specifics:

- **QID** (Qatar ID) replaces Iqama as the residency-permit identity field.
- **Wage Protection System (WPS)** (Law No. 17 of 2020: salaries must be
  paid through a WPS-registered bank account) is Qatar's own real,
  verifiable compliance requirement -- there's no GOSI-equivalent expat
  social-insurance scheme to model for Qatar, so `Qatar Employee Profile`
  tracks `wps_registered` instead, and `countries/qatar/rules.py`'s
  `check_wps_registered` is Qatar's payroll-adjacent rule in place of
  Saudi's `check_gosi_registered`. Qatar therefore has no `payroll.py` --
  `gcc_hr_core/payroll.py`'s dispatch already no-ops safely for countries
  that don't implement one (verified by
  `test_country_change_dispatch_is_a_safe_noop_when_country_module_missing`).
- **EOSB**: Qatar Labour Law No. 14 of 2004, Art. 54 -- at least three
  weeks' basic wage per year of service, for one year or more of service.
  Modelled as a single `Gratuity Rule` slab (`21/30`), unlike Saudi's three
  resignation-tiered rules -- this app doesn't model any resignation-
  specific reduction for Qatar, since that nuance isn't confidently
  verified; the seeded rule's description says so explicitly, following
  the same "illustrative, verify before relying on it" pattern as GOSI's
  rates and Nitaqat's target.
- **Qatarization**: Qatar doesn't have as uniformly codified a public quota
  system as Nitaqat, so `Qatarization Requirement`'s seeded global fallback
  is even more explicitly a placeholder (see its own `description` field)
  than Saudization's was.
- **Government Integration needed zero new frontend or `api/government.py`
  code.** `QAT_QATARIZATION_REPORT` and `QAT_WPS_REPORT` just show up in the
  existing Government Submission list/detail pages the moment they're
  seeded -- `api/test_government.py`'s
  `test_end_to_end_via_api_wrappers_for_qatar_submission_type` runs the
  identical, Saudi-authored state machine against a Qatar submission type
  specifically to prove that.

**A real bug this phase's whole premise surfaced, not a Qatar-specific
one**: `gcc_hr_core/workforce.py`'s daily scheduler dispatch hardcoded the
literal string `"saudization"` as the submodule name to look up on every
country's package -- harmless while Saudi was the only country, but exactly
the kind of Saudi-specific leak into supposedly generic core code the
architecture claims not to have. Fixed by renaming the dispatcher's lookup
to a generic `workforce_nationalization`, and giving both `countries/
saudi_arabia/` and `countries/qatar/` a thin `workforce_nationalization.py`
that just re-exports their real (`saudization.py`/`qatarization.py`)
implementation's public functions -- Saudi's actual business logic never
changed, only how the dispatcher finds it. `gcc_hr_core/test_workforce.py`
recalculates every one of the six shipped countries in a single sweep to
guard against this regressing. See `countries/base.py` for the documented
contract.

**Rule-function duplication, deliberate, not an oversight**:
`check_passport_expiry`/`check_contract_active`/`check_contract_salary_match`
in `countries/qatar/rules.py` are byte-for-byte identical in logic to
Saudi's versions of the same checks -- genuinely country-agnostic, but
duplicated rather than shared. Sharing them would mean either Qatar's seeded
`HR Compliance Rule` rows pointing their `check_method` at a module named
`saudi_arabia` (confusing coupling), or extracting a new shared module and
migrating Saudi's already-seeded rows to point at it (a change to Saudi's
shipped data). Neither seemed worth it for two countries; UAE (Phase 7)
duplicated the exact same three functions a third time rather than
extracting them, on the stated basis that a fourth copy should trigger
extraction instead. Oman (Phase 8), Bahrain (Phase 9), and Kuwait (Phase
10) are that fourth, fifth, and sixth copy, and the honest update is: still
not extracted, all the way to the last country this app targets. Doing so
now would mean migrating five already-shipped countries'
`HR Compliance Rule.check_method` pointers to a new shared module -- exactly
the "change to already-shipped data" this note originally ruled out at
Qatar's turn, and there was no new information at any later country's turn
that made that tradeoff any better. The threshold in this note was
aspirational and never enforced, six copies in; if a hypothetical seventh
country ever gets added, extraction should happen *before* writing its
`rules.py`, not after.

## UAE (Phase 7)

The third country, and the first one where Frappe HR itself already ships
usable regional content. UAE's package mirrors Qatar's in shape (`UAE
Employee Profile`, `Emiratisation Requirement`/`Emiratisation Profile`,
`countries/united_arab_emirates/{setup,employee,rules,emiratisation,
government}.py`) but its EOSB handling is genuinely different:

- **EOSB reuses `hrms/regional/united_arab_emirates/setup.py` directly**,
  rather than hand-rolling a competing `Gratuity Rule` the way Saudi's and
  Qatar's `setup.py` had to. Frappe HR ships no Saudi or Qatar regional
  package, so those two countries had nothing to reuse; UAE does
  (`hrms.regional.united_arab_emirates.setup.setup()`), and it already
  models the current UAE Labour Law (Federal Decree-Law No. 33 of 2021,
  Art. 51) slabs *including* the resignation-reduction tiers this app
  deliberately didn't attempt to model for Qatar. Calling hrms's own
  function -- rather than copying its `Gratuity Rule` definitions into this
  app -- is reuse-over-duplicate in its most literal form: if hrms's own
  slabs ever change, this app picks up the change automatically.
  `create_gratuity_rules()` calls it directly rather than depending on
  hrms's own dispatch (`hrms/overrides/company.py`, gated behind
  `frappe.flags.country_change`) having already fired, since that only
  triggers when a Company's country *changes* on an existing document, not
  on insert -- the same fragility this app's own dispatch has, documented
  above.
- **hrms's own regional script has two known bugs, fixed up on the rows it
  creates, not by editing hrms's file.** It sets a stale/renamed field
  (`work_experience_calculation_method`; Frappe silently drops unknown
  field names, so it's never actually applied -- the correct current name
  is `work_experience_calculation_function`) and never sets the mandatory
  `applicable_earnings_component`, working only because it inserts with
  `ignore_mandatory=True`. Both bugs were already discovered once before,
  independently, while writing Saudi's own EOSB rules in Phase 3 -- but
  this time the buggy code is hrms's, which is out of scope to edit
  directly (never modify another app's files), so `create_gratuity_rules()`
  calls hrms's `setup()` first, then walks the three named rules it creates
  and corrects both fields if needed. Idempotent, covered by
  `countries/united_arab_emirates/test_setup.py`.
- **QID/WPS/Emiratisation** otherwise mirror Qatar's Phase 6 shape exactly:
  Emirates ID in place of Iqama/QID, `wps_registered` in place of a GOSI
  equivalent (UAE has none either), and an Emiratisation quota that -- like
  Qatarization -- is seeded as an explicitly illustrative placeholder, even
  though UAE's Cabinet Resolution-driven quota (private-sector companies
  with 50+ skilled employees, a defined annual increase target) is more
  concretely codified than Qatar's.
- **Government Integration needed zero new frontend or `api/government.py`
  code, a third time.** `api/test_government.py`'s
  `test_end_to_end_via_api_wrappers_for_uae_submission_type` runs the same
  unmodified state machine against `UAE_EMIRATISATION_REPORT`.

## Oman (Phase 8)

The fourth country, and back to hand-rolled EOSB -- hrms ships no Oman
regional package, so `create_gratuity_rules()` seeds its own `Gratuity
Rule` the same way Saudi's and Qatar's `setup.py` do, not the way UAE's
does. Oman's package mirrors the other three in shape (`Oman Employee
Profile`, `Omanisation Requirement`/`Omanisation Profile`,
`countries/oman/{setup,employee,rules,omanisation,government}.py`):

- **Resident Card** replaces Iqama/QID/EID as the residency-permit identity
  field -- Oman's actual name for the document.
- **PASI (Public Authority for Social Insurance) registration** is Oman's
  payroll-adjacent check in place of GOSI/WPS, tracked the same way WPS is
  for Qatar/UAE: an identity/tracking `Check` field (`pasi_registered`) on
  `Oman Employee Profile`, not a contribution calculator. Oman's social
  insurance for expatriate workers is a genuinely evolving area (a 2023
  reform extended coverage that had previously been Omani-nationals-only)
  and this app isn't confident enough in current contribution rates to
  model them the way Saudi's GOSI is modelled -- a registration flag is the
  honest level of automation here, the same caution Qatar's Phase 6 took
  for its own payroll-adjacent check. `Oman Employee Profile` also carries
  `wps_registered` (Oman has a WPS too) purely as a tracked data field, not
  a compliance rule of its own.
- **EOSB**: Oman Labour Law (Royal Decree 35/2003, as amended) -- 15 days'
  wage per year for each of the first three years, one month's wage per
  year after that. Modelled as a single two-slab `Gratuity Rule`, the same
  shape as Saudi's and Qatar's. No resignation-specific reduction is
  modelled, the same caution Qatar's EOSB rule took.
- **Omanisation** is, unusually among this app's four countries so far, one
  of the *most* established GCC nationalization schemes -- sector-specific
  Ministry of Labour quotas dating back decades, predating Emiratisation
  and Qatarization by a wide margin. `Omanisation Requirement`'s seeded row
  is still an explicitly illustrative placeholder (see that doctype's own
  `description` field): a real-world-established program doesn't make this
  app's placeholder default any less of a placeholder.
- **Government Integration needed zero new frontend or `api/government.py`
  code, a fourth time.** `api/test_government.py`'s
  `test_end_to_end_via_api_wrappers_for_oman_submission_type` runs the same
  unmodified state machine against `OM_OMANISATION_REPORT`.

## Bahrain (Phase 9)

The fifth country. Bahrain's package mirrors Oman's in shape (`Bahrain
Employee Profile`, `Bahrainisation Requirement`/`Bahrainisation Profile`,
`countries/bahrain/{setup,employee,rules,bahrainisation,government}.py`),
built by a background agent working in parallel with Kuwait's (Phase 10) --
the two share zero files, so no coordination beyond the shared-file wiring
(`hooks.py`, `modules.txt`, `patches.txt`, router/nav, the test runner list,
and this document) was needed:

- **CPR (Central Population Registry)** replaces Resident Card/EID/QID/Iqama
  as the residency-permit identity field -- Bahrain's actual name for the
  unified ID both citizens and residents carry.
- **SIO (Social Insurance Organisation) registration** is Bahrain's
  payroll-adjacent check, and genuinely the most consequential one among
  the four non-Saudi countries so far: Bahrain's unemployment insurance
  scheme (Law No. 78 of 2006) actually covers *all* private-sector
  employees, expatriates included -- unlike Saudi's GOSI, which for
  non-Saudis covers occupational hazards only. Despite that, it's still
  modelled the conservative way (an identity/tracking `Check` field,
  `sio_registered`, not a contribution calculator), for the same reason
  Oman's PASI isn't modelled with real rates either: this app isn't
  confident enough in current SIO contribution percentages to compute
  payroll math with them. `Bahrain Employee Profile` also carries
  `wps_registered` (Bahrain has WPS too) as a second tracked field.
- **EOSB**: Bahrain Labour Law (Law No. 36 of 2012), Art. 116 -- half a
  month's wage per year for the first three years, one month's wage per
  year after that. Modelled as a single two-slab `Gratuity Rule`, the same
  shape as Oman's -- the two laws are independent, but the real thresholds
  happen to produce numerically identical slabs (15 days for years 0-3,
  30 days per year after), which `countries/bahrain/setup.py`'s docstring
  calls out explicitly rather than leaving as an unexplained coincidence.
- **Government Integration needed zero new frontend or `api/government.py`
  code, a fifth time.** `api/test_government.py`'s
  `test_end_to_end_via_api_wrappers_for_bahrain_submission_type` runs the
  same unmodified state machine against `BAH_BAHRAINISATION_REPORT`.

## Kuwait (Phase 10)

The sixth and last GCC country this app targets. Kuwait's package mirrors
Oman's/Bahrain's shape for everything except EOSB, which instead mirrors
Saudi's -- built by a background agent working in parallel with Bahrain's
(Phase 9), the two sharing zero files:

- **Civil ID** replaces CPR/Resident Card/EID/QID/Iqama as the
  residency-permit identity field -- Kuwait's actual name for the unified
  ID both citizens and residents carry (same shape as Bahrain's CPR, a
  different real document).
- **WPS registration** is Kuwait's payroll-adjacent check, the same
  identity/tracking `Check` field shape as Qatar's/UAE's -- Kuwait's PIFSS
  pension scheme covers Kuwaiti nationals only, so (like Qatar and UAE)
  there's no GOSI-equivalent to model for expatriates and no `payroll.py`.
- **EOSB deliberately does *not* mirror Oman's/Bahrain's single-rule
  shape.** Kuwait Labour Law No. 6 of 2010, Art. 51 uses the same
  day-fraction structure Saudi's KSA Labour Law Art. 84 does -- 15 days'
  wage per year for the first five years, one month's wage per year after,
  with the same commonly-cited resignation-reduction bands (none under 2
  years, 1/3 from 2-5, 2/3 from 5-10, full at 10+). `countries/kuwait/
  setup.py`'s `GRATUITY_RULES` is a byte-for-byte structural copy of
  Saudi's own list (4 rows: full award + three resignation bands), renamed.
  This is the first time in this app's history that a later country's
  `setup.py` deliberately mirrors an *earlier* country's internal shape
  rather than the immediately-preceding country's -- confirming the
  per-country contract genuinely allows each country to pick whichever
  existing shape fits its real law, not just whatever the last country did.
- **Government Integration needed zero new frontend or `api/government.py`
  code, a sixth and final time.** `api/test_government.py`'s
  `test_end_to_end_via_api_wrappers_for_kuwait_submission_type` runs the
  same unmodified state machine against `KWT_KUWAITISATION_REPORT` -- the
  same state machine, written once for Saudi Arabia in Phase 5, now proven
  against all six countries this app ships.

## Frontend: why a separate SPA instead of Frappe Desk

Per instruction, all Phase 1 management (Country/Company Settings,
Employees, Documents, Compliance Rules/Checks) is done through the Vue SPA,
not Desk list/form views -- Desk remains available for admins who need it
(every doctype ships normal permissions), but it isn't the intended day-to-
day surface. Pages talk to `frappe.client.*` directly via frappe-ui's
`createListResource`/`createDocumentResource`/`call()` for plain CRUD;
`api/dashboard.py` and `api/compliance.py` are the *only* two custom
endpoints in Phase 1, because a dashboard's grouped counts/average and the
"run this now" action are the only things plain CRUD can't express.

## Security

- No government secrets exist yet in Phase 1 (nothing to store). When Phase
  5 introduces provider credentials, they go through Frappe's `Password`
  fieldtype (encrypted at rest), never fixtures, never Git.
- `HR Audit Log` has no `create`/`write`/`delete` permission for any role --
  it's written exclusively by `gcc_hr_core/audit.py:log_action()` via
  `insert(ignore_permissions=True)`, so it can't be edited after the fact.
- Multi-company data isolation relies on Frappe's own User Permission
  mechanism (any doctype with a `company`/`employee` Link field is
  automatically scoped for a user restricted to specific
  Companies/Employees) rather than a custom
  `permission_query_conditions` -- Frappe already solves this generically.
