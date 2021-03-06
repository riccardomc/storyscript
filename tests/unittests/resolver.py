# -*- coding: utf-8 -*-
import re

from pytest import mark, raises

from storyscript.resolver import Resolver


def test_resolver_handside(patch):
    patch.object(Resolver, 'object')
    result = Resolver.handside('item', 'data')
    Resolver.object.assert_called_with('item', 'data')
    assert result == Resolver.object()


def test_resolver_stringify():
    assert Resolver.stringify(1) == '1'


def test_resolver_stringify_string():
    assert Resolver.stringify('one') == '"""one"""'


def test_resolver_stringify_string_multiline():
    assert Resolver.stringify('one"') == '"""one\""""'


def test_resolver_values():
    values = [{'$OBJECT': 'path', 'paths': ['one']},
              {'$OBJECT': 'path', 'paths': ['two']}]
    assert Resolver.values(values, {'one': 1, 'two': 2}) == [1, 2]


def test_resolver_string():
    assert Resolver.string('hello', {}) == 'hello'


def test_resolver_object_str_str():
    items = [
        [{'$OBJECT': 'string', 'string': 'example'},
         {'$OBJECT': 'string', 'string': 'data'}]
    ]
    assert dict(Resolver.dict(items, {})) == {
        'example': 'data'
    }


def test_resolver_file():
    assert Resolver.file('filename', {}) == 'filename'


def test_resolver_file_values(patch):
    patch.object(Resolver, 'values', return_value=['a'])
    result = Resolver.file('{}.py', {}, values=['values'])
    Resolver.values.assert_called_with(['values'], {})
    assert result == 'a.py'


def test_resolver_argument(patch):
    patch.object(Resolver, 'object')
    result = Resolver.argument('argument', {})
    Resolver.object.assert_called_with('argument', {})
    assert result == Resolver.object()


def test_resolver_object_path_path():
    items = [
        [{'$OBJECT': 'path', 'paths': ['a']},
         {'$OBJECT': 'path', 'paths': ['b']}]
    ]
    data = {'a': 'example', 'b': 'data'}
    assert dict(Resolver.dict(items, data)) == {
        'example': 'data'
    }


def test_resolver_path():
    path = ['a', 'b', 'c']
    data = {'a': {'b': {'c': 'value'}}}
    assert Resolver.path(path, data) == 'value'


def test_resolver_path_list():
    path = ['a', '1', 'b']
    data = {'a': [None, {'b': 'value'}]}
    assert Resolver.path(path, data) == 'value'


def test_resolver_path_key_error():
    assert Resolver.path(['a', 'b'], {}) is None


def test_resolver_dictionary(patch):
    patch.object(Resolver, 'resolve')
    result = Resolver.dictionary({'key': 'value'}, 'data')
    Resolver.resolve.assert_called_with('value', 'data')
    assert result == {'key': Resolver.resolve()}


def test_resolver_dictionary_empty():
    assert Resolver.dictionary({}, 'data') == {}


def test_resolver_list_object(patch):
    patch.object(Resolver, 'resolve', return_value='done')
    result = Resolver.list_object(['item'], {})
    assert list(result) == ['done']


@mark.parametrize('match, expectation', [
    (None, False),
    ('else', True)
])
def test_resolver_method_like(mocker, match, expectation):
    right = mocker.MagicMock(match=mocker.MagicMock(return_value=match))
    result = Resolver.method('like', 'left', right)
    right.match.assert_called_with('left')
    assert result is expectation


@mark.parametrize('match, expectation', [
    (None, True),
    ('else', False)
])
def test_resolver_method_notlike(mocker, match, expectation):
    right = mocker.MagicMock(match=mocker.MagicMock(return_value=match))
    result = Resolver.method('notlike', 'left', right)
    right.match.assert_called_with('left')
    assert result is expectation


def test_resolver_method_in():
    assert Resolver.method('in', 'left', ['left'])


@mark.parametrize('method', ['has', 'contains'])
def test_resolver_method_has(method):
    assert Resolver.method(method, ['left'], 'left')


def test_resolver_method_excludes():
    assert Resolver.method('in', 'left', ['right']) is False


def test_resolver_method_is():
    assert Resolver.method('is', 'left', 'left')


def test_resolver_method_isnt():
    assert Resolver.method('isnt', 'left', 'right')


def test_resolver_method_value_error():
    with raises(ValueError):
        Resolver.method('unknown', 'left', 'right')


def test_resolver_expression(patch):
    patch.object(Resolver, 'values', return_value=[1])
    patch.object(Resolver, 'stringify', return_value='1')
    result = Resolver.expression('data', '{} == 1', 'values')
    Resolver.values.assert_called_with('values', data='data')
    Resolver.stringify.assert_called_with(1)
    assert result


def test_resolver_object_string(patch):
    patch.object(Resolver, 'string')
    item = {'$OBJECT': 'string', 'string': 'message'}
    result = Resolver.object(item, 'data')
    Resolver.string.assert_called_with('message', 'data')
    assert result == Resolver.string()


def test_resolver_object_string_values(patch):
    patch.object(Resolver, 'string')
    item = {'$OBJECT': 'string', 'string': 'message', 'values': 'values'}
    result = Resolver.object(item, 'data')
    Resolver.string.assert_called_with('message', 'data', values='values')
    assert result == Resolver.string()


def test_resolver_object_path(patch):
    patch.object(Resolver, 'path')
    path = {'$OBJECT': 'path', 'paths': ['example']}
    result = Resolver.object(path, 'data')
    Resolver.path.assert_called_with(['example'], 'data')
    assert result == Resolver.path()


def test_resolver_object_dict(patch):
    patch.object(Resolver, 'dict')
    _dict = {'$OBJECT': 'dict', 'items': []}
    result = Resolver.object(_dict, 'data')
    Resolver.dict.assert_called_with(_dict['items'], 'data')
    assert result == dict(Resolver.dict())


def test_resolver_object_regexp(patch):
    patch.object(re, 'compile')
    expression = {'$OBJECT': 'regexp', 'regexp': 'regular'}
    Resolver.object(expression, 'data')
    re.compile.assert_called_with('regular')


def test_resolver_object_value():
    value = {'$OBJECT': 'value', 'value': 'x'}
    result = Resolver.object(value, 'data')
    assert result == 'x'


def test_resolver_object_dictionary(patch):
    patch.object(Resolver, 'dictionary')
    result = Resolver.object({'$OBJECT': 'dictionary'}, 'data')
    Resolver.dictionary.assert_called_with({'$OBJECT': 'dictionary'}, 'data')
    assert result == Resolver.dictionary()


def test_resolver_object_list(patch):
    patch.object(Resolver, 'list_object')
    result = Resolver.object({'$OBJECT': 'list', 'items': []}, 'data')
    Resolver.list_object.assert_called_with([], 'data')
    assert result == []


def test_resolver_object_method(patch):
    patch.object(Resolver, 'method')
    patch.object(Resolver, 'handside', return_value='hand')
    item = {'$OBJECT': 'method', 'method': 'method', 'left': 'left',
            'right': 'right'}
    result = Resolver.object(item, 'data')
    Resolver.method.assert_called_with('method', 'hand', 'hand')
    assert result == Resolver.method()


def test_resolver_object_argument(patch):
    patch.object(Resolver, 'argument')
    item = {'$OBJECT': 'argument', 'argument': {}}
    result = Resolver.object(item, 'data')
    Resolver.argument.assert_called_with({}, 'data')
    assert result == Resolver.argument()


def test_resolver_object_file(patch):
    patch.object(Resolver, 'file')
    item = {'$OBJECT': 'file', 'string': 'filename'}
    result = Resolver.object(item, 'data')
    Resolver.file.assert_called_with(item['string'], 'data')
    assert result == Resolver.file()


def test_resolver_object_file_values(patch):
    patch.object(Resolver, 'file')
    item = {'$OBJECT': 'file', 'string': 'filename', 'values': ['values']}
    result = Resolver.object(item, 'data')
    Resolver.file.assert_called_with(item['string'], 'data', values=['values'])
    assert result == Resolver.file()


def test_resolver_resolve_expression(patch):
    patch.object(Resolver, 'expression')
    item = {'$OBJECT': 'expression', 'expression': '==', 'values': []}
    result = Resolver.resolve(item, 'data')
    Resolver.expression.assert_called_with('data', item['expression'],
                                           item['values'])
    assert result == Resolver.expression()


def test_resolver_list(patch):
    patch.object(Resolver, 'resolve', return_value='done')
    result = Resolver.list(['items'], {})
    Resolver.resolve.assert_called_with('items', {})
    assert result == 'done'


def test_resolver_list_booleans(patch):
    patch.object(Resolver, 'resolve', return_value=True)
    result = Resolver.list(['items'], {})
    Resolver.resolve.assert_called_with('items', {})
    assert result == [True]


def test_resolver_resolve(patch):
    assert Resolver.resolve('whatever', 'data') == 'whatever'


def test_resolve_many():
    result = Resolver.resolve({
        '$OBJECT': 'string',
        'string': '{}',
        'values': [{
            '$OBJECT': 'path',
            'paths': ['foo', 'bar']
        }]
    }, {'foo': {'bar': 'data'}})

    assert result == 'data'


def test_resolver_resolve_object(patch):
    patch.object(Resolver, 'object')
    result = Resolver.resolve({}, 'data')
    Resolver.object.assert_called_with({}, 'data')
    assert result == Resolver.object()


def test_resolver_resolve_list(patch):
    patch.object(Resolver, 'list')
    result = Resolver.resolve([], 'data')
    Resolver.list.assert_called_with([], 'data')
    assert result == Resolver.list()
