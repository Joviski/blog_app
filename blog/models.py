from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import CustomUser
# Create your models here.


class Post(models.Model):
    """Post Model Class."""
    title = models.CharField(
        max_length=50,
        verbose_name=_("Post Title"),
        help_text=_("Title of the post."),
        null=False,
        blank=False,
    )
    content = models.TextField(
        verbose_name=_("Post Content"),
        help_text=_("Content of the post."),
        null=False,
        blank=False,
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="post",
        null=False,
        blank=False,
    )
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta Class."""
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def __str__(self):
        """Override str() method."""
        return f"{self.id} - {self.title}"
