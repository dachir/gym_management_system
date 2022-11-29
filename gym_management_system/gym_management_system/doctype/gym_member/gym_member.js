// Copyright (c) 2022, Kossivi Amouzou and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Member', {
	refresh: function(frm) {
		//alert(frm.doc.name);
		frm.add_custom_button('Create Membership',() =>{
			frappe.new_doc('Gym Membership', {
				gym_member: frm.doc.name
			})
		});

		frm.add_custom_button('Book',() =>{
			frappe.db.get_list('Gym Membership', 
			{
				fields: ['name'], 
				filters: {
					"docstatus": 1,
					"gym_member": frm.doc.name,
					"from_date": ['<=', frappe.datetime.now_date()],
					"to_date": ['>=', frappe.datetime.now_date()]
				}
			}).then(r =>{
				console.log(r)
				if(r[0] === undefined) {
					frappe.throw('There is no valid membership for current member');
					return;
				};
				let dialog = new frappe.ui.Dialog({
					title: 'Book a Locker',
					fields: [
						{
							fieldname: 'gym_locker',
							label: 'Gym Locker',
							fieldtype: 'Link',
							options : 'Gym Locker',
						}
					],
					primary_action(values) {
						frappe.db.insert({
							doctype: 'Gym Locker Booking',
							'gym_locker': values.gym_locker,
							'gym_membership': r[0].name,
							'status': 'In Use',
							'date': frappe.datetime.now_date(),
							'start_time': frappe.datetime.now_time(),
						}).then(doc =>{
							dialog.hide();
							frappe.set_route('Form','Gym Locker Booking',doc.name);
						})
					}
				});
				dialog.show();
			});
		},'Locker');

		frm.add_custom_button('Release',() =>{
			frappe.call({
				method:"gym_management_system.gym_management_system.doctype.gym_member.gym_member.release_locker",
				args: {
					"member": frm.doc.name
				},
				callback: function(r) {
					
				},
				freeze: true,
			});
		},'Locker');
	}
});
