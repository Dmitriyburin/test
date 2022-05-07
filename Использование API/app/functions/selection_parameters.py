def params_scale(ll, spn=None, pt=None):
    params = {
        "ll": ','.join(ll),
        "l": "map",
        "spn": ','.join(spn) if spn is not None else None,
        "pt": f"{','.join(pt)},pm2rdm" if pt is not None else None,
    }
    return params
