whl := camera-0.0.1-py3-none-any.whl

all: dist/$(whl)

clean:
	rm -f dist/$(whl)

dist/%.whl: FORCE
	python setup.py bdist_wheel

FORCE: ;
