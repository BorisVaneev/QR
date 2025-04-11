from flask import Flask, render_template_string, request, send_file
import qrcode
import io

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

@app.route('/', methods=['GET', 'POST'])
def home():
    img_url = None
    
    if request.method == 'POST':
        text = request.form['text']
        
        # Генерация QR-кода
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохранение в память
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        img_url = f"/qr_image?text={text}"
    
    return render_template_string(HTML_TEMPLATE, img_url=img_url)

@app.route('/qr_image')
def qr_image():
    text = request.args.get('text', '')
    
    # Повторная генерация для скачивания
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

if __name__ == '__main__':
    app.run()
