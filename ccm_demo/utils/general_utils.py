import warnings
import requests

def warn_for_status(response, message):
    if response.status_code != 200:
        warnings.warn("Response status code: {}, status message {}".format(response.status_code, message))
        return None
    else:
        return response.content.decode().strip()