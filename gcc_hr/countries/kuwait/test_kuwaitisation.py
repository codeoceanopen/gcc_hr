# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.countries.kuwait.kuwaitisation import (
	compute_status,
	get_applicable_target,
	get_workforce_counts,
	recalculate,
	simulate,
)

TEST_COMPANY = "_Test GCC Kuwaitisation Co"


class TestKuwaitisation(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "Company", "company_name": TEST_COMPANY, "abbr": "TGKZC", "default_currency": "KWD", "country": "Kuwait"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Kuwait"}).insert(
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
		frappe.db.set_value("Kuwait Employee Profile", employee.name, "nationality_status", nationality_status)
		return employee

	def _make_company(self, label):
		"""A dedicated company per test that counts employees -- see
		test_saudization.py's identical helper and ARCHITECTURE.md's
		"Saudization (Phase 4)" section for why."""
		name = f"_Test GCC Kuwaitisation {label}"
		if not frappe.db.exists("Company", name):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": name,
					"abbr": "".join(w[0] for w in label.split())[:5].upper() + "K",
					"default_currency": "KWD",
					"country": "Kuwait",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", name):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": name, "country": "Kuwait"}).insert(
				ignore_permissions=True
			)
		return name

	def test_global_fallback_target_is_seeded(self):
		self.assertEqual(get_applicable_target("_Test GCC Nonexistent Co", None, None), 20.0)

	def test_company_specific_override_takes_priority(self):
		row = frappe.get_doc(
			{
				"doctype": "Kuwaitisation Requirement",
				"company": TEST_COMPANY,
				"target_percentage": 30,
				"effective_from": "2024-01-01",
			}
		)
		row.insert(ignore_permissions=True)
		try:
			self.assertEqual(get_applicable_target(TEST_COMPANY, None, None), 30)
		finally:
			frappe.delete_doc("Kuwaitisation Requirement", row.name, force=True, ignore_permissions=True)
		self.assertEqual(get_applicable_target(TEST_COMPANY, None, None), 20.0)

	def test_activity_and_size_match_beats_global_fallback(self):
		row = frappe.get_doc(
			{
				"doctype": "Kuwaitisation Requirement",
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
			self.assertEqual(get_applicable_target(TEST_COMPANY, "Retail", "Small"), 20.0)
		finally:
			frappe.delete_doc("Kuwaitisation Requirement", row.name, force=True, ignore_permissions=True)

	def test_compute_status_bands(self):
		self.assertEqual(compute_status(25, 20), "Compliant")
		self.assertEqual(compute_status(20, 20), "Compliant")
		self.assertEqual(compute_status(19, 20), "At Risk")
		self.assertEqual(compute_status(18, 20), "At Risk")
		self.assertEqual(compute_status(17, 20), "Non-Compliant")
		self.assertEqual(compute_status(5, None), "Compliant")

	def test_workforce_counts_only_include_active_employees(self):
		company = self._make_company("Workforce Counts")
		self._make_employee("Test Kuwaitisation Active Kuwaiti", "Kuwaiti", status="Active", company=company)
		self._make_employee("Test Kuwaitisation Left Kuwaiti", "Kuwaiti", status="Left", company=company)
		self._make_employee("Test Kuwaitisation Active Non-Kuwaiti", "Non-Kuwaiti", status="Active", company=company)

		counts = get_workforce_counts(company)
		self.assertEqual(counts["employee_count"], 2)
		self.assertEqual(counts["kuwaiti_employee_count"], 1)
		self.assertEqual(counts["non_kuwaiti_employee_count"], 1)

	def test_recalculate_creates_and_updates_profile(self):
		company = self._make_company("Recalculate")
		self._make_employee("Test Recalc Kuwaiti 1", "Kuwaiti", company=company)
		self._make_employee("Test Recalc Kuwaiti 2", "Kuwaiti", company=company)
		self._make_employee("Test Recalc Non-Kuwaiti 1", "Non-Kuwaiti", company=company)

		profile = recalculate(company)
		self.assertEqual(profile.employee_count, 3)
		self.assertEqual(profile.kuwaiti_employee_count, 2)
		self.assertAlmostEqual(profile.kuwaiti_percentage, 66.67, places=1)
		self.assertEqual(profile.target_percentage, 20.0)
		self.assertEqual(profile.compliance_status, "Compliant")
		self.assertIsNotNone(profile.last_calculation)

	def test_simulate_does_not_touch_real_data(self):
		company = self._make_company("Simulate No Touch")
		self._make_employee("Test Simulate Kuwaiti 1", "Kuwaiti", company=company)
		self._make_employee("Test Simulate Non-Kuwaiti 1", "Non-Kuwaiti", company=company)
		before = get_workforce_counts(company)

		result = simulate(company, hire_non_kuwaiti=5)

		after = get_workforce_counts(company)
		self.assertEqual(before, after)
		self.assertEqual(result["projected_non_kuwaiti_employee_count"], before["non_kuwaiti_employee_count"] + 5)
		self.assertLess(result["projected_percentage"], result["current_percentage"])

	def test_simulate_terminating_kuwaiti_employees_worsens_status(self):
		company = self._make_company("Simulate Terminate")
		self._make_employee("Test Simulate Terminate Kuwaiti 1", "Kuwaiti", company=company)
		self._make_employee("Test Simulate Terminate Kuwaiti 2", "Kuwaiti", company=company)
		self._make_employee("Test Simulate Terminate Non-Kuwaiti 1", "Non-Kuwaiti", company=company)

		result = simulate(company, terminate_kuwaiti=1)
		self.assertLess(result["projected_percentage"], result["current_percentage"])

	def test_simulate_counts_never_go_negative(self):
		result = simulate(TEST_COMPANY, terminate_kuwaiti=1000, terminate_non_kuwaiti=1000)
		self.assertEqual(result["projected_kuwaiti_employee_count"], 0)
		self.assertEqual(result["projected_non_kuwaiti_employee_count"], 0)

	def test_recalculate_rejects_company_configured_for_a_different_country(self):
		# Backend enforcement (not just UI visibility): a Kuwait-only doctype
		# must not be usable against a company whose GCC HR Company Settings
		# points at a different country -- see
		# gcc_hr_core.doctype.gcc_hr_company_settings.enforce_company_country.
		company = "_Test GCC Kuwaitisation Wrong Country Co"
		if not frappe.db.exists("Company", company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": company,
					"abbr": "TGKWC",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", company):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": company, "country": "Saudi Arabia"}).insert(
				ignore_permissions=True
			)

		# recalculate() creates/saves a Kuwaitisation Profile, whose own
		# validate() is where the country check lives.
		self.assertRaises(frappe.ValidationError, recalculate, company)
