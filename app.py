from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import shutil
from scraper import scrape_images
import math

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

@app.route("/get_filters", methods=["GET"])
def get_filters():
    """Menghasilkan daftar filter berdasarkan jumlah gambar dalam folder"""
    if os.path.exists(IMAGE_FOLDER):
        images = [img for img in os.listdir(IMAGE_FOLDER) if img.endswith((".jpg", ".png"))]
        images.sort()
        total_images = len(images)
        max_range = math.ceil(total_images / 100)  # Hitung kelipatan 100
        filters = [f"{i*100+1}-{(i+1)*100}" for i in range(max_range)]
    else:
        filters = []

    return jsonify(filters)


@app.route("/load_images", methods=["GET"])
def load_images():
    page = int(request.args.get("page", 1))
    search_query = request.args.get("query", "").lower()
    filter_range = request.args.get("filter", "")
    per_page = 10  # Set jumlah gambar per halaman

    if os.path.exists(IMAGE_FOLDER):
        images = [img for img in os.listdir(IMAGE_FOLDER) if img.endswith((".jpg", ".png"))]
        images.sort()

        # Filter berdasarkan pencarian nama file
        if search_query:
            images = [img for img in images if search_query in img.lower()]

        # Filter berdasarkan rentang angka di nama file (image_X_0.jpg)
        if filter_range:
            start, end = map(int, filter_range.split("-"))
            images = [img for img in images if any(img.startswith(f"image_{i}_") for i in range(start, end + 1))]

        # Pagination (Infinite Scroll)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_images = images[start_idx:end_idx]
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
