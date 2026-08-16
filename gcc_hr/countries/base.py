# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Documents the country-package contract. Nothing here is imported at
runtime -- gcc_hr.countries.get_country_module()/get_country_attr() look up
these names dynamically by convention, exactly like hrms/regional does for
its own (narrower) regional_overrides mechanism. A country package only
needs to implement the submodules it actually uses; missing ones simply
mean that feature isn't available for that country yet (see Phase 1's
qatar/uae/oman/bahrain/kuwait placeholder packages).

Expected submodules, by convention, under gcc_hr/countries/<country_slug>/:

    setup.py
        setup(company: str | None = None) -- called from
        GCCHRCompanySettings.run_country_setup() whenever a company's country
        is set/changed. Seeds country-specific fixtures: HR Document Type,
        HR Compliance Rule, HR Compliance Score Band rows, Gratuity Rule
        records for EOSB, Saudization defaults, etc. Idempotent
        (insert(ignore_if_duplicate=True)), same contract as
        hrms/regional/<country>/setup.py's setup().

        uninstall() -- inverse of setup(), same contract as
        hrms/overrides/company.py:delete_company_fixtures().

    rules.py
        One check function per HR Compliance Rule.check_method configured
        for this country, each shaped:

            def check_xxx(employee: str, profile: "EmployeeComplianceProfile", rule: dict)
                -> tuple[str, str, str]:
                '''Returns (result, message, recommended_action).
                result is one of "Passed" / "Failed" / "Skipped".'''

    employee.py     Country-specific employee identity fields/validations
                     (e.g. Saudi's Iqama/GOSI/sponsor profile, Phase 2;
                     Qatar's QID/WPS profile, Phase 6).
    payroll.py       Payroll compliance + contract-vs-payroll checks (Phase 3).
    gosi.py          GOSI/social-insurance calculation (Saudi-specific, Phase 3).
    government.py    Government Submission Type generate_method/validate_method
                     implementations (Phase 5) -- see gcc_hr_core/government.py.

    Workforce-nationalization (target %, workforce counts, risk status, a
    what-if simulator) needs its own real, country-flavored module for
    readability (saudization.py for Saudi, qatarization.py for Qatar --
    Emiratisation etc. later), since the underlying doctypes/target rules
    genuinely differ per country (Phase 4/6). But gcc_hr_core/workforce.py's
    daily scheduler dispatches generically across every country, so it can't
    hardcode any one of those names -- every country package additionally
    provides a `workforce_nationalization.py` that just re-exports its real
    module's public functions (recalculate/simulate/get_applicable_target/
    get_workforce_counts/compute_status). This split was discovered, not
    designed up front: Phase 4 shipped with the dispatcher hardcoding the
    literal string "saudization", which worked until Phase 6 needed the same
    hook for Qatar -- a Saudi-specific leak in supposedly generic core code.
    Fixed by renaming the dispatcher's lookup (gcc_hr_core/workforce.py,
    itself core, not Saudi's code) and adding the thin re-export shim to
    Saudi's package, rather than special-casing "saudization" inside core.

    iqama.py         Residency-permit specific helpers (Saudi-specific).
"""
