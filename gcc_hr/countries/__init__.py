# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Country plugin dispatcher.

Nothing in gcc_hr.gcc_hr_core (or any other country package) ever imports a
specific country's package directly -- everything goes through
get_country_module() so that adding a new country is purely additive.
Mirrors hrms/overrides/company.py's `f"hrms.regional.{scrub(country)}..."`
dispatch pattern, just keyed off GCC HR Company Settings.country instead of
Company.country, and used for the whole country interface, not just tax
hooks.
"""

import frappe


def get_country_module(country: str, submodule: str):
	"""Return gcc_hr.countries.<scrubbed country>.<submodule>, or None if that
	country package/submodule doesn't exist yet (e.g. Qatar in Phase 1)."""
	if not country:
		return None
	module_name = f"gcc_hr.countries.{frappe.scrub(country)}.{submodule}"
	try:
		return frappe.get_module(module_name)
	except ImportError:
		return None


def get_country_attr(country: str, submodule: str, attr: str):
	"""Convenience: get_country_module(...).<attr>, or None if either the
	module or the attribute is missing."""
	module = get_country_module(country, submodule)
	if module is None:
		return None
	return getattr(module, attr, None)
