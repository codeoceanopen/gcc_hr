# GCC HR Compliance

A GCC HR localization and compliance platform built on top of **Frappe HR**
and **ERPNext** -- not a replacement for them. It adds a country-plugin
architecture, a configurable compliance engine, and a dedicated Vue 3
Command Center SPA on top of standard Frappe HR/ERPNext doctypes it reuses
rather than duplicates (`Employee`, `Contract`, `Gratuity`/`Gratuity Rule`,
`Salary Slip`, `Payroll Entry`, ...).

## Features

- **Six countries covered** -- Saudi Arabia, Qatar, UAE, Oman, Bahrain and
  Kuwait, each with its own national-ID-based employee identity (Iqama, QID,
  EID, Resident Card, CPR, Civil ID) and document types.
- **Compliance engine** -- configurable rules, document-expiry tracking, and
  a scoring model, country-agnostic at its core.
- **Workforce nationalization tracking** -- Saudization, Qatarization,
  Emiratisation, Omanisation, Bahrainisation and Kuwaitisation, with a daily
  recalculation engine and a what-if hiring/termination simulator.
- **Payroll & EOSB compliance** -- GOSI and contract-vs-payroll validation,
  and End-of-Service Benefit calculation per country, reusing Frappe HR's
  own regional Gratuity Rules where they exist.
- **Government Integration Framework** -- generates and validates government
  submission documents, then tracks a human's manual filing on the real
  government portal. It never fabricates a government API: where no
  verified official API exists, it falls back to a
  generate / validate / download / manual-submit / upload-response /
  track-status workflow instead of pretending to call one.
- **Audit logging** across the compliance engine.
- **Command Center** -- a dedicated Vue 3 SPA for managing all of the above.

Every country package is fully independent of the others -- see
`ARCHITECTURE.md`'s "Country plugin architecture" section.

## Requirements

- Frappe Framework, ERPNext and Frappe HR (`hrms`) already installed on the
  target site
- Python 3.14 (bench-managed)
- Node 24
- MariaDB, Redis

## Installation

1. Get the app into your bench:

   ```bash
   cd $PATH_TO_YOUR_BENCH
   bench get-app gcc_hr https://github.com/codeoceanopen/gcc_hr.git
   ```

2. Install it on a site that already has `erpnext` and `hrms` installed:

   ```bash
   bench --site $SITE install-app gcc_hr
   ```

3. Build the frontend (skip this if you're pulling a release with the
   frontend already built):

   ```bash
   cd apps/gcc_hr/frontend
   yarn install
   yarn build
   ```

4. Open `http://$SITE/gcc_hr` and log in. Guests are redirected to
   `/login?redirect-to=/gcc_hr`.

## Frontend development

```bash
cd apps/gcc_hr/frontend
yarn install
yarn dev      # dev server, proxies API calls to the running bench
yarn build    # production build (see vite.config.ts)
```

## Documentation

**[Open the documentation](https://htmlpreview.github.io/?https://github.com/codeoceanopen/gcc_hr/blob/main/docs/GCC_HR_Documentation.html)**
-- a self-contained guide covering installation, architecture, the
doctype/API reference, the security model, and a walkthrough of every
module. (Source: [docs/GCC_HR_Documentation.html](docs/GCC_HR_Documentation.html)
-- GitHub renders raw HTML as source, not as a page, so use the link above
rather than opening that file directly.)

See also `ARCHITECTURE.md` for how the app is put together, `DATABASE.md`
for the doctype/relationship design, `PERMISSIONS.md` for the role/access
model, `CHANGELOG.md` for release history, and `SECURITY.md` for how to
report a vulnerability.

## Contributing

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

See `CONTRIBUTING.md` for the development workflow this app follows.

## CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

## License

MIT
