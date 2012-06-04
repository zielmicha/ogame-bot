import pickle
import time

def write(name, value):
    wr_value = {
        'time': time.time(),
        'value': value,
    }
    assert '/' not in name
    with open('_data_' + name, 'w') as f:
        pickle.dump(wr_value, f)

def load(name, timeout=20):
    try:
        val = pickle.load(open('_data_' + name))
    except IOError:
        return None

    if val['time'] + timeout < time.time():
        return None
    else:
        return val['value']

if __name__ == '__main__':
    main()
