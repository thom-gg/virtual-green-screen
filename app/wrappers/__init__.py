from app.wrappers.u2net_wrapper import U2NetWrapper


all_models = [
    {
        'name': "U2NET 320x320",
        'model': U2NetWrapper,
        'args': ['u2net', 320]
    },
    {
        'name': "U2NET 160x160",
        'model': U2NetWrapper,
        'args': ['u2net', 160]
    },
    {
        'name': "U2NET 32x32",
        'model': U2NetWrapper,
        'args': ['u2net', 32]
    },
    {
        'name': "U2NETP",
        'model': U2NetWrapper,
        'args': ['u2netp']
    }
]