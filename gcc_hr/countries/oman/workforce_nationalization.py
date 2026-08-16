# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Thin re-export so gcc_hr_core/workforce.py's generic country dispatch can
find Oman's implementation without core ever hardcoding "omanisation" --
see countries/base.py for the documented contract."""

from gcc_hr.countries.oman.omanisation import (  # noqa: F401
	compute_status,
	get_applicable_target,
	get_workforce_counts,
	recalculate,
	simulate,
)
