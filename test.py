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
    "uers": [],
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
            "restaurant": "Melange"
        },    
        {
            "id": "3", 
            "name": "Pasta", 
            "price": 799,
            "restaurant": "Melange"
         },
    ],
    "delivery": {}   #UUID:[DeliveryProvider, 'finished']
}


OrderRequestBody = tuple[str, datetime]
DeliveryProvider = Literal["uber", "uklon"]

def blocking_process(delay):
    time.sleep(delay)

@dataclass
class DeliveryOrder:
    order_name:str
    number:uuid.UUID |None = None


#class DeliveryProvider(enum.StrEnum):
#    UBER = "uber"
#    UKLON = "uklon"
# poc: save_order_to_database(deliver_provider=DeliveryProvider.UBER)
 

# SERVISES (APPLICATION/OPERATIONAL/USE CASE) TIER 

class DeliveryService(abc.ABC):
    def __init__(self, order: DeliveryOrder) -> None:
        self._order: DeliveryOrder = order

    @classmethod
    def _process_delivery(cls) -> None:
        print(f"DELIVERY PROCESSING...")

        while True:
            delivery_items = STORAGE["delivery"]

            if not delivery_items:
                time.sleep(1)
        else:
            orders_to_remove = set()
            for key, value in delivery_items.items():
                if value[1] == "finished":
                    print(f"\n\tOrder {key} is delivered by {value[0]}")
                    order_to_remove.add[key]
                    
            for order_id in orders_to_remove:
                del STORAGE["delivery"][order_id]
                print(f"\n\tOrder {order_id} is removed from storage")
                

    def _ship(self, delay: int):
        """all concrate .ship() methods should call this method"""
        def callback():
            blocking_process(delay)
            STORAGE["delivery"][self._order.number][1] = "finished"
            print(f"\nUPDATED STORAGE: {self._order.number} is finished")

        thread = threading.Thread(target=callback)
        thread.start()
    
    @abc.abstractmethod 
    def ship(self):
        """concrate delivery provider implementation."""
    

class Uklon(DeliveryService):
    def ship(self): 
        self._order.number = uuid.uuid4()
        STORAGE["delivery"][self._order.number] = ["uklon", "ongoing"]

        delay: int = random.randint(4, 8)
        print(f"\nShiping [{self._order}] with Uklon. Time to wait {delay}")
        self._ship(delay)
        
        
    


class Uber(DeliveryService):
    def ship(self):  
        self._order.number = uuid.uuid4()
        STORAGE["delivery"][self._order.number] = ["uber", "ongoing"]

        delay: int = random.randint(4, 8)
        print(f"\nShiping [{self._order}] with Uber. Time to wait {delay}")
        self._ship(delay)
        
         


class Scheduler:
    def __init__(self):
        self.orders: queue.Queue[OrderRequestBody] = queue.Queue()

    def add_order(self,order: OrderRequestBody):
        self.orders.put(order)
        print(f"ORDER {order[0]} IS SCHEDULER")

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
 

    def proces_orders(self):
        print("SCHEDULER PROCESSING...")

            # USER INPUT EXAMPLE
        while True:
            order = self.orders.get(True)
                
            time_to_wait = order[1] - datetime.now()
            if time_to_wait.total_seconds() > 0:
                self.orders.put(order)
                time.sleep(0.5)
            else:
                self.ship_order(order[0])
                #print(f"\n\t{order[0]} SENT TO SHIPING DEPARTAMENT")

# ENTRYPOINT
def main():
    scheduler = Scheduler()
    threading.Thread(target=scheduler.proces_orders, daemon=True).start()
    threading.Thread(target=DeliveryService._process_delivery, daemon=True).start()
    


    # USER INPUT EXAMPLE
    while True:
       if order_details := input("Enter order deteils: "):
           data = order_details.split(" ")
           order_name, delay = data[0], int(data[1])
           scheduler.add_order((order_name, datetime.now() + timedelta(seconds=delay)))




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("BYE")
        raise SystemExit(0) 
