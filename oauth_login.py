import oauth2 as oauth
import urlparse

class OAuthLogin:
    REQUEST_TOKEN_URL = 'http://www.tumblr.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'http://www.tumblr.com/oauth/access_token'
    AUTHORIZE_URL = 'http://www.tumblr.com/oauth/authorize'

    def __init__(self, consumer_key, consumer_secret):
        # Begin authentication
        self._consumer = oauth.Consumer(consumer_key, consumer_secret)
        resp, content = oauth.Client(self._consumer).request(self.REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        request_token = dict(urlparse.parse_qsl(content))
        self._oauth_token_secret = request_token['oauth_token_secret']
        self.oauth_token = request_token['oauth_token']
        self.login_url = "%s?oauth_token=%s" % (self.AUTHORIZE_URL, self.oauth_token)

    def verify_authentication(self, oauth_verifier, oauth_token):
        token = oauth.Token(oauth_token, self._oauth_token_secret)
        token.set_verifier(oauth_verifier)
        resp, content = oauth.Client(self._consumer, token).request(self.ACCESS_TOKEN_URL, "POST")
        access_token = dict(urlparse.parse_qsl(content))
        return {'oauth_token': access_token['oauth_token'],
                'oauth_token_secret': access_token['oauth_token_secret']}
