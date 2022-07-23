import logging
import requests
import time
from requests.adapters import HTTPAdapter, Retry
from numpy.testing import run_module_suite  # noqa: E402


def test_google_with_retry():
    URL = "https://www.google.com/"
    session = requests.Session()
    retries = Retry(total=1)
    session.mount("https://", HTTPAdapter(max_retries=retries))
    logging.warn(session.get(URL))
    time.sleep(5 * 60)
    logging.warn(session.get(URL))


def test_google_without_retry():
    URL = "https://www.google.com/"
    session = requests.Session()
    logging.warn(session.get(URL))
    time.sleep(5 * 60)
    logging.warn(session.get(URL))


def test_simbad_with_retry():
    URL = "https://simbad.u-strasbg.fr/simbad/sim-script"
    session = requests.Session()
    retries = Retry(total=1)
    session.mount("https://", HTTPAdapter(max_retries=retries))
    logging.warn(session.get(URL))
    time.sleep(5 * 60)
    logging.warn(session.get(URL))


def test_simbad_without_retry():
    URL = "https://simbad.u-strasbg.fr/simbad/sim-script"
    session = requests.Session()
    logging.warn(session.get(URL))
    time.sleep(5 * 60)
    logging.warn(session.get(URL))


if __name__ == "__main__":
    run_module_suite()
