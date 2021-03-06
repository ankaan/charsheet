<%inherit file="base.mako"/>
<%!
    from charsheet.views import resource_path
%>

<%namespace name="pagination" file="pagination.mako"/>

<%def name="bar(location)">
    % if paginator.page_count > 1:
        <nav class="navbar navbar-default" role="navigation">
            <div class="navbar-header">
                ${pagination.render(paginator)}
            </div>
        </nav>
    % endif
</%def>

<%block name="content">
    <div class="container">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h1>User List</h1>
            </div>

            ${bar('top')}

            <table class="table table-hover linklist">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                    </tr>
                </thead>
                <tbody>
                    % for u in paginator.items:
                        <tr>
                            % if request.has_permission('edit',u):
                                <td><a href="${resource_path(u)}">${u.name}</a></td>
                                <td><a href="${resource_path(u)}">${u.email}</a></td>
                            % else:
                                <td colspan="2"><a href="${resource_path(u)}">${u.name}</a></td>
                            % endif
                        </tr>
                    % endfor
                </tbody>
            </table>

            ${bar('bottom')}
        </div>
    </div>
</%block>
