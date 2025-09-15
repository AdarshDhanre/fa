import os
import pytesseract
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

# If Tesseract is not in PATH, set it manually:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    if "prescriptionFile" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["prescriptionFile"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # OCR: Extract text from image
        try:
            text = pytesseract.image_to_string(Image.open(filepath))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        # Simple fake detection logic (you can replace with ML model)
        if "fake" in text.lower() or "invalid" in text.lower():
            result = {
                "status": "Fraud",
                "details": "Suspicious words found in prescription",
                "extracted_text": text.strip(),
            }
        else:
            result = {
                "status": "Verified",
                "details": "No suspicious patterns detected",
                "extracted_text": text.strip(),
            }

        return jsonify(result)

    return jsonify({"error": "File type not allowed"}), 400


if __name__ == "__main__":
    app.run(debug=True)
