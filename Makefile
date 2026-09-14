.PHONY: verify demo

verify:
	python -m pip install -e ".[dev]" -q
	pytest -q

demo:
	mkdir -p build
	python -m freight_audit.cli --input examples/input --output build/adjudications.jsonl
	cat build/adjudications.jsonl
