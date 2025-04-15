import requests
import os
from flask import Flask, render_template, request, send_file, jsonify
import qrcode
import io
import base64

app = Flask(__name__)

# Вставь сюда свой Imgur Client ID
IMGUR_CLIENT_ID = "ff5c7d74ca974aa"

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
    qr_url = None
    if request.method == 'POST':
        image = request.files.get('image')  # Получаем файл изображения
        if image:
            # Отправка изображения на Imgur
            imgur_url = 'https://api.imgur.com/3/upload'
            headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
            files = {'image': image.read()}
            data = {'image': files['image']}
            response = requests.post(imgur_url, headers=headers, data=data)

            if response.status_code == 200:
                img_data = response.json()
                img_url = img_data['data']['link']
                # Генерация QR-кода с ссылкой на изображение
                qr_url = f"/qr_image?text={img_url}"
            else:
                return "Ошибка при загрузке изображения на Imgur", 500
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
