import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news_pk_for_args, comment_form
):
    url = reverse('news:detail', args=news_pk_for_args)
    response = client.post(url, data=comment_form)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    not_author, not_author_client, news, news_pk_for_args, comment_form
):
    url = reverse('news:detail', args=news_pk_for_args)
    response = not_author_client.post(url, data=comment_form)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.news == news
    assert comment.text == comment_form['text']
    assert comment.author == not_author


def test_user_cant_use_bad_words(
    not_author_client, news_pk_for_args
):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_pk_for_args)
    response = not_author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        'form',
        'text',
        WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client, comment_pk_for_args, news_pk_for_args
):
    url = reverse('news:detail', args=news_pk_for_args)
    delete_url = reverse('news:delete', args=comment_pk_for_args)
    response = author_client.delete(delete_url)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
    author_client, comment_pk_for_args, comment_form, news_pk_for_args, comment
):
    url = reverse('news:detail', args=news_pk_for_args)
    edit_url = reverse('news:edit', args=comment_pk_for_args)
    response = author_client.post(edit_url, data=comment_form)
    assertRedirects(response, f'{url}#comments')
    comment = Comment.objects.get()
    assert comment.text == comment_form['text']


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment_pk_for_args
):
    delete_url = reverse('news:delete', args=comment_pk_for_args)
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        comment_pk_for_args, comment_form, not_author_client, comment
):
    edit_url = reverse('news:edit', args=comment_pk_for_args)
    response = not_author_client.post(edit_url, data=comment_form)
    assert response.status_code == HTTPStatus.NOT_FOUND
    edit_comment = Comment.objects.get()
    assert edit_comment.text == comment.text
