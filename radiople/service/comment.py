# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.comment import Comment

from radiople.api.common import make_paging

from sqlalchemy import func
from sqlalchemy import desc

from sqlalchemy.orm import joinedload


class CommentService(Service):

    __model__ = Comment

    def exists(self, comment_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(Comment.id == comment_id).exists()
        ).scalar()


class ApiCommentService(CommentService):

    def get_list(self, broadcast_id, paging):
        query = Session.query(self.__model__) \
            .filter(Comment.broadcast_id == broadcast_id)

        total_count = query.with_entities(
            func.count(Comment.id)).scalar()

        if paging.cursor:
            query = query.filter(Comment.id <= paging.cursor)

        item = query.options(joinedload('*', innerjoin=True)) \
            .order_by(desc(Comment.id)) \
            .limit(paging.limit + 1).all()

        cursor = item[-1].id if len(item) > paging.limit else None

        return make_paging(item[:paging.limit], total_count, cursor)


api_service = ApiCommentService()
