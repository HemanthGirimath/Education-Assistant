from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from redis_client import redis_client
from config import config
from services.pdf_processor import extract_text_from_pdf
from services.chat_service import chat_with_pdf
from services.quiz_service import generate_quiz
from services.teach_service import teach_me
from services.study_guide_service import generate_study_guide

from services.pdf_service import get_pdf_text
from services.summarize_service import summarize_lecture

app = Flask(__name__)
app.config.from_object(config)
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_path)

        # Save file path & text in Redis (for session tracking)
        user_id = session.get("user_id", "default_user")  # Temporary user session
        redis_client.hset(f"user:{user_id}:pdfs", filename, extracted_text)

        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200

    return jsonify({"error": "Invalid file type"}), 400

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query")
    filename = data.get("filename")

    response = chat_with_pdf(filename, query)
    print("Sending Response to Frontend:", response)  # Debugging

    return jsonify({"answer": response})  # Ensure response is wrapped in 'answer'


@app.route("/generate_quiz", methods=["POST"])
def generate_quiz_route():
    data = request.json
    filename = data.get("filename")
    start_topic = data.get("start_topic")
    end_topic = data.get("end_topic")

    if not filename or not start_topic or not end_topic:
        return jsonify({"error": "Filename, start_topic, and end_topic are required"}), 400

    user_id = session.get("user_id", "default_user")
    pdf_text = redis_client.hget(f"user:{user_id}:pdfs", filename)

    if not pdf_text:
        return jsonify({"error": "PDF not found"}), 404

    quiz = generate_quiz(pdf_text, start_topic, end_topic)
    return jsonify({"quiz": quiz}), 200

@app.route("/teach_me", methods=["POST"])
def teach_me_route():
    data = request.json
    filename = data.get("filename")
    topic = data.get("topic")

    if not filename or not topic:
        return jsonify({"error": "Filename and topic are required"}), 400

    user_id = session.get("user_id", "default_user")
    pdf_text = redis_client.hget(f"user:{user_id}:pdfs", filename)

    if not pdf_text:
        return jsonify({"error": "PDF not found"}), 404

    lesson = teach_me(pdf_text, topic)
    return jsonify({"lesson": lesson}), 200


@app.route("/generate_study_guide", methods=["POST"])
def generate_study_guide_route():
    data = request.json
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    user_id = session.get("user_id", "default_user")
    pdf_text = redis_client.hget(f"user:{user_id}:pdfs", filename)

    if not pdf_text:
        return jsonify({"error": "PDF not found"}), 404

    study_guide = generate_study_guide(pdf_text)
    return jsonify({"study_guide": study_guide}), 200

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    pdf_text = get_pdf_text(filename)
    if not pdf_text:
        return jsonify({"error": "Could not extract text from PDF"}), 400

    summary = summarize_lecture(pdf_text)
    return jsonify({"summary": summary})
if __name__ == "__main__":
    app.run(debug=True)
