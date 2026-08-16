# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.gcc_hr_core.audit import log_action


class TestHRAuditLog(FrappeTestCase):
	def test_no_role_can_create_or_write_audit_log(self):
		meta = frappe.get_meta("HR Audit Log")
		for perm in meta.permissions:
			self.assertFalse(perm.create, f"{perm.role} should not have create on HR Audit Log")
			self.assertFalse(perm.write, f"{perm.role} should not have write on HR Audit Log")
			self.assertFalse(perm.delete, f"{perm.role} should not have delete on HR Audit Log")

	def test_log_action_inserts_despite_no_create_permission(self):
		before = frappe.db.count("HR Audit Log")
		log_action(action="Unit Test Action", reason="test_log_action_inserts_despite_no_create_permission")
		self.assertEqual(frappe.db.count("HR Audit Log"), before + 1)
