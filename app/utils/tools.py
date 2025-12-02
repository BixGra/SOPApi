from urllib.parse import urlencode


def data_to_query_parameters(data: dict) -> str:
    query_parameters: list[tuple] = []
    for key, value in data.items():
        if isinstance(value, (list, tuple)):
            for item in value:
                query_parameters.append((key, str(item)))
        else:
            query_parameters.append((key, str(value)))
    return urlencode(query_parameters)
