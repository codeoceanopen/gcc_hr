# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.gcc_hr_core.payroll import sync_country_payroll, validate_payroll_compliance

TEST_COMPANY = "_Test GCC Core Payroll Co"


def _stub_link_row(doctype: str, name: str, **fields):
	"""Create a minimal, real row for `doctype`/`name` via db_insert() (skips
	validate()/business logic entirely) purely so a Link field pointing at
	it passes Frappe's `_validate_links()` existence check. Salary Slip and
	Payroll Entry both have deep ERPNext payroll prerequisites (Salary
	Structure, Holiday List, ...) that are orthogonal to what these tests
	verify -- see CONTRIBUTING.md."""
	doc = frappe.get_doc({"doctype": doctype, "docstatus": 0, **fields})
	doc.name = name
	doc.db_insert()
	return doc


class TestCorePayroll(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "Company", "company_name": TEST_COMPANY, "abbr": "TGCPC", "default_currency": "SAR", "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia", "payroll_compliance_required": 1}
			).insert(ignore_permissions=True)

	def _make_employee(self, label):
		return frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": label,
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)

	def test_sync_country_payroll_dispatches_to_saudi_gosi_when_registered(self):
		employee = self._make_employee("Test Sync Payroll Employee")
		frappe.get_doc(
			{
				"doctype": "GOSI Employee Profile",
				"employee": employee.name,
				"registration_status": "Registered",
				"gosi_number": "1112223334",
			}
		).insert(ignore_permissions=True)

		_stub_link_row(
			"Salary Slip",
			"FAKE-SLIP-SYNC-001",
			employee=employee.name,
			employee_name=employee.employee_name,
			company=TEST_COMPANY,
			posting_date="2025-01-31",
			currency="SAR",
		)
		fake_slip = frappe._dict(
			{
				"employee": employee.name,
				"name": "FAKE-SLIP-SYNC-001",
				"posting_date": "2025-01-31",
				"end_date": "2025-01-31",
				"earnings": [frappe._dict({"salary_component": "Basic", "amount": 6000})],
			}
		)
		sync_country_payroll(fake_slip)
		self.assertTrue(frappe.db.exists("GOSI Payroll Calculation", {"salary_slip": "FAKE-SLIP-SYNC-001"}))

	def test_sync_country_payroll_is_a_noop_without_a_country(self):
		fake_slip = frappe._dict({"employee": "NON-EXISTENT-EMPLOYEE", "name": "FAKE-SLIP-002"})
		sync_country_payroll(fake_slip)  # must not raise
		self.assertFalse(frappe.db.exists("GOSI Payroll Calculation", {"salary_slip": "FAKE-SLIP-002"}))

	def test_validate_payroll_compliance_creates_check_and_blocks_on_critical(self):
		employee = self._make_employee("Test Payroll Compliance Employee")
		_stub_link_row("Payroll Entry", "FAKE-PE-001", company=TEST_COMPANY, posting_date="2025-01-31")
		fake_payroll_entry = frappe._dict(
			{
				"name": "FAKE-PE-001",
				"company": TEST_COMPANY,
				"employees": [frappe._dict({"employee": employee.name})],
			}
		)
		with self.assertRaises(frappe.ValidationError):
			validate_payroll_compliance(fake_payroll_entry)

		pcc_name = frappe.db.exists("Payroll Compliance Check", {"payroll_entry": "FAKE-PE-001"})
		self.assertTrue(pcc_name)
		pcc = frappe.get_doc("Payroll Compliance Check", pcc_name)
		self.assertEqual(pcc.status, "Blocked")
		self.assertGreater(pcc.critical, 0)
		self.assertEqual(len(pcc.employees), 1)

	def test_validate_payroll_compliance_does_not_block_when_not_required(self):
		frappe.db.set_value("GCC HR Company Settings", TEST_COMPANY, "payroll_compliance_required", 0)
		try:
			employee = self._make_employee("Test Payroll Compliance Not Required")
			_stub_link_row("Payroll Entry", "FAKE-PE-002", company=TEST_COMPANY, posting_date="2025-01-31")
			fake_payroll_entry = frappe._dict(
				{
					"name": "FAKE-PE-002",
					"company": TEST_COMPANY,
					"employees": [frappe._dict({"employee": employee.name})],
				}
			)
			validate_payroll_compliance(fake_payroll_entry)  # must not raise
			pcc_name = frappe.db.exists("Payroll Compliance Check", {"payroll_entry": "FAKE-PE-002"})
			self.assertTrue(pcc_name)
			self.assertEqual(frappe.db.get_value("Payroll Compliance Check", pcc_name, "status"), "Blocked")
		finally:
			frappe.db.set_value("GCC HR Company Settings", TEST_COMPANY, "payroll_compliance_required", 1)

	def test_validate_payroll_compliance_noop_for_unconfigured_company(self):
		unconfigured_company = "_Test GCC Unconfigured Co"
		if not frappe.db.exists("Company", unconfigured_company):
			frappe.get_doc(
				{"doctype": "Company", "company_name": unconfigured_company, "abbr": "TGUC", "default_currency": "USD"}
			).insert(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("GCC HR Company Settings", unconfigured_company))

		fake_payroll_entry = frappe._dict({"name": "FAKE-PE-003", "company": unconfigured_company, "employees": []})
		validate_payroll_compliance(fake_payroll_entry)  # must not raise; company has no GCC HR Company Settings
