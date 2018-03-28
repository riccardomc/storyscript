from pytest import fixture

from storyscript.tree import Method, Program
from storyscript.version import version


@fixture
def parser(magic):
    return magic()


@fixture
def program(parser):
    return Program(parser, 'story')


def test_program_init(parser, program):
    assert program.parser == parser
    assert program.parser.program == program
    assert program.story == 'story'


def test_program_representation(parser, program):
    assert '{}'.format(program) == 'Program({}, story)'.format(parser)


def test_program_sorted_lines(program):
    lines = {'1': {}, '2': {}, '21': {}, '3': {}}
    assert program.sorted_lines(lines) == ['1', '2', '3', '21']


def test_program_next_line(patch, program):
    patch.object(Program, 'sorted_lines', return_value=['1', '2'])
    lines = {'1': {'ln': '1'}, '2': {'ln': '2'}}
    result = program.next_line(lines, '1')
    Program.sorted_lines.assert_called_with(lines)
    assert result == lines['2']


def test_program_next_line_jump(patch, program):
    patch.object(Program, 'sorted_lines', return_value=['1', '3'])
    lines = {'1': {'ln': '1'}, '3': {'ln': '3'}}
    assert program.next_line(lines, '1') == lines['3']


def test_program_next_line_none(patch, program):
    patch.object(Program, 'sorted_lines', return_value=['1'])
    lines = {'1': {'ln': '1'}}
    assert program.next_line(lines, '1') is None


def test_program_last_line(patch, program):
    patch.object(Program, 'sorted_lines')
    result = program.last_line('lines')
    Program.sorted_lines.assert_called_with('lines')
    assert result == Program.sorted_lines()[-1]


def test_program_last_line_none(patch, program):
    patch.object(Program, 'sorted_lines', return_value=None)
    result = program.last_line('lines')
    Program.sorted_lines.assert_called_with('lines')
    assert result is None


def test_program_children(patch, program):
    patch.object(Program, 'parse_item')
    program.children({}, ['child'], parent=None)
    Program.parse_item.assert_called_with({}, 'child', parent=None)


def test_program_parse_item(patch, method, program):
    patch.object(Method, 'json')
    result = {}
    program.parse_item(result, method)
    assert result[method.lineno] == method.json()


def test_program_parse_item_recursion(patch, method, program):
    patch.object(Method, 'json')
    result = {}
    program.parse_item(result, [[method]])
    assert result[method.lineno] == method.json()


def test_program_parse_item_parent(patch, magic, method, program):
    patch.object(Method, 'json', return_value={})
    result = {}
    program.parse_item(result, method, parent=magic(lineno='100'))
    assert result[method.lineno]['parent'] == '100'


def test_program_parse_item_suite(patch, method, program):
    patch.object(Method, 'json')
    child = Method('method', 'parser', 2)
    method.suite = [child]
    result = {}
    program.parse_item(result, method)
    assert result['2'] == child.json()


def test_program_parse_suite(patch, magic, program):
    patch.object(Program, 'last_line', return_value=None)
    item = magic(lineno='2', json=magic(return_value={}))
    result = program.parse_suite([item], '1')
    assert item.json.call_count == 1
    assert result == {'2': {'parent': '1'}}


def test_program_parse_suite_next_line(patch, magic, program):
    patch.object(Program, 'last_line', return_value='2')
    item = magic(lineno='2', json=magic(return_value={}))
    result = program.parse_suite([item], '1')
    assert Program.last_line.call_count == 1
    assert result['2']['next'] == '2'


def test_program_generate(patch, magic, program):
    patch.many(Program, ['last_line', 'parse_suite'])
    Program.last_line.return_value = None
    item = magic(lineno='1', json=magic(return_value={}, suite=None))
    program.story = [item]
    result = program.generate()
    assert Program.last_line.call_count == 1
    assert item.json.call_count == 1
    assert result == {'1': {}}


def test_program_generate_next_line(patch, magic, program):
    patch.many(Program, ['last_line', 'parse_suite'])
    Program.last_line.return_value = '1'
    item = magic(lineno='1', json=magic(return_value={}, suite=None))
    program.story = [item, item]
    result = program.generate()
    assert result == {'1': {'next': program.last_line()}}


def test_program_generate_suite(patch, magic, program):
    patch.many(Program, ['last_line', 'parse_suite'])
    Program.last_line.return_value = None
    Program.parse_suite.return_value = {'2': {}}
    item = magic(lineno='1', json=magic(return_value={}, suite='suite'))
    program.story = [item]
    result = program.generate()
    Program.parse_suite.assert_called_with(item.suite, '1')
    assert '1' in result
    assert result['2'] == {}


def test_program_json(patch, program):
    patch.object(Program, 'generate')
    result = program.json()
    assert Program.generate.call_count == 1
    assert result == {'version': version, 'script': program.generate()}
