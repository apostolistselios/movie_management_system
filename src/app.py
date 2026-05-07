import utils
from movies import MovieRepository
from redis_client import RedisClient
from users import UserRepository


def insert_movie(movie_repository: MovieRepository, username: str) -> None:
    """Prompts the user to insert the details of a movie and the saves it to redis.

    If the movie doesnt already exist saves it to redis.
    If it exist does nothing, just informs the user.

    Either way it inserts the user to the movies watchlist.

    Args:
        movie_repository (MovieRepository): the movie repository instance
        username (str): the username of the logged in user
    """

    print("\n--- Inserting a movie ---")

    title = utils.get_non_empty("Enter the movie title: ")
    director = utils.get_non_empty("Enter the movie director: ")

    try:
        release_year = int(input("Enter the movie release year: "))
    except ValueError:
        print("\n--- ERROR: Invalid format for release year. Must be a number. ---")
        return

    if not movie_repository.exists(title):
        print(f"--- Inserting the movie: {title} ---")
        movie_repository.add(title, director, release_year)
    else:
        print(f"--- Movie: {title} already exists ---")

    movie_repository.add_to_watchlist(title, username)


def query_movie(
    movie_repository: MovieRepository, user_repository: UserRepository, username: str
) -> None:
    """Prompts the user to enter a movie titles and displays the data of the given movie.

    It also adds the user to the movies watchlist, increases the movies trending score,
    and add the movie to the users search history.

    Args:
        movie_repository (MovieRepository): the movie repository instance
        user_repository (UserRepository): the user repository instance
        username (str): the username of the logged in user
    """

    title = utils.get_non_empty("Please enter a movie title: ")
    movie = movie_repository.get(title)
    if not movie:
        print(f"\n--- Movie: {title} was not found ---")
        return

    no_users_watched = movie_repository.get_watch_count(title)

    print("\n--- Movie Information ---")
    print(f"Title: {movie['title']}")
    print(f"Director: {movie['director']}")
    print(f"Release Year: {movie['release_year']}")
    print(f"Number of users that watched the movie: {no_users_watched}")

    movie_repository.add_to_watchlist(title, username)
    movie_repository.increment_trending_score(title)
    user_repository.add_to_history(username, title)


def print_statistics(
    movie_repository: MovieRepository, user_repository: UserRepository, username: str
) -> None:
    """Displays platform and user statistics.

    Args:
        movie_repository (MovieRepository): the movie repository instance
        user_repository (UserRepository): the user repository instance
        username (str): the username of the logged in user
    """

    top_trending_movies = movie_repository.get_top_trending()
    user_history = user_repository.get_history(username)
    popularity_metrics = movie_repository.get_popularity_metrics()

    print("\n--- Statistics ---")
    print("\nTop 3 trending movies:")
    if not top_trending_movies:
        print("No trending movies yet.")
    else:
        for index, movie in enumerate(top_trending_movies, start=1):
            print(
                f"{index}. {movie['title']} (Trending Score: {movie['trending_score']})"
            )

    print("\nYour last 5 searched movies:")
    if not user_history:
        print("No search history yet.")
    else:
        for index, title in enumerate(user_history, start=1):
            print(f"{index}. {title}")

    print("\nPopularity metrics:")
    if not popularity_metrics:
        print("No movies found.")
    else:
        for movie in popularity_metrics:
            print(f"{movie['title']}: {movie['interested_users']} interested users")


def main() -> None:
    redis_client = RedisClient()
    movie_repository = MovieRepository(redis_client)
    user_repository = UserRepository(redis_client)

    username = input("Enter your username: ")

    while True:
        print("\n--- Μένου Redis Movies ---")
        print("(I)nsert Movie | (Q)uery | (S)tatistics | e(X)it")
        choice = input("Option: ").upper()

        if choice == "I":
            insert_movie(movie_repository, username)

        elif choice == "Q":
            query_movie(movie_repository, user_repository, username)

        elif choice == "S":
            print_statistics(movie_repository, user_repository, username)

        elif choice == "X":
            print("Exiting...")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
