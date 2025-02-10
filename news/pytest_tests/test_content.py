import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(home_object_list):
    object_list = home_object_list
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(home_object_list):
    object_list = home_object_list
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, news_pk_for_args, many_comments):
    detail_url = reverse('news:detail', args=news_pk_for_args)
    response = client.get(detail_url)
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user, form_status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('not_author_client'), True)
    )
)
def test_different_client_has_form(news_pk_for_args, user, form_status):
    detail_url = reverse('news:detail', args=news_pk_for_args)
    response = user.get(detail_url)
    assert ('form' in response.context) == form_status
    if form_status:
        assert isinstance(response.context['form'], CommentForm)
