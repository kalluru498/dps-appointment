#!/bin/bash

# Test Runner Script
# Runs different types of tests based on arguments

set -e

echo "================================"
echo "DPS Monitor - Test Runner"
echo "================================"
echo ""

# Default to all tests
TEST_TYPE="all"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--unit)
            TEST_TYPE="unit"
            shift
            ;;
        -i|--integration)
            TEST_TYPE="integration"
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -u, --unit         Run unit tests only (fast)"
            echo "  -i, --integration  Run integration tests (requires internet)"
            echo "  -c, --coverage     Generate coverage report"
            echo "  -v, --verbose      Verbose output"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                    # Run all tests"
            echo "  ./run_tests.sh -u                 # Run unit tests only"
            echo "  ./run_tests.sh -u -c              # Unit tests with coverage"
            echo "  ./run_tests.sh -i                 # Run integration tests"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest tests/"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

case $TEST_TYPE in
    unit)
        echo "Running unit tests only..."
        PYTEST_CMD="$PYTEST_CMD -m 'not integration'"
        ;;
    integration)
        echo "Running integration tests..."
        PYTEST_CMD="$PYTEST_CMD -m integration"
        ;;
    all)
        echo "Running all tests..."
        ;;
esac

if [ "$COVERAGE" = true ]; then
    echo "Coverage reporting enabled"
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=term-missing --cov-report=html"
fi

echo ""
echo "Command: $PYTEST_CMD"
echo ""

# Run the tests
eval $PYTEST_CMD

# Show coverage report location if generated
if [ "$COVERAGE" = true ]; then
    echo ""
    echo "================================"
    echo "Coverage report generated!"
    echo "View at: htmlcov/index.html"
    echo "================================"
fi

echo ""
echo "Tests complete!"
