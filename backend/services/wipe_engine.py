import subprocess, time, hashlib
from db.database import init_db, insert_log
from utils.report import generate_pdf_report, sign_report_with_openssl

init_db()

def list_drives():
    try:
        out = subprocess.check_output(
            ["lsblk","-J","-o","NAME,KNAME,TYPE,SIZE,MODEL,ROTA,MOUNTPOINT"],
            text=True
        )
        return {"ok": True, "lsblk": out}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _sha256_head(device_path, head_bytes=1024*1024):
    try:
        with open(device_path, "rb") as f:
            return hashlib.sha256(f.read(head_bytes)).hexdigest()
    except:
        return None

def run_shred(device, passes=3, force=False):
    if not force:
        raise RuntimeError("force=True required for destructive ops")
    subprocess.run(["shred","-v","-n",str(passes),"-z",device], check=True)

def run_dd_zeros(device, passes=1, force=False):
    if not force:
        raise RuntimeError("force=True required for destructive ops")
    for _ in range(passes):
        subprocess.run(
            f"dd if=/dev/zero of={device} bs=1M status=progress conv=fsync",
            shell=True, check=True
        )

def run_hdparm_secure_erase(device, force=False):
    if not force:
        raise RuntimeError("force=True required for destructive ops")
    pw = "SIHpass"
    subprocess.run(["hdparm","--user-master","u","--security-set-pass",pw,device], check=True)
    subprocess.run(["hdparm","--security-erase",pw,device], check=True)

def run_nvme_format(device, force=False):
    if not force:
        raise RuntimeError("force=True required for destructive ops")
    subprocess.run(["nvme","format",device,"--ses=1"], check=True)

def initiate_wipe(device, method, passes=1, force=False):
    start = time.time()
    sha_before = _sha256_head(device)
    status = "started"
    try:
        if method=="shred":
            run_shred(device, passes, force)
        elif method=="dd_zero":
            run_dd_zeros(device, passes, force)
        elif method=="hdparm_secure_erase":
            run_hdparm_secure_erase(device, force)
        elif method=="nvme_format":
            run_nvme_format(device, force)
        else:
            raise ValueError("Unknown method")
        status = "success"
    except Exception as e:
        status = f"failed: {e}"
    end = time.time()
    sha_after = _sha256_head(device)
    report = generate_pdf_report(device, method, passes, sha_before, sha_after, status, start, end)
    try:
        sig = sign_report_with_openssl(report)
    except:
        sig = None
    insert_log(device, method, passes, start, end, sha_before, sha_after, status, report)
    return {"report": report, "sig": sig, "status": status}
