import zmq


class ZMQFailureChain:
    def __init__(self, error_msg):
        self.value = None
        self.error_msg = error_msg

    def then(self, f, *args, **kwargs):
        return ZMQFailureChain(self.error_msg)


class ZMQChain:
    def __init__(self, value=None):
        self.value = value

    def then(self, f, *args, **kwargs):
        try:
            value = f(*args, **kwargs)
            return ZMQChain(value)
        except zmq.ZMQError:
            error_msg = 'ZMQError during evaluation of {}(args={}, kwargs={})'.format(f.__name__, args, kwargs)
            return ZMQFailureChain(error_msg)
