import qrcode
import os  # Добавляем эту строку

def generate_qrcode(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrimg.png")

# Исправленная строка:
url = os.getenv("NAME", "default_user")  # Теперь правильно!
generate_qrcode(url)
