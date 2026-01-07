"""
PDF Combiner Web Application
A simple Flask app to combine multiple PDF files
"""
from flask import Flask, render_template, request, send_file, jsonify
from pypdf import PdfMerger
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/combine', methods=['POST'])
def combine_pdfs():
    """Combine multiple PDF files"""
    try:
        # Check if files were uploaded
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files[]')
        output_filename = request.form.get('filename', 'combined.pdf')
        
        # Ensure output filename ends with .pdf
        if not output_filename.endswith('.pdf'):
            output_filename += '.pdf'
        
        # Secure the filename
        output_filename = secure_filename(output_filename)
        
        # Validate that we have at least 2 files
        if len(files) < 2:
            return jsonify({'error': 'Please upload at least 2 PDF files'}), 400
        
        # Validate all files are PDFs
        for file in files:
            if file.filename == '':
                return jsonify({'error': 'One or more files have no name'}), 400
            if not allowed_file(file.filename):
                return jsonify({'error': f'Invalid file type: {file.filename}. Only PDF files are allowed'}), 400
        
        # Create a temporary directory for uploaded files
        temp_dir = tempfile.mkdtemp()
        uploaded_files = []
        
        # Save uploaded files temporarily
        for file in files:
            temp_path = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(temp_path)
            uploaded_files.append(temp_path)
        
        # Combine PDFs
        merger = PdfMerger()
        
        for pdf_file in uploaded_files:
            merger.append(pdf_file)
        
        # Save combined PDF
        output_path = os.path.join(temp_dir, output_filename)
        merger.write(output_path)
        merger.close()
        
        # Clean up uploaded files
        for file_path in uploaded_files:
            try:
                os.remove(file_path)
            except (OSError, FileNotFoundError):
                pass
        
        # Send the combined PDF
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    # Note: For production use, set debug=False and use a production WSGI server like gunicorn
    # Example: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
