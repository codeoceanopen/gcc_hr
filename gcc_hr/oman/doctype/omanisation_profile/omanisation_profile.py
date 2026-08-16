# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


class OmanisationProfile(Document):
	def validate(self):
		enforce_company_country(self.company, "Oman")
