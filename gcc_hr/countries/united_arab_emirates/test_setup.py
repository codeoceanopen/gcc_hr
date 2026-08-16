# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Covers create_gratuity_rules()'s reuse-and-fixup of hrms's own regional
UAE Gratuity Rules specifically -- see that function's docstring in
setup.py for the two hrms bugs being worked around."""

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.countries.united_arab_emirates.setup import UAE_GRATUITY_RULE_NAMES, create_gratuity_rules


class TestUAESetup(FrappeTestCase):
	def test_gratuity_rules_reused_from_hrms_and_bugs_fixed_up(self):
		create_gratuity_rules()

		for name in UAE_GRATUITY_RULE_NAMES:
			self.assertTrue(frappe.db.exists("Gratuity Rule", name), f"{name} should exist (seeded by hrms)")
			rule = frappe.get_doc("Gratuity Rule", name)
			self.assertEqual(rule.work_experience_calculation_function, "Take Exact Completed Years")
			self.assertTrue(rule.applicable_earnings_component, "applicable_earnings_component should not be empty")
			self.assertEqual(rule.applicable_earnings_component[0].salary_component, "Basic")

	def test_create_gratuity_rules_is_idempotent(self):
		create_gratuity_rules()
		create_gratuity_rules()  # must not raise or duplicate the fixup

		for name in UAE_GRATUITY_RULE_NAMES:
			rule = frappe.get_doc("Gratuity Rule", name)
			self.assertEqual(len(rule.applicable_earnings_component), 1)
