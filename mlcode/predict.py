import pickle
import numpy as np

# Load the saved model
with open("sklearn_decision_tree.pkl", "rb") as f:
    model = pickle.load(f)

# Ask user to enter input values
print("Enter the following health details:")

glucose = float(input("Glucose level: "))
bp = float(input("Blood Pressure: "))
insulin = float(input("Insulin level: "))
bmi = float(input("BMI: "))
dpf = float(input("Diabetes Pedigree Function: "))
age = float(input("Age: "))

# Combine all inputs into one list
sample_input = [glucose, bp, insulin, bmi, dpf, age]

# Convert to array and reshape for prediction
input_array = np.array(sample_input).reshape(1, -1)

# Predict using the loaded model
prediction = model.predict(input_array)

# Show result
if prediction[0] == 1:
    print("\nHIGH RISK")
else:
    print("\nLOW RISK")
