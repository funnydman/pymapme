# 🗺️ PyMapMe

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic 2.0+](https://img.shields.io/badge/pydantic-2.0+-green.svg)](https://pydantic.dev/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Tests](https://img.shields.io/badge/tests-98%25%20coverage-brightgreen.svg)](https://github.com/funnydman/pymapme)

Transform Pydantic models from one structure to another with declarative field mapping.

✨ **Reshape data between APIs** 

🎯 **Flatten nested structures**

🔄 **Aggregate complex models** 

All while maintaining Pydantic's validation and type safety.

---

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🔧 Requirements](#-requirements)
- [🛠️ Development](#️-development)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🚀 Quick Start

Map data from a source Pydantic model to a target model with a different structure, using simple field declarations:

```python
from pydantic import BaseModel, Field
from pymapme.models.mapping import MappingModel

# Source models
class PersonalInfo(BaseModel):
    first_name: str
    last_name: str

class JobInfo(BaseModel):
    title: str
    company: str

class UserProfile(BaseModel):
    personal: PersonalInfo
    job: JobInfo

# Target model with flattened structure
class UserSummary(MappingModel):
    name: str = Field(json_schema_extra={"source": "personal.first_name"})
    title: str = Field(json_schema_extra={"source": "job.title"})

# Transform
profile = UserProfile(
    personal=PersonalInfo(first_name="John", last_name="Smith"),
    job=JobInfo(title="Developer", company="Acme")
)
summary = UserSummary.build_from_model(profile)
# UserSummary(name="John", title="Developer")
```

## ✨ Features

### 🎯 Nested Field Mapping
Map deeply nested fields using dot notation:

```python
class OrderSummary(MappingModel):
    customer_name: str = Field(json_schema_extra={"source": "customer.profile.name"})
    payment_total: float = Field(json_schema_extra={"source": "payment.amount"})
    shipping_city: str = Field(json_schema_extra={"source": "shipping.address.city"})
```

### 🔧 Custom Transformation Functions
Transform data using custom functions with access to the source model:

```python
class UserDisplay(MappingModel):
    full_name: str = Field(json_schema_extra={"source_func": "_build_full_name"})
    
    @staticmethod
    def _build_full_name(source_model, default):
        return f"{source_model.first_name} {source_model.last_name}".strip()
```

### 📊 Context Data Injection
Inject additional data during transformation:

```python
class EnrichedUser(MappingModel):
    name: str = Field(json_schema_extra={"source": "name"})
    is_premium: bool = Field(json_schema_extra={"source_func": "_check_premium"})
    
    @staticmethod
    def _check_premium(source_model, default, user_tier: str = "basic"):
        return user_tier == "premium"

# Usage with context
user = User(name="John")
enriched = EnrichedUser.build_from_model(user, context={"user_tier": "premium"})
# EnrichedUser(name="John", is_premium=True)
```

### ⚡ Automatic Field Mapping
Fields without explicit mapping use the same field name from source:

```python
class SimpleMapping(MappingModel):
    # These map automatically by name
    name: str
    email: str
    # This uses explicit mapping
    user_id: int = Field(json_schema_extra={"source": "id"})
```


## 📦 Installation

```bash
# Using pip
pip install pymapme

# Using Poetry
poetry add pymapme
```

## 🔧 Requirements

- Python 3.13+
- Pydantic 2.0+

## 🛠️ Development

### Setup
```bash
# Clone the repository
git clone https://github.com/funnydman/pymapme.git
cd pymapme

# Install dependencies
poetry install
```

### Commands
```bash
# Run tests with coverage
make run-unit-tests

# Run static analysis (Ruff + mypy)
make run-static-analysis

# Auto-format code
make format

# Build package
make build-package
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

### 1. Fork and Clone
```bash
git clone https://github.com/funnydman/pymapme.git
cd pymapme
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Write tests for new functionality
- Follow existing code patterns
- Update documentation if needed

### 4. Verify Quality
```bash
# Run full test suite
make run-unit-tests

# Check code quality
make run-static-analysis

# Format code
make format
```

### 5. Submit Pull Request
- Ensure all tests pass
- Include clear description of changes
- Reference any related issues

### Development Guidelines
- **Tests**: Write tests for all new features and bug fixes
- **Type hints**: Use modern Python type annotations
- **Documentation**: Update examples and docstrings as needed
- **Commit messages**: Use clear, descriptive commit messages

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
