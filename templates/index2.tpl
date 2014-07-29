<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="A layout example that shows off a blog page with a list of posts.">

    <title>rTumblr</title>

    
<script src="/static/js/sorttable.js"></script>

<link rel="stylesheet" href="http://yui.yahooapis.com/pure/0.5.0/pure-min.css">



<!--[if lte IE 8]>
  
    <link rel="stylesheet" href="http://yui.yahooapis.com/pure/0.5.0/grids-responsive-old-ie-min.css">
  
<![endif]-->
<!--[if gt IE 8]><!-->
  
    <link rel="stylesheet" href="http://yui.yahooapis.com/pure/0.5.0/grids-responsive-min.css">
  
<!--<![endif]-->



  
    <!--[if lte IE 8]>
        <link rel="stylesheet" href="/static/css/layouts/blog-old-ie.css">
    <![endif]-->
    <!--[if gt IE 8]><!-->
        <link rel="stylesheet" href="/static/css/layouts/blog.css">
    <!--<![endif]-->
    <link rel="stylesheet" href="/static/css/general.css">
  




    

    

    

</head>
<body>

%setdefault('title', '')
%setdefault('page_title', title)
%setdefault('subtitle', '')
%setdefault('avatar_url', 'http://assets.tumblr.com/images/favicons/favicon.ico')
%setdefault('pages', {})
%setdefault('limit', 20)
%setdefault('username', '')
%setdefault('posts', None)
%loggedin = bool(username)
<div id="layout" class="pure-g">
    <div class="sidebar pure-u-1 pure-u-md-1-4">
        <div class="header">
            <hgroup>
                <h1 class="brand-title">rTumblr</h1>
                <h2 class="brand-tagline">tumblr but better!</h2>
            </hgroup>

            <nav class="nav">
                <ul class="nav-list">
                    <li class="nav-item">
                    %if loggedin:
                        <a class="pure-button" href="/logout">Logout {{username}}</a>
                    %else:
                        <a class="pure-button" href="/login">Login</a>
                    %end
                    </li>
                <br>
                %if loggedin:
                    %for page, url in pages.iteritems():
                        <li class="nav-item">
                            <a class="pure-button" href="{{url}}">{{page}}</a>
                        </li>
                    %end
                %end
                <br>
                <br>
                <form class="post-avatar pure-form" method="get" action="/blog">
                    <input type="text" class="pure-input-rounded" name="blog", placeholder="{{title or 'Search blogs...'}}" size="15">
                    <button type="submit" class="pure-button" style="display: none;">
                </form>

                </ul>
            </nav>
        </div>
    </div>

    <div class="content pure-u-1 pure-u-md-3-4">

        <div>
            <!-- A wrapper for all the blog posts -->
            <div class="posts">
                <!-- A single blog post -->
                <section class="post">
                    <div class="woo" style="display: inline-block; width: 100%; height: 48px">
                        <img class="post-avatar" height="48" width="48" src="{{avatar_url}}">
                        <form class="post-avatar pure-form" method="get">
                            <input type="text" class="pure-input-rounded" name="limit", placeholder="{{limit}}" size="1">
                            <button type="submit" class="pure-button" style="display: none;">Search</button>
                        </form>

                        <h2 class="post-title" style="display:table-cell;">{{page_title}}</h2>
                        %if subtitle:
                            <small>{{subtitle}}</small>
                        %end
                    </div>

                    <div class="post-description">
                        <p>
                        %if posts:
                            <table id="post-table" class="pure-table pure-table-bordered sortable" style="width: 100%; text-align: left;">
                                <thead>
                                    <tr>
                                        <th>Blog</th>
                                        <th style="width: 70%">Link</th>
                                        <th style="width: 30%">Type</th>
                                        <th>Notes</th>
                                    </tr>
                                </thead>

                                <tbody>
                                %for i, post in enumerate(posts, start=1):
                                    <tr>
                                        <th><a href="/blog/{{post['blog']}}">{{post['blog']}}</a></th>
                                        %post_title = 'Post #%s: %s' % (i, post.get('title', 'Untitled'))
                                        <th><a href="{{post['link']}}">{{post_title}}</a></th>
                                        <th>{{post['type']}}</th>
                                        <th>{{post['notes']}}</th>
                                    </tr>
                                %end
                        %elif type(posts) == type(list()) and len(posts) == 0:
                            <p>Empty!</p>
                        %end
                                </tbody>
                            </table>
                        </p>
                    </div>
                </section>
            </div>

            <div class="footer">
                <div class="pure-menu pure-menu-horizontal pure-menu-open">
                    <ul>
                        <li><a href="http://github.com/johannes-keinestam/rtumblr">GitHub</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>






</body>
</html>
