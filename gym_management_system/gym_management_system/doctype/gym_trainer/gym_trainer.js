// Copyright (c) 2022, Kossivi Amouzou and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Trainer', {
	setup: function(frm) {
        //frm.get_field('availability_details').grid.cannot_add_rows = true;
        frm.get_field("availability_details").grid.only_sortable();
    },

    before_save: function (frm) {
        return frappe.call({
            method: 'gym_management_system.gym_management_system.doctype.gym_trainer.gym_trainer.get_availability',
            args: { "name": frm.doc.name, },
            callback: function(r, rt){
                if (r.message) {
					//frm.doc.availability_details.clear()
                    frm.clear_table("availability_details");
					console.log(r.message);
                    r.message.forEach(e => {
                        var row = frm.add_child('availability_details');
                        row.day = e.gym_day,
                        row.start_time = e.start_time,
                        row.end_time = e.end_time
                        row.workout_plan = e.workout_plan;
                        row.description = e.description;
                    });

                    frm.refresh_field('availability_details');
                    frm.dirty();
                    frm.refresh();
                }

            }

        });

    },

});


 

frappe.ui.form.on("Gym Trainer","onload", function(frm, cdt, cdn) {
    var df = frappe.meta.get_docfield("Gym Trainer Availability Details","workout_plan", cur_frm.doc.name);
    df.read_only = 1;
    df = frappe.meta.get_docfield("Gym Trainer Availability Details","description", cur_frm.doc.name);
    df.read_only = 1;
    df = frappe.meta.get_docfield("Gym Trainer Availability Details","day", cur_frm.doc.name);
    df.read_only = 1;
    df = frappe.meta.get_docfield("Gym Trainer Availability Details","start_time", cur_frm.doc.name);
    df.read_only = 1;
    df = frappe.meta.get_docfield("Gym Trainer Availability Details","end_time", cur_frm.doc.name);
    df.read_only = 1;
});
