### GCC HR Compliance

A GCC HR localization and compliance platform built on top of **Frappe HR +
ERPNext** -- not a replacement for them. It adds a country-plugin
architecture (Core + per-country package + Government Integration layer), a
configurable compliance engine (rules, document-expiry tracking, scoring),
and a dedicated Vue 3 SPA (`frontend/`) for managing all of it, on top of
standard Frappe HR/ERPNext doctypes it reuses rather than duplicates
(`Employee`, `Contract`, `Gratuity`/`Gratuity Rule`, `Salary Slip`,
`Payroll Entry`, ...). See ARCHITECTURE.md for how it's put together,
DATABASE.md for the doctype/relationship design, PERMISSIONS.md for the
role/access model, CHANGELOG.md for what's shipped so far (Phase 1:
country-agnostic foundation -- country/company settings, employee compliance
profiles, document expiry tracking, the compliance rule engine and scoring,
audit logging, and the Command Center SPA; Phase 2: Saudi employee identity
`Saudi Employee Profile`, Iqama/work-permit document types, and Saudi's
first four compliance rules; Phase 3: GOSI, contract-vs-payroll validation,
payroll compliance checks, and EOSB via seeded `Gratuity Rule`s; Phase 4:
Saudization workforce-nationalization tracking (`Saudization Requirement`/
`Saudization Profile`), the daily recalculation engine, and a what-if
hiring/termination simulator; Phase 5: the Government Integration Framework
(`Government Submission Type`/`Government Submission`) -- generate/validate
a submission document, then track a human's manual filing on the real
government portal; Phase 6: Qatar, the second country -- QID-based identity
(`Qatar Employee Profile`), Qatarization workforce tracking, EOSB, and two
Qatar Government Submission Types, none of it requiring a single change to
Saudi's code; Phase 7: UAE, the third country -- EID-based identity (`UAE
Employee Profile`), Emiratisation workforce tracking, two UAE Government
Submission Types, and EOSB that reuses Frappe HR's own regional UAE
Gratuity Rules rather than seeding a competing one; Phase 8: Oman, the
fourth country -- Resident-Card-based identity (`Oman Employee Profile`),
Omanisation workforce tracking, two Oman Government Submission Types, and
hand-rolled EOSB, since Frappe HR ships no Oman regional package; Phase 9:
Bahrain, the fifth country -- CPR-based identity (`Bahrain Employee
Profile`), Bahrainisation workforce tracking, and an SIO registration flag
(Bahrain's unemployment insurance genuinely covers expatriates, unlike
Saudi's GOSI, though still modelled conservatively as a flag not a
calculator); Phase 10: Kuwait, the sixth and last GCC country -- Civil-ID-
based identity (`Kuwait Employee Profile`), Kuwaitisation workforce
tracking, and EOSB that mirrors Saudi's multi-slab resignation-reduction
shape rather than the single-rule shape Qatar/Oman/Bahrain use), and
SECURITY.md for how to report a vulnerability.

**Supported countries.** All six countries this app targets are
implemented -- Saudi Arabia, Qatar, UAE, Oman, Bahrain, and Kuwait -- built
one phase at a time (Phase 2 landed Saudi identity/documents/rules; Phase 3
landed GOSI/payroll validation/EOSB; Phase 4 landed Saudization tracking and
the what-if simulator; Phase 5 landed the Government Integration Framework,
seeded with a Nitaqat report and a GOSI registration worksheet; Phase 6
landed Qatar end to end; Phase 7 landed UAE end to end, including reusing
Frappe HR's own UAE EOSB rules; Phase 8 landed Oman end to end; Phases 9 and
10 landed Bahrain and Kuwait end to end, built by two background agents
working in parallel on disjoint file trees). Every country package was
added without touching any other, already-shipped country's code -- see
ARCHITECTURE.md's "Country plugin architecture" section. No government API
integration is implemented for any country unless a verified official API
exists for it (see "Government integration" below).

**Government integration.** GCC HR never fabricates a government API. Where
no official API is available (or hasn't been verified for this project),
the Government Integration Framework (Phase 5, shipped) falls back to
generate / validate / download / manual-submit / upload-response /
track-status workflows instead of pretending to call one -- see
ARCHITECTURE.md's "Government Integration (Phase 5)" section. Phases 6
through 10 proved this framework is genuinely country-agnostic: every
country's submission types work through the exact same, unmodified state
machine and API layer Saudi Arabia's own use.

### Installation

This app already lives in this bench at `apps/gcc_hr` and is installed on
`mysite.local`, alongside `erpnext` and `hrms` (required apps). To install
it on another site with those apps already installed:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app gcc_hr
bench --site $SITE install-app gcc_hr
```

### Frontend development

```bash
cd apps/gcc_hr/frontend
yarn install
yarn dev      # dev server, proxies API calls to the running bench
yarn build    # production build -- also produces gcc_hr/www/gcc_hr.html (see vite.config.ts)
```

The SPA is served at `/gcc_hr` once built (see `gcc_hr/www/gcc_hr.py`).
Guests are redirected to `/login?redirect-to=/gcc_hr`.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/gcc_hr
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

See CONTRIBUTING.md for the phase-based development workflow this app follows.

### Full documentation

[docs/GCC_HR_Documentation.html](docs/GCC_HR_Documentation.html) is a
self-contained guide covering installation, architecture, the doctype/API
reference, the security model, and a walkthrough of every module --
download it and open it in a browser (GitHub renders raw HTML as source,
not as a page).

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

### License

mit
