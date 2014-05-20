<%inherit file="base.mako"/>
<%!
    from charsheet.views import resource_path
%>

<%block name="content">
    <div class="container">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h1>User Profile</h1>
            </div>
            <table class="table table-hover profile linklist">
                <tbody>
                    <tr><th>Name</th><td>${request.context.name}</td></tr>
                    % if request.has_permission('edit',request.context):
                        <tr><th>Email</th><td><a href="mailto:${request.context.email}">${request.context.email}</a></td></tr>
                    % endif
                    % if request.has_permission('admin',request.context):
                        <tr><th>Admin</th><td>${request.context.admin}</td></tr>
                        <tr><th>Active admin</th><td>${request.context.active_admin}</td></tr>
                    % endif
                </tbody>
            </table>
            % if request.has_permission('edit',request.context):
                <div class="panel-footer">
                    <a href="${resource_path(request.context,'@@edit')}" class="btn btn-default" role="button">Edit</a>
                </div>
            % endif
        </div>
    </div>
</%block>
