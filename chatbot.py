import os
import json
import re
import logging
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('stopwords')
    nltk.download('wordnet')

# Ensure the data is properly loaded
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# Simple tokenizer function to replace NLTK's word_tokenize
def simple_tokenize(text):
    """Simple tokenizer that splits on spaces and punctuation"""
    # Remove punctuation and replace with space
    text = re.sub(r'[^\w\s]', ' ', text)
    # Split on whitespace and filter out empty strings
    return [token for token in text.split() if token]

class DisasterChatbot:
    def __init__(self):
        """Initialize the disaster chatbot with knowledge base"""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Load disaster data
        self.disaster_data = self._load_json_data('data/disaster_data.json')
        self.helpline_numbers = self._load_json_data('data/helpline_numbers.json')
        self.historical_disasters = self._load_json_data('data/historical_disasters.json')
        
        # Define expanded disaster types for keyword matching
        self.disaster_types = [
            'flood', 'landslide', 'tsunami', 'earthquake', 'drought', 
            'cyclone', 'wildfire', 'heatwave', 'industrial', 'pandemic'
        ]
        
        # Define expanded categories for disaster information
        self.categories = [
            'prevention', 'preparation', 'recovery', 'during', 'after', 'before', 
            'helpline', 'historical', 'warning', 'first_aid'
        ]
        
        logging.debug("Chatbot initialized successfully")
    
    def _load_json_data(self, file_path):
        """Load data from JSON files"""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Error loading data from {file_path}: {str(e)}")
            # Return empty dict to prevent failures
            return {}
    
    def _preprocess_text(self, text):
        """Preprocess user input for better matching"""
        # Convert to lowercase
        text = text.lower()
        # Tokenize using our simple tokenizer
        tokens = simple_tokenize(text)
        # Remove stopwords and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words and token.isalnum()
        ]
        return processed_tokens
    
    def _extract_keywords(self, processed_text):
        """Extract disaster types, categories, locations, and years from processed text"""
        disaster_matches = []
        category_matches = []
        location_matches = []
        year_matches = []
        
        # Process input text as string to check for years
        input_text = ' '.join(processed_text)
        
        # Find years (like 2018, 2023) in the input
        year_pattern = r'\b(19|20)\d{2}\b'
        year_matches = re.findall(year_pattern, input_text)
        
        # Indian states and notable locations for disaster events
        locations = [
            'kerala', 'tamil nadu', 'karnataka', 'andhra pradesh', 'telangana', 'maharashtra', 
            'gujarat', 'rajasthan', 'madhya pradesh', 'uttar pradesh', 'bihar', 'west bengal', 
            'odisha', 'punjab', 'haryana', 'himachal pradesh', 'uttarakhand', 'jammu', 'kashmir',
            'assam', 'mumbai', 'chennai', 'kolkata', 'bangalore', 'hyderabad', 'latur', 'bhuj', 
            'kutch', 'marathwada', 'vidarbha', 'konkan', 'wayanad', 'idukki', 'pathanamthitta'
        ]
        
        # Enhanced disaster keywords dictionary including man-made and biological disasters
        enhanced_disaster_keywords = {
            'flood': ['flood', 'flooding', 'inundation', 'submerge', 'deluge', 'monsoon', 'overflow'],
            'landslide': ['landslide', 'landslip', 'mudslide', 'rockfall', 'debris flow', 'slope failure'],
            'tsunami': ['tsunami', 'tidal wave', 'seismic sea wave', 'harbor wave'],
            'earthquake': ['earthquake', 'quake', 'tremor', 'seismic', 'temblor', 'aftershock'],
            'drought': ['drought', 'dry spell', 'water scarcity', 'water shortage', 'arid', 'famine'],
            'cyclone': ['cyclone', 'hurricane', 'typhoon', 'storm', 'tropical cyclone', 'storm surge'],
            'wildfire': ['wildfire', 'forest fire', 'bush fire', 'fire', 'burning', 'blaze'],
            'heatwave': ['heatwave', 'heat wave', 'hot spell', 'extreme heat', 'heat stress'],
            'industrial': ['industrial accident', 'factory accident', 'chemical spill', 'oil spill', 'gas leak', 'toxic release'],
            'pandemic': ['pandemic', 'epidemic', 'outbreak', 'disease', 'virus', 'infection', 'contagion']
        }
        
        # Enhanced categories for better intent matching
        enhanced_category_keywords = {
            'prevention': ['prevention', 'prevent', 'prepare', 'preparation', 'mitigate', 'mitigation', 
                          'avoid', 'ready', 'readiness', 'before', 'risk reduction', 'safety measures', 'precaution'],
            'during': ['during', 'survive', 'survival', 'live through', 'withstand', 'endure', 
                      'safety', 'protect', 'protection', 'emergency', 'evacuation', 'evacuate'],
            'recovery': ['recovery', 'recover', 'aftermath', 'after', 'rebuild', 'reconstruction', 
                        'restore', 'rehabilitation', 'relief', 'aid', 'assistance', 'cope'],
            'helpline': ['helpline', 'help line', 'hotline', 'emergency number', 'contact', 'phone', 
                        'call', 'ndrf', 'sdrf', 'disaster response', 'rescue', 'emergency service'],
            'historical': ['history', 'historical', 'past', 'previous', 'earlier', 'record', 
                          'chronicle', 'incident', 'occurrence', 'event'],
            'warning': ['warning', 'alert', 'early warning', 'forecast', 'prediction', 'monitor', 'detection'],
            'first_aid': ['first aid', 'medical', 'treatment', 'injury', 'wound', 'bandage', 'cpr', 'resuscitation']
        }
        
        # Check for locations in the processed text
        for location in locations:
            if location in input_text:
                location_matches.append(location)
        
        # Check for disaster types using enhanced keywords
        for disaster_type, keywords in enhanced_disaster_keywords.items():
            if any(keyword in input_text for keyword in keywords):
                disaster_matches.append(disaster_type)
        
        # Check for categories using enhanced keywords
        for category, keywords in enhanced_category_keywords.items():
            if any(keyword in input_text for keyword in keywords):
                category_matches.append(category)
        
        # Remove duplicates
        disaster_matches = list(set(disaster_matches))
        category_matches = list(set(category_matches))
        location_matches = list(set(location_matches))
        
        return disaster_matches, category_matches, location_matches, year_matches
    
    def get_response(self, user_message):
        """Generate response based on user message"""
        # Preprocess user input
        processed_text = self._preprocess_text(user_message)
        
        # Extract keywords including locations and years
        disaster_types, categories, locations, years = self._extract_keywords(processed_text)
        
        # Check for greeting
        greeting_patterns = ['hello', 'hi', 'hey', 'greetings', 'namaste']
        if any(greeting in processed_text for greeting in greeting_patterns):
            return "Hello! I'm the 2025 Geoguard Flood and Landslide Prediction Chatbot. I can provide information about natural disasters in India, including prevention, preparation, and recovery for floods, landslides, earthquakes, tsunamis, droughts, and more. How can I help you today?"
        
        # Check for general questions about disasters
        general_info = self._get_general_disaster_info(user_message)
        if general_info:
            return general_info
        
        # Check for early warning systems and alerts
        if 'warning' in categories or any(word in user_message.lower() for word in ['alert', 'early warning', 'forecast', 'predict', 'prediction', 'monitor']):
            if disaster_types:
                return self._get_early_warning_info(disaster_types[0])
            else:
                return "Early warning systems are crucial for disaster preparedness. India has various systems like:\n\n- Indian Meteorological Department (IMD) for cyclones and floods\n- Tsunami Early Warning Centre (TEWC) for tsunamis\n- National Earthquake Monitoring Centre for earthquakes\n- Drought Early Warning System (DEWS)\n\nYou can ask me about early warning systems for specific disasters like floods or cyclones."
        
        # Check for first aid queries
        if 'first_aid' in categories or any(word in user_message.lower() for word in ['first aid', 'medical', 'injury', 'treatment', 'wound', 'bandage', 'cpr']):
            return self._get_first_aid_info(disaster_types[0] if disaster_types else None)
        
        # Check for helpline request
        if 'helpline' in processed_text or 'number' in processed_text or 'contact' in processed_text or 'emergency' in processed_text:
            # Check if a state is mentioned
            states = self.helpline_numbers.keys()
            mentioned_state = None
            
            for state in states:
                state_lower = state.lower()
                if state_lower in user_message.lower():
                    mentioned_state = state
                    break
            
            return self._get_helpline_response(mentioned_state, disaster_types)
        
        # Check for specific historical event query with location, year, and disaster type
        specific_historical = False
        
        # If we have both a location and year or a specific disaster mentioned with year/location
        if (locations and years) or (disaster_types and (locations or years)):
            specific_historical = True
            # Check for queries about historical events
            return self._get_specific_historical_response(disaster_types, locations, years, user_message)
        
        # Check for general historical disaster information
        if any(word in processed_text for word in ['history', 'historical', 'past', 'previous', 'occurred']):
            return self._get_historical_response(disaster_types)
        
        # Handle normal disaster information requests
        if disaster_types:
            disaster_type = disaster_types[0]  # Use the first matched disaster type
            
            # If no specific category is mentioned, provide general information
            if not categories:
                return self._get_general_information(disaster_type)
            
            # Provide information based on the requested category
            category = categories[0]  # Use the first matched category
            
            if category in ['prevention', 'before', 'preparation']:
                return self._get_prevention_info(disaster_type)
            elif category in ['during']:
                return self._get_during_info(disaster_type)
            elif category in ['recovery', 'after']:
                return self._get_recovery_info(disaster_type)
            else:
                return self._get_general_information(disaster_type)
        
        # Default response if no specific information is requested
        return "I'm the 2025 Geoguard Flood and Landslide Prediction Chatbot. I can provide information about disaster prevention, preparation, recovery, early warnings, historical events, and first aid for various natural disasters including floods, landslides, earthquakes, tsunamis, droughts, cyclones, wildfires, and heatwaves. How can I assist you today?"
    
    def _get_general_information(self, disaster_type):
        """Get general information about a disaster type"""
        if disaster_type in self.disaster_data:
            info = self.disaster_data[disaster_type]
            return f"{info['description']}\n\nYou can ask me about prevention measures, what to do during a {disaster_type}, or recovery steps after a {disaster_type}."
        return f"I don't have specific information about {disaster_type}. Please ask about floods, landslides, tsunamis, earthquakes, or droughts."
    
    def _get_prevention_info(self, disaster_type):
        """Get prevention/preparation information"""
        if disaster_type in self.disaster_data and 'prevention' in self.disaster_data[disaster_type]:
            prevention = self.disaster_data[disaster_type]['prevention']
            return f"Here's how to prepare for a {disaster_type}:\n\n{prevention}"
        return f"I don't have specific prevention information for {disaster_type}. Please ask about floods, landslides, tsunamis, earthquakes, or droughts."
    
    def _get_during_info(self, disaster_type):
        """Get information about what to do during a disaster"""
        if disaster_type in self.disaster_data and 'during' in self.disaster_data[disaster_type]:
            during = self.disaster_data[disaster_type]['during']
            return f"Here's what to do during a {disaster_type}:\n\n{during}"
        return f"I don't have specific information about what to do during a {disaster_type}. Please ask about floods, landslides, tsunamis, earthquakes, or droughts."
    
    def _get_recovery_info(self, disaster_type):
        """Get recovery information"""
        if disaster_type in self.disaster_data and 'recovery' in self.disaster_data[disaster_type]:
            recovery = self.disaster_data[disaster_type]['recovery']
            return f"Here's how to recover after a {disaster_type}:\n\n{recovery}"
        return f"I don't have specific recovery information for {disaster_type}. Please ask about floods, landslides, tsunamis, earthquakes, or droughts."
    
    def _get_helpline_response(self, state, disaster_types):
        """Get helpline information for a state or nationally"""
        response = "Here are the emergency helpline numbers you should know:\n\n"
        
        # If specific disaster type is mentioned, prioritize that information
        if disaster_types and disaster_types[0] in self.helpline_numbers.get('National', {}):
            disaster = disaster_types[0]
            response += f"For {disaster.capitalize()} emergencies: "
            response += f"{self.helpline_numbers['National'].get(disaster, 'Not available')}\n\n"
        
        # Add state-specific helplines if a state was mentioned
        if state and state in self.helpline_numbers:
            response += f"{state} Emergency Helplines:\n"
            for service, number in self.helpline_numbers[state].items():
                response += f"- {service}: {number}\n"
        # Otherwise, provide national helplines
        else:
            response += "National Emergency Helplines:\n"
            for service, number in self.helpline_numbers.get('National', {}).items():
                response += f"- {service}: {number}\n"
            
            response += "\nFor state-specific helplines, please mention the state name."
        
        return response
    
    def _get_historical_response(self, disaster_types):
        """Get historical information about past disasters"""
        if not disaster_types:
            # Provide a summary of major disasters if no specific type is mentioned
            response = "India has faced numerous natural disasters throughout its history. Here are some significant events from the last 20 years:\n\n"
            for disaster_type, events in self.historical_disasters.items():
                if events:
                    response += f"{disaster_type.capitalize()}:\n"
                    # Include only a few recent events from each type in the summary
                    count = 0
                    for event in events:
                        # Only show events from the last 20 years (since 2000+)
                        if event['year'].startswith('2') and count < 3:
                            response += f"- {event['year']} ({event['location']}): {event['description'][:100]}...\n"
                            count += 1
                    response += "\n"
            return response
        
        # Provide detailed information about a specific disaster type
        disaster_type = disaster_types[0]
        if disaster_type in self.historical_disasters and self.historical_disasters[disaster_type]:
            events = self.historical_disasters[disaster_type]
            response = f"Historical {disaster_type} events in India over the last 20+ years:\n\n"
            
            # Look for location mentions in the user query
            for event in events:
                # Focus on events from recent decades
                if event['year'].startswith('19') and len(events) > 10:
                    continue
                response += f"- {event['year']} ({event['location']}): {event['description'][:150]}...\n\n"
            
            return response
        
        return f"I don't have historical information about {disaster_type} events in India."
    
    def get_helpline_numbers(self, state=None):
        """Get helpline numbers for a specific state or nationally"""
        if state and state in self.helpline_numbers:
            return {state: self.helpline_numbers[state]}
        return self.helpline_numbers
    
    def _get_specific_historical_response(self, disaster_types, locations, years, user_message):
        """Get information about specific historical disasters based on location and/or year"""
        # Default to flood if no disaster type specified but asking about specific events
        if not disaster_types and (locations or years):
            # Check if we can determine disaster type from the query itself
            for disaster_type in self.disaster_types:
                if disaster_type in user_message.lower():
                    disaster_types = [disaster_type]
                    break
            
            # If still no disaster type, look for clues in locations
            if not disaster_types:
                # Kerala is often associated with floods
                if 'kerala' in locations:
                    disaster_types = ['flood']
                # Uttarakhand is often associated with landslides
                elif 'uttarakhand' in locations:
                    disaster_types = ['landslide']
                # Gujarat is often associated with earthquakes
                elif 'gujarat' in locations or 'bhuj' in locations:
                    disaster_types = ['earthquake']
                # Tamil Nadu is often associated with tsunamis (2004)
                elif 'tamil nadu' in locations:
                    disaster_types = ['tsunami']
                # Maharashtra commonly experiences droughts
                elif 'maharashtra' in locations:
                    disaster_types = ['drought']
        
        # If we have identified a disaster type
        if disaster_types:
            disaster_type = disaster_types[0]
            matching_events = []
            
            # Get events for the disaster type
            if disaster_type in self.historical_disasters:
                events = self.historical_disasters[disaster_type]
                
                # Filter events by year and location if provided
                for event in events:
                    year_match = not years or any(year in event['year'] for year in years)
                    location_match = not locations or any(location.lower() in event['location'].lower() for location in locations)
                    
                    if year_match and location_match:
                        matching_events.append(event)
            
            if matching_events:
                if len(matching_events) == 1:
                    # If there's just one match, give detailed information
                    event = matching_events[0]
                    response = f"Details about the {event['year']} {disaster_type} in {event['location']}:\n\n{event['description']}"
                    return response
                else:
                    # If there are multiple matches, summarize them
                    response = f"Historical {disaster_type} events matching your criteria:\n\n"
                    for event in matching_events:
                        response += f"- {event['year']} ({event['location']}): {event['description']}\n\n"
                    return response
            
            # If we have a disaster type but no matching events
            if years:
                return f"I don't have information about {disaster_type} events in {', '.join(years)} in my database."
            elif locations:
                return f"I don't have information about {disaster_type} events in {', '.join(locations)} in my database."
            else:
                return self._get_historical_response([disaster_type])
        
        # If we have years or locations but couldn't determine disaster type
        if years or locations:
            response = "I found some historical disaster events that might be relevant:\n\n"
            found_events = False
            
            # Look through all disaster types
            for disaster_type, events in self.historical_disasters.items():
                for event in events:
                    year_match = not years or any(year in event['year'] for year in years)
                    location_match = not locations or any(location.lower() in event['location'].lower() for location in locations)
                    
                    if year_match and location_match:
                        response += f"- {event['year']} {disaster_type} in {event['location']}: {event['description'][:150]}...\n\n"
                        found_events = True
            
            if found_events:
                return response
            else:
                if years and locations:
                    return f"I don't have information about disasters in {', '.join(locations)} during {', '.join(years)}."
                elif years:
                    return f"I don't have information about disasters during {', '.join(years)}."
                elif locations:
                    return f"I don't have information about disasters in {', '.join(locations)}."
        
        # Default response if nothing matched
        return "I don't have specific historical information matching your query. You can ask about floods, landslides, tsunamis, earthquakes, or droughts in specific states or years."

    def _get_early_warning_info(self, disaster_type=None):
        """Get information about early warning systems for disasters"""
        early_warning_info = {
            'flood': "Flood Early Warning Systems in India:\n\n"
                     "The Central Water Commission (CWC) operates a network of 878 hydrological observation stations across India's river basins. When water levels cross danger thresholds, alerts are issued to local authorities and communities.\n\n"
                     "IMD's Doppler Weather Radar network provides real-time rainfall intensity data, offering 3-6 hours of warning time for urban floods and flash floods.\n\n"
                     "The National Disaster Management Authority (NDMA) operates the Flood Early Warning System (FEWS) which combines weather forecasts, river flow data, and topographical information to predict flooding 72 hours in advance. Alerts are disseminated via SMS, radio, TV, and the NDMA app.",
                     
            'landslide': "Landslide Early Warning Systems in India:\n\n"
                         "The Geological Survey of India (GSI) maintains a network of 180 landslide monitoring stations across landslide-prone regions. These provide warnings based on rainfall thresholds and ground movement sensors.\n\n"
                         "In the Western Ghats and Himalayan regions, Rain Gauge-Based Warning Systems determine landslide warnings based on rainfall intensity and duration.\n\n"
                         "The Indian Space Research Organisation (ISRO) uses satellite imagery to identify areas with high landslide susceptibility. The National Remote Sensing Centre (NRSC) issues warnings when conditions for landslides are detected.",
                         
            'tsunami': "Tsunami Early Warning System in India:\n\n"
                       "The Indian Tsunami Early Warning Centre (ITEWC) operated by the Indian National Centre for Ocean Information Services (INCOIS) provides tsunami warnings for the entire Indian Ocean region.\n\n"
                       "The system uses a network of bottom pressure recorders, tide gauges, and seismic stations to detect tsunamigenic earthquakes. It can issue alerts within 10-20 minutes of an earthquake.\n\n"
                       "Three levels of warnings are issued: Warning (high risk, immediate evacuation), Alert (medium risk, prepare to evacuate), and Watch (low risk, stay away from coasts).",
                       
            'earthquake': "Earthquake Early Warning Systems in India:\n\n"
                          "The National Centre for Seismology (NCS) operates a network of 115 seismological observatories across India to monitor seismic activity.\n\n"
                          "While true early warning for earthquakes (before shaking begins) is limited, the Indian Meteorological Department (IMD) provides real-time earthquake information and post-earthquake assessments.\n\n"
                          "In high-risk areas like Delhi-NCR, Gujarat, and Northeast India, microzonation studies have been conducted to identify vulnerable areas and develop response plans.",
                          
            'drought': "Drought Monitoring and Early Warning Systems in India:\n\n"
                       "The India Meteorological Department (IMD) provides Seasonal Climate Forecasts with monsoon predictions to help anticipate potential drought conditions.\n\n"
                       "The National Agricultural Drought Assessment and Monitoring System (NADAMS) uses satellite data to monitor agricultural drought conditions every two weeks during the crop growing season.\n\n"
                       "The Drought Early Warning System (DEWS) integrates meteorological, hydrological, and agricultural data to issue warnings 3-6 months in advance. Warnings are classified as Normal, Watch, Alert, and Emergency based on drought severity.",
                       
            'cyclone': "Cyclone Early Warning System in India:\n\n"
                        "The India Meteorological Department (IMD) operates a comprehensive Cyclone Warning System with weather satellites, Doppler weather radars, automated weather stations, and ocean buoys.\n\n"
                        "IMD can track and forecast cyclones 5-7 days in advance with high accuracy, providing regular bulletins every 3 hours during a cyclone.\n\n"
                        "Four-stage warnings are issued: Pre-Cyclone Watch (72 hours before), Cyclone Alert (48 hours), Cyclone Warning (24 hours), and Post-Landfall Outlook. The NDMA disseminates warnings through multiple channels including the UMANG mobile app.",
                        
            'heatwave': "Heat Wave Early Warning System in India:\n\n"
                         "The India Meteorological Department (IMD) issues heat wave warnings when maximum temperatures exceed 40°C in plains or 30°C in hill regions.\n\n"
                         "Color-coded alerts are used: Green (no action needed), Yellow (be updated), Orange (be prepared), and Red (take action). Five-day heat wave forecasts are issued during summer months.\n\n"
                         "The National Disaster Management Authority (NDMA) has implemented a Heat Action Plan in vulnerable states like Gujarat, Odisha, and Telangana, which includes public cooling centers and advisory communications.",
                         
            'wildfire': "Forest Fire Early Warning System in India:\n\n"
                         "The Forest Survey of India (FSI) operates a Forest Fire Alert System that uses satellite data from NASA and ISRO to detect forest fires.\n\n"
                         "Pre-fire alerts are generated based on temperature, humidity, and fuel load conditions. SMS alerts are sent to forest officials and community representatives in high-risk areas.\n\n"
                         "The system provides automated fire alerts within 30 minutes of detection to over 66,000 registered users across forest departments."
        }
        
        if disaster_type and disaster_type in early_warning_info:
            return early_warning_info[disaster_type]
        
        # Default response if no specific disaster type is mentioned or not in our database
        return ("Early warning systems are crucial for disaster preparedness in India. These include:\n\n"
                "- Indian Meteorological Department (IMD) for cyclones, floods and heatwaves\n"
                "- Tsunami Early Warning Centre (ITEWC) for tsunamis\n"
                "- National Centre for Seismology for earthquakes\n"
                "- Drought Early Warning System (DEWS)\n"
                "- Forest Fire Alert System for wildfires\n"
                "- Landslide Early Warning Systems in mountainous regions\n\n"
                "You can ask about early warning systems for specific disasters like floods, cyclones, or earthquakes.")
    
    def _get_first_aid_info(self, disaster_type=None):
        """Get first aid and emergency medical information related to disasters"""
        first_aid_info = {
            'general': "Basic First Aid Guidelines During Disasters:\n\n"
                      "1. Ensure your own safety before helping others\n"
                      "2. Call emergency services (Dial 108 or 112) as soon as possible\n"
                      "3. Check for consciousness, breathing, and severe bleeding\n"
                      "4. Keep the injured person still if spinal injury is suspected\n"
                      "5. Apply direct pressure to stop bleeding\n"
                      "6. Keep the person warm and calm\n"
                      "7. Do not give food or water to unconscious persons\n"
                      "8. Document what happened and any treatments provided\n\n"
                      "Essential items for a disaster first aid kit include:\n"
                      "- Bandages in various sizes and adhesive tape\n"
                      "- Antiseptic wipes and antibiotic ointment\n"
                      "- Disposable gloves and face masks\n"
                      "- Scissors, tweezers, and safety pins\n"
                      "- Thermometer and blood pressure monitor\n"
                      "- OTC pain relievers and antihistamines\n"
                      "- Emergency blanket and instant cold packs\n"
                      "- Flashlight with extra batteries\n"
                      "- First aid instruction manual or app\n"
                      "- Personal medications and prescriptions\n"
                      "- Hand sanitizer and clean cloths\n"
                      "- Emergency contact information",
                      
            'flood': "First Aid During Floods:\n\n"
                     "1. Avoid contact with floodwater which may be contaminated\n"
                     "2. Clean and disinfect all wounds that contact floodwater\n"
                     "3. Treat skin rashes or infections promptly\n"
                     "4. For near-drowning victims:\n"
                     "   - Remove from water and check breathing\n"
                     "   - Start CPR if not breathing (30 chest compressions followed by 2 rescue breaths)\n"
                     "   - Turn on side if breathing but unconscious\n"
                     "   - Seek medical help immediately\n"
                     "5. Watch for symptoms of waterborne diseases like diarrhea, vomiting, or fever\n\n"
                     "Additional items for flood-specific first aid kit:\n"
                     "- Water purification tablets or portable filter\n"
                     "- Extra antibiotics and anti-diarrheal medication\n"
                     "- Waterproof containers for medications\n"
                     "- Rubber gloves and boots to avoid contamination\n"
                     "- Waterproof flashlight and extra batteries",
                     
            'earthquake': "First Aid After Earthquakes:\n\n"
                          "1. For crush injuries:\n"
                          "   - Call for help before attempting to free the person\n"
                          "   - Control bleeding with direct pressure\n"
                          "   - Immobilize injured areas\n"
                          "   - Monitor for crush syndrome (kidney failure after prolonged compression)\n"
                          "2. For fractures:\n"
                          "   - Immobilize the injured area with splints\n"
                          "   - Apply cold packs to reduce swelling\n"
                          "   - Elevate the injured limb if possible\n"
                          "3. For head injuries:\n"
                          "   - Keep the person still\n"
                          "   - Monitor for changes in consciousness\n"
                          "   - Control external bleeding without applying pressure to skull fractures\n\n"
                          "Earthquake-specific first aid kit should include:\n"
                          "- Dust masks or N95 respirators\n"
                          "- Splints and triangular bandages for fractures\n"
                          "- Heavy-duty gloves for removing debris\n"
                          "- Duct tape and plastic sheeting\n"
                          "- Crowbar or basic tools for light rescue\n"
                          "- Emergency whistle to signal for help",
                          
            'landslide': "First Aid After Landslides:\n\n"
                         "1. Stay away from the slide area - more slides may occur\n"
                         "2. For those extracted from debris:\n"
                         "   - Check airway, breathing, and circulation\n"
                         "   - Treat for shock by laying the person flat, elevating legs, and keeping warm\n"
                         "   - Immobilize suspected fractures\n"
                         "   - Clean wounds thoroughly to prevent infection\n"
                         "3. Watch for hypothermia if the person was trapped for a long time\n"
                         "4. Monitor for crush syndrome (kidney failure after prolonged compression)\n\n"
                         "Landslide-specific first aid items:\n"
                         "- Heavy-duty gloves and boots\n"
                         "- Ropes for emergency evacuation\n"
                         "- Portable shovel\n"
                         "- Emergency thermal blankets\n"
                         "- Water filtration system",
                         
            'tsunami': "First Aid After Tsunamis:\n\n"
                       "1. For near-drowning victims:\n"
                       "   - Remove from water and check breathing\n"
                       "   - Start CPR if not breathing\n"
                       "   - Turn on side if breathing but unconscious\n"
                       "2. Treat for hypothermia by removing wet clothes and warming gradually\n"
                       "3. Clean all wounds thoroughly to prevent infection from contaminated water\n"
                       "4. Watch for symptoms of bacterial infection including redness, swelling, or fever\n"
                       "5. Seek medical attention for injuries from floating debris\n\n"
                       "Tsunami-specific first aid supplies:\n"
                       "- Waterproof emergency blankets\n"
                       "- Extra sets of dry clothing\n"
                       "- Water purification tablets\n"
                       "- Waterproof containers for supplies\n"
                       "- Salt solution for wound cleaning",
                       
            'cyclone': "First Aid After Cyclones:\n\n"
                        "1. For wounds from flying debris:\n"
                        "   - Clean thoroughly with clean water and soap\n"
                        "   - Apply antibiotic ointment if available\n"
                        "   - Cover with sterile dressing\n"
                        "2. For fractures:\n"
                        "   - Immobilize the injured area\n"
                        "   - Apply cold packs to reduce swelling\n"
                        "3. For electrical injuries (from downed power lines):\n"
                        "   - Do not touch the person if they're still in contact with the electrical source\n"
                        "   - Check breathing and pulse once safe\n"
                        "   - Treat burns with cool, clean, wet cloth\n\n"
                        "Cyclone-specific first aid items:\n"
                        "- Extra bandages for multiple injuries\n"
                        "- Waterproof containers for medications\n"
                        "- Wind-up or battery-powered radio\n"
                        "- Long-lasting food and water supplies\n"
                        "- Solar charger for communication devices",
                        
            'heatwave': "First Aid for Heat-Related Illnesses:\n\n"
                       "1. For heat exhaustion (heavy sweating, weakness, cold/clammy skin):\n"
                       "   - Move to a cool place\n"
                       "   - Loosen clothing\n"
                       "   - Apply cool, wet cloths\n"
                       "   - Sip water slowly\n"
                       "2. For heat stroke (high body temperature, hot/red skin, rapid pulse):\n"
                       "   - Call emergency services immediately\n"
                       "   - Move to cooler location\n"
                       "   - Use cool cloths or bath to lower temperature\n"
                       "   - Do NOT give fluids\n"
                       "3. For heat cramps:\n"
                       "   - Stop physical activity and rest\n"
                       "   - Drink water or sports drinks\n"
                       "   - Wait for cramps to subside before resuming activity\n\n"
                       "Heatwave first aid kit additions:\n"
                       "- Oral rehydration solution packets\n"
                       "- Instant ice packs\n"
                       "- Electrolyte replacement drinks\n"
                       "- Thermometer to monitor body temperature\n"
                       "- Cooling towels or cloths",
                       
            'drought': "First Aid During Drought Conditions:\n\n"
                      "1. For dehydration symptoms (extreme thirst, dry mouth, fatigue):\n"
                      "   - Move to shaded area\n"
                      "   - Drink water slowly\n"
                      "   - For severe cases, use oral rehydration solution\n"
                      "2. For heat-related illnesses, follow heatwave protocols\n"
                      "3. For respiratory issues due to dust:\n"
                      "   - Avoid outdoor activities when dusty\n"
                      "   - Use masks when outdoors\n"
                      "   - Rinse eyes with clean water if irritated\n\n"
                      "Drought first aid kit should include:\n"
                      "- Extra water supplies (minimum 3 liters per person per day)\n"
                      "- Oral rehydration salts\n"
                      "- Dust masks or respirators\n"
                      "- Eye drops for dust irritation\n"
                      "- Moisturizing lotion for cracked skin",
                       
            'wildfire': "First Aid for Wildfire-Related Injuries:\n\n"
                      "1. For smoke inhalation:\n"
                      "   - Move to fresh air immediately\n"
                      "   - Loosen tight clothing\n"
                      "   - If breathing is difficult, seek medical attention\n"
                      "2. For burns:\n"
                      "   - Cool the burn with cool (not cold) water for 10-15 minutes\n"
                      "   - Cover with clean, dry cloth\n"
                      "   - Do not apply creams, ointments, or butter\n"
                      "   - Do not break blisters\n"
                      "3. For eye irritation from smoke:\n"
                      "   - Rinse eyes with clean water\n"
                      "   - Avoid rubbing eyes\n\n"
                      "Wildfire first aid kit should include:\n"
                      "- N95 respirator masks\n"
                      "- Eye drops for smoke irritation\n"
                      "- Burn gel or aloe vera gel\n"
                      "- Clean water in sealed containers\n"
                      "- Eye protection goggles",
                       
            'pandemic': "First Aid During Pandemic Situations:\n\n"
                       "1. For suspected infection:\n"
                       "   - Isolate from others\n"
                       "   - Monitor temperature and symptoms\n"
                       "   - Contact healthcare provider before visiting medical facilities\n"
                       "2. For respiratory distress:\n"
                       "   - Maintain sitting position to ease breathing\n"
                       "   - Seek emergency care for severe difficulty breathing\n"
                       "3. For managing fever:\n"
                       "   - Use fever-reducing medications as advised\n"
                       "   - Apply cool cloth to forehead\n"
                       "   - Stay hydrated\n\n"
                       "Pandemic first aid supplies:\n"
                       "- Medical-grade face masks (N95 or surgical)\n"
                       "- Hand sanitizer (minimum 60% alcohol)\n"
                       "- Disposable gloves\n"
                       "- Disinfectant wipes\n"
                       "- Thermometer and pulse oximeter\n"
                       "- OTC medications for fever and cough\n"
                       "- Vitamin supplements as advised by healthcare professionals"
        }
        
        if disaster_type and disaster_type in first_aid_info:
            return first_aid_info[disaster_type]
        
        return first_aid_info['general']
    
    def _get_general_disaster_info(self, query):
        """Provide answers to common general questions about disasters"""
        general_questions = {
            'what is a natural disaster': 
                "A natural disaster is a catastrophic event caused by natural processes of the Earth, such as earthquakes, floods, hurricanes, wildfires, and tsunamis, leading to property damage, environmental destruction, and loss of life.",
                
            'what are the types of natural disasters': 
                "The main types of natural disasters include earthquakes, floods, hurricanes, tornadoes, tsunamis, volcanic eruptions, landslides, wildfires, droughts, and extreme weather events.",
                
            'what causes natural disasters': 
                "Natural disasters can be caused by geological activities (earthquakes, volcanic eruptions), weather conditions (hurricanes, tornadoes), hydrological factors (floods, tsunamis), or human-induced changes such as deforestation and climate change.",
                
            'what is an earthquake': 
                "An earthquake is the shaking of the Earth's surface caused by the movement of tectonic plates along faults.",
                
            'how are earthquakes measured': 
                "Earthquakes are measured using the Richter scale (magnitude) and the Mercalli scale (intensity based on observed effects).",
                
            'what causes earthquakes': 
                "Earthquakes are primarily caused by tectonic plate movements, volcanic activity, and human activities like mining and reservoir-induced seismicity.",
                
            'what should i do during an earthquake': 
                "During an earthquake: 1) Drop, cover, and hold on; 2) Stay indoors away from windows and heavy furniture; 3) If outdoors, move to an open area away from buildings.",
                
            'how can we prepare for an earthquake': 
                "To prepare for an earthquake: 1) Secure heavy furniture and appliances; 2) Have an emergency kit ready; 3) Educate family members on earthquake drills.",
                
            'what causes floods': 
                "Floods are caused by heavy rainfall, storm surges, river overflow, melting snow, or dam failures.",
                
            'how can i protect my home from flooding': 
                "To protect your home from flooding: 1) Elevate electrical appliances and valuables; 2) Use sandbags to block water entry; 3) Have an emergency evacuation plan.",
                
            'what should i do if i am caught in a flood': 
                "If caught in a flood: 1) Move to higher ground immediately; 2) Avoid walking or driving through floodwaters; 3) Listen to emergency broadcasts for updates.",
                
            'what causes landslides': 
                "Landslides are caused by heavy rainfall, earthquakes, volcanic eruptions, or human activities like deforestation and mining.",
                
            'how can landslides be prevented': 
                "To prevent landslides: 1) Plant vegetation on slopes; 2) Avoid construction in landslide-prone areas; 3) Build retaining walls where necessary.",
                
            'what should i do if a landslide occurs': 
                "If a landslide occurs: 1) Move away from the path of the slide; 2) Seek shelter in a strong building; 3) Stay alert for aftershocks and additional slides.",
                
            'what is the difference between a hurricane and a tornado': 
                "A hurricane is a large, rotating storm system that forms over warm ocean waters, while a tornado is a violent, rotating column of air that forms over land.",
                
            'how can i stay safe during a hurricane': 
                "To stay safe during a hurricane: 1) Evacuate if instructed; 2) Stay indoors, away from windows; 3) Have a hurricane preparedness kit ready.",
                
            'what are the warning signs of a tornado': 
                "Warning signs of a tornado include: 1) Dark, greenish skies; 2) Loud roaring noise (like a freight train); 3) Sudden drop in air pressure.",
                
            'what causes tsunamis': 
                "Tsunamis are caused by underwater earthquakes, volcanic eruptions, or landslides displacing large amounts of water.",
                
            'how can i recognize a tsunami warning': 
                "Tsunami warning signs include: 1) Strong earthquake near the coast; 2) Sudden sea level changes (rapid receding or surging water); 3) Official tsunami alerts from authorities.",
                
            'what should i do if i see a tsunami approaching': 
                "If you see a tsunami approaching: 1) Move to higher ground immediately; 2) Follow evacuation routes; 3) Stay away from beaches and coastal areas.",
                
            'what causes wildfires': 
                "Wildfires are caused by lightning, human activities (campfires, cigarette butts), or extreme heat and dry conditions.",
                
            'how can wildfires be prevented': 
                "To prevent wildfires: 1) Avoid open flames in dry areas; 2) Clear dry vegetation around homes; 3) Follow local fire restrictions.",
                
            'what are the health risks of wildfire smoke': 
                "Wildfire smoke can cause respiratory issues, eye irritation, and aggravate conditions like asthma.",
                
            'what is a drought': 
                "A drought is a prolonged period of abnormally low rainfall, leading to water shortages.",
                
            'how can we conserve water during a drought': 
                "To conserve water during a drought: 1) Fix leaks and use water-efficient appliances; 2) Limit lawn watering and car washing; 3) Reuse water whenever possible.",
                
            'what causes volcanic eruptions': 
                "Volcanic eruptions occur when magma, gases, and ash are expelled from a volcano due to pressure build-up.",
                
            'how can we stay safe during a volcanic eruption': 
                "During a volcanic eruption: 1) Evacuate the danger zone; 2) Wear masks to protect against ash inhalation; 3) Avoid river valleys that may carry lava flows.",
                
            'what are the warning signs of a volcanic eruption': 
                "Warning signs of a volcanic eruption include: 1) Increased seismic activity; 2) Gas emissions from vents; 3) Swelling or bulging of the volcano."
        }
        
        # Look for the closest matching question
        normalized_query = query.lower().strip().rstrip('?')
        
        for question, answer in general_questions.items():
            if normalized_query in question or question in normalized_query:
                return answer
                
        # If no direct match found, return a general response
        return None
        
    def get_historical_disasters(self, disaster_type=None):
        """Get historical disaster information"""
        if disaster_type and disaster_type in self.historical_disasters:
            return {disaster_type: self.historical_disasters[disaster_type]}
        return self.historical_disasters
