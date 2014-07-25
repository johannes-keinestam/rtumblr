import os
import pytumblr
from bottle import get, post, request, run, view, TEMPLATE_PATH, static_file, redirect, template
import urlparse
import oauth2 as oauth
from functools import partial

consumer_key = '04Liy0s8Gfxx7TyaojiPVN0JMMACuhM1TITjL8fw5j7X3vf0Pw'
consumer_secret = '92QRq11NKjWy4Bo5jgF3edfu3QY3fUTFNCectAaEu7sFn1jLQC'

class OAuthTumblrRestClient(pytumblr.TumblrRestClient):

    REQUEST_TOKEN_URL = 'http://www.tumblr.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'http://www.tumblr.com/oauth/access_token'
    AUTHORIZE_URL = 'http://www.tumblr.com/oauth/authorize'
    user = None

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
        return "%s?oauth_token=%s" % (self.AUTHORIZE_URL, request_token['oauth_token'])

    def authenticate_step_2(self, oauth_verifier, oauth_token):
        token = oauth.Token(oauth_token, self._oauth_token_secret)
        token.set_verifier(oauth_verifier)
        resp, content = oauth.Client(self._consumer, token).request(self.ACCESS_TOKEN_URL, "POST")
        access_token = dict(urlparse.parse_qsl(content))
        # Authentication done, replace request object with authenticated one
        self._request = self.request
        self.request = pytumblr.request.TumblrRequest(self.consumer_key, self.consumer_secret,
                                                      access_token['oauth_token'],
                                                      access_token['oauth_token_secret'])
        self.user = self.info()['user']['name']

    def logout(self):
        assert self.authenticated, "You are not logged in -- cannot log out!"
        self.request = self._request
        self.user = None

    @property
    def authenticated(self):
        return self.user != None

class BlogNotFoundException(Exception):
    pass

def response_to_posts(post_response, sort=False):
    posts = []
    for post in post_response:
        posts.append({
            'blog':  post['blog_name'],
            'type':  post['type'],
            'notes': post['note_count'],
            'link':  post['post_url'],
            'title': post.get('title') or post.get('id')
        })
    if sort:
        return sorted(posts, key=lambda p: int(p['notes']), reverse=sort=='up')
    return posts

def get_user_avatar():
    if tumblr_client.authenticated:
        return tumblr_client.avatar(tumblr_client.user)['avatar_url']
    return 'http://assets.tumblr.com/images/favicons/favicon.ico'

def template_dict(request, **params):
    result = {'pages': pages, 'username': tumblr_client.user,
              'avatar_url': get_user_avatar(),
              'limit': requested_posts(request)}
    result.update(params)
    return result

def get_posts(func, key, n=20, **params):
    max_allowed = 20
    left = n
    posts = []
    while left > 0:
        response = func(limit=min(n, max_allowed), offset=n-left, **params)
        if 'meta' in response and response['meta']['status'] == 404:
            raise BlogNotFoundException()
        fetched_posts = response[key]
        if not fetched_posts:
            break;
        left -= len(fetched_posts)
        posts += fetched_posts
    return posts

@get('/blog')
@view('templates/index2')
def blog_search():
    print 'Hey bro!'
    blog_page = ('/blog/' + request.query.blog) if request.query.blog else '/'
    return redirect(blog_page)

@get('/blog/<blog>')
@view('templates/index2')
def blog_view(blog):
    num_posts = requested_posts(request)
    params = {}
    if request.query.ptype:
        params['type'] = request.query.ptype
    try:
        response = get_posts(partial(tumblr_client.posts, blog), 'posts', num_posts, **params)
    except BlogNotFoundException:
        return template_dict(None, page_title='Blog %s not found' % blog)
    posts = response_to_posts(response, request.query.sort)
    blog_info = tumblr_client.blog_info(blog)
    return template_dict(request,
                         posts=posts,
                         title=blog_info['blog']['name'],
                         subtitle=blog_info['blog']['title'],
                         avatar_url=tumblr_client.avatar(blog)['avatar_url'])

def requested_posts(request):
    if not request or not request.query.limit.isdigit():
        return 20
    return int(request.query.limit)

@get('/likes')
@view('templates/index2')
def likes_view():
    if tumblr_client.authenticated:
        num_posts = requested_posts(request)
        liked_posts = get_posts(tumblr_client.likes, 'liked_posts', num_posts)
        posts = response_to_posts(liked_posts, request.query.sort)
        page_title = 'Likes'
    else:
        posts = None
        page_title = 'Welcome, Guest!'
    return template_dict(request, posts=posts, page_title=page_title)

@get('/')
@view('templates/index2')
def dashboard_view():
    if tumblr_client.authenticated:
        num_posts = requested_posts(request)
        dashboard_posts = get_posts(tumblr_client.dashboard, 'posts', num_posts)
        posts = response_to_posts(dashboard_posts, request.query.sort)
        page_title = 'Dashboard'
    else:
        posts = None
        page_title = 'Welcome, Guest!'
    return template_dict(request, posts=posts, page_title=page_title)

@get('/static/<sfile:re:.+>')
def get_static(sfile):
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    return static_file(sfile, root=root)

@get('/login')
def login():
    return redirect(tumblr_client.authenticate(consumer_key, consumer_secret))

@get('/verify')
def verify():
    tumblr_client.authenticate_step_2(request.query.oauth_verifier, request.query.oauth_token)
    return redirect('/')

@get('/logout')
def logout():
    tumblr_client.logout()
    return redirect('/')

@get('/hi')
def say_hello():
    username = tumblr_client.info()['user']['name']
    return '<p><h1>Welcome <b>%s</b></h1></p>' % username

pages = {
    'Dashboard': '/',
    'Likes': '/likes',
}
TEMPLATE_PATH.append(os.path.dirname(os.path.realpath(__file__)))
tumblr_client = OAuthTumblrRestClient(consumer_key)
run(host='localhost', port=8080, reloader=True)
