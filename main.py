from flask import Flask, render_template, request, send_file
import PyPDF2
import pdfkit
import re

app = Flask(__name__)

# -----------------------------
# EMAIL DETECTION
# -----------------------------
def detect_email(text):
    text = text.lower()

    keywords = [
        "win","winner","prize","lottery","money","free",
        "urgent","verify","bank","click here"
    ]

    score = sum(word in text for word in keywords) * 20
    score = min(score, 100)

    if score >= 60:
        result = f"Scam Detected ({score}%)"
    elif score >= 30:
        result = f"Suspicious ({score}%)"
    else:
        result = f"Safe ({score}%)"

    return result


# -----------------------------
# URL DETECTION
# -----------------------------
def detect_url(url):
    url = url.lower()

    if "login" in url or "verify" in url:
        return "phishing (80%)"
    elif ".xyz" in url:
        return "malware (90%)"
    else:
        return "safe (10%)"


# -----------------------------
@app.route('/')
def home():
    return render_template("index.html")


# -----------------------------
@app.route('/scam/', methods=['POST'])
def scam():

    file = request.files['file']
    text = ""

    if file.filename.endswith('.txt'):
        text = file.read().decode("utf-8", errors="ignore")

    elif file.filename.endswith('.pdf'):
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()

    result = detect_email(text)

    return render_template("index.html", message=result)


# -----------------------------
@app.route('/predict', methods=['POST'])
def predict():

    url = request.form.get('url')
    result = detect_url(url)

    return render_template("index.html",
                           predicted_class=result,
                           input_url=url)


# -----------------------------
@app.route('/download_report')
def download_report():

    result = request.args.get('result', 'Safe')

    # Extract score
    match = re.search(r'(\d+)%', result)
    score = int(match.group(1)) if match else 0

    # Color logic
    if score >= 70:
        color = "#ff4d4d"
    elif score >= 40:
        color = "#ffa500"
    else:
        color = "#4caf50"

    rendered = render_template(
        "report.html",
        result=result,
        score=score,
        color=color
    )

    config = pdfkit.configuration(
        wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )

    pdfkit.from_string(rendered, "report.pdf", configuration=config)

    return send_file("report.pdf", as_attachment=True)


# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
