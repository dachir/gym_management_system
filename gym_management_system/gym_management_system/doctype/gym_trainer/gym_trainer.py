# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GymTrainer(Document):
	pass
	#def before_save(self):
	#	self.get_availability()

@frappe.whitelist()
def get_availability(name):

	avails = frappe.db.sql(
	"""
		SELECT  CONCAT(a.name,r.name) as name,a.parent, a.parentfield, a.parenttype, a.gym_day, a.start_time, a.end_time, r.workout_plan, CONCAT(r.plan_name, ' ', r.level) AS description
		FROM `tabGym Trainer Availability` a  INNER JOIN `tabGym Workout Plan Register` r ON a.parent = r.parent
		WHERE a.parent = %s
	""",(name),as_dict = 1)

	return avails
