import re
import spacy
import PyPDF2
import requests
from io import BytesIO
from flask import Flask, request, jsonify, render_template, abort

# Initialize Flask app
app = Flask(__name__)

# -----------------------------
# Initialize NLP Model and Define Skills
# -----------------------------
nlp = spacy.load("en_core_web_sm")
SKILLS_LIST = skills = [
    "Python", "Jupyter", "Pandas", "NumPy", "SciPy", "Flask", "Django", "Pytest", "PyTorch",
    "Java", "Spring", "Spring Boot", "Hibernate", "JavaFX", "JSP", 
    "C++", "STL", "Boost", "CMake", "Qt", 
    "JavaScript", "ES6", "Node.js", "TypeScript", "jQuery", "Express.js",
    "SQL", "PostgreSQL", "MariaDB", "SQLite", "T-SQL", "NoSQL", "MongoDB", "Cassandra", 
    "Machine Learning", "Scikit-learn", "XGBoost", "LightGBM", "Keras", "OpenCV", 
    "Deep Learning", "Neural Networks", "CNNs", "RNNs", "GANs", "Reinforcement Learning",
    "NLP", "SpaCy", "NLTK", "Hugging Face Transformers", "NER", "Sentiment Analysis", 
    "Data Analysis", "Matplotlib", "Seaborn", "Tableau", "Power BI", 
    "TensorFlow", "TensorFlow Lite", "TensorFlow.js", "Keras", "TensorFlow Extended", 
    "PyTorch", "TorchVision", "TorchText", "TorchAudio", "PyTorch Lightning", 
    "Django", "Django REST Framework", "Django Channels", "Celery", 
    "Flask", "Flask RESTful", "Flask-SQLAlchemy", "Flask-JWT", "Flask-WTF",
    "ReactJS", "React Native", "Redux", "React Router", "Next.js", "JSX", 
    "Angular", "AngularJS", "Angular Material", "NgRx", 
    "Node.js", "Express.js", "NestJS", "Fastify", "Socket.io", 
    "AWS", "EC2", "S3", "Lambda", "RDS", "AWS Amplify", "DynamoDB", "AWS CloudFormation", 
    "Azure", "Azure Functions", "Azure Blob Storage", "Azure SQL Database", "Azure Kubernetes Service", "Azure Active Directory",
    "GCP", "Google App Engine", "Google Compute Engine", "BigQuery", "Firebase", "Google Kubernetes Engine",
    "HTML", "HTML5", "Semantic HTML", "Web Components", 
    "CSS", "CSS3", "Flexbox", "CSS Grid", "SASS", "LESS", "Bootstrap", 
    "MySQL", "MariaDB", "PostgreSQL", "MongoDB", "SQLite",
    "DevOps", "Docker", "Kubernetes", "Jenkins", "Terraform", "Ansible", "CI/CD", 
    "Cloud Computing", "AWS", "Google Cloud", "Microsoft Azure", "IBM Cloud", "Oracle Cloud",
    "Containerization", "Docker", "Kubernetes", "OpenShift", "Docker Compose", 
    "Big Data", "Apache Hadoop", "Apache Spark", "Apache Kafka", "Hive", "Pig", 
    "Blockchain", "Ethereum", "Solidity", "Hyperledger", "Cryptocurrency Development", 
    "UI/UX Design", "Figma", "Sketch", "Adobe XD", "InVision", "Wireframing", 
    "Cybersecurity", "Ethical Hacking", "Penetration Testing", "SIEM", "Firewalls and Network Security", "SSL/TLS Encryption", 
    "Mobile App Development", "Android", "Java", "Kotlin", "iOS", "Swift", "Flutter", "React Native", "Xamarin", 
    "Game Development", "Unity", "Unreal Engine", "C#", "Blender", "Cocos2d", 
    "Version Control", "Git", "GitHub", "GitLab", "Bitbucket", 
    "Automation", "Selenium", "Robot Framework", "AutoHotkey", "Cypress", 
    "Test Automation", "JUnit", "TestNG", "Mocha", "Jest", "Cypress", 
    "IoT", "Raspberry Pi", "Arduino", "MQTT", "Zigbee","PHP"
]


# -----------------------------
# Helper Function: Extract Text from PDF Bytes
# -----------------------------
def extract_text_from_pdf_bytes(file_bytes):
    """
    Extract text from PDF file bytes.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {e}")

# -----------------------------
# Helper Function: Extract Skills from Text
# -----------------------------
def extract_skills(text):
    """
    Extract skills from the text using a predefined list.
    """
    extracted_skills = set()
    for skill in SKILLS_LIST:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            extracted_skills.add(skill)
    return list(extracted_skills)

# -----------------------------
# API Endpoint: Parse Resume (File Upload) and Return JSON
# -----------------------------
@app.route('/parse_resume', methods=['POST'])
def parse_resume():
    """
    Accepts a PDF file via a multipart form upload and returns JSON data
    containing extracted skills and total experience.
    """
    if 'file' not in request.files:
        abort(400, description="No file part in the request.")

    file = request.files['file']
    if file.filename == "" or not file.filename.lower().endswith('.pdf'):
        abort(400, description="Please upload a valid PDF file.")

    try:
        file_bytes = file.read()
        text = extract_text_from_pdf_bytes(file_bytes)
        if not text:
            abort(400, description="No text could be extracted from the PDF.")
        # Extract skills and total experience
        skills = extract_skills(text)
        result = {
            "skills": skills,
        }
        return jsonify(result)
    except Exception as e:
        abort(500, description=str(e))

# -----------------------------
# API Endpoint: Parse Resume by PDF URL and Return JSON
# -----------------------------
@app.route('/parse_resume_url', methods=['GET'])
def parse_resume_url():
    """
    Accepts a PDF URL via a query parameter 'pdf_url' and returns JSON data
    containing extracted skills and total experience. The URL can point to a cloud storage location (HTTP/HTTPS)
    or a file system path.
    """
    pdf_url = request.args.get("pdf_url")
    if not pdf_url:
        abort(400, description="No PDF URL provided.")

    try:
        # Check if the URL is an HTTP URL; if not, assume it's a file system path
        if pdf_url.startswith("http"):
            response = requests.get(pdf_url)
            if response.status_code != 200:
                abort(400, description="Failed to fetch PDF from the provided URL.")
            file_bytes = response.content
        else:
            with open(pdf_url, "rb") as f:
                file_bytes = f.read()

        text = extract_text_from_pdf_bytes(file_bytes)
        if not text:
            abort(400, description="No text could be extracted from the PDF.")
        skills = extract_skills(text)
        result = {
            "skills": skills,
        }
        return jsonify(result)
    except Exception as e:
        abort(500, description=str(e))

# -----------------------------
# HTML Endpoint: Upload Form
# -----------------------------
@app.route('/upload', methods=['GET'])
def upload_page():
    """
    Renders an HTML page with a file upload form.
    """
    return render_template('upload.html')

# -----------------------------
# Main Entry Point
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)