import ast


def decode_command(command: str) -> tuple[str, dict]:
    """Decode received command

    Args:
        command (str): string command

    Raises:
        Exception: 

    Returns:
        tuple[str, dict]: url, {params}
    """

    split_cmd = command.split("*params=")
    if len(split_cmd) == 1:
        url = command
        params = {}
    elif len(split_cmd) == 2:
        url, params_str = split_cmd
        params = ast.literal_eval(params_str)
    else:
        raise Exception("Got unexpected ''params'' argument in command")

    return url, params


def generate_command(url: str, scraper_params: dict = None) -> str:
    """Generate command to send over amqp to server. Encode all scraper parameters to specified format

    Command format:
        < url >*params={key 1: val 1,...}

    Args:
        url (str): website url
        **kwargs (key: value): parameters to send

    Returns:
        str: generated command
    """

    if not scraper_params:
        scraper_params = {}

    command = f"{url}*params={scraper_params}"

    return command
