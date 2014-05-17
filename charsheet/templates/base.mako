<!DOCTYPE html>
<%!
    from charsheet.views import resource_path
    from charsheet.models import (crumbs, crumbs_string)
%>

<html lang="${request.locale_name}">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Nianze character sheet manager">
        <meta name="author" content="Anders Engstr&ouml;m">
        ##<link rel="shortcut icon" href="${request.static_url('charsheet:static/pyramid-16x16.png')}">

        <title><%block name="title">${crumbs_string(request.context)} :: Nianze character sheet manager</%block></title>

        <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
        <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css">
        <link rel="stylesheet" href="${request.static_url('deform:static/css/form.css')}">
        <link rel="stylesheet" href="${request.static_url('charsheet:static/theme.css')}">


        <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
        <!--[if lt IE 9]>
        <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
        <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
        <![endif]-->
    </head>

    <body>
        <div class="bar">
            <div class="crumbs">
                % for resource in crumbs(request.context):
                    <a href="${resource_path(resource)}">${resource.__crumbs_name__}</a> /
                % endfor
            </div>
            <div class="persona">
                % if not request.authenticated_userid:
                    <img src='https://login.persona.org/i/sign_in_blue.png' id='signin' alt='sign-in button'/>
                % else:
                    <a id='signout' href="#signout">Sign out</a>
                % endif
            </div>
        </div>

        <div class="content">
            <%block name="content"></%block>
        </div>

        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
        <script src="//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>

        <script src="https://login.persona.org/include.js" type="text/javascript"></script>
        <script type="text/javascript">${request.persona_js}</script>

        <script src="${request.static_url('deform:static/script/deform.js')}"></script>
    </body>
</html>
