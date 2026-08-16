# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


class SaudiEmployeeProfile(Document):
	def validate(self):
		# Skip if not yet linked to an Employee -- the profile can be created
		# before the employee link is fully wired in some flows.
		if not self.employee:
			return
		company = frappe.db.get_value("Employee", self.employee, "company")
		enforce_company_country(company, "Saudi Arabia")


# Deliberately no hard `validate()` block requiring iqama_number for
# Non-Saudi employees: the profile is auto-created (see
# gcc_hr.countries.saudi_arabia.employee.sync_employee) the moment a new
# hire's Employee record is inserted, before HR has necessarily received
# their Iqama -- a save-blocking MandatoryError there would break that
# auto-provisioning flow. `mandatory_depends_on` in the JSON still drives
# the Desk form's required-field indicator as a fill-this-in reminder; the
# actual compliance signal is the SA_NON_SAUDI_IQAMA_ON_FILE rule (see
# countries/saudi_arabia/rules.py:check_non_saudi_has_iqama), which is the
# right mechanism for "this is missing and should be flagged/scored", as
# opposed to "this must never be saved without it."
