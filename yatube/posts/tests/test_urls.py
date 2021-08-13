from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Comment, Follow, Group, Post, User


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Test-user')
        cls.user = User.objects.create(username='Test-user-2')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='В лесу родилась елочка, в лесу она росла.',
            author=cls.author,
            group=cls.group
        )
        cls.pk = cls.post.pk
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )
        cls.templates_url_names = {
            'index.html': '/',
            'group.html': f'/group/{URLTests.group.slug}/',
            'new.html': '/new/',
            'post.html': f'/{URLTests.author.username}/{URLTests.pk}/',
            'profile.html': f'/{URLTests.author.username}/',
            'follow.html': '/follow/',
            'comments.html': (
                f'/{URLTests.author.username}/{URLTests.pk}/comment/')
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = URLTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_homepage_exists(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug_exists(self):
        response = self.guest_client.get(f'/group/{URLTests.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_new_exists_authorized(self):
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_redirect_anonymous(self):
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)

    def test_user_page_exists(self):
        response = self.guest_client.get(f'/{URLTests.author.username}/')
        self.assertEqual(response.status_code, 200)

    def test_post_page_exists(self):
        response = self.guest_client.get(
            f'/{URLTests.author.username}/{URLTests.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_post_page_edit_redirect_anonymous(self):
        response = self.guest_client.get(
            f'/{URLTests.author.username}/{URLTests.pk}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_post_page_edit_redirect_non_author(self):
        new_user = User.objects.create(username='new_user')
        non_author = Client()
        non_author.force_login(new_user)
        response = non_author.get(
            f'/{URLTests.author.username}/{URLTests.pk}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_post_page_edit_exists_post_author(self):
        self.authorized_client.force_login(URLTests.author)
        response = self.authorized_client.get(
            f'/{URLTests.author.username}/{URLTests.pk}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_page_edit_use_correct_template(self):
        self.authorized_client.force_login(URLTests.author)
        response = self.authorized_client.get(
            f'/{URLTests.author.username}/{URLTests.pk}/edit/')
        self.assertTemplateUsed(response, 'new.html')

    def test_post_page_edit_non_author_redirect_post_page(self):
        new_user = User.objects.create(username='new_user')
        non_author = Client()
        non_author.force_login(new_user)
        response = non_author.get(
            f'/{URLTests.author.username}/{URLTests.pk}/edit/',
            follow=True)
        self.assertRedirects(
            response, f'/{URLTests.author.username}/{URLTests.pk}/')

    def test_urls_uses_correct_template(self):
        for template, adress in URLTests.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_wrong_url_404(self):
        response = self.guest_client.get('/page/which/not/exist')
        self.assertEqual(response.status_code, 404)

    def test_comment_page_exist_authorized(self):
        response = self.authorized_client.get(
            f'/{URLTests.author.username}/{URLTests.pk}/comment/')
        self.assertEqual(response.status_code, 200)

    def test_comment_page_redirect_anonymous(self):
        response = self.guest_client.get(
            f'/{URLTests.author.username}/{URLTests.pk}/comment/')
        self.assertEqual(response.status_code, 302)

    def test_follow_page_exists_authorized(self):
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, 200)

    def test_follow_page_redirect_anonymous(self):
        response = self.guest_client.get('/follow/')
        self.assertEqual(response.status_code, 302)
