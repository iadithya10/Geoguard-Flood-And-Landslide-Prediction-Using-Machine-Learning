import os
import random
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory, Response

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "disaster_awareness_key")

# Emergency helpline data
emergency_contacts = {
    "National": [
        {"name": "National Emergency Number", "number": "112"},
        {"name": "National Disaster Response Force (NDRF)", "number": "011-24363260"},
        {"name": "Disaster Management Division", "number": "011-23092923"},
        {"name": "Police", "number": "100"},
        {"name": "Fire", "number": "101"},
        {"name": "Ambulance", "number": "102"},
    ],
    "Andhra Pradesh": [
        {"name": "Disaster Management", "number": "1070"},
        {"name": "State Emergency Operation Center", "number": "0863-2377201"},
    ],
    "Assam": [
        {"name": "Disaster Management", "number": "1070"},
        {"name": "State Emergency Operation Center", "number": "0361-2237221"},
    ],
    "Bihar": [
        {"name": "Disaster Management", "number": "1070"},
        {"name": "State Emergency Operation Center", "number": "0612-2294204"},
    ],
    "Gujarat": [
        {"name": "Disaster Management", "number": "1070"},
        {"name": "State Emergency Operation Center", "number": "079-23251900"},
    ],
    "Kerala": [
        {"name": "Disaster Management", "number": "1070"},
        {"name": "State Emergency Operation Center", "number": "0471-2364424"},
    ],
    "Maharashtra": [
        {"name": "Disaster Management", "number": "1070"},
        {"name": "State Emergency Operation Center", "number": "022-22694725"},
    ],
    "Tamil Nadu": [
        {"name": "Disaster Management", "number": "1070"},
        {"name": "State Emergency Operation Center", "number": "044-28593990"},
    ],
    "Uttarakhand": [
        {"name": "Disaster Management", "number": "1070"},
        {"name": "State Emergency Operation Center", "number": "0135-2710334"},
    ],
    "West Bengal": [
        {"name": "Disaster Management", "number": "1070"},
        {"name": "State Emergency Operation Center", "number": "033-22143526"},
    ]
}

# Educational videos data
videos_data = {
    "Flood Awareness": [
        {
            "title": "Flood Safety Tips",
            "embed_code": "https://www.youtube.com/embed/43M5mZuzHF8",
            "description": "Important safety tips to remember during flood situations."
        },
        {
            "title": "Understanding Flood Warnings",
            "embed_code": "https://www.youtube.com/embed/4PXj7bOD7IY",
            "description": "How to interpret flood warnings and take appropriate action."
        }
    ],
    "Earthquake Awareness": [
        {
            "title": "Earthquake Safety and Preparedness",
            "embed_code": "https://www.youtube.com/embed/BLEPakj1YTY",
            "description": "Essential tips and guidelines for earthquake safety and preparedness."
        },
        {
            "title": "What To Do During an Earthquake",
            "embed_code": "https://www.youtube.com/embed/dJpIU1rSOFY",
            "description": "Step-by-step guide on what to do when an earthquake strikes."
        }
    ],
    "Tsunami Awareness": [
        {
            "title": "Tsunami Warning Signs",
            "embed_code": "https://www.youtube.com/embed/V0s2i7Cc7wA",
            "description": "Recognizing tsunami warning signs and taking quick action."
        }
    ]
}

# Quiz questions
quiz_questions = [
    {
        "question": "What should you do first in case of a flood warning?",
        "options": [
            "Stay where you are",
            "Move to higher ground",
            "Call friends",
            "Go swimming"
        ],
        "answer": 1
    },
    {
        "question": "Which of these is NOT a sign of an impending landslide?",
        "options": [
            "Cracks appearing in the ground",
            "Doors or windows sticking",
            "Clear blue skies",
            "Water seeping from hillsides"
        ],
        "answer": 2
    },
    {
        "question": "During an earthquake, what is the recommended action?",
        "options": [
            "Run outside",
            "Stand near windows",
            "Drop, cover, and hold on",
            "Use elevators to evacuate"
        ],
        "answer": 2
    },
    {
        "question": "What natural warning sign may indicate an approaching tsunami?",
        "options": [
            "Heavy rainfall",
            "A rapid recession of water from the shore",
            "Fog",
            "High winds"
        ],
        "answer": 1
    },
    {
        "question": "Which items should be in your emergency kit?",
        "options": [
            "Just food",
            "Food, water, and first aid supplies",
            "Only electronic devices",
            "Only clothes"
        ],
        "answer": 1
    },
    {
        "question": "How can you receive emergency alerts?",
        "options": [
            "Only through television",
            "Only through radio",
            "Through multiple channels including weather radio, smartphone alerts, and television",
            "Only through newspapers"
        ],
        "answer": 2
    },
    {
        "question": "What should you do if you're driving during a flood?",
        "options": [
            "Drive through flooded areas quickly",
            "Park near riverbanks",
            "Turn around, don't drown",
            "Stop under bridges"
        ],
        "answer": 2
    },
    {
        "question": "Which of these is NOT a good practice during landslide season?",
        "options": [
            "Monitoring local warnings",
            "Building on steep slopes",
            "Planting ground cover on slopes",
            "Having an evacuation plan"
        ],
        "answer": 1
    },
    {
        "question": "After an earthquake, when is it safe to return home?",
        "options": [
            "Immediately after the shaking stops",
            "Only after authorities declare it's safe",
            "Whenever you feel like it",
            "After aftershocks"
        ],
        "answer": 1
    },
    {
        "question": "What is the safest action when a tsunami warning is issued?",
        "options": [
            "Go to the beach to watch",
            "Stay at home if you live near the coast",
            "Evacuate to higher ground or inland",
            "Go fishing"
        ],
        "answer": 2
    },
    {
        "question": "What causes floods?",
        "options": [
            "Only heavy rainfall",
            "Multiple factors including heavy rainfall, dam failures, and rapid snow melt",
            "Only tsunamis",
            "Only broken water mains"
        ],
        "answer": 1
    },
    {
        "question": "What is the leading cause of landslides?",
        "options": [
            "Traffic vibrations",
            "Water saturation of slopes",
            "Loud music",
            "Air pollution"
        ],
        "answer": 1
    },
    {
        "question": "How should you prepare your home for a potential flood?",
        "options": [
            "Open all windows",
            "Elevate electrical systems and waterproof basements",
            "Fill bathtubs with soil",
            "Remove all doors"
        ],
        "answer": 1
    },
    {
        "question": "What should you avoid during a thunderstorm?",
        "options": [
            "Using rubber-soled shoes indoors",
            "Staying inside a car",
            "Standing under tall trees",
            "Using battery-powered devices"
        ],
        "answer": 2
    },
    {
        "question": "Which of these is NOT a method to reduce landslide risk around your property?",
        "options": [
            "Installing proper drainage systems",
            "Planting trees and vegetation",
            "Building retaining walls when appropriate",
            "Removing all soil from your yard"
        ],
        "answer": 3
    },
    {
        "question": "What should you do if trapped in a building during a disaster?",
        "options": [
            "Try to escape through broken windows",
            "Signal for help and call emergency services",
            "Conserve phone battery by not calling anyone",
            "Play music loudly to attract attention"
        ],
        "answer": 1
    },
    {
        "question": "Which document should you safeguard before a disaster?",
        "options": [
            "Old newspapers",
            "Magazines",
            "Important identification and financial documents",
            "Recipe books"
        ],
        "answer": 2
    },
    {
        "question": "How often should you check and refresh your emergency supplies?",
        "options": [
            "Never",
            "Once every 10 years",
            "At least twice a year",
            "Only during disasters"
        ],
        "answer": 2
    },
    {
        "question": "Which of these is a sign of flood-damaged building that is unsafe to enter?",
        "options": [
            "The electricity is working",
            "Visible cracks in foundation or shifting of the building",
            "The door is unlocked",
            "Birds nesting on the roof"
        ],
        "answer": 1
    },
    {
        "question": "What should you do with utilities after a major disaster?",
        "options": [
            "Always turn them back on immediately",
            "Have them inspected before using them",
            "Ignore them completely",
            "Use them only at night"
        ],
        "answer": 1
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/emergency')
def emergency():
    states = list(emergency_contacts.keys())
    return render_template('emergency.html', states=states, contacts=emergency_contacts)

@app.route('/videos')
def videos():
    categories = list(videos_data.keys())
    return render_template('videos.html', categories=categories, videos=videos_data)

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/get_questions', methods=['GET'])
def get_questions():
    selected_questions = random.sample(quiz_questions, 10)
    return jsonify(selected_questions)

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)