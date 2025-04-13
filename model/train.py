import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Load the dataset
data = pd.read_csv('train.csv')

# Features and target variable
features = [
    'MonsoonIntensity', 'TopographyDrainage', 'RiverManagement', 'Deforestation', 
    'Urbanization', 'ClimateChange', 'DamsQuality', 'Siltation', 'AgriculturalPractices', 
    'Encroachments', 'IneffectiveDisasterPreparedness', 'DrainageSystems', 
    'CoastalVulnerability', 'Landslides', 'Watersheds', 'DeterioratingInfrastructure', 
    'PopulationScore', 'WetlandLoss', 'InadequatePlanning', 'PoliticalFactors'
]
target = 'FloodProbability'  

# Splitting the data
X = data[features]
y = data[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Feature scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Reshape data for LSTM input
X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

# Building the RNN model#######################################################################################
#model = Sequential([
#    LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
#    Dropout(0.2),
#    LSTM(units=50, return_sequences=False),
#    Dropout(0.2),
#    Dense(units=1, activation='sigmoid')  # Binary classification])

# Compiling the model
#model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Training the model
#model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=1)

# Save the model and scaler
#model.save('flood_prediction_rnn_model.h5')  # Save the Keras model
joblib.dump(scaler, 'scaler.joblib')  # Save the scaler using joblib

# Save model info
#model_info = {
#    'model_path': 'flood_prediction_rnn_model.h5',
#    'scaler_path': 'scaler.joblib'}
#joblib.dump(model_info, 'model_info.joblib')
#print("Model and scaler have been saved using joblib.")
#################################################################################################################
# To load later:
loaded_model_info = joblib.load('model_info.joblib')
loaded_scaler = joblib.load(loaded_model_info['scaler_path'])
loaded_model = load_model(loaded_model_info['model_path'])

# Prepare test data
X_test = loaded_scaler.transform(X_test.reshape(X_test.shape[0], X_test.shape[2]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

# Make predictions
y_pred = (loaded_model.predict(X_test) > 0.5).astype("int32")
# Convert y_test to integer type if needed
y_test = y_test.astype(int)  # Ensure y_test is binary (0 or 1)

# Make predictions
y_pred_probs = loaded_model.predict(X_test)  # Get probabilities
y_pred_binary = (y_pred_probs > 0.5).astype(int).flatten()

# Compute accuracy
print(f'Accuracy: {accuracy_score(y_test, y_pred_binary)}')
print('Classification Report:\n', classification_report(y_test,y_pred_binary))
print('Confusion Matrix:\n', confusion_matrix(y_test, y_pred_binary))
