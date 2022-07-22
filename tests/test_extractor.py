import matplotlib as mpl  # must be run first! But therefore requires noqa E02 on all other imports
mpl.use('Agg')

from numpy.testing import run_module_suite  # noqa: E402

from spectractor import parameters  # noqa: E402
from spectractor.extractor.extractor import Spectractor  # noqa: E402
from spectractor.logbook import LogBook  # noqa: E402
from spectractor.config import load_config, apply_rebinning_to_parameters  # noqa: E402
import os  # noqa: E402
import sys  # noqa: E402
import numpy as np  # noqa: E402
import unittest  # noqa: E402


def test_with_retry():
    import logging
    import requests
    import time
    from requests.adapters import HTTPAdapter, Retry
    session = requests.Session()
    retries = Retry(total=1)
    session.mount('https://', HTTPAdapter(max_retries=retries))
    logging.warn(session.get("https://simbad.u-strasbg.fr/simbad/sim-script"))
    time.sleep(5*60)
    logging.warn(session.get("https://simbad.u-strasbg.fr/simbad/sim-script"))


def test_without_retry():
    import logging
    import requests
    import time
    from requests.adapters import HTTPAdapter, Retry
    session = requests.Session()
    logging.warn(session.get("https://simbad.u-strasbg.fr/simbad/sim-script"))
    time.sleep(5*60)
    logging.warn(session.get("https://simbad.u-strasbg.fr/simbad/sim-script"))


if __name__ == "__main__":

    run_module_suite()
