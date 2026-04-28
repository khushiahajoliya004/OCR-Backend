import frappe
import requests


@frappe.whitelist()
def scan_card(file_url):
    settings = frappe.get_single("OCR API Settings")

    if not settings.enabled:
        frappe.throw("OCR Plugin is disabled. Enable it in OCR API Settings.")

    file_doc = frappe.get_doc("File", {"file_url": file_url})
    file_path = file_doc.get_full_path()

    api_url = f"{settings.api_base_url.rstrip('/')}/api/v1/ocr"
    api_key = settings.get_password("api_key")

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                api_url,
                headers={"x-api-key": api_key},
                files={"file": (file_doc.file_name, f, "image/jpeg")},
                timeout=int(settings.timeout_seconds or 30),
            )
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.Timeout:
        frappe.throw("OCR request timed out.")
    except requests.exceptions.RequestException as e:
        frappe.throw(f"OCR request failed: {str(e)}")

    frappe.get_doc({
        "doctype": "OCR Scan Log",
        "request_id": result.get("request_id"),
        "api_key_hint": (api_key or "")[:8] + "...",
        "status": "Success",
        "processing_time_ms": result.get("processing_time_ms"),
        "file_name": file_doc.file_name,
        "confidence": result.get("confidence"),
        "extracted_text": result.get("text"),
    }).insert(ignore_permissions=True)

    return result
