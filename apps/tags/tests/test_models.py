from django.test import TestCase

from apps.tags.models import Tag


class TagModelTest(TestCase):
    def test_tag_creation(self):
        tag_obj = Tag.objects.create(tag='test tag')

        self.assertEqual(tag_obj.tag, 'test tag')
