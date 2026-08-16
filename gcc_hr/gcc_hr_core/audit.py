# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe


def log_action(
	action: str,
	reference_doctype: str | None = None,
	reference_name: str | None = None,
	employee: str | None = None,
	company: str | None = None,
	old_value: str | None = None,
	new_value: str | None = None,
	reason: str | None = None,
	source: str = "System",
	user: str | None = None,
):
	"""Insert an immutable HR Audit Log row. Always uses ignore_permissions
	since no role is granted create rights on HR Audit Log -- it is written
	exclusively by this helper, never edited afterwards."""
	frappe.get_doc(
		{
			"doctype": "HR Audit Log",
			"user": user or frappe.session.user,
			"action": action,
			"company": company,
			"employee": employee,
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"old_value": old_value,
			"new_value": new_value,
			"reason": reason,
			"source": source,
		}
	).insert(ignore_permissions=True)


def log_doc_change(doc, method=None):
	"""Generic doc_events["on_update"] handler for configuration/compliance
	doctypes -- logs a diff of changed fields against the pre-save version.
	Registered in hooks.py for doctypes where "who changed what" matters:
	country/company settings, compliance rules, thresholds, score bands."""
	before = doc.get_doc_before_save()
	if not before:
		return

	changed = {}
	for fieldname, value in doc.as_dict().items():
		if fieldname.startswith(("_", "modified", "creation")):
			continue
		old = before.get(fieldname)
		if old != value:
			changed[fieldname] = {"old": old, "new": value}

	if not changed:
		return

	employee = doc.get("employee") if doc.meta.has_field("employee") else None
	company = doc.get("company") if doc.meta.has_field("company") else None

	log_action(
		action=f"{doc.doctype} Updated",
		reference_doctype=doc.doctype,
		reference_name=doc.name,
		employee=employee,
		company=company,
		old_value=frappe.as_json({k: v["old"] for k, v in changed.items()}),
		new_value=frappe.as_json({k: v["new"] for k, v in changed.items()}),
		source="Manual",
	)
