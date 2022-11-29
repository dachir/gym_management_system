# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, today

class GymMember(Document):
	
	def before_save(self):
		self.full_name = self.first_name + ' ' +(self.last_name or '')
		self.compute_age()
		
	
	def compute_age(self):
		if self.age:
			self.age = date_diff(today(), self.date_of_birth) / 365


@frappe.whitelist()
def release_locker(member):
	bookings = frappe.db.get_list('Gym Locker Booking', fields = ['name'], 	
					filters= {
						"status": "In Use",
						"email_id": member,
					}
				)
	for b in bookings:
		#frappe.msgprint(str(b.get('doctype')))
		doc = frappe.get_doc('Gym Locker Booking', b.name)
		doc.status = 'Free'
		doc.save()
		frappe.msgprint('Locker used by this member is now available')


