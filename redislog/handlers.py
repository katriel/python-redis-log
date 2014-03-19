import logging
import redis
import simplejson as json

class RedisFormatter(logging.Formatter):
    def format(self, record):
        """
        JSON-encode a record for serializing through redis.

        Convert date to iso format, and stringify any exceptions.
        """
        data = record._raw.copy()

        # serialize the datetime date as utc string
        data['time'] = data['time'].isoformat()

        # stringify exception data
        if data.get('traceback'):
            data['traceback'] = self.formatException(data['traceback'])

        return json.dumps(data)

class RedisPubSubHandler(logging.Handler):
    """
    Publish messages to redis channel.

    As a convenience, the classmethod to() can be used as a
    constructor, just as in Andrei Savu's mongodb-log handler.
    """

    @classmethod
    def to(cklass, channel, host='localhost', port=6379, level=logging.NOTSET):
        return cklass(channel, redis.Redis(host=host, port=port), level=level)

    def __init__(self, channel, redis_client, level=logging.NOTSET):
        """
        Create a new logger for the given channel and redis_client.
        """
        logging.Handler.__init__(self, level)
        self.channel = channel
        self.redis_client = redis_client
        self.formatter = RedisFormatter()

    def emit(self, record):
        """
        Publish record to redis logging channel
        """
        self.redis_client.publish(self.channel, self.format(record))


class RedisHandler(logging.Handler):
    """
    Save messages to redis

    As a convenience, the classmethod to() can be used as a
    constructor, just as in Andrei Savu's mongodb-log handler.
    """

    @classmethod
    def to(cklass, log_key, host='localhost', port=6379, level=logging.NOTSET, expire=24):
        return cklass(log_key, redis.Redis(host=host, port=port), level=level, expire=24)

    def __init__(self, log_key, redis_client, level=logging.NOTSET, expire=24):
        """
        Create a new logger for the given channel and redis_client.
        """
        logging.Handler.__init__(self, level)
        self.log_key = log_key
        self.expire = expire
        self.redis_client = redis_client
        self.formatter = RedisFormatter()

    def emit(self, record):
        """
        Publish record to redis logging channel
        """
        self.redis_client.rpush(self.log_key, self.format(record))
        self.redis_client.expire(self.log_key, self.expire*60*60)


