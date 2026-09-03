# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SupplierClaim(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		claim_amount: DF.Currency
		claim_quantity: DF.Int
		claim_reason: DF.Link
		claim_status: DF.Literal["Draft", "Submitted", "Settled", "Rejected"]
		claim_type: DF.Link
		item_code: DF.Link
		naming_series: DF.Literal["SC-.YYYY.-"]
		reference_receipt_no: DF.Link
		settlement_method: DF.Link
		supplier: DF.Link
		supporting_documents: DF.Attach
	# end: auto-generated types

	def validate(self):
		self.validate_duplicate_claim()
		self.calculate_claim_amount()

	def validate_duplicate_claim(self):
		# Check if a matching claim already exists
		duplicate = frappe.db.exists(
			"Supplier Claim",
			{
				"supplier": self.supplier,
				"reference_receipt_no": self.reference_receipt_no,
				"item_code": self.item_code,
				"claim_type": self.claim_type,
				"docstatus": ["!=", 2],
				"name": ["!=", self.name],
			},
		)
    	# Show error if a duplicate claim is found
		if duplicate:
			frappe.throw(
				_("A claim for this Supplier, Receipt, Item and Claim Type already exists: {0}").format(
					frappe.bold(duplicate)
				)
			)

	def calculate_claim_amount(self):
		# Load the referenced Purchase Receipt
		receipt = frappe.get_doc("Purchase Receipt", self.reference_receipt_no)

		rate = None
		# Find the matching item in the receipt
		for row in receipt.items:
			if row.item_code == self.item_code:
				rate = row.rate
				break

		# Show error if item is not found
		if rate is None:
			frappe.throw(
				_("Item {0} was not found in Purchase Receipt {1}").format(
					self.item_code, self.reference_receipt_no
				)
			)

		self.claim_amount = self.claim_quantity * rate
