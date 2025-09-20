import os, time, subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def generate_pdf_report(device, method, passes, sha_before, sha_after, status, start_ts, end_ts):
    os.makedirs("reports", exist_ok=True)
    ts = int(start_ts)
    path = f"reports/wipe_report_{ts}.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    c.drawString(50, 800, "SIH25070 - Secure Wipe Report")
    c.drawString(50, 780, f"Device: {device}")
    c.drawString(50, 760, f"Method: {method} (passes={passes})")
    c.drawString(50, 740, f"Start: {time.ctime(start_ts)}")
    c.drawString(50, 720, f"End: {time.ctime(end_ts)}")
    c.drawString(50, 700, f"Status: {status}")
    c.drawString(50, 680, f"SHA before: {sha_before}")
    c.drawString(50, 660, f"SHA after : {sha_after}")
    c.save()
    return path

def sign_report_with_openssl(pdf_path, private_key="keys/private.pem"):
    sig_path = pdf_path + ".sig"
    subprocess.run(
        ["openssl","dgst","-sha256","-sign",private_key,"-out",sig_path,pdf_path],
        check=True
    )
    return sig_path
