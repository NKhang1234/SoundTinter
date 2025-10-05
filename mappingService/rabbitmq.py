from msgBroker_Interface import MessageBroker
from config import RBMQ_USER, RBMQ_PASSWORD, RBMQ_PORT, RBMQ_FWD_QUEUE, RBMQ_BWD_QUEUE
import asyncio
import aio_pika
import logging

logger = logging.getLogger(__name__)

class RabbitMQ(MessageBroker):
    _connection: aio_pika.RobustConnection = None

    def __init__(self, serverName: str):
        self.serverName = serverName
        self.receiveBuffer = asyncio.Queue()
        self.fwdChannel: aio_pika.abc.AbstractChannel = None
        self.bwdChannel: aio_pika.abc.AbstractChannel = None
        self.getTimeOut = None

    async def connect(self):
        if RabbitMQ._connection is None or RabbitMQ._connection.is_closed:
            while True:
                try:
                    RabbitMQ._connection = await aio_pika.connect_robust(
                        f"amqp://{RBMQ_USER}:{RBMQ_PASSWORD}@rabbitmq:{RBMQ_PORT}/"
                    )
                except Exception as e:
                    logger.warning(f"RabbitMQ has not started yet")
                    await asyncio.sleep(5)
                else:
                    logger.info(f"{self.serverName} connected to RabbitMQ successfully")
                    break
                
        # Create channels
        self.bwdChannel = await RabbitMQ._connection.channel() # Sending
        self.fwdChannel = await RabbitMQ._connection.channel() # Receiving

        # Declare queues
        await self.bwdChannel.declare_queue(RBMQ_BWD_QUEUE)
        queue = await self.fwdChannel.declare_queue(RBMQ_FWD_QUEUE)

        # Start consuming
        await queue.consume(self._callback)

    async def send(self, userID: str, filterName: str, status: str):
        await self.bwdChannel.default_exchange.publish(
            message = aio_pika.Message(
                body=b"",
                headers={
                    "userID": userID,
                    "filterName": filterName,
                    "status": status
                }
            ),
            routing_key=RBMQ_BWD_QUEUE
        )
        logger.info(f"{self.serverName} sent successfully mapping result: {filterName} - user {userID}")
    
    async def _callback(self, message: aio_pika.IncomingMessage):
        async with message.process():
            await self.receiveBuffer.put({
                "userID": message.headers.get("userID"),
                "songName": message.headers.get("songName")
            })
            logger.info(f"{self.serverName} received {message.headers.get('songName')} from user {message.headers.get('userID')}")

    async def get(self) -> dict:
        timeout = self.getTimeOut
        try:
            if timeout:
                return await asyncio.wait_for(self.receiveBuffer.get(), timeout=timeout)
            else:
                return await self.receiveBuffer.get()
        except asyncio.TimeoutError:
            return None

    @classmethod
    async def close(cls):
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
            cls._connection = None
