// Copyright (c) 2026, GCC HR Compliance and contributors
// For license information, please see license.txt

frappe.ui.form.on("Qatarization Requirement", {
	onload(frm) {
		// Same footgun as Saudization Requirement (see that doctype's own
		// .js file): Frappe auto-fills any field literally named "company"
		// with the user's default company on a new document, which would
		// silently defeat this doctype's "blank company = applies to every
		// company" design.
		if (frm.is_new() && frm.doc.company) {
			frm.set_value("company", "");
		}
	},
});
