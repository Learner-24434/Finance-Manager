from pytest import raises
from csv import *
from V0.project import *

def test_create_acc():
    create_acc('test', 'password', 200)
    assert authenticate('test', 'password') == 'test'
    with raises(SystemExit):
        assert authenticate('test', 'passwords')

def test_del_acc():
    del_acc('test')

    with raises(FileNotFoundError):
        with open('test', 'r'):
            pass

def test_write():
    create_acc('test', 'password', 200)
    write('test', '12-09-2023', 'special', 'hello world')
    os.chdir('test')
    with open('diary.csv', 'r') as f:
        reader = DictReader(f)
        for row in reader:
            assert row['date'] == '12-09-2023'
            assert row['category'] == 'special'
            assert row['entry'] == 'hello world'
    os.chdir(os.pardir)
    del_acc('test')

def test_read():
    create_acc('test', 'password', 200)
    write('test', '12-09-2023', 'special', 'hello world')
    assert read('test', '12-09-2023') == ['hello world']
    del_acc('test')

def test_get():
    create_acc('test', 'password', 200)
    write('test', '12-09-2023', 'special', 'hello world')
    assert get_info('test', 'date', print_res = False) == {'12-09-2023'}
    del_acc('test')