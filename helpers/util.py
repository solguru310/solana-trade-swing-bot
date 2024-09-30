def is_integer_num(n):
     if isinstance(n, int):
         return True
     if isinstance(n, float):
         return n.is_integer()
     return False

def convert_dict_str_vals_to_float(d):
    for k, v in d.items():
        d[k] = float(v) if is_float(v) else v
    return d

def is_float(v) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False

def show(label, value, line = None):
    if line and line == 'above':
        print('-----------------------------------------------------------------------------------------------------------------')
    print(label + ': ' + str(value))

def show_object(label, object):
    print(label + '-------------------------------------------')
    print(object)
    print('---------------------------------------------------')