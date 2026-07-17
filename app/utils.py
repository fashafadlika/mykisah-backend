import smtplib
from email.message import EmailMessage

# Ganti dengan email dan App Password milikmu
SENDER_EMAIL = "auth.mykisah@gmail.com" 
SENDER_PASSWORD = "hdya voyv yrag hpjz" # 16 digit huruf acak tanpa spasi

def send_otp_email(recipient_email: str, otp_code: str):
    msg = EmailMessage()
    msg['Subject'] = "Kode OTP Verifikasi Akun Anda"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    
    # Isi pesan email
    msg.set_content(f"""
    Halo,
    
    Terima kasih telah mendaftar. Berikut adalah kode OTP verifikasi Anda:
    
    {otp_code}
    
    Kode ini hanya berlaku selama 5 menit. Jangan berikan kode ini kepada siapapun!
    """)

    # Proses mengirim email (menggunakan server SMTP Gmail)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Gagal mengirim email: {e}")