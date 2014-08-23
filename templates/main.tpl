<html>
    <head>
        <title>rTumblr</title>
        <link rel="stylesheet" href="/static/css/theme_switcher.css">
        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js"></script>
        <script src="/static/js/mustache.js"></script>
        <script src="/static/js/cookies.min.js"></script>
        <script>
        function htmlDecode(input){
            var e = document.createElement('div');
            e.innerHTML = input;
            return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue;
        };

        function getParameters() {
            %import json
            decoded = htmlDecode('{{json.dumps(parameters)}}');
            parameters = JSON.parse(decoded);
            parameters.numPosts = parameters.posts ? parameters.posts.length : 0
            return parameters;
        };

        jQuery.ajaxSetup({async:false});

        function switchTemplate(template_name) {
            $.get('/templates/' + template_name + '.mst', function(template) {
                var rendered = Mustache.render(template, getParameters());
                $('#target').html(rendered);
                Cookies.set('template', template_name)
            });
        };

        function switchToLatestTemplate() {
            switchTemplate(Cookies.get('template') || 'default')
        }
        </script>
    </head>
    <body onLoad="switchToLatestTemplate()">
        <div id="themeSwitcher">
            <ul id="nav">
                <li>
                    <a href="#"><img src="/static/img/paint.png"></a>
                    <ul>
                        <li><a onClick="switchTemplate('default')">default</a></li>
                        <li><a onClick="switchTemplate('reddit')">reddit</a></li>
                        <li><a onClick="switchTemplate('simple')">simple</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    <div id="target"></div>
    </body>
</html>
