from django.db import models
from django_userforeignkey.models.fields import UserForeignKey


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuthorMixin(models.Model):
    created_by = UserForeignKey(auto_user_add=True, verbose_name="Created By",
                                related_name="%(app_label)s_%(class)s_related")

    class Meta:
        abstract = True


class AuthorWithTimeStampMixin(AuthorMixin, TimeStampMixin):
    pass

    class Meta:
        abstract = True
