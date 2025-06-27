import requests
from tabulate import tabulate  # این پکیج رو باید نصب داشته باشی

ACCESS_TOKEN = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwieC5vcmciOiJIMCJ9..biPurUU6Ad_BWNMChBsBug.mqSdNqQvz0FNb4wI9Axe2K3Z3bqktOSKCvGimN2r8v0xreSxHe85GL68ElXgx2smNFZKulD2_jde5BgDn6YHB89mGleiRm286SpCPCpL0toH13QfTPg_5vaInbiw-OPM2GpbwkqmWkO2LvjNgS0fiRrotBw0PSaBehrUvaCe5yRHxD0XdBVOom68jVDJohikwjL5d4emLpuT-RJzfmVYe5e1W-F4sKuKFf7e6y9UabWDTpuejXhxeyWgoyP070etAgGkVP9IkyfzA44GsTBNs2kfwSiNdQy7nsFojMIRs_-Qu-goZwH0Dh5AasrV0eByy5GDxmxZPVj9TJPH2R_RC9oCd7jRXctrirNmtXeMJEiriyGZEsviEPvW4OAYK0KaUZmm_RhyBMtuh1Nxic1QOvYLNFTCze3sJTYRqcOMfPpo_xZVHwG0a8jebP-s-FX0GIWQGLarvsTmbv6KD29GQKmZFKJ8sb9cMKVlhA9MvIa9NwI3ErLS_oNySnkIll_ZtcKnP0DFNyFz8y23v9oSvXB4gbmeyx8dqhJirfjnVfjEeD9Qfv08Y3CpY3WXi3Lvz99vJ7y2_fe3gD0T2qx8HCuNWZdCsOEJlKLHDVlWGKQhlnihPO-DeTc0f0xJnpOT.lMYaaALHalPZVgC1TY486Q"  # Access Token
REALM_ID = "9341453609602712"
PAYMENT_ID = "101"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json"
}

# گرفتن Payment
payment_url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{REALM_ID}/payment/{PAYMENT_ID}?minorversion=75"
payment_resp = requests.get(payment_url, headers=headers)
if payment_resp.status_code != 200:
    print("خطا در گرفتن Payment:", payment_resp.text)
    exit()

payment = payment_resp.json().get("Payment", {})
customer_name = payment.get("CustomerRef", {}).get("name", "")
payment_date = payment.get("TxnDate", "")
reference_no = None
amount_received = payment.get("TotalAmt", "")
invoice_id = None

# پیدا کردن شماره مرجع و انویس
for line in payment.get("Line", []):
    for ex in line.get("LineEx", {}).get("any", []):
        if ex["value"].get("Name") == "txnReferenceNumber":
            reference_no = ex["value"].get("Value")
    for txn in line.get("LinkedTxn", []):
        if txn.get("TxnType") == "Invoice":
            invoice_id = txn.get("TxnId")

invoice_no = ""
product_services = []

# اگر Invoice وصل شده وجود داشت اطلاعاتش رو هم بگیر
if invoice_id:
    invoice_url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{REALM_ID}/invoice/{invoice_id}?minorversion=75"
    invoice_resp = requests.get(invoice_url, headers=headers)
    if invoice_resp.status_code == 200:
        invoice = invoice_resp.json().get("Invoice", {})
        invoice_no = invoice.get("DocNumber", "")
        for line in invoice.get("Line", []):
            detail = line.get("SalesItemLineDetail", {})
            item_name = detail.get("ItemRef", {}).get("name", "")
            if item_name:
                product_services.append(item_name)
    else:
        print("خطا در دریافت Invoice:", invoice_resp.text)

# جدول فیلدهای دلخواه
table = [
    ["Customer Display Name", customer_name],
    ["Payment Date", payment_date],
    ["Reference no.", reference_no],
    ["Amount received", amount_received],
    ["Invoice no.", invoice_no],
    ["Product/service", "، ".join(product_services) if product_services else "-"],
]

print(tabulate(table, headers=["Field", "Value"], tablefmt="fancy_grid"))
