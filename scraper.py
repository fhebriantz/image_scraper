import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor

def scrape_images(base_url, start_page, end_page):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    SAVE_DIR = "static/images"
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    for page in range(start_page, end_page + 1):
        url = f"{base_url}{page}/"
        print(f"📡 Membuka {url}...")
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))

        # Cari semua elemen gambar
        images = driver.find_elements(By.XPATH, f"//img[contains(@alt, 'Photo #{page}')]")
        selected_images = []

        for img in images:
            alt_text = img.get_attribute("alt")
            img_src = img.get_attribute("src")

            # Filter hanya gambar dengan alt mengandung "Photo #page"
            if alt_text and f"Photo #{page}" in alt_text and img_src:
                selected_images.append(img_src)

        # Download gambar yang sesuai
        for idx, img_url in enumerate(selected_images):
            try:
                response = requests.get(img_url, stream=True)
                if response.status_code == 200:
                    image_path = os.path.join(SAVE_DIR, f"image_{page}_{idx}.jpg")
                    with open(image_path, "wb") as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    print(f"✅ Gambar disimpan: {image_path}")
                    driver.execute_script("window.stop();")  # Menghentikan load halaman setelah mendapatkan gambar
            except Exception as e:
                print(f"❌ Gagal mengunduh gambar: {e}")

    driver.quit()
    print(f"🎉 Scraping selesai! Semua gambar telah diunduh.")
