from flask import Flask, request, render_template_string, session, redirect, url_for
import pandas as pd
import openai
import os
import uuid
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'supersecret'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

BASE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Data Storyteller</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <style>
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3f37c9;
            --accent-color: #4cc9f0;
        }
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .btn-primary {
            background-color: var(--primary-color);
            border: none;
            padding: 10px 25px;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            background-color: var(--secondary-color);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.4);
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: white;
        }
        .upload-area:hover {
            border-color: var(--primary-color);
            background: rgba(67, 97, 238, 0.05);
        }
        .feature-icon {
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 1rem;
        }
        .header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 100px 0;
            margin-bottom: 50px;
            border-radius: 0 0 50% 50% / 0 0 50px 50px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark" style="background: var(--primary-color);">
        <div class="container">
            <a class="navbar-brand fw-bold" href="#">AI Data Storyteller</a>
        </div>
    </nav>

    <div class="container my-5">
        <div class="text-center mb-5">
            <h1 class="display-4 fw-bold mb-3">Transform Your Data into Compelling Stories</h1>
            <p class="lead text-muted">Upload your Excel or CSV file and let AI generate meaningful insights and narratives.</p>
        </div>

        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card p-4">
                    <div class="card-body">
                        <form method="POST" enctype="multipart/form-data" class="text-center">
                            <div class="upload-area mb-4" id="dropArea">
                                <i class="bi bi-cloud-arrow-up feature-icon"></i>
                                <h4>Drag & Drop your file here</h4>
                                <p class="text-muted">or click to browse files (Excel or CSV)</p>
                                <input type="file" name="file" id="fileInput" class="d-none" accept=".xlsx,.xls,.csv" required>
                                <button type="button" class="btn btn-outline-primary mt-3" onclick="document.getElementById('fileInput').click()">
                                    Select File
                                </button>
                                <div id="fileName" class="mt-2 fw-bold"></div>
                            </div>
                            <button type="submit" class="btn btn-primary btn-lg animate__animated animate__pulse animate__infinite">
                                <i class="bi bi-magic me-2"></i>Generate Insights
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-5">
            <div class="col-md-4 mb-4">
                <div class="card h-100 p-4 text-center">
                    <i class="bi bi-lightning-charge feature-icon"></i>
                    <h4>Quick Analysis</h4>
                    <p>Get instant insights from your data with our powerful AI engine.</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100 p-4 text-center">
                    <i class="bi bi-graph-up feature-icon"></i>
                    <h4>Visual Stories</h4>
                    <p>Transform complex data into easy-to-understand visual narratives.</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100 p-4 text-center">
                    <i class="bi bi-shield-lock feature-icon"></i>
                    <h4>Secure & Private</h4>
                    <p>Your data stays on your machine. We respect your privacy.</p>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-4 mt-5">
        <div class="container">
            <p class="mb-0"> 2023 AI Data Storyteller. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"></script>
    <script>
        // File input handling
        const fileInput = document.getElementById('fileInput');
        const dropArea = document.getElementById('dropArea');
        const fileName = document.getElementById('fileName');

        // Handle drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropArea.classList.add('border-primary');
            dropArea.style.borderWidth = '3px';
        }

        function unhighlight() {
            dropArea.classList.remove('border-primary');
            dropArea.style.borderWidth = '2px';
        }

        // Handle dropped files
        dropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        // Handle file selection
        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });

        function handleFiles(files) {
            if (files.length > 0) {
                const file = files[0];
                fileName.textContent = `Selected: ${file.name}`;
            }
        }
    </script>
</body>
</html>
'''

HTML_RESULT = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Preview - AI Data Storyteller</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            margin-top: 2rem;
        }
        .btn-primary {
            background-color: #4361ee;
            border: none;
            padding: 10px 25px;
            border-radius: 50px;
            font-weight: 600;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark" style="background: #4361ee;">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">AI Data Storyteller</a>
        </div>
    </nav>
    
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-10">
                <div class="card p-4">
                    <h2 class="text-center mb-4">Data Preview: {{ filename }}</h2>
                    <div class="table-responsive">
                        {{ table | safe }}
                    </div>
                    <form action="/analyze" method="POST">
                        <input type="hidden" name="filename" value="{{ filename }}">
                        <div class="text-center mt-4">
                            <button type="submit" class="btn btn-primary btn-lg">Generate Story</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

HTML_HEADER_SELECT = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Preview - AI Data Storyteller</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: #f8f9fa;
            padding-top: 2rem;
        }
        .data-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            padding: 2rem;
            margin-bottom: 2rem;
        }
        .table {
            background: white;
        }
        .table th {
            background: #f8f9fa;
            font-weight: 600;
        }
        .btn-primary {
            background-color: #4361ee;
            border: none;
            padding: 10px 25px;
            border-radius: 50px;
            font-weight: 600;
        }
        .btn-outline-secondary {
            border-radius: 50px;
            padding: 8px 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="text-center mb-5">
            <h1 class="display-5 fw-bold">Data Preview</h1>
            <p class="text-muted">Review your data before generating insights</p>
        </div>

        <div class="data-container">
            <div class="table-responsive">
                {{ table|safe }}
            </div>
        </div>

        <div class="text-center mt-4">
            <form method="POST" action="/analyze" class="d-inline-block me-2">
                <input type="hidden" name="filename" value="{{ filename }}">
                <button type="submit" class="btn btn-primary btn-lg">
                    <i class="bi bi-magic me-2"></i>Generate Insights
                </button>
            </form>
            <a href="/" class="btn btn-outline-secondary btn-lg">
                <i class="bi bi-arrow-left me-2"></i>Upload Different File
            </a>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
</body>
</html>
'''

HTML_INSIGHTS = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Generated Insights - Data Storyteller</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <style>
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3f37c9;
        }
        body {
            background: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }
        .insight-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-left: 4px solid var(--primary-color);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .insight-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .story-section {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .section-title {
            color: var(--primary-color);
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #eee;
        }
        .btn-primary {
            background-color: var(--primary-color);
            border: none;
            padding: 10px 25px;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            background-color: var(--secondary-color);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.4);
        }
        .btn-outline-secondary {
            border-radius: 50px;
            padding: 10px 25px;
        }
        .floating-buttons {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark" style="background: var(--primary-color);">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">AI Data Storyteller</a>
        </div>
    </nav>

    <div class="container my-5">
        <div class="text-center mb-5">
            <h1 class="display-4 fw-bold mb-3">Your Data Story</h1>
            <p class="lead text-muted">AI-powered insights and narratives from your data</p>
        </div>

        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="insight-card animate__animated animate__fadeIn">
                    <h3 class="section-title"> Key Insights</h3>
                    <div class="insights-content">
                        {{ insights|safe }}
                    </div>
                </div>

                <div class="story-section animate__animated animate__fadeIn" style="animation-delay: 0.2s">
                    <h3 class="section-title"> Data Story</h3>
                    <div class="story-content">
                        {{ story|safe }}
                    </div>
                </div>

                <div class="text-center mt-5">
                    <a href="/" class="btn btn-primary me-3">
                        <i class="bi bi-arrow-repeat me-2"></i>Analyze Another File
                    </a>
                    <button onclick="copyToClipboard()" class="btn btn-outline-secondary">
                        <i class="bi bi-clipboard me-2"></i>Copy Insights
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="floating-buttons">
        <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" class="btn btn-primary rounded-circle" style="width: 50px; height: 50px;">
            <i class="bi bi-arrow-up"></i>
        </button>
    </div>

    <footer class="bg-dark text-white text-center py-4 mt-5">
        <div class="container">
            <p class="mb-0"> 2023 AI Data Storyteller. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <script>
        function copyToClipboard() {
            const content = document.querySelector('.insights-content').innerText + '\n\n' + document.querySelector('.story-content').innerText;
            navigator.clipboard.writeText(content).then(() => {
                // Show a nice toast notification
                const toast = document.createElement('div');
                toast.className = 'position-fixed bottom-0 end-0 m-3 p-3 bg-success text-white rounded';
                toast.style.zIndex = '1100';
                toast.innerHTML = '<i class="bi bi-check-circle me-2"></i>Copied to clipboard!';
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);
            });
        }

        // Add animation to elements when they come into view
        const animateOnScroll = () => {
            const elements = document.querySelectorAll('.insight-card, .story-section');
            elements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                const windowHeight = window.innerHeight;
                if (elementTop < windowHeight - 100) {
                    element.classList.add('animate__fadeInUp');
                }
            });
        };

        window.addEventListener('scroll', animateOnScroll);
        // Initial check in case elements are already in view
        animateOnScroll();
    </script>
</body>
</html>
'''

def analyze_data(df):
    info = []

    # Dataset shape
    info.append(" Shape: {} rows × {} columns".format(df.shape[0], df.shape[1]))

    # Column names and types
    info.append("\n Column Info:")
    info.append(df.dtypes.to_string())

    # Missing values
    missing = df.isnull().sum()
    if missing.any():
        info.append("\n Missing Values:")
        info.append(missing[missing > 0].to_string())
    else:
        info.append("\n No missing values detected.")

    # Summary stats for numeric columns
    numeric_cols = df.select_dtypes(include='number')
    if not numeric_cols.empty:
        info.append("\n Summary Statistics (Numerics):")
        info.append(numeric_cols.describe().to_string())
    else:
        info.append("\n No numeric columns found.")

    return "\n\n".join(info)


def generate_story(insights):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Here is a dataset analysis:\n\n{insights}\n\nWrite a short, human-style data story with key findings."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful data analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return redirect(url_for('index'))

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.csv', '.xls', '.xlsx']:
            return "Unsupported file type"

        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Store file info in session
        session['filename'] = filename
        
        # Read the file for preview
        if ext == '.csv':
            df = pd.read_csv(filepath)
        else:  # Excel file
            df = pd.read_excel(filepath)
            
        # Convert to HTML and render with the result template
        return render_template_string(HTML_RESULT, 
                                   table=df.head(10).to_html(classes='table table-striped table-bordered table-hover'),
                                   filename=filename)
    
    # For GET request or if no file uploaded yet
    return render_template_string(BASE_HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'filename' not in request.form:
        return redirect(url_for('index'))
    
    filename = request.form['filename']
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Read the file
    if filename.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:  # Excel file
        df = pd.read_excel(filepath)
    
    # Generate insights and story
    insights = analyze_data(df)
    story = generate_story(insights)
    
    # Render the results
    return render_template_string(HTML_INSIGHTS, 
                               table=df.head(10).to_html(classes='table table-striped table-bordered table-hover'),
                               insights=insights, 
                               story=story)

if __name__ == '__main__':
    app.run(debug=True)
