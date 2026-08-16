# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from gcc_hr.gcc_hr_core.compliance_engine.expiry_engine import compute_status_for_document
from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import get_company_country


class HRComplianceDocument(Document):
	def validate(self):
		if not self.country and self.company:
			self.country = get_company_country(self.company)
		self.apply_expiry_status()

	def apply_expiry_status(self):
		if not self.expiry_date:
			return
		status, days_remaining, _severity = compute_status_for_document(
			expiry_date=self.expiry_date, country=self.country, document_type=self.document_type
		)
		self.status = status
		self.days_remaining = days_remaining
