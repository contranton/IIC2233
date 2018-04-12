import datetime
from custom_exceptions import (MoreLikesThanViewsException,
                               NoTagsException,
                               InvalidDateError)


def awful_check_date(date):
    date_split = date.split(".")
    if len(date_split) != 3:
        return False
    if not all(map(lambda x: x.isnumeric, date_split)):
        return False

    y, d, m = date_split
    if len(y) != len(d) or len(d) != len(m):
        return False
    if (int(m) - 1) not in range(12):
        return False
    if int(d) > 31:
        return False
    # Screw leap years, different month lenghts, yadda yadda
    # This is why it's loads better to do something like:
    #
    # try:
    #     publish_d = datetime.datetime.strptime(publish_date, "%y.%d%.%m")
    # except ValueError:
    #     raise InvalidDateError()
    #
    # which uses a library already built to handle these cases!
    # A bit of a silly restriction, that one. Rewriting the wheel
    # for this is tedious, unnecessary, and can introduce more errors!
    return True


def tiempo_trending(publish_date, trending_date):

    # Tedioooous
    if not awful_check_date(publish_date):
        raise InvalidDateError()
    if not awful_check_date(trending_date):
        raise InvalidDateError()

    publish_d = datetime.datetime.strptime(publish_date, "%y.%d.%m")
    trending_d = datetime.datetime.strptime(trending_date, "%y.%d.%m")

    days = (trending_d - publish_d).days

    return days


def like_dislike_ratio(likes, dislikes):

    if not likes.isnumeric() or not dislikes.isnumeric():
        raise ValueError("Likes o Dislikes no son numéricos")

    if int(dislikes) == 0:
        raise ZeroDivisionError("Dislikes son 0!")

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
