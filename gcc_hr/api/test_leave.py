# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.api.leave import get_leave_summary

TEST_COMPANY = "_Test GCC Leave API Co"


class TestLeaveAPI(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGLAC",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)

	def test_get_leave_summary_returns_a_list(self):
		frappe.set_user("Administrator")
		result = get_leave_summary(TEST_COMPANY)
		self.assertIsInstance(result, list)

	def test_get_leave_summary_rejects_wrong_country_company(self):
		frappe.set_user("Administrator")
		other_company = "_Test GCC Leave API Wrong Country Co"
		if not frappe.db.exists("Company", other_company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": other_company,
					"abbr": "TGLAW",
					"default_currency": "QAR",
					"country": "Qatar",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", other_company):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": other_company, "country": "Qatar"}).insert(
				ignore_permissions=True
			)

		self.assertRaises(frappe.ValidationError, get_leave_summary, other_company)
