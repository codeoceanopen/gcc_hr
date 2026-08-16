// Copyright (c) 2026, GCC HR Compliance and contributors
// For license information, please see license.txt

frappe.ui.form.on("Saudization Requirement", {
	onload(frm) {
		// Frappe auto-fills any field literally named "company" with the
		// user's default company on a new document. That silently defeats
		// this doctype's "blank company = applies to every company"
		// design (see the field's own description) unless the user
		// notices and clears it themselves -- so clear it for them here.
		if (frm.is_new() && frm.doc.company) {
			frm.set_value("company", "");
		}
	},
});
