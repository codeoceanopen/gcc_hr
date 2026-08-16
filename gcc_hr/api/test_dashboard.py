# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.api.dashboard import get_summary


class TestDashboardSummary(FrappeTestCase):
	def test_get_summary_runs_without_error(self):
		# Regression test: frappe.get_all(fields=["...", "count(*) as count"])
		# raises ValidationError on Frappe v16 -- SQL functions must use the
		# {"COUNT": "*", "as": "count"} dict syntax instead.
		frappe.set_user("Administrator")
		result = get_summary()
		self.assertIn("total_employees", result)
		self.assertIn("status_counts", result)
		for status in ("Compliant", "Warning", "Critical", "Blocked"):
			self.assertIn(status, result["status_counts"])
		self.assertIsInstance(result["average_score"], float)

	def test_get_summary_with_company_filter_scopes_counts_and_includes_expiring_breakdown(self):
		# Added for the Saudi Compliance Dashboard (frontend/src/pages/saudi/
		# ComplianceDashboard.vue) -- same aggregation, just scoped to one
		# company, plus a per-document-type breakdown of what's expiring.
		frappe.set_user("Administrator")
		result = get_summary(company="_Test GCC Nonexistent Dashboard Co")
		self.assertEqual(result["total_employees"], 0)
		self.assertEqual(result["documents_expiring_by_type"], [])

	def test_get_summary_includes_compliance_trend_and_recent_critical_issues(self):
		# Added for the Command Center rebuild (frontend/src/pages/Dashboard.vue)
		# -- real historical data (HR Compliance Check) and a unified urgent-
		# items feed (HR Compliance Document + Contract), never fabricated
		# numbers. A company with no history/data yields empty lists, not
		# errors -- that's the correct "nothing to show yet" state.
		frappe.set_user("Administrator")
		result = get_summary(company="_Test GCC Nonexistent Dashboard Co")
		self.assertEqual(result["compliance_trend"], [])
		self.assertEqual(result["recent_critical_issues"], [])

		result = get_summary()
		self.assertIsInstance(result["compliance_trend"], list)
		self.assertIsInstance(result["recent_critical_issues"], list)
		for row in result["compliance_trend"]:
			self.assertIn("month", row)
			self.assertIn("average_score", row)
		for issue in result["recent_critical_issues"]:
			self.assertIn("label", issue)
			self.assertIn("reference", issue)
			self.assertIn("severity", issue)
