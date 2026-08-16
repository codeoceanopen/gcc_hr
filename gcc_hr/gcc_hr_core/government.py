# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Government Integration Framework (Phase 5).

Per the brief's "Important Government Integration Rule": this app never
fabricates a government API. No GCC government currently exposes a verified,
public API for GOSI/Qiwa/Nitaqat/Muqeem-type submissions, so this framework
never pretends to call one -- it only automates the parts that don't require
one (generating the submission document from data already in this app,
validating it) and tracks the parts a human still has to do by hand on the
real government portal (submit, then come back and record what happened).
That's the generate / validate / manual-submit / upload-response /
track-status shape README.md describes.

Which document a Government Submission Type produces, and how it's
validated, is configuration (generate_method/validate_method, dotted Python
paths) -- exactly the same shape as HR Compliance Rule.check_method. The
state machine itself (Draft -> Generated -> Validated -> Ready for
Submission -> Submitted -> Response Uploaded -> Completed) is enforced here,
not left to the Desk form, so a submission can never skip a step no human
has actually done yet.
"""

import frappe
from frappe.utils import now_datetime

from gcc_hr.gcc_hr_core.audit import log_action

_TRANSITIONS = {
	"generate": ("Draft", "Generated"),
	"validate": ("Generated", "Validated"),
	"mark_ready": ("Validated", "Ready for Submission"),
	"record_manual_submission": ("Ready for Submission", "Submitted"),
	"upload_response": ("Submitted", "Response Uploaded"),
	"complete": ("Response Uploaded", "Completed"),
}


def _require_status(doc, action: str):
	allowed_from = _TRANSITIONS[action][0]
	if doc.status != allowed_from:
		frappe.throw(f"Cannot {action.replace('_', ' ')} a submission in status {doc.status!r} (expected {allowed_from!r}).")


def create_submission(company: str, submission_type: str, reference_name: str | None = None) -> "frappe.model.document.Document":
	doc = frappe.get_doc(
		{
			"doctype": "Government Submission",
			"company": company,
			"submission_type": submission_type,
			"reference_name": reference_name,
			"status": "Draft",
		}
	)
	doc.insert()
	log_action(
		action="Government Submission Created",
		reference_doctype="Government Submission",
		reference_name=doc.name,
		company=company,
		source="Manual",
	)
	return doc


def generate(name: str) -> "frappe.model.document.Document":
	"""(Re-)generate the submission document. Allowed from Draft, or from
	Generated/Validated/Ready for Submission to regenerate after fixing the
	underlying data -- but regenerating always resets validation, since a
	changed document may no longer be valid."""
	doc = frappe.get_doc("Government Submission", name)
	if doc.status not in ("Draft", "Generated", "Validated", "Ready for Submission"):
		frappe.throw(f"Cannot generate a submission in status {doc.status!r} once it has been submitted.")

	submission_type = frappe.get_doc("Government Submission Type", doc.submission_type)
	if not submission_type.is_active:
		frappe.throw(f"Government Submission Type {submission_type.name} is not active.")

	try:
		func = frappe.get_attr(submission_type.generate_method)
	except Exception:
		frappe.log_error(title="GCC HR: invalid Government Submission Type generate_method", message=frappe.get_traceback())
		frappe.throw(f"Generate Method {submission_type.generate_method} could not be imported.")

	result = func(company=doc.company, reference_doctype=doc.reference_doctype, reference_name=doc.reference_name)
	content = result["content"]
	if isinstance(content, str):
		content = content.encode("utf-8")

	from frappe.utils.file_manager import save_file

	file_doc = save_file(result["filename"], content, doc.doctype, doc.name, is_private=1)

	doc.db_set(
		{
			"generated_document": file_doc.file_url,
			"generated_on": now_datetime(),
			"status": "Generated",
			"validation_errors": "",
			"validated_on": None,
		},
		update_modified=False,
		notify=False,
	)
	log_action(
		action="Government Submission Generated",
		reference_doctype="Government Submission",
		reference_name=doc.name,
		company=doc.company,
		new_value=file_doc.file_url,
		source="Manual",
	)
	doc.reload()
	return doc


def validate_submission(name: str) -> "frappe.model.document.Document":
	doc = frappe.get_doc("Government Submission", name)
	_require_status(doc, "validate")

	submission_type = frappe.get_doc("Government Submission Type", doc.submission_type)
	errors: list[str] = []
	if submission_type.validate_method:
		try:
			func = frappe.get_attr(submission_type.validate_method)
		except Exception:
			frappe.log_error(title="GCC HR: invalid Government Submission Type validate_method", message=frappe.get_traceback())
			frappe.throw(f"Validate Method {submission_type.validate_method} could not be imported.")
		errors = func(company=doc.company, reference_doctype=doc.reference_doctype, reference_name=doc.reference_name) or []

	doc.db_set(
		{
			"validation_errors": "\n".join(errors),
			"validated_on": now_datetime(),
			"status": "Validated" if not errors else "Generated",
		},
		update_modified=False,
		notify=False,
	)
	log_action(
		action="Government Submission Validated",
		reference_doctype="Government Submission",
		reference_name=doc.name,
		company=doc.company,
		new_value=f"errors={len(errors)}",
		source="Manual",
	)
	doc.reload()
	return doc


def mark_ready(name: str) -> "frappe.model.document.Document":
	doc = frappe.get_doc("Government Submission", name)
	_require_status(doc, "mark_ready")
	doc.db_set("status", "Ready for Submission", update_modified=False, notify=False)
	log_action(
		action="Government Submission Marked Ready",
		reference_doctype="Government Submission",
		reference_name=doc.name,
		company=doc.company,
		source="Manual",
	)
	doc.reload()
	return doc


def record_manual_submission(name: str, government_reference_number: str | None = None) -> "frappe.model.document.Document":
	"""Records that a human has manually filed this submission on the real
	government portal (see Government Submission Type.portal_url/
	portal_instructions) -- this app never files it on their behalf."""
	doc = frappe.get_doc("Government Submission", name)
	_require_status(doc, "record_manual_submission")
	doc.db_set(
		{
			"status": "Submitted",
			"submitted_on": now_datetime(),
			"submitted_by": frappe.session.user,
			"government_reference_number": government_reference_number,
		},
		update_modified=False,
		notify=False,
	)
	log_action(
		action="Government Submission Recorded as Submitted",
		reference_doctype="Government Submission",
		reference_name=doc.name,
		company=doc.company,
		new_value=government_reference_number or "",
		source="Manual",
	)
	doc.reload()
	return doc


def upload_response(name: str, file_url: str) -> "frappe.model.document.Document":
	doc = frappe.get_doc("Government Submission", name)
	_require_status(doc, "upload_response")
	doc.db_set(
		{"response_document": file_url, "response_uploaded_on": now_datetime(), "status": "Response Uploaded"},
		update_modified=False,
		notify=False,
	)
	log_action(
		action="Government Submission Response Uploaded",
		reference_doctype="Government Submission",
		reference_name=doc.name,
		company=doc.company,
		new_value=file_url,
		source="Manual",
	)
	doc.reload()
	return doc


def complete(name: str, outcome: str, notes: str | None = None) -> "frappe.model.document.Document":
	if outcome not in ("Accepted", "Rejected"):
		frappe.throw("Outcome must be Accepted or Rejected.")
	doc = frappe.get_doc("Government Submission", name)
	_require_status(doc, "complete")
	doc.db_set(
		{"status": "Completed", "outcome": outcome, "notes": notes or doc.notes},
		update_modified=False,
		notify=False,
	)
	log_action(
		action="Government Submission Completed",
		reference_doctype="Government Submission",
		reference_name=doc.name,
		company=doc.company,
		new_value=outcome,
		source="Manual",
	)
	doc.reload()
	return doc
