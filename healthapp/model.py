from django.db import models
from django.contrib.auth.models import User

class HealthRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Health inputs
    glucose = models.FloatField()
    blood_pressure = models.FloatField()
    insulin = models.FloatField()  # ✅ Added back
    bmi = models.FloatField()
    dpf = models.FloatField()
    age = models.IntegerField()

    # Prediction result
    prediction = models.CharField(max_length=20)

    # AI-generated plans
    workout_plan = models.TextField()
    diet_plan = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.prediction} - {self.submitted_at.strftime('%Y-%m-%d')}"
