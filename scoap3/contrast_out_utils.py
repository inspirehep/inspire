def contrast_out_cmp(x, y):
    def get_val_type(x):
        val = x
        val_vtex = False
        val_type = None

        if "vtex" in val:
            val_vtex = True
            val = val.split('_')[0]
            val = val.strip("vtex")
        else:
            for w in ["CERN", "P", "S", "Q", "AB", "J"]:
                if w is not "CERN" and w in val:
                    if w is "P":
                        val_type = 1
                    if w is "Q":
                        val_type = 2
                    if w is "S":
                        val_type = 3
                    if w is "AB":
                        val_type = 4
                    if w is "J":
                        val_type = 5
                val = val.strip(w)

        return val, val_type, val_vtex

    x_number, x_type, x_vtex = get_val_type(x)
    y_number, y_type, y_vtex = get_val_type(y)

    if x_vtex or y_vtex:
        if x_vtex and not y_vtex:
            return 1
        elif not x_vtex and y_vtex:
            return -1
        elif x_vtex and y_vtex:
            if int(x_number) > int(y_number):
                return 1
            elif int(x_number) < int(y_number):
                return -1
            else:
                return 0
    else:
        if int(x_number) > int(y_number):
            return 1
        elif int(x_number) < int(y_number):
            return -1
        else:
            if int(x_type) > int(y_type):
                return 1
            elif int(x_type) < int(y_type):
                return -1
            else:
                return 0

def find_package_name(path):
    try:
        return [p_name for p_name in path.split('/') if "CERN" in p_name or "vtex" in p_name][0]
    except:
        return "unknown"
