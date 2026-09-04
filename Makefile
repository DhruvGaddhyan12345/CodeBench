.PHONY: test demo benchmark safety

test:
	python -m pytest -q

demo:
	python scripts/run_demo.py

benchmark:
	python scripts/run_benchmark.py --tasks benchmarks/tasks

safety:
	python scripts/run_safety_tests.py
