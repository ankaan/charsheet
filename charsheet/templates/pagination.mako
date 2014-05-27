<%!
    from charsheet.pagination import PrettyPager
%>

<%def name="render(paginator)">
    <%
        prettypager = PrettyPager(paginator,explicit=5)
    %>
    <ul class="pagination ${prettypager.css_class}">
        % for link in prettypager.links():
            % if link.active:
                <li class="active">
                    <span>${link.name} <span class="sr-only">(current)</span></span>
                </li>
            % elif link.disabled:
                <li class="disabled ${'hidden-xs' if link.collapse else ''}"><span>${link.name}<span></li>
            % elif link.collapse:
                <li class="hidden-xs"><a href="${link.url}">${link.name}</a></li>
            % else:
                <li><a href="${link.url}">${link.name}</a></li>
            % endif
        % endfor
    </ul>
</%def>
