# Pmoves-cipher — Hyperdimensions Integration Dossier

_Last updated: 2026-02-16_
_Branch variant: `PMOVES.AI-Edition-Hardened-Cipher`_
_Topology file: `saves/Pmoves-cipher_topology.json`_

---

## 1. Module Identity

| Field | Value |
|-------|-------|
| **Submodule** | `Pmoves-cipher` |
| **Branch Suffix** | `-Cipher` |
| **Primary Type(s)** | data |
| **Evolution Stage** | base — Base form (1-2 layers, single type) |
| **Ports** | 8096 (Cipher Memory) |

## 2. Purpose in PMOVES.AI

This dossier documents the hyperdimensional display configuration for `Pmoves-cipher`.
The topology JSON renders this submodule's agents and services on a Poincare disk,
with CHIT geometry state vector driving the surface deformation.

## 3. Agent Roster

| Agent | Class | Type | Port | Stage | Description |
|-------|-------|------|------|-------|-------------|
| Cipher Memory | specialized | data/agent | 8096 | base | Knowledge-graph memory for agents (Neo4j backend) |

## 4. Layer Coverage

| Layer | Active | Description |
|-------|--------|-------------|
| L0 | yes | Identity Anchors (325 persona anchors) |
| L1 | no | Orchestrators (control-plane coordination) |
| L2 | no | Bus + Routing (NATS transport, gateway routing) |
| L2.5 | no | Hyperdimensions (geometry state visualization + control knobs) |
| L3 | no | Swarm Intelligence (EvoSwarm, role-based packs) |
| L4 | no | Modal Intelligence (text LLM, audio/TTS/STT, VLM) |
| L5 | yes | Memory + Safety (persistent storage, CHIT manifests, sandboxes) |

## 5. CHIT Toggle Sensitivity

| Toggle | Active |
|--------|--------|
| delta | no |
| kappa | no |
| hz | no |
| swarm | no |
| attribution | no |

These toggles determine whether this submodule's agents respond to geometry
state vector changes from the Hyperdimensions control plane (L2.5).

## 6. NATS Subjects

### Publishes
- None

### Subscribes
- None

## 7. Health Endpoints

- `/health` on port 8096

## 8. Topology Configuration

- **Poincare Disk Model**: Agents positioned by class (ring) and type (sector)
- **Surface Height**: Driven by CHIT toggle density x evolution stage multiplier
- **Color Encoding**: Primary type color modulated by readiness
- **Animation**: delta, fitness, hz parameters oscillate to show state dynamics

### Geometry State Vector Defaults

| Parameter | Default | Driven By |
|-----------|---------|-----------|
| delta | 0.2 | Tree-likeness sensitivity |
| kappa | 0.0 | Hierarchy pressure |
| hz | 0.1 | Spectral entropy |
| fitness | 0.5 | Swarm participation |
| attribution | 0.4 | Attribution gating |

## 9. Cross-References

- **Service Catalog**: [`.claude/context/services-catalog.md`](../../.claude/context/services-catalog.md)
- **CHIT Integration**: [`pmoves/docs/PMOVESCHIT/GEOMETRY_BUS_INTEGRATION.md`](../../pmoves/docs/PMOVESCHIT/GEOMETRY_BUS_INTEGRATION.md)
- **Agent Taxonomy**: [`pmoves/docs/AGENTS/PMOVES_AGENT_CLASS_TAXONOMY.md`](../../pmoves/docs/AGENTS/PMOVES_AGENT_CLASS_TAXONOMY.md)
- **NATS Subjects**: [`.claude/context/nats-subjects.md`](../../.claude/context/nats-subjects.md)
- **Submodule Docs**: [`Pmoves-cipher/README.md`](../../Pmoves-cipher/README.md)
- **Global Topology**: [`saves/agent_topology.json`](../saves/agent_topology.json)

## 10. Owner / Audit

| Field | Value |
|-------|-------|
| Owning lane | L2.5 Hyperdimensions |
| Integration audit | 2026-02-16 |
| Registry source | `pmoves/config/agent_registry.yaml` |
