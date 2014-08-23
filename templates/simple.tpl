<html>
<link rel="stylesheet" href="http://yui.yahooapis.com/pure/0.5.0/pure-min.css">
<style>
    div.container {
        margin: 10px;
        background-color:Gray;
        -moz-border-radius: 15px;
        border-radius: 10px;
        padding: 10px;
    }
</style>

<head>
    <title>rTumblr</title>
</head>
%setdefault('title', '')
%setdefault('page_title', title)
%setdefault('subtitle', '')
%setdefault('avatar_url', 'http://assets.tumblr.com/images/favicons/favicon.ico')
%setdefault('pages', {})
%setdefault('limit', 20)
%setdefault('username', '')
%setdefault('posts', None)
%loggedin = bool(username)

<body>
<div class="container">
    <p><b>{{page_title}}:</b> <i>{{subtitle}}</i></p>
    <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>Blog</th>
                <th>Link</th>
                <th>Type</th>
                <th>Notes</th>
            </tr>
        </thead>

        <tbody>
        %for post in posts:
            <tr>
                <th>{{post['blog']}}</th>
                <th><a href="{{post['link']}}">{{post['link']}}</a></th>
                <th>{{post['type']}}</th>
                <th>{{post['notes']}}</th>
            </tr>
        %end
        </tbody>
    </table>
</div>

</body>
</html>