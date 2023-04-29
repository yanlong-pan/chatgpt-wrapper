from functools import reduce
from deepmerge import always_merger
from copy import deepcopy

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

user_registration_schema = reduce(always_merger.merge, [deepcopy(user_schema), deepcopy(email_schema), deepcopy(password_schema), {
    'required': ['username', 'email', 'password']
}])

user_login_schema = reduce(always_merger.merge, [deepcopy(user_schema), deepcopy(email_schema),
    {
        'properties': {
            'password': {
                'type': 'string',
            },
        },
    }, {
        'anyOf': [
            {'required': ['username', 'password']},
            {'required': ['email', 'password']}
        ]
    }
])