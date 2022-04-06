from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Q


class UserManager(BaseUserManager):
    def _create_user(self, email, **extra_fields):
        if not email:
            raise ValueError('The given email must be set.')

        user = self.model(email=email, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, email, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, **extra_fields)

    def create_superuser(self, email, **extra_fields):
        """ Create and save a SuperUser with the given email. """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, **extra_fields)

    def search(self, query):
        """
        Search the given string (query) in full_name, username and biography fields.
        """
        return self.filter(
            Q(full_name__icontains=query, full_name__trigram_word_similar=query) |
            Q(username__icontains=query) | Q(username__trigram_word_similar=query) |
            Q(biography__icontains=query) | Q(biography__trigram_word_similar=query)
        )
