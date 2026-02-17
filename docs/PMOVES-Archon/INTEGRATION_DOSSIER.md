# PMOVES-Archon — Hyperdimensions Integration Dossier

_Last updated: 2026-02-16_
_Branch variant: `PMOVES.AI-Edition-Hardened-Archon`_
_Topology file: `saves/PMOVES-Archon_topology.json`_

---

## 1. Module Identity

| Field | Value |
|-------|-------|
| **Submodule** | `PMOVES-Archon` |
| **Branch Suffix** | `-Archon` |
| **Primary Type(s)** | agent |
| **Evolution Stage** | stage_2 — Stage 2 (5+ layers, CHIT-enabled, publishes/consumes CGP packets) |
| **Ports** | 8091 (Archon) |

## 2. Purpose in PMOVES.AI

This dossier documents the hyperdimensional display configuration for `PMOVES-Archon`.
The topology JSON renders this submodule's agents and services on a Poincare disk,
with CHIT geometry state vector driving the surface deformation.

## 3. Agent Roster

| Agent | Class | Type | Port | Stage | Description |
|-------|-------|------|------|-------|-------------|
| Archon | standard | agent/llm | 8091 | stage_2 | Supabase-driven planning/execution copilot |

## 4. Layer Coverage

| Layer | Active | Description |
|-------|--------|-------------|
| L0 | yes | Identity Anchors (325 persona anchors) |
| L1 | yes | Orchestrators (control-plane coordination) |
| L2 | yes | Bus + Routing (NATS transport, gateway routing) |
| L2.5 | yes | Hyperdimensions (geometry state visualization + control knobs) |
| L3 | no | Swarm Intelligence (EvoSwarm, role-based packs) |
| L4 | yes | Modal Intelligence (text LLM, audio/TTS/STT, VLM) |
| L5 | yes | Memory + Safety (persistent storage, CHIT manifests, sandboxes) |

## 5. CHIT Toggle Sensitivity

| Toggle | Active |
|--------|--------|
| delta | yes |
| kappa | yes |
| hz | yes |
| swarm | no |
| attribution | yes |

These toggles determine whether this submodule's agents respond to geometry
state vector changes from the Hyperdimensions control plane (L2.5).

## 6. NATS Subjects

### Publishes
- None

### Subscribes
- None

## 7. Health Endpoints

- `/healthz` on port 8091

## 8. Topology Configuration

- **Poincare Disk Model**: Agents positioned by class (ring) and type (sector)
- **Surface Height**: Driven by CHIT toggle density x evolution stage multiplier
- **Color Encoding**: Primary type color modulated by readiness
- **Animation**: delta, fitness, hz parameters oscillate to show state dynamics

### Geometry State Vector Defaults

| Parameter | Default | Driven By |
|-----------|---------|-----------|
| delta | 0.7 | Tree-likeness sensitivity |
| kappa | -0.5 | Hierarchy pressure |
| hz | 0.6 | Spectral entropy |
| fitness | 0.5 | Swarm participation |
| attribution | 0.95 | Attribution gating |

## 9. Cross-References

- **Service Catalog**: [`.claude/context/services-catalog.md`](../../.claude/context/services-catalog.md)
- **CHIT Integration**: [`pmoves/docs/PMOVESCHIT/GEOMETRY_BUS_INTEGRATION.md`](../../pmoves/docs/PMOVESCHIT/GEOMETRY_BUS_INTEGRATION.md)
- **Agent Taxonomy**: [`pmoves/docs/AGENTS/PMOVES_AGENT_CLASS_TAXONOMY.md`](../../pmoves/docs/AGENTS/PMOVES_AGENT_CLASS_TAXONOMY.md)
- **NATS Subjects**: [`.claude/context/nats-subjects.md`](../../.claude/context/nats-subjects.md)
- **Submodule Docs**: [`PMOVES-Archon/README.md`](../../PMOVES-Archon/README.md)
- **Global Topology**: [`saves/agent_topology.json`](../saves/agent_topology.json)

## 10. Owner / Audit

| Field | Value |
|-------|-------|
| Owning lane | L2.5 Hyperdimensions |
| Integration audit | 2026-02-16 |
| Registry source | `pmoves/config/agent_registry.yaml` |
