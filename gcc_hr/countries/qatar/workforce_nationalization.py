# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Thin re-export so gcc_hr_core/workforce.py's generic country dispatch can
find Qatar's implementation without core ever hardcoding "qatarization" --
see countries/saudi_arabia/workforce_nationalization.py for the same shim on
Saudi's side, and countries/base.py for why this split exists."""

from gcc_hr.countries.qatar.qatarization import (  # noqa: F401
	compute_status,
	get_applicable_target,
	get_workforce_counts,
	recalculate,
	simulate,
)
