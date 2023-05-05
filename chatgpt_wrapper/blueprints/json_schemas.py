from functools import reduce
from deepmerge import always_merger
from copy import deepcopy

def build_single_property_schema(property, type='string', **kargs):
    return {
        'type': 'object',
        'properties': {
            property: {'type': type, **kargs},
        },
    }

username_schema = build_single_property_schema('username')

email_schema = build_single_property_schema(property='email', format='email')

password_schema = build_single_property_schema(property='password', minLength=8, pattern='^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$')

user_input_schema = build_single_property_schema(property='user_input')

character_schema = build_single_property_schema(property='character')

refresh_schema = build_single_property_schema(property='refresh', type='boolean')

user_registration_schema = reduce(always_merger.merge, [
    deepcopy(username_schema),
    deepcopy(email_schema),
    deepcopy(password_schema), 
    {
        'required': ['username', 'email', 'password']
    }
])

user_login_schema = reduce(always_merger.merge, [
    deepcopy(username_schema),
    deepcopy(email_schema),
    build_single_property_schema('password'), 
    {
        'anyOf': [
            {'required': ['username', 'password']},
            {'required': ['email', 'password']}
        ]
    }
])

chat_schema = reduce(always_merger.merge, [
    user_input_schema,
    character_schema,
    refresh_schema,
    {'required': ['user_input', 'character']}
])