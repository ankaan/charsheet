<%inherit file="base.mako"/>
<%!
    from charsheet.views import resource_path
    from charsheet.models import userlist
%>

<%def name="trlink(title,resource)">
    % if resource is not None and request.has_permission('view',resource):
        <tr><td><a href="${resource_path(resource)}">${title}</a></td></tr>
    % endif
</%def>

<%block name="content">
    <h1>Nianze character sheet manager</h1>
    <table class="table table-hover linklist">
        ${trlink('Profile', request.user)}
        ${trlink('User List', userlist)}
    </table>
</%block>
