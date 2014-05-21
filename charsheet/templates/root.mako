<%inherit file="base.mako"/>
<%!
    from charsheet.views import resource_path
    from charsheet.models import userlist
    from charsheet.models import partylist
%>

<%def name="trlink(title,resource)">
    % if resource is not None and request.has_permission('view',resource):
        <tr><td><a href="${resource_path(resource)}">${title}</a></td></tr>
    % endif
</%def>

<%block name="content">
    <div class="container">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h1>Nianze character sheet manager</h1>
            </div>
            <table class="table table-hover linklist">
                <tbody>
                    ${trlink('Party List', partylist)}
                    ${trlink('User List', userlist)}
                    ${trlink('Profile', request.user)}
                </tbody>
            </table>
        </div>
    </div>
</%block>
