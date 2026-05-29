from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

import graphene
from graphene_django import DjangoObjectType

from .models import Tag, Cloudcast


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'tag_type')


class UserType(graphene.ObjectType):
    username = graphene.String()
    display_name = graphene.String()


class CloudcastType(DjangoObjectType):
    owner_info = graphene.Field(UserType)
    picture_url = graphene.String()

    class Meta:
        model = Cloudcast
        fields = ('id', 'name', 'slug', 'quality_score', 'play_count', 'publish_date')

    def resolve_owner_info(self, info):
        return UserType(
            username=self.owner.username,
            display_name=getattr(self.owner, 'first_name', self.owner.username),
        )

    def resolve_picture_url(self, info):
        return self.picture_url


def discover_show(genre_slugs, user=None, exclude_slugs=None):
    one_year_ago = timezone.now() - timedelta(days=365)

    base_qs = (
        Cloudcast.objects
        .filter(
            tags__slug__in=genre_slugs,
            tags__tag_type='genre',
        )
        .filter(quality_score__gte=0.5)
        .filter(publish_date__gte=one_year_ago)
        .filter(is_public=True)
    )

    if exclude_slugs:
        base_qs = base_qs.exclude(slug__in=exclude_slugs)

    base_qs = base_qs.annotate(
        genre_match_count=Count(
            'tags',
            filter=Q(tags__slug__in=genre_slugs, tags__tag_type='genre'),
            distinct=True,
        )
    )

    base_qs = base_qs.order_by('-genre_match_count', '-play_count')

    if user and user.is_authenticated:
        unlistened_qs = base_qs.exclude(listeners=user)
        result = unlistened_qs.first()
        if result:
            return result

    return base_qs.first()


class Query(graphene.ObjectType):
    tags = graphene.List(
        TagType,
        tag_type=graphene.String(),
        first=graphene.Int(),
    )
    discover_show = graphene.Field(
        CloudcastType,
        genre_slugs=graphene.List(
            graphene.NonNull(graphene.String),
            required=True,
        ),
        exclude_slugs=graphene.List(graphene.NonNull(graphene.String)),
    )

    def resolve_tags(self, info, tag_type=None, first=None):
        qs = Tag.objects.all()
        if tag_type:
            qs = qs.filter(tag_type=tag_type)
        qs = qs.order_by('name')
        if first:
            qs = qs[:first]
        return qs

    def resolve_discover_show(self, info, genre_slugs, exclude_slugs=None):
        if not genre_slugs:
            return None
        user = info.context.user if hasattr(info.context, 'user') else None
        return discover_show(genre_slugs, user=user, exclude_slugs=exclude_slugs)
