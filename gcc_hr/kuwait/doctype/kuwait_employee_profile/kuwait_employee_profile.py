# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


class KuwaitEmployeeProfile(Document):
	def validate(self):
		if not self.employee:
			return
		company = frappe.db.get_value("Employee", self.employee, "company")
		enforce_company_country(company, "Kuwait")
