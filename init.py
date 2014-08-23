import os
from pytumblr import TumblrRestClient
from bottle import get, request, run, view, TEMPLATE_PATH, static_file, redirect, template, response
from functools import partial
from oauth_login import OAuthLogin
from datetime import datetime, timedelta

consumer_key = '04Liy0s8Gfxx7TyaojiPVN0JMMACuhM1TITjL8fw5j7X3vf0Pw'
consumer_secret = '92QRq11NKjWy4Bo5jgF3edfu3QY3fUTFNCectAaEu7sFn1jLQC'
pending_logins = {}

class BlogNotFoundException(Exception):
    pass

def response_to_posts(post_response, sort=False):
    posts = []
    for index, post in enumerate(post_response, start=1):
        photo_info = {
            'id': str(post.get('id')),
            'blog':  post.get('blog_name'),
            'type':  post.get('type'),
            'notes': post.get('note_count', -1),
            'link':  post.get('post_url'),
            'date': post['timestamp'],
            'title': post.get('title') or str(post.get('id')),
            'index': index,
        }
        if post.get('type') == 'photo':
            photo_format = post['photos'][0]['original_size']['url'][-3:].lower()
            if photo_format == 'gif':
                photo_info['type'] += ' (gif)'
            if len(post['photos']) > 1:
                photo_info['type'] += ' album'
        posts.append(photo_info)
    return posts

def sort_posts_by(posts, sort=False):
    if sort:
        return sorted(posts, key=lambda p: int(p['notes']), reverse=sort=='up')
    else:
        return posts

def get_pending_login(oauth_token):
    # Cull hung logins
    for oauth_token, request in pending_logins.iteritems():
        if (datetime.now() - request['time']) > timedelta(1800):
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
    return {'parameters': result}

def filter_duplicate_posts(posts):
    post_ids = []
    result_posts = []
    for post in posts:
        if post['id'] not in post_ids:
            result_posts.append(post)
            post_ids.append(post['id'])
    return result_posts

def non_paginated_post_fetcher(fetch, key, should_quit, filter_duplicates=False, **params):
    #
    # Fetches posts (a multiple of 20) until the function should_quit fails.
    # Filtering the result is up to the caller (e.g. not all the last 20 were wanted).
    #
    max_allowed = 20
    fetched = 0
    posts = []
    while not should_quit(posts):
        response = fetch(limit=max_allowed, offset=fetched, **params)
        if 'meta' in response and response['meta']['status'] == 404:
            raise BlogNotFoundException()
        fetched_posts = response_to_posts(response[key])
        if not fetched_posts:
            break;
        fetched += len(fetched_posts)
        posts += fetched_posts
    return filter_duplicate_posts(posts) if filter_duplicates else posts

def get_n_posts(fetcher, key, n=20, filter_duplicates=False, **params):
    def quit_when_n_posts(posts):
        return len(posts) >= n
    def filter_larger_posts(posts):
        return posts[0:n]
    posts = non_paginated_post_fetcher(fetcher, key, quit_when_n_posts, filter_duplicates, **params)
    return filter_larger_posts(posts)

def get_posts_since_date(fetcher, key, until_date, filter_duplicates=False, **params):
    def quit_when_older_posts(posts):
        if posts:
            oldest_post_time = posts[-1]['date']
            return oldest_post_time < until_date
    def filter_older_posts(posts):
        return [post for post in posts if post['date'] >= until_date]
    posts = non_paginated_post_fetcher(fetcher, key, quit_when_older_posts, filter_duplicates, **params)
    return filter_older_posts(posts)

@get('/blog')
def blog_search():
    blog_page = ('/blog/' + request.query.blog) if request.query.blog else '/'
    return redirect(blog_page)

@get('/b/<blog>')
@get('/blog/<blog>')
@view('templates/main')
def blog_view(blog):
    client = tumblr_client()
    num_posts = requested_posts()
    since_date = requested_date()
    params = {}
    if request.query.ptype:
        params['type'] = request.query.ptype
    try:
        if since_date:
            posts = get_posts_since_date(partial(client.posts, blog), 'posts', since_date, **params)
        else:
            posts = get_n_posts(partial(client.posts, blog), 'posts', num_posts, **params)
    except BlogNotFoundException:
        return template_dict(page_title='Blog %s not found' % blog)
    posts = sort_posts_by(posts, request.query.sort)
    blog_info = client.blog_info(blog)
    return template_dict(posts=posts,
                         title=blog_info['blog']['name'],
                         subtitle=blog_info['blog']['title'],
                         avatar_url=client.avatar(blog)['avatar_url'])

def requested_posts():
    if not request or not request.query.limit.isdigit():
        return 20
    return int(request.query.limit)

def requested_date():
    if request and request.query.date:
        try:
            return datetime.fromtimestamp(int(request.query.date))
        except Exception, e:
            print 'Could not get from timestamp %s: ' % request.query.date
            print e

@get('/likes')
@view('templates/main')
def likes_view():
    params = {}
    if request.query.ptype:
        params['type'] = request.query.ptype
    if authenticated():
        num_posts = requested_posts()
        liked_posts = get_n_posts(tumblr_client().likes, 'liked_posts', num_posts, **params)
        posts = sort_posts_by(liked_posts, request.query.sort)
        page_title = 'Likes'
    else:
        posts = None
        page_title = 'Welcome, Guest!'
    return template_dict(posts=posts, page_title=page_title)

@get('/')
@view('templates/main')
def dashboard_view():
    params = {}
    if request.query.ptype:
        params['type'] = request.query.ptype
    if authenticated():
        num_posts = requested_posts()
        dashboard_posts = get_n_posts(tumblr_client().dashboard, 'posts', num_posts, **params)
        posts = sort_posts_by(dashboard_posts, request.query.sort)
        page_title = 'Dashboard'
    else:
        posts = None
        page_title = 'Welcome, Guest!'
    return template_dict(posts=posts, page_title=page_title)

@get('/static/<sfile:re:.+>')
def get_static(sfile):
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    return static_file(sfile, root=root)

@get('/templates/<tfile>')
def get_template(tfile):
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
    return static_file(tfile, root=root)

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


pages = [
    {'name': 'Dashboard', 'url': '/'},
    {'name': 'Likes', 'url': '/likes'},
]
TEMPLATE_PATH.append(os.path.dirname(os.path.realpath(__file__)))

if __name__ == "__main__":
    run(host='localhost', port=8080, reloader=True)
