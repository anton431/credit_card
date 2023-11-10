from aiohttp import ClientSession


async def async_user_authentication_headers(client: ClientSession, data) -> dict[str, str]:
    response_token = await client.post("/api/auth", data=data, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'accept': 'application/json'})

    auth_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    return headers


async def async_authentication_token_from_username(client: ClientSession,
                                       card_number: str,
                                       password: str) -> dict[str, str]:
    """
    Register user and return a valid token for the user with given username.
    """
    data = {
        "username": card_number,
        "password": password
    }

    return await async_user_authentication_headers(client=client, data=data)


def user_authentication_headers(client: ClientSession, data) -> dict[str, str]:
    response_token = client.post("/api/auth", data=data, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'accept': 'application/json'})

    auth_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    return headers


def authentication_token_from_username(client: ClientSession,
                                       card_number: str,
                                       password: str) -> dict[str, str]:
    """
    Register user and return a valid token for the user with given username.
    """
    data = {
        "username": card_number,
        "password": password
    }

    return user_authentication_headers(client=client, data=data)
