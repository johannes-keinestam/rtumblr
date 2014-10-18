import os
import random
from pytumblr import TumblrRestClient
from bottle import get, request, run, view, TEMPLATE_PATH, static_file, redirect, template, response
from functools import partial
from oauth_login import OAuthLogin
from datetime import datetime, timedelta

try:
    import settings
    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET
except Exception, e:
    raise Exception("rTumblr not set up: settings.py is missing." + str(e))

pending_logins = {}

class BlogNotFoundException(Exception):
    pass

def response_to_posts(post_response, sort=False):
    posts = []
    for index, post in enumerate(post_response, start=1):
        post_info = {
            'id': str(post.get('id')),
            'blog':  post.get('blog_name'),
            'type':  post.get('type'),
            'album':  False,
            'notes': post.get('note_count', -1),
            'post_url':  post.get('post_url'),
            'date': post['timestamp'],
            'title': post.get('title') or str(post.get('id')),
            'index': index,
        }
        if post.get('type') == 'photo':
            post_info['photo'] = post['photos'][0]['original_size']['url']
            photo_format = post_info['photo'][-3:].lower()
            if photo_format == 'gif':
                post_info['type'] += ' (gif)'
            if len(post['photos']) > 1:
                post_info['album'] = True
                post_info['type'] += ' album'
        if post.get('type') == 'video':
            post_info['video'] = {
                'url': post.get('video_url', post.get('post_url')),
                'thumbnail': post.get('thumbnail_url', '/static/img/blank.png')
            }
        posts.append(post_info)
    return posts

def sort_posts_by(posts, sort=False, key='notes'):
    if sort and sort != 'no':
        sorted_posts = sorted(posts, key=lambda p: p[key], reverse=sort!='down')
        for index, post in enumerate(sorted_posts, start=1):
            post['index'] = index
        return sorted_posts
    else:
        return posts

def followed_blogs():
    client = tumblr_client()
    following_response = client.following()
    total_followed_blogs = following_response['total_blogs']
    fetched_blogs = following_response['blogs']
    while total_followed_blogs > len(fetched_blogs):
        following_response = client.following(offset=len(fetched_blogs))
        fetched_blogs += following_response['blogs']
    return fetched_blogs

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
            oldest_post_time = datetime.fromtimestamp(posts[-1]['date'])
            return oldest_post_time < until_date
    def filter_older_posts(posts):
        return [post for post in posts if datetime.fromtimestamp(post['date']) >= until_date]
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
@get('/dashboard')
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

@get('/hot')
@view('templates/main')
def get_hot():
    hot_since = datetime.now() - timedelta(days=1)
    client = tumblr_client()
    params = {}
    if request.query.ptype:
        params['type'] = request.query.ptype
    posts = []
    updated_followed_blogs = [blog for blog in followed_blogs() if datetime.fromtimestamp(blog['updated']) >= hot_since]
    for blog in random.sample(updated_followed_blogs, min(len(updated_followed_blogs), 5)):
        blog_name = blog['name']
        blog_posts = get_posts_since_date(partial(client.posts, blog_name), 'posts', hot_since, **params)
        blog_average_notes = 0 if not blog_posts else sum([p['notes'] for p in blog_posts]) / len(blog_posts)
        print '%s: fetched %s posts (avg notes: %s)' % (blog_name, len(blog_posts), blog_average_notes)
        for post in blog_posts:
            post['weighted_notes'] = float(post['notes']) / blog_average_notes
        posts += blog_posts
    posts = sort_posts_by(posts, request.query.sort or True, key='weighted_notes')
    return template_dict(posts=posts, title='Hot')

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
    {'name': 'Hot', 'url': '/hot'},
]
TEMPLATE_PATH.append(os.path.dirname(os.path.realpath(__file__)))

if __name__ == "__main__":
    run(host='localhost', port=8080, reloader=True)
