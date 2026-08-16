# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHRCountrySettings(FrappeTestCase):
	def test_gcc_countries_seeded_by_after_install(self):
		for country in (
			"Saudi Arabia",
			"Qatar",
			"United Arab Emirates",
			"Oman",
			"Bahrain",
			"Kuwait",
		):
			self.assertTrue(frappe.db.exists("HR Country Settings", country), f"{country} not seeded")

	def test_non_gcc_country_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "HR Country Settings",
					"country": "India",
					"currency": "INR",
				}
			).insert(ignore_permissions=True)

	def test_only_countries_with_seeded_rules_have_compliance_engine_enabled(self):
		# Saudi Arabia's rules are seeded by gcc_hr.countries.saudi_arabia.setup
		# (Phase 2), Qatar's by gcc_hr.countries.qatar.setup (Phase 6),
		# UAE's by gcc_hr.countries.united_arab_emirates.setup (Phase 7),
		# Oman's by gcc_hr.countries.oman.setup (Phase 8), Bahrain's by
		# gcc_hr.countries.bahrain.setup (Phase 9), and Kuwait's by
		# gcc_hr.countries.kuwait.setup (Phase 10) -- all six GCC countries
		# now have the compliance engine enabled, each of which flips this on.
		for country in ("Saudi Arabia", "Qatar", "United Arab Emirates", "Oman", "Bahrain", "Kuwait"):
			self.assertEqual(
				frappe.db.get_value("HR Country Settings", country, "compliance_engine_enabled"),
				1,
				f"{country} should have the compliance engine enabled",
			)
