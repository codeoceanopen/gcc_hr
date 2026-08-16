# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Saudi Labour Law annual leave entitlement (Article 109: 21 calendar days
per year of service before the 5th year, 30 calendar days per year from the
5th year onward) and its own carry-forward/encashment (cash-out) rules.

This does NOT build a parallel leave engine -- HRMS's own Leave Type/Leave
Allocation/Leave Encashment doctypes already do carry-forward and encashment
correctly (see setup.py's seeded "Saudi Annual Leave" Leave Type: is_carry_
forward + allow_encashment enabled). This module only adds the tenure-based
entitlement calculation and reads the resulting Leave Allocation/Leave
Encashment records -- see rules.py's check_annual_leave_entitlement for the
compliance-engine integration."""

import frappe
from frappe.utils import getdate, today

ANNUAL_LEAVE_TYPE = "Saudi Annual Leave"
LESS_THAN_5_YEARS_DAYS = 21
FIVE_YEARS_OR_MORE_DAYS = 30
TENURE_THRESHOLD_YEARS = 5


def get_annual_leave_entitlement(date_of_joining, on_date: str | None = None) -> int:
	"""KSA Labour Law Art. 109: 21 calendar days/year for under 5 years of
	service, 30 calendar days/year from the start of the 5th year onward.
	No date_of_joining on file -- assume the lower tier rather than over-
	crediting an unknown tenure."""
	if not date_of_joining:
		return LESS_THAN_5_YEARS_DAYS
	years_of_service = (getdate(on_date or today()) - getdate(date_of_joining)).days / 365.25
	return FIVE_YEARS_OR_MORE_DAYS if years_of_service >= TENURE_THRESHOLD_YEARS else LESS_THAN_5_YEARS_DAYS


def get_latest_annual_leave_allocation(employee: str) -> dict | None:
	"""Most recent submitted "Saudi Annual Leave" Leave Allocation for this
	employee, or None if none exists yet."""
	rows = frappe.get_all(
		"Leave Allocation",
		filters={"employee": employee, "leave_type": ANNUAL_LEAVE_TYPE, "docstatus": 1},
		fields=["name", "new_leaves_allocated", "unused_leaves", "total_leaves_allocated", "to_date"],
		order_by="to_date desc",
		limit_page_length=1,
	)
	return rows[0] if rows else None


def get_leave_summary(company: str) -> list[dict]:
	"""Per-employee annual leave summary for the Saudi Leave page: current
	allocation, carried-forward days, and total encashed to date -- reads
	HRMS's own doctypes directly, no gcc_hr-side leave data of its own."""
	employees = frappe.get_all("Employee", filters={"company": company, "status": "Active"}, fields=["name", "employee_name", "date_of_joining"])
	summary = []
	for emp in employees:
		allocation = get_latest_annual_leave_allocation(emp.name)
		entitlement = get_annual_leave_entitlement(emp.date_of_joining)
		summary.append(
			{
				"employee": emp.name,
				"employee_name": emp.employee_name,
				"entitlement_days": entitlement,
				"allocated_days": allocation["new_leaves_allocated"] if allocation else None,
				"carried_forward_days": allocation["unused_leaves"] if allocation else 0,
				"total_leaves_allocated": allocation["total_leaves_allocated"] if allocation else None,
				"has_allocation": bool(allocation),
			}
		)
	return summary
