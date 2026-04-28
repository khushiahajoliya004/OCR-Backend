// Adds "Scan Visiting Card" button to Contact and Lead forms

frappe.ui.form.on("Contact", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Scan Visiting Card"), () => show_ocr_dialog(frm), __("OCR"));
		}
	},
});

frappe.ui.form.on("Lead", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Scan Visiting Card"), () => show_ocr_dialog(frm), __("OCR"));
		}
	},
});

function show_ocr_dialog(frm) {
	const d = new frappe.ui.Dialog({
		title: __("Scan Visiting Card"),
		fields: [
			{
				label: __("Card Image (JPG / PNG)"),
				fieldname: "card_image",
				fieldtype: "Attach Image",
				reqd: 1,
			},
		],
		primary_action_label: __("Scan"),
		primary_action(values) {
			frappe.call({
				method: "ocr_plugin.ocr_plugin.api.scan_card",
				args: { file_url: values.card_image },
				freeze: true,
				freeze_message: __("Scanning card…"),
				callback(r) {
					if (r.message && r.message.status === "success") {
						d.hide();
						show_result_dialog(frm, r.message);
					}
				},
			});
		},
	});
	d.show();
}

function show_result_dialog(frm, data) {
	const d = new frappe.ui.Dialog({
		title: __("Extracted Card Data"),
		fields: [
			{
				label: __("Extracted Text"),
				fieldname: "extracted_text",
				fieldtype: "Small Text",
				default: data.text,
				read_only: 1,
			},
			{
				label: __("Confidence"),
				fieldname: "confidence",
				fieldtype: "Data",
				default: (data.confidence * 100).toFixed(1) + "%",
				read_only: 1,
			},
			{
				label: __("Processing Time"),
				fieldname: "proc_time",
				fieldtype: "Data",
				default: data.processing_time_ms + " ms",
				read_only: 1,
			},
		],
		primary_action_label: __("Save Text to Notes"),
		primary_action() {
			frm.set_value("notes", data.text);
			frm.save();
			d.hide();
			frappe.show_alert({ message: __("OCR text saved to Notes"), indicator: "green" });
		},
		secondary_action_label: __("Discard"),
		secondary_action() {
			d.hide();
		},
	});
	d.show();
}
