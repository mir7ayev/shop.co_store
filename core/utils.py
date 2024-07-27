import requests

from django.conf import settings


def check_service_access_token(service_access_token):
    response = requests.post(
        url="http://134.122.76.27:8026/api/v1/check/token/",
        data={'secret_token': service_access_token}
    )
    response.raise_for_status()

    return True


def get_service_access_token():
    response = requests.post(
        url="http://134.122.76.27:8026/api/v1/create/token/",
        data={'secret_service_key': settings.AUTH_SECRET_KEY}
    )
    response.raise_for_status()

    return response.json().get('secret_token')


def get_user_data(user_access_token):
    service_access_token = get_service_access_token()
    response = requests.post(
        url="http://134.122.76.27:8025/api/v1/auth/single/user/",
        headers={'Authorization': f'Bearer {user_access_token}'},
        data={'secret_token': service_access_token}
    )
    response.raise_for_status()

    return response.json()
