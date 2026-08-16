# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Covers create_gratuity_rules()'s Kuwait-specific hand-rolled multi-slab,
resignation-reduction rules (mirroring Saudi Arabia's own shape) -- unlike
UAE's create_gratuity_rules() this isn't fixing up hrms's own seeded rows,
just asserting our own rows were created correctly."""

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.countries.kuwait.setup import GRATUITY_RULES, create_gratuity_rules

KUWAIT_GRATUITY_RULE_NAMES = [rule["name"] for rule in GRATUITY_RULES]


class TestKuwaitSetup(FrappeTestCase):
	def test_gratuity_rules_seeded_with_resignation_bands(self):
		create_gratuity_rules()

		expected_names = [
			"Kuwait - Full Award (Termination/Retirement/Contract End)",
			"Kuwait - Resignation 2-5 Years (1/3 Award)",
			"Kuwait - Resignation 5-10 Years (2/3 Award)",
			"Kuwait - Resignation 10+ Years (Full Award)",
		]
		self.assertEqual(sorted(KUWAIT_GRATUITY_RULE_NAMES), sorted(expected_names))

		for name in expected_names:
			self.assertTrue(frappe.db.exists("Gratuity Rule", name), f"{name} should exist (seeded by setup.py)")
			rule = frappe.get_doc("Gratuity Rule", name)
			self.assertEqual(rule.work_experience_calculation_function, "Take Exact Completed Years")
			self.assertTrue(rule.applicable_earnings_component, "applicable_earnings_component should not be empty")
			self.assertEqual(rule.applicable_earnings_component[0].salary_component, "Basic")

	def test_create_gratuity_rules_is_idempotent(self):
		create_gratuity_rules()
		create_gratuity_rules()  # must not raise or duplicate

		for name in KUWAIT_GRATUITY_RULE_NAMES:
			rule = frappe.get_doc("Gratuity Rule", name)
			self.assertEqual(len(rule.applicable_earnings_component), 1)
