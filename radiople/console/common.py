from flask import request

from radiople.exceptions import BadRequest


class Paging(object):

    @property
    def page(self):
        page = int(request.args.get('page', 1))
        if page <= 0:
            raise BadRequest
        return page

    @property
    def offset(self):
        return (self.page - 1) * self.page_size

    @property
    def sort(self):
        sort = request.args.get('sort', 'desc')
        return sort if sort in ['desc', 'asc'] else 'desc'

    def get_by(self, allowed_keys):
        return self.by if self.by in allowed_keys else None

    @property
    def by(self):
        by = request.args.get('by')
        return by if by and by.strip() != '' else None

    @property
    def page_size(self):
        return int(request.args.get('page_size', 20))

    @property
    def q(self):
        q = request.args.get('q')
        return q if q and q.strip() != '' else None


def get_paging():
    return Paging()


def make_paging(item, total_count, page):
    return {
        'item': item,
        'paging': {
            'total_count': total_count,
            'page': page,
        }
    }
