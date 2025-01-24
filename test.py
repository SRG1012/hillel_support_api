from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import time
import queue
import enum
from typing import Literal
import random
import uuid
import abc


STORAGE = {
    "users": [],
    "dishes": [
        {
            "id": "1",
            "name": "Pizza",
            "price": 1099,
            "restaurant": "Bueno",
        },
        {
            "id": "2",
            "name": "Burger",
            "price": 599,
            "restaurant": "Melange",
        },
        {
            "id": "3",
            "name": "Pasta",
            "price": 799,
            "restaurant": "Melange",
        },
    ],
    "delivery": {},  # UUID: [DeliveryProvider, status, updated_at]
}

OrderRequestBody = tuple[str, datetime]
DeliveryProvider = Literal["uber", "uklon"]


def blocking_process(delay):
    time.sleep(delay)


@dataclass
class DeliveryOrder:
    order_name: str
    number: uuid.UUID | None = None


class DeliveryService(abc.ABC):
    def __init__(self, order: DeliveryOrder) -> None:
        self._order: DeliveryOrder = order

    @classmethod
    def _process_delivery(cls) -> None:
        print("DELIVERY PROCESSING...")

        while True:
            delivery_items = STORAGE["delivery"]

            if not delivery_items:
                time.sleep(1)
                continue

            orders_to_archive = set()
            for key, value in delivery_items.items():
                if value[1] == "finished":
                    print(f"\n\tOrder {key} is delivered by {value[0]}")
                    value[1] = "archived"
                    value[2] = datetime.now()

    @staticmethod
    def _remove_archived():
        """Worker to clean up archived orders older than 1 minute."""
        while True:
            now = datetime.now()
            to_delete = [
                key
                for key, value in STORAGE["delivery"].items()
                if value[1] == "archived" and (now - value[2]).total_seconds() > 60
            ]
            for key in to_delete:
                print(f"Removing archived order {key}")
                del STORAGE["delivery"][key]
            time.sleep(5)

    def _ship(self, delay: int):
        """All concrete .ship() methods should call this method."""
        def callback():
            blocking_process(delay)
            STORAGE["delivery"][self._order.number][1] = "finished"
            STORAGE["delivery"][self._order.number][2] = datetime.now()
            print(f"\nUPDATED STORAGE: {self._order.number} is finished")

        thread = threading.Thread(target=callback)
        thread.start()

    @abc.abstractmethod
    def ship(self):
        """Concrete delivery provider implementation."""


class Uklon(DeliveryService):
    def ship(self):
        self._order.number = uuid.uuid4()
        STORAGE["delivery"][self._order.number] = ["uklon", "ongoing", datetime.now()]

        delay: int = random.randint(4, 8)
        print(f"\nShipping [{self._order}] with Uklon. Time to wait {delay}")
        self._ship(delay)


class Uber(DeliveryService):
    def ship(self):
        self._order.number = uuid.uuid4()
        STORAGE["delivery"][self._order.number] = ["uber", "ongoing", datetime.now()]

        delay: int = random.randint(4, 8)
        print(f"\nShipping [{self._order}] with Uber. Time to wait {delay}")
        self._ship(delay)


class Scheduler:
    def __init__(self):
        self.orders: queue.Queue[OrderRequestBody] = queue.Queue()

    def add_order(self, order: OrderRequestBody):
        self.orders.put(order)
        print(f"ORDER {order[0]} IS SCHEDULED")

    def _delivery_service_dispatcher(self) -> type[DeliveryService]:
        random_provider: DeliveryProvider = random.choice(["uklon", "uber"])

        match random_provider:
            case "uklon":
                return Uklon
            case "uber":
                return Uber
            case _:
                raise Exception("panic...")

    def ship_order(self, order_name: str) -> None:
        service_class: type[DeliveryService] = self._delivery_service_dispatcher()
        service_class(order=DeliveryOrder(order_name=order_name)).ship()

    def process_orders(self):
        print("SCHEDULER PROCESSING...")

        while True:
            order = self.orders.get(True)

            time_to_wait = order[1] - datetime.now()
            if time_to_wait.total_seconds() > 0:
                self.orders.put(order)
                time.sleep(0.5)
            else:
                self.ship_order(order[0])


# ENTRYPOINT
def main():
    scheduler = Scheduler()
    threading.Thread(target=scheduler.process_orders, daemon=True).start()
    threading.Thread(target=DeliveryService._process_delivery, daemon=True).start()
    threading.Thread(target=DeliveryService._remove_archived, daemon=True).start()

    while True:
        if order_details := input("Enter order details (name delay): "):
            try:
                data = order_details.split(" ")
                order_name, delay = data[0], int(data[1])
                scheduler.add_order((order_name, datetime.now() + timedelta(seconds=delay)))
            except (ValueError, IndexError):
                print("Invalid input. Please enter the order details in the format: <name> <delay>")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("BYE")
        raise SystemExit(0)
