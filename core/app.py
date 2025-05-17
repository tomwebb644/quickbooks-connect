from flask import Flask, request, jsonify, render_template
from PIL import Image
import pytesseract
from openai import OpenAI
import os

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))


client = OpenAI()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    image = Image.open(file.stream)
    extracted_text = pytesseract.image_to_string(image)

    hours_data = parse_with_gpt(extracted_text)
    return jsonify(hours_data)

def parse_with_gpt(raw_text):
    prompt = f"""
    From the following work log text, extract dates and hours worked. Subtract any lunch/break time mentioned. Format:
    [{{"date": "YYYY-MM-DD", "hours": number}}]

    Text:
    {raw_text}
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    output = response.choices[0].message.content
    try:
        return eval(output) if output.startswith('[') else {"result": output}
    except:
        return {"result": output}

if __name__ == "__main__":
    app.run(debug=True)
