# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Phase 3 added new Saudi compliance rules (contract-active,
contract-vs-payroll salary match, GOSI registered), Gratuity Rule seeds
(EOSB), and GOSI Settings seeds -- all inside the same
countries.saudi_arabia.setup.setup() that v0_0.setup_saudi_arabia already
ran once. Frappe patches don't re-run just because the function they call
changed, so this re-invokes setup() (idempotent) to backfill the additions
for any site that already applied v0_0."""

import frappe

from gcc_hr.countries.saudi_arabia.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "Saudi Arabia"):
		return
	setup()
