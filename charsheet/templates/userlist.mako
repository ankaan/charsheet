<%inherit file="base.mako"/>
<%!
    from charsheet.views import resource_path
%>

<%block name="content">
    <div class="container">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h1>User List</h1>
            </div>
            % if paginator.page_count > 1:
                <div class="panel-heading">
                    <%block name="pagenav">
                        <ul class="pagination pagination-sm">
                            <%
                                p = paginator
                                explicit = 5

                                low_lim = p.first_page+1
                                high_lim = max(low_lim, p.last_page-explicit)
                                start = min(max(low_lim, p.page - explicit/2), high_lim)
                                stop = min(start+explicit, p.last_page)
                            %>
                            % if p.page > p.first_page:
                                <li><a href="?page=${p.first_page}">&lt;&lt;</a></li>
                                <li><a href="?page=${p.page-1}">&lt; Previous</a></li>
                            % else:
                                <li class="disabled"><span>&lt;&lt;</span></li>
                                <li class="disabled"><span>&lt; Previous</span></li>
                            % endif

                            % if p.page == p.first_page:
                                <li class="active"><span>${p.first_page} <span class="sr-only">(current)</span><span></li>
                            % elif start == p.first_page+1:
                                <li><a href="?page=${p.first_page}">${p.first_page}</a></li>
                            % else:
                                <li class="disabled"><span>...<span></li>
                            % endif

                            % for n in range(start, stop):
                                % if n == p.page:
                                    <li class="active"><span>${n} <span class="sr-only">(current)</span><span></li>
                                % else:
                                    <li><a href="?page=${n}">${n}</a></li>
                                % endif
                            % endfor
                            
                            % if p.page_count <= 1:
                                <li></li>
                            % elif p.page == p.last_page:
                                <li class="active"><span>${p.last_page} <span class="sr-only">(current)</span><span></li>
                            % elif start+explicit >= p.last_page:
                                <li><a href="?page=${p.last_page}">${p.last_page}</a></li>
                            % else:
                                <li class="disabled"><span>...<span></li>
                            % endif

                            % if p.page < p.last_page:
                                <li><a href="?page=${p.page+1}">Next &gt;</a></li>
                                <li class="wide"><a href="?page=${p.last_page}">&gt;&gt;</a></li>
                            % else:
                                <li class="disabled"><span>Next &gt;</span></li>
                                <li class="disabled wide"><span>&gt;&gt;</span></li>
                            % endif
                        </ul>
                    </%block>
                </div>
            % endif

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

            % if paginator.page_count > 1:
                <div class="panel-footer">
                    ${pagenav()}
                </div>
            % endif
        </div>
    </div>
</%block>
