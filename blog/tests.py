from django.test import TestCase

from .models import Article


# тестирование практически ничего не тестирует

class ArticleMethodTests(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.articles = []
        cls.articles.append(Article(pub_date='2018-02-13 18:17:16'))
        cls.articles.append(Article(pub_date='2018-02-13 18:18:13'))
        cls.articles.append(Article(pub_date='2018-02-13 18:20:26'))

        # цикл не нужен
        # Article.objects.bulk_create(cls.articles)
        for article in cls.articles:
            article.save()

    def test_get_next_id(self):

        self.assertEqual(self.articles[0].get_next_id(), 2)
        self.assertEqual(self.articles[1].get_next_id(), 3)
        self.assertEqual(self.articles[2].get_next_id(), False)

    def test_get_previous_id(self):

        self.assertEqual(self.articles[0].get_previous_id(), False)
        self.assertEqual(self.articles[1].get_previous_id(), 1)
        self.assertEqual(self.articles[2].get_previous_id(), 2)
