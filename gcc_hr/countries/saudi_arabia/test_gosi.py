# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.countries.saudi_arabia.gosi import calculate_for_salary_slip, compute_contribution

TEST_COMPANY = "_Test GCC GOSI Co"


class TestGOSICalculation(FrappeTestCase):
	def test_compute_contribution_applies_seeded_saudi_rates(self):
		result = compute_contribution(
			basic_salary=8000, eligible_allowances=2000, category="Saudi", on_date="2025-01-01"
		)
		self.assertIsNotNone(result)
		self.assertEqual(result["contribution_base"], 10000)
		self.assertEqual(result["employee_contribution"], round(10000 * 9.75 / 100, 2))
		self.assertEqual(result["employer_contribution"], round(10000 * 11.75 / 100, 2))
		self.assertEqual(
			result["total_contribution"], result["employee_contribution"] + result["employer_contribution"]
		)

	def test_compute_contribution_non_saudi_is_employer_only(self):
		result = compute_contribution(
			basic_salary=5000, eligible_allowances=0, category="Non-Saudi", on_date="2025-01-01"
		)
		self.assertEqual(result["employee_contribution"], 0)
		self.assertGreater(result["employer_contribution"], 0)

	def test_compute_contribution_respects_floor_and_ceiling(self):
		below_floor = compute_contribution(
			basic_salary=100, eligible_allowances=0, category="Non-Saudi", on_date="2025-01-01"
		)
		floor = frappe.db.get_value("GOSI Settings", {"applicable_employee_category": "Non-Saudi"}, "contribution_floor")
		self.assertEqual(below_floor["contribution_base"], floor)

		above_ceiling = compute_contribution(
			basic_salary=999999, eligible_allowances=0, category="Saudi", on_date="2025-01-01"
		)
		ceiling = frappe.db.get_value("GOSI Settings", {"applicable_employee_category": "Saudi"}, "contribution_ceiling")
		self.assertEqual(above_ceiling["contribution_base"], ceiling)

	def test_compute_contribution_returns_none_before_any_settings_effective(self):
		self.assertIsNone(compute_contribution(8000, 0, "Saudi", "2000-01-01"))

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "Company", "company_name": TEST_COMPANY, "abbr": "TGGC", "default_currency": "SAR", "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia"}).insert(
				ignore_permissions=True
			)
		cls.employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test GOSI Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)

	def _fake_salary_slip(self, name="FAKE-SLIP-001"):
		return frappe._dict(
			{
				"employee": self.employee.name,
				"name": name,
				"posting_date": "2025-01-31",
				"end_date": "2025-01-31",
				"earnings": [frappe._dict({"salary_component": "Basic", "amount": 8000})],
			}
		)

	def test_calculate_for_salary_slip_skips_when_no_gosi_profile(self):
		self.assertFalse(frappe.db.exists("GOSI Employee Profile", self.employee.name))
		self.assertIsNone(calculate_for_salary_slip(self._fake_salary_slip()))

	def test_calculate_for_salary_slip_skips_when_not_registered(self):
		frappe.get_doc(
			{"doctype": "GOSI Employee Profile", "employee": self.employee.name, "registration_status": "Pending"}
		).insert(ignore_permissions=True)
		try:
			self.assertIsNone(calculate_for_salary_slip(self._fake_salary_slip()))
		finally:
			frappe.delete_doc("GOSI Employee Profile", self.employee.name, force=True, ignore_permissions=True)

	def test_get_gosi_status_summary_counts_by_registration_status(self):
		# Added for the Saudi dashboard's GOSI panel -- no company-wide GOSI
		# aggregate existed before this (only per-employee fields, or a CSV
		# worksheet via government.generate_gosi_registration_summary).
		from gcc_hr.countries.saudi_arabia.gosi import get_gosi_status_summary

		registered = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test GOSI Summary Registered",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)
		frappe.get_doc(
			{
				"doctype": "GOSI Employee Profile",
				"employee": registered.name,
				"registration_status": "Registered",
				"gosi_number": "1111111111",
			}
		).insert(ignore_permissions=True)

		# Deliberately no GOSI Employee Profile for this one -- should count
		# as "Not Registered", same default government.py's CSV worksheet uses.
		frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test GOSI Summary Unregistered",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)

		result = get_gosi_status_summary(TEST_COMPANY)
		self.assertGreaterEqual(result["counts"]["Registered"], 1)
		self.assertGreaterEqual(result["counts"]["Not Registered"], 1)
		self.assertEqual(result["status"], "Needs Review")

	def test_calculate_for_salary_slip_skips_when_suspended(self):
		frappe.get_doc(
			{
				"doctype": "GOSI Employee Profile",
				"employee": self.employee.name,
				"registration_status": "Registered",
				"gosi_number": "1234567890",
				"status": "Suspended",
			}
		).insert(ignore_permissions=True)
		try:
			self.assertIsNone(calculate_for_salary_slip(self._fake_salary_slip()))
		finally:
			frappe.delete_doc("GOSI Employee Profile", self.employee.name, force=True, ignore_permissions=True)
