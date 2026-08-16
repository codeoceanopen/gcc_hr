# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


class GOSIEmployeeProfile(Document):
	def validate(self):
		# Skip if not yet linked to an Employee -- the profile can be created
		# before the employee link is fully wired in some flows.
		if not self.employee:
			return
		company = frappe.db.get_value("Employee", self.employee, "company")
		enforce_company_country(company, "Saudi Arabia")
