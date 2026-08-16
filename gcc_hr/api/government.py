# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Thin, permission-checked wrappers around gcc_hr_core/government.py's
state machine -- needed because that module uses db_set (bypasses the normal
permission pipeline, same reason api/saudization.py checks permissions
itself before calling recalculate())."""

import frappe

from gcc_hr.gcc_hr_core import government


def _check_write(name: str):
	if not frappe.has_permission("Government Submission", "write", doc=name):
		frappe.throw(frappe._("Not permitted to act on this Government Submission."), frappe.PermissionError)


@frappe.whitelist()
def create_submission(company: str, submission_type: str, reference_name: str | None = None):
	if not frappe.has_permission("Government Submission", "create"):
		frappe.throw(frappe._("Not permitted to create a Government Submission."), frappe.PermissionError)
	doc = government.create_submission(company, submission_type, reference_name)
	return doc.name


@frappe.whitelist()
def generate(name: str):
	_check_write(name)
	return government.generate(name).as_dict()


@frappe.whitelist()
def validate_submission(name: str):
	_check_write(name)
	return government.validate_submission(name).as_dict()


@frappe.whitelist()
def mark_ready(name: str):
	_check_write(name)
	return government.mark_ready(name).as_dict()


@frappe.whitelist()
def record_manual_submission(name: str, government_reference_number: str | None = None):
	_check_write(name)
	return government.record_manual_submission(name, government_reference_number).as_dict()


@frappe.whitelist()
def upload_response(name: str, file_url: str):
	_check_write(name)
	return government.upload_response(name, file_url).as_dict()


@frappe.whitelist()
def complete_submission(name: str, outcome: str, notes: str | None = None):
	_check_write(name)
	return government.complete(name, outcome, notes).as_dict()
