# OT/IT Historian Replacement Architecture Prompt

## Purpose
This prompt is designed to generate credible, implementable open-source historian replacement architectures for manufacturing plants. It enforces reality checks on licensing, OPC UA capabilities, and HA claims that typical LLM responses often miss.

## Why Domain Knowledge Matters
Most LLM "solutions" fail in OT environments because they lack sufficient domain expertise behind the prompt. Common issues include:
- Confusing open standards vs open source (OPC UA is a standard; implementations can be OSS)
- Assuming HA/clustering exists in OSS editions where it may not
- Using incorrect port numbers (e.g., 62541 is a library name; OPC UA default is 4840)
- Assuming OPC UA Historical Access is always available (it depends on vendor servers)
- Missing that store-and-forward is mandatory in plants, not optional

This prompt addresses these gaps through explicit constraints and verification requirements.

---

## The Prompt

```
ROLE
You are an OT/IT integration architect and ISA-95 / Purdue practitioner designing plant-ready architectures (not slides). Your goal is a credible, implementable open-source historian replacement.

TASK
Design an OPEN-SOURCE-FIRST, on-prem architecture to replace a proprietary historian (PI/Aveva class) for a manufacturing plant.

CONTEXT (assume unless stated otherwise)
- Sources: DCS/PLC/SCADA via OPC UA (opc.tcp default port 4840) and Modbus where needed.
- OPC UA note: OPC UA is an open standard (not inherently "open-source"). Prefer open-source clients/stacks on the collector side; treat vendor OPC UA servers as external dependencies with variable capabilities.
- Goals: high-rate time-series + events/alarms, ISA-95 separation, long retention, easy queries, dashboards, alerts, and AI/ML access.
- Constraints: open-source-first, commodity x86/Linux, offline-capable (store-and-forward), strong cybersecurity (IEC 62443 mindset), minimal vendor lock-in.
- Assumption: storage/compute aren't the bottleneck; reliability, maintainability, and governance are.

NON-NEGOTIABLE REALITY CHECKS (must be enforced)

A) LICENSING REALITY CHECK
- For EVERY component, label license class: "Open-source", "Source-available", or "Commercial".
- If clustering/HA or key features require a paid license, state it explicitly and propose an OSS alternative.

B) OPC UA REALITY CHECK
- Do NOT assume OPC UA Historical Access exists. Mark any HistoryRead/backfill dependence as "depends on server support".
- Edge buffering/store-and-forward is mandatory, not optional.

C) HA REALITY CHECK
- Do NOT claim OSS clustering/HA unless you are confident it exists in OSS form.
- Clearly separate: (1) Single-node + backups, (2) True HA cluster.
- If HA is proposed, describe the HA pattern in plain terms (leader election / replication / failover) and call out dependencies.

OUTPUT FORMAT (MUST follow this exact structure, with headings 1–10)

0) Assumptions + "Needs Verification" List (max 10 bullets)
   - List what you assumed and what must be validated on the plant systems (OPC UA server capabilities, tag rates, etc.)

1) Architecture Diagram (ASCII)
   - Show ISA-95 layers, zones/conduits, and data flows.
   - Label protocols and key ports (OPC UA 4840, MQTT TLS 8883, DB ports).

2) Component List by ISA-95 Layer (L0–L4)
   - Provide 1–2 options per role.
   - For each option: license class + why chosen + key tradeoff.

3) Data Model
   - Tag namespace + asset hierarchy mapping (ISA-95)
   - MQTT UNS / Sparkplug optional: if used, include correct Sparkplug topic pattern (include message type)
   - Timestamp + quality semantics: source ts vs receipt ts; OPC UA status code mapping; dedupe key

4) Ingestion Patterns
   - OPC UA subscription strategy (sampling vs publishing; deadband/report-by-exception)
   - Buffering/store-and-forward: disk buffer, replay throttle, dedupe, reconnect behavior
   - Backfill/replay: clearly label "depends on server support" for HistoryRead; otherwise replay from edge buffer

5) Storage Choices (Compare)
   - TimescaleDB vs InfluxDB OSS vs openHistorian
   - Include: query model (SQL vs non-SQL), retention/compression, ecosystem maturity, and OSS HA feasibility

6) Security Design (IEC 62443 style)
   - Zones/conduits, firewall rule intent, identity model (certs/roles), authN/authZ
   - Cert management for OPC UA (mTLS), broker authN/authZ, DB RBAC
   - Secrets handling, patching cadence, logging/SIEM hooks

7) HA/DR
   - Failure modes: node loss, partitions, broker outage, DB fail
   - RPO/RTO targets WITH assumptions
   - Backup/restore (PITR where applicable), upgrade strategy (rolling vs blue-green)

8) Performance Sizing (Rough Math)
   - tags, sample rate, points/sec, bytes/point, retention, compression factor
   - expected storage growth and write IOPS
   - identify where bottlenecks appear first in real plants

9) Reality Checks (Plant pain points)
   - clock drift, cert expiry, tag explosion/cardinality, replay storms, flaky networks
   - mitigations + the exact metrics/alerts to monitor

10) PoC Plan (2 weeks)
    - Steps, test cases, acceptance criteria
    - Must include: controlled disconnect test, replay test, security config test, dashboard latency test
    - Define pass/fail criteria and how you measure them

HARD RULES
- Only claim features you can justify from official docs; if unsure, write "needs verification".
- Prefer plant-ready choices over trendy ones; keep the stack minimal.
- Avoid proprietary components unless there is no OSS equivalent; if used, label OPTIONAL and provide a strict OSS alternative.
- Ask no more than 3 clarification questions; otherwise proceed with stated assumptions.
- End with a Decision Table with 3 variants:
  (1) Strict OSS baseline, (2) OSS + source-available enhancements (optional), (3) Hybrid with commercial support (optional).
```

---

## How to Use This Prompt

1. **Copy the prompt** from the code block above
2. **Paste it** into your preferred LLM (ChatGPT, Claude, etc.)
3. **Optionally customize** the context section with your specific:
   - Tag counts and scan rates
   - Control system vendors (DeltaV, Aveva, Siemens, Rockwell, etc.)
   - HA requirements
4. **Review the output** against the reality checks - the LLM should explicitly state licensing classes and mark assumptions

## Expected Output Structure

The prompt forces the LLM to deliver:
- ✅ Explicit licensing reality (Open-source / Source-available / Commercial)
- ✅ OPC UA reality checks (no assumed Historical Access)
- ✅ HA reality checks (true cluster vs single-node)
- ✅ ASCII architecture diagram showing ISA-95 layers
- ✅ Component comparison tables
- ✅ Security zones/conduits (IEC 62443 style)
- ✅ Performance sizing math
- ✅ 2-week PoC plan with pass/fail criteria
- ✅ Decision table with 3 variants

## Common LLM Failure Modes in OT (That This Prompt Fixes)

| Issue | Why It Happens | How This Prompt Fixes It |
|-------|----------------|-------------------------|
| Claims OSS clustering when it's commercial | LLM trained on marketing docs | Forces explicit license class labels |
| Assumes OPC UA Historical Access exists | Common in samples, rare in reality | Mandatory "needs verification" notes |
| Wrong port numbers (62541 vs 4840) | Confusion between library names and ports | Explicit port specification required |
| Missing store-and-forward | Treats as "nice to have" | Labels as mandatory, not optional |
| Vague HA claims | No operational detail | Requires plain-language HA pattern description |

## Related Resources

- [ISA-95 Enterprise-Control System Integration](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa95)
- [IEC 62443 Industrial Security Standards](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa99)
- [OPC UA Specification](https://opcfoundation.org/about/opc-technologies/opc-ua/)
- [Sparkplug Specification](https://sparkplug.eclipse.org/specification/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Grafana OT/SCADA Solutions](https://grafana.com/solutions/iot-monitoring/)

## Contributing

If you use this prompt and find ways to improve it, please share your refinements! Common areas for enhancement:
- Additional reality checks for specific control systems
- More detailed PoC test cases
- Expanded security requirements for specific industries (pharma, oil & gas, etc.)

## License

This prompt template is provided as-is for public use. Attribution appreciated but not required.

---

**Author**: Ranga Seshadri (rangabb@gmail.com)  
**LinkedIn**: [in/rangas](https://linkedin.com/in/rangas)  
**Medium**: [@rangabb](https://medium.com/@rangabb)  
**Repository**: [github.com/ranga291257/astra](https://github.com/ranga291257/astra)
