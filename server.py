from flask import Flask, request, jsonify, render_template
import requests
app = Flask(__name__)

GEMINI_API_KEY = 'AIzaSyCcyaERy2bxQvsH6AF5eGRPIDku9My5v9U'

NEIGHBORHOOD_WATCH_KEYWORDS = [
    # Core terms
    "neighborhood watch", "neighbourhood watch", "community watch", "block watch",
    "citizen patrol", "crime prevention", "community safety", "neighborhood security", "neigh",
    "neighbor" , "neigbor","neighborr","neighbur", "neigbur","neighborhod",
    
    # Activities
    "patrol", "surveillance", "observation", "monitoring", "vigilance",
    "watch program", "safety program", "crime watch", "security patrol",
    
    # Reporting
    "report", "reporting", "incident", "suspicious", "suspicious activity",
    "suspicious person", "unusual", "stranger", "unknown vehicle", "crime report",
    "police report", "emergency", "non-emergency", "911", "dispatch",
    
    # Crime types
    "burglary", "theft", "vandalism", "graffiti", "trespassing", "loitering",
    "break-in", "robbery", "assault", "package theft", "car theft", "bike theft",
    "property crime", "violent crime", "drug activity", "prostitution", "gang activity","crime","Crime"
    
    # Safety measures
    "prevention", "deterrent", "lighting", "street lights", "security cameras",
    "alarm system", "locks", "deadbolt", "window locks", "security system",
    "safety tips", "crime prevention tips", "home security", "property security",
    
    # Community
    "community meeting", "town hall", "block party", "neighborhood meeting",
    "safety meeting", "police meeting", "community alert", "neighborhood alert",
    "email alert", "text alert", "phone tree", "neighborhood network",
    
    # Organization
    "volunteer", "coordinator", "organize", "schedule", "patrol schedule",
    "duty roster", "sign up", "participate", "join", "membership",
    "leadership", "block captain", "zone captain", "district coordinator",
    
    # Law enforcement
    "police", "sheriff", "deputy", "officer", "law enforcement",
    "police department", "sheriff's office", "crime statistics",
    "crime map", "crime data", "police report", "incident report",
    
    # Emergency
    "emergency", "fire", "medical emergency", "ambulance", "paramedic",
    "hazard", "danger", "urgent", "immediate", "life-threatening",
    
    # Suspicious indicators
    "strange", "unfamiliar", "unattended", "package", "vehicle",
    "person", "behavior", "activity", "loitering", "peering",
    "casing", "scouting", "photographing", "sketching",
    
    # Technology
    "ring camera", "security camera", "doorbell camera", "motion lights",
    "smart lights", "alarm", "sensor", "app", "notification", "alert system",
    
    # Communication
    "newsletter", "facebook group", "whatsapp group", "nextdoor",
    "social media", "email list", "text alerts", "phone chain",
    
    # Training
    "training", "workshop", "seminar", "certification", "cpr",
    "first aid", "self defense", "safety training", "awareness",
    
    # Vulnerable groups
    "elderly", "seniors", "children", "school", "playground",
    "park", "recreation area", "community center",
    
    # Environmental design
    "cpted", "environmental design", "landscaping", "visibility",
    "natural surveillance", "territorial reinforcement", "access control",
    
    # Seasonal
    "holiday safety", "vacation", "travel", "winter", "summer",
    "holiday crime", "seasonal crime", "daylight savings"
]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').lower()
    is_relevant = any(keyword in user_message for keyword in NEIGHBORHOOD_WATCH_KEYWORDS)
    if not is_relevant:
        return jsonify({
            'response': (
                "🚫 I only handle Neighborhood Watch queries. Please ask about:\n\n"
                "🔹 Organizing watch programs\n"
                "🔹 Reporting suspicious activity\n"
                "🔹 Crime prevention tips\n"
                "🔹 Community safety strategies\n\n"
                "How can I help with neighborhood safety?"
            )
        })
    prompt = (
        "As a Neighborhood Watch expert, provide concise, structured advice about: " + user_message + "\n\n"
        "Format requirements:\n"
        "1. MAX 3-5 key points\n"
        "2. Use bullet points (🔹) only\n"
        "3. Include relevant emojis\n"
        "4. Keep entire response under 150 words\n"
        "5. Use ONLY plain text with line breaks, NO markdown\n"
        "6. Skip introductions/conclusions\n\n"
        "Example format:\n"
        "🔹 Home Security - Lock doors/windows 🔒, use security lights 💡\n"
        "🔹 Neighborhood Awareness - Report suspicious activity 👮♂️\n"
        "🚨 Emergency: Call 911 for immediate threats"
    )
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        response_data = response.json()
        
        if not response_data.get('candidates'):
            raise ValueError("No candidates in response")
            
        first_candidate = response_data['candidates'][0]
        if not first_candidate.get('content'):
            raise ValueError("No content in candidate")
            
        parts = first_candidate['content'].get('parts', [])
        if not parts:
            raise ValueError("No parts in content")
            
        bot_response = parts[0].get('text', "I couldn't generate a response. Please try again.")
        bot_response = (
            bot_response.replace('•', '🔹')
            .replace('-', '🔹')
            .replace('**', '')  
            .replace('*', '')   
            .strip()
        )
        
    except requests.exceptions.Timeout:
        bot_response = "⏳ Timeout Error\n\nOur safety service is taking too long to respond. Please try again later."
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {str(e)}")
        bot_response = "🔴 Service Unavailable\n\nOur safety service is temporarily down. For emergencies, contact local authorities."
    except ValueError as e:
        print(f"Response Parsing Error: {str(e)}")
        bot_response = "⚠️ Response Error\n\nCouldn't process safety information. Please try again."
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        bot_response = "⚠️ Technical Error\n\nPlease try your safety question again."

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)