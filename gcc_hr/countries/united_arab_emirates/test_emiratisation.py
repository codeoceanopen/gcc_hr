# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.countries.united_arab_emirates.emiratisation import (
	compute_status,
	get_applicable_target,
	get_workforce_counts,
	recalculate,
	simulate,
)

TEST_COMPANY = "_Test GCC Emiratisation Co"


class TestEmiratisation(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "Company", "company_name": TEST_COMPANY, "abbr": "TGEZC", "default_currency": "AED", "country": "United Arab Emirates"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "United Arab Emirates"}
			).insert(ignore_permissions=True)

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
			fields["relieving_date"] = "2025-01-01"  # required by Employee.validate_status() for non-Active
		employee = frappe.get_doc(fields).insert(ignore_permissions=True)
		frappe.db.set_value("UAE Employee Profile", employee.name, "nationality_status", nationality_status)
		return employee

	def _make_company(self, label):
		"""A dedicated company per test that counts employees -- see
		test_saudization.py's identical helper and ARCHITECTURE.md's
		"Saudization (Phase 4)" section for why: FrappeTestCase only rolls
		back once at class teardown, not between test methods."""
		name = f"_Test GCC Emiratisation {label}"
		if not frappe.db.exists("Company", name):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": name,
					"abbr": "".join(w[0] for w in label.split())[:5].upper() + "E",
					"default_currency": "AED",
					"country": "United Arab Emirates",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", name):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": name, "country": "United Arab Emirates"}).insert(
				ignore_permissions=True
			)
		return name

	def test_global_fallback_target_is_seeded(self):
		self.assertEqual(get_applicable_target("_Test GCC Nonexistent Co", None, None), 10.0)

	def test_company_specific_override_takes_priority(self):
		row = frappe.get_doc(
			{
				"doctype": "Emiratisation Requirement",
				"company": TEST_COMPANY,
				"target_percentage": 25,
				"effective_from": "2024-01-01",
			}
		)
		row.insert(ignore_permissions=True)
		try:
			self.assertEqual(get_applicable_target(TEST_COMPANY, None, None), 25)
		finally:
			frappe.delete_doc("Emiratisation Requirement", row.name, force=True, ignore_permissions=True)
		self.assertEqual(get_applicable_target(TEST_COMPANY, None, None), 10.0)

	def test_activity_and_size_match_beats_global_fallback(self):
		row = frappe.get_doc(
			{
				"doctype": "Emiratisation Requirement",
				# Explicit "" -- see setup.py's create_emiratisation_requirement()
				# note on Frappe's company-field default-injection footgun.
				"company": "",
				"activity": "Construction",
				"business_size": "Large",
				"target_percentage": 15,
				"effective_from": "2024-01-01",
			}
		)
		row.insert(ignore_permissions=True)
		try:
			self.assertEqual(get_applicable_target(TEST_COMPANY, "Construction", "Large"), 15)
			self.assertEqual(get_applicable_target(TEST_COMPANY, "Retail", "Small"), 10.0)
		finally:
			frappe.delete_doc("Emiratisation Requirement", row.name, force=True, ignore_permissions=True)

	def test_compute_status_bands(self):
		self.assertEqual(compute_status(15, 10), "Compliant")
		self.assertEqual(compute_status(10, 10), "Compliant")
		self.assertEqual(compute_status(9, 10), "At Risk")
		self.assertEqual(compute_status(8, 10), "At Risk")
		self.assertEqual(compute_status(7, 10), "Non-Compliant")
		self.assertEqual(compute_status(5, None), "Compliant")

	def test_workforce_counts_only_include_active_employees(self):
		company = self._make_company("Workforce Counts")
		self._make_employee("Test Emiratisation Active Emirati", "Emirati", status="Active", company=company)
		self._make_employee("Test Emiratisation Left Emirati", "Emirati", status="Left", company=company)
		self._make_employee("Test Emiratisation Active Non-Emirati", "Non-Emirati", status="Active", company=company)

		counts = get_workforce_counts(company)
		self.assertEqual(counts["employee_count"], 2)
		self.assertEqual(counts["emirati_employee_count"], 1)
		self.assertEqual(counts["non_emirati_employee_count"], 1)

	def test_recalculate_creates_and_updates_profile(self):
		company = self._make_company("Recalculate")
		self._make_employee("Test Recalc Emirati 1", "Emirati", company=company)
		self._make_employee("Test Recalc Emirati 2", "Emirati", company=company)
		self._make_employee("Test Recalc Non-Emirati 1", "Non-Emirati", company=company)

		profile = recalculate(company)
		self.assertEqual(profile.employee_count, 3)
		self.assertEqual(profile.emirati_employee_count, 2)
		self.assertAlmostEqual(profile.emirati_percentage, 66.67, places=1)
		self.assertEqual(profile.target_percentage, 10.0)
		self.assertEqual(profile.compliance_status, "Compliant")
		self.assertIsNotNone(profile.last_calculation)

	def test_simulate_does_not_touch_real_data(self):
		company = self._make_company("Simulate No Touch")
		self._make_employee("Test Simulate Emirati 1", "Emirati", company=company)
		self._make_employee("Test Simulate Non-Emirati 1", "Non-Emirati", company=company)
		before = get_workforce_counts(company)

		result = simulate(company, hire_non_emirati=5)

		after = get_workforce_counts(company)
		self.assertEqual(before, after)
		self.assertEqual(result["projected_non_emirati_employee_count"], before["non_emirati_employee_count"] + 5)
		self.assertLess(result["projected_percentage"], result["current_percentage"])

	def test_simulate_terminating_emirati_employees_worsens_status(self):
		company = self._make_company("Simulate Terminate")
		self._make_employee("Test Simulate Terminate Emirati 1", "Emirati", company=company)
		self._make_employee("Test Simulate Terminate Emirati 2", "Emirati", company=company)
		self._make_employee("Test Simulate Terminate Non-Emirati 1", "Non-Emirati", company=company)

		result = simulate(company, terminate_emirati=1)
		self.assertLess(result["projected_percentage"], result["current_percentage"])

	def test_simulate_counts_never_go_negative(self):
		result = simulate(TEST_COMPANY, terminate_emirati=1000, terminate_non_emirati=1000)
		self.assertEqual(result["projected_emirati_employee_count"], 0)
		self.assertEqual(result["projected_non_emirati_employee_count"], 0)

	def test_emiratisation_profile_rejects_non_uae_company(self):
		# Backend enforcement (not just UI visibility): an Emiratisation
		# Profile must not be usable against a company whose GCC HR Company
		# Settings points at a different country -- see
		# gcc_hr_core.doctype.gcc_hr_company_settings.enforce_company_country.
		other_company = "_Test GCC Non-UAE Co"
		if not frappe.db.exists("Company", other_company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": other_company,
					"abbr": "TGNUC",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", other_company):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": other_company, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc({"doctype": "Emiratisation Profile", "company": other_company}).insert(
				ignore_permissions=True
			)
