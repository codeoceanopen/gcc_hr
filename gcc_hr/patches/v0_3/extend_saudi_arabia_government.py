# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Phase 5 added Government Submission Type seeding inside the same
countries.saudi_arabia.setup.setup() that earlier patches already ran once.
Re-invokes it (idempotent) so sites migrated before Phase 5 shipped get the
two seeded submission types (Nitaqat Report, GOSI Registration Worksheet)."""

import frappe

from gcc_hr.countries.saudi_arabia.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "Saudi Arabia"):
		return
	setup()
