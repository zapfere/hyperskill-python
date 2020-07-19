from abc import ABCMeta
from typing import Dict, List

from django.views import View
from django.shortcuts import redirect, render

from .models import Ticket, QueueStats

number = "number"
change_oil = "change_oil"
inflate_tires = "inflate_tires"
diagnostic = "diagnostic"
menu = {
    change_oil: "Change oil",
    inflate_tires: "Inflate tires",
    diagnostic: "Get diagnostic test"
}
line_of_cars = {
    number: 0,
    change_oil: list(),
    inflate_tires: list(),
    diagnostic: list()
}
ticket_number = None


class WelcomeView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "tickets/welcome.html")


class MenuView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
                      "tickets/menu.html",
                      context={"items": menu.items()})


class TicketView(View, metaclass=ABCMeta):

    def _get_wait_time(self) -> int:
        raise NotImplementedError

    def _put_ticket_in_line(self, ticket: Ticket) -> None:
        raise NotImplementedError
    
    @staticmethod
    def _increment_number() -> int:
        current = line_of_cars[number]
        current += 1
        line_of_cars[number] = current
        return current

    def _create_ticket(self) -> Dict[str, int]:
        ticket = Ticket(self._increment_number(), self._get_wait_time())
        self._put_ticket_in_line(ticket)
        return {
            "ticket_number": ticket.ticket_number,
            "minutes_to_wait": ticket.minutes_to_wait
        }

    def get(self, request, *args, **kwargs):
        return render(request,
                      "tickets/ticket.html",
                      context=self._create_ticket())


class ChangeOilTicketView(TicketView):

    def _get_wait_time(self) -> int:
        return len(line_of_cars[change_oil]) * 2

    def _put_ticket_in_line(self, ticket: Ticket) -> None:
        line_of_cars[change_oil].append(ticket)


class InflateTiresTicketView(TicketView):

    def _get_wait_time(self) -> int:
        return len(line_of_cars[change_oil]) * 2 \
               + len(line_of_cars[inflate_tires]) * 5

    def _put_ticket_in_line(self, ticket: Ticket) -> None:
        line_of_cars[inflate_tires].append(ticket)


class DiagnosticTicketView(TicketView):

    def _get_wait_time(self) -> int:
        return len(line_of_cars[change_oil]) * 2 \
               + len(line_of_cars[inflate_tires]) * 5 \
               + len(line_of_cars[diagnostic]) * 30

    def _put_ticket_in_line(self, ticket: Ticket) -> None:
        line_of_cars[diagnostic].append(ticket)


class ProcessingView(View):

    @staticmethod
    def _get_line_length(line_name: str) -> int:
        return len(line_of_cars[line_name])

    @staticmethod
    def _get_queue_stats() -> Dict[str, List[QueueStats]]:
        queue_stats = [
            QueueStats(
                "Change oil queue",
                ProcessingView._get_line_length(change_oil)
            ),
            QueueStats(
                "Inflate tires queue",
                ProcessingView._get_line_length(inflate_tires)
            ),
            QueueStats(
                "Get diagnostic queue",
                ProcessingView._get_line_length(diagnostic)
            )
        ]
        return {"queues": queue_stats}

    def get(self, request, *args, **kwargs):
        return render(request,
                      "tickets/processing.html",
                      context=self._get_queue_stats())

    def post(self, request, *args, **kwargs):
        global ticket_number

        for line_name in (change_oil, inflate_tires, diagnostic):
            queue = line_of_cars[line_name]
            if len(queue) > 0:
                ticket_number = queue.pop(0).ticket_number
                break
        else:
            ticket_number = None

        return redirect("/processing")


class NextView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
                      "tickets/next.html",
                      context={"ticket_number": ticket_number})
