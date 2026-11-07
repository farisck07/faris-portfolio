from django.core.management.base import BaseCommand
from django.db import transaction
from portfolio.models import Profile, Skill, Passion


class Command(BaseCommand):
    help = "Add starter profile, skills and passions once. Does not fabricate projects or credentials."

    @transaction.atomic
    def handle(self, *args, **options):
        _, created = Profile.objects.get_or_create(pk=1)
        if not created:
            self.stdout.write("Profile already exists; existing content left unchanged.")
            return
        Skill.objects.bulk_create([
            Skill(title="Python", category="backend", published=True, position=1),
            Skill(title="Django", category="backend", published=True, position=2),
            Skill(title="HTML & CSS", category="frontend", published=True, position=3),
        ])
        Passion.objects.bulk_create([
            Passion(title="Building for the web", symbol="</>", description="Turning ideas into useful experiences with Python, Django and thoughtful interfaces.", published=True, position=1),
            Passion(title="The details that matter", symbol="✦", description="Exploring how clear design and carefully written code make a product feel better to use.", published=True, position=2),
            Passion(title="Always learning", symbol="↗", description="Learning through projects, asking better questions and improving one step at a time.", published=True, position=3),
        ])
        self.stdout.write(self.style.SUCCESS("Starter content added. Review and personalise it in your admin."))
