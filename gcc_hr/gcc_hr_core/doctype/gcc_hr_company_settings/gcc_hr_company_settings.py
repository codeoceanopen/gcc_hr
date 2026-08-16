# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GCCHRCompanySettings(Document):
	def validate(self):
		if self.country and not frappe.db.get_value("HR Country Settings", self.country, "is_active"):
			frappe.msgprint(
				_(
					"{0}'s localization module is not marked Active on HR Country Settings. "
					"Compliance/document features for this company may be incomplete."
				).format(frappe.bold(self.country)),
				indicator="orange",
				alert=True,
			)


def get_company_settings(company: str) -> dict | None:
	"""Cached lookup used by the compliance engine and reports."""
	if not company:
		return None
	return frappe.get_cached_doc("GCC HR Company Settings", company).as_dict() if frappe.db.exists(
		"GCC HR Company Settings", company
	) else None


def get_company_country(company: str) -> str | None:
	"""Canonical company -> country resolver. Returns the HR Country Settings
	name (== country name, since that doctype is autonamed field:country), or
	None if the company has no GCC HR Company Settings configured yet. This
	is the single source of truth other call sites should use instead of
	repeating frappe.db.get_value("GCC HR Company Settings", company, "country")."""
	if not company:
		return None
	return frappe.db.get_value("GCC HR Company Settings", company, "country")


def enforce_company_country(company: str, expected_country: str):
	"""Raise if `company`'s configured country isn't `expected_country`. Every
	country-specific doctype/API must call this -- UI visibility alone is not
	security, and nothing previously stopped e.g. a Qatar company from getting
	a Saudization Profile."""
	actual = get_company_country(company)
	if actual != expected_country:
		frappe.throw(
			_("Company {0} is configured for {1}, not {2}.").format(
				frappe.bold(company), actual or _("no country"), expected_country
			),
			frappe.ValidationError,
		)


def run_country_setup(doc, method=None):
	"""doc_events["GCC HR Company Settings"]["on_update"] -- dispatch to the
	country package's setup() the same way hrms/overrides/company.py dispatches
	to hrms.regional.<country>.setup.setup() on Company.on_update, just keyed
	off this doctype's own `country` field. No-op for countries that don't
	implement countries.<country>.setup yet (e.g. Qatar in Phase 1-4)."""
	before = doc.get_doc_before_save()
	if before and before.country == doc.country:
		return

	from gcc_hr.countries import get_country_attr

	# HR Country Settings is autonamed field:country, so doc.country (the
	# Link value) already *is* the country name -- no extra lookup needed.
	setup_fn = get_country_attr(doc.country, "setup", "setup") if doc.country else None
	if setup_fn:
		setup_fn(doc.company)
