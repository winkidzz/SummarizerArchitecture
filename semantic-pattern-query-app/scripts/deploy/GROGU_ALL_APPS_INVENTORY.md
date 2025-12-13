# Grogu Server - Complete Application Inventory

**Date**: 2025-11-22  
**Server IP**: 192.168.1.100  
**Hostname**: grogu  
**User**: winkidzz

---

## 📋 Applications & Services Overview

### 🔐 Authentication & Identity Management

#### 1. **Keycloak** (Identity & Access Management)
- **Container**: `keycloak`
- **Image**: `quay.io/keycloak/keycloak:latest`
- **Version**: 26.4.5
- **Ports**: 
  - HTTP: `8080` (external) → `8080` (internal)
  - HTTPS: `8443` (external) → `8443` (internal)
  - Management: `9000` (internal only)
- **URLs**:
  - Admin Console: `http://grogu:8080/admin` or `http://192.168.1.100:8080/admin`
  - Master Realm: `http://grogu:8080/realms/master`
  - OpenID Config: `http://grogu:8080/realms/master/.well-known/openid-configuration`
- **Credentials**:
  - Username: `admin`
  - Password: `admin`
- **Status**: ✅ Running
- **Java**: OpenJDK 21.0.9 LTS
- **Network**: `monitoring`

---

### 📊 Monitoring & Observability

#### 2. **Grafana** (Monitoring Dashboards)
- **Container**: `rag-grafana`
- **Image**: `grafana/grafana:latest`
- **Version**: 12.3.0
- **Ports**: `3333` (external) → `3000` (internal)
- **URLs**:
  - Web UI: `http://grogu:3333` or `http://192.168.1.100:3333`
  - Health: `http://grogu:3333/api/health`
- **Credentials**:
  - Username: `admin`
  - Password: `admin`
- **Status**: ✅ Running (20 hours uptime)
- **Network**: `monitoring`
- **Features**: 6 RAG dashboards loaded

#### 3. **Prometheus** (Metrics Collection)
- **Container**: `rag-prometheus`
- **Image**: `prom/prometheus:latest`
- **Ports**: `9090` (external) → `9090` (internal)
- **URLs**:
  - Web UI: `http://grogu:9090` or `http://192.168.1.100:9090`
  - Health: `http://grogu:9090/-/healthy`
  - API: `http://grogu:9090/api/v1/`
- **Credentials**: None (no authentication by default)
- **Status**: ✅ Running (20 hours uptime)
- **Network**: `monitoring`
- **Config**: Scrapes RAG API and self

#### 4. **Netdata** (Real-time System Monitoring)
- **Container**: `captain-netdata-container`
- **Image**: `caprover/netdata:v1.34.1`
- **Ports**: `19999` (internal, via CapRover)
- **URLs**: Accessible via CapRover dashboard
- **Credentials**: Via CapRover
- **Status**: ✅ Running (3 weeks uptime)

---

### 🗄️ Databases & Storage

#### 5. **PostgreSQL 17.5** (Primary Database)
- **Type**: System service (not Docker)
- **Version**: PostgreSQL 17.5
- **Ports**: `5432` (listening on all interfaces)
- **URLs**:
  - Connection: `grogu:5432` or `192.168.1.100:5432`
- **Credentials**: 
  - Default user: `postgres`
  - User databases: `winkidzz`, `audio_storage_db`
- **Status**: ✅ Running
- **Extensions**: pgvector 0.8.0 (vector search)
- **Databases**: `postgres`, `winkidzz`, `audio_storage_db`

#### 6. **PostgreSQL 12.22** (Legacy)
- **Type**: System service
- **Version**: PostgreSQL 12.22
- **Ports**: `5433` (if configured)
- **Status**: ✅ Running

#### 7. **PostgreSQL (n8n Database)**
- **Container**: `srv-captain--n8n-db.1.7ccrtt2l9gf21wyi4t7wtxfus`
- **Image**: `postgres:17.5-alpine`
- **Ports**: `5432` (internal, Docker network)
- **Credentials**:
  - Username: `n8n`
  - Password: `prasanna`
  - Database: `n8n`
- **Status**: ✅ Running (16 hours uptime)

#### 8. **Elasticsearch 8.19.7** (Search Engine)
- **Container**: `semantic-elasticsearch`
- **Image**: `docker.elastic.co/elasticsearch/elasticsearch:8.19.7`
- **Ports**: 
  - HTTP: `9200` (external) → `9200` (internal)
  - Cluster: `9300` (external) → `9300` (internal)
- **URLs**:
  - API: `http://grogu:9200` or `http://192.168.1.100:9200`
  - Health: `http://grogu:9200/_cluster/health`
- **Credentials**: None (security disabled)
- **Status**: ✅ Running (21 hours uptime, healthy)
- **Cluster**: Single-node, status: yellow (normal)

#### 9. **Elasticsearch (CapRover)**
- **Container**: `srv-captain--elasticsearch.1.j9fbnccvv5ffcpd9u84os95p9`
- **Image**: `docker.elastic.co/elasticsearch/elasticsearch:8.19.7`
- **Ports**: `9200`, `9300` (internal, Docker network)
- **Status**: ✅ Running (16 hours uptime)
- **Access**: Via CapRover

#### 10. **Redis 7.2-alpine** (Cache)
- **Container**: `semantic-redis`
- **Image**: `redis:7.2-alpine`
- **Ports**: `6380` (external) → `6379` (internal)
- **URLs**:
  - Connection: `grogu:6380` or `192.168.1.100:6380`
- **Credentials**: None (no password by default)
- **Status**: ✅ Running (21 hours uptime, healthy)

#### 11. **Qdrant v1.16.0** (Vector Database)
- **Container**: `qdrant`
- **Image**: `qdrant/qdrant:v1.16.0`
- **Ports**: 
  - HTTP: `6333` (external) → `6333` (internal)
  - gRPC: `6334` (external) → `6334` (internal)
- **URLs**:
  - HTTP API: `http://grogu:6333` or `http://192.168.1.100:6333`
  - Health: `http://grogu:6333/healthz`
- **Credentials**: None
- **Status**: ✅ Running (21 hours uptime)
- **Storage**: `~/qdrant_storage` (host volume)

#### 12. **Neo4j** (Graph Database)
- **Container**: `srv-captain--neo4j-db.1.k30a45nxbd3xu7utjzg0ilmla`
- **Image**: `neo4j:community-ubi9`
- **Ports**: `7473`, `7474`, `7687` (internal, Docker network)
- **Status**: ✅ Running
- **Access**: Via CapRover

---

### 🚀 Application Platforms

#### 13. **CapRover** (Self-Hosting Platform)
- **Container**: `captain-captain.1.1z84dvzonqmh1k8mfgnuibfqo`
- **Image**: `caprover/caprover:1.14.1`
- **Ports**: `3000` (external) → `3000` (internal)
- **URLs**:
  - Dashboard: `http://grogu:3000` or `http://192.168.1.100:3000`
- **Credentials**: Set during initial setup (check CapRover docs)
- **Status**: ✅ Running (16 hours uptime)
- **Purpose**: Self-hosting platform for managing apps

#### 14. **GitLab CE** (DevOps Platform)
- **Container**: `srv-captain--gitlab.1.m9vu05kb1oult7ks38fglgn5t`
- **Image**: `gitlab/gitlab-ce:latest`
- **Ports**: `22`, `80`, `443` (internal, via CapRover/Nginx)
- **URLs**: Accessible via CapRover domain
- **Credentials**: 
  - Initial root password: Check `/etc/gitlab/initial_root_password` in container
  - Or use GitLab's password reset
- **Status**: ✅ Running (16 hours uptime, healthy)
- **Database**: Embedded PostgreSQL

#### 15. **n8n** (Workflow Automation)
- **Container**: `srv-captain--n8n.1.p6dy7xse7hq8yz2b54xgut9cv`
- **Image**: `n8nio/n8n:stable`
- **Ports**: `5678` (internal, via CapRover)
- **URLs**: Accessible via CapRover domain
- **Credentials**: Set during first login
- **Status**: ✅ Running (16 hours uptime)
- **Database**: PostgreSQL (n8n-db container)
  - Username: `n8n`
  - Password: `prasanna`

#### 16. **Home Assistant** (Home Automation)
- **Container**: `srv-captain--ha.1.5eyoatnnbv1hm4ynzpchphp45`
- **Image**: `ghcr.io/home-assistant/home-assistant:2025.2.1`
- **Ports**: Internal (via CapRover)
- **URLs**: Accessible via CapRover domain
- **Status**: ✅ Running (16 hours uptime)

#### 17. **WhisperCapRover** (Audio Processing)
- **Container**: `srv-captain--whispercaprover.1.lwe6enzzxqizda79mtrbr66a3`
- **Image**: `ishworksregistry.captain.ishworks.website/whispercaprover:latest`
- **Ports**: `80` (internal, via CapRover)
- **Status**: ✅ Running (16 hours uptime, healthy)

---

### 🌐 Infrastructure Services

#### 18. **Nginx** (Reverse Proxy)
- **Container**: `captain-nginx.1.b5pajylbobva1h52yk7z1ualx`
- **Image**: `nginx:1.27.2`
- **Ports**: 
  - HTTP: `80` (external) → `80` (internal)
  - HTTPS: `443` (external) → `443` (internal)
- **URLs**: 
  - HTTP: `http://grogu` or `http://192.168.1.100`
  - HTTPS: `https://grogu` or `https://192.168.1.100`
- **Status**: ✅ Running (16 hours uptime)
- **Purpose**: Reverse proxy for CapRover apps

#### 19. **Docker Registry**
- **Container**: `captain-registry.1.i1jhetcq4ukqx7npn811tvsbj`
- **Image**: `registry:2`
- **Ports**: `5000` (internal, Docker network)
- **Status**: ✅ Running (16 hours uptime)
- **Purpose**: Private Docker registry

#### 20. **Docker Registry (ishworks)**
- **Container**: `srv-captain--ishworksregistry.1.wwm7z6vk224gl55s7sa8or5m8`
- **Image**: `registry:2`
- **Ports**: `5000` (internal, Docker network)
- **Status**: ✅ Running (16 hours uptime)

#### 21. **Certbot** (SSL Certificate Management)
- **Container**: `captain-certbot.1.f41657pzkvk3g253hqndl6f7i`
- **Image**: `caprover/certbot-sleeping:v2.11.0`
- **Ports**: `80`, `443` (internal)
- **Status**: ✅ Running (16 hours uptime)
- **Purpose**: Automatic SSL certificate management

#### 22. **GoAccess** (Web Log Analyzer)
- **Container**: `captain-goaccess-container`
- **Image**: `caprover/goaccess:1.9.3`
- **Ports**: `7890` (internal, via CapRover)
- **Status**: ✅ Running (16 hours uptime)
- **Access**: Via CapRover dashboard

#### 23. **GitLab Runner** (CI/CD)
- **Container**: `srv-captain--gitlabrunner.1.uvexig2ipsuooaxd2wy4y3f34`
- **Image**: `gitlab/gitlab-runner:v18.2.1`
- **Status**: ✅ Running (16 hours uptime)
- **Purpose**: GitLab CI/CD runner

---

## 📊 Port Summary

| Port | Service | Access |
|------|---------|--------|
| 22 | SSH | `ssh winkidzz@grogu` |
| 80 | Nginx (HTTP) | Public |
| 443 | Nginx (HTTPS) | Public |
| 3000 | CapRover Dashboard | `http://grogu:3000` |
| 3333 | Grafana | `http://grogu:3333` |
| 5432 | PostgreSQL | `grogu:5432` |
| 5678 | n8n | Via CapRover |
| 6333 | Qdrant HTTP | `http://grogu:6333` |
| 6334 | Qdrant gRPC | `grogu:6334` |
| 6380 | Redis | `grogu:6380` |
| 7473-7474 | Neo4j | Via CapRover |
| 7687 | Neo4j Bolt | Via CapRover |
| 8080 | Keycloak HTTP | `http://grogu:8080` |
| 8443 | Keycloak HTTPS | `https://grogu:8443` |
| 9090 | Prometheus | `http://grogu:9090` |
| 9200 | Elasticsearch | `http://grogu:9200` |
| 9300 | Elasticsearch Cluster | `grogu:9300` |

---

## 🔑 Credentials Summary

### Authentication Services
- **Keycloak**: `admin` / `admin`
- **Grafana**: `admin` / `admin`

### Databases
- **PostgreSQL (n8n)**: `n8n` / `prasanna`
- **PostgreSQL (System)**: User-specific (check with `psql -l`)

### CapRover Apps
- Access credentials set during initial setup or first login
- Check CapRover dashboard for app-specific credentials

---

## 🌐 Access URLs Summary

### Direct Access (No Domain Required)
- **Keycloak**: `http://grogu:8080/admin` or `http://192.168.1.100:8080/admin`
- **Grafana**: `http://grogu:3333` or `http://192.168.1.100:3333`
- **Prometheus**: `http://grogu:9090` or `http://192.168.1.100:9090`
- **CapRover**: `http://grogu:3000` or `http://192.168.1.100:3000`
- **Qdrant**: `http://grogu:6333` or `http://192.168.1.100:6333`
- **Elasticsearch**: `http://grogu:9200` or `http://192.168.1.100:9200`

### Via CapRover (Domain-Based)
- GitLab, n8n, Home Assistant, and other apps are accessible via CapRover domains
- Check CapRover dashboard for specific URLs

---

## 📝 Notes

1. **Security**: Change default passwords for production use
2. **Network**: Most services are on Docker networks (monitoring, captain-default)
3. **CapRover**: Manages most applications via reverse proxy
4. **PostgreSQL**: Multiple instances (system, n8n, GitLab embedded)
5. **Elasticsearch**: Two instances (semantic-elasticsearch, CapRover ES)

---

## 🛠️ Quick Commands

### View All Containers
```bash
ssh winkidzz@grogu "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

### Check Service Health
```bash
# Keycloak
curl http://grogu:8080/health

# Grafana
curl http://grogu:3333/api/health

# Prometheus
curl http://grogu:9090/-/healthy

# Elasticsearch
curl http://grogu:9200/_cluster/health

# Qdrant
curl http://grogu:6333/healthz
```

### View Logs
```bash
ssh winkidzz@grogu "docker logs <container-name> -f"
```

---

**Last Updated**: 2025-11-22  
**Maintained By**: winkidzz

