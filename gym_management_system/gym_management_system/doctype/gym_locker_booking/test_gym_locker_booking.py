# Copyright (c) 2022, Kossivi Amouzou and Contributors
# See license.txt

import frappe
from frappe.utils import now
from frappe.tests.utils import FrappeTestCase
from gym_management_system.gym_management_system.doctype.gym_member.gym_member import release_locker

mem1 = {}

def prepare_test(self):
	if frappe.flags.test_Lockers_created:
		return

	#frappe.set_user("Gym Admin")
	self.test1 = frappe.get_doc({
		"doctype" : "Gym Member",
		"email_address" : "test1@test.com",
		"first_name" : "test 1",
	}).insert()

	self.mem1 = frappe.get_doc({
		"doctype": "Gym Membership",
		"gym_member":self.test1.name,
		"from_date": "2022-12-01",
		"membership_type": "GOLD",
	}).insert()

	self.glb1 = frappe.get_doc({
		"doctype": "Gym Locker Booking",
		"gym_locker":"LOCK01",
		"status": "In Use",
		'gym_membership': self.mem1.name,
		"date": now(),
		"start_time": now(),
	}).insert()

	print(str(self.mem1))
	frappe.flags.test_Lockers_created = True


class TestGymLockerBooking(FrappeTestCase):
	def setUp(self):
		prepare_test(self)

	def tearDown(self):
		#frappe.set_user("Gym Admin")
		pass

	def test_locker_allready_allocated(self):
		test2 = frappe.get_doc({
			"doctype": "Gym Member",
			"email_address": "test2@test.com",
			"first_name":"test 2",
		}).insert()

		mem2 = frappe.get_doc({
			"doctype": "Gym Membership",
			"gym_member":test2.name,
			"from_date": "2022-12-01",
			"membership_type": "SILVER",
		}).insert()

		glb = frappe.get_doc({
			"doctype": "Gym Locker Booking",
			"gym_locker":"LOCK01",
			"status": "In Use",
			'gym_membership': mem2.name,
			"date": now(),
			"start_time": now(),
		})
		self.assertRaises(frappe.exceptions.ValidationError, lambda: glb.insert())
		#with self.assertRaises(frappe.exceptions.ValidationError):
			#glb.insert()
			

	def test_free_locker(self):
		#print(str(self.mem1))
		release_locker(self.mem1.gym_member)
		locker01 = frappe.get_doc("Gym Locker","LOCK01")
		self.assertTrue(locker01.satus, "Available")


