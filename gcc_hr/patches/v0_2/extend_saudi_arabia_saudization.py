# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Phase 4 added Saudization Requirement seeding and per-company
Saudization Profile creation inside the same countries.saudi_arabia.setup
.setup() that earlier patches already ran once. Re-invokes it (idempotent)
and explicitly backfills a Saudization Profile for every company already
pointed at Saudi Arabia, since setup(company=None) only provisions a
profile for the one company passed to it."""

import frappe

from gcc_hr.countries.saudi_arabia.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "Saudi Arabia"):
		return
	setup()

	from gcc_hr.countries.saudi_arabia.saudization import recalculate

	saudi_companies = frappe.get_all("GCC HR Company Settings", filters={"country": "Saudi Arabia"}, pluck="company")
	for company in saudi_companies:
		recalculate(company)
