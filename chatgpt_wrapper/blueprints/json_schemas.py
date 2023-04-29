from functools import reduce
from deepmerge import always_merger

user_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
    },
}

email_schema = {
    'type': 'object',
    'properties': {
        'email': {'type': 'string', 'format': 'email'},
    },
}

password_schema = {
    'type': 'object',
    'properties': {
        'password': {
        'type': 'string',
        'minLength': 8,
        'pattern': '^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$',
        },
    },
}

user_registration_schema = reduce(always_merger.merge, [user_schema, email_schema, password_schema, {
    'required': ['username', 'email', 'password']
}])