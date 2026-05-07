import utils
from redis_client import RedisClient


class MovieRepository:
    """Handles movie persistence in Redis.

    Movie titles are normalized and used to build Redis keys internally.
    """

    _TRENDING_SCORE_MOVIES_KEY = "trending_score:movies"

    def __init__(self, redis_client: RedisClient) -> None:
        self.redis = redis_client.redis

    def _get_normalized_title(self, title: str) -> str:
        """Normalizes the given movie title using `utils.normalize_str`.

        Args:
            title (str): the given movie title

        Returns:
            str: the normalized movie title
        """

        return utils.normalize_str(title)

    def _get_movie_key(self, title: str) -> str:
        """Builds the Redis key for a movie from its title.

        The title is normalized before it is used as part of the Redis key.
        For example: "The Matrix" becomes "movie:the_matrix".

        Args:
            title (str): the given movie title

        Returns:
            str: the movie key used by redis
        """

        return f"movie:{self._get_normalized_title(title)}"

    def _get_watchlist_key(self, movie_key: str) -> str:
        """Builds the Redis key for a movie watchlist from the given movie key.

        Args:
            movie_key (str): the given movie key

        Returns:
            str: the watchlist redis key
        """

        return f"{movie_key}:watchlist"

    def add_to_watchlist(self, title: str, username: str) -> None:
        """Adds the username to the movie watchlist in Redis.

        The movie title is used to build the movie Redis key.

        Args:
            title (str): the given movie title.
            username (str): the username of the logged in user.
        """

        movie_key = self._get_movie_key(title)
        self.redis.sadd(self._get_watchlist_key(movie_key), username)

    def exists(self, title: str) -> bool:
        """Checks if movie already exists in redis.

        The movie title is used to build the movie Redis key.

        Args:
            title (str): the given movie title

        Returns:
            bool: true if the movie already exists, false otherwise
        """

        movie_key = self._get_movie_key(title)
        return bool(self.redis.exists(movie_key))

    def add(self, title: str, director: str, release_year: int) -> None:
        """Adds a movie to redis.

        The movie title is used to build the movie Redis key and is also stored
        as movie data.

        Args:
            title (str): the given movie title
            director (str): the given movie director
            release_year (int): the given movie release year
        """

        movie_key = self._get_movie_key(title)
        self.redis.hset(
            movie_key,
            mapping={
                "title": title,
                "director": director,
                "release_year": release_year,
            },
        )

    def get(self, title: str) -> dict:
        """Gets the movie data from Redis

        The movie title is used to build the movie Redis key.

        Args:
            title (str): the given movie title

        Returns:
            dict: the movie data, if the movie doesnt exist returns an empty dict.
        """

        movie_key = self._get_movie_key(title)
        return self.redis.hgetall(movie_key)

    def get_watch_count(self, title: str) -> int:
        """Gets the number of users that have the current movie in their watchlist.

        The movie title is used to build the movie Redis key.

        Args:
            title (str): the given movie title

        Returns:
            int: the number of users
        """

        movie_key = self._get_movie_key(title)
        return self.redis.scard(self._get_watchlist_key(movie_key))

    def increment_trending_score(self, title: str) -> None:
        """Increments the trending score of the given movie by one.

        It saves the movie with the normalized title.

        Args:
            title (str): the given movie title.
        """

        self.redis.zincrby(
            self._TRENDING_SCORE_MOVIES_KEY, 1, self._get_normalized_title(title)
        )

    def get_top_trending(self, limit: int = 3) -> list[dict]:
        """Gets the top trending movies ordered by their trending score.

        Args:
            limit (int): the maximum number of movies to get.

        Returns:
            list[dict]: the top trending movies with their trending score.
        """

        trending_movies = self.redis.zrevrange(
            self._TRENDING_SCORE_MOVIES_KEY,
            0,
            limit - 1,
            withscores=True,
        )

        movies = []
        for normalized_title, score in trending_movies:
            movie = self.get(normalized_title)
            if movie:
                movie["trending_score"] = int(score)
                movies.append(movie)

        return movies

    def get_popularity_metrics(self) -> list[dict]:
        """Gets the unique user interest count for each movie.

        Returns:
            list[dict]: movie data with the number of interested users sorted descending.
        """

        movies = []
        for movie_key in self.redis.scan_iter("movie:*"):
            if movie_key.endswith(":watchlist"):
                continue

            movie = self.redis.hgetall(movie_key)
            if movie:
                watchlist_key = self._get_watchlist_key(movie_key)
                movie["interested_users"] = self.redis.scard(watchlist_key)
                movies.append(movie)

        return sorted(
            movies,
            key=lambda movie: movie["interested_users"],
            reverse=True,
        )


if __name__ == "__main__":
    pass
