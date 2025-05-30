from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail
from website.models import TrainingPlan  # Upewnij się, że to jest odpowiednia aplikacja

class Command(BaseCommand):
    help = 'Wysyła przypomnienia o treningach zaplanowanych na dziś'

    def handle(self, *args, **options):
        today_code = now().strftime('%a').lower()[:3]  # np. 'mon', 'tue'

        # Pobieramy wszystkie plany treningowe, które mają włączone powiadomienia
        plans = TrainingPlan.objects.filter(send_notification=True)

        count = 0  # Liczba wysłanych powiadomień
        for plan in plans:
            # Filtrowanie dni treningowych w Pythonie, zamiast w bazie danych
            if today_code in plan.training_days:
                user = plan.user
                if user.email:
                    # Wysyłamy powiadomienie
                    send_mail(
                        subject='Training Notification',
                        message=f'Cześć {user.username},\n\nDziś masz zaplanowany trening: \"{plan.name}\".\nNie zapomnij!\n\nMiłego dnia!',
                        from_email='no-reply@twojadomena.pl',
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    count += 1

        # Wyświetlamy wynik w terminalu
        self.stdout.write(self.style.SUCCESS(f'Wysłano {count} powiadomień.'))
