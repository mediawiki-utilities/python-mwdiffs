def ops2opdocs(operations, a, b):
    for operation in operations:
        yield op2doc(operation, a, b)


def op2doc(operation, a, b):

    name, a1, a2, b1, b2 = operation
    doc = {
        'name': name,
        'a1': a1,
        'a2': a2,
        'b1': b1,
        'b2': b2
    }
    if name == "insert":
        doc['tokens'] = b[b1:b2]
    elif name == "delete":
        doc['tokens'] = a[a1:a2]

    return doc
