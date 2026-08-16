# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeComplianceProfile(Document):
	def validate(self):
		self.set_country()

	def set_country(self):
		if not self.company:
			return
		from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
			get_company_country,
		)

		self.country = get_company_country(self.company)


def create_compliance_profile(doc, method=None):
	"""Employee.after_insert hook -- auto-create the compliance profile."""
	if frappe.db.exists("Employee Compliance Profile", doc.name):
		return
	profile = frappe.get_doc(
		{
			"doctype": "Employee Compliance Profile",
			"employee": doc.name,
		}
	)
	profile.insert(ignore_permissions=True)
	dispatch_country_employee_sync(doc, profile.country)


def sync_compliance_profile(doc, method=None):
	"""Employee.on_update hook -- keep the profile's fetched fields in sync."""
	if not frappe.db.exists("Employee Compliance Profile", doc.name):
		create_compliance_profile(doc)
		return
	profile = frappe.get_doc("Employee Compliance Profile", doc.name)
	profile.set_country()
	profile.save(ignore_permissions=True)
	dispatch_country_employee_sync(doc, profile.country)


def dispatch_country_employee_sync(employee_doc, country):
	"""Give the employee's country package a chance to create/update its own
	identity doctype (e.g. Saudi Employee Profile) -- see
	gcc_hr/countries/base.py's employee.py contract. A no-op for countries
	that don't implement employee.py yet."""
	if not country:
		return
	from gcc_hr.countries import get_country_attr

	sync_fn = get_country_attr(country, "employee", "sync_employee")
	if sync_fn:
		sync_fn(employee_doc)
