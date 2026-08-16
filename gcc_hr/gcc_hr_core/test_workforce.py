# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Proves gcc_hr_core/workforce.py's generic country dispatch (looked up by
the submodule name `workforce_nationalization`, not any specific country's
name -- see that module's docstring and countries/base.py) actually
recalculates every shipped country's workforce-nationalization profile in a
single sweep, using each country's own real implementation via its thin
re-export shim."""

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.gcc_hr_core.workforce import run_daily_workforce_nationalization_recalculation

TEST_SAUDI_COMPANY = "_Test GCC Workforce Saudi Co"
TEST_QATAR_COMPANY = "_Test GCC Workforce Qatar Co"
TEST_UAE_COMPANY = "_Test GCC Workforce UAE Co"
TEST_OMAN_COMPANY = "_Test GCC Workforce Oman Co"
TEST_BAHRAIN_COMPANY = "_Test GCC Workforce Bahrain Co"
TEST_KUWAIT_COMPANY = "_Test GCC Workforce Kuwait Co"


class TestWorkforceDispatch(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		for company, country, abbr, currency in (
			(TEST_SAUDI_COMPANY, "Saudi Arabia", "TGWSC", "SAR"),
			(TEST_QATAR_COMPANY, "Qatar", "TGWQC", "QAR"),
			(TEST_UAE_COMPANY, "United Arab Emirates", "TGWUC", "AED"),
			(TEST_OMAN_COMPANY, "Oman", "TGWOC", "OMR"),
			(TEST_BAHRAIN_COMPANY, "Bahrain", "TGWBC", "BHD"),
			(TEST_KUWAIT_COMPANY, "Kuwait", "TGWKC", "KWD"),
		):
			if not frappe.db.exists("Company", company):
				frappe.get_doc(
					{"doctype": "Company", "company_name": company, "abbr": abbr, "default_currency": currency, "country": country}
				).insert(ignore_permissions=True)
			if not frappe.db.exists("GCC HR Company Settings", company):
				frappe.get_doc({"doctype": "GCC HR Company Settings", "company": company, "country": country}).insert(
					ignore_permissions=True
				)

	def test_daily_sweep_recalculates_all_countries_generically(self):
		frappe.db.delete("Saudization Profile", {"company": TEST_SAUDI_COMPANY})
		frappe.db.delete("Qatarization Profile", {"company": TEST_QATAR_COMPANY})
		frappe.db.delete("Emiratisation Profile", {"company": TEST_UAE_COMPANY})
		frappe.db.delete("Omanisation Profile", {"company": TEST_OMAN_COMPANY})
		frappe.db.delete("Bahrainisation Profile", {"company": TEST_BAHRAIN_COMPANY})
		frappe.db.delete("Kuwaitisation Profile", {"company": TEST_KUWAIT_COMPANY})

		run_daily_workforce_nationalization_recalculation()

		self.assertTrue(frappe.db.exists("Saudization Profile", TEST_SAUDI_COMPANY))
		self.assertTrue(frappe.db.exists("Qatarization Profile", TEST_QATAR_COMPANY))
		self.assertTrue(frappe.db.exists("Emiratisation Profile", TEST_UAE_COMPANY))
		self.assertTrue(frappe.db.exists("Omanisation Profile", TEST_OMAN_COMPANY))
		self.assertTrue(frappe.db.exists("Bahrainisation Profile", TEST_BAHRAIN_COMPANY))
		self.assertTrue(frappe.db.exists("Kuwaitisation Profile", TEST_KUWAIT_COMPANY))
		self.assertIsNotNone(frappe.db.get_value("Saudization Profile", TEST_SAUDI_COMPANY, "last_calculation"))
		self.assertIsNotNone(frappe.db.get_value("Qatarization Profile", TEST_QATAR_COMPANY, "last_calculation"))
		self.assertIsNotNone(frappe.db.get_value("Emiratisation Profile", TEST_UAE_COMPANY, "last_calculation"))
		self.assertIsNotNone(frappe.db.get_value("Omanisation Profile", TEST_OMAN_COMPANY, "last_calculation"))
		self.assertIsNotNone(frappe.db.get_value("Bahrainisation Profile", TEST_BAHRAIN_COMPANY, "last_calculation"))
		self.assertIsNotNone(frappe.db.get_value("Kuwaitisation Profile", TEST_KUWAIT_COMPANY, "last_calculation"))
