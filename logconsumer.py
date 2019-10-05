import sys
import signal
import asyncio
import logging
from os import environ
from asyncio_redis import Pool

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class LogListener:
	@classmethod
	async def create(cls, host='127.0.0.1', port=6379, poolsize=4, channels=None):
		self = LogListener()
		self.channels = channels if channels else []
		self.connection = await Pool.create(host=host, port=port, poolsize=poolsize)
		self.subscriber = await self.connection.start_subscribe()
		log.debug('subscribing to channels: %s' % self.channels)
		await self.subscriber.subscribe(self.channels)
		return self

	async def listen(self):
		while True:
			await asyncio.sleep(1)
			reply = await self.subscriber.next_published()
			yield reply

	async def stop(self):
		await self.connection.close()


async def main(channels, host, port):
	log.debug('starting redis LogListener')
	ll = await LogListener.create(host=host, port=port, channels=channels)
	log.debug('listening on channels: %s on host: %s:%s' % (channels, host, port))
	async for message in ll.listen():
		print(message.value, file=sys.stderr, flush=True)


def exit():
	raise SystemExit(1)


if __name__ == '__main__':
	channels = environ.get('LL_CHANNELS', 'logs')
	channels = channels.replace(' ', '').split(',')
	log.debug('channels: %s' % channels)
	host = environ.get('LL_HOST', '127.0.0.1')
	log.debug('host: %s' % host)
	port = int(environ.get('LL_PORT', '6379'))
	log.debug('port: %s' % port)
	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGINT, exit)
	try:
		loop.run_until_complete(main(channels, host, port))
	except SystemExit:
		log.info('exiting')
