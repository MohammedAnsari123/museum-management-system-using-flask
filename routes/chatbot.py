from flask import Blueprint, request, jsonify, render_template
from modules.chatbot_logic import get_chatbot_response

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
        
    try:
        response = get_chatbot_response(query)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return jsonify({'error': 'Failed to process request. Please check database/model Status.'}), 500

@chatbot_bp.route('/chat')
def chat_interface():
    return render_template('chatbot_full.html')
