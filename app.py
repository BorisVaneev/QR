import os
import io
import qrcode
import base64
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

# Настройки Cloudinary (замени своими данными)
cloudinary.config(
    cloud_name="dgtn0npco",
    api_key="925288137256823",
    api_secret="YY9bjM3pPVUGs_jodnsHyoHZPOk"
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/tools', methods=['GET', 'POST'])
def tools():
    img_url = None
    if request.method == 'POST':
        text = request.form['text']
        color = request.form.get('color', 'black')
        img_url = f"/qr_image?text={text}&color={color}"
    return render_template('tools.html', img_url=img_url)

@app.route('/monocle', methods=['GET', 'POST'])
def monocle():
    qr_url = None
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            try:
                upload_result = cloudinary.uploader.upload(file, resource_type="auto")
                image_url = upload_result['secure_url']
                qr_url = f"/qr_image?text={image_url}"
            except Exception as e:
                return f"Ошибка при загрузке на Cloudinary: {e}", 500
        else:
            return "Пожалуйста, выберите изображение или PDF", 400

    return render_template('monocle.html', img_url=qr_url)

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
    app.run(debug=True)
