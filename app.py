#Running on http://127.0.0.1:5000

"""Web app."""
import random
from unittest.mock import Base
import flask
from flask import Flask, jsonify, render_template, request, redirect, send_file, session, url_for, send_from_directory
import pickle

import joblib
from training import prediction
import requests
from datetime import datetime
import logging
from datetime import datetime
import os
from chatbot import DisasterChatbot
from googletrans import Translator
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Configure logging
app = flask.Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "disaster_awareness_key")

# Initialize chatbot and translator
chatbot = DisasterChatbot()
translator = Translator()

# Get the current month
current_month = datetime.now().strftime("%B")


# Video data - including only working videos from edited code
videos_data = {
    "Flood Awareness": [
        {
            "title": "Floods: Understanding Risks and Safety",
            "description": "Learn about flood risks and essential safety measures to protect yourself.",
            "embed_code": "https://www.youtube.com/embed/43M5mZuzHF8"
        }
    ],
    "Earthquake Awareness": [
        {
            "title": "Earthquakes: Drop, Cover, Hold On",
            "description": "The correct procedure to follow during an earthquake.",
            "embed_code": "https://www.youtube.com/embed/GSDmqLQmMN0"
        }
    ]
}

# Emergency contact data for India (from original code)
emergency_contacts = {
    "National": [
        {"name": "National Emergency Number", "number": "112", "description": "For all emergency situations across India"},
        {"name": "National Disaster Response Force (NDRF)", "number": "011-23438091", "description": "National disaster assistance and rescue"},
        {"name": "Disaster Management India", "number": "1078", "description": "Disaster management helpline"},
        {"name": "National Emergency Response Centre", "number": "011-23438252", "description": "Central coordination for disaster response"},
        {"name": "Police Emergency", "number": "100", "description": "Police assistance during emergencies"},
        {"name": "Fire Emergency", "number": "101", "description": "Fire service emergencies"},
        {"name": "Ambulance", "number": "108", "description": "Medical emergency ambulance service"},
        {"name": "Women Helpline", "number": "1091", "description": "Women's emergency helpline"}
    ],
    # States
    "Andhra Pradesh": [
        {"name": "AP State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "AP Emergency Operation Center", "number": "0863-2377088", "description": "Emergency operations center"},
        {"name": "AP Emergency Services", "number": "108", "description": "Medical emergencies"}
    ],
    "Arunachal Pradesh": [
        {"name": "Arunachal Pradesh SDMA", "number": "1070", "description": "State disaster management authority"},
        {"name": "Itanagar Emergency Services", "number": "108", "description": "Medical and disaster emergencies"},
        {"name": "Arunachal Pradesh Emergency Cell", "number": "0360-2247707", "description": "Emergency coordination"}
    ],
    "Assam": [
        {"name": "Assam State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Assam Flood Control Room", "number": "0361-2237221", "description": "Flooding emergencies in Assam"},
        {"name": "Guwahati Emergency Services", "number": "108", "description": "Medical emergencies"}
    ],
    "Bihar": [
        {"name": "Bihar State Disaster Management Authority", "number": "0612-2547232", "description": "State disaster coordination"},
        {"name": "Bihar Flood Control Room", "number": "0612-2210058", "description": "Flooding emergencies in Bihar"},
        {"name": "Bihar Emergency Services", "number": "108", "description": "Medical emergencies"}
    ],
    "Chhattisgarh": [
        {"name": "Chhattisgarh SDMA", "number": "1070", "description": "State disaster management authority"},
        {"name": "Raipur Emergency Services", "number": "108", "description": "Medical and disaster emergencies"},
        {"name": "Chhattisgarh Emergency Operation Center", "number": "0771-2223471", "description": "Emergency coordination"}
    ],
    "Goa": [
        {"name": "Goa State Disaster Management Authority", "number": "1077", "description": "State disaster coordination"},
        {"name": "Goa Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Goa Coastal Police", "number": "0832-2225383", "description": "Coastal emergencies"}
    ],
    "Gujarat": [
        {"name": "Gujarat State Disaster Management Authority", "number": "079-23251900", "description": "State disaster coordination"},
        {"name": "Gujarat Earthquake Helpline", "number": "079-23251902", "description": "Earthquake emergencies in Gujarat"},
        {"name": "Gujarat Flood Control Room", "number": "1070", "description": "Flooding emergencies in Gujarat"}
    ],
    "Haryana": [
        {"name": "Haryana State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Haryana Emergency Operation Center", "number": "0172-2570335", "description": "Emergency operations center"},
        {"name": "Haryana Emergency Services", "number": "108", "description": "Medical emergencies"}
    ],
    "Himachal Pradesh": [
        {"name": "Himachal Pradesh SDMA", "number": "1070", "description": "State disaster management authority"},
        {"name": "HP Emergency Services", "number": "108", "description": "Medical and disaster emergencies"},
        {"name": "Shimla Emergency Cell", "number": "0177-2812344", "description": "Emergency coordination for Shimla"}
    ],
    "Jharkhand": [
        {"name": "Jharkhand State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Ranchi Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Jharkhand Emergency Operation Center", "number": "0651-2481060", "description": "Emergency operations"}
    ],
    "Karnataka": [
        {"name": "Karnataka State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Bengaluru Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Karnataka Emergency Operation Center", "number": "080-22032582", "description": "Emergency coordination"}
    ],
    "Kerala": [
        {"name": "Kerala State Disaster Management Authority", "number": "0471-2331639", "description": "State disaster coordination"},
        {"name": "Kerala Flood Control Room", "number": "1070", "description": "Flooding emergencies in Kerala"},
        {"name": "Kerala Coastal Police", "number": "1093", "description": "Coastal and tsunami emergencies"}
    ],
    "Madhya Pradesh": [
        {"name": "Madhya Pradesh SDMA", "number": "1070", "description": "State disaster management authority"},
        {"name": "MP Emergency Services", "number": "108", "description": "Medical and disaster emergencies"},
        {"name": "Bhopal Emergency Cell", "number": "0755-2441419", "description": "Emergency coordination"}
    ],
    "Maharashtra": [
        {"name": "Maharashtra State Disaster Management Authority", "number": "022-22694725", "description": "State disaster coordination"},
        {"name": "Mumbai Disaster Helpline", "number": "1916", "description": "Mumbai-specific disaster response"},
        {"name": "Maharashtra Emergency Ambulance", "number": "108", "description": "Medical emergencies in Maharashtra"}
    ],
    "Manipur": [
        {"name": "Manipur State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Imphal Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Manipur Emergency Cell", "number": "0385-2450214", "description": "Emergency coordination"}
    ],
    "Meghalaya": [
        {"name": "Meghalaya SDMA", "number": "1070", "description": "State disaster management authority"},
        {"name": "Shillong Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Meghalaya Emergency Operation Center", "number": "0364-2504434", "description": "Emergency operations"}
    ],
    "Mizoram": [
        {"name": "Mizoram State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Aizawl Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Mizoram Emergency Operation Center", "number": "0389-2342520", "description": "Emergency operations"}
    ],
    "Nagaland": [
        {"name": "Nagaland SDMA", "number": "1070", "description": "State disaster management authority"},
        {"name": "Kohima Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Nagaland Emergency Cell", "number": "0370-2291122", "description": "Emergency coordination"}
    ],
    "Odisha": [
        {"name": "Odisha State Disaster Management Authority", "number": "0674-2395398", "description": "State disaster coordination"},
        {"name": "Odisha Cyclone Helpline", "number": "1070", "description": "Cyclone emergencies in Odisha"},
        {"name": "Odisha Emergency Services", "number": "108", "description": "Medical and disaster emergencies"}
    ],
    "Punjab": [
        {"name": "Punjab State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Punjab Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Punjab Emergency Operation Center", "number": "0172-2749074", "description": "Emergency operations"}
    ],
    "Rajasthan": [
        {"name": "Rajasthan SDMA", "number": "1070", "description": "State disaster management authority"},
        {"name": "Jaipur Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Rajasthan Emergency Operation Center", "number": "0141-2227296", "description": "Emergency coordination"}
    ],
    "Sikkim": [
        {"name": "Sikkim State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Gangtok Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Sikkim Landslide Helpline", "number": "03592-202932", "description": "Landslide emergencies"}
    ],
    "Tamil Nadu": [
        {"name": "Tamil Nadu Disaster Response Force", "number": "044-28410405", "description": "State disaster coordination"},
        {"name": "Chennai Flood Control Room", "number": "044-25203664", "description": "Flooding emergencies in Chennai"},
        {"name": "Tamil Nadu Emergency Services", "number": "108", "description": "Medical and disaster emergencies"}
    ],
    "Telangana": [
        {"name": "Telangana State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Hyderabad Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Telangana Emergency Operation Center", "number": "040-23454088", "description": "Emergency operations"}
    ],
    "Tripura": [
        {"name": "Tripura SDMA", "number": "1070", "description": "State disaster management authority"},
        {"name": "Agartala Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Tripura Emergency Cell", "number": "0381-2416045", "description": "Emergency coordination"}
    ],
    "Uttarakhand": [
        {"name": "Uttarakhand State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "Dehradun Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Uttarakhand Landslide Helpline", "number": "0135-2710334", "description": "Landslide emergencies"}
    ],
    "Uttar Pradesh": [
        {"name": "UP State Disaster Management Authority", "number": "1070", "description": "State disaster coordination"},
        {"name": "UP Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "UP Flood Control Room", "number": "0522-2236758", "description": "Flooding emergencies"}
    ],
    "West Bengal": [
        {"name": "West Bengal Disaster Management Department", "number": "033-22143526", "description": "State disaster coordination"},
        {"name": "Kolkata Flood Control Room", "number": "033-22145664", "description": "Flooding in Kolkata region"},
        {"name": "Cyclone Warning Center", "number": "1582", "description": "Cyclone alerts and emergencies"}
    ],

    # Union Territories
    "Andaman and Nicobar Islands": [
        {"name": "A&N Islands Disaster Management", "number": "03192-238881", "description": "Disaster coordination"},
        {"name": "Port Blair Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Tsunami Warning Center", "number": "1070", "description": "Tsunami alerts and emergencies"}
    ],
    "Chandigarh": [
        {"name": "Chandigarh Disaster Management", "number": "1070", "description": "Disaster coordination"},
        {"name": "Chandigarh Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Chandigarh Emergency Operation Center", "number": "0172-2700109", "description": "Emergency operations"}
    ],
    "Dadra and Nagar Haveli and Daman and Diu": [
        {"name": "DNH & DD Disaster Management", "number": "1070", "description": "Disaster coordination"},
        {"name": "DNH & DD Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Coastal Emergency Helpline", "number": "0260-2230304", "description": "Coastal emergencies"}
    ],
    "Delhi": [
        {"name": "Delhi Disaster Management Authority", "number": "1077", "description": "Delhi disaster response coordination"},
        {"name": "Delhi Fire Services", "number": "101", "description": "Fire emergencies in Delhi"},
        {"name": "Delhi Flood Control Room", "number": "011-22421656", "description": "Flooding emergencies in Delhi"}
    ],
    "Jammu and Kashmir": [
        {"name": "J&K Disaster Management Authority", "number": "1070", "description": "Disaster coordination"},
        {"name": "J&K Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "J&K Landslide & Avalanche Helpline", "number": "0194-2455946", "description": "Landslides and avalanches"}
    ],
    "Ladakh": [
        {"name": "Ladakh Disaster Management", "number": "1070", "description": "Disaster coordination"},
        {"name": "Leh Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Ladakh Avalanche Helpline", "number": "01982-257410", "description": "Avalanche emergencies"}
    ],
    "Lakshadweep": [
        {"name": "Lakshadweep Disaster Management", "number": "04896-262250", "description": "Disaster coordination"},
        {"name": "Lakshadweep Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Coastal Emergency Helpline", "number": "1070", "description": "Coastal emergencies"}
    ],
    "Puducherry": [
        {"name": "Puducherry Disaster Management", "number": "1070", "description": "Disaster coordination"},
        {"name": "Puducherry Emergency Services", "number": "108", "description": "Medical emergencies"},
        {"name": "Puducherry Coastal Helpline", "number": "0413-2253407", "description": "Coastal emergencies"}
    ]
}

# Quiz questions database (from original code)
quiz_questions = [
    {
        "question": "What should you do first when you hear a flood warning?",
        "options": [
            "Go outside to check water levels",
            "Move to higher ground immediately",
            "Call friends to warn them",
            "Turn off the electricity at the main breaker"
        ],
        "answer": 1
    },
    {
        "question": "Which of these is NOT a sign of an impending landslide?",
        "options": [
            "Doors or windows stick or jam for the first time",
            "New cracks appear in plaster, tile, or foundations",
            "Outside walls or stairs begin to pull away from the building",
            "Temperature suddenly decreases in the area"
        ],
        "answer": 3
    },
    {
        "question": "During an earthquake, what is the recommended action?",
        "options": [
            "Run outside immediately",
            "Stand in a doorway",
            "Drop, cover, and hold on",
            "Call emergency services"
        ],
        "answer": 2
    },
    {
        "question": "Which natural sign might warn of an approaching tsunami?",
        "options": [
            "Sudden rise in temperature",
            "Unusual animal behavior",
            "Rapid recession of water from the shore",
            "Increase in insect activity"
        ],
        "answer": 2
    },
    {
        "question": "What item is MOST essential in an emergency preparedness kit?",
        "options": [
            "Flashlight",
            "Water (one gallon per person per day)",
            "First aid kit",
            "Battery-powered radio"
        ],
        "answer": 1
    },
    {
        "question": "How much water should you store for emergency purposes per person per day?",
        "options": [
            "Half a gallon",
            "One gallon",
            "Two gallons",
            "Three gallons"
        ],
        "answer": 1
    },
    {
        "question": "What is the safest location during a tornado?",
        "options": [
            "An interior room on the lowest floor",
            "Near windows to watch the tornado",
            "In a car with the windows closed",
            "Outside, away from buildings"
        ],
        "answer": 0
    },
    {
        "question": "Which of these is NOT a recommended action during a wildfire evacuation?",
        "options": [
            "Close all windows and doors before leaving",
            "Leave sprinklers on around your house",
            "Follow designated evacuation routes",
            "Take important documents with you"
        ],
        "answer": 1
    },
    {
        "question": "Which agency issues tsunami warnings in the United States?",
        "options": [
            "Federal Bureau of Investigation (FBI)",
            "National Weather Service (NWS)",
            "Centers for Disease Control (CDC)",
            "Environmental Protection Agency (EPA)"
        ],
        "answer": 1
    },
    {
        "question": "What color is typically used for severe hurricane warnings?",
        "options": [
            "Yellow",
            "Green",
            "Blue",
            "Red"
        ],
        "answer": 3
    },
    {
        "question": "How far inland can strong tsunamis reach?",
        "options": [
            "Up to 100 feet",
            "Up to 500 feet",
            "Up to 1 mile",
            "Up to several miles"
        ],
        "answer": 3
    },
    {
        "question": "What should you do if caught in a vehicle during a flash flood?",
        "options": [
            "Drive through the water slowly",
            "Stay in the vehicle if water isn't too deep",
            "Abandon the vehicle and move to higher ground",
            "Wait for rescue in the vehicle"
        ],
        "answer": 2
    },
    {
        "question": "Which of these natural disasters typically gives the least amount of warning time?",
        "options": [
            "Hurricanes",
            "Earthquakes",
            "Volcanic eruptions",
            "Winter storms"
        ],
        "answer": 1
    },
    {
        "question": "What is the purpose of the 'triangle of life' theory in earthquake safety?",
        "options": [
            "It's the official FEMA recommended procedure",
            "It suggests forming triangular hand symbols to signal rescuers",
            "It suggests seeking shelter next to solid objects rather than under them",
            "It's a technique for administering CPR during earthquakes"
        ],
        "answer": 2
    },
    {
        "question": "During which season do most hurricanes occur in the Atlantic Basin?",
        "options": [
            "Winter (December-February)",
            "Spring (March-May)",
            "Summer (June-August)",
            "Fall (September-November)"
        ],
        "answer": 3
    },
    {
        "question": "What is the first thing you should check for after an earthquake?",
        "options": [
            "Structural damage to your building",
            "Gas leaks",
            "News updates",
            "Neighbors' safety"
        ],
        "answer": 1
    },
    {
        "question": "Which of these items should NOT be included in an emergency preparedness kit?",
        "options": [
            "Perishable food",
            "Manual can opener",
            "Dust mask",
            "Moist towelettes"
        ],
        "answer": 0
    },
    {
        "question": "What does the term 'storm surge' refer to?",
        "options": [
            "Heavy rainfall during a storm",
            "Strong winds during a hurricane",
            "Abnormal rise in seawater level during a storm",
            "Lightning strikes during thunderstorms"
        ],
        "answer": 2
    },
    {
        "question": "What percentage of tsunamis are caused by earthquakes?",
        "options": [
            "About 50%",
            "About 70%",
            "About 90%",
            "About 30%"
        ],
        "answer": 2
    },
    {
        "question": "Which disaster type is measured using the Richter scale?",
        "options": [
            "Hurricanes",
            "Tsunamis",
            "Tornadoes",
            "Earthquakes"
        ],
        "answer": 3
    },
    {
        "question": "What is the recommended method for purifying water during an emergency?",
        "options": [
            "Let it stand for 24 hours",
            "Add salt",
            "Boil for at least one minute",
            "Run through cloth"
        ],
        "answer": 2
    },
    {
        "question": "What is the 'eye' of a hurricane?",
        "options": [
            "The area of heaviest rainfall",
            "The center where it's calm with clear skies",
            "The location where the hurricane first forms",
            "The area with the strongest winds"
        ],
        "answer": 1
    },
    {
        "question": "What should you do if you smell gas after an earthquake?",
        "options": [
            "Immediately turn off the gas meter",
            "Open windows and get out quickly",
            "Call the gas company first",
            "Light a match to check where the leak is coming from"
        ],
        "answer": 1
    },
    {
        "question": "What is the proper way to extinguish a small kitchen fire?",
        "options": [
            "Pour water on it",
            "Cover it with a metal lid",
            "Open windows to let the smoke out",
            "Fan the flames to control the direction"
        ],
        "answer": 1
    },
    {
        "question": "Which of these weather conditions can trigger landslides?",
        "options": [
            "High humidity",
            "Low air pressure",
            "Intense heat",
            "Heavy rainfall"
        ],
        "answer": 3
    },
    {
        "question": "What does the Saffir-Simpson scale measure?",
        "options": [
            "Earthquake intensity",
            "Hurricane strength",
            "Tornado speed",
            "Landslide risk"
        ],
        "answer": 1
    },
    {
        "question": "Which of these is a good strategy for earthquake-proofing your home?",
        "options": [
            "Place heavy objects on high shelves",
            "Hang pictures with wire instead of nails",
            "Secure heavy furniture to walls",
            "Keep all doors closed"
        ],
        "answer": 2
    },
    {
        "question": "What is the recommended depth for an emergency water well?",
        "options": [
            "10-20 feet",
            "50-100 feet",
            "100-200 feet",
            "It depends on the local water table"
        ],
        "answer": 3
    },
    {
        "question": "What should be your priority if you are trapped in a building after a disaster?",
        "options": [
            "Conserve your phone battery",
            "Make noise periodically to alert rescuers",
            "Try to find a way out immediately regardless of danger",
            "Stay on the phone with emergency services"
        ],
        "answer": 1
    },
    {
        "question": "How often should you replace the food in your emergency kit?",
        "options": [
            "Every 6 months",
            "Every year",
            "Every 2 years",
            "Every 5 years"
        ],
        "answer": 0
    }
]

# Game data - items needed for different disaster preparations (from original code)
game_data = {
    "disasters": [
        {
            "id": "flood",
            "name": "Flood",
            "description": "Prepare your home for a potential flood by selecting the right items.",
            "items": [
                {"id": "sandbags", "name": "Sandbags", "correct": True, "description": "Creates barriers to prevent water entry"},
                {"id": "water_pump", "name": "Water Pump", "correct": True, "description": "Removes flood water from your home"},
                {"id": "life_vest", "name": "Life Vest", "correct": True, "description": "Essential for safety in flood waters"},
                {"id": "flashlight", "name": "Flashlight", "correct": True, "description": "Necessary during power outages"},
                {"id": "camping_tent", "name": "Camping Tent", "correct": False, "description": "Not useful during a flood"},
                {"id": "sunscreen", "name": "Sunscreen", "correct": False, "description": "Not a flood preparation item"}
            ]
        },
        {
            "id": "earthquake",
            "name": "Earthquake",
            "description": "Prepare for an earthquake by selecting items to secure your home and ensure safety.",
            "items": [
                {"id": "emergency_kit", "name": "Emergency Kit", "correct": True, "description": "Contains first aid and survival supplies"},
                {"id": "furniture_straps", "name": "Furniture Straps", "correct": True, "description": "Secures heavy furniture to walls"},
                {"id": "whistle", "name": "Whistle", "correct": True, "description": "Alerts rescuers to your location"},
                {"id": "fire_extinguisher", "name": "Fire Extinguisher", "correct": True, "description": "For post-earthquake fires"},
                {"id": "beach_umbrella", "name": "Beach Umbrella", "correct": False, "description": "Not useful for earthquake safety"},
                {"id": "golf_clubs", "name": "Golf Clubs", "correct": False, "description": "Not relevant for earthquake preparation"}
            ]
        },
        {
            "id": "hurricane",
            "name": "Hurricane",
            "description": "Prepare for an approaching hurricane by selecting appropriate safety items.",
            "items": [
                {"id": "plywood", "name": "Plywood", "correct": True, "description": "For boarding up windows"},
                {"id": "water_storage", "name": "Water Storage", "correct": True, "description": "For drinking if water supply is compromised"},
                {"id": "weather_radio", "name": "Weather Radio", "correct": True, "description": "For emergency broadcasts"},
                {"id": "first_aid", "name": "First Aid Kit", "correct": True, "description": "For treating injuries"},
                {"id": "surfboard", "name": "Surfboard", "correct": False, "description": "Dangerous during a hurricane"},
                {"id": "kite", "name": "Kite", "correct": False, "description": "Completely inappropriate for hurricane conditions"}
            ]
        },
        {
            "id": "tsunami",
            "name": "Tsunami",
            "description": "Prepare for a tsunami warning by selecting the correct evacuation items.",
            "items": [
                {"id": "emergency_docs", "name": "Emergency Documents", "correct": True, "description": "Important papers in waterproof container"},
                {"id": "evacuation_map", "name": "Evacuation Map", "correct": True, "description": "Shows routes to high ground"},
                {"id": "portable_radio", "name": "Portable Radio", "correct": True, "description": "For emergency broadcasts"},
                {"id": "emergency_food", "name": "Emergency Food", "correct": True, "description": "Non-perishable items for 72 hours"},
                {"id": "swimming_goggles", "name": "Swimming Goggles", "correct": False, "description": "Not appropriate for tsunami evacuation"},
                {"id": "beach_toys", "name": "Beach Toys", "correct": False, "description": "Inappropriate during a tsunami emergency"}
            ]
        }
    ]
}

# Track session quiz questions to avoid repetition (from original code)
def get_random_questions(num_questions=10):
    asked_indices = session.get('asked_questions', [])
    available_indices = [i for i in range(len(quiz_questions)) if i not in asked_indices]
    if len(available_indices) < num_questions:
        asked_indices = []
        available_indices = list(range(len(quiz_questions)))
    question_indices = random.sample(available_indices, num_questions)
    session['asked_questions'] = asked_indices + question_indices
    return [quiz_questions[i] for i in question_indices]

data = [{'name':'Delhi', "sel": "selected"}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}]
months = [{"name":"May", "sel": ""}, {"name":"June", "sel": ""}, {"name":"July", "sel": ""}, {"name": current_month, "sel": "selected"}]
cities = [{'name':'Delhi', "sel": "selected"}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}, {'name':'New York', "sel": ""}, {'name':'Los Angeles', "sel": ""}, {'name':'London', "sel": ""}, {'name':'Paris', "sel": ""}, {'name':'Sydney', "sel": ""}, {'name':'Beijing', "sel": ""}]

#use joblib or pickle to load the model
model = joblib.load("model/model.pickle")

@app.route("/")
def index() -> str:
    return redirect(url_for('home'))

@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/accuracy.html')
def accuracy():
    return render_template('accuracy.html')

@app.route('/predicts.html')
def predicts():
    return render_template('predicts.html', cities=cities, cityname="Information about the city")

@app.route('/disaster_awareness.html')
def community():
    return render_template('disaster_awareness.html')

@app.route('/predicts.html', methods=["GET", "POST"])
def get_predicts():
    try:
        cities = [{'name':'Delhi', "sel": ""}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, 
                  {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}, {'name':'New York', "sel": ""},
                  {'name':'Los Angeles', "sel": ""}, {'name':'London', "sel": ""}, {'name':'Paris', "sel": ""},
                  {'name':'Sydney', "sel": ""}, {'name':'Beijing', "sel": ""}]

        cityname = request.form.get("city", "").strip()
        if not cityname:
            return render_template('predicts.html', cities=cities, cityname="Please select a valid city.")

        for item in cities:
            if item['name'] == cityname:
                item['sel'] = 'selected'

        print("Selected City:", cityname)

        # HERE API for Geolocation
        URL = "https://geocode.search.hereapi.com/v1/geocode"
        api_key = 'pPFSt0miNxLZJY6_Zs-h-nB9W1XxxJG6s3wat1L37r8'
        PARAMS = {'apikey': api_key, 'q': cityname}

        r = requests.get(url=URL, params=PARAMS)
        print("API Response Code:", r.status_code)

        if r.status_code != 200:
            return render_template('predicts.html', cities=cities, cityname="Error fetching location data.")

        data = r.json()
        print("API Response:", data)

        if 'items' not in data or not data['items']:
            return render_template('predicts.html', cities=cities, cityname="Could not find coordinates for that city.")

        latitude = data['items'][0]['position']['lat']
        longitude = data['items'][0]['position']['lng']
        print(f"Latitude: {latitude}, Longitude: {longitude}")

        # Weather Prediction
        final = prediction.get_data(latitude, longitude)
        if not final or len(final) < 6:
            return render_template('predicts.html', cities=cities, cityname="Error retrieving prediction data.")

        print("Weather Data:", final)

        final[4] *= 15
        pred = "Safe" if str(model.predict([final])[0]) == "0" else "Unsafe"
        return render_template(
            'predicts.html', 
            cityname=f"Information about {cityname}", 
            cities=cities, 
            temp=round((final[0] - 32) * 0.5556, 2), 
            maxt=round(final[1], 2), 
            wspd=round(final[2], 2), 
            cloudcover=round(final[3], 2), 
            percip=round(final[4], 2), 
            humidity=round(final[5], 2), 
            pred=pred
        )

    except Exception as e:
        print("Error:", e)
        print(type(model))
        return render_template('predicts.html', cities=cities, cityname="Oops, we weren't able to retrieve data for that city.")

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/videos')
def videos():
    categories = list(videos_data.keys())
    return render_template('videos.html', videos=videos_data, categories=categories)

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/emergency')
def emergency():
    all_regions = list(emergency_contacts.keys())
    states = []
    union_territories = []
    for region in all_regions:
        if region == "National":
            continue
        elif region in ["Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", 
                        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"]:
            union_territories.append(region)
        else:
            states.append(region)
    states.sort()
    union_territories.sort()
    all_regions = ["National"] + states + union_territories
    return render_template('emergency.html', contacts=emergency_contacts, states=all_regions, 
                          regular_states=states, union_territories=union_territories)

@app.route('/get_questions', methods=['GET'])
def get_questions():
    questions = get_random_questions(10)
    return jsonify(questions)

@app.route('/get_game_data', methods=['GET'])
def get_game_data():
    return jsonify(game_data)

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/chatbot.html', methods=['GET', 'POST'])
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Process chat messages and return responses with language translation"""
    try:
        user_message = request.json.get('message', '')
        target_language = request.json.get('language', 'en')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Translate user message to English for processing if not already in English
        if target_language != 'en':
            try:
                # Detect language and translate to English if needed
                detected = translator.detect(user_message)
                if detected.lang != 'en':
                    user_message_eng = translator.translate(user_message, src=detected.lang, dest='en').text
                else:
                    user_message_eng = user_message
            except Exception as e:
                logging.warning(f"Translation error (input): {str(e)}")
                user_message_eng = user_message  # Fallback to original message
        else:
            user_message_eng = user_message
            
        # Check if this is a language change notification
        if user_message_eng.lower() == "language selection changed":
            # Special message for language change
            language_names = {
                'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu', 
                'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 'kn': 'Kannada',
                'ml': 'Malayalam', 'pa': 'Punjabi', 'ur': 'Urdu', 'or': 'Odia', 'as': 'Assamese'
            }
            language_name = language_names.get(target_language, target_language)
            message_eng = f"I'll now respond in {language_name}. You can ask me about natural disasters, prevention measures, emergency helplines, or historical events in India."
            
            # Translate language change message
            if target_language != 'en':
                try:
                    response = translator.translate(message_eng, src='en', dest=target_language).text
                except Exception as e:
                    logging.warning(f"Translation error for language change: {str(e)}")
                    response = message_eng
            else:
                response = message_eng
        else:
            # Get response from chatbot (always in English)
            response_eng = chatbot.get_response(user_message_eng)
            
            # Translate response to target language if not English
            if target_language != 'en':
                try:
                    response = translator.translate(response_eng, src='en', dest=target_language).text
                except Exception as e:
                    logging.warning(f"Translation error (output): {str(e)}")
                    response = response_eng  # Fallback to English response
            else:
                response = response_eng
            
        return jsonify({'response': response})
    
    except Exception as e:
        logging.error(f"Error processing chat message: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500


@app.route('/get_helplines', methods=['GET'])
def get_helplines():
    """Return disaster helpline numbers"""
    try:
        state = request.args.get('state', None)
        helplines = chatbot.get_helpline_numbers(state)
        return jsonify(helplines)
    
    except Exception as e:
        logging.error(f"Error fetching helpline numbers: {str(e)}")
        return jsonify({'error': 'An error occurred fetching helpline numbers'}), 500

@app.route('/historical', methods=['GET'])
def get_historical_disasters():
    """Return historical disaster data"""
    try:
        disaster_type = request.args.get('type', None)
        historical_data = chatbot.get_historical_disasters(disaster_type)
        return jsonify({'historical_data': historical_data})
    
    except Exception as e:
        logging.error(f"Error fetching historical data: {str(e)}")
        return jsonify({'error': 'An error occurred fetching historical disaster data'}), 500


if __name__ == '__main__':
    app.run(debug=True)
