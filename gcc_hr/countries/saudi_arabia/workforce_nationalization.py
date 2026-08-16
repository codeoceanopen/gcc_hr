# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Thin re-export so gcc_hr_core/workforce.py's generic country dispatch --
which looks up a submodule literally named `workforce_nationalization`, not
`saudization` (that was this app's own naming choice, not a generic
convention) -- can find Saudi's implementation without gcc_hr_core ever
hardcoding the word "saudization". Saudi's real logic stays in
saudization.py unchanged; see countries/qatar/workforce_nationalization.py
for Qatar's equivalent and ARCHITECTURE.md's "Qatar (Phase 6)" section for
why this shim exists."""

from gcc_hr.countries.saudi_arabia.saudization import (  # noqa: F401
	compute_status,
	get_applicable_target,
	get_workforce_counts,
	recalculate,
	simulate,
)
