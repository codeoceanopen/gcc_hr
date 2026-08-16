# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from gcc_hr.gcc_hr_core.compliance_engine.expiry_engine import run_daily_expiry_sweep

TEST_COMPANY = "_Test GCC Document Co"


class TestHRComplianceDocument(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGDC",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("HR Document Type", "Saudi Arabia-Passport"):
			frappe.get_doc(
				{
					"doctype": "HR Document Type",
					"country": "Saudi Arabia",
					"document_type_name": "Passport",
				}
			).insert(ignore_permissions=True)
		cls.employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Document Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Female",
			}
		).insert(ignore_permissions=True)

	def test_status_computed_on_insert(self):
		doc = frappe.get_doc(
			{
				"doctype": "HR Compliance Document",
				"employee": self.employee.name,
				"document_type": "Saudi Arabia-Passport",
				"expiry_date": add_days(today(), 3),
			}
		).insert(ignore_permissions=True)
		self.assertEqual(doc.status, "Expiring Soon")
		self.assertEqual(doc.days_remaining, 3)
		self.assertEqual(doc.country, "Saudi Arabia")

	def test_daily_sweep_corrects_stale_status(self):
		doc = frappe.get_doc(
			{
				"doctype": "HR Compliance Document",
				"employee": self.employee.name,
				"document_type": "Saudi Arabia-Passport",
				"expiry_date": add_days(today(), 3),
			}
		).insert(ignore_permissions=True)

		# simulate time passing without the document being re-saved
		frappe.db.set_value(
			"HR Compliance Document", doc.name, {"status": "Valid", "days_remaining": 400}, update_modified=False
		)

		run_daily_expiry_sweep()

		doc.reload()
		self.assertEqual(doc.status, "Expiring Soon")
		self.assertEqual(doc.days_remaining, 3)
