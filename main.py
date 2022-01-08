from prometheus_client import Counter, start_http_server
import urllib.parse as urlparse
import requests
import config

LONG_POLL_BASE_URL = "https://{server}?act=a_check&key={key}&ts={ts}&wait=25&mode=2&version=2"


def api_request(method, params):
    parts = list(urlparse.urlparse(f"https://api.vk.com/method/{method}"))
    query = params | {
        "access_token": config.ACCESS_TOKEN,
        "v": "5.131"
    }

    parts[4] = urlparse.urlencode(query)
    url = urlparse.urlunparse(parts)

    return requests.get(url)


messages = Counter("messages", "Messages counter", ["peer_id", "sender"])
long_poll_data = api_request("messages.getLongPollServer", dict(lp_version=3)).json()["response"]

start_http_server(3333)

while True:
    response = requests.get(LONG_POLL_BASE_URL.format(**long_poll_data)).json()
    long_poll_data.update(ts=response["ts"])
    for u in response["updates"]:
        if u[0] == 4:
            messages.labels(str(u[3]), u[6]["from"]).inc()
