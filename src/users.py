from redis_client import RedisClient


class UserRepository:
    """Handles user persistence in Redis."""

    def __init__(self, redis_client: RedisClient) -> None:
        self.redis = redis_client.redis

    def _get_history_key(self, username: str) -> str:
        """Builds the Redis key for a users search history.

        Args:
            username (str): the username of the logged in user.

        Returns:
            str: the redis key of the search history.
        """

        return f"user:{username}:history"

    def add_to_history(self, username: str, title: str) -> None:
        """Adds the given movie title to the users search history and trims list to 5.

        Args:
            username (str): the username of the logged in user.
            title (str): the given movie title
        """

        history_key = self._get_history_key(username)
        self.redis.lpush(history_key, title)
        self.redis.ltrim(history_key, 0, 4)

    def get_history(self, username: str) -> list[str]:
        """Gets the last movies searched by the given user, newest first.

        Args:
            username (str): the username of the logged in user.

        Returns:
            list[str]: the user's latest searched movie titles, newest first.
        """

        return self.redis.lrange(self._get_history_key(username), 0, -1)


if __name__ == "__main__":
    pass
