<html>
    <head>
        <title>rTumblr</title>
        <link rel="stylesheet" href="/static/css/theme_switcher.css">
        <script src="http://code.jquery.com/jquery-latest.min.js"></script>
        <script src="/static/js/mustache.js"></script>
        <script src="/static/js/cookies.min.js"></script>
        <script src="/static/js/moment-with-locales.min.js"></script>
        <script>
        // Helper methods for Mustache templates
        function formattedTimeSincePost(formatStr, _) {
            // TODO: Allow custom format
            return moment.unix(this.date).fromNow();
        };
        function formattedPostDate(formatStr, _) {
            return moment.unix(this.date).format(formatStr);
        };

        function getHelperFunctions() {
            helpers = []
            helpers.formattedPostDate = function() {return formattedPostDate; };
            helpers.formattedTimeSincePost = function() {return formattedTimeSincePost; };
            return helpers;
        };

        function htmlDecode(input){
            var e = document.createElement('div');
            e.innerHTML = input;
            return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue;
        };

        cachedParameters = null;
        function getParameters() {
            if (cachedParameters) {
                return cachedParameters;
            }
            %import json
            decoded = htmlDecode('{{json.dumps(parameters)}}');
            parameters = JSON.parse(decoded);
            parameters.numPosts = parameters.posts ? parameters.posts.length : 0;
            jQuery.extend(parameters, getHelperFunctions());
            cachedParameters = parameters;
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
                        <li><a onClick="switchTemplate('gallery')">gallery</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    <div id="target"></div>
    </body>
</html>
