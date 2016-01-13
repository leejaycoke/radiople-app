import redis

r = redis.StrictRedis(host='pp-dev', port=6379, db=2)


def is_like(episode_id, user_id):
    return r.sismember('episode_like:%d' % episode_id, user_id)
