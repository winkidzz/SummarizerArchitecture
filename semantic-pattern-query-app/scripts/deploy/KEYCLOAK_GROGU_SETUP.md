# Keycloak Installation on Grogu Server

**Date**: 2025-11-22  
**User**: winkidzz  
**Server**: grogu

## ✅ Installation Summary

### Keycloak Details
- **Version**: 26.4.5 (latest)
- **Java Version**: OpenJDK 21.0.9 LTS
- **Container**: `keycloak`
- **Status**: ✅ Running
- **Framework**: Quarkus 3.27.0

### Ports
- **HTTP**: 8080 (external) → 8080 (internal)
- **HTTPS**: 8443 (external) → 8443 (internal)
- **Management**: 9000 (internal only)

### Network
- **Docker Network**: `monitoring` (shared with Prometheus/Grafana)

### Storage
- **Data Volume**: `keycloak_data` (persistent)

## 🔐 Admin Credentials

- **Username**: `admin`
- **Password**: `admin`
- **⚠️ Important**: Change the password in production!

## 🌐 Access URLs

From other machines:
- **Admin Console**: `http://grogu:8080` or `http://192.168.1.100:8080`
- **Admin Console Direct**: `http://grogu:8080/admin`
- **Master Realm**: `http://grogu:8080/realms/master`

## 📋 Installation Details

### Container Information
```bash
Container Name: keycloak
Image: quay.io/keycloak/keycloak:latest
Status: Running
Ports: 8080:8080, 8443:8443
```

### Environment Variables
- `KEYCLOAK_ADMIN=admin` (deprecated, use `KC_BOOTSTRAP_ADMIN_USERNAME`)
- `KEYCLOAK_ADMIN_PASSWORD=admin` (deprecated, use `KC_BOOTSTRAP_ADMIN_PASSWORD`)
- `KC_HEALTH_ENABLED=true`
- `KC_METRICS_ENABLED=true`

### Startup Command
```bash
start-dev  # Development mode (not for production)
```

## 🛠️ Management Commands

### Start Keycloak
```bash
ssh winkidzz@grogu "docker start keycloak"
```

### Stop Keycloak
```bash
ssh winkidzz@grogu "docker stop keycloak"
```

### Restart Keycloak
```bash
ssh winkidzz@grogu "docker restart keycloak"
```

### View Logs
```bash
ssh winkidzz@grogu "docker logs keycloak -f"
```

### Check Status
```bash
ssh winkidzz@grogu "docker ps | grep keycloak"
```

### Verify Java Version
```bash
ssh winkidzz@grogu "docker exec keycloak java -version"
```

### Check Health
```bash
ssh winkidzz@grogu "curl http://localhost:8080/health"
```

## 🔧 Configuration

### Production Setup (Recommended)

For production use, you should:

1. **Use production mode** instead of `start-dev`:
   ```bash
   docker run -d --name keycloak \
     --network monitoring \
     -p 8080:8080 \
     -p 8443:8443 \
     -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
     -e KC_BOOTSTRAP_ADMIN_PASSWORD=your-secure-password \
     -e KC_HEALTH_ENABLED=true \
     -e KC_METRICS_ENABLED=true \
     -e KC_DB=postgres \
     -e KC_DB_URL_HOST=localhost \
     -e KC_DB_URL_DATABASE=keycloak \
     -e KC_DB_USERNAME=keycloak \
     -e KC_DB_PASSWORD=keycloak_password \
     -v keycloak_data:/opt/keycloak/data \
     quay.io/keycloak/keycloak:latest \
     start
   ```

2. **Connect to PostgreSQL** (already available on grogu):
   - Use PostgreSQL 17.5 on port 5432
   - Create a dedicated database for Keycloak

3. **Enable HTTPS**:
   - Configure SSL certificates
   - Use port 8443 for HTTPS

4. **Change admin password**:
   - Log in to admin console
   - Go to Account → Password

## 📊 Verification

### Check if Keycloak is Running
```bash
ssh winkidzz@grogu "docker ps | grep keycloak"
```

### Verify Java 21
```bash
ssh winkidzz@grogu "docker exec keycloak java -version"
# Should show: openjdk version "21.0.9"
```

### Test Admin Console
1. Open browser: `http://grogu:8080/admin`
2. Login with: `admin` / `admin`
3. Should see Keycloak admin console

### Check Health Endpoint
```bash
curl http://grogu:8080/health
```

### Check Metrics (if enabled)
```bash
curl http://grogu:8080/metrics
```

## 🔗 Integration with Other Services

Keycloak is on the `monitoring` network, so it can communicate with:
- Prometheus (for metrics scraping)
- Grafana (for monitoring dashboards)

## 📝 Notes

- **Development Mode**: Currently running in `start-dev` mode (not for production)
- **Java 21**: Confirmed using OpenJDK 21.0.9 LTS
- **Data Persistence**: Data stored in Docker volume `keycloak_data`
- **Network**: Connected to `monitoring` network for service discovery

## 🚀 Next Steps

1. **Access Admin Console**: `http://grogu:8080/admin`
2. **Change Admin Password**: Security best practice
3. **Create Realms**: Set up realms for your applications
4. **Configure Clients**: Add OAuth2/OIDC clients
5. **Set up Users**: Create user accounts
6. **Configure Identity Providers**: Add social logins if needed
7. **Enable Production Mode**: Switch from dev to production mode
8. **Connect to PostgreSQL**: Use existing PostgreSQL 17.5 for production

## 🔒 Security Recommendations

1. Change default admin password immediately
2. Use production mode for production deployments
3. Enable HTTPS/TLS
4. Use strong database passwords
5. Regularly update Keycloak image
6. Configure proper firewall rules
7. Enable audit logging
8. Use environment variables for sensitive data

