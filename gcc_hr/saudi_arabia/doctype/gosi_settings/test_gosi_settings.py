# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.saudi_arabia.doctype.gosi_settings.gosi_settings import get_applicable_settings


class TestGOSISettings(FrappeTestCase):
	def test_seeded_settings_exist_for_both_categories(self):
		for category in ("Saudi", "Non-Saudi"):
			self.assertTrue(
				frappe.db.exists("GOSI Settings", {"applicable_employee_category": category}),
				f"No GOSI Settings seeded for {category}",
			)

	def test_effective_from_before_after_date(self):
		row = frappe.get_doc(
			{
				"doctype": "GOSI Settings",
				"applicable_employee_category": "Saudi",
				"effective_from": "2020-01-01",
				"effective_to": "2020-12-31",
				"employee_contribution_rate": 1,
				"employer_contribution_rate": 1,
			}
		)
		row.insert(ignore_permissions=True)
		try:
			self.assertEqual(get_applicable_settings("Saudi", "2020-06-01").name, row.name)
			self.assertIsNone(get_applicable_settings("Saudi", "2019-01-01"))
			# 2021 falls back to whatever open-ended/current row applies (the
			# real seeded 2024-07-01 row, or None if that's also not yet
			# effective) -- just confirm it's not *this* superseded row.
			after = get_applicable_settings("Saudi", "2021-01-01")
			self.assertNotEqual(getattr(after, "name", None), row.name)
		finally:
			frappe.delete_doc("GOSI Settings", row.name, force=True, ignore_permissions=True)

	def test_effective_to_optional_means_open_ended(self):
		self.assertEqual(
			frappe.db.get_value("GOSI Settings", {"applicable_employee_category": "Saudi"}, "effective_to"), None
		)
		result = get_applicable_settings("Saudi", "2099-01-01")
		self.assertIsNotNone(result)  # the open-ended seeded row still applies far in the future
