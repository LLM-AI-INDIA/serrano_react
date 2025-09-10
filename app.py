from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import io
import os
import shutil
from src.model import openai_model_with_mcp_tools
from src.reentry_care_plan import generate_reentry_care_plan, get_candidates_by_name
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

# Get candidates by name endpoint
@app.route('/get_candidates_by_name', methods=['POST'])
def get_candidates_endpoint():
    """Get all candidate profiles for a given name"""
    print("\n=== GET_CANDIDATES_BY_NAME ENDPOINT ===")
    try:
        data = request.get_json()
        print(f"📥 INPUT: {data}")
        candidate_name = data.get('candidate_name', '').strip()
        
        if not candidate_name:
            print("❌ ERROR: No candidate name provided")
            return jsonify({'error': 'Candidate name is required'}), 400
        
        print(f"🔍 SEARCHING for candidates with name: '{candidate_name}'")
        
        # Call the utility function
        print("🔧 CALLING get_candidates_by_name()...")
        candidates = get_candidates_by_name(candidate_name)
        print(f"📊 FOUND {len(candidates)} candidates: {candidates}")
        
        # Format response
        profiles = []
        for name, medical_id in candidates:
            profiles.append({
                'name': name,
                'medical_id': medical_id,
                'display_text': f"{name} (ID: {medical_id})"
            })
        
        result = {
            'success': True,
            'candidates': profiles,
            'count': len(profiles)
        }
        print(f"📤 OUTPUT: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ ERROR in get_candidates_endpoint: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        print("=== END GET_CANDIDATES_BY_NAME ===")

# Reentry Care Plan endpoint
@app.route('/generate_reentry_care_plan', methods=['POST'])
def generate_reentry_endpoint():
    """Handle Reentry Care Plan generation"""
    print("\n=== GENERATE_REENTRY_CARE_PLAN ENDPOINT ===")
    try:
        data = request.get_json()
        print(f"📥 INPUT: {data}")
        selected_fields = data.get('selected_fields', [])
        candidate_name = data.get('candidate_name', '')
        
        if not candidate_name:
            print("❌ ERROR: No candidate name provided")
            return jsonify({'error': 'Candidate name is required'}), 400
        
        if not selected_fields:
            print("❌ ERROR: No fields selected")
            return jsonify({'error': 'At least one field must be selected'}), 400
        
        print(f"🏗️ GENERATING Reentry Care Plan for '{candidate_name}'")
        print(f"📋 SELECTED FIELDS ({len(selected_fields)}): {selected_fields}")
        
        # Call your existing reentry function
        print("🔧 CALLING generate_reentry_care_plan()...")
        doc_io = generate_reentry_care_plan(selected_fields, candidate_name)
        
        if doc_io is None:
            print("❌ ERROR: Document generation failed")
            return jsonify({'error': 'Failed to generate care plan'}), 500
            
        print("📄 DOCUMENT generated successfully")
        
        # Save the document to a file for download
        output_path = "data/reentry_output.docx"
        with open(output_path, 'wb') as f:
            f.write(doc_io.getvalue())
        
        # Return the file for download
        filename = f"{candidate_name}_reentry_care_plan.docx"
        print(f"📤 SENDING FILE: {filename}")
        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        print(f"❌ ERROR in reentry endpoint: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        print("=== END GENERATE_REENTRY_CARE_PLAN ===")

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

# if __name__ == '__main__':
#     # Ensure data directory exists
#     os.makedirs('data', exist_ok=True)
#     os.makedirs('image', exist_ok=True)
    
#     # Get port from environment variable (for Cloud Run compatibility)
#     port = int(os.environ.get('PORT', 8080))
    
#     # Run the application (production settings)
#     app.run(debug=False, host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    os.makedirs('image', exist_ok=True)  # Ensure image directory exists
    
    # Get port from environment variable (for Cloud Run compatibility)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=port)