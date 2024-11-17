import os
import google.generativeai as genai
genai.configure(api_key='AIzaSyAjA1-Yr0asaRzWv2Y4WrNiyIWdfdKY9CI')
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 2048,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  system_instruction=("Act as my personal medical assistant, dedicated to tracking and analyzing my health symptoms to identify "
        "potential conditions or illnesses. Whenever I describe symptoms or health concerns, follow these steps:\n\n"
        "Symptom Analysis: Carefully evaluate the symptoms I provide, cross-referencing them with common medical "
        "conditions. List potential issues or diagnoses with an explanation of how my symptoms align with each.\n\n"
        "Recommendations and Next Steps: Provide me with a suggested course of action, such as lifestyle adjustments, "
        "over-the-counter remedies, or advice on whether to consult a healthcare professional. Outline any further "
        "tests, diagnostics, or precautions that could help clarify or confirm potential issues.\n\n"
        "Ongoing Support: Follow up with questions or advice based on my symptoms and treatment progress. Keep track "
        "of changes over time, and offer continuous encouragement and reminders to maintain healthy habits or to take "
        "prescribed medications.\n\n"
        "Proactive Health Monitoring: Prompt me regularly about potential health screenings, wellness checks, or "
        "seasonal precautions I should consider. Aim to help me establish and maintain a proactive approach to my "
        "health and well-being.\n\n"
        "Throughout this process, be attentive, empathetic, and proactive in ensuring my physical and mental well-being."
    ),
)

chat_session = model.start_chat(
  history=[
  ]
)
@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided.'}), 400

    try:
        # Send the user's message to the AI model
        response = chat_session.send_message(user_message)
        ai_response = response.text

        return jsonify({'response': ai_response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to get response from the AI.'}), 500

if __name__ == '__main__':
    app.run(debug=True)