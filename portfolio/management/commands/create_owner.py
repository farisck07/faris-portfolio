from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from portfolio.models import Owner


class Command(BaseCommand):
    help = "Create and bind the portfolio's one owner. No default password is supplied."

    def add_arguments(self, parser):
        parser.add_argument("--username")
        parser.add_argument("--email")

    def handle(self, *args, **options):
        if Owner.objects.exists():
            raise CommandError("An owner is already configured. Use changepassword to reset that account's password.")
        username = options["username"] or input("Owner username: ").strip()
        email = options["email"] if options["email"] is not None else input("Email (optional): ").strip()
        user = get_user_model()(username=username, email=email, is_staff=True, is_superuser=True)
        try:
            user.full_clean(exclude=["password", "last_login", "date_joined"])
            password = getpass("Password: ")
            if password != getpass("Confirm password: "):
                raise CommandError("Passwords did not match. Please run create_owner again.")
            validate_password(password, user=user)
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from exc
        try:
            with transaction.atomic():
                if Owner.objects.exists():
                    raise CommandError("An owner is already configured.")
                user.set_password(password)
                user.save()
                Owner.objects.create(pk=1, user=user)
        except IntegrityError as exc:
            raise CommandError("The owner already exists or this username is taken.") from exc
        self.stdout.write(self.style.SUCCESS("Owner created. Sign in at /admin/ with the credentials you just chose."))
