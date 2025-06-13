from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete
from .models import ActivityLog, TrainingPlan, User


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Loguje pomyślne zalogowanie użytkownika."""
    ActivityLog.objects.create(user=user, action="Użytkownik zalogował się.")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Loguje wylogowanie użytkownika."""
    ActivityLog.objects.create(user=user, action="Użytkownik wylogował się.")


@receiver(post_save, sender=User)
def log_user_register(sender, instance, created, **kwargs):
    """Loguje rejestrację nowego użytkownika."""
    if created:
        ActivityLog.objects.create(user=instance, action="Użytkownik zarejestrował się.")


@receiver(post_save, sender=TrainingPlan)
def log_training_plan_save(sender, instance, created, **kwargs):
    """Loguje stworzenie lub edycję planu treningowego."""
    if created:
        action_text = f"Stworzył(a) nowy plan treningowy: '{instance.name}'."
    else:
        # Można by rozbudować o logowanie szczegółów edycji, ale na razie uprośćmy
        action_text = f"Zaktualizował(a) plan treningowy: '{instance.name}'."

    ActivityLog.objects.create(user=instance.user, action=action_text)


@receiver(post_delete, sender=TrainingPlan)
def log_training_plan_delete(sender, instance, **kwargs):
    """Loguje usunięcie planu treningowego."""
    ActivityLog.objects.create(user=instance.user, action=f"Usunął(ęła) plan treningowy: '{instance.name}'.")
