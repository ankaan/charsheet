<!DOCTYPE html>
<%!
    from charsheet.views import resource_path
    from charsheet.models import crumbs
    from charsheet.models import crumbs_string
    from charsheet.models import userlist
    from charsheet.models import partylist
%>

<%def name="navlink(title,resource)">
    % if resource is not None and request.has_permission('view',resource):
        <li class="${request.context == resource and 'active' or ''}">
            <a href="${resource_path(resource)}">${title}</a>
        </li>
    % endif
</%def>

<html lang="${request.locale_name}">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Nianze character sheet manager">
        <meta name="author" content="Anders Engstr&ouml;m">

        <title><%block name="title">${crumbs_string(request.context)} :: Nianze character sheet manager</%block></title>

        <link rel="stylesheet" type="text/css" media="screen" charset="utf-8"
            href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">

        <link rel="stylesheet" type="text/css" media="screen" charset="utf-8"
            href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css">

        % for css in context.get('css_resources', []):
            <link rel="stylesheet" type="text/css" media="screen" href="${request.static_url(css)}">
        % endfor

        <link rel="stylesheet" href="${request.static_url('charsheet:static/charsheet.css')}">

        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
        <script src="//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>
        <script src="${request.static_url('deform:static/scripts/deform.js')}"></script>

        % for js in context.get('js_resources', []):
            <script type="text/javascript" src="${request.static_url(js)}"></script>
        % endfor

    </head>

    <body>
        <nav class="navbar navbar-inverse" role="navigation">
            <div class="container">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#page-navbar-collapse">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="${resource_path(request.root)}">Nianze Charsheet</a>
                </div>

                <div class="navbar-collapse collapse" id="page-navbar-collapse">
                    <ul class="nav navbar-nav">
                        ${navlink('Party List',partylist)}
                        ${navlink('User List',userlist)}
                        ${navlink('Profile',request.user)}
                    </ul>
                    <ul class="nav navbar-nav navbar-right">
                        <li>
                            % if request.authenticated_userid:
                                <a id="signout" href="#signout">Sign out</a>
                            % else:
                                <a id="signin" href="#signin"><img alt='Sign in'
                                         src='https://login.persona.org/i/sign_in_blue.png'
                                         /></a>
                            % endif
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="location">
            <div class="container">
                <ol class="breadcrumb">
                    % for resource in crumbs(request.context):
                        <li>
                            <a href="${resource_path(resource)}">
                                ${resource.__crumbs_name__}
                            </a>
                        </li>
                    % endfor
                </ol>
            </div>
        </div>


        <div class="container">
            <div class="flash-messages">
                % for queue in ['', 'success', 'info', 'warning', 'danger']:
                    % for message in request.session.pop_flash(queue):
                    <div class="alert alert-${ queue and queue or 'info' }">
                            <button type="button" class="close" data-dismiss="alert">&times;</button>
                            ${message}
                        </div>
                    % endfor
                % endfor
            </div>
        </div>

        <div class="content">
            <%block name="content"></%block>
        </div>

        <div class="container footer">
            <div class="right">
                <a href="https://github.com/ankaan/charsheet">Source @ GitHub</a>
            </div>
            <div class="left">
                <p>© Anders Engstr&ouml;m</p>
            </div>
        </div>

        <script src="https://login.persona.org/include.js" type="text/javascript"></script>
        <script type="text/javascript">${request.persona_js}</script>
    </body>
</html>
