.PHONY: install install-dev setup test test-quick lint typecheck format check check-all clean build run-desktop dev coverage

# Install production dependencies
install:
	@echo "Installing media-manager..."
	pip install -e .

# Install with dev + desktop deps
install-dev:
	pip install -e ".[dev]"
	cd desktop && npm ci

setup:
	pip install -e ".[dev]"
	cd desktop && npm ci

# Run full test suite
test:
	pytest tests/ -x --tb=short -q

# Run quick tests (first-fail)
test-quick:
	pytest tests/ -x --tb=line -q --no-header

# Lint Python
lint:
	ruff check src/ tests/

# Type-check TypeScript
typecheck:
	cd desktop && npx tsc --noEmit

format:
	ruff format src/ tests/
	cd desktop && npx prettier --write "src/**/*.{ts,tsx}"

# Clean build artifacts
clean:
	@echo "Cleaning..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	cd desktop && rm -rf dist node_modules/.vite 2>/dev/null || true
	@echo "Clean"

# Build desktop app
build:
	cd desktop && npm run build
	cd desktop/src-tauri && cargo build --release

# Run desktop in dev mode
run-desktop:
	cd desktop && npm run tauri dev

dev:
	cd desktop && npm run tauri dev

# All checks
check: lint typecheck test-quick
	@echo "All checks passed!"

check-all: lint typecheck test
	@echo "All checks passed!"

coverage:
	pytest tests/ --cov=src/media_manager --cov-report=html
	@echo "Coverage report: htmlcov/index.html"
