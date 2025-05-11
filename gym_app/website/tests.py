from django.test import TestCase
from website.models import TrainingPlan
from django.contrib.auth.models import User

class TrainingPlanTestCase(TestCase):
    
    def setUp(self):
        # Tworzymy użytkownika, bo TrainingPlan wymaga usera
        self.user = User.objects.create_user(username='testuser', password='password123')
        
    def test_training_plan_get_training_days_display(self):
        # Tworzymy plan treningowy powiązany z użytkownikiem
        plan = TrainingPlan.objects.create(
            user=self.user,
            name="Test Plan",
            training_days=['mon', 'tue']
        )
        
        # Sprawdzamy, czy dni treningowe są zwracane poprawnie
        training_days_display = plan.get_training_days_display()
        print(training_days_display)
        
        # Assercja - sprawdzamy, czy wynik jest taki, jakiego się spodziewamy
        self.assertEqual(training_days_display, ['Monday', 'Tuesday'])

