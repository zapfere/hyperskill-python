from django.db import models

# Create your models here.


class Ticket:
    def __init__(self, ticket_number, minutes_to_wait):
        self.ticket_number = ticket_number
        self.minutes_to_wait = minutes_to_wait


class QueueStats:
    def __init__(self, name, count):
        self.name = name
        self.count = count
