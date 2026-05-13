from flask import Flask, request, jsonify
import os
from main import process_receipt

app = Flask(__name__)

@app.route("/")
def home():
    return "Expense Audit API Running"

@app.route("/process", methods=["POST"])
def process():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    purpose = request.form.get("purpose", "")

    filename = file.filename   # now reliable

    file_path = "temp_" + filename
    file.save(file_path)

    claimed_date = request.form.get("claimed_date")
    
    try:
        result = process_receipt(file_path, purpose, claimed_date)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)