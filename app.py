import qrcode
from flask import Flask, send_file, request
import os
import io

app = Flask(__name__)

@app.route('/')
def home():
    # Получаем текст из параметра URL (?text=Привет) или переменной окружения
    text = request.args.get('text', os.getenv("QR_TEXT", "default_text"))
    
    # Генерируем QR-код в памяти (без сохранения в файл)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохраняем изображение в байтовый поток
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Отправляем изображение как файл
    return send_file(img_bytes, mimetype='image/png')

if __name__ == '__main__':
    app.run()
