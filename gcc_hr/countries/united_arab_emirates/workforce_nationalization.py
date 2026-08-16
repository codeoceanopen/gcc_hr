# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Thin re-export so gcc_hr_core/workforce.py's generic country dispatch can
find UAE's implementation without core ever hardcoding "emiratisation" --
see countries/saudi_arabia/workforce_nationalization.py and
countries/qatar/workforce_nationalization.py for the same shim on the other
two countries, and countries/base.py for why this split exists."""

from gcc_hr.countries.united_arab_emirates.emiratisation import (  # noqa: F401
	compute_status,
	get_applicable_target,
	get_workforce_counts,
	recalculate,
	simulate,
)
