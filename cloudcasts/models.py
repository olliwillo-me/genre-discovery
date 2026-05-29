from django.conf import settings
from django.db import models


class Tag(models.Model):
    TAG_TYPE_CHOICES = [
        ('genre', 'Genre'),
        ('freeform', 'Freeform'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    tag_type = models.CharField(max_length=20, choices=TAG_TYPE_CHOICES, default='freeform')

    def __str__(self):
        return self.name


class Cloudcast(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cloudcasts',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='cloudcasts')
    quality_score = models.FloatField(default=0.0)
    publish_date = models.DateTimeField()
    play_count = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    picture_url = models.URLField(blank=True, default='')
    listeners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='listened_cloudcasts',
    )

    class Meta:
        unique_together = ('owner', 'slug')
        ordering = ['-publish_date']

    def __str__(self):
        return self.name
