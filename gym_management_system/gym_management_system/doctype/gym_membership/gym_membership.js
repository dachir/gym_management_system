// Copyright (c) 2022, Kossivi Amouzou and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Membership', {
	call_test_function: function(){
		frappe.call({
			method:"gym_management_system.gym_management_system.doctype.gym_membership.gym_membership.activity_registration",
			args: {
				"params": "params"
			},
			callback: function(r) {
				console.log(r)
			},
			freeze: true,
		});
	},
	refresh: function(frm) {
		/* Locker Management */
		frm.add_custom_button('Book',() =>{
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
						'gym_membership': frm.doc.name,
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

		},'Locker');

		frm.add_custom_button('Release',() =>{
			frappe.call({
				method:"gym_management_system.gym_management_system.doctype.gym_member.gym_member.release_locker",
				args: {
					"member": frm.doc.gym_member
				},
				callback: function(r) {
					
				},
				freeze: true,
			});
		},'Locker');

		/* Gym Programs */
		frm.add_custom_button('Trainer Subscription',() =>{
			new frappe.ui.form.MultiSelectDialog({
				doctype: "Gym Trainer",
				target: cur_frm,
				setters: {},
				add_filters_group: 1,
				date_field: "start_date",
				get_query() {
					return {
						filters: null
					}
				},
				action(selections, args) {
					const params = {
						doctype: 'Gym Workout Plan',
						parent_id: cur_frm.doc.name,
						ids: args.filtered_children,
						allow_child_item_selection: args.allow_child_item_selection,
					} ;
					frappe.call({
						method:"gym_management_system.gym_management_system.doctype.gym_membership.gym_membership.activity_registration",
						args: {
							params: params
						},
						callback: function(r) {
							console.log(r);
							frm.refresh_field('timing');
							frm.dirty();
                    		frm.refresh();
						},
						freeze: true,
					});
					
					console.log(params);
					cur_dialog.hide();
				},
				allow_child_item_selection: true,
				child_fieldname: "availability_details",
				child_columns: ["description","day","start_time","end_time"] // retorune name dans args.filtered_children	
			});
		},'Gym Programs');

		frm.add_custom_button('Class Booking',() =>{
			new frappe.ui.form.MultiSelectDialog({
				doctype: "Gym Class",
				target: cur_frm,
				setters: {
					class_name: null
				},
				columns: ["class_name"],
				add_filters_group: 1,
				date_field: "start_date",
				get_query() {
					return {
						filters: null
					}
				},
				action(selections, args) {
					const params = {
						doctype: 'Gym Class',
						parent_id: cur_frm.doc.name,
						ids: args.filtered_children,
						allow_child_item_selection: args.allow_child_item_selection,
					} ;
					frappe.call({
						method:"gym_management_system.gym_management_system.doctype.gym_membership.gym_membership.activity_registration",
						args: {
							params: params
						},
						callback: function(r) {
							console.log(r);
							cur_frm.refresh_field('timing');
							cur_frm.dirty();
                    		cur_frm.refresh();
						},
						freeze: true,
					});
					console.log(params);
					cur_dialog.hide();
				},
				allow_child_item_selection: true,
				child_fieldname: "gym_program",
				child_columns: ["gym_day","start_time","end_time"] // retourne name dans args.filtered_children	
			});

		},'Gym Programs');		
	}
});
