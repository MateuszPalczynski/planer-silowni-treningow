from django.test import TestCase,Client
from django.urls import reverse
from django.utils.dateparse import parse_date
from website.models import TrainingPlan, Exercise, TrainingPlanCompletion
from django.contrib.auth.models import User,Group

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
    
    def test_create_training_plan_invalid_plan_id_returns_404(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('create_training_plan'), {'plan_id': 9999})  # nonexistent
        self.assertEqual(response.status_code, 404)

    def test_create_training_plan_unauthenticated_user_redirects_to_login(self):
        response = self.client.post(reverse('create_training_plan'), {'plan_id': self.expert_plan.id})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)


class HomeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.expert_creator = User.objects.create_user(username='trainer', password='password123')

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

    def test_home_view_authenticated_user(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn('form', response.context)
        self.assertIn('training_plans', response.context)
        self.assertIn('expert_plans', response.context)
        self.assertContains(response, "Expert Plan A")  # Make sure plan is visible
    
    def test_home_view_unauthenticated_user(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(response.context['training_plans'])  # not logged in, should be empty

    def test_user_login_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('home'))

    def test_user_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIn('Please enter a correct username and password. Note that both fields may be case-sensitive.', response.context['form'].non_field_errors())

    def test_register_valid_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpass123!',
            'password2': 'newpass123!'
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_invalid_data(self):
        response = self.client.post(reverse('register'), {
            'username': '',
            'password1': '123',
            'password2': '456',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertFormError(response.context['form'], 'username', 'This field is required.')

    
    def test_user_logout(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_home_view_shows_only_user_plans(self):
        other_plan = TrainingPlan.objects.create(user=self.expert_creator, name="Trainer Plan")
        TrainingPlan.objects.create(user=self.user, name="User Plan")

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('home'))

        plans = response.context['training_plans']
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0].user, self.user)

    def test_register_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            'username': 'anotheruser',
            'password1': 'abc12345',
            'password2': 'different123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertContains(response, "The two password fields didn’t match.")

    def test_delete_plan_logged_in_user(self):
        plan = TrainingPlan.objects.create(user=self.user, name="Plan to delete")
        self.client.login(username='testuser', password='password123')
        response = self.client.post(f'/delete-plan/{plan.id}/')
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(TrainingPlan.objects.filter(id=plan.id).exists())

class MarkTrainingPlanDoneTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user1', password='pass')
        self.other_user = User.objects.create_user(username='user2', password='pass')
        self.plan = TrainingPlan.objects.create(user=self.user, name="Plan A")
        self.url = reverse('mark_training_plan_done', args=[self.plan.id])

    def test_requires_login(self):
        response = self.client.post(self.url, {'done_date': '2024-06-01'})
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_forbidden_for_other_user(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(self.url, {'done_date': '2024-06-01'})
        self.assertEqual(response.status_code, 403)

    def test_invalid_date(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(self.url, {'done_date': 'invalid'})
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(TrainingPlanCompletion.objects.exists())

    def test_creates_completion_record(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(self.url, {'done_date': '2024-06-01'})
        self.assertRedirects(response, reverse('home'))
        completion = TrainingPlanCompletion.objects.get(training_plan=self.plan, user=self.user)
        self.assertEqual(completion.date_completed, parse_date('2024-06-01'))

    def test_updates_existing_completion_record(self):
        TrainingPlanCompletion.objects.create(training_plan=self.plan, user=self.user, date_completed='2024-05-01')
        self.client.login(username='user1', password='pass')
        response = self.client.post(self.url, {'done_date': '2024-06-05'})
        self.assertRedirects(response, reverse('home'))
        completion = TrainingPlanCompletion.objects.get(training_plan=self.plan, user=self.user)
        self.assertEqual(completion.date_completed, parse_date('2024-06-05'))

class UpdateTrainerNotesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.trainer = User.objects.create_user(username='trainer', password='pass')
        self.user = User.objects.create_user(username='user', password='pass')
        self.plan = TrainingPlan.objects.create(user=self.user, name="Plan A")
        self.url = reverse('update_trainer_notes', args=[self.plan.id])

        # Add trainer to 'trener' group
        group = Group.objects.create(name='trener')
        self.trainer.groups.add(group)

    def test_requires_login(self):
        response = self.client.post(self.url, {'trainer_notes': 'Note'})
        self.assertEqual(response.status_code, 302)

    def test_forbidden_for_non_trainer(self):
        self.client.login(username='user', password='pass')
        response = self.client.post(self.url, {'trainer_notes': 'Note'})
        self.assertEqual(response.status_code, 403)

    def test_allows_trainer_to_update_notes(self):
        self.client.login(username='trainer', password='pass')
        response = self.client.post(self.url, {'trainer_notes': 'Updated note'})
        self.assertRedirects(response, reverse('home'))
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.trainer_notes, 'Updated note')

class UpdateTrainingPlanTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user1', password='pass')
        self.other_user = User.objects.create_user(username='user2', password='pass')
        self.plan = TrainingPlan.objects.create(user=self.user, name="Plan A")
        self.url = reverse('update_training_plan', args=[self.plan.id])

    def test_requires_login(self):
        response = self.client.post(self.url, {'notes': 'note', 'send_notification': True})
        self.assertEqual(response.status_code, 302)

    def test_forbidden_for_other_user(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(self.url, {'notes': 'note'})
        self.assertEqual(response.status_code, 403)

    def test_updates_notes_and_flag(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(self.url, {'notes': 'Updated notes', 'send_notification': True})
        self.assertRedirects(response, reverse('home'))
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.notes, 'Updated notes')
        self.assertTrue(self.plan.send_notification)
