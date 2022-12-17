# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

class GymMemberDailyAppointment(WebsiteGenerator):
	
	def on_submit(self):
		if self.gym_trainer :
			trainer = frappe.get_doc("Gym Trainer", self.gym_trainer)
			if not self.rating :
				if trainer.rating > 0 :
					if self.rating > 0 :
						trainer.rating = (trainer.rating + self.rating) / 2
				else :
					trainer.rating = self.rating
			else:
				trainer.rating = self.rating
			#trainer.save(ignore_permissions=True)
			trainer.save()


	def on_cancel(self):
		if self.rating > 0 :
			nb = frappe.db.count('Gym Trainer')
			trainer = frappe.get_doc("Gym Trainer", self.gym_trainer)
			trainer.rating = trainer.rating * 2 - self.rating if nb > 0 else 0

