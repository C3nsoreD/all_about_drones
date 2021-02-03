from mesh.filters import LoopBackFilter

class F1:
    pass

class F2:
    pass


f_list  = [F1, F2]
filters = [LoopBackFilter()] + [F for F in f_list]


print(filters)
