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
    page = int(request.args.get("page", 1))
    search_query = request.args.get("query", "").lower()  # Ambil query dari frontend
    per_page = 10  # Jumlah gambar per halaman

    if os.path.exists(IMAGE_FOLDER):
        images = [f"images/{img}" for img in os.listdir(IMAGE_FOLDER) if img.endswith((".jpg", ".png"))]
        images.sort()  # Urutkan agar lebih rapi

        # Jika ada pencarian, filter hasilnya
        if search_query:
            images = [img for img in images if search_query in img.lower()]

        # Pagination (ambil subset dari daftar gambar)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_images = images[start:end]
    else:
        paginated_images = []

    return jsonify(paginated_images)

@app.route("/reset", methods=["POST"])
def reset():
    """Menghapus semua gambar di folder."""
    clear_images()
    return jsonify({"message": "Semua gambar berhasil dihapus!"})

if __name__ == "__main__":
    app.run(debug=True)
