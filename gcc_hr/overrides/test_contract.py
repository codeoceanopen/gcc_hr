# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

TEST_COMPANY = "_Test GCC Contract Co"


class TestContractOverride(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGCC",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		cls.employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Contract Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)

	def test_total_salary_computed_for_employee_contracts(self):
		contract = frappe.get_doc(
			{
				"doctype": "Contract",
				"party_type": "Employee",
				"party_name": self.employee.name,
				"start_date": "2026-01-01",
				"end_date": "2028-01-01",
				"contract_terms": "Test contract terms.",
				"gcc_basic_salary": 5000,
				"gcc_housing_allowance": 1500,
				"gcc_transport_allowance": 300,
				"gcc_other_allowances": 200,
			}
		).insert(ignore_permissions=True)
		self.assertEqual(contract.gcc_total_salary, 7000)

	def test_total_salary_untouched_for_non_employee_contracts(self):
		contract = frappe.get_doc(
			{
				"doctype": "Contract",
				"party_type": "Customer",
				"party_name": "Administrator",  # placeholder party_user isn't needed for this check
				"start_date": "2026-01-01",
				"contract_terms": "Non-employee contract.",
			}
		)
		contract.party_name = None  # Customer party_name requires a real Customer; skip if unavailable
		contract.gcc_basic_salary = 1000
		from gcc_hr.overrides.contract import compute_total_salary

		compute_total_salary(contract)
		self.assertIsNone(contract.gcc_total_salary)  # untouched for non-Employee contracts, not zeroed
