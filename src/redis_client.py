import sys

from redis import Redis


class RedisClient:
    """Singleton that manages the Redis connection."""

    _instance: "RedisClient | None" = None

    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.redis = self.connect()
        self._initialized = True

    def connect(self) -> Redis:
        """Connect to Redis. The application exits if the connection fails.

        Returns:
            Redis: The created Redis client instance.
        """

        try:
            client = Redis(host="localhost", port=6379, decode_responses=True)
            client.ping()
            print("Connected to Redis")

            return client
        except Exception as error:
            print(f"Redis is not available: {error}")
            sys.exit(1)
