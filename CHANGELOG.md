# Changelog

## Phase 9 -- Bahrain, and Phase 10 -- Kuwait (2026-08-14)

The fifth and sixth countries, shipped together: Bahrain and Kuwait are the last two GCC countries this app targets. Built by two background agents working in parallel on fully disjoint file sets (`gcc_hr/bahrain/`+`countries/bahrain/`+`frontend/.../bahrain/` vs. the same tree for `kuwait/`), with the orchestrating session handling every shared file (`hooks.py`, `modules.txt`, `patches.txt`, router/nav, the test runner list, and this document) afterward to avoid any write conflict -- the repo isn't git-tracked, so worktree isolation wasn't an option; disjoint-file-set parallelism was the safe substitute.

### Backend

- **Bahrain** (`gcc_hr/bahrain/`, `countries/bahrain/`): `Bahrain Employee Profile` (CPR in place of Resident Card/EID/QID/Iqama), `Bahrainisation Requirement`/`Bahrainisation Profile` (identical shape to Saudization/Qatarization/Emiratisation/Omanisation), hand-rolled EOSB (Bahrain Labour Law No. 36/2012 -- half a month's wage/year for the first 3 years, one month/year after; numerically identical slabs to Oman's rule, independently). `sio_registered` tracks Bahrain's Social Insurance Organisation unemployment scheme -- genuinely covers expatriates, unlike Saudi's GOSI, but still modelled as a registration flag rather than a contribution calculator, the same conservative caution taken for every other country's payroll-adjacent check. Two Government Submission Types: `BAH_BAHRAINISATION_REPORT`, `BAH_SIO_REGISTRATION`. Patch `v0_7/setup_bahrain.py`.
- **Kuwait** (`gcc_hr/kuwait/`, `countries/kuwait/`): `Kuwait Employee Profile` (Civil ID), `Kuwaitisation Requirement`/`Kuwaitisation Profile` (same shape). `wps_registered` in place of a GOSI equivalent (Kuwait's PIFSS pension covers nationals only). **EOSB mirrors Saudi's multi-slab, resignation-reduction shape instead of Oman's/Bahrain's single-rule shape** -- Kuwait Labour Law No. 6/2010 uses the same day-fraction/resignation-band structure Saudi's does, so `GRATUITY_RULES` in `countries/kuwait/setup.py` is a structural copy of Saudi's own 4-row list, renamed. Two Government Submission Types: `KWT_KUWAITISATION_REPORT`, `KWT_WPS_REPORT`. Patch `v0_8/setup_kuwait.py`.
- **API**: `api/bahrainisation.py`, `api/kuwaitisation.py`, identical shape to the other four countries'. Zero new code in `api/government.py` for either.

### Frontend

- **`BahrainProfileCard.vue`**/**`Bahrainisation.vue`** (`/gcc_hr/bahrain/bahrainisation`) and **`KuwaitProfileCard.vue`**/**`Kuwaitisation.vue`** (`/gcc_hr/kuwait/kuwaitisation`) -- identical shape to the other countries' equivalents. Zero new frontend code for Government Integration, for either country.
- `nav.ts`'s `CURRENT_PHASE` bumped to 10; new "Bahrain" and "Kuwait" nav sections.

### Testing

66 new tests (240 total, all passing). Covers both countries' full rule sets, workforce-nationalization engines, government submission generators, API wrappers, and -- for Kuwait specifically -- a `test_setup.py` asserting all 4 hand-rolled Gratuity Rule rows exist with the correct slabs/fields.

### Bugs found and fixed / structural changes during Phase 9/10's own verification

- **The "borrow a placeholder country for the engine's zero-rules test" pattern finally ran out of countries.** `gcc_hr_core/compliance_engine/test_engine.py` had moved from Qatar -> UAE -> Oman -> Bahrain across Phases 6-9's own turns, each time borrowing whichever GCC country hadn't shipped real rules yet. Kuwait (Phase 10) shipping real rules means all six GCC countries this app targets now have seeded rules -- there is no placeholder country left, and HR Country Settings' own validation rejects any non-GCC country (`test_non_gcc_country_rejected`), so a fictional one isn't an option either. Replaced the whole strategy: `setUpClass` now disables Bahrain's real seeded rules for the duration of the test class (via `frappe.db.set_value(..., "enabled", 0)`) and restores them afterward via `addClassCleanup`, rather than relying on a country having zero rules to begin with. This is the permanent fix, not another kick-the-can -- there's no seventh country to move to next time.
- **Found the preventive fix for the recurring `bench migrate` / `ModuleNotFoundError` / `bench clear-cache` cycle.** Phases 6-8 all hit this at least once, always reactively (migrate fails, then `clear-cache`, then migrate again). For Phase 9/10, `bench clear-cache` was run *before* the first migrate attempt, and the failure never occurred at all -- confirming this is a preventable cache-staleness issue, not an unavoidable one, and updating the standing guidance in ARCHITECTURE.md accordingly.
- **Two background agents building disjoint file trees in parallel produced zero merge conflicts**, as designed -- confirming the "give each agent an exclusive file list, forbid the shared files, wire the shared files up once centrally afterward" pattern is a viable substitute for git-worktree isolation when the repo isn't git-tracked.

## Phase 8 -- Oman (2026-08-14)

The fourth country, and back to hand-rolled EOSB -- unlike UAE, Frappe HR ships no Oman regional package to reuse.

### Backend

- **`Oman Employee Profile`** (`gcc_hr/oman/doctype/`): Resident Card in place of Iqama/QID/EID, plus `pasi_registered`/`wps_registered` for the Public Authority for Social Insurance and Wage Protection System -- both tracked as identity/registration flags, not contribution calculators, since this app isn't confident enough in current PASI contribution rates (a genuinely evolving area after a 2023 reform extended coverage) to model them the way GOSI is modelled for Saudi.
- **`Omanisation Requirement`/`Omanisation Profile`** and **`countries/oman/omanisation.py`**: identical shape to Phase 4/6/7's Saudization/Qatarization/Emiratisation.
- **EOSB is hand-rolled**, unlike UAE's Phase 7 EOSB: Oman Labour Law (Royal Decree 35/2003, as amended) -- 15 days' wage per year for the first three years, one month's wage per year after that. One two-slab `Gratuity Rule`, no resignation-specific reduction modelled (same caution as Qatar's).
- **`countries/oman/rules.py`/`government.py`**: `check_resident_card_expiry`/`check_work_permit_expiry`/`check_non_omani_has_resident_card`/`check_pasi_registered` (Oman-specific) plus the same three duplicated generic checks the other three countries have. Two Government Submission Types: `OM_OMANISATION_REPORT` and `OM_PASI_REGISTRATION`.
- **API**: `api/omanisation.py`, identical shape to the other three countries'. Zero new code in `api/government.py`.
- **Patch** `v0_6/setup_oman.py`: Oman's first patch, same shape as `v0_4`/`v0_5`.

### Frontend

- **`OmanProfileCard.vue`** and **`Omanisation.vue`** (`/gcc_hr/oman/omanisation`) -- identical shape to the Qatar/UAE equivalents. Zero new frontend code for Government Integration.
- `nav.ts`'s `CURRENT_PHASE` bumped to 8; new "Oman" nav section.

### Testing

32 new tests (174 total, all passing). Covers the full rule set, the workforce-nationalization engine, both government submission generators, the API wrappers, and a fourth country's proof that the Government Submission state machine needs zero country-specific code.

### Bugs found and fixed during Phase 8's own verification

- **The inert-country test fixture needed moving a third time, right on schedule.** `gcc_hr_core/compliance_engine/test_engine.py` needs a country with zero seeded rules; Phase 6 moved it from Qatar to UAE, Phase 7 moved it from UAE to Oman (since UAE was about to get real rules), and Phase 8 -- seeding Oman's real rules -- moved it again, this time to Bahrain (still a placeholder), with the comment updated to track the full history. `test_hr_country_settings.py`'s enabled/disabled country lists were updated the same way.
- **`bench migrate` failing with `ModuleNotFoundError` a second time despite `modules.txt` being correct up front** -- identical to Phase 7's experience, resolved the same way (`bench clear-cache`), reinforcing that this is a Frappe cache-staleness issue rather than anything specific to how a phase adds a module.

## Phase 7 -- UAE (2026-08-14)

The third country, and the first one where Frappe HR itself already ships a usable regional EOSB implementation -- reused directly instead of duplicated.

### Backend

- **`UAE Employee Profile`** (`gcc_hr/united_arab_emirates/doctype/`): EID (Emirates ID) in place of Iqama/QID, plus `wps_registered`/`wps_bank_name` for the Wage Protection System -- UAE's real distinguishing compliance requirement, same shape as Qatar's. No `payroll.py` for the same reason Qatar has none (no expat social-insurance equivalent to model).
- **`Emiratisation Requirement`/`Emiratisation Profile`** and **`countries/united_arab_emirates/emiratisation.py`**: identical shape to Phase 4/6's Saudization/Qatarization (target lookup by specificity, active-employee counts, risk band, pure what-if simulator).
- **EOSB reuses `hrms/regional/united_arab_emirates/setup.py` directly**, rather than hand-rolling a competing `Gratuity Rule` -- the first country in this app where Frappe HR ships regional content to reuse at all (it has none for Saudi Arabia or Qatar). `create_gratuity_rules()` calls `hrms.regional.united_arab_emirates.setup.setup()` and then fixes up two pre-existing bugs in hrms's own script on the rows it creates (a stale/renamed field Frappe silently drops, and a missing mandatory field it works around via `ignore_mandatory=True`) -- both bugs already discovered once before, independently, while writing Saudi's own EOSB rules in Phase 3. See ARCHITECTURE.md's "UAE (Phase 7)" section.
- **`countries/united_arab_emirates/rules.py`/`government.py`**: `check_eid_expiry`/`check_work_permit_expiry`/`check_non_emirati_has_eid`/`check_wps_registered` (UAE-specific) plus the same three duplicated generic checks Qatar has. Two Government Submission Types: `UAE_EMIRATISATION_REPORT` and `UAE_WPS_REPORT` -- neither calls, or pretends to call, a real government API.
- **API**: `api/emiratisation.py`, identical shape to `api/qatarization.py`. Zero new code in `api/government.py`.
- **Patch** `v0_5/setup_uae.py`: UAE's first patch, same shape as `v0_4/setup_qatar.py`.

### Frontend

- **`UAEProfileCard.vue`** and **`Emiratisation.vue`** (`/gcc_hr/uae/emiratisation`) -- identical shape to their Qatar equivalents. Zero new frontend code for Government Integration.
- `nav.ts`'s `CURRENT_PHASE` bumped to 7; new "UAE" nav section.

### Testing

34 new tests (142 total, all passing after fixing the issues below). Covers the full rule set, the workforce-nationalization engine, both government submission generators, the API wrappers, and -- specifically for UAE -- `countries/united_arab_emirates/test_setup.py`, which asserts hrms's own seeded `Gratuity Rule` rows actually get both bug fixes applied, idempotently.

### Bugs found and fixed during Phase 7's own verification

- **Two Phase-1-era tests had already been moved off Qatar in anticipation of this exact problem (Phase 6's note said so), and needed moving again.** `gcc_hr_core/compliance_engine/test_engine.py` had been pointed at United Arab Emirates as its "no seeded compliance rules" fixture company after Phase 6 broke its original Qatar fixture; Phase 7 seeding UAE's real rules broke it the same way, right on schedule. Moved to Oman (still a placeholder) with an updated comment tracking the history. `test_hr_country_settings.py`'s enabled/disabled country lists were updated the same way.
- **Missing `modules.txt` entry, again, differently this time.** `"United Arab Emirates"` was added to `modules.txt` *before* creating the first doctype JSON (the lesson from Phase 6's identical bug) -- and `bench migrate` still failed with the same `ModuleNotFoundError` on the first attempt. Resolved by `bench clear-cache`, not a code change; Frappe's own module-list resolution apparently cached stale state from earlier in the session. Documented as a new, distinct failure mode from Phase 6's (which was a genuinely missing entry) in ARCHITECTURE.md's "Why two `saudi_arabia` folders" section.
- **The test suite's own write-count ceiling, not a product bug.** The console-based test runner (see CONTRIBUTING.md) wraps the entire suite in one savepoint, never committing until the final rollback, by design -- so nothing persists no matter what. That design choice means Frappe's own runaway-write safety valve (`frappe.db.MAX_WRITES_PER_TRANSACTION`, default 200,000 writes per transaction) accumulates across the *whole* suite rather than resetting per test, and finally tripped once the suite crossed 130 tests, failing six UAE tests with `TooManyWritesError` on ordinary `Company`/`Employee` inserts that had nothing wrong with them. Fixed by raising the limit in the runner script itself before each run; not a `gcc_hr` code change, and not something `bench run-tests`' real per-test-class isolation would ever hit.

## Phase 6 -- Qatar (2026-08-14)

The second country. Full identity/documents/rules, Qatarization workforce tracking, EOSB, and two Government Submission Types -- added without changing a line of Saudi Arabia's business logic, proving out the country-plugin architecture's central promise.

### Backend

- **`Qatar Employee Profile`** (`gcc_hr/qatar/doctype/`): QID (Qatar ID) in place of Iqama, plus `wps_registered`/`wps_bank_name` for the Wage Protection System (Law No. 17 of 2020) -- Qatar's real distinguishing compliance requirement, in place of Saudi's GOSI (there's no expat social-insurance equivalent to model for Qatar, so Qatar has no `payroll.py`; the existing generic dispatch already no-ops safely for that).
- **`Qatarization Requirement`/`Qatarization Profile`** (`gcc_hr/qatar/doctype/`) and **`countries/qatar/qatarization.py`**: identical shape to Phase 4's Saudization (target lookup by specificity, active-employee counts, risk band, pure what-if simulator) -- Qatar's own seeded target is an even more explicit illustrative placeholder than Saudi's, since Qatar has no Nitaqat-equivalent public quota system.
- **EOSB**: one `Gratuity Rule` ("Qatar - Standard End of Service Gratuity", 21/30 of basic wage per year, Qatar Labour Law No. 14/2004 Art. 54) -- a single standard rate, not Saudi's three resignation-tiered rules, since this app doesn't confidently model any Qatar-specific resignation reduction; the seeded rule says so explicitly.
- **`countries/qatar/rules.py`/`government.py`**: `check_qid_expiry`/`check_work_permit_expiry`/`check_non_qatari_has_qid`/`check_wps_registered` (Qatar-specific) plus `check_passport_expiry`/`check_contract_active`/`check_contract_salary_match` (identical logic to Saudi's, deliberately duplicated -- see ARCHITECTURE.md). Two Government Submission Types: `QAT_QATARIZATION_REPORT` (from `Qatarization Profile`) and `QAT_WPS_REPORT` (a worksheet of who still needs WPS registration, from `Qatar Employee Profile`) -- neither calls, or pretends to call, a real government API.
- **API**: `api/qatarization.py` (`recalculate_now`/`simulate`), identical shape to `api/saudization.py`. **Zero new code in `api/government.py`** -- Qatar's two submission types run through the exact same state machine Saudi's use.
- **Patch** `v0_4/setup_qatar.py`: Qatar's first patch, combining what were three separate Saudi patches (localization/payroll/workforce) into one, since Qatar ships all of it in a single phase.

### The core bug this phase's whole premise surfaced

`gcc_hr_core/workforce.py`'s daily scheduler dispatch hardcoded the literal string `"saudization"` as the country-package submodule to look up -- harmless with one country, but exactly the kind of Saudi-specific leak into supposedly generic core code this architecture claims not to have. Fixed by renaming the dispatcher's lookup to a generic `workforce_nationalization`, and giving both `countries/saudi_arabia/` and `countries/qatar/` a thin `workforce_nationalization.py` that re-exports their real (`saudization.py`/`qatarization.py`) module's public functions -- Saudi's actual business logic never changed, only how the dispatcher finds it. The scheduler function itself was renamed too (`run_daily_saudization_recalculation` -> `run_daily_workforce_nationalization_recalculation`). See ARCHITECTURE.md's "Qatar (Phase 6)" section.

### Frontend

- **`QatarProfileCard.vue`** (shown on Employee Detail when the employee's company country is Qatar) and **`Qatarization.vue`** (`/gcc_hr/qatar/qatarization`) -- identical shape to their Saudi equivalents.
- **Zero new frontend code for Government Integration** -- Qatar's two submission types just show up in the existing `/gcc_hr/government` pages the moment they're seeded.
- `nav.ts`'s `CURRENT_PHASE` bumped to 6; new "Qatar" nav section.

### Testing

33 new tests (108 total). Two pre-existing tests broke as a direct, honest consequence of this phase, not a product bug -- see below; all 108 pass after fixing them.

### Bugs found and fixed during Phase 6's own verification

- **The headline one, already described above**: `gcc_hr_core/workforce.py` hardcoding `"saudization"`.
- **Two Phase-1-era tests had silently depended on Qatar having zero compliance rules.** `gcc_hr_core/compliance_engine/test_engine.py` used Qatar as its "no seeded rules" fixture company (a reasonable choice in Phase 1, when that was true) and `test_hr_country_settings.py` asserted Qatar's compliance engine was *not* enabled. Phase 6 seeding Qatar's real rules broke both -- correctly: the product worked exactly as designed, the tests' fixture choice just stopped being valid. Fixed by moving `test_engine.py`'s inert-country fixture to United Arab Emirates (still a placeholder as of Phase 6, with a comment explaining why, for whichever phase makes it not-inert next) and updating `test_hr_country_settings.py` to expect Qatar enabled alongside Saudi Arabia.
- **Missing `modules.txt` entry**: added the `qatar/` doctype folder and JSON files before adding `"Qatar"` to `gcc_hr/modules.txt` -- `bench migrate` failed with `ModuleNotFoundError: No module named 'frappe.core.doctype.qatarization_requirement'` (Frappe fell back to `frappe.core` when it couldn't resolve the module to this app). One-line fix; caught immediately by the first migrate attempt, before any doctype was actually created.

## Phase 5 -- Government Integration (2026-08-14)

The Government Integration Framework: generate a submission document from data this app already tracks, validate it, and record a human's manual filing on the real government portal end to end -- because no GCC government exposes a verified public API to call instead, and this app never fabricates one.

### Backend

- **`Government Submission Type`** (`gcc_hr_core/doctype/`): configurable per submission kind -- `generate_method`/`validate_method` are dotted Python paths resolved with `frappe.get_attr()`, the exact same shape as `HR Compliance Rule.check_method`. Also carries `portal_url`/`portal_instructions`, always shown to the user so a submission is never recorded as filed without pointing at where it was actually filed.
- **`Government Submission`**: the transactional record, one per filing. `gcc_hr_core/government.py` enforces its state machine (Draft -> Generated -> Validated -> Ready for Submission -> Submitted -> Response Uploaded -> Completed) -- every transition function checks the current status before acting, so a submission can't be marked Ready with unresolved validation errors or Submitted before anyone has validated it. `generate()` calls the submission type's generator, attaches the result as a private `File` via `frappe.utils.file_manager.save_file(..., is_private=1)`. Every transition is audited via `gcc_hr_core/audit.py:log_action()`.
- **Saudi Arabia's two submission types** (`countries/saudi_arabia/government.py`), both grounded in data this app already has, not a fabricated integration: `SA_NITAQAT_REPORT` turns the existing `Saudization Profile` (Phase 4) into a CSV, and refuses to validate one built from a profile recalculated more than 30 days ago; `SA_GOSI_REGISTRATION` turns `GOSI Employee Profile` (Phase 3) into a worksheet of who still needs registering at gosi.gov.sa.
- **API** (`api/government.py`): thin, permission-checked wrappers around the state machine -- needed because `gcc_hr_core/government.py` writes via `db_set`, which bypasses the normal permission pipeline (the same reason `api/saudization.py` checks permission before calling `recalculate()`).
- **`countries/saudi_arabia/setup.py`** now also seeds both `Government Submission Type` rows. New patch `patches/v0_3/extend_saudi_arabia_government.py` backfills them for sites migrated before Phase 5 shipped.

### Frontend

- **Government Integration pages** (`/gcc_hr/government`, `/gcc_hr/government/:name`): a list of every submission with status/outcome, a "New Submission" dialog, and a detail page that walks the state machine -- Generate/Regenerate, download the generated document, Validate (surfaces validation errors inline), Mark Ready, Record Manual Submission (captures the government reference number), Upload Response Document (via frappe-ui's `FileUploader`), and Complete (Accepted/Rejected + notes). A banner on the detail page always names the real portal URL and instructions before any submission can be recorded as filed.
- Removed `pages/ComingSoon.vue` -- Government Integration was its last consumer, and it's dead code now that the real pages exist. `nav.ts`'s `CURRENT_PHASE` bumped to 5; the Government Integration nav item no longer carries `comingInPhase: 5`.
- `types/frappe-ui.d.ts` gained a `FileUploader` stub, and `utils/format.ts` gained `governmentSubmissionTone()`.

### Testing

17 new tests (75 total, all passing): the full state machine (happy path end to end, every out-of-order transition guard, regeneration resetting validation, an inactive/unimportable `generate_method`), both Saudi generate/validate function pairs against real `Saudization Profile`/`GOSI Employee Profile` data, and an end-to-end pass through the API wrappers.

### Bugs found and fixed during Phase 5's own verification

- **`vue-tsc` template-checking quirk**: `@click="() => window.open(...)"` inline in a template failed type-checking with `Property 'window' does not exist on type '...ComponentPublicInstance...'` -- Vue's inline-handler compilation resolves bare identifiers against the component instance rather than the global scope inside an arrow function written directly in a template binding. Fixed by moving the two `window.open()` calls (download generated document / view response document) into named methods in `<script setup>`, referenced as plain `@click="methodName"` -- the same pattern already used everywhere else in this app's templates.

## Phase 4 -- Saudization (2026-08-13)

Workforce-nationalization (Nitaqat) tracking, a risk band, and a What-If simulator that never touches real employee data.

### Backend

- **`Saudization Requirement`** (`gcc_hr/saudi_arabia/doctype/`): configurable target percentage, matched by company override, then Activity+Business Size, then a global fallback -- all effective-dated the same way `GOSI Settings` is. Nitaqat's real required percentage varies by sector/size and changes by MHRSD decree, so (like GOSI's rates) the seeded row is explicitly labelled as an illustrative placeholder, never a claim of a real requirement.
- **`Saudization Profile`**: one row per company, `field:company` autonamed. `countries/saudi_arabia/saudization.py`: `get_workforce_counts()` counts *Active* employees only, split Saudi/Non-Saudi via `Saudi Employee Profile.nationality_status` (the existing Phase 2 field -- no duplicate nationality data introduced); `recalculate()` writes the profile via `db_set` (no full `save()`, since the count/percentage fields are all read-only-by-design outputs, not user input going through `validate()`); `compute_status()` maps the gap to Compliant/At Risk/Non-Compliant using a 2-point tolerance band that's this app's own UX threshold, not a Nitaqat rule.
- **What-If Simulator** (`saudization.py:simulate()`): pure projection over the current counts -- hire/terminate Saudi/Non-Saudi deltas, clamped at 0, recomputes the projected percentage and status. Never calls `.save()`/`.insert()` on anything; a dedicated test (`test_simulate_does_not_touch_real_data`) asserts the real counts are unchanged after calling it.
- **API** (`api/saudization.py`): `recalculate_now(company)` (permission-checked against `Saudization Profile`) and `simulate(...)` (read-permission-checked) -- the only two Phase 4 endpoints, for the same reason Phase 1's dashboard needed one: neither is expressible as plain `frappe.client.*` CRUD.
- **Daily scheduler**: `gcc_hr_core/workforce.py:run_daily_saudization_recalculation()` -- generic dispatcher (iterates every `GCC HR Company Settings` row and calls `get_country_attr(country, "saudization", "recalculate")`), so this stays Saudi-only code core never imports directly, same shape as the payroll and compliance dispatchers.
- **`countries/saudi_arabia/setup.py`** now also seeds the global-fallback `Saudization Requirement` and (when a specific company is passed, e.g. from the `GCC HR Company Settings` country-change hook) provisions that company's `Saudization Profile` immediately rather than waiting for the next daily run. New patch `patches/v0_2/extend_saudi_arabia_saudization.py` backfills both for companies already on Saudi Arabia before this phase shipped.

### Frontend

- **Saudization page** (`/gcc_hr/saudi/saudization`): a table of every company's current counts/percentage/target/gap/status with a per-row [Recalculate] action, plus a What-If Simulator card (hire/terminate inputs -> current vs. projected percentage and risk).
- `nav.ts`'s `CURRENT_PHASE` bumped to 4; Saudization no longer shows a "Phase 4" badge. Also fixed a leftover bug from Phase 3: "Employment Contracts" was still tagged `comingInPhase: 3` even though that page shipped that same phase.

### Testing

11 new tests (58 total, all passing): target-lookup priority (company override > activity+size > global fallback) and effective-dating, the status-band boundaries, active-only workforce counting, `recalculate()`'s writes, the simulator's math *and* its non-mutation guarantee, and both API endpoints.

### Bugs found and fixed during Phase 4's own verification

- **The headline one**: seeding the global-fallback `Saudization Requirement` without explicitly setting `company` let Frappe's own default-injection auto-fill it with the current user's default company (any field literally named `company` gets this treatment when absent from an insert). That silently turned the "applies to every company" row into a company-specific one, breaking target lookups for every *other* company -- caught immediately because seeding into this dev site's real "glob (Demo)" company produced a wrong row visibly scoped to it. Fixed the seeder to pass `"company": ""` explicitly (present-but-falsy skips the default-injection path; absent-entirely triggers it) -- and, since this is exactly as reachable by a real admin filling in the Desk form by hand, added `saudization_requirement.js` to clear the field on new documents rather than just fixing the one seeded row.
- Two of the new tests had their own bugs, not the product's: creating an Employee with `status="Left"` needs `relieving_date` (ERPNext's own validation) that the test helper wasn't setting, and one test recreated the exact default-injection bug above in its own fixture data (also missing the explicit `"company": ""`).
- A third, subtler test-isolation bug surfaced on a full-suite rerun: `FrappeTestCase` only rolls back once, at class teardown, not between individual test methods, so four tests that both created `Employee` rows and asserted an exact workforce count were silently order-dependent on a shared `TEST_COMPANY` -- passing only because alphabetical test-method ordering happened to run the count-asserting tests before other tests polluted that company with more employees. Fixed by giving each of those four tests its own dedicated company via a new `_make_company()` helper; see ARCHITECTURE.md's "Saudization (Phase 4)" section for the general rule this establishes.

## Phase 3 -- Saudi Payroll (2026-08-13)

GOSI, contract-vs-payroll validation, payroll compliance checks, and EOSB. Extends standard Frappe HR payroll (Salary Slip, Payroll Entry, Gratuity) rather than building a parallel engine.

### Backend

- **GOSI** (`gcc_hr/saudi_arabia/doctype/`): `GOSI Settings` (effective-dated employee/employer contribution rate + floor/ceiling per Saudi/Non-Saudi category -- seeded with an explicitly-labelled *illustrative* starting point, not a claim of current official rates), `GOSI Employee Profile` (registration status/number per employee), `GOSI Payroll Calculation` (one immutable row per Salary Slip, system-created only -- no role has `create`). `countries/saudi_arabia/gosi.py` splits the pure contribution arithmetic (`compute_contribution()`) from the Salary-Slip-reading/doctype-creating wrapper (`calculate_for_salary_slip()`) specifically so the math is unit-testable without needing a full Salary Structure/Assignment/Slip provisioned.
- **Payroll dispatch**: `gcc_hr_core/payroll.py:sync_country_payroll()` on `Salary Slip.on_submit` -- generic core hook that dispatches to `get_country_attr(country, "payroll", "on_salary_slip_submit")`, so GOSI calculation stays Saudi-only code that core never imports directly.
- **3 new Saudi compliance rules** (`countries/saudi_arabia/rules.py`): `SA_CONTRACT_ACTIVE` (linked Contract exists, is submitted, hasn't expired), `SA_CONTRACT_SALARY_MATCH` (Contract's Basic Salary vs. the active Salary Structure Assignment's `base` -- Skips, doesn't Fail, when there's nothing to compare against yet), `SA_GOSI_REGISTERED` (Warning severity -- registration commonly lags a new hire by a short grace period, so it's a signal, not a hard block).
- **EOSB**: 4 `Gratuity Rule` rows seeded for KSA Labour Law Art. 84 (half a month's wage per year for the first 5 years, a full month per year after; resignation reduces the award: none under 2 years, 1/3 from 2-5, 2/3 from 5-10, full at 10+) -- reusing HRMS's own slab-based Gratuity engine entirely, the same way `hrms/regional/united_arab_emirates/setup.py` seeds UAE's, rather than a new "EOSB Calculation" doctype.
- **`Payroll Compliance Check`** (+ child `Payroll Compliance Check Employee`) in `gcc_hr_core`: one row per Payroll Entry submission attempt, with a per-employee breakdown linking back to that employee's `HR Compliance Check`. `gcc_hr_core/payroll.py:validate_payroll_compliance()` on `Payroll Entry.before_submit` runs the compliance engine for every employee in the run and, if `GCC HR Company Settings.payroll_compliance_required` is set (default on) and any employee has a Critical/Blocking issue, blocks submission with `frappe.throw`.
- **New patch** `patches/v0_1/extend_saudi_arabia_payroll.py` -- re-invokes `countries/saudi_arabia/setup.py:setup()` (idempotent) so companies that already ran Phase 2's patch pick up the new rules/Gratuity Rules/GOSI Settings; Frappe patches don't re-run just because the function they call changed.

### Frontend

- **GOSI page** (`/gcc_hr/saudi/gosi`) -- GOSI Settings (read-only rate table), employee registration list + create, recent payroll calculations.
- **Payroll Compliance page** (`/gcc_hr/payroll` + `/gcc_hr/payroll/:name` detail) -- list of runs with per-employee drill-down.
- **Contracts page** (`/gcc_hr/contracts`) -- list + create for the standard `Contract` doctype (party_type=Employee), including the GCC salary breakdown fields from Phase 1.
- `nav.ts`'s `CURRENT_PHASE` bumped to 3; GOSI/Payroll Compliance/Contracts nav items no longer show a "Phase N" badge.

### Testing

16 new tests (47 total, all passing): GOSI contribution math at every boundary (seeded Saudi/Non-Saudi rates, floor/ceiling capping, no-settings-effective-yet), effective-dating lookup, the "skip when not registered/suspended" guards, all three new Saudi rules including a full-engine-run recount, and the payroll-compliance dispatch/blocking logic (creates a check, blocks when required and critical, doesn't block when not required, no-ops for a company with no GCC HR Company Settings at all).

Also verified live in a browser: created a fully-provisioned Saudi employee (Iqama, work permit, GOSI registration, submitted Contract), ran the compliance check and confirmed a 100% score with the exact expected breakdown (5 passed, 2 correctly Skipped -- Passport and Contract-Salary-Match, both with nothing yet to compare against), then checked the Contracts, GOSI and Payroll Compliance pages all render correctly against real data with zero console/network errors.

### Bugs found and fixed during Phase 3's own verification

- `gosi_settings.py:get_applicable_settings()` compared a DB-returned `datetime.date` (`row.effective_to`) against a caller-supplied `str` on_date with `>=`, raising `TypeError` -- Python doesn't define an ordering between those types. Fixed by normalizing both sides through `frappe.utils.getdate()`.
- `Gratuity Rule`'s `applicable_earnings_component` (which salary component(s) the award is based on) is mandatory, but `hrms/regional/united_arab_emirates/setup.py` never sets it -- it survives only because that script passes `ignore_mandatory=True` to `insert()`. Rather than copy that workaround, set `applicable_earnings_component` to Basic properly.
- The same UAE script also sets `work_experience_calculation_method`, a field that doesn't exist on the current `Gratuity Rule` schema (renamed to `work_experience_calculation_function` at some point; `frappe.get_doc(dict)` silently drops unknown keys, so UAE's setup has quietly been leaving this field at its default ever since). Used the correct current field name instead of copying the stale one.
- Testing `calculate_for_salary_slip()`'s doctype-creation path (not just its early-return guards) needs a real `Salary Slip`/`Payroll Entry` row to exist, or Frappe's Link validation rejects it outright (`LinkValidationError`) -- confirmed by trying a bogus link name directly. Provisioning a fully valid Salary Slip through ERPNext's real payroll stack requires a Holiday List, Salary Structure and Salary Structure Assignment, and even then a `get_holiday_list_for_employee` check (evaluated at `nowdate()`, not the slip's own posting date, for reasons not worth reverse-engineering further) kept failing regardless of the Employee's assigned Holiday List or the Company's default one, cache-clearing included. Given this is ERPNext's own payroll-provisioning complexity, not anything this app's code is responsible for, settled on a narrower, well-justified boundary instead: extract the pure math (`compute_contribution`) for direct unit testing, and use `frappe.get_doc({...}).db_insert()` (bypasses `validate()`/business logic, writes a minimal real row) to create just enough of a stand-in `Salary Slip`/`Payroll Entry` to satisfy the Link check for the handful of tests that need one.

## Phase 2 -- Saudi Arabia Localization (2026-08-13)

Saudi identity fields, Iqama/work-permit document tracking, and Saudi's first four compliance rules. Contracts and payroll are untouched -- still Phase 3.

### Backend

- **`Saudi Arabia` module** (`gcc_hr/saudi_arabia/`, a top-level Frappe module folder distinct from `gcc_hr/countries/saudi_arabia/`'s plain Python package -- see ARCHITECTURE.md's "Why two `saudi_arabia` folders" for why Frappe's module-folder resolution requires this split): `Saudi Employee Profile`, one row per Employee, autonamed `field:employee`. Holds nationality status (Saudi/Non-Saudi), Iqama/border/visa/work-permit numbers and expiries, sponsor, profession, GOSI registration number (identity reference only -- Phase 3 owns the actual contribution calculation), Qiwa contract status.
- **`countries/saudi_arabia/employee.py:sync_employee()`** -- auto-creates the Saudi Employee Profile the moment an Employee is inserted under a company whose `GCC HR Company Settings.country` is Saudi Arabia. Dispatched generically from `gcc_hr_core`'s `create_compliance_profile()`/`sync_compliance_profile()` via `get_country_attr(country, "employee", "sync_employee")` -- core still never imports `saudi_arabia` directly.
- **`countries/saudi_arabia/setup.py:setup()`** -- seeds all 10 Saudi `HR Document Type` rows (Iqama, Passport, Work Permit, Employment Contract, National ID, Health Certificate, Professional License, Driving License, Visa, Other) and 4 `HR Compliance Rule` rows, then flips `HR Country Settings("Saudi Arabia").compliance_engine_enabled` on. Dispatched by `GCC HR Company Settings`'s existing country-change hook, *and* by a new patch (`patches/v0_0/setup_saudi_arabia.py`) for companies already pointed at Saudi Arabia before this phase shipped -- the on_update dispatch only fires when the country field actually *changes*, so an upgrade needs the explicit patch. The patch also backfills `Saudi Employee Profile` for any pre-existing employees at those companies.
- **`countries/saudi_arabia/rules.py`** -- the four check functions: `check_iqama_expiry`, `check_work_permit_expiry` (both Critical, 30-day warning window), `check_passport_expiry` (Warning, 90-day window, reads `Employee Compliance Profile.passport_expiry` directly rather than re-querying), `check_non_saudi_has_iqama` (Blocking -- a Non-Saudi employee with no Iqama number on file at all). All four skip cleanly (not Fail) for Saudi nationals or when no Saudi Employee Profile exists yet.

### Frontend

- `SaudiProfileCard.vue` -- a new card on the Employee Detail page, shown only when `profile.doc.country === 'Saudi Arabia'`, with editable fields for every identity/permit field on `Saudi Employee Profile` and a Save button (`createDocumentResource(...).setValue.submit(...)`).

### Testing

8 new tests (27 total, all passing): Saudi Employee Profile auto-creation (and non-creation for non-Saudi companies), the "missing Iqama is a soft compliance signal, not a hard block" design decision, all four rule functions at their expiry boundaries (expired / expiring-within-window / comfortably valid), Saudi-national skip behavior, and a full engine run confirming all four Saudi rules actually execute and score correctly.

Also verified live in a browser against the running bench, end to end: created a real Non-Saudi employee under a Saudi-Arabia-configured company, filled in Iqama/Sponsor/Profession on the new Saudi card, saved, reloaded the page to confirm persistence, then clicked [Run Compliance Check] and watched the score move from 0% (no Saudi identity data at all) to 60% (Iqama-on-file rule now passing, Iqama-expiry rule now correctly *failing* because the expiry date entered was within the 30-day window, work-permit-expiry still failing with no data, passport-expiry skipped with no data) -- the exact math the engine should produce, confirming Vue -> API -> engine -> DB -> back to Vue works for Saudi-specific rules, not just the generic Phase 1 path.

### Bugs found and fixed during Phase 2's own verification

- The two existing generic engine tests (`test_compliance_check_with_no_rules_scores_100`, `test_only_saudi_arabia_compliance_engine_enabled_by_default`) hard-coded Saudi Arabia as their "no rules configured" test country. Once Phase 2 seeded 4 real Saudi rules and flipped the engine flag on, both tests' premises became false. Fixed by moving the *generic* engine-mechanics tests to Qatar (still rule-free) and rewriting the country-settings test to assert the new, correct state (Saudi Arabia's flag is now 1; every other country's is still 0) instead of asserting the old Phase 1 default.
- `mandatory_depends_on` in `saudi_employee_profile.json` (Iqama Number required when Non-Saudi) turned out to be a Desk-form-only hint -- Frappe never enforces it server-side (confirmed by grepping the framework: the property only appears in JS form-validation code, never in `model/document.py`'s mandatory-field logic). Initially attempted a `validate()`-level `frappe.throw`, but that would break `sync_employee()`'s auto-provisioning (a fresh hire's profile is created before HR has their Iqama). Fixed by leaving it unenforced and relying on `check_non_saudi_has_iqama` as the actual (correctly *soft*, scored) compliance signal instead -- a better design than the hard block would have been anyway.
- A test set `Employee.valid_upto` via `frappe.db.set_value` and expected the already-loaded `Employee Compliance Profile.passport_expiry` (`fetch_from: employee.valid_upto`) to reflect it after `.reload()` -- but `fetch_from` only re-copies during the *profile's own* `validate()`/save cycle, not merely by reloading (which just re-reads the profile's own already-stored value). Fixed the test to `.save()` the profile to force the re-fetch, rather than assuming reload alone would do it.
- Running the ad hoc `unittest`-in-console test runner leaked committed data into the real database twice more during this phase's own verification (same root cause as Phase 1's cleanup note below), including once via a `frappe.db.commit()` inside `run_daily_compliance_sweep`/`expiry_engine` that silently released the wrapping `SAVEPOINT`, breaking the rollback outright. Fixed the runner itself: set `frappe.db._disable_transaction_control = 1` for the duration of the run (the flag the real `bench run-tests` machinery uses to make `commit()` a no-op during tests) before rolling back to the savepoint -- see CONTRIBUTING.md's updated "Running tests" section.

## Phase 1 -- Foundation (2026-08-13)

Country-agnostic foundation. No Saudi-specific logic anywhere yet -- that starts Phase 2.

### Backend

- **`GCC HR Core` module** (`gcc_hr/gcc_hr_core/`):
  - `HR Country Settings` -- one row per GCC country (Saudi Arabia, Qatar, UAE, Oman, Bahrain, Kuwait), seeded by `install.py:after_install()`. Rejects any non-GCC country.
  - `GCC HR Company Settings` -- one row per Company; selecting a country dispatches to that country's `countries/<slug>/setup.py:setup()` (verified as a safe no-op for Saudi Arabia in Phase 1, since that package doesn't exist yet).
  - `Employee Compliance Profile` -- auto-created/kept in sync on `Employee.after_insert`/`on_update`. Salary fields are `fetch_from` the linked `Contract`'s new Custom Fields, not stored twice.
  - `HR Document Type`, `HR Compliance Document`, `HR Document Expiry Threshold` -- configurable document catalog + expiry tracking. Status/severity computed by `compliance_engine/expiry_engine.py`, with a daily sweep (`run_daily_expiry_sweep`) that goes through each document's full `save()` so `Notification` triggers still fire.
  - `HR Compliance Rule`, `HR Compliance Check` (+ `HR Compliance Check Result` child), `HR Compliance Score Band` -- the compliance engine (`compliance_engine/engine.py`, `scoring.py`). Rule metadata (severity, effective dates, enabled) is configuration; each rule's predicate is a dotted-path Python callable, validated importable at save time.
  - `HR Audit Log` -- append-only (no role has create/write/delete; written only via `audit.py:log_action()`), wired to `on_update` of every Phase 1 config/profile doctype via `audit.py:log_doc_change()`.
- **Country plugin dispatcher** (`gcc_hr/countries/__init__.py`) -- `get_country_module()`/`get_country_attr()`, mirroring `hrms/overrides/company.py`'s regional-setup pattern. Placeholder packages for qatar/uae/oman/bahrain/kuwait; saudi_arabia gets real content starting Phase 2.
- **Contract extended, not duplicated** -- 11 Custom Fields (GCC salary breakdown + contract terms) via fixtures, `gcc_total_salary` computed by `overrides/contract.py` on `validate`.
- **Roles** -- 7 new custom roles (GCC HR Administrator, HR Officer, Payroll Manager, Payroll Officer, Compliance Manager, Compliance Officer, Government Integration Manager), reusing standard HR Manager/Employee for the rest.
- **Notifications** -- 6 fixture `Notification` records (document expiry at 90/30/7 days, document expired, compliance score critical, contract expiring), using Frappe's own Days-Before/Value-Change triggers rather than custom notification code.
- **API** -- `api/dashboard.py:get_summary()` (the one aggregation endpoint the Command Center needs), `api/compliance.py:run_compliance_check_for_employee()` (backs the [Run Compliance Check] button).
- **`website_route_rules`** -- `/gcc_hr/<path:app_path>` -> `gcc_hr`, so Vue Router's history-mode sub-routes resolve server-side instead of 404ing on direct navigation/refresh.
- **Employee dashboard connection** -- `override_doctype_dashboards["Employee"]` adds a "GCC HR Compliance" group (composes with HRMS's own Employee dashboard hook, doesn't replace it).

### Frontend

- Vue 3 + TypeScript SPA, served at `/gcc_hr`, built with Vite + `frappe-ui` + Pinia + Vue Router + Tailwind. `yarn build` runs `vue-tsc --noEmit` as part of the build; `frontend/src/types/frappe-ui.d.ts` redirects the `frappe-ui` module specifier to a local ambient declaration (that package ships raw, partially-typed source with no compiled `.d.ts`, so type-checking it directly surfaces its own internal type errors as if they were ours) -- same approach `qcore`'s frontend uses for the same package, in this same bench.
- Pages: Command Center (dashboard cards + status breakdown), Employee Compliance Profiles (list + detail, with a working [Run Compliance Check] action), Compliance Documents (list + create), Compliance Rules (list + create + enable/disable toggle), Compliance Checks (read-only history), Country Settings (toggle active/compliance-engine-enabled), Company Settings (list + create). `ComingSoon` placeholders (no fake data) for Contracts/Payroll/Government/GOSI/Saudization nav items, labelled with the phase that actually ships them.
- All CRUD goes through `frappe.client.*` via frappe-ui resources; only the dashboard summary and the "run check now" action are custom endpoints.

### Testing

19 `FrappeTestCase` tests, all passing: country seeding/validation, company-settings country dispatch + audit logging, compliance-profile auto-creation, the full compliance engine (no-rules default, a failing critical rule's score/status math, invalid `check_method` rejection), document expiry status at every boundary + the daily sweep correcting stale documents, audit-log immutability, Contract salary computation, and the dashboard summary endpoint.

### Bugs found and fixed during Phase 1's own verification

- `expiry_engine.compute_status_for_document()`'s severity loop didn't `break` on the first (most urgent) matching threshold, so it always returned the *least* severe matching band instead of the most severe.
- `api/dashboard.py` used raw SQL-function strings (`"count(*) as count"`, `"avg(compliance_score)"`) in `fields=[...]`, which Frappe v16's query builder rejects (`ValidationError: SQL functions are not allowed as strings in SELECT`); fixed to the dict syntax (`{"COUNT": "*", "as": "count"}` / `{"AVG": ..., "as": ...}`).
- frappe-ui's `createResource`/`createListResource`/`createDocumentResource` silently fall back to a bare `fetch(url)` (no `/api/method/` prefix) unless `setConfig('resourceFetcher', frappeRequest)` is called at bootstrap -- without it, every list/resource call 404s by resolving against the current SPA route instead of the site root. Fixed in `frontend/src/main.js`. (This appears to affect `qcore`'s own `createResource`-based dashboard call too, in this same bench -- not something this app can fix, just noting it.)
- Vue Router's history mode needs a server-side catch-all (`website_route_rules`) or every sub-route 404s on direct navigation/refresh -- added, following the same pattern `qcore` uses for its own SPA.
- `HR Compliance Check` initially granted Compliance Manager `create` permission, which would let someone create a blank, unpopulated check via Desk (the score/results only get computed by the engine) -- removed; check creation is engine-only, matching the "immutable run history" design.
- Converting the SPA to TypeScript surfaced three more: an object-iteration `v-for` key typed `string | number` passed straight into a `string`-only prop/function (`Dashboard.vue`), an unused `props` binding, and (fixed by simplifying rather than typing around it) an `App.vue` branch that checked `route.meta.shell` on a route meta field no route ever actually set -- dead code from copying `qcore`'s `App.vue`, removed instead of type-augmented.
- `api/dashboard.py`'s `average_score` was `int 0` (not `0.0`) whenever `Employee Compliance Profile` has zero rows -- `AVG()` over an empty set is SQL `NULL`, and `None or 0` in Python gives an `int`. Caught by `test_dashboard.py`'s own type assertion once the scratch/test employees created during manual verification were cleaned up. Fixed with an explicit `float(...)`.

### Known gaps vs. the fuller spec (not blocking, tracked for later)

- **i18n / Arabic RTL**: not implemented yet. Not part of this app's own Phase 1 breakdown, but is part of the overall brief -- next candidate after Phase 2 (Saudi) or interleaved with it, since Saudi is exactly where Arabic content starts mattering.
- **`bench run-tests --app gcc_hr`** hits the pre-existing ERPNext test-harness issue described in CONTRIBUTING.md's "Running tests" section on a site that already has real Company data (unrelated to this app) -- documented workaround there.
