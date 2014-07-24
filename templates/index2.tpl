<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="A layout example that shows off a blog page with a list of posts.">

    <title>rTumblr</title>

    


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
  




    

    

    

</head>
<body>

%setdefault('title', '')
%setdefault('subtitle', '')
%setdefault('avatar_url', 'http://assets.tumblr.com/images/favicons/favicon.ico')
%setdefault('pages', {})
%setdefault('username', '')
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
                %for page, url in pages.iteritems():
                    <li class="nav-item">
                        <a class="pure-button" href="{{url}}">{{page}}</a>
                    </li>
                %end
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
                    <header class="post-header">
                        <img class="post-avatar" alt="Tilo Mitra&#x27;s avatar" height="48" width="48" src="{{avatar_url}}">
                        <h2 class="post-title">{{title}}</h2>
                        %if subtitle:
                            <small>{{subtitle}}</small>
                        %end
                    </header>

                    <div class="post-description">
                        <p>
                        <table class="pure-table pure-table-bordered">
                            <thead>
                                <tr>
                                    <th>Blog</th>
                                    <th>Link</th>
                                    <th>Type</th>
                                    <th><a href="?sort=up">Notes</th>
                                </tr>
                            </thead>

                            <tbody>
                            %for post in posts:
                                <tr>
                                    <th><a href="/blog/{{post['blog']}}">{{post['blog']}}</a></th>
                                    <th><a href="{{post['link']}}">{{post['link']}}</a></th>
                                    <th>{{post['type']}}</th>
                                    <th>{{post['notes']}}</th>
                                </tr>
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
                        <li><a href="http://purecss.io/">About</a></li>
                        <li><a href="http://twitter.com/yuilibrary/">Twitter</a></li>
                        <li><a href="http://github.com/yui/pure/">GitHub</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>






</body>
</html>
