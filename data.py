
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/ramirezdiana/myst_equipo6_lab3                                       -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import requests
import pandas as pd
def api():
    """

    :return: Dataframe de instrumentos del API
    """
    class BearerAuth(requests.auth.AuthBase):
        def __init__(self, token):
            self.token = token
        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r
    response = requests.get('https://api-fxpractice.oanda.com/v3/accounts/101-011-16494438-002/instruments',
                            auth=BearerAuth('4d5aad4aa2939a132fe264df7592d9ab-6a99aceb020a93917af53376dbb1a8d5'))
    general = pd.read_json(response.text)
    general = general.instruments.apply(pd.Series)
    return general


instruments = api()
