from django.test import TestCase

from apps.tags.models import Tag


class TagModelTest(TestCase):
    def test_tag_creation(self):
        tag = Tag.objects.create(name='test tag')

        self.assertEqual(tag.name, 'test tag')
