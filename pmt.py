import requests
from fpdf import FPDF
import os

ACCESS_TOKEN = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwieC5vcmciOiJIMCJ9..UNCYTEJ670Ody4ZYURjWDA.NmnS4j0dPWLfyO1avKgIYDEkH2jWZZATKmsabokKObnHYk5Xd3peu3P7PDM1QSKVVRweHcjmxXobPxlpg4bxvnZ9eJnwpSp8dAGx31xx1RZz4KL9byW6p1OaP6xTLiBV3nHNpvmQbFic2MEdUD_mIHA3KnCXQcSNYEDsbDHHNUbx5AxiySuLA4xpOxllfhP2G-QZ9lWp5gf9zOAQ9N2kshhl-h6A6hkwgRSB44rGmYcNR84EMBqMzKfjVuwq4X9PFf02uQ5GxT3dq88dqWzjwzz1VhiUyqQatKAHhYOfqQWRMGQ34u-Qvmd15QP0XkFQMOc7PAaLoe1jr-2k_quXvXUbg79d9hvoq8St4zJiPAKO3jsdWPRC6QtD0pmrXS3CdI1uwa5wa7bH44w2xpB48Hl0GtUjzw_9vaIfjdXAHRBtlFUk7rhKY9UeJ9lhrEAESrBPyyyurLOJ6hm1VJjxK9OB2z03RmsSVV448yHf5CY20blFY3t1lnTEPJoO4eimLXEI1tegZS3BjG-PufxPt7O6Z68mQyxc5qoDQjpjb4n-kjvgeH-kXwIUanyeyxxaD05qCe1cH80KmJr5qFBX2XK71cbFt-VRGxcAP9-zGIABDYxnnJT6CAL-IyyVNboJ.y9pHfHhvvM-4WymQpcq1Rw"  # توکن معتبر
REALM_ID = "9341453609602712"
PAYMENT_ID = "101"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json"
}

# --- گرفتن Payment ---
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

# پیدا کردن شماره مرجع و Invoice
for line in payment.get("Line", []):
    for ex in line.get("LineEx", {}).get("any", []):
        if ex["value"].get("Name") == "txnReferenceNumber":
            reference_no = ex["value"].get("Value")
    for txn in line.get("LinkedTxn", []):
        if txn.get("TxnType") == "Invoice":
            invoice_id = txn.get("TxnId")

# یوزر ایجادکننده (در اکثر موارد خالی است)
user_name = "-"
meta = payment.get("MetaData", {})
if "CreateByRef" in meta and "name" in meta["CreateByRef"]:
    user_name = meta["CreateByRef"]["name"]

invoice_no = ""
product_services = []
product_amounts = []
invoice_total = ""
invoice_paid = float(amount_received) if amount_received else 0
invoice_balance = ""
invoice_date = ""
tax_amount = 0
discount_amt = 0

# --- گرفتن اطلاعات Invoice ---
if invoice_id:
    invoice_url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{REALM_ID}/invoice/{invoice_id}?minorversion=75"
    invoice_resp = requests.get(invoice_url, headers=headers)
    if invoice_resp.status_code == 200:
        invoice = invoice_resp.json().get("Invoice", {})
        invoice_no = invoice.get("DocNumber", "")
        invoice_total = invoice.get("TotalAmt", "")
        invoice_date = invoice.get("TxnDate", "")
        tax_amount = invoice.get("TxnTaxDetail", {}).get("TotalTax", 0)
        discount_amt = invoice.get("DiscountAmt", 0)
        for line in invoice.get("Line", []):
            if line.get("DetailType") == "SalesItemLineDetail":
                detail = line.get("SalesItemLineDetail", {})
                item_name = detail.get("ItemRef", {}).get("name", "")
                amount = line.get("Amount", 0)
                product_services.append(item_name)
                product_amounts.append(amount)
        invoice_balance = invoice.get("Balance", "")
    else:
        print("خطا در دریافت Invoice:", invoice_resp.text)

# ساخت لیست محصولات برای جدول
products_table = [(name, amt) for name, amt in zip(product_services, product_amounts)]

# مبلغ به حروف (نمونه ساده - اگر خواستی تبدیل اتوماتیک بنویسم)
amount_words = "two hundred twenty"  # یا تابع تبدیل عدد به حروف بگذار

# ========== ساخت PDF ==========
# فاصله‌ها (به میلیمتر) -- هر کدام جداگانه
top_margin = 30
space_after_table1 = 2
space_after_table2 = 5
space_after_table3 = 2
space_after_table4 = 12

pdf = FPDF(orientation="L", unit="mm", format="A5")
pdf.add_page()
pdf.set_auto_page_break(auto=False)

pdf.set_y(top_margin)

# --- جدول 1 ---
pdf.set_font("Arial", "", 12)
margin = 8
table_width = pdf.w - 2 * margin
col1_width = table_width * 0.70
col2_width = table_width * 0.30

row_height_table1 = 7  # ارتفاع هر خط در جدول 1

y = pdf.get_y()
x = margin
cell_1 = f"Received From\n{customer_name}"
cell_2 = f"Payment Date: {payment_date}\nReference no.: {reference_no}"

pdf.set_xy(x, y)
pdf.multi_cell(col1_width, row_height_table1, cell_1, border=0, align='L')
pdf.set_xy(x + col1_width, y)
pdf.multi_cell(col2_width, row_height_table1, cell_2, border=0, align='R')

pdf.ln(space_after_table1)


# --- جدول 2 ---
pdf.set_font("Arial", "", 12)
col1_width = table_width * 0.30
col2_width = table_width * 0.70
y = pdf.get_y()
x = margin
pdf.set_xy(x, y)
pdf.cell(col1_width, 10, f"Amount received: {amount_received} $", border=0, align='L')
pdf.cell(col2_width, 10, f"In words: {amount_words}", border=0, ln=1, align='L')

pdf.ln(space_after_table2)

# --- جدول 3 ---
col1_width = table_width * 0.70
col2_width = table_width * 0.30
header_height = 8
row_height = 6
y = pdf.get_y()
x = margin

pdf.set_font("Arial", "B", 12)
pdf.set_xy(x, y)
pdf.cell(col1_width, header_height, "Product/Service", border=0, align='L')
pdf.cell(col2_width, header_height, "Amount", border=0, ln=1, align='R')

pdf.set_font("Arial", "", 12)
for desc, amt in products_table:
    pdf.set_x(x)
    pdf.cell(col1_width, row_height, str(desc), border=0, align='L')
    pdf.cell(col2_width, row_height, str(amt), border=0, ln=1, align='R')

pdf.ln(space_after_table3)

# --- جدول 4 ---
pdf.set_font("Arial", "", 12)
y = pdf.get_y()
x = margin

cell_txt = f"Invoice Total: {invoice_total}\nPaid: {invoice_paid}\nBalance due: {invoice_balance}"
pdf.set_xy(x, y)
pdf.multi_cell(table_width, 8, cell_txt, border=0, align='R')

pdf.ln(space_after_table4)

# --- بخش نهایی: Created by ---
pdf.set_font("Arial", "I", 11)
pdf.cell(0, 10, f"Created by: {user_name}", ln=1, align='L')

save_folder = "downloads"
os.makedirs(save_folder, exist_ok=True)
pdf_path = os.path.join(save_folder, "cash_receipt_layout.pdf")
pdf.output(pdf_path)
print("PDF ذخیره شد:", pdf_path)
