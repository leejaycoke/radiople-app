# -*- coding: utf-8 -*-

from radiople.db import Session


from radiople.service import Service

from radiople.model.broadcast import Broadcast
from radiople.model.sb_broadcast import SbBroadcast
from radiople.model.episode import Episode
from radiople.model.comment import Comment
from radiople.model.subscription import Subscription
from radiople.model.rating import Rating

from sqlalchemy import func


class SbBroadcastService(Service):

    __model__ = SbBroadcast

    def refresh_comment_count(self, broadcast_id):
        current = self.get(broadcast_id)
        if not current:
            return

        comment_count = Session.query(Comment) \
            .with_entities(func.count(Comment.id)) \
            .filter(Comment.broadcast_id == broadcast_id).scalar()

        self.update(current, comment_count=comment_count)

    def refresh_episode_count(self, broadcast_id):
        current = self.get(broadcast_id)
        if not current:
            return

        episode_count = Session.query(Episode) \
            .with_entities(func.count(Episode.id)) \
            .filter(Episode.broadcast_id == broadcast_id).scalar()

        self.update(current, episode_count=episode_count)

    def refresh_subscriber_count(self, broadcast_id):
        current = self.get(broadcast_id)
        if not current:
            return

        subscriber_count = Session.query(Subscription) \
            .with_entities(func.count(Subscription.broadcast_id)) \
            .filter(Subscription.broadcast_id == broadcast_id).scalar()

        self.update(current, subscriber_count=subscriber_count)

    def refresh_rating(self, broadcast_id):
        current = self.get(broadcast_id)
        if not current:
            return

        try:
            count, average = Session.query(Rating) \
                .with_entities(func.count(Rating.broadcast_id),
                               func.avg(Rating.point)) \
                .filter(Rating.broadcast_id == broadcast_id).one()
        except:
            return

        average = average or 0

        self.update(current, rating_count=count, rating_average=average)


class ApiSbBroadcastService(SbBroadcastService):

    pass


service = SbBroadcastService()
api_service = ApiSbBroadcastService()
