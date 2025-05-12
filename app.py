from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import requests
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT') or 587)
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'False').lower() in ['true', '1', 't']
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME'))

from flask_mail import Mail, Message

mail = Mail(app)

RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

app.static_folder = 'static'

@app.route('/')
def index():
    error = request.args.get('error')
    success = request.args.get('success')
    return render_template('index.html', error=error, success=success)

@app.route('/robots.txt')
def serve_robots():
    return send_from_directory(app.static_folder, 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def serve_sitemap():
    return send_from_directory(app.static_folder, 'sitemap.xml', mimetype='application/xml')

@app.route('/kirim-pesan', methods=['POST'])
def kirim_pesan():
    nama = request.form.get('nama')
    email = request.form.get('email')
    pesan = request.form.get('pesan')
    recaptcha_response = request.form.get('g-recaptcha-response')

    if not nama or not email or not pesan:
        print("Error: Data formulir tidak lengkap.")
        return redirect(url_for('index', error="Mohon lengkapi semua kolom formulir."))

    if not recaptcha_response:
        print("Error: reCAPTCHA response missing!")
        return redirect(url_for('index', error="Mohon selesaikan verifikasi reCAPTCHA."))

    verification_payload = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }

    try:
        response = requests.post(VERIFY_URL, data=verification_payload)
        response.raise_for_status()
        result = response.json()

        if result.get('success'):
            print("reCAPTCHA verification successful!")
            try:
                RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')
                if not RECIPIENT_EMAIL:
                     print("Error: RECIPIENT_EMAIL environment variable not set!")
                     return redirect(url_for('index', error="Kesalahan konfigurasi server (email penerima)."))

                msg = Message(subject=f"Pesan Baru dari Portofolio - {nama}",
                              recipients=[RECIPIENT_EMAIL],
                              sender=app.config.get('MAIL_DEFAULT_SENDER'))
                msg.body = f"""
Anda menerima pesan baru dari formulir kontak di portofolio Anda:

Nama: {nama}
Email: {email}
Pesan:
{pesan}
"""
                mail.send(msg)
                print("Email berhasil dikirim!")

                return redirect(url_for('index', success="Pesan Anda berhasil dikirim!"))

            except Exception as e:
                print(f"Error sending email: {e}")
                return redirect(url_for('index', error="Terjadi kesalahan saat mengirim pesan. Mohon coba lagi nanti."))

        else:
            print("reCAPTCHA verification failed:", result.get('error-codes'))
            return redirect(url_for('index', error="Verifikasi reCAPTCHA gagal. Mohon coba lagi."))

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to reCAPTCHA verification API: {e}")
        return redirect(url_for('index', error="Terjadi kesalahan server saat memverifikasi reCAPTCHA."))

    except Exception as e:
        print(f"An unexpected error occurred during form processing: {e}")
        return redirect(url_for('index', error="Terjadi kesalahan tak terduga."))

if __name__ == '__main__':
    required_env_vars = ['RECAPTCHA_SECRET_KEY', 'MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'RECIPIENT_EMAIL']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

    if missing_vars:
         print("\n" + "="*50)
         print("!!! PERINGATAN: Variabel Lingkungan Belum Lengkap !!!")
         print("Untuk menjalankan aplikasi ini secara lokal dengan fitur email/reCAPTCHA,")
         print("variabel lingkungan berikut harus diset di file .env Anda:")
         for var in missing_vars:
             print(f"- {var}")
         print("Fitur email dan/atau reCAPTCHA mungkin tidak berfungsi tanpa variabel ini.")
         print("="*50 + "\n")
    else:
        print("\nVariabel lingkungan yang dibutuhkan terdeteksi. Menjalankan aplikasi...")
        print(f"MAIL_SERVER: {os.environ.get('MAIL_SERVER')}")
        print(f"MAIL_PORT: {os.environ.get('MAIL_PORT')}")
        print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
        print(f"MAIL_USERNAME: {os.environ.get('MAIL_USERNAME')}")
        print(f"RECIPIENT_EMAIL: {os.environ.get('RECIPIENT_EMAIL')}")
        print(f"RECAPTCHA_SECRET_KEY: {'*' * len(os.environ.get('RECAPTCHA_SECRET_KEY')) if os.environ.get('RECAPTCHA_SECRET_KEY') else 'None'}")

    app.run(debug=True)
