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

        <title><%block name="title">${crumbs_string(request.context)} :: Nianze character sheet manager</%block></title>

        % for css in context.get('css_resources', []):
            <link rel="stylesheet" type="text/css" media="screen" href="${request.static_url(css)}">
        % endfor


        <link rel="stylesheet" type="text/css" media="screen" charset="utf-8"
            href="${request.static_url('deform:static/css/bootstrap.min.css')}" />
        <link rel="stylesheet" type="text/css" media="screen" charset="utf-8"
            href="${request.static_url('deform_bootstrap:static/deform_bootstrap.css')}" />

        <link rel="stylesheet" href="${request.static_url('charsheet:static/theme.css')}">

        <!-- Le javascript, which unfortunately has to be at the top for Deform to work -->
        <script src="${request.static_url('deform:static/scripts/jquery-2.0.3.min.js')}"></script>
        <script src="${request.static_url('deform:static/scripts/deform.js')}"></script>

        % for js in context.get('js_resources', []):
            <script type="text/javascript" src="${request.static_url(js)}"></script>
        % endfor

        <script src="${request.static_url('deform_bootstrap:static/deform_bootstrap.js')}"></script>
        <script src="${request.static_url('deform_bootstrap:static/bootstrap.min.js')}"></script>
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

        <div class="container">
            <div class="flash-messages">
                % for queue in ['', 'success', 'info', 'error']:
                    % for message in request.session.pop_flash(queue):
                    <div class="alert ${ 'alert-'+queue if queue != '' else '' }">
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

        <script src="https://login.persona.org/include.js" type="text/javascript"></script>
        <script type="text/javascript">${request.persona_js}</script>
    </body>
</html>
