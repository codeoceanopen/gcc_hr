# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


class UAEEmployeeProfile(Document):
	def validate(self):
		# Skip if not yet linked to an Employee -- the profile can be created
		# before the employee link is fully wired in some flows.
		if not self.employee:
			return
		company = frappe.db.get_value("Employee", self.employee, "company")
		enforce_company_country(company, "United Arab Emirates")


# Deliberately no hard `validate()` block requiring eid_number for
# Non-Emirati employees, for the same reason Saudi/Qatar Employee Profile
# have none -- see those doctypes' controller docstrings. The soft
# compliance signal here is UAE_NON_EMIRATI_EID_ON_FILE
# (countries/united_arab_emirates/rules.py).
