import shutil
import tempfile
from datetime import datetime as dt

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post, User
from yatube.settings import PAGE_SIZE


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Test-user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Test-user-2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_page_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': ViewsTest.group.slug})
            ),
            'new.html': reverse('new_post'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.guest_client.get(reverse('index'))
        last_post = response.context['page'].object_list[0]
        today = dt.today().date()
        self.assertEqual(last_post.text, 'Тестовый текст')
        self.assertEqual(last_post.pub_date.date(), today)
        self.assertEqual(last_post.author, ViewsTest.author)
        self.assertEqual(last_post.group, ViewsTest.group)
        self.assertEqual(last_post.image, f'posts/{ViewsTest.uploaded.name}')

    def test_group_page_show_correct_context(self):
        response = self.guest_client.get(
            reverse('group_posts', kwargs={'slug': ViewsTest.group.slug}))
        last_post = response.context['page'].object_list[0]
        today = dt.today().date()
        self.assertEqual(last_post.text, 'Тестовый текст')
        self.assertEqual(last_post.pub_date.date(), today)
        self.assertEqual(last_post.author, ViewsTest.author)
        self.assertEqual(last_post.group, ViewsTest.group)
        self.assertEqual(last_post.image, f'posts/{ViewsTest.uploaded.name}')

    def test_profile_page_show_correct_context(self):
        response = self.guest_client.get(
            reverse('profile', kwargs={'username': ViewsTest.author.username}))
        last_post = response.context['page'].object_list[0]
        today = dt.today().date()
        self.assertEqual(last_post.text, 'Тестовый текст')
        self.assertEqual(last_post.pub_date.date(), today)
        self.assertEqual(last_post.author, ViewsTest.author)
        self.assertEqual(last_post.group, ViewsTest.group)
        self.assertEqual(last_post.image, f'posts/{ViewsTest.uploaded.name}')

    def test_post_page_show_correct_context(self):
        pk = ViewsTest.author.posts.first().pk
        today = dt.today().date()
        response = self.guest_client.get(
            reverse('post', kwargs={
                'username': ViewsTest.author.username,
                'post_id': pk
            }))
        post = response.context['post']
        author = response.context['author']
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(author, ViewsTest.author)
        self.assertEqual(post.group, ViewsTest.group)
        self.assertEqual(post.pub_date.date(), today)
        self.assertEqual(post.image, f'posts/{ViewsTest.uploaded.name}')

    def test_new_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        self.authorized_client.force_login(ViewsTest.author)
        pk = ViewsTest.author.posts.first().pk
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': ViewsTest.author.username,
                'post_id': pk
            }))
        form_fields = {
            'text': forms.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_post_display_home_page(self):
        new_post = Post.objects.create(
            text='Новый тестовый текст',
            author=ViewsTest.author,
            group=ViewsTest.group
        )
        response = self.guest_client.get(reverse('index'))
        last_post = response.context['page'].object_list[0]
        self.assertEqual(last_post, new_post)

    def test_new_post_display_group_page(self):
        new_post = Post.objects.create(
            text='Новый тестовый текст',
            author=ViewsTest.author,
            group=ViewsTest.group
        )
        response = self.guest_client.get(reverse(
            'group_posts', kwargs={'slug': ViewsTest.group.slug}))
        last_post = response.context['page'].object_list[0]
        self.assertEqual(last_post, new_post)

    def test_new_post_dont_display_another_group_page(self):
        new_group = Group.objects.create(
            title='Новая тестовая группа',
            slug='new-test-slug',
            description='Новое тестовое описание'
        )
        new_post = Post.objects.create(
            text='Новый тестовый текст',
            author=ViewsTest.author,
            group=new_group
        )
        response = self.guest_client.get(reverse(
            'group_posts', kwargs={'slug': ViewsTest.group.slug}))
        last_post = response.context['page'].object_list[0]
        self.assertNotEqual(last_post, new_post)

    def test_home_page_cache(self):
        new_post = Post.objects.create(
            text='New test text',
            author=ViewsTest.author,
            group=ViewsTest.group
        )
        self.guest_client.get(reverse('index'))
        new_post.delete()
        response = self.guest_client.get(reverse('index'))
        self.assertIn(new_post.text, str(response.content))
        cache.clear()
        response = self.guest_client.get(reverse('index'))
        last_post = response.context['page'].object_list[0]
        self.assertNotEqual(last_post, new_post)

    def test_authorized_client_profile_follow(self):
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': ViewsTest.author.username}))
        followship = Follow.objects.get(user=self.user)
        self.assertEqual(followship.author, ViewsTest.author)

    def test_authorized_client_profile_unfollow(self):
        Follow.objects.create(
            user=self.user,
            author=ViewsTest.author)
        self.authorized_client.get(reverse(
            'profile_unfollow',
            kwargs={'username': ViewsTest.author.username}))
        self.assertEqual(self.user.follower.count(), 0)

    def test_new_post_shows_to_follower(self):
        Follow.objects.create(
            user=self.user,
            author=ViewsTest.author)
        new_post = Post.objects.create(
            text='Новый тестовый текст',
            author=ViewsTest.author)
        response = self.authorized_client.get(reverse('follow_index'))
        last_post = response.context['page'].object_list[0]
        self.assertEqual(last_post, new_post)

    def test_new_post_not_shows_to_unfollower(self):
        new_post = Post.objects.create(
            text='Новый тестовый текст',
            author=ViewsTest.author)
        response = self.authorized_client.get(reverse('follow_index'))
        last_post = response.context['page'].object_list.first
        self.assertNotEqual(last_post, new_post)


class PaginationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Test-user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        for i in range(0, PAGE_SIZE + 3):
            text = 'Тестовый текст'
            Post.objects.create(
                text=text,
                author=cls.author,
                group=cls.group,)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Test-user-2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_home_page_contains_correct_quantity_records(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(len(response.context['page'].object_list), PAGE_SIZE)

    def test_second_home_page_contains_three_records(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context['page'].object_list), 3)

    def test_first_group_page_contains_correct_quantity_records(self):
        response = self.guest_client.get(reverse(
            'group_posts', kwargs={'slug': PaginationTest.group.slug}))
        self.assertEqual(len(response.context['page'].object_list), PAGE_SIZE)

    def test_second_group_page_contains_three_records(self):
        response = self.guest_client.get(reverse(
            'group_posts', kwargs={
                'slug': PaginationTest.group.slug}) + '?page=2')
        self.assertEqual(
            len(response.context['page'].object_list), 3)

    def test_first_profile_page_contains_correct_quantity_records(self):
        response = self.guest_client.get(reverse(
            'profile', kwargs={'username': PaginationTest.author.username}))
        self.assertEqual(len(response.context['page'].object_list), PAGE_SIZE)

    def test_second_profile_page_contains_three_records(self):
        response = self.guest_client.get(reverse(
            'profile',
            kwargs={'username': PaginationTest.author.username}) + '?page=2')
        self.assertEqual(len(response.context['page'].object_list), 3)
