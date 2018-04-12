class MoreLikesThanViewsException(Exception):
    def __init__(self):
        super().__init__("El video tiene mas likes que views!")


class NoTagsException(Exception):
    def __init__(self):
        super().__init__("El video no tiene tags!")

class InvalidDateError(Exception):
    def __init__(self):
        super().__init__("Fecha invalida!")
                           
