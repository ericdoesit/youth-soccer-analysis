#!/bin/bash
# Run all analysis scripts

cd "$(dirname "$0")/.."

echo "========================================"
echo "US Youth Soccer Analysis Suite"
echo "========================================"
echo ""

read -p "Choose analysis to run:
  1) Dashboard Analysis (Cost-Benefit)
  2) Equity Analysis (Who Loses Most)
  3) Both

Enter choice (1-3): " choice

case $choice in
  1)
    echo ""
    echo "Running Dashboard Analysis..."
    python3 scripts/dashboard_analysis.py
    ;;
  2)
    echo ""
    echo "Running Equity Analysis..."
    python3 scripts/equity_analysis.py
    ;;
  3)
    echo ""
    echo "Running Dashboard Analysis..."
    python3 scripts/dashboard_analysis.py
    echo ""
    echo "========================================"
    echo ""
    echo "Running Equity Analysis..."
    python3 scripts/equity_analysis.py
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "========================================"
echo "Analysis complete!"
echo "========================================"
