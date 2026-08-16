# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.countries.saudi_arabia.leave import (
	ANNUAL_LEAVE_TYPE,
	FIVE_YEARS_OR_MORE_DAYS,
	LESS_THAN_5_YEARS_DAYS,
	get_annual_leave_entitlement,
	get_latest_annual_leave_allocation,
)
from gcc_hr.countries.saudi_arabia.rules import check_annual_leave_entitlement

TEST_COMPANY = "_Test GCC Saudi Leave Co"


class TestAnnualLeaveEntitlement(FrappeTestCase):
	def test_entitlement_is_21_days_under_5_years(self):
		self.assertEqual(get_annual_leave_entitlement("2022-01-01", on_date="2024-01-01"), LESS_THAN_5_YEARS_DAYS)

	def test_entitlement_is_30_days_at_5_years(self):
		self.assertEqual(get_annual_leave_entitlement("2019-01-01", on_date="2024-01-02"), FIVE_YEARS_OR_MORE_DAYS)

	def test_entitlement_defaults_to_21_days_without_date_of_joining(self):
		self.assertEqual(get_annual_leave_entitlement(None), LESS_THAN_5_YEARS_DAYS)


class TestCheckAnnualLeaveEntitlement(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGSLC",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("Leave Type", ANNUAL_LEAVE_TYPE):
			frappe.get_doc(
				{
					"doctype": "Leave Type",
					"leave_type_name": ANNUAL_LEAVE_TYPE,
					"max_leaves_allowed": 30,
					"is_carry_forward": 1,
					"allow_encashment": 1,
					"earning_component": "Basic",
				}
			).insert(ignore_permissions=True)

	def _make_employee(self, label, date_of_joining):
		return frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": label,
				"company": TEST_COMPANY,
				"date_of_birth": "1985-01-01",
				"date_of_joining": date_of_joining,
				"gender": "Male",
			}
		).insert(ignore_permissions=True)

	def _make_allocation(self, employee, days):
		allocation = frappe.get_doc(
			{
				"doctype": "Leave Allocation",
				"employee": employee,
				"company": TEST_COMPANY,
				"leave_type": ANNUAL_LEAVE_TYPE,
				"from_date": "2024-01-01",
				"to_date": "2024-12-31",
				"new_leaves_allocated": days,
				"total_leaves_allocated": days,
			}
		)
		allocation.insert(ignore_permissions=True)
		allocation.submit()
		return allocation

	def test_skipped_when_no_allocation_exists(self):
		employee = self._make_employee("Test Leave No Allocation", "2024-01-01")
		result, message, action = check_annual_leave_entitlement(employee.name, None, None)
		self.assertEqual(result, "Skipped")

	def test_failed_when_allocation_below_entitlement(self):
		employee = self._make_employee("Test Leave Under Allocated", "2024-01-01")
		self._make_allocation(employee.name, 10)
		result, message, action = check_annual_leave_entitlement(employee.name, None, None)
		self.assertEqual(result, "Failed")
		self.assertIn("21", message)

	def test_passed_when_allocation_meets_entitlement(self):
		employee = self._make_employee("Test Leave Fully Allocated", "2024-01-01")
		self._make_allocation(employee.name, 21)
		result, message, action = check_annual_leave_entitlement(employee.name, None, None)
		self.assertEqual(result, "Passed")

	def test_get_latest_annual_leave_allocation_returns_most_recent(self):
		employee = self._make_employee("Test Leave Latest Allocation", "2024-01-01")
		self._make_allocation(employee.name, 21)
		latest = get_latest_annual_leave_allocation(employee.name)
		self.assertIsNotNone(latest)
		self.assertEqual(latest["new_leaves_allocated"], 21)
