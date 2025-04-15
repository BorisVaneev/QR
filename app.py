from flask import Flask, render_template, render_template_string, request, send_file, jsonify
import qrcode
import io
import base64

app = Flask(__name__)

# Главная страница — обычный QR генератор
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
  <br>
  <a href="/tools">Перейти к инструментам</a>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    img_url = None
    if request.method == 'POST':
        text = request.form['text']
        img_url = f"/qr_image?text={text}"
    return render_template_string(HTML_TEMPLATE, img_url=img_url)

# Страница /tools с выбором цвета и размера
@app.route('/tools', methods=['GET', 'POST'])
def tools():
    img_url = None
    if request.method == 'POST':
        text = request.form['text']
        color = request.form.get('color', 'black')
        size = int(request.form.get('size', '10'))  # Преобразуем размер в число
        img_url = f"/qr_image?text={text}&color={color}&size={size}"
    return render_template('tools.html', img_url=img_url)

@app.route('/qr_image')
def qr_image():
    text = request.args.get('text', '')
    color = request.args.get('color', 'black')
    size = int(request.args.get('size', 10))  # Преобразуем размер в число

    # Определим минимальную версию QR в зависимости от размера
    version = 1
    if size >= 15:
        version = 2
    elif size >= 20:
        version = 3

    qr = qrcode.QRCode(
        version=version,  # Используем версию для определения размера
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,  # Размер клетки
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=color, back_color="white")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return send_file(img_bytes, mimetype='image/png')
# RapidAPI функция — остаётся!
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
    img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

    return jsonify({
        'text': text,
        'image_base64': img_base64,
        'content_type': 'image/png'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
