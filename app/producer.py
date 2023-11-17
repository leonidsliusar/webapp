from functools import wraps
from types import NoneType
from typing import Coroutine, Callable
import pika
from app.core.models import PropsModel


class ProducerBotTask:

    def __init__(self):
        self.connection = ...

    @property
    def connection(self) -> pika.BlockingConnection:
        return self._connection

    @connection.setter
    def connection(self, val: NoneType = None):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='directBot', exchange_type='direct')
        self.channel.queue_declare(queue='botTaskUpd')
        self.channel.queue_declare(queue='botTaskAdd')
        self.channel.queue_bind(queue='botTaskUpd', exchange='directBot', routing_key='upd')
        self.channel.queue_bind(queue='botTaskAdd', exchange='directBot', routing_key='add')

    @staticmethod
    def connect(coro: Callable):

        @wraps(coro)
        async def wrapper(self, props_obj: PropsModel):
            if self.connection.is_closed:
                self.connection = ...
            await coro(self, props_obj)
            self.connection.close()

        return wrapper

    @connect
    async def produce_new_object(self, props_obj: PropsModel) -> None:
        props_id = props_obj.id
        self.channel.basic_publish(exchange='directBot', routing_key='add', body=props_id.encode())

    @connect
    async def produce_upd_object(self, props_obj: PropsModel) -> None:
        props_id = props_obj.id
        self.channel.basic_publish(exchange='directBot', routing_key='upd', body=props_id.encode())


task_manager = ProducerBotTask()
