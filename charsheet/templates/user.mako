<%inherit file="base.mako"/>
<%!
    from charsheet.views import resource_path
%>

<%block name="content">
    <h1>User Profile</h1>
    <table class="table table-hover profile linklist">
        <tr><th>Name</th><td>${request.context.name}</td></tr>
        % if request.has_permission('edit',request.context):
            <tr><th>Email</th><td><a href="mailto:${request.context.email}">${request.context.email}</a></td></tr>
        % endif
        % if request.has_permission('admin',request.context):
            <tr><th>Admin</th><td>${request.context.admin}</td></tr>
            <tr><th>Active admin</th><td>${request.context.active_admin}</td></tr>
        % endif
        % if request.has_permission('edit',request.context):
            <tr>
                <td><a href="${resource_path(request.context,'@@edit')}">Edit</a></td>
                <td><a href="${resource_path(request.context,'@@edit')}" class="stealth">&nbsp;</a></td>
            </tr>
        % endif
    </table>
</%block>
