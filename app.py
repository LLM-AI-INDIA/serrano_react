from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import io
import os
import shutil
from src.model import openai_model_with_mcp_tools
from src.reentry_care_plan import generate_reentry_care_plan
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app with static folder for frontend
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Serve frontend files
@app.route('/')
def serve_frontend():
    """Serve the main HTML file"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/app.js')
def serve_js():
    """Serve the JavaScript file"""
    return send_from_directory(app.static_folder, 'app.js')

# Serve image files
@app.route('/image/<path:filename>')
def serve_images(filename):
    """Serve images from the image directory"""
    try:
        return send_from_directory('image', filename)
    except FileNotFoundError:
        return jsonify({'error': 'Image not found'}), 404

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

# Reentry Care Plan endpoint
@app.route('/generate_reentry_care_plan', methods=['POST'])
def generate_reentry_endpoint():
    """Handle Reentry Care Plan generation"""
    try:
        data = request.get_json()
        selected_fields = data.get('selected_fields', [])
        candidate_name = data.get('candidate_name', '')
        
        if not candidate_name:
            return jsonify({'error': 'Candidate name is required'}), 400
        
        if not selected_fields:
            return jsonify({'error': 'At least one field must be selected'}), 400
        
        print(f"Generating Reentry Care Plan for {candidate_name} with fields: {selected_fields}")
        
        # Call your existing reentry function
        doc_io = generate_reentry_care_plan(selected_fields, candidate_name)
        
        if doc_io is None:
            return jsonify({'error': 'Failed to generate care plan'}), 500
        
        # Save the document to a file for download
        output_path = "data/reentry_output.docx"
        with open(output_path, 'wb') as f:
            f.write(doc_io.getvalue())
        
        # Return the file for download
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{candidate_name}_reentry_care_plan.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        print(f"Error in reentry endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# Adult Health Risk Assessment endpoint
@app.route('/generate_hra_adult', methods=['POST'])
def generate_hra_adult_endpoint():
    """Handle Adult HRA generation using OpenAI MCP tools"""
    try:
        data = request.get_json()
        selected_fields = data.get('selected_fields', [])
        candidate_name = data.get('candidate_name', '')
        
        if not candidate_name:
            return jsonify({'error': 'Candidate name is required'}), 400
        
        if not selected_fields:
            return jsonify({'error': 'At least one field must be selected'}), 400
        
        print(f"Generating Adult HRA for {candidate_name} with fields: {selected_fields}")
        
        # Call your OpenAI MCP function
        result = openai_model_with_mcp_tools(selected_fields, candidate_name)
        
        if isinstance(result, dict):
            # If successful, the function already generated the DOCX via json_to_docx_append_vertical_tables
            output_path = "data/output.docx"  # This is where document_pre.py saves the file
            
            if not os.path.exists(output_path):
                return jsonify({'error': 'Document generation failed - output file not created'}), 500
            
            # Rename the file for this specific use case
            final_path = f"data/{candidate_name}_adult_hra.docx"
            
            # Copy the generated file to the final path
            shutil.copy(output_path, final_path)
            
            return send_file(
                final_path,
                as_attachment=True,
                download_name=f"{candidate_name}_adult_hra.docx",
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        else:
            # If there was an error, return it
            return jsonify({'error': f'Failed to generate HRA: {result}'}), 500
            
    except Exception as e:
        print(f"Error in adult HRA endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# Juvenile Health Risk Assessment endpoint
@app.route('/generate_hra_juvenile', methods=['POST'])
def generate_hra_juvenile_endpoint():
    """Handle Juvenile HRA generation using OpenAI MCP tools"""
    try:
        data = request.get_json()
        selected_fields = data.get('selected_fields', [])
        candidate_name = data.get('candidate_name', '')
        
        if not candidate_name:
            return jsonify({'error': 'Candidate name is required'}), 400
        
        if not selected_fields:
            return jsonify({'error': 'At least one field must be selected'}), 400
        
        print(f"Generating Juvenile HRA for {candidate_name} with fields: {selected_fields}")
        
        # Call your OpenAI MCP function
        result = openai_model_with_mcp_tools(selected_fields, candidate_name)
        
        if isinstance(result, dict):
            # If successful, the function already generated the DOCX via json_to_docx_append_vertical_tables
            output_path = "data/output.docx"  # This is where document_pre.py saves the file
            
            if not os.path.exists(output_path):
                return jsonify({'error': 'Document generation failed - output file not created'}), 500
            
            # Rename the file for this specific use case
            final_path = f"data/{candidate_name}_juvenile_hra.docx"
            
            # Copy the generated file to the final path
            shutil.copy(output_path, final_path)
            
            return send_file(
                final_path,
                as_attachment=True,
                download_name=f"{candidate_name}_juvenile_hra.docx",
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        else:
            # If there was an error, return it
            return jsonify({'error': f'Failed to generate HRA: {result}'}), 500
            
    except Exception as e:
        print(f"Error in juvenile HRA endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors by serving the frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    os.makedirs('image', exist_ok=True)
    
    # Get port from environment variable (for Cloud Run compatibility)
    port = int(os.environ.get('PORT', 8080))
    
    # Run the application (production settings)
    app.run(debug=False, host='0.0.0.0', port=port)

# if __name__ == '__main__':
#     # Ensure data directory exists
#     os.makedirs('data', exist_ok=True)
#     os.makedirs('image', exist_ok=True)  # Ensure image directory exists
    
#     # Get port from environment variable (for Cloud Run compatibility)
#     port = int(os.environ.get('PORT', 5000))
    
#     # Run the application
#     app.run(debug=True, host='0.0.0.0', port=port)