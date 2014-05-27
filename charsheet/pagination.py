class PrettyPager(object):
    def __init__(
            self,
            paginator,
            explicit=5,
            get_param='page',
            name_first=None,
            name_last=None,
            name_previous="< Previous",
            name_next="Next >",
            name_disabled="...",
            css_class="pagination-sm",
            ):
        self.paginator = paginator
        self.get_param = get_param
        self.explicit = explicit
        self.name_first = name_first
        self.name_last = name_last
        self.name_previous = name_previous
        self.name_next = name_next
        self.name_disabled = name_disabled
        self.css_class = css_class

    def links(self):
        p = self.paginator
        explicit = self.explicit

        low_lim = p.first_page+2
        high_lim = max(low_lim, p.last_page-1-explicit)
        start = min(max(low_lim, p.page - explicit/2), high_lim)
        stop = min(start+explicit, p.last_page-1)

        if self.name_first:
            yield self._mklink(p.first_page, self.name_first, disabled=(p.page == p.first_page))
        if self.name_previous:
            yield self._mklink(p.page-1, self.name_previous, disabled=(p.page == p.first_page))

        # First page is always present.
        yield self._mklink(p.first_page, active=(p.page == p.first_page))

        # Page 2 or disabled.
        if p.page_count <= 2:
            pass
        elif start > p.first_page+2:
            yield self._mklink(p.first_page+1, self.name_disabled, disabled=True, collapse=True)
        else:
            active = (p.page == p.first_page+1)
            yield self._mklink(
                    p.first_page+1,
                    active=(p.page == p.first_page+1),
                    collapse=(p.page > p.first_page+1),
                    )

        # All numbered pages shown except first two and last two.
        for n in range(start, stop):
            active = n == p.page
            yield self._mklink(n, active=active, collapse=(not active))

        # Second to last page or disabled.
        if p.page_count <= 2:
            # Not enough pages.
            pass
        elif stop < p.last_page-1:
            yield self._mklink(p.last_page-1, self.name_disabled, disabled=True, collapse=True)
        else:
            yield self._mklink(
                    p.last_page-1,
                    active=(p.page == p.last_page-1),
                    collapse=(p.page < p.last_page-1),
                    )

        # Last page
        if p.page_count > 1:
            yield self._mklink(p.last_page, active=(p.page == p.last_page))
        
        if self.name_next:
            yield self._mklink(p.page+1, self.name_next, disabled=(p.page == p.last_page))
        if self.name_last:
            yield self._mklink(p.last_page, self.name_last, disabled=(p.page == p.last_page))

    def _mklink(self, page_number, name=None, active=False, disabled=False, collapse=False):
        return PageLink(page_number, name, active, disabled, collapse, self.get_param)

class PageLink(object):
    def __init__(self, page_number, name, active, disabled, collapse, get_param):
        self.page_number = page_number
        self.name = name or str(page_number)
        self.active = active
        self.disabled = disabled
        self.collapse = collapse
        self.get_param = get_param
        self.url = "?%s=%i"%(get_param, page_number)
        self.named = bool(name)
