# Impor modul yang diperlukan dari Flask
from flask import Flask, render_template, url_for, send_from_directory
import os # Modul os membantu dengan path, meskipun dalam kasus ini mungkin tidak selalu wajib

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Set folder static secara eksplisit (opsional tapi disarankan untuk kejelasan)
# Flask akan mencari file statis di folder ini
app.static_folder = 'static'

# --- Rute Utama Halaman ---
# Rute untuk halaman utama (root URL '/')
@app.route('/')
def index():
    # Render file index.html dari folder templates
    # Pastikan index.html ada di dalam folder 'templates'
    return render_template('index.html')

# --- Rute untuk File SEO Teknis ---
# Rute untuk melayani robots.txt dari root domain (/robots.txt)
@app.route('/robots.txt')
def serve_robots():
    # Menggunakan send_from_directory untuk mengirim file dari folder static
    # 'robots.txt' adalah nama file yang dicari
    # mimetype='text/plain' menetapkan tipe konten respons
    # cache_timeout (opsional) mengatur durasi cache di browser/server
    return send_from_directory(app.static_folder, 'robots.txt', mimetype='text/plain')

# Rute untuk melayani sitemap.xml dari root domain (/sitemap.xml)
@app.route('/sitemap.xml')
def serve_sitemap():
    # Mengirim file sitemap.xml dari folder static
    # mimetype='application/xml' menetapkan tipe konten respons
    return send_from_directory(app.static_folder, 'sitemap.xml', mimetype='application/xml')

# --- Contoh Rute Lain (jika ada) ---
# Anda bisa menambahkan rute lain di sini jika proyek Anda berkembang
# @app.route('/tentang')
# def tentang():
#     return "Halaman Tentang"

# --- Menjalankan Aplikasi ---
# Kode di bawah ini hanya dijalankan saat script ini dieksekusi langsung
if __name__ == '__main__':
    # app.run() menjalankan server pengembangan Flask
    # debug=True: Mengaktifkan mode debug (untuk pengembangan)
    # Server akan otomatis me-reload jika ada perubahan kode
    # JANGAN GUNAKAN debug=True di lingkungan produksi!
    app.run(debug=True)