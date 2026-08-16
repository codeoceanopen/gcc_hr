# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Saudi-specific payroll side-effects. Dispatched generically from
gcc_hr_core/payroll.py's Salary Slip on_submit hook via
gcc_hr.countries.get_country_attr(country, "payroll", "on_salary_slip_submit")
-- core never imports this module directly."""

from gcc_hr.countries.saudi_arabia.gosi import calculate_for_salary_slip


def on_salary_slip_submit(salary_slip):
	calculate_for_salary_slip(salary_slip)
