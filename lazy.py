class LazyOperation:
	"""
	Object that contains unevaluated expression. Executes expression inside upon calling `eval()`.
	"""

	def __init__(self, function, *args, **kwargs):
		self._function = function
		self._args = list(args)
		self._kwargs = kwargs

	def eval(self):
		for i, arg in enumerate(self._args):
			if isinstance(arg, LazyOperation):
				result = arg.eval()
				self._args[i] = result
		for key, arg in self._kwargs.items():
			if isinstance(arg, LazyOperation):
				result = arg.eval()
				self._kwargs[key] = result

		return self._function(*self._args, **self._kwargs)

def lazy(function):
	def lazyfunc(*args, **kwargs):
		return LazyOperation(function, *args, **kwargs)
	return lazyfunc

@lazy
def lazy_add(a, b):
	return a + b

@lazy
def lazy_mul(a, b):
	return a * b


if __name__ == "__main__":
	print(lazy_add(1, 2).eval())

	thunk = lazy_mul(lazy_add(1, 2), 4)
	print(thunk.eval())
