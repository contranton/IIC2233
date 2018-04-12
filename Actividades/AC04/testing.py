import unittest
import library as lib


class testFunctions(unittest.TestCase):
    def setUp(self):
        self.trending_date = "18.12.03"
        self.publish_date = "18.4.02"
        self.likes = "1533"
        self.dislikes = "7443"

    def test_tiempo_trending(self):
        self.assertEqual(lib.tiempo_trending(self.publish_date, self.trending_date), 36)

    def test_like_dislike_ratio(self):
        self.assertAlmostEquals(lib.like_dislike_ratio(self.likes, self.dislikes), 0.205965336558)


class testExceptions(unittest.TestCase):
    def setUp(self):
        self.wrong_publish_date = "18 - 12 - 03"
        self.trending_date = "18.4.02"

    def test_wrong_date(self):
        with self.assertRaises(ValueError):
            lib.tiempo_trending(self.wrong_publish_date, self.trending_date)

    def test_wrong_likes(self):
        with self.assertRaises(ValueError):
            lib.like_dislike_ratio("n13J#", "1353")

if __name__ == '__main__':
    unittest.main()
