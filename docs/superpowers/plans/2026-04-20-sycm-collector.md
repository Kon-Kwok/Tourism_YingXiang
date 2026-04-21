# SYCM Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a first-pass SYCM collector that reuses the local Chrome login state, collects homepage data, and can persist normalized records into MySQL.

**Architecture:** Add a small Python package that reads the local Chrome login state and uses direct HTTP requests to collect homepage APIs. Keep the first collector focused on the homepage APIs and store normalized metrics plus trend series in dedicated MySQL tables.

**Tech Stack:** Python 3, standard library `unittest`, `requests`, optional `pymysql`

---

### Task 1: Add failing unit tests for Chrome login-state access and homepage normalization
- [ ] Write tests for Chrome cookie decryption.
- [ ] Write tests for homepage metric and trend normalization.

### Task 2: Implement the Python SYCM collector package
- [ ] Add Chrome login-state HTTP helpers.
- [ ] Add a homepage collector that fetches overview, trend, and table JSON over HTTP.
- [ ] Add a small CLI with `healthcheck` and `collect-home`.

### Task 3: Add MySQL schema and persistence helpers
- [ ] Add table DDL for homepage metrics, trends, raw payloads, and collection batches.
- [ ] Add a persistence layer with idempotent upserts.

### Task 4: Verify
- [ ] Run the unit test suite.
- [ ] Run `healthcheck`.
- [ ] Run `collect-home --dry-run` against the live SYCM tab.
