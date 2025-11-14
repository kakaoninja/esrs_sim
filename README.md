# Master Climate Sim

Financial impact assessment tool for ESRS Environmental Topics (E1-E5) using scenario-based cost modeling.

## Overview

Calculate financial costs for corporate environmental compliance across all ESRS environmental topics:
- **E1**: Climate Change
- **E2**: Pollution
- **E3**: Water & Marine Resources
- **E4**: Biodiversity & Ecosystems
- **E5**: Circular Economy

Uses climate scenarios (IEA, NGFS, IPCC) with influence factors (CO2 prices, energy prices, regulatory stringency, technology costs, physical impacts) to calculate costs across categories (carbon pricing, transition, physical risk, compliance) with confidence intervals.

## Features

- Cost calculation for all ESRS E1-E5 environmental topics
- Multiple climate scenario support (IEA Net Zero 2050, NGFS, custom)
- Double materiality framework (financial vs impact materiality)
- Influence factor modeling with configurable correlations
- Statistical interpolation for missing data
- Suspicious value detection and flagging
- CSV output with complete audit trails
- Single-user local execution (SQLite database)

## Quick Start

### Prerequisites

- Python 3.11 or higher
- SQLite (included with Python)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd master_climate_sim

# Optional venv:
  # Create virtual environment
  python -m venv venv

  # Activate virtual environment
  # Windows:
  venv\Scripts\activate
  # macOS/Linux:
  source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
sqlite3 data/master_climate_sim.db < specs/001-esrs-e1-simulation/contracts/database-schemas.sql
```

### Basic Usage

```bash
# Calculate costs for a company under IEA Net Zero 2050 scenario
python -m src.cli calculate \
  --company-id "ACME_CORP" \
  --scenario-id "IEA_NZ2050" \
  --topics E1,E2,E3,E4,E5 \
  --output results/acme_iea_nz2050.csv
```

See [quickstart guide](specs/001-esrs-e1-simulation/quickstart.md) for detailed usage examples.

## Project Structure

```
master_climate_sim/
├── src/                    # Source code
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   ├── calculations/       # Cost calculation implementations
│   ├── data/               # Database access layer
│   ├── interpolation/      # Missing data handling
│   ├── validation/         # Input validation
│   ├── output/             # CSV generation
│   └── cli/                # Command-line interface
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── contract/           # Contract tests
│   └── fixtures/           # Test data
├── data/                   # SQLite database
├── config/                 # Configuration files
│   └── scenarios/          # Scenario definitions
├── results/                # Output CSV files
└── specs/                  # Feature specifications
    └── 001-esrs-e1-simulation/
        ├── spec.md         # Feature specification
        ├── plan.md         # Implementation plan
        ├── tasks.md        # Task breakdown
        ├── data-model.md   # Entity model
        ├── research.md     # Technical decisions
        ├── quickstart.md   # Usage guide
        └── contracts/      # Schemas
```

## Documentation

- **[Feature Specification](specs/001-esrs-e1-simulation/spec.md)** - Requirements and user stories
- **[Implementation Plan](specs/001-esrs-e1-simulation/plan.md)** - Technical architecture
- **[Data Model](specs/001-esrs-e1-simulation/data-model.md)** - Entity relationships
- **[Quickstart Guide](specs/001-esrs-e1-simulation/quickstart.md)** - Usage examples
- **[Task Breakdown](specs/001-esrs-e1-simulation/tasks.md)** - Implementation tasks

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with coverage
pytest --cov=src tests/
```

### Test-Driven Development

This project follows strict TDD per the constitution:

1. Write test first (should fail)
2. Implement minimum code to pass test
3. Refactor while keeping tests green
4. Repeat

See [constitution](\.specify\memory\constitution.md) for development principles.

## Constitution Principles

1. **Scientific Accuracy**: All calculations reference authoritative sources (ESRS, GHG Protocol, IEA, NGFS, IPCC)
2. **Test-First Development**: Mandatory TDD for all features
3. **Performance & Scalability**: <60 seconds for E1-E5 assessment
4. **Data Integrity & Traceability**: Complete audit trails for ESRS assurance
5. **Simplicity & Maintainability**: Clear code, minimal dependencies

## License

[MIT_License](https://github.com/kakaoninja/esrs_sim/blob/main/LICENSE)

## Contributing

[Ask me before contributing](mailto:kakaoninja@gmail.com)

## Support

For issues and questions, see [GitHub Issues](<repository-url>/issues)
