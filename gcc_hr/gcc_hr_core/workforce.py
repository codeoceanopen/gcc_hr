# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Workforce-nationalization (Saudization, Qatarization, and future
equivalents like Emiratisation) scheduling. Generic dispatcher, same shape
as compliance_engine and payroll.py -- core never imports a country's
workforce module directly.

Looks up a submodule literally named `workforce_nationalization`, not
`saudization` -- that was Phase 4's naming choice for Saudi's own module,
which this dispatcher used to hardcode directly (a Saudi-specific leak in
otherwise-generic core code, only surfaced once Qatar needed the same
hook in Phase 6). Each country package keeps its real implementation under
its own name (`saudi_arabia/saudization.py`, `qatar/qatarization.py`) for
readability, and additionally exposes a thin `workforce_nationalization.py`
re-export so this dispatcher finds it without core ever naming a specific
country. See countries/base.py."""

import frappe

from gcc_hr.countries import get_country_attr


def run_daily_workforce_nationalization_recalculation():
	companies = frappe.get_all("GCC HR Company Settings", fields=["company", "country"])
	for row in companies:
		recalculate_fn = get_country_attr(row.country, "workforce_nationalization", "recalculate")
		if recalculate_fn:
			recalculate_fn(row.company)
	frappe.db.commit()
