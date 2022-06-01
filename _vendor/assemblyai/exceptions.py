"""Exceptions for the assemblyai library."""


def handle_errors(response, status_code):
    if status_code >= 400 and status_code < 500:
        msg = response.json()
        raise ClientError(msg)

    elif status_code == 500:
        msg = 'Server error, developers have been alerted.'
        raise ServerError(msg)

    elif status_code > 500:
        raise ClientError(status_code)


def handle_warnings(response, object, log):
    """Handle  warnings and exceptions."""
    warning = None
    handle_errors(response, response.status_code)
    if response:
        response = response.json()[object]
    if 'warning' in response:
        warning = response['warning']
        log.warning('Warning: %s' % warning)
    if response['status'] == 'error':
        msg = response['error']
        raise ServerError(msg)
    return warning


class ClientError(Exception):
    pass


class ServerError(Exception):
    pass
