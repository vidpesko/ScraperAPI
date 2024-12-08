import ast, json


def encode_msg(data: dict) -> str:
    """Shared function for all encode_* functions

    Args:
        data (dict): dict of data

    Returns:
        str: Message
    """

    return json.dumps(data).encode()


def decode_command(message: str) -> tuple[str, dict]:
    """Decode received message

    Args:
        message (str): string message

    Raises:
        Exception:

    Returns:
        tuple[str, dict]: url, {params}
    """

    message_dict = json.loads(message)

    url = message_dict["url"]
    params = message_dict.get("parameters", {})

    return url, params


def encode_command(url: str, scraper_params: dict = None) -> str:
    """Generate message to send over amqp to server. Encode all scraper parameters to JSON

    #### Command format:
        {
            "url": ""
            "parameters": {}
        }

    Args:
        url (str): website url
        **kwargs (key: value): parameters to send

    Returns:
        str: generated message
    """

    if not scraper_params:
        scraper_params = {}

    message = {
        "url": url,
        "parameters": scraper_params
    }

    return encode_msg(message)


def encode_exception(exception: Exception, url: str, scraper_params: dict = None) -> str:
    """Encodes scraper exceptions to send back to client

    Args:
        exception (Exception): Exception
        url (str): url of page
        scraper_params (dict, optional): scraper parameters. Defaults to None.

    Returns:
        str: Message
    """

    if not scraper_params:
        scraper_params = {}

    message = {
        "exception": True,
        "str": str(exception),
        "repr": repr(exception),
        "url": url,
        "scraper_parameters": scraper_params
    }

    return encode_msg(message)


def encode_response(html: str, url: str, scraper_params: dict = None) -> str:
    """Encodes scraper output (HTML) to send it back to the client

    Args:
        html (str): html of page
        url (str): url of page
        scraper_params (dict, optional): scraper parameters. Defaults to None.

    Returns:
        str: Message
    """

    if not scraper_params:
        scraper_params = {}

    message = {
        "exception": False,
        "html": html,
        "url": url,
        "scraper_parameters": scraper_params
    }

    return encode_msg(message)
