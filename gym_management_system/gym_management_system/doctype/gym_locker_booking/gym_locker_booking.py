# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus

class GymLockerBooking(Document):
	
	def before_save(self):
		if self.status == "In Use":
			self.validate_issue()
			# set the article status to be Issued
			locker = frappe.get_doc("Gym Locker", self.gym_locker)
			locker.satus = "Issued"
			locker.save()
		elif self.status == "Free":
			self.validate_return()
			# set the article status to be Available
			locker = frappe.get_doc("Gym Locker", self.gym_locker)
			locker.satus = "Available"
			locker.save()

	def validate(self):
		self.validate_membership()
		self.validate_maximum_limit()

	def validate_issue(self):
		self.validate_membership()
		locker = frappe.get_doc("Gym Locker", self.gym_locker)
		# locker cannot be issued if it is already issued
		if locker.satus == "Issued":
			frappe.throw("Locker is already issued to another member")

	def validate_return(self):
		locker = frappe.get_doc("Gym Locker", self.gym_locker)
		# locker cannot be returned if it is not issued first
		if locker.satus == "Available":
			frappe.throw("Locker cannot be set free if not issued first")

	def validate_membership(self):
		# check if a valid membership exist for this Gym member
		return
		valid_membership = frappe.db.exists(
		"Gym Membership",
			{
				"gym_membership": self.gym_membership,
				"docstatus": DocStatus.submitted(),
				"from_date": ("<=", self.date),
				"to_date": (">=", self.date),
			},
		)
		#frappe.msgprint(str(valid_membership))
		if not valid_membership:
			frappe.throw("The member does not have a valid membership")

	# call this method from validate
	def validate_maximum_limit(self):
		locker_number = frappe.db.get_single_value("Gym Settings", "locker_number")
		count = frappe.db.count(
			"Gym Locker Booking",
			{
				"gym_membership": self.gym_membership, 
				"status": "In Use", 
				"docstatus": DocStatus.submitted()
			},
		)
		if count >= locker_number:
			frappe.throw("Maximum limit reached for issuing lockers")


