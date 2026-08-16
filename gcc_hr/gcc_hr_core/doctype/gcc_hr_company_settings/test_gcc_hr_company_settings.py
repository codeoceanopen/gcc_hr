# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

TEST_COMPANY = "_Test GCC Company Settings Co"


class TestGCCHRCompanySettings(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGCS",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			# Saudi Arabia's countries/saudi_arabia/setup.py doesn't exist until Phase 2 --
			# this insert dispatches run_country_setup() and must not raise even so.
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)

	def test_country_change_dispatch_is_a_safe_noop_when_country_module_missing(self):
		doc = frappe.get_doc("GCC HR Company Settings", TEST_COMPANY)
		doc.save(ignore_permissions=True)  # re-triggers on_update/run_country_setup; must not raise
		self.assertEqual(doc.country, "Saudi Arabia")

	def test_currency_fetched_from_company(self):
		doc = frappe.get_doc("GCC HR Company Settings", TEST_COMPANY)
		self.assertEqual(doc.currency, "SAR")

	def test_config_change_is_audited(self):
		before = frappe.db.count("HR Audit Log", {"reference_doctype": "GCC HR Company Settings"})
		doc = frappe.get_doc("GCC HR Company Settings", TEST_COMPANY)
		doc.payroll_frequency = "Bimonthly"
		doc.save(ignore_permissions=True)
		after = frappe.db.count("HR Audit Log", {"reference_doctype": "GCC HR Company Settings"})
		self.assertGreater(after, before)
