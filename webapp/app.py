
from flask import Flask, jsonify, send_from_directory
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import os

from dotenv import load_dotenv
import requests

app = Flask(__name__)

# Load environment variables from .env file

load_dotenv()
GOOGLE_PHOTOS_URL = "https://photos.google.com/share/AF1QipOemNZIoHICM9H-sPKepGpkpMcJBri7EPEdTvUGR8BgVtNTGG518EQ9IYlW2jd_jQ?key=WS11NEN4Wi16QzdUdnEwODJsY3JpQUxHMlJqd0FB"
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# For demo, cache scraped URLs in memory

# Store all possible images and shown images
image_urls = []
shown_images = set()

def scrape_image_urls():
    global image_urls
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(GOOGLE_PHOTOS_URL)
    driver.implicitly_wait(5)

    # Scroll to load more images (simulate user scrolling)
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(5):  # Scroll 5 times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Find all img tags
    imgs = driver.find_elements("tag name", "img")
    urls = []
    for img in imgs:
        src = img.get_attribute("src")
        try:
            width = int(img.get_attribute("width") or 0)
            height = int(img.get_attribute("height") or 0)
        except Exception:
            width = height = 0
        if src and width > 100 and height > 100:
            urls.append(src)
    driver.quit()
    image_urls = urls

@app.route('/api/random-image')
def random_image():
    global shown_images
    if not image_urls:
        scrape_image_urls()
    available_images = [u for u in image_urls if u not in shown_images]
    if not available_images:
        # Reset history if all images shown
        shown_images = set()
        available_images = image_urls.copy()
    if available_images:
        # Pick a random image
        url = random.choice(available_images)
        shown_images.add(url)

        # Try to get enhanced version from Google Photos
        enhanced_url = None
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(GOOGLE_PHOTOS_URL)
            driver.implicitly_wait(3)
            # Find the image element by src
            img_elem = None
            imgs = driver.find_elements("tag name", "img")
            for img in imgs:
                if img.get_attribute("src") == url:
                    img_elem = img
                    break
            if img_elem:
                img_elem.click()
                driver.implicitly_wait(5)
                # Wait for enhanced image to load
                import time
                time.sleep(3)
                # Find the largest image now visible
                imgs = driver.find_elements("tag name", "img")
                max_area = 0
                for img in imgs:
                    src = img.get_attribute("src")
                    try:
                        width = int(img.get_attribute("width") or 0)
                        height = int(img.get_attribute("height") or 0)
                    except Exception:
                        width = height = 0
                    area = width * height
                    if src and area > max_area:
                        max_area = area
                        enhanced_url = src
                driver.quit()
        except Exception:
            enhanced_url = None
        # If enhanced image found and different, use it
        if enhanced_url and enhanced_url != url:
            return jsonify({"url": enhanced_url})
        # If not, fallback to Pixabay if not loaded in 3 seconds
        # Try Pixabay
        if PIXABAY_API_KEY:
            pixabay_url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q=Human+Portrait&image_type=photo&orientation=vertical&per_page=50"
            try:
                resp = requests.get(pixabay_url)
                data = resp.json()
                pixabay_images = [hit['webformatURL'] for hit in data.get('hits', []) if 'webformatURL' in hit]
                pixabay_images = [u for u in pixabay_images if u not in shown_images]
                if pixabay_images:
                    url = random.choice(pixabay_images)
                    shown_images.add(url)
                    return jsonify({"url": url})
            except Exception:
                pass
        # Try Unsplash
        try:
            unsplash_url = "https://source.unsplash.com/featured/?portrait,person"
            # Unsplash returns a redirect to a random image
            resp = requests.get(unsplash_url, allow_redirects=False)
            if resp.status_code == 302:
                unsplash_img = resp.headers.get('Location')
                if unsplash_img and unsplash_img not in shown_images:
                    shown_images.add(unsplash_img)
                    return jsonify({"url": unsplash_img})
        except Exception:
            pass
        # Try Lorem Picsum
        try:
            picsum_url = "https://picsum.photos/600/800"
            resp = requests.get(picsum_url, allow_redirects=False)
            if resp.status_code == 302:
                picsum_img = resp.headers.get('Location')
                if picsum_img and picsum_img not in shown_images:
                    shown_images.add(picsum_img)
                    return jsonify({"url": picsum_img})
        except Exception:
            pass
        # Otherwise, show the original image
        return jsonify({"url": url})
    else:
        return jsonify({"error": "No images found from Google Photos or Pixabay."}), 404

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
