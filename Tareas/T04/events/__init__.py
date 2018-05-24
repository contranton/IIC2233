class Event(object):

    logger = Logger()
    
    def __init__(self, name, entity, function):
        self.name = name
        self.entity = entity
        self.function = function
        self.update_time(0)

    def __call__(self, *args, **kwargs):
        print(self.time, end=": ")
        return self.function(self.entity, *args, **kwargs)

    @property
    def time(self):
        return self.updated_time(self.entity)

    def update_time(self, new_time):
        if callable(new_time):
            self.updated_time = new_time
        else:
            self.updated_time = lambda p: new_time

    def __repr__(self):
        s = "Event({}, {}, {})"
        return s.format(self.name, self.time, self.entity)
