# SentinelEdge Third-Party Licenses and Intellectual Property Notices

**Document Version:** 1.0.0  
**Effective Date:** November 21, 2026

---

SentinelEdge incorporates, interfaces with, or depends upon several open-source libraries and computer vision models. Below is an attribution and licensing summary for all core dependencies:

| Component | Upstream Project | License | Operational Usage |
| :--- | :--- | :--- | :--- |
| **YOLOv8** | [Ultralytics](https://github.com/ultralytics/ultralytics) | AGPL-3.0 / Commercial | Edge Object Detection (`yolov8n.pt`) |
| **ByteTrack** | [ByteTrack](https://github.com/ifzhang/ByteTrack) | MIT License | Multi-Object Tracking & Dwell-Time |
| **FastAPI** | [FastAPI](https://github.com/tiangolo/fastapi) | MIT License | High-Performance ASGI REST & WebSocket API |
| **Next.js 15** | [Vercel Next.js](https://github.com/vercel/next.js) | MIT License | Enterprise Web Operator Console |
| **React 19** | [Meta / Facebook](https://github.com/facebook/react) | MIT License | Declarative UI Framework |
| **PostgreSQL** | [PostgreSQL Global Development Group](https://www.postgresql.org) | PostgreSQL License | Relational State Store |
| **pgvector** | [pgvector](https://github.com/pgvector/pgvector) | PostgreSQL License | Vector Embeddings & Cosine Search Index |
| **Redis** | [Redis Ltd](https://redis.io) | BSD 3-Clause / RSALv2 / SSPL | Low-Latency Streaming Event Broker |
| **Sentence-Transformers** | [UKP Lab / HuggingFace](https://github.com/UKPLab/sentence-transformers) | Apache 2.0 | Dense Vector Text Embeddings (`all-MiniLM-L6-v2`) |
| **PyTorch** | [PyTorch Foundation](https://pytorch.org) | BSD-style | Deep Learning Tensor Runtime |
| **Tailwind CSS** | [Tailwind Labs](https://tailwindcss.com) | MIT License | Utility-First Responsive Styling |
| **Recharts** | [Recharts](https://github.com/recharts/recharts) | MIT License | Interactive Analytics Data Visualizations |
| **Lucide Icons** | [Lucide](https://lucide.dev) | ISC License | High-Contrast System Icons |
| **Nginx** | [Igor Sysoev / F5](https://nginx.org) | 2-Clause BSD | Reverse Proxy, Rate Limiting & TLS Termination |

---

## Model Licensing Advisory (Ultralytics YOLOv8)

Users and commercial deployers must take note of Ultralytics licensing terms:
* **Open-Source Deployments:** If you distribute derivative works incorporating YOLOv8 under open-source licenses compatible with AGPL-3.0, you may utilize YOLOv8 under the terms of the GNU Affero General Public License v3.0.
* **Commercial Proprietary Deployments:** If you deploy SentinelEdge commercially without open-sourcing your proprietary modifications or infrastructure wrappers, you are required to procure a commercial enterprise license directly from Ultralytics (see: [https://ultralytics.com/license](https://ultralytics.com/license)).
