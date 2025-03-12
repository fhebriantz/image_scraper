from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import shutil
from scraper import scrape_images

app = Flask(__name__)

# Folder tempat menyimpan gambar
IMAGE_FOLDER = "static/images"
PER_PAGE = 10  # Jumlah gambar yang dimuat per permintaan

# Fungsi untuk menghapus semua gambar
def clear_images():
    if os.path.exists(IMAGE_FOLDER):
        shutil.rmtree(IMAGE_FOLDER)
    os.makedirs(IMAGE_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        url = f'https://fapello.com/{username}/'
        start_page = int(request.form["start_page"])
        end_page = int(request.form["end_page"])

        # Jalankan scraping
        scrape_images(url, start_page, end_page)

        return redirect(url_for("index"))

    return render_template("index.html")  # Tidak mengirim gambar langsung

@app.route("/load_images")
def load_images():
    """Mengambil gambar secara bertahap untuk infinite scroll."""
    page = int(request.args.get("page", 1))  # Halaman yang diminta
    if not os.path.exists(IMAGE_FOLDER):
        return jsonify([])

    images = sorted(
        [f"images/{img}" for img in os.listdir(IMAGE_FOLDER) if img.endswith((".jpg", ".png"))]
    )

    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    paginated_images = images[start:end]

    return jsonify(paginated_images)  # Mengirim gambar sesuai halaman

@app.route("/reset", methods=["POST"])
def reset():
    """Menghapus semua gambar di folder."""
    clear_images()
    return jsonify({"message": "Semua gambar berhasil dihapus!"})

if __name__ == "__main__":
    app.run(debug=True)
