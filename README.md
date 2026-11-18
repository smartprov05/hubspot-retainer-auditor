# HubSpot Retainer & Burn Rate Auditor CLI

[![CI](https://github.com/smartprov05/hubspot-retainer-auditor/actions/workflows/ci.yml/badge.svg)](https://github.com/smartprov05/hubspot-retainer-auditor/actions/workflows/ci.yml)

A lightweight, zero-dependency Python script to audit client retainer balances, track billable hours burn, and detect unbilled revenue leakage directly in **HubSpot CRM**.

---

## The Problem
Digital agencies, consultancies, and MSPs frequently bill on prepaid monthly retainer hours (e.g., 20 hours/mo). But because HubSpot CRM lacks native retainer wallets and prepaid drawdown tracking:
1. **Unbilled Overages:** Reps keep logging time after the retainer block is exhausted. The agency leaks hundreds or thousands of dollars in unbilled work.
2. **Surprise Invoices:** Clients get surprised by end-of-month overage bills without advance notice.
3. **Late Top-Up Deals:** Account managers don't know a retainer is almost empty until payroll/invoicing time.

This CLI connects to your HubSpot portal, analyzes client company retainer properties, and flags accounts in overage or near exhaustion.

---

## Quick Start

### 1. Requirements
- Python 3.6+ (uses only standard library `urllib`, `json`, `os`, `sys`).
- A HubSpot **Private App Token** with:
  - `crm.objects.companies.read`
  - `crm.objects.tickets.read`

### 2. Run the Script
```bash
# 1. Set your HubSpot Private App Token
export HUBSPOT_ACCESS_TOKEN="pat-na1-xxxxxx"

# 2. (Optional) Set your agency's average billable hourly rate (default: $150/hr)
export AGENCY_HOURLY_RATE="175.0"

# 3. Run the audit
python3 audit_retainers.py
```

### 3. Example Terminal Output
```text
==========================================================
      HubSpot Agency Retainer & Burn Rate Auditor         
==========================================================
Audit Assumptions: Default Billable Rate = $175.00/hr

Audited 42 client companies from HubSpot CRM.

--- 1. OVERAGE ALERTS (Unbilled Revenue Leakage) ---
⚠️  Acme Global (acme.com):
    Allocated: 20.0 hrs | Used: 24.5 hrs | Overage: 4.5 hrs
    Estimated Unbilled Work: $787.50

Total Leaked Revenue: $1,575.00 across 2 clients.

--- 2. LOW-BALANCE ALERTS (Upcoming Renewal Triggers) ---
🔔 TechCorp Inc: 3.5 hrs remaining (18% of 20.0 hrs allocated).
    Action: Stage a top-up renewal deal before hours run dry.
```

---

## Automated In-CRM Retainer Management

If you want automated time tracking on HubSpot Tickets and Deals, FIFO block drawdowns, low-balance warnings, and automated top-up deal creation without running custom scripts, check out **Retainer Wallet for HubSpot**:

- **Native CRM Time Tracking:** Start timers or log time directly inside HubSpot Ticket and Deal records.
- **Prepaid Retainer Wallets:** Automatically draws down hours from active retainer blocks (oldest first).
- **Automated Top-Up Deals:** Creates a renewal deal in your sales pipeline when a client reaches 20% remaining balance.
- **Client Statements:** Generates 1-click itemized monthly PDF and CSV statements for clients.

👉 **Learn more and install:** [Retainer Wallet for HubSpot](https://kayabyte.dev/hubspot/retainer-wallet/?src=c-gh-retainer)  
*(Free tier available for up to 3 retainers. Installs directly into HubSpot)*.
