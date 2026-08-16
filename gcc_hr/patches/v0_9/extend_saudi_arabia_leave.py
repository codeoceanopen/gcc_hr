# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""This phase added the "Saudi Annual Leave" Leave Type (carry-forward +
encashment) and the SA_ANNUAL_LEAVE_ENTITLEMENT compliance rule inside the
same countries.saudi_arabia.setup.setup() that earlier patches already ran
once. Re-invokes it (idempotent) so companies already pointed at Saudi
Arabia before this phase pick up both new records -- same pattern as
patches/v0_2/extend_saudi_arabia_saudization.py."""

import frappe

from gcc_hr.countries.saudi_arabia.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "Saudi Arabia"):
		return
	setup()
