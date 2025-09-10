# MuseCrwler Web App

A minimal web app that fetches and displays random human portrait images from a Google Photos shared album. If no images are found, it automatically falls back to free sources like Pixabay, Unsplash, and Lorem Picsum.

## Features
- Scrapes images from a Google Photos shared link using Selenium.
- Displays a random image in a modern, centered canvas.
- Fetch button loads a new random image.
- Fullscreen button for immersive viewing.
- Loading animation while fetching images.
- Fallback to Pixabay, Unsplash, and Lorem Picsum if no images are found.
- No repeat images until all have been shown.

## Setup
1. Clone the repository.
2. Install Python dependencies:
   ```
   pip install flask selenium python-dotenv requests
   ```
3. Download ChromeDriver and add it to your PATH.
4. Add your Pixabay API key to `.env`:
   ```
   PIXABAY_API_KEY=your_pixabay_api_key_here
   ```
5. Run the app:
   ```
   python webapp/app.py
   ```
6. Open `http://localhost:5000` in your browser.

## Configuration
- The Google Photos link is set directly in `app.py`.
- `.env` is used for the Pixabay API key only.

## Free Image Sources
- [Google Photos](https://photos.google.com/)
- [Pixabay](https://pixabay.com/api/docs/)
- [Unsplash](https://unsplash.com/developers)
- [Lorem Picsum](https://picsum.photos/)

## License
MIT
