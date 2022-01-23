from django_filters import FilterSet, CharFilter, BooleanFilter, Filter, ModelChoiceFilter
from .models import Post, Author


class PostFilter(FilterSet):
    # post_author = Filter(field_name='post_author__author_user__first_name')
    # headline = CharFilter(field_name='headline', )

    class Meta:
        model = Post
        fields = {'post_author__author_user__first_name': ['contains'],
                  'headline': ['icontains'],
                  'create_date': ['lte'],
                  }

# class PostFilter(FilterSet):
#
#     class Meta:
#         model = Post
#         fields = {'post_author__author_user__first_name': ['contains'], 'headline': ['icontains'], 'create_date': ['lte']}
