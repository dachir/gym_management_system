# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.website.website_generator import WebsiteGenerator

class GymWorkoutPlan(WebsiteGenerator):
	
	def before_save(self):
		self.route = f"/workout_plans/{self.name}".lower()
