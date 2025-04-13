from flask import Flask, render_template_string, request, send_file, jsonify
import qrcode
import io
import base64

app = Flask(__name__)

# HTML-шаблон с формой
HTML_TEMPLATE = """
<!doctype html>
<html>
<head><title>Генератор QR-кодов</title></head>
<body>
  <h1>Создать QR-код</h1>
  <form method="POST">
    <input type="text" name="text" placeholder="Введите текст" required>
    <button type="submit">Сгенерировать</button>
  </form>
  {% if img_url %}
    <h2>Ваш QR-код:</h2>
    <img src="{{ img_url }}" width="300">
    <br>
    <a href="{{ img_url }}" download="qrcode.png">Скачать</a>
  {% endif %}
</body>
</html>
"""

# Главная страница — HTML генератор
@app.route('/', methods=['GET', 'POST'])
def home():
    img_url = None

    if request.method == 'POST':
        text = request.form['text']
        img_url = f"/qr_image?text={text}"

    return render_template_string(HTML_TEMPLATE, img_url=img_url)

# Изображение QR-кода по тексту (для отображения и скачивания)
@app.route('/qr_image')
def qr_image():
    text = request.args.get('text', '')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return send_file(img_bytes, mimetype='image/png')

# API для RapidAPI — возвращает base64 QR-кода
@app.route('/api/qrcode', methods=['POST'])
def api_qrcode():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" field'}), 400

    text = data['text']

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Преобразование в base64
    img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

    return jsonify({
        'text': text,
        'image_base64': img_base64,
        'content_type': 'image/png'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
