import unittest
import library as L


class TestPreprocessing(unittest.TestCase):

    def setup(self):
        pass

    def test_clean_html(self):
        pass

    def test_is_bot(self):
        pass


class TestQueries(unittest.TestCase):

    def setUp(self):
        self.movies = L.load_database(test=True)

        # Remove the two problematic movie
        self.movies = list(L.take_fully_defined_movies(self.movies))

    def test_filter_by_date(self):
        filtered1 = list(L.filter_by_date(self.movies,
                                          2000,
                                          lower=True))
        filtered2 = list(L.filter_by_date(self.movies,
                                          2000,
                                          lower=False))
        assert(len(filtered1) == 8)
        assert(len(filtered2) == 8)

    def test_popular_movies(self):
        populars = list(L.popular_movies(self.movies,
                                         r_min=50,
                                         r_max=100,
                                         r_type="MC"))
        assert(len(populars) == 12)

    def test_best_comments(self):
        best = list(L.best_comments(self.movies, 3))
        assert(best[0].title == '"Saw"')
        assert(best[1].title == '"High School Musical"')

    def test_take_movie_while(self):
        list_ = list(L.take_movie_while(self.movies,
                                        column="id",
                                        symbol="<",
                                        value="5"))
        assert(len(list_) == 4)

    def test_popular_genre(self):
        genres = L.popular_genre(self.movies, "All")
        assert(genres == ['Acción', 'Ciencia ficción', 'Comedia', 'Fantasía'])

    def test_popular_actors(self):
        pops = L.popular_actors(self.movies, 3, 17)
        assert(pops == ["Ricardo Schilling",
                        "Jaime Castro",
                        "Fernando Pieressa"])

    def test_get_review_positivity(self):
        review = "arrogant witty willing conservative careless boastful"
        assert(L.get_review_positivity(review) == -1)

    def test_highest_paid_actors(self):
        best = L.highest_paid_actors(self.movies, 3)
        assert(best == ["ACTOR 1",
                        "ACTOR 2",
                        "ACTOR 3"])

    def test_successful_actors(self):
        pass

