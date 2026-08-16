# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.api.government import (
	complete_submission,
	create_submission,
	generate,
	mark_ready,
	record_manual_submission,
	upload_response,
	validate_submission,
)

TEST_COMPANY = "_Test GCC Government API Co"
TEST_QATAR_COMPANY = "_Test GCC Government API QAT Co"
TEST_UAE_COMPANY = "_Test GCC Government API UAE Co"
TEST_OMAN_COMPANY = "_Test GCC Government API OM Co"
TEST_BAHRAIN_COMPANY = "_Test GCC Government API BAH Co"
TEST_KUWAIT_COMPANY = "_Test GCC Government API KWT Co"


class TestGovernmentAPI(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGGAZ",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)

		from gcc_hr.countries.saudi_arabia.saudization import recalculate

		recalculate(TEST_COMPANY)

		if not frappe.db.exists("Company", TEST_QATAR_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_QATAR_COMPANY,
					"abbr": "TGGAQ",
					"default_currency": "QAR",
					"country": "Qatar",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_QATAR_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_QATAR_COMPANY, "country": "Qatar"}
			).insert(ignore_permissions=True)

		from gcc_hr.countries.qatar.qatarization import recalculate as recalculate_qatar

		recalculate_qatar(TEST_QATAR_COMPANY)

		if not frappe.db.exists("Company", TEST_UAE_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_UAE_COMPANY,
					"abbr": "TGGAU",
					"default_currency": "AED",
					"country": "United Arab Emirates",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_UAE_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_UAE_COMPANY, "country": "United Arab Emirates"}
			).insert(ignore_permissions=True)

		from gcc_hr.countries.united_arab_emirates.emiratisation import recalculate as recalculate_uae

		recalculate_uae(TEST_UAE_COMPANY)

		if not frappe.db.exists("Company", TEST_OMAN_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_OMAN_COMPANY,
					"abbr": "TGGAO",
					"default_currency": "OMR",
					"country": "Oman",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_OMAN_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_OMAN_COMPANY, "country": "Oman"}
			).insert(ignore_permissions=True)

		from gcc_hr.countries.oman.omanisation import recalculate as recalculate_oman

		recalculate_oman(TEST_OMAN_COMPANY)

		if not frappe.db.exists("Company", TEST_BAHRAIN_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_BAHRAIN_COMPANY,
					"abbr": "TGGAB",
					"default_currency": "BHD",
					"country": "Bahrain",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_BAHRAIN_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_BAHRAIN_COMPANY, "country": "Bahrain"}
			).insert(ignore_permissions=True)

		from gcc_hr.countries.bahrain.bahrainisation import recalculate as recalculate_bahrain

		recalculate_bahrain(TEST_BAHRAIN_COMPANY)

		if not frappe.db.exists("Company", TEST_KUWAIT_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_KUWAIT_COMPANY,
					"abbr": "TGGAK",
					"default_currency": "KWD",
					"country": "Kuwait",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_KUWAIT_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_KUWAIT_COMPANY, "country": "Kuwait"}
			).insert(ignore_permissions=True)

		from gcc_hr.countries.kuwait.kuwaitisation import recalculate as recalculate_kuwait

		recalculate_kuwait(TEST_KUWAIT_COMPANY)

	def test_end_to_end_via_api_wrappers_for_kuwait_submission_type(self):
		"""Sixth country, same unmodified state machine."""
		frappe.set_user("Administrator")

		name = create_submission(TEST_KUWAIT_COMPANY, "KWT_KUWAITISATION_REPORT")
		self.assertTrue(frappe.db.exists("Government Submission", name))

		doc = generate(name)
		self.assertEqual(doc["status"], "Generated")

		doc = validate_submission(name)
		self.assertEqual(doc["status"], "Validated")

		doc = mark_ready(name)
		self.assertEqual(doc["status"], "Ready for Submission")

		doc = record_manual_submission(name, government_reference_number="KWT-XYZ-654")
		self.assertEqual(doc["status"], "Submitted")

		doc = upload_response(name, "/private/files/fake-kwt.pdf")
		self.assertEqual(doc["status"], "Response Uploaded")

		doc = complete_submission(name, "Accepted")
		self.assertEqual(doc["status"], "Completed")

	def test_end_to_end_via_api_wrappers_for_bahrain_submission_type(self):
		"""Fifth country, same unmodified state machine."""
		frappe.set_user("Administrator")

		name = create_submission(TEST_BAHRAIN_COMPANY, "BAH_BAHRAINISATION_REPORT")
		self.assertTrue(frappe.db.exists("Government Submission", name))

		doc = generate(name)
		self.assertEqual(doc["status"], "Generated")

		doc = validate_submission(name)
		self.assertEqual(doc["status"], "Validated")

		doc = mark_ready(name)
		self.assertEqual(doc["status"], "Ready for Submission")

		doc = record_manual_submission(name, government_reference_number="BAH-XYZ-987")
		self.assertEqual(doc["status"], "Submitted")

		doc = upload_response(name, "/private/files/fake-bah.pdf")
		self.assertEqual(doc["status"], "Response Uploaded")

		doc = complete_submission(name, "Accepted")
		self.assertEqual(doc["status"], "Completed")

	def test_end_to_end_via_api_wrappers_for_oman_submission_type(self):
		"""Fourth country, same unmodified state machine."""
		frappe.set_user("Administrator")

		name = create_submission(TEST_OMAN_COMPANY, "OM_OMANISATION_REPORT")
		self.assertTrue(frappe.db.exists("Government Submission", name))

		doc = generate(name)
		self.assertEqual(doc["status"], "Generated")

		doc = validate_submission(name)
		self.assertEqual(doc["status"], "Validated")

		doc = mark_ready(name)
		self.assertEqual(doc["status"], "Ready for Submission")

		doc = record_manual_submission(name, government_reference_number="OM-XYZ-321")
		self.assertEqual(doc["status"], "Submitted")

		doc = upload_response(name, "/private/files/fake-om.pdf")
		self.assertEqual(doc["status"], "Response Uploaded")

		doc = complete_submission(name, "Accepted")
		self.assertEqual(doc["status"], "Completed")

	def test_end_to_end_via_api_wrappers_for_uae_submission_type(self):
		"""Same proof as the Qatar test below, for the third country -- this
		state machine has now been exercised, unmodified, by all three
		country packages this app ships so far."""
		frappe.set_user("Administrator")

		name = create_submission(TEST_UAE_COMPANY, "UAE_EMIRATISATION_REPORT")
		self.assertTrue(frappe.db.exists("Government Submission", name))

		doc = generate(name)
		self.assertEqual(doc["status"], "Generated")

		doc = validate_submission(name)
		self.assertEqual(doc["status"], "Validated")

		doc = mark_ready(name)
		self.assertEqual(doc["status"], "Ready for Submission")

		doc = record_manual_submission(name, government_reference_number="UAE-XYZ-456")
		self.assertEqual(doc["status"], "Submitted")

		doc = upload_response(name, "/private/files/fake-uae.pdf")
		self.assertEqual(doc["status"], "Response Uploaded")

		doc = complete_submission(name, "Accepted")
		self.assertEqual(doc["status"], "Completed")

	def test_end_to_end_via_api_wrappers_for_qatar_submission_type(self):
		"""api/government.py and gcc_hr_core/government.py contain zero
		Qatar-specific code -- this test's only point is proving that same,
		Saudi-authored state machine works unmodified for a Qatar submission
		type too. If this ever needs a Qatar-specific branch anywhere in
		that pipeline, the "generic government framework" claim is false."""
		frappe.set_user("Administrator")

		name = create_submission(TEST_QATAR_COMPANY, "QAT_QATARIZATION_REPORT")
		self.assertTrue(frappe.db.exists("Government Submission", name))

		doc = generate(name)
		self.assertEqual(doc["status"], "Generated")

		doc = validate_submission(name)
		self.assertEqual(doc["status"], "Validated")

		doc = mark_ready(name)
		self.assertEqual(doc["status"], "Ready for Submission")

		doc = record_manual_submission(name, government_reference_number="QAT-XYZ-789")
		self.assertEqual(doc["status"], "Submitted")

		doc = upload_response(name, "/private/files/fake-qat.pdf")
		self.assertEqual(doc["status"], "Response Uploaded")

		doc = complete_submission(name, "Accepted")
		self.assertEqual(doc["status"], "Completed")

	def test_end_to_end_via_api_wrappers(self):
		frappe.set_user("Administrator")

		name = create_submission(TEST_COMPANY, "SA_NITAQAT_REPORT")
		self.assertTrue(frappe.db.exists("Government Submission", name))

		doc = generate(name)
		self.assertEqual(doc["status"], "Generated")

		doc = validate_submission(name)
		self.assertEqual(doc["status"], "Validated")

		doc = mark_ready(name)
		self.assertEqual(doc["status"], "Ready for Submission")

		doc = record_manual_submission(name, government_reference_number="ABC123")
		self.assertEqual(doc["status"], "Submitted")
		self.assertEqual(doc["government_reference_number"], "ABC123")

		doc = upload_response(name, "/private/files/fake.pdf")
		self.assertEqual(doc["status"], "Response Uploaded")

		doc = complete_submission(name, "Accepted")
		self.assertEqual(doc["status"], "Completed")
		self.assertEqual(doc["outcome"], "Accepted")
