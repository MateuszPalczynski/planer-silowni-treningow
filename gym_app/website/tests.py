from django.test import TestCase
from django.urls import reverse
from website.models import TrainingPlan, Exercise
from django.contrib.auth.models import User

class TrainingPlanTestCase(TestCase):
    
    def setUp(self):
        # Tworzymy użytkownika, bo TrainingPlan wymaga usera
        self.user = User.objects.create_user(username='testuser', password='password123')

        self.expert_creator = User.objects.create_user(username='trainer', password='password123')

        # Tworzymy przykładowe ćwiczenia
        self.exercise1 = Exercise.objects.create(name='Pushups')
        self.exercise2 = Exercise.objects.create(name='Squats')

        self.expert_plan = TrainingPlan.objects.create(
            user=self.expert_creator,
            name="Expert Plan A",
            intensity="high",
            training_days=['mon', 'wed', 'fri'],
            is_expert=True  
        )
        self.expert_plan.exercises.set([self.exercise1, self.exercise2])
        
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
    
    def test_can_create_expert_plan(self):
        """Sprawdza, czy można poprawnie utworzyć plan z flagą is_expert=True."""
        # Akcja: Pobieramy plan ekspercki stworzony w setUp
        plan = TrainingPlan.objects.get(id=self.expert_plan.id)
        
        # Asercja: Sprawdzamy, czy flaga jest poprawnie ustawiona
        self.assertTrue(plan.is_expert)
        self.assertEqual(plan.name, "Expert Plan A")

    def test_import_expert_plan_successfully(self):
        """
        Testuje "szczęśliwą ścieżkę": zalogowany użytkownik poprawnie importuje plan eksperta.
        """
        # Przygotowanie: logujemy zwykłego użytkownika
        self.client.login(username='testuser', password='password123')

        # Akcja: Symulujemy wysłanie POST z ID planu eksperta do widoku
        response = self.client.post(reverse('create_training_plan'), {'plan_id': self.expert_plan.id})
        
        # Asercje:
        # 1. Sprawdzamy, czy zostaliśmy przekierowani (status 302) po sukcesie
        self.assertEqual(response.status_code, 302)
        
        # 2. Sprawdzamy, czy w bazie danych powstał NOWY plan dla naszego użytkownika
        self.assertTrue(TrainingPlan.objects.filter(user=self.user, name="Expert Plan A").exists())
        
        # 3. Pobieramy ten nowy plan i sprawdzamy jego szczegóły
        newly_created_plan = TrainingPlan.objects.get(user=self.user)
        
        self.assertEqual(newly_created_plan.name, self.expert_plan.name) # Nazwa powinna być taka sama
        self.assertEqual(newly_created_plan.intensity, self.expert_plan.intensity) # Intensywność też
        self.assertFalse(newly_created_plan.is_expert) # WAŻNE: Skopiowany plan NIE jest już planem eksperta
        
        # 4. Sprawdzamy, czy ćwiczenia (relacja ManyToMany) zostały poprawnie skopiowane
        self.assertEqual(list(newly_created_plan.exercises.all()), list(self.expert_plan.exercises.all()))

        # 5. Upewniamy się, że oryginalny plan eksperta wciąż istnieje i jest nienaruszony
        self.assertTrue(TrainingPlan.objects.filter(id=self.expert_plan.id, is_expert=True).exists())



    def test_import_non_expert_plan_returns_404(self):
        """
        Testuje próbę importu planu, który nie jest oznaczony jako ekspercki.
        """
        # Przygotowanie: Tworzymy zwykły plan, nie-ekspercki
        non_expert_plan = TrainingPlan.objects.create(
            user=self.expert_creator,
            name="Zwykły plan",
            is_expert=False
        )
        self.client.login(username='testuser', password='password123')
        
        # Akcja: Próbujemy go zaimportować
        response = self.client.post(reverse('create_training_plan'), {'plan_id': non_expert_plan.id})
        
        # Asercja: Nasz widok filtruje po `is_expert=True`, więc nie znajdzie tego planu -> 404
        self.assertEqual(response.status_code, 404)

        
