# SentinelEdge Acceptable Use Policy (AUP)

**Effective Date:** November 21, 2026  
**Document Version:** 1.0.0  
**Enforcement Level:** Mandatory for All Deployments, Integrations, and Forks

---

## 1. Purpose and Scope

This Acceptable Use Policy ("AUP") defines the mandatory ethical, operational, and legal boundaries governing the installation, execution, and deployment of the SentinelEdge Edge Computer Vision & Incident Intelligence Platform. 

SentinelEdge was created to enhance physical facility safety, protect perimeter boundaries, and assist emergency responders while **strictly upholding individual human dignity and privacy**. Any deployment that undermines personal privacy or violates fundamental human rights constitutes a breach of this policy and revokes the deployer's right to utilize the platform.

---

## 2. Permitted and Intended Use Cases

SentinelEdge is explicitly authorized for use in the following operational environments:

### 2.1. Industrial & Occupational Safety
* **Hazard Zone Clearance:** Detecting unauthorized presence in dangerous industrial work cells, chemical storage areas, or heavy machinery operational envelopes.
* **Emergency Route Clearance:** Ensuring fire exits, emergency ambulance bays, and industrial evacuation paths remain unblocked by vehicles or cargo.
* **Perimeter Intrusion Detection:** Securing outer facility fences, data center perimeters, and logistics yards against unauthorized off-hours intrusion.

### 2.2. Commercial & Public Venue Management
* **Crowd Density Monitoring:** Quantifying spatial density in public transit hubs, concourses, and stadiums to prevent crowd surges and bottlenecks without identifying individuals.
* **Traffic Flow & Vehicle Congestion:** Analyzing vehicle flow and dwell times at commercial loading gates, toll portals, and parking ingress points.
* **Asset Protection:** Safeguarding unattended infrastructure, energy substations, and telecommunications towers against sabotage.

---

## 3. Strictly Prohibited Uses

The following uses of SentinelEdge are **strictly prohibited across all jurisdictions**:

| Prohibited Category | Specific Disallowed Activity |
| :--- | :--- |
| **Mass Biometric Surveillance** | Implementing facial recognition databases, automated identity matching, or tracking named individuals across public spaces. |
| **Demographic & Discriminatory Profiling** | Inferring, classifying, or alerting based on race, ethnicity, religious dress, gender, disability, sexual orientation, or perceived political affiliation. |
| **Private Space Surveillance** | Positioning camera sensors in restrooms, locker rooms, employee break areas, prayer spaces, or private residential quarters. |
| **Worker Harassment & Anti-Unionization** | Utilizing spatial dwell-time monitoring to micro-manage, penalize, or intimidate workers, or to monitor lawful union organizing activities. |
| **Unlawful Covert Surveillance** | Operating hidden or concealed cameras in public venues without statutory warning signage required by local law. |
| **Weaponized & Military Systems** | Integrating SentinelEdge into autonomous weapons, loitering munitions, combat targeting systems, or armed defense drones. |
| **Tampering with Anonymization** | Intentionally disabling, modifying, or bypassing the in-memory Gaussian face blurring and license plate masking engines to harvest raw PII. |

---

## 4. Operational Guardrails

All deployers must implement the following operational safeguards:
1. **Physical Signage:** Prominently display physical signage at all access points declaring: *"Premises monitored by automated privacy-preserving edge computer-vision sensors for security and safety."*
2. **Access Control:** Enforce multi-factor or strong password authentication for operator accounts. Do not share master `admin` credentials across multiple operators.
3. **Audit Trail Review:** Periodically inspect the PostgreSQL incident audit logs (`incident_audits` table) to verify operators are not abusing search queries or incident review tools.
4. **Data Retention Limits:** Configure automatic pruning of incident metadata (default: 30 days) to prevent permanent historical record hoarding.

---

## 5. Violations and License Revocation

Any deployer, organization, or user found to be utilizing SentinelEdge in violation of this Acceptable Use Policy:
* Forfeits all rights and permissions granted under the Apache 2.0 software license.
* Must immediately cease execution and destroy all local container instances and binary builds of the software.
* May be reported to relevant data protection authorities (e.g., EU Data Protection Authorities, FTC) for statutory privacy enforcement.
