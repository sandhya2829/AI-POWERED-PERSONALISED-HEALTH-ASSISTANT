from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import HealthRecord
import os, pickle
import markdown
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env & configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Load scikit-learn model (updated)
model_path = os.path.join(os.path.dirname(__file__), 'sklearn_decision_tree.pkl')
with open(model_path, 'rb') as f:
    sklearn_model = pickle.load(f)

# Gemini helper
def generate_gemini_response(prompt):
    try:
        response = gemini_model.generate_content(prompt)
        return markdown.markdown(response.text.strip())
    except Exception as e:
        return f"<b>Gemini Error:</b> {str(e)}"

# Register
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not username or not password:
            return render(request, 'register.html', {'error': 'All fields are required.'})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists.'})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('predict')
    return render(request, 'register.html')

# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('predict')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials.'})
    return render(request, 'login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Prediction View (updated with sklearn)
@login_required
def predict_view(request):
    if request.method == 'POST':
        try:
            data = {
                'name': request.POST['name'],
                'gender': request.POST['gender'],
                'glucose': int(request.POST['glucose']),
                'bp': int(request.POST['bp']),
                'insulin': int(request.POST['insulin']),
                'bmi': float(request.POST['bmi']),
                'dpf': float(request.POST['dpf']),
                'age': int(request.POST['age']),
            }
            request.session['user_input'] = data
            features = [data['glucose'], data['bp'], data['insulin'], data['bmi'], data['dpf'], data['age']]

            #  Predict using scikit-learn model
            result = sklearn_model.predict([features])[0]
            prediction = "High Risk" if result == 1 else "Low Risk"

            request.session['risk'] = prediction
            return redirect('dashboard')
        except Exception as e:
            return render(request, 'form.html', {'error': str(e)})
    return render(request, 'form.html')

# Home
@login_required
def home_view(request):
    return render(request, 'home.html')

# Dashboard
@login_required
def dashboard_view(request):
    if 'risk' not in request.session:
        return redirect('predict')
    risk = request.session.get('risk', 'Low Risk')
    return render(request, 'dashboard.html', {'result': risk})

# Diet Plan
@login_required
def diet_plan_view(request):
    data = request.session.get('user_input', {})
    risk = request.session.get('risk', 'Low Risk')
    if not data:
        return render(request, 'diet_plan.html', {'diet': "No data", 'chat_response': None})
    
    prompt = f"""Create a personalized diet plan for {data.get('name')}, a {data.get('gender')} aged {data.get('age')} with Glucose {data.get('glucose')}, BMI {data.get('bmi')}, Risk Level: {risk}."""
    diet = generate_gemini_response(prompt)

    # Save to database if not already saved
    if not request.session.get('saved'):
        workout_prompt = f"""Create a personalized workout plan for {data.get('name')}, a {data.get('gender')} aged {data.get('age')} with BP {data.get('bp')}, BMI {data.get('bmi')}, Risk Level: {risk}."""
        workout_plan = generate_gemini_response(workout_prompt)

        HealthRecord.objects.create(
            user=request.user,
            glucose=data['glucose'],
            blood_pressure=data['bp'],
            insulin=data['insulin'],
            bmi=data['bmi'],
            dpf=data['dpf'],
            age=data['age'],
            prediction=risk,
            workout_plan=workout_plan,
            diet_plan=diet
        )
        request.session['saved'] = True

    chat_response = None
    if request.method == 'POST' and 'chat_prompt' in request.POST:
        user_query = request.POST['chat_prompt']
        chat_response = generate_gemini_response(f"Answer shortly: {user_query}")
    return render(request, 'diet_plan.html', {'diet': diet, 'chat_response': chat_response})

# Workout Plan
@login_required
def workout_plan_view(request):
    data = request.session.get('user_input', {})
    risk = request.session.get('risk', 'Low Risk')
    if not data:
        return render(request, 'workout_plan.html', {'workout': "No data", 'chat_response': None})
    prompt = f"""Create a personalized workout plan for {data.get('name')}, a {data.get('gender')} aged {data.get('age')} with BP {data.get('bp')}, BMI {data.get('bmi')}, Risk Level: {risk}."""
    workout = generate_gemini_response(prompt)
    chat_response = None
    if request.method == 'POST' and 'chat_prompt' in request.POST:
        user_query = request.POST['chat_prompt']
        chat_response = generate_gemini_response(f"Answer shortly: {user_query}")
    return render(request, 'workout_plan.html', {'workout': workout, 'chat_response': chat_response})

# Exercise Search
@login_required
def exercise_search_view(request):
    exercises = {
        "Push Up": "IODxDxX7oi4",
        "Squat": "xuf1czJv-XI",
        "Lunge": "QOVaHwm-Q6U",
        "Burpee": "TU8QYVW0gDU",
        "Deadlift": "uhghy9pFIPY",
        "Plank": "pvIjsG5Svck",
        "Bench Press": "FQy6mzpcBs0",
        "Bicep Curl": "Ost6UtXWTJg",
        "Mountain Climbing": "ZhiCSdOVJp0",
        "Dumbbell row": "VJ-2i-WY-q0"
    }
    query = request.GET.get('query', '')
    results = []
    if query:
        prompt = f"Give 5 steps to do the exercise '{query}' in bullet points under 200 words."
        description = generate_gemini_response(prompt)
        results.append({
            'description': description,
            'video_id': exercises.get(query, '')
        })
    return render(request, 'exercise_search.html', {
        'query': query,
        'exercises': list(exercises.keys()),
        'results': results
    })

# Diet Search
@login_required
def diet_search_view(request):
    foods = {
        "banana": "W5jIsrRzYXs",
        "apple": "vpDWkrU77ps",
        "spinach": "MjiwLYS37Ms",
        "broccoli": "WSBh6-0vyRE",
        "carrot": "IATn3DcKMXM",
        "oats": "yis-6dP8_JE",
        "almonds": "ovHblnNMHYs",
        "avocado": "bfxF7MHzbcE",
    }
    query = request.GET.get('query', '')
    results = []
    if query:
        prompt = f"List health benefits and uses of {query} in under 200 words using bullet points."
        description = generate_gemini_response(prompt)
        results.append({
            'description': description,
            'video_id': foods.get(query.lower(), '')
        })
    return render(request, 'diet_search.html', {
        'query': query,
        'foods': list(foods.keys()),
        'results': results
    })

# Progress View
@login_required
def progress_view(request):
    data = request.session.get('user_input', {})
    if not data:
        return redirect('dashboard')
    user_data = {
        'Glucose': int(data.get('glucose', 0)),
        'BloodPressure': int(data.get('bp', 0)),
        'Insulin': int(data.get('insulin', 0)),
        'BMI': float(data.get('bmi', 0.0)),
        'DPF': float(data.get('dpf', 0.0)),
        'Age': int(data.get('age', 0))
    }
    normal_data = {
        'Glucose': 100,
        'BloodPressure': 80,
        'Insulin': 85,
        'BMI': 22.5,
        'DPF': 0.5,
        'Age': 30
    }
    return render(request, 'progress.html', {
        'user_data_keys': list(user_data.keys()),
        'user_data_values': list(user_data.values()),
        'normal_data_values': list(normal_data.values())
    })

# Health History View
@login_required
def health_history_view(request):
    records = HealthRecord.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'health_history.html', {'records': records})
