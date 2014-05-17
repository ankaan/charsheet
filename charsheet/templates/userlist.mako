<%inherit file="base.mako"/>
<%!
    from charsheet.views import (resource_path, pager)
%>

<%block name="content">
    <h1>User List</h1>

    <%block name="pagenav">
        <div class="pagenav">
            ${pager(paginator)}
        </div>
    </%block>

    <table class="table table-hover linklist">
        <tr>
            <th>Name</th>
            <th>Email</th>
        </tr>
        % for u in paginator.items:
            <tr>
                <td><a href="${resource_path(u)}">${u.name}</a></td>
                % if request.has_permission('edit',u):
                    <td><a href="${resource_path(u)}">${u.email}</a></td>
                % else:
                    <td><a href="${resource_path(u)}" class="stealth">&nbsp;</a></td>
                % endif
            </tr>
        % endfor
    </table>

    ${pagenav()}

</%block>
