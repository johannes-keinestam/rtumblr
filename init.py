import os
from pytumblr import TumblrRestClient
from bottle import get, request, run, view, TEMPLATE_PATH, static_file, redirect, template, response
from functools import partial
from oauth_login import OAuthLogin
from datetime import datetime

consumer_key = '04Liy0s8Gfxx7TyaojiPVN0JMMACuhM1TITjL8fw5j7X3vf0Pw'
consumer_secret = '92QRq11NKjWy4Bo5jgF3edfu3QY3fUTFNCectAaEu7sFn1jLQC'
pending_logins = {}

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

def get_pending_login(oauth_token):
    # Cull hung logins
    for oauth_token, request in pending_logins.iteritems():
        if (datetime.now() - request['time']).total_seconds() > 1800:
            del pending_logins[oauth_token]
            print 'Culled pending login request %s' % oauth_token
    return pending_logins.get(oauth_token, {}).get('request')

def add_login_request(login_request):
    pending_logins[login_request.oauth_token] = {
        'request': login_request,
        'time': datetime.now()
    }

def get_user_avatar():
    if authenticated():
        return tumblr_client().avatar(username())['avatar_url']
    return 'http://assets.tumblr.com/images/favicons/favicon.ico'

def template_dict(**params):
    result = {'pages': pages, 'username': username(),
              'avatar_url': get_user_avatar(),
              'limit': requested_posts()}
    result.update(params)
    return result

def get_posts(func, key, n=20, **params):
    def filter_duplicate_posts(posts):
        post_ids = []
        result_posts = []
        for post in posts:
            if post['id'] not in post_ids:
                result_posts.append(post)
                post_ids.append(post['id'])
        return result_posts
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
    return filter_duplicate_posts(posts)

@get('/blog')
@view('templates/index2')
def blog_search():
    print 'Hey bro!'
    blog_page = ('/blog/' + request.query.blog) if request.query.blog else '/'
    return redirect(blog_page)

@get('/blog/<blog>')
@view('templates/index2')
def blog_view(blog):
    client = tumblr_client()
    num_posts = requested_posts()
    params = {}
    if request.query.ptype:
        params['type'] = request.query.ptype
    try:
        response = get_posts(partial(client.posts, blog), 'posts', num_posts, **params)
    except BlogNotFoundException:
        return template_dict(page_title='Blog %s not found' % blog)
    posts = response_to_posts(response, request.query.sort)
    blog_info = client.blog_info(blog)
    return template_dict(posts=posts,
                         title=blog_info['blog']['name'],
                         subtitle=blog_info['blog']['title'],
                         avatar_url=client.avatar(blog)['avatar_url'])

def requested_posts():
    if not request or not request.query.limit.isdigit():
        return 20
    return int(request.query.limit)

@get('/likes')
@view('templates/index2')
def likes_view():
    params = {}
    if request.query.ptype:
        params['type'] = request.query.ptype
    if authenticated():
        num_posts = requested_posts()
        liked_posts = get_posts(tumblr_client().likes, 'liked_posts', num_posts, **params)
        posts = response_to_posts(liked_posts, request.query.sort)
        page_title = 'Likes'
    else:
        posts = None
        page_title = 'Welcome, Guest!'
    return template_dict(posts=posts, page_title=page_title)

@get('/')
@view('templates/index2')
def dashboard_view():
    params = {}
    if request.query.ptype:
        params['type'] = request.query.ptype
    if authenticated():
        num_posts = requested_posts()
        dashboard_posts = get_posts(tumblr_client().dashboard, 'posts', num_posts, **params)
        posts = response_to_posts(dashboard_posts, request.query.sort)
        page_title = 'Dashboard'
    else:
        posts = None
        page_title = 'Welcome, Guest!'
    return template_dict(posts=posts, page_title=page_title)

@get('/static/<sfile:re:.+>')
def get_static(sfile):
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    return static_file(sfile, root=root)

@get('/login')
def login():
    print 'Sent login: %s' % ([consumer_key, consumer_secret])
    login_request = OAuthLogin(consumer_key, consumer_secret)
    add_login_request(login_request)
    return redirect(login_request.login_url)

@get('/verify')
def verify():
    print 'Received login: %s' % (request.query_string)
    login_request = get_pending_login(request.query.oauth_token)
    if not login_request:
        return 'Login timed out'
    login_response = login_request.verify_authentication(request.query.oauth_verifier,
                                                         request.query.oauth_token)
    response.set_cookie('oauth_token', login_response['oauth_token'])
    response.set_cookie('oauth_token_secret', login_response['oauth_token_secret'])
    return redirect('/')


@get('/logout')
def logout():
    response.set_cookie('oauth_token', '')
    response.set_cookie('oauth_token_secret', '')
    return redirect('/')

@get('/hi')
def say_hello():
    return '<p><h1>Welcome <b>%s</b></h1></p>' % username()

def tumblr_client():
    oauth_token = request.get_cookie('oauth_token')
    oauth_token_secret = request.get_cookie('oauth_token_secret')
    if oauth_token and oauth_token_secret:
        return TumblrRestClient(consumer_key, consumer_secret,
                                oauth_token, oauth_token_secret)
    else:
        return TumblrRestClient(consumer_key, consumer_secret)

def authenticated():
    return username() != None

def username():
    user_info = tumblr_client().info()
    if 'meta' in user_info and user_info['meta']['status'] == 401:
        # Could not authenticate as the saved user.
        # Logging out.
        response.set_cookie('oauth_token', '')
        response.set_cookie('oauth_token_secret', '')
        return None
    return user_info['user']['name']


pages = {
    'Dashboard': '/',
    'Likes': '/likes',
}
TEMPLATE_PATH.append(os.path.dirname(os.path.realpath(__file__)))
run(host='localhost', port=8080, reloader=True)
