from django.test import TestCase, Client
from website.models import TrainingPlan,Exercise,TrainingPlanExercise
from django.contrib.auth.models import User, Group
from django.urls import reverse
from .forms import TrainingPlanForm

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

class ExerciseModelTestCase(TestCase):
    def test_exercise(self):
        #Tworzymy ćwiczenie
        exercise = Exercise.objects.create(name="Push-up", description="Chest workout")
        #Sprawdzamy poprawnosć nazwy
        self.assertEqual(str(exercise), "Push-up")

class TrainingPlanExerciseModelTestCase(TestCase):
    def setUp(self):
        #Tworzymy użytkownika plan i ćwiczenie
        self.user = User.objects.create_user(username='tester', password='123')
        self.plan = TrainingPlan.objects.create(user=self.user, name="My Plan", training_days=['mon'])
        self.exercise = Exercise.objects.create(name="Squats")

    def test_training_plan_exercise_str(self):
        # Tworzymy relację plan-ćwiczenie z liczbą powtórzeń
        tpe = TrainingPlanExercise.objects.create(training_plan=self.plan, exercise=self.exercise, repeats=15)
        # Sprawdzamy poprawność
        self.assertEqual(str(tpe), "Squats x 15")

    def test_unique_training_plan_exercise(self):
        # Dodajemy pierwszą relację plan-ćwiczenie
        TrainingPlanExercise.objects.create(training_plan=self.plan, exercise=self.exercise, repeats=10)
        # Próba dodania drugiej relacji z tym samym planem i ćwiczeniem powinna rzucić wyjątek
        with self.assertRaises(Exception): 
            TrainingPlanExercise.objects.create(training_plan=self.plan, exercise=self.exercise, repeats=12)

class TrainingPlanFormTestCase(TestCase):
    def setUp(self):
        # Tworzymy użytkownika do przekazania do formularza
        self.user = User.objects.create_user(username='formuser', password='pass')

    def test_valid_training_plan_form(self):
        # Przekazujemy poprawne dane do formularza
        form_data = {
            'name': 'Plan A',
            'intensity': 'high',
            'training_days': ['mon', 'wed'],
            'notes': 'Test note'
        }
        form = TrainingPlanForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_invalid_training_days(self):
        # Przekazujemy niepoprawny dzień treningowy
        form_data = {
            'name': 'Plan B',
            'intensity': 'low',
            'training_days': ['noday'],  # Błędny dzień tygodnia
        }
        form = TrainingPlanForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())

class TrainingPlanViewTestCase(TestCase):
    def setUp(self):
        # Tworzymy użytkownika i logujemy go
        self.user = User.objects.create_user(username='viewuser', password='pass')
        self.client.login(username='viewuser', password='pass')
        # Tworzymy ćwiczenie, które dodamy do planu
        self.exercise = Exercise.objects.create(name="Lunges")

    def test_create_training_plan_view(self):
        # Wysyłamy POST z danymi formularza do endpointa tworzącego plan
        response = self.client.post('/create_training_plan/', {
            'name': 'Leg Day',
            'intensity': 'medium',
            'training_days': ['fri'],
            'notes': 'Do it hard',
            'exercise_%d' % self.exercise.id: 'on',
            'repeats_%d' % self.exercise.id: 12
        })
        # Sprawdzamy, czy zostaliśmy przekierowani
        self.assertEqual(response.status_code, 302)  
        # Sprawdzamy, czy plan został zapisany w bazie
        self.assertEqual(TrainingPlan.objects.count(), 1)
        plan = TrainingPlan.objects.first()
        self.assertEqual(plan.name, "Leg Day")

    def test_delete_training_plan_view(self):
        # Tworzymy plan, który będziemy usuwać
        plan = TrainingPlan.objects.create(user=self.user, name="Delete Plan", training_days=['wed'])
        # Wysyłamy POST do endpointa usuwającego plan
        response = self.client.post(f'/delete-plan/{plan.pk}/')
        # Sprawdzamy, czy zostaliśmy przekierowani
        self.assertEqual(response.status_code, 302)
        # Sprawdzamy, czy plan został usunięty
        self.assertFalse(TrainingPlan.objects.filter(pk=plan.pk).exists())

from django.contrib.auth.models import Group

class TrainerPermissionTestCase(TestCase):
    def setUp(self):
        # Tworzymy użytkownika i grupę "trener", przypisujemy użytkownika
        self.trainer = User.objects.create_user(username='trainer', password='pass')
        trainer_group = Group.objects.create(name='trener')
        self.trainer.groups.add(trainer_group)
        # Tworzymy plan treningowy przypisany do trenera
        self.plan = TrainingPlan.objects.create(user=self.trainer, name="Trainer Plan", training_days=['thu'])

    def test_trainer_can_edit_trainer_notes(self):
        # Logujemy trenera
        self.client.login(username='trainer', password='pass')
        # Wysyłamy POST do endpointa edytującego notatki trenerskie
        response = self.client.post(f'/training/update_trainer_notes/{self.plan.pk}/', {
            'trainer_notes': 'Focus on form',
            'send_notification': 'on'
        })
        # Sprawdzamy przekierowanie
        self.assertEqual(response.status_code, 302)
        # Sprawdzamy, czy notatka została zapisana
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.trainer_notes, 'Focus on form')
