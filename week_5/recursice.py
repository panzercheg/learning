def get_id(content, guid):
    for entry in content:
        if isinstance(content, dict):
            print(content[entry])
            return get_id(content[entry], guid)
        if entry == "guid" and content[entry] == guid:
            print("guid {}".format(content[entry]))
            return entry


src = {'1123': {'456': {'tmp': {'guid': '1213'}}},
    'dffdsfsdf': {'dfdesfdsfds': 123},
    'rjuiwehreiw': {'2134123': 234892394},
    '4543543': {'5634534': 654654645}}

print(get_id(src, '2134123'))