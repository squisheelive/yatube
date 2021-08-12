import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый Текст',
            'group': FormsTest.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        post = Post.objects.create(
            text='Текст до редактирования',
            author=self.user,
            group=FormsTest.group
        )
        pk = post.pk
        form_data = {
            'text': 'Тестовый Текст',
            'group': FormsTest.group.pk,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': pk}),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(pk=pk)
        self.assertRedirects(response, reverse(
            'post', kwargs={
                'username': self.user.username,
                'post_id': pk}))
        self.assertEqual(post.text, 'Тестовый Текст')

    def test_comment_post(self):
        author = User.objects.create(username='Test-user-2')
        post = Post.objects.create(
            text='Новый тестовый текст',
            author=author)
        comment_count = post.comments.count()
        response = self.authorized_client.post(
            reverse('add_comment', kwargs={
                'username': author.username,
                'post_id': post.pk}),
            data={'text': 'тестовый комментарий'},
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'post', kwargs={
                'username': author.username,
                'post_id': post.pk}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
