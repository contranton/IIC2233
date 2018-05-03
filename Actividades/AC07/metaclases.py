import funciones


class MetaAuto(type):
    def __call__(cls, *args):
        new_car = type.__call__(cls, *args)
        if hasattr(cls, "cars"):
            if len(getattr(cls, "cars")) >= 3:
                return None
            getattr(cls, "cars").append(new_car)
            return new_car

        cls.cars = [new_car]
        return new_car
    
    def __new__(mcs, name, bases, dct):
        # Add pieces
        dct["piezas"] = funciones.crear_piezas()

        # Add function
        foo = funciones.definir_estado_piezas
        dct[foo.__name__] = foo
        
        return type.__new__(mcs, name, bases, dct)

    
class MetaTrabajador(type):
    def __new__(meta, name, base, clsdict):
        del clsdict["revizar_ztado"]
        clsdict[funciones.revisar_estado.__name__] = funciones.revisar_estado
        clsdict[funciones.reparar.__name__] = funciones.reparar
        return super().__new__(meta, name, base, clsdict)

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "worker"):
            cls.worker = super().__call__(*args, **kwargs)
        return cls.worker
    
if __name__ == '__main__':
    class Auto(metaclass=MetaAuto):
        pass

    a = Auto()
    b = Auto()
    c = Auto()
    d = Auto()
