<html>
<link rel="stylesheet" href="http://yui.yahooapis.com/pure/0.5.0/pure-min.css">
<style>
    div.container {
        margin: 10px;
        background-color:Black;
        -moz-border-radius: 15px;
        border-radius: 10px;
        padding: 10px;
    }
</style>

<head>
    <title>rTumblr</title>
</head>

<body>
<div class="container">
    %if blog_info:
    <p><b>{{blog_info['name']}}:</b> <i>{{blog_info['title']}}</i></p>
    %end
    <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>Blog</th>
                <th>Link</th>
                <th>Type</th>
                <th>Likes</th>
                <th>Notes</th>
            </tr>
        </thead>

        <tbody>
        %for post in posts:
            <tr>
                <th>{{post['blog']}}</th>
                <th><a href="{{post['link']}}">{{post['link']}}</a></th>
                <th>{{post['type']}}</th>
                <th>{{post['likes']}}</th>
                <th>{{post['notes']}}</th>
            </tr>
        %end
        </tbody>
    </table>
</div>

</body>
</html>