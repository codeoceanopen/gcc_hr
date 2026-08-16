# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import csv
import io

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.countries.bahrain.government import (
	generate_bahrainisation_report,
	generate_sio_registration_summary,
	validate_bahrainisation_report,
	validate_sio_registration_summary,
)
from gcc_hr.countries.bahrain.bahrainisation import recalculate

TEST_COMPANY = "_Test GCC Bahrain Government Co"


class TestBahrainGovernment(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGBGZ",
					"default_currency": "BHD",
					"country": "Bahrain",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Bahrain"}).insert(
				ignore_permissions=True
			)

	def test_generate_bahrainisation_report_reflects_bahrainisation_profile(self):
		recalculate(TEST_COMPANY)
		result = generate_bahrainisation_report(TEST_COMPANY)
		self.assertEqual(result["content_type"], "text/csv")
		rows = list(csv.reader(io.StringIO(result["content"])))
		self.assertEqual(rows[0][0], "Company")
		self.assertEqual(rows[1][0], TEST_COMPANY)

	def test_generate_bahrainisation_report_fails_without_profile(self):
		with self.assertRaises(frappe.ValidationError):
			generate_bahrainisation_report("_Test GCC Nonexistent Co")

	def test_validate_bahrainisation_report_fails_without_profile(self):
		errors = validate_bahrainisation_report("_Test GCC Nonexistent Co")
		self.assertTrue(errors)

	def test_validate_bahrainisation_report_passes_after_recalculate(self):
		recalculate(TEST_COMPANY)
		errors = validate_bahrainisation_report(TEST_COMPANY)
		self.assertEqual(errors, [])

	def test_generate_sio_registration_summary_lists_active_employees(self):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Bahrain Gov Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		result = generate_sio_registration_summary(TEST_COMPANY)
		self.assertEqual(result["content_type"], "text/csv")
		rows = list(csv.reader(io.StringIO(result["content"])))
		self.assertIn(employee.name, [r[0] for r in rows[1:]])

	def test_validate_sio_registration_summary_fails_without_company_settings(self):
		errors = validate_sio_registration_summary("_Test GCC Nonexistent Co")
		self.assertTrue(errors)

	def test_validate_sio_registration_summary_passes_for_configured_company(self):
		errors = validate_sio_registration_summary(TEST_COMPANY)
		self.assertEqual(errors, [])
