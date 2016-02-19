class LazyOperation:
	"""
	It is a lazy operation.
	"""

	def __init__(self, function, *args, **kwargs):
		self._function = function
		self._args = args
		self._kwargs = kwargs

	def eval(self):
		for arg in self._args:
			if isinstance(arg, LazyOperation):
				arg = arg.eval()
		for kwarg in self._kwargs.values():
			if isinstance(kwarg, LazyOperation):
				kwarg = kwarg.eval()

		print (self._function, self._args, self._kwargs)

		return self._function(*self._args, **self._kwargs)

def lazy(function):
	def lazyfunc(*args, **kwargs):
		return LazyOperation(function, args, kwargs)
	return lazyfunc