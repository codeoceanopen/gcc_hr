# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

GCC_COUNTRIES = (
	"Saudi Arabia",
	"Qatar",
	"United Arab Emirates",
	"Oman",
	"Bahrain",
	"Kuwait",
)


class HRCountrySettings(Document):
	def validate(self):
		if self.country not in GCC_COUNTRIES:
			frappe.throw(
				_("{0} is not a supported GCC country. Supported countries: {1}").format(
					frappe.bold(self.country), ", ".join(GCC_COUNTRIES)
				)
			)


def get_active_countries() -> list[str]:
	"""Countries with is_active=1, i.e. whose localization module may be selected."""
	return frappe.get_all("HR Country Settings", filters={"is_active": 1}, pluck="country")
