### generacja nowych użytkowników FAKER
from faker import Faker
from myapp.models import CustomUser
from django.core.management.base import BaseCommand
from django.utils import timezone
import random


fake = Faker("pl_PL")

def generate_pesel(date_of_birth):
    year = date_of_birth.year
    month = date_of_birth.month
    day = date_of_birth.day

    if 2000 <= year <= 2099:
        month += 20
    elif 1800 <= year <= 1899:
        month += 80
    elif 2100 <= year <= 2199:
        month += 40
    elif 2200 <= year <= 2299:
        month += 60

    date_part = f"{str(year)[-2:]}{month:02d}{day:02d}"
    serial = f"{random.randint(0, 9999):04d}"
    partial = date_part + serial

    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = sum(int(partial[i]) * weights[i] for i in range(10))
    last_digit = (10 - (checksum % 10)) % 10

    return partial + str(last_digit)

class Command(BaseCommand):
    help = "Generate fake users (doctors or patients)"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10)
        parser.add_argument("--role", type=str, choices=["doctor", "patient"], default="patient")

    def handle(self, *args, **options):
        count = options["count"]
        role = options["role"]

        for _ in range(count):
            dob = fake.date_of_birth(minimum_age=25, maximum_age=65)
            pesel = generate_pesel(dob)
            email = fake.unique.email()
            username = fake.name()

            user = CustomUser.objects.create_user(
                email=email,
                username=username,
                password="test1234",
                role=role,
                date_of_birth=dob,
                pesel=pesel
            )
            self.stdout.write(self.style.SUCCESS(f"Created {role}: {username} ({email})"))