import cloudinary
import cloudinary.uploader
import os
from flask import Flask, render_template, request, send_file, jsonify
import qrcode
import io
import base64

app = Flask(__name__)

# Конфигурация Cloudinary
cloudinary.config(
    cloud_name="Monocle",  # Ваш Cloud Name
    api_key="925288137256823",  # Ваш API Key
    api_secret="YY9bjM3pPVUGs_jodnsHyoHZPOk",  # Ваш API Secret
)

# Главная страница — Генератор QR-кодов
@app.route('/', methods=['GET', 'POST'])
def home():
    img_url = None

    if request.method == 'POST':
        text = request.form['text']
        img_url = f"/qr_image?text={text}"

    return render_template('home.html', img_url=img_url)

# Страница с инструментами — для выбора цвета
@app.route('/tools', methods=['GET', 'POST'])
def tools():
    img_url = None
    if request.method == 'POST':
        text = request.form['text']
        color = request.form.get('color', 'black')

        img_url = f"/qr_image?text={text}&color={color}"

    return render_template('tools.html', img_url=img_url)

# Страница для генерации QR-кодов для изображений (например, меню)
@app.route('/monocle', methods=['GET', 'POST'])
def monocle():
    img_url = None
    if request.method == 'POST':
        image = request.files.get('image')  # Получаем файл изображения
        if image:
            # Отправка изображения на Cloudinary
            try:
                response = cloudinary.uploader.upload(image)
                img_url = response['url']  # Получаем URL изображения на Cloudinary
                # Генерация QR-кода с ссылкой на изображение
                qr_url = f"/qr_image?text={img_url}"
            except Exception as e:
                return f"Ошибка при загрузке изображения на Cloudinary: {str(e)}", 500
        else:
            return "Пожалуйста, выберите изображение", 400

    return render_template('monocle.html', img_url=qr_url)

# Генерация QR-изображения по ссылке или тексту
@app.route('/qr_image')
def qr_image():
    text = request.args.get('text', '')
    color = request.args.get('color', 'black')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=color, back_color="white")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return send_file(img_bytes, mimetype='image/png')

# API для генерации QR-кодов
@app.route('/api/qrcode', methods=['POST'])
def api_qrcode():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" field'}), 400

    text = data['text']
    color = data.get('color', 'black')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=color, back_color="white")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

    return jsonify({
        'text': text,
        'image_base64': img_base64,
        'content_type': 'image/png'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
