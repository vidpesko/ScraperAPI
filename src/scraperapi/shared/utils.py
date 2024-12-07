import ast, json


def decode_message(message: str) -> tuple[str, dict]:
    """Decode received message

    Args:
        message (str): string message

    Raises:
        Exception:

    Returns:
        tuple[str, dict]: url, {params}
    """

    print(message)
    message_dict = json.loads(message)

    url = message_dict["url"]
    params = message_dict.get("parameters", {})

    return url, params


def encode_message(url: str, scraper_params: dict = None) -> str:
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

    return json.dumps(message)
