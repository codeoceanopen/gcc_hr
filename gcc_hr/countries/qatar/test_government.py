# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import csv
import io

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.countries.qatar.government import (
	generate_qatarization_report,
	generate_wps_report,
	validate_qatarization_report,
	validate_wps_report,
)
from gcc_hr.countries.qatar.qatarization import recalculate

TEST_COMPANY = "_Test GCC Qatar Government Co"


class TestQatarGovernment(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGQGZ",
					"default_currency": "QAR",
					"country": "Qatar",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Qatar"}
			).insert(ignore_permissions=True)

	def test_generate_qatarization_report_reflects_qatarization_profile(self):
		recalculate(TEST_COMPANY)
		result = generate_qatarization_report(TEST_COMPANY)
		self.assertEqual(result["content_type"], "text/csv")
		rows = list(csv.reader(io.StringIO(result["content"])))
		self.assertEqual(rows[0][0], "Company")
		self.assertEqual(rows[1][0], TEST_COMPANY)

	def test_generate_qatarization_report_fails_without_profile(self):
		with self.assertRaises(frappe.ValidationError):
			generate_qatarization_report("_Test GCC Nonexistent Co")

	def test_validate_qatarization_report_fails_without_profile(self):
		errors = validate_qatarization_report("_Test GCC Nonexistent Co")
		self.assertTrue(errors)

	def test_validate_qatarization_report_passes_after_recalculate(self):
		recalculate(TEST_COMPANY)
		errors = validate_qatarization_report(TEST_COMPANY)
		self.assertEqual(errors, [])

	def test_generate_wps_report_lists_active_employees(self):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test QAT Gov Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		result = generate_wps_report(TEST_COMPANY)
		self.assertEqual(result["content_type"], "text/csv")
		rows = list(csv.reader(io.StringIO(result["content"])))
		self.assertIn(employee.name, [r[0] for r in rows[1:]])

	def test_validate_wps_report_fails_without_company_settings(self):
		errors = validate_wps_report("_Test GCC Nonexistent Co")
		self.assertTrue(errors)

	def test_validate_wps_report_passes_for_configured_company(self):
		errors = validate_wps_report(TEST_COMPANY)
		self.assertEqual(errors, [])
