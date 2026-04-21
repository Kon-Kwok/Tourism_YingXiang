# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260421-001] correction

**Logged**: 2026-04-21T22:42:32.933145
**Priority**: medium
**Status**: promoted
**Area**: docs

### Summary
In this project context, the user's SYCM database should be interpreted as the `qianniu` schema, not a separate `sycm` schema.

### Details
I initially treated `sycm` as a missing MySQL database. The user clarified that their SYCM data is actually stored in the `qianniu` database. Future database inspection and guidance should use that mapping.

### Suggested Action
When discussing this user's database layout, map SYCM-related storage to `qianniu` unless the user states otherwise.

### Metadata
- Source: user_feedback
- Related Files: CLAUDE.md, AGENTS.md
- Tags: database, sycm, qianniu

### Resolution
- **Resolved**: 2026-04-21T23:25:00+08:00
- **Commit/PR**: local workspace
- **Notes**: Promoted the mapping into project guidance so future database inspection treats user-facing SYCM data as the `qianniu` schema.

---

## [LRN-20260421-002] best_practice

**Logged**: 2026-04-21T23:25:00+08:00
**Priority**: high
**Status**: promoted
**Area**: backend

### Summary
Date-based merge pipelines into `qianniu_fliggy_shop_daily_key_data` need a unique key on `日期` or `ON DUPLICATE KEY UPDATE` will not merge sources into one row.

### Details
The workflow combines order-summary data and SYCM flow-monitor data for the same business date. Without a unique constraint on `日期`, both source-specific upserts can create separate rows instead of updating the same row, which breaks the intended daily aggregation behavior.

### Suggested Action
Before relying on date-based upserts for this table, ensure `日期` has a unique key and verify merge semantics against the live schema.

### Metadata
- Source: conversation
- Related Files: CLAUDE.md, AGENTS.md
- Tags: mysql, upsert, schema, qianniu

### Resolution
- **Resolved**: 2026-04-21T23:25:00+08:00
- **Commit/PR**: local workspace
- **Notes**: Promoted the rule into project guidance and aligned the live table schema to use a unique key on `日期`.

---

## [LRN-20260421-003] best_practice

**Logged**: 2026-04-21T23:25:00+08:00
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
When running inline MySQL from the shell, avoid backtick-quoted identifiers inside double-quoted command strings because the shell may execute them before MySQL sees the SQL.

### Details
An `ALTER TABLE ... ADD UNIQUE KEY ... (\`日期\`)` command failed because the shell interpreted the backticks. The fix was to send SQL through a single-quoted heredoc so MySQL receives the statement unchanged.

### Suggested Action
For SQL containing backticks or other shell-sensitive characters, prefer `mysql <<'SQL' ... SQL` instead of embedding the SQL directly in a double-quoted shell string.

### Metadata
- Source: error
- Related Files: .learnings/ERRORS.md
- Tags: mysql, shell, quoting

---

## [LRN-20260421-004] best_practice

**Logged**: 2026-04-21T23:52:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
`fliggy-order-list` can intermittently return `success=false` with “订单搜索失败，请稍后再试”; the client should retry instead of treating it as an empty business result.

### Details
During a full end-to-end validation of the six top-level ingestion commands, the order-list pipeline inserted `0 / 0 / 0` into `qianniu_fliggy_shop_daily_key_data`. The root cause was not SQL execution. The upstream HTTP endpoint occasionally returned a business-layer transient failure payload with `success=false`, `errorMsg=订单搜索失败，请稍后再试`, `total=0`, and an empty `orderList`. Reissuing the exact same request against the same date succeeded on later attempts and returned the expected 18 orders. The collector previously normalized this failure payload as if it were a valid empty day, which silently corrupted downstream ingestion.

### Suggested Action
Keep transient-failure retry logic in the order-list client and treat `success=false` business failures as retryable before normalizing the payload.

### Metadata
- Source: simplify-and-harden
- Related Files: src/tourism_automation/collectors/fliggy_order_list/client.py, tests/collectors/test_fliggy_order_list.py
- Tags: fliggy, order-list, retry, ingestion
- Pattern-Key: harden.transient_http_business_error
- Recurrence-Count: 1
- First-Seen: 2026-04-21
- Last-Seen: 2026-04-21

### Resolution
- **Resolved**: 2026-04-21T23:52:00+08:00
- **Commit/PR**: local workspace
- **Notes**: Added up to 5 attempts with a short delay for the known transient order-search failure and covered it with a unit test.

---
