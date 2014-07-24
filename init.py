import os
import pytumblr
from bottle import get, post, request, run, view, TEMPLATE_PATH, static_file, redirect
import urlparse
import oauth2 as oauth

consumer_key = '04Liy0s8Gfxx7TyaojiPVN0JMMACuhM1TITjL8fw5j7X3vf0Pw'
consumer_secret = '92QRq11NKjWy4Bo5jgF3edfu3QY3fUTFNCectAaEu7sFn1jLQC'


class OAuthTumblrRestClient(pytumblr.TumblrRestClient):

    REQUEST_TOKEN_URL = 'http://www.tumblr.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'http://www.tumblr.com/oauth/access_token'
    AUTHORIZE_URL = 'http://www.tumblr.com/oauth/authorize'
    authenticated = False

    def authenticate(self, consumer_key, consumer_secret):
        if self.authenticated:
            return
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        # Begin authentication
        self._consumer = oauth.Consumer(consumer_key, consumer_secret)
        resp, content = oauth.Client(self._consumer).request(self.REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        request_token = dict(urlparse.parse_qsl(content))
        self._oauth_token_secret = request_token['oauth_token_secret']
        return "%s?oauth_token=%s" % (AUTHORIZE_URL, request_token['oauth_token'])

    def authenticate_step_2(self, oauth_verifier, oauth_token):
        token = oauth.Token(oauth_token, self._oauth_token_secret)
        token.set_verifier(oauth_verifier)
        resp, content = oauth.Client(self._consumer, token).request(access_token_url, "POST")
        access_token = dict(urlparse.parse_qsl(content))
        # Authentication done, replace request object with authenticated one
        self._request = self.request
        tumblr_client = pytumblr.TumblrRestClient(self.consumer_key, self.consumer_secret,
                                                  access_token['oauth_token'],
                                                  access_token['oauth_token_secret'])
        self.authenticated = True
        pprint(tumblr_client.info())


class KeyContainer():
    def __init__(self): self.keys = {}
    def get(self, key): return self.keys[key]
    def set(self, key, val): self.keys[key] = val

@get('/blog/<blog>')
@view('templates/index2')
def index(blog):
    params = {}
    if request.query.ptype:
        params['type'] = request.query.ptype
    response = tumblr_client.posts(blog, **params)
    posts = []
    for raw_post in response['posts']:
        posts.append({
            'blog':  raw_post['blog_name'],
            'type':  raw_post['type'],
            'likes': 0,
            'notes': raw_post['note_count'],
            'link':  raw_post['post_url']
        })
    return {'posts': posts, 'blog_info': response['blog'], 'avatar_url': tumblr_client.avatar(blog)['avatar_url']}

@get('/')
@view('templates/index2')
def index():
    posts = [
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'},
        {'blog': 'peacecorps', 'type': 'text', 'likes': 50, 'notes': 250, 'link': 'http://peacecorps.tumblr.com/post/92542423560/peace-corps-volunteers-support-new-let-girls'}
    ]
    return {'posts': posts}

@get('/static/<sfile:re:.+>')
def get_static(sfile):
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    print 'trying to fetch %s from %s' % (sfile, root)
    return static_file(sfile, root=root)

@get('/login')
def login():
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for 
    # having the user authorize an access token and to sign the request to obtain 
    # said access token.

    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    print "Request Token:"
    print "    - oauth_token        = %s" % request_token['oauth_token']
    print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
    print 

    keys.set('oauth_token_secret', request_token['oauth_token_secret'])
    keys.set('consumer', consumer)
    # Step 2: Redirect to the provider. Since this is a CLI script we do not 
    # redirect. In a web application you would redirect the user to the URL
    # below.

    authorizi = "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
    print "Go to the following link in your browser:"
    print 
    print authorizi
    return redirect(authorizi)

@post('/verify')
@get('/verify')
def login():
    oauth_verifier = request.query.oauth_verifier
    token = oauth.Token(request.query.oauth_token,
                        keys.get('oauth_token_secret'))
    token.set_verifier(oauth_verifier)
    client = oauth.Client(keys.get('consumer'), token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    print 'access token response: %s' % resp
    print 'access token decoded: %s' % access_token
    from pprint import pprint

    print "Access Token:"
    print "    - oauth_token        = %s" % access_token['oauth_token']
    print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    print
    print "You may now access protected resources using the access tokens above." 
    print

    tumblr_client = pytumblr.TumblrRestClient(consumer_key, consumer_secret,
                                              access_token['oauth_token'],
                                              access_token['oauth_token_secret'])
    print 'you are:'
    pprint(tumblr_client.info())

@get('/hi')
def say_hello():
    return str(tumblr_client.info())



oauth_token_secret = None

keys = KeyContainer()
TEMPLATE_PATH.append(os.path.dirname(os.path.realpath(__file__)))
tumblr_client = pytumblr.TumblrRestClient(consumer_key)
run(host='localhost', port=8080, reloader=True)
