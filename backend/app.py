import os
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import PyPDF2
import pytesseract
from PIL import Image
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_image(file_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")

def analyze_engagement(text):
    """Analyze text and suggest engagement improvements using OpenAI"""
    try:
        # Check if API key is set
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # Fallback to basic analysis if no API key
            return get_basic_analysis(text)
        
        openai.api_key = api_key
        
        prompt = f"""Analyze the following social media content and provide specific engagement improvement suggestions.

Content:
{text[:2000]}  # Limit to 2000 chars to save tokens

Provide:
1. Overall engagement score (1-10)
2. Three specific suggestions to improve engagement
3. Tone analysis (e.g., professional, casual, enthusiastic)
4. Key strengths and weaknesses

Format your response as JSON with keys: score, suggestions (array), tone, strengths (array), weaknesses (array)"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a social media expert analyzing content for engagement optimization."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        import json
        analysis = json.loads(response.choices[0].message.content)
        return analysis
    
    except Exception as e:
        # Fallback to basic analysis
        return get_basic_analysis(text)

def get_basic_analysis(text):
    """Provide basic analysis when OpenAI is not available"""
    word_count = len(text.split())
    char_count = len(text)
    
    # Basic scoring
    score = 5
    if word_count > 50 and word_count < 200:
        score += 2
    if char_count > 0:
        score += 1
    
    suggestions = [
        "Consider adding more engaging hooks in the opening lines",
        "Use questions to encourage audience interaction",
        "Include relevant hashtags and mentions to increase reach"
    ]
    
    tone = "neutral"
    if any(word in text.lower() for word in ["exciting", "amazing", "great", "awesome"]):
        tone = "enthusiastic"
    elif any(word in text.lower() for word in ["please", "kindly", "appreciate"]):
        tone = "professional"
    
    strengths = ["Clear message delivery"]
    weaknesses = ["Could benefit from more engaging elements"]
    
    if word_count < 20:
        weaknesses.append("Content is too short for optimal engagement")
    
    return {
        "score": min(score, 10),
        "suggestions": suggestions,
        "tone": tone,
        "strengths": strengths,
        "weaknesses": weaknesses
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/analyze', methods=['POST'])
def analyze_content():
    """Main endpoint for file upload and analysis"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Save file securely
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text based on file type
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        if file_extension == 'pdf':
            extracted_text = extract_text_from_pdf(file_path)
        else:
            extracted_text = extract_text_from_image(file_path)
        
        # Check if text was extracted
        if not extracted_text or len(extracted_text.strip()) < 10:
            os.remove(file_path)
            return jsonify({"error": "No text could be extracted from the file"}), 400
        
        # Analyze engagement
        analysis = analyze_engagement(extracted_text)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Return results
        return jsonify({
            "extracted_text": extracted_text[:1000],  # Limit response size
            "full_text_length": len(extracted_text),
            "word_count": len(extracted_text.split()),
            "analysis": analysis
        }), 200
    
    except Exception as e:
        # Clean up file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({"error": str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
