# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.countries.oman.omanisation import (
	compute_status,
	get_applicable_target,
	get_workforce_counts,
	recalculate,
	simulate,
)

TEST_COMPANY = "_Test GCC Omanisation Co"


class TestOmanisation(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "Company", "company_name": TEST_COMPANY, "abbr": "TGOZC", "default_currency": "OMR", "country": "Oman"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Oman"}).insert(
				ignore_permissions=True
			)

	def _make_employee(self, label, nationality_status, status="Active", company=TEST_COMPANY):
		fields = {
			"doctype": "Employee",
			"first_name": label,
			"company": company,
			"date_of_birth": "1990-01-01",
			"date_of_joining": "2024-01-01",
			"gender": "Male",
			"status": status,
		}
		if status != "Active":
			fields["relieving_date"] = "2025-01-01"
		employee = frappe.get_doc(fields).insert(ignore_permissions=True)
		frappe.db.set_value("Oman Employee Profile", employee.name, "nationality_status", nationality_status)
		return employee

	def _make_company(self, label):
		"""A dedicated company per test that counts employees -- see
		test_saudization.py's identical helper and ARCHITECTURE.md's
		"Saudization (Phase 4)" section for why."""
		name = f"_Test GCC Omanisation {label}"
		if not frappe.db.exists("Company", name):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": name,
					"abbr": "".join(w[0] for w in label.split())[:5].upper() + "O",
					"default_currency": "OMR",
					"country": "Oman",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", name):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": name, "country": "Oman"}).insert(
				ignore_permissions=True
			)
		return name

	def test_global_fallback_target_is_seeded(self):
		self.assertEqual(get_applicable_target("_Test GCC Nonexistent Co", None, None), 15.0)

	def test_company_specific_override_takes_priority(self):
		row = frappe.get_doc(
			{
				"doctype": "Omanisation Requirement",
				"company": TEST_COMPANY,
				"target_percentage": 30,
				"effective_from": "2024-01-01",
			}
		)
		row.insert(ignore_permissions=True)
		try:
			self.assertEqual(get_applicable_target(TEST_COMPANY, None, None), 30)
		finally:
			frappe.delete_doc("Omanisation Requirement", row.name, force=True, ignore_permissions=True)
		self.assertEqual(get_applicable_target(TEST_COMPANY, None, None), 15.0)

	def test_activity_and_size_match_beats_global_fallback(self):
		row = frappe.get_doc(
			{
				"doctype": "Omanisation Requirement",
				"company": "",
				"activity": "Banking",
				"business_size": "Large",
				"target_percentage": 40,
				"effective_from": "2024-01-01",
			}
		)
		row.insert(ignore_permissions=True)
		try:
			self.assertEqual(get_applicable_target(TEST_COMPANY, "Banking", "Large"), 40)
			self.assertEqual(get_applicable_target(TEST_COMPANY, "Retail", "Small"), 15.0)
		finally:
			frappe.delete_doc("Omanisation Requirement", row.name, force=True, ignore_permissions=True)

	def test_compute_status_bands(self):
		self.assertEqual(compute_status(20, 15), "Compliant")
		self.assertEqual(compute_status(15, 15), "Compliant")
		self.assertEqual(compute_status(14, 15), "At Risk")
		self.assertEqual(compute_status(13, 15), "At Risk")
		self.assertEqual(compute_status(12, 15), "Non-Compliant")
		self.assertEqual(compute_status(5, None), "Compliant")

	def test_workforce_counts_only_include_active_employees(self):
		company = self._make_company("Workforce Counts")
		self._make_employee("Test Omanisation Active Omani", "Omani", status="Active", company=company)
		self._make_employee("Test Omanisation Left Omani", "Omani", status="Left", company=company)
		self._make_employee("Test Omanisation Active Non-Omani", "Non-Omani", status="Active", company=company)

		counts = get_workforce_counts(company)
		self.assertEqual(counts["employee_count"], 2)
		self.assertEqual(counts["omani_employee_count"], 1)
		self.assertEqual(counts["non_omani_employee_count"], 1)

	def test_recalculate_creates_and_updates_profile(self):
		company = self._make_company("Recalculate")
		self._make_employee("Test Recalc Omani 1", "Omani", company=company)
		self._make_employee("Test Recalc Omani 2", "Omani", company=company)
		self._make_employee("Test Recalc Non-Omani 1", "Non-Omani", company=company)

		profile = recalculate(company)
		self.assertEqual(profile.employee_count, 3)
		self.assertEqual(profile.omani_employee_count, 2)
		self.assertAlmostEqual(profile.omani_percentage, 66.67, places=1)
		self.assertEqual(profile.target_percentage, 15.0)
		self.assertEqual(profile.compliance_status, "Compliant")
		self.assertIsNotNone(profile.last_calculation)

	def test_simulate_does_not_touch_real_data(self):
		company = self._make_company("Simulate No Touch")
		self._make_employee("Test Simulate Omani 1", "Omani", company=company)
		self._make_employee("Test Simulate Non-Omani 1", "Non-Omani", company=company)
		before = get_workforce_counts(company)

		result = simulate(company, hire_non_omani=5)

		after = get_workforce_counts(company)
		self.assertEqual(before, after)
		self.assertEqual(result["projected_non_omani_employee_count"], before["non_omani_employee_count"] + 5)
		self.assertLess(result["projected_percentage"], result["current_percentage"])

	def test_simulate_terminating_omani_employees_worsens_status(self):
		company = self._make_company("Simulate Terminate")
		self._make_employee("Test Simulate Terminate Omani 1", "Omani", company=company)
		self._make_employee("Test Simulate Terminate Omani 2", "Omani", company=company)
		self._make_employee("Test Simulate Terminate Non-Omani 1", "Non-Omani", company=company)

		result = simulate(company, terminate_omani=1)
		self.assertLess(result["projected_percentage"], result["current_percentage"])

	def test_simulate_counts_never_go_negative(self):
		result = simulate(TEST_COMPANY, terminate_omani=1000, terminate_non_omani=1000)
		self.assertEqual(result["projected_omani_employee_count"], 0)
		self.assertEqual(result["projected_non_omani_employee_count"], 0)

	def test_omanisation_profile_rejects_non_oman_company(self):
		# UI visibility is not security -- a company configured for a
		# different country (e.g. Saudi Arabia) must not be able to get an
		# Omanisation Profile, regardless of what the frontend shows.
		other_company = "_Test GCC Non-Oman Co"
		if not frappe.db.exists("Company", other_company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": other_company,
					"abbr": "TGNOC",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", other_company):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": other_company, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc({"doctype": "Omanisation Profile", "company": other_company}).insert(
				ignore_permissions=True
			)
