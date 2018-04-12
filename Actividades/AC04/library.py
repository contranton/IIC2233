import datetime
from custom_exceptions import (MoreLikesThanViewsException,
                               NoTagsException)


def tiempo_trending(publish_date, trending_date):
    
    publish_d = datetime.datetime.strptime(publish_date, "%y.%d.%m")
    trending_d = datetime.datetime.strptime(trending_date, "%y.%d.%m")
    days = (trending_d - publish_d).days

    return days


def like_dislike_ratio(likes, dislikes):

    if not likes.isnumeric() or not dislikes.isnumeric():
        raise ValueError("Likes o Dislikes no son numéricos")
    return int(likes) / int(dislikes)


def info_video(title, views, likes, dislikes, tags):
    if int(likes) > int(views):
        raise MoreLikesThanViewsException()

    if not tags:
        raise NoTagsException()

    print("El video {0} ha tenido {1} views, con {2} likes y {3} dislikes"
          .format(title, views, likes, dislikes))


# Own definitions ahead


def log(video, error):
    with open("exceptions.txt", 'a') as f:
        s = "El video {} levantó la siguiente excepción: {}\n"
        f.write(s.format(video.title, error))
