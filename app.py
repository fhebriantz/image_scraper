from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import shutil
from scraper import scrape_images

app = Flask(__name__)

# Folder untuk menyimpan semua gambar
IMAGE_FOLDER = "static/images"

# Fungsi untuk menghapus semua gambar
def clear_images():
    if os.path.exists(IMAGE_FOLDER):
        shutil.rmtree(IMAGE_FOLDER)
    os.makedirs(IMAGE_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    images = []
    
    if request.method == "POST":
        username = request.form["username"]
        url = f'https://fapello.com/{username}/'
        start_page = int(request.form["start_page"])
        end_page = int(request.form["end_page"])

        # Jalankan scraping
        scrape_images(url, start_page, end_page)

        return redirect(url_for("index"))
    
    # Ambil daftar gambar dari folder
    if os.path.exists(IMAGE_FOLDER):
        images = [f"images/{img}" for img in os.listdir(IMAGE_FOLDER) if img.endswith((".jpg", ".png"))]

    return render_template("index.html", images=images)

@app.route("/reset", methods=["POST"])
def reset():
    clear_images()
    return jsonify({"message": "Semua gambar berhasil dihapus!"})

if __name__ == "__main__":
    app.run(debug=True)
