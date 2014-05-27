<%inherit file="base.mako"/>
<%!
    from charsheet.views import resource_path
%>

<%block name="content">
    <div class="container">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h1>Character List</h1>
            </div>

            <table class="table table-hover linklist">
                <thead>
                    <tr>
                        <th>Name</th>
                    </tr>
                </thead>
                <tbody>
                    % for c in charlist:
                        <tr>
                            <td><a href="${resource_path(c)}">${c.name}</a></td>
                        </tr>
                    % endfor
                </tbody>
            </table>
        </div>
    </div>
</%block>
