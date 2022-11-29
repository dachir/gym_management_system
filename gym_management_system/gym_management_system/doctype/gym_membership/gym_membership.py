# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days
from frappe.model.docstatus import DocStatus

class GymMembership(Document):
	
	def validate(self):
		nb_days = frappe.db.get_single_value("Gym Settings", "number_of_days")
		self.to_date = add_days(self.from_date, nb_days or 30)

	# check before submitting this document
	def before_submit(self): 
		exists = frappe.db.exists(
			"Gym Membership",
			{
				"gym_member": self.gym_member,
				"docstatus": DocStatus.submitted(),
				# check if the membership's end date is later than this membership's start date
				"to_date": (">", self.from_date),
			},
		)
		if exists:
			frappe.throw("There is an active membership for this member") 