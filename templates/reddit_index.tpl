<!doctype html>
<html>
   <head>
      <title>reddit: the front page of the internet</title>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <meta name="viewport" content="width=1024">
      <link rel="stylesheet" type="text/css" href="/static/css/reddit.Wf_VWenEr9c.css" media="all">
      <!--[if gte IE 8]><!-->
      <link rel="stylesheet" href="http://b.thumbs.redditmedia.com/QcbYZ7Vd3nhIv7NA.css" title="applied_subreddit_stylesheet" type="text/css">
   </head>
   <body class="listing-page hot-page front-page" >
      <div id="header" role="banner">
         <div id="sr-header-area">
            <div class="width-clip">
               <div class="dropdown srdrop" onclick="open_menu(this)" onmouseover="hover_open_menu(this)"><span class="selected title">my subreddits</span></div>
               <div class="drop-choices srdrop"><a href="http://www.reddit.com/r/announcements/" class="choice" >announcements</a><a href="http://www.reddit.com/subreddits/" class="bottom-option choice" >edit subscriptions</a></div>
               <div class="sr-list">
                  <ul class="flat-list sr-bar hover" >
                     <li class='selected'><a href="/" class="choice" >Dashboard</a></li>
                     <li ><span class="separator">-</span><a href="http://www.reddit.com/r/all" class="choice" >all</a></li>
                     <li ><span class="separator">-</span><a href="http://www.reddit.com/r/random/" class="random choice" >random</a></li>
                  </ul>
                  <span class="separator">&nbsp;|&nbsp;</span>
                  <ul class="flat-list sr-bar hover" id='sr-bar'>
                     <li ><a href="http://www.reddit.com/r/mildlyinteresting/" class="choice" >mildlyinteresting</a></li>
                  </ul>
               </div>
               <a href="http://www.reddit.com/subreddits/" id="sr-more-link" >more &raquo;</a>
            </div>
         </div>
         <div id="header-bottom-left">
            <a href="/" id="header-img" class="default-header" title="">reddit.com</a>&nbsp;
            <ul class="tabmenu " >
               <li class='selected'><a href="/hot" class="choice" >hot</a></li>
               <li ><a href="/" class="choice" >new</a></li>
               <li ><a href="/?sort=up" class="choice" >top</a></li>
            </ul>
         </div>
         <div id="header-bottom-right">
            <span class="user">want to join?&#32;<a href="/login" >login or register</a>&#32;in seconds</span>
         </div>
      </div>
      <div class="side">
         <div class='spacer'>
            <form action="http://www.reddit.com/search" id="search" role="search">
               <input type="text" name="q" placeholder="go to blog" />
            </form>
         </div>
      </div>
      <a name="content"></a>
      <div class="content" role="main">
         <div class='spacer'>
            <style>body >.content .link .rank, .rank-spacer { width: 2.2ex } body >.content .link .midcol, .midcol-spacer { width: 5.1ex }</style>
            <div id="siteTable" class="sitetable linklisting">
               %for i, post in enumerate(posts or [], start=1):
               <div class=" thing odd&#32; link "  ="click_thing(this)" >
                  <p class="parent"></p>
                  <span class="rank">{{i}}</span>
                  <div class="midcol unvoted" >
                     <div class="arrow up login-required" aria-label="upvote" tabindex="0" ></div>
                     <div class="score">{{post['notes']}}</div>
                     <div class="arrow down login-required" aria-label="downvote" tabindex="0" ></div>
                  </div>
                  <a class="thumbnail may-blank " href="{{post['link']}}" ><img src="http://a.thumbs.redditmedia.com/QgOaqfquGJsRqIjZ.jpg" width='70' height='70' alt=""></a>
                  <div class="entry unvoted">
                     <p class="title"><a class="title may-blank " href="{{post['link']}}" tabindex="1" >{{'Post #%s: %s' % (i, post.get('title', 'Untitled'))}}</a>&#32;<span class="domain">(<a href="#">tumblr.com</a>)</span></p>
                     <p class="tagline">submitted {{4+i}} hours ago to <a href="/blog/{{post['blog']}}" class="subreddit hover may-blank" >/r/{{post['blog']}}</a></p>
                     <ul class="flat-list buttons">
                        <li class="first"><a href="#" class="comments may-blank" >{{post['notes']}} notes</a></li>
                     </ul>
                  </div>
                  <div class="child" ></div>
                  <div class="clearleft"></div>
               </div>
               <div class="clearleft"></div>
               %end
               <div class="nav-buttons"><span class="nextprev">view more:&#32;<a href="http://www.reddit.com/?count=25&amp;after=t3_2brz5k" rel="nofollow next" >next &rsaquo;</a></span><span class="next-suggestions">or try a&#32;<a href="http://www.reddit.com/r/random" >random subreddit</a></span></div>
            </div>
         </div>
      </div>
   </body>
</html>