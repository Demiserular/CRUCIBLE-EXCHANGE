# Test Plan: Crucible Exchange System

## 1. Overview

**Project:** Crucible FIX Exchange  
**Version:** 1.0  
**Author:** SDET  
**Date:** November 2025

### 1.1 Purpose
This test plan outlines the testing strategy for the Crucible Exchange System, a high-performance mock FIX protocol exchange server with real-time WebSocket updates, REST API, and optional C++ matching engine.

### 1.2 Scope
- Unit Testing (pytest)
- Integration Testing
- BDD/Acceptance Testing (Behave)
- Performance/Load Testing
- API Testing
- Database Testing
- Network/Protocol Testing

---

## 2. Test Environment

### 2.1 Hardware Requirements
- CPU: 2+ cores
- RAM: 4GB minimum
- Storage: 1GB free space

### 2.2 Software Requirements
| Component | Version |
|-----------|---------|
| Python | 3.12+ |
| pytest | 7.4+ |
| Behave | 1.2.6 |
| SQLite | 3.x |
| Git | 2.x |

### 2.3 Network Configuration
| Service | Port | Protocol |
|---------|------|----------|
| Exchange Server | 9878 | FIX 4.2 |
| WebSocket Server | 8765 | WS |
| API Server | 5000 | HTTP |

---

## 3. Test Categories

### 3.1 Unit Tests (`tests/`)

| Test File | Coverage Area | Test Count |
|-----------|---------------|------------|
| `test_matching_engine.py` | Order matching logic | 15+ |
| `test_fix_engine.py` | FIX protocol parsing | 15+ |
| `test_database.py` | SQLite operations | 12+ |
| `test_network.py` | Socket operations | 10+ |
| `test_cpp_benchmark.py` | C++ performance | 8+ |

### 3.2 BDD Tests (`features/`)

| Feature File | Scenarios |
|--------------|-----------|
| `order_matching.feature` | 5 scenarios |
| `api_testing.feature` | 7 scenarios |
| `database_testing.feature` | 6 scenarios |

---

## 4. Test Cases

### 4.1 Order Matching Tests

| TC ID | Description | Priority | Status |
|-------|-------------|----------|--------|
| TC-OM-001 | Place buy order | High | Ready |
| TC-OM-002 | Place sell order | High | Ready |
| TC-OM-003 | Match exact price | High | Ready |
| TC-OM-004 | No match (price gap) | High | Ready |
| TC-OM-005 | Partial fill | Medium | Ready |
| TC-OM-006 | Cancel order | High | Ready |
| TC-OM-007 | Market order execution | Medium | Ready |
| TC-OM-008 | Price-time priority | High | Ready |

### 4.2 FIX Protocol Tests

| TC ID | Description | Priority | Status |
|-------|-------------|----------|--------|
| TC-FIX-001 | Logon message | High | Ready |
| TC-FIX-002 | Logout message | High | Ready |
| TC-FIX-003 | Heartbeat | Medium | Ready |
| TC-FIX-004 | New Order Single | High | Ready |
| TC-FIX-005 | Cancel Request | High | Ready |
| TC-FIX-006 | Execution Report | High | Ready |
| TC-FIX-007 | Message parsing | High | Ready |
| TC-FIX-008 | Checksum validation | Medium | Ready |

### 4.3 REST API Tests

| TC ID | Endpoint | Method | Expected |
|-------|----------|--------|----------|
| TC-API-001 | `/api/submit_order` | POST | 200/201 |
| TC-API-002 | `/api/orderbook` | GET | 200 |
| TC-API-003 | `/api/executions` | GET | 200 |
| TC-API-004 | `/api/statistics` | GET | 200 |
| TC-API-005 | `/api/health` | GET | 200 |
| TC-API-006 | Invalid payload | POST | 400 |

### 4.4 Database Tests

| TC ID | Description | Priority | Status |
|-------|-------------|----------|--------|
| TC-DB-001 | Save order | High | Ready |
| TC-DB-002 | Retrieve order | High | Ready |
| TC-DB-003 | Save execution | High | Ready |
| TC-DB-004 | Query by status | Medium | Ready |
| TC-DB-005 | Query by symbol | Medium | Ready |
| TC-DB-006 | Concurrent writes | High | Ready |

### 4.5 Performance Tests

| TC ID | Description | Target | Status |
|-------|-------------|--------|--------|
| TC-PERF-001 | Add 1000 orders | < 1s | Ready |
| TC-PERF-002 | Match 100 orders | < 0.5s | Ready |
| TC-PERF-003 | Load test 5000 orders | < 10s | Ready |
| TC-PERF-004 | C++ vs Python comparison | C++ faster | Ready |

---

## 5. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Exchange server not running | High | Skip network tests in CI |
| C++ engine not compiled | Medium | Skip C++ tests if unavailable |
| Database corruption | High | Use test database, cleanup |
| Port conflicts | Medium | Use dedicated test ports |
| Timeout failures | Medium | Configurable timeouts |

---

## 6. Test Execution

### 6.1 Running All Tests

```bash
# Unit tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# BDD tests
behave features/

# Specific test file
pytest tests/test_matching_engine.py -v
```

### 6.2 CI/CD Pipeline

Tests are automatically executed on:
- Push to `main`, `master`, `develop` branches
- Pull requests to main branches

Pipeline stages:
1. **Lint** - Code quality checks (Pylint, Flake8)
2. **Unit Tests** - pytest with coverage
3. **BDD Tests** - Behave scenarios
4. **Security** - Bandit, Safety scans
5. **Build** - Verify imports and dependencies

---

## 7. Test Metrics

### 7.1 Coverage Goals
- Line Coverage: > 70%
- Branch Coverage: > 60%
- Critical paths: 100%

### 7.2 Pass Criteria
- All High priority tests pass
- No critical security vulnerabilities
- Performance within targets
- Zero regressions

---

## 8. Deliverables

| Artifact | Location |
|----------|----------|
| Unit Test Report | `pytest-results.xml` |
| Coverage Report | `htmlcov/index.html` |
| BDD Report | `bdd-results.json` |
| Lint Reports | `pylint-report.txt`, `flake8-report.txt` |
| Security Reports | `bandit-report.json`, `safety-report.json` |

---

## 9. Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| SDET | | | |
| Dev Lead | | | |
| QA Manager | | | |
