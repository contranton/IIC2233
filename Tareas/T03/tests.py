import unittest

import library.databases as D
import library.general as G
import library.preproc as P
from library.getters import get_review_positivity
import library

class TestPreprocessing(unittest.TestCase):

    def test_clean_html(self):
        review = "<a>hola mundo</a> como <href=https://www.zombo.com/> esta"
        assert(P.clean_html(review) == "hola mundo como  esta")

    def test_is_bot(self):
        review = "My girlfriend and I loved loved loved this movie"
        assert(P.is_bot(review))


class TestQueries(unittest.TestCase):

    def setUp(self):
        self.movies = D.load_database(test=True)

        self.prevDB = library.DB
        library.DB = "MiniDatabase/"

        # Remove the two problematic movie
        self.movies = list(D.take_fully_defined_movies(self.movies))

    def tearDown(self):
        library.DB = self.prevDB

    def test_filter_by_date(self):
        filtered1 = list(D.filter_by_date(self.movies,
                                          2000,
                                          lower=True))
        filtered2 = list(D.filter_by_date(self.movies,
                                          2000,
                                          lower=False))
        assert(len(filtered1) == 8)
        assert(len(filtered2) == 8)

    def test_popular_movies(self):
        populars = list(D.popular_movies(self.movies,
                                         r_min=50,
                                         r_max=100,
                                         r_type="MC"))
        assert(len(populars) == 12)

    def test_best_comments(self):
        best = list(D.best_comments(self.movies, 3))
        assert(best[0].title == 'Ironman')
        assert(best[1].title == 'High School Musical')

    def test_take_movie_while(self):
        list_ = list(D.take_movie_while(self.movies,
                                        column="id",
                                        symbol="<",
                                        value="5"))
        assert(len(list_) == 4)

    def test_popular_genre(self):
        genres = G.popular_genre(self.movies, "RT")
        assert(genres == ["Comedia", "Fantasía", "Drama", "Suspenso"])

    def test_popular_actors(self):
        pops = G.popular_actors(self.movies, 3, 17)
        assert(pops == ["Ricardo Schilling",
                        "Jaime Castro",
                        "Fernando Pieressa"])

    def test_get_review_positivity(self):
        review = "arrogant witty willing conservative careless boastful"
        assert(get_review_positivity(review) == -1)

    def test_highest_paid_actors(self):
        best = G.highest_paid_actors(self.movies)
        assert(best[0][0] == "Sebastián Behrmann")

    def test_successful_actors(self):
        bests = list(G.successful_actors(self.movies))
        assert(bests[0][0] == "Enzo Tamburini")

