# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.gcc_hr_core import government

TEST_COMPANY = "_Test GCC Government Co"
FAKE_TYPE_CODE = "_TEST_FAKE_SUBMISSION_TYPE"
FAKE_INACTIVE_TYPE_CODE = "_TEST_FAKE_INACTIVE_SUBMISSION_TYPE"


def fake_generate_for_tests(company=None, reference_doctype=None, reference_name=None):
	return {"filename": "fake.txt", "content": "hello", "content_type": "text/plain"}


def fake_validate_with_errors_for_tests(company=None, reference_doctype=None, reference_name=None):
	return ["Something is wrong."]


class TestGovernmentSubmission(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGGZ",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)

		from gcc_hr.countries.saudi_arabia.saudization import recalculate

		recalculate(TEST_COMPANY)  # Saudization Profile is the Nitaqat report's reference data

		if not frappe.db.exists("Government Submission Type", FAKE_TYPE_CODE):
			frappe.get_doc(
				{
					"doctype": "Government Submission Type",
					"submission_type_code": FAKE_TYPE_CODE,
					"submission_type_name": "Fake Type For Tests",
					"country": "Saudi Arabia",
					"category": "Other",
					"generate_method": "gcc_hr.gcc_hr_core.test_government.fake_generate_for_tests",
					"validate_method": "gcc_hr.gcc_hr_core.test_government.fake_validate_with_errors_for_tests",
					"is_active": 1,
				}
			).insert(ignore_permissions=True)

		if not frappe.db.exists("Government Submission Type", FAKE_INACTIVE_TYPE_CODE):
			frappe.get_doc(
				{
					"doctype": "Government Submission Type",
					"submission_type_code": FAKE_INACTIVE_TYPE_CODE,
					"submission_type_name": "Fake Inactive Type For Tests",
					"country": "Saudi Arabia",
					"category": "Other",
					"generate_method": "gcc_hr.gcc_hr_core.test_government.fake_generate_for_tests",
					"is_active": 0,
				}
			).insert(ignore_permissions=True)

	def _new_submission(self, submission_type="SA_NITAQAT_REPORT"):
		return government.create_submission(TEST_COMPANY, submission_type)

	def test_full_happy_path(self):
		doc = self._new_submission()
		self.assertEqual(doc.status, "Draft")

		doc = government.generate(doc.name)
		self.assertEqual(doc.status, "Generated")
		self.assertTrue(doc.generated_document)

		doc = government.validate_submission(doc.name)
		self.assertEqual(doc.status, "Validated")
		self.assertEqual(doc.validation_errors, "")

		doc = government.mark_ready(doc.name)
		self.assertEqual(doc.status, "Ready for Submission")

		doc = government.record_manual_submission(doc.name, government_reference_number="NITAQAT-123")
		self.assertEqual(doc.status, "Submitted")
		self.assertEqual(doc.government_reference_number, "NITAQAT-123")
		self.assertEqual(doc.submitted_by, frappe.session.user)

		doc = government.upload_response(doc.name, "/private/files/fake-response.pdf")
		self.assertEqual(doc.status, "Response Uploaded")
		self.assertEqual(doc.response_document, "/private/files/fake-response.pdf")

		doc = government.complete(doc.name, "Accepted", notes="All good.")
		self.assertEqual(doc.status, "Completed")
		self.assertEqual(doc.outcome, "Accepted")
		self.assertEqual(doc.notes, "All good.")

	def test_cannot_validate_before_generate(self):
		doc = self._new_submission()
		with self.assertRaises(frappe.ValidationError):
			government.validate_submission(doc.name)

	def test_cannot_mark_ready_before_validate(self):
		doc = self._new_submission()
		government.generate(doc.name)
		with self.assertRaises(frappe.ValidationError):
			government.mark_ready(doc.name)

	def test_cannot_skip_straight_to_complete(self):
		doc = self._new_submission()
		with self.assertRaises(frappe.ValidationError):
			government.complete(doc.name, "Accepted")

	def test_complete_rejects_invalid_outcome(self):
		doc = self._new_submission()
		government.generate(doc.name)
		government.validate_submission(doc.name)
		government.mark_ready(doc.name)
		government.record_manual_submission(doc.name)
		government.upload_response(doc.name, "/private/files/x.pdf")
		with self.assertRaises(frappe.ValidationError):
			government.complete(doc.name, "Maybe")

	def test_regenerate_resets_validation(self):
		doc = self._new_submission()
		government.generate(doc.name)
		government.validate_submission(doc.name)
		self.assertEqual(frappe.db.get_value("Government Submission", doc.name, "status"), "Validated")

		doc = government.generate(doc.name)
		self.assertEqual(doc.status, "Generated")
		self.assertEqual(doc.validation_errors, "")

	def test_validation_failure_keeps_status_generated_and_blocks_mark_ready(self):
		doc = self._new_submission(FAKE_TYPE_CODE)
		government.generate(doc.name)

		doc = government.validate_submission(doc.name)
		self.assertEqual(doc.status, "Generated")
		self.assertIn("Something is wrong.", doc.validation_errors)

		with self.assertRaises(frappe.ValidationError):
			government.mark_ready(doc.name)

	def test_generate_fails_for_inactive_submission_type(self):
		doc = self._new_submission(FAKE_INACTIVE_TYPE_CODE)
		with self.assertRaises(frappe.ValidationError):
			government.generate(doc.name)

	def test_generate_fails_for_unimportable_generate_method(self):
		bad_type_code = "_TEST_FAKE_BAD_METHOD_SUBMISSION_TYPE"
		if not frappe.db.exists("Government Submission Type", bad_type_code):
			frappe.get_doc(
				{
					"doctype": "Government Submission Type",
					"submission_type_code": bad_type_code,
					"submission_type_name": "Fake Bad Method Type For Tests",
					"country": "Saudi Arabia",
					"category": "Other",
					"generate_method": "gcc_hr.gcc_hr_core.test_government.this_function_does_not_exist",
					"is_active": 1,
				}
			).insert(ignore_permissions=True)
		doc = self._new_submission(bad_type_code)
		with self.assertRaises(frappe.ValidationError):
			government.generate(doc.name)
