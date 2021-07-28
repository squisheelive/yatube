from django.test import TestCase
from posts.models import Group, Post, User


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Test-user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='В лесу родилась елочка, в лесу она росла.',
            author=cls.author,
            group=cls.group
        )

    def test_post_str(self):
        post = ModelsTest.post
        post_str = str(post)
        text_cut = post.text[:15]
        self.assertEqual(post_str, text_cut)

    def test_group_str(self):
        group = ModelsTest.group
        group_str = str(group)
        self.assertEqual(group_str, 'Тестовый заголовок')
