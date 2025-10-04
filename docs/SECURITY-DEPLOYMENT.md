# Validatus Security Deployment Guide

## 🔐 Security Best Practices

### Service Account Authentication

**❌ NEVER use service account key files in production**
**❌ NEVER create service account keys in Terraform**

Service account keys are a major security risk because:
- Private keys are stored in plaintext in Terraform state files
- Keys are difficult to rotate securely
- Violates security compliance frameworks (SOC 2, ISO 27001)
- Google Cloud strongly recommends against this approach

Instead, use one of these secure authentication methods:

#### For Cloud Run
```bash
# Enable service account on Cloud Run service
gcloud run services update validatus-backend \
  --service-account=validatus-backend@your-project.iam.gserviceaccount.com \
  --region=us-central1
```

#### For GKE with Workload Identity
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: validatus-backend
  namespace: default
  annotations:
    iam.gke.io/gcp-service-account: validatus-backend@your-project.iam.gserviceaccount.com
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: validatus-backend
spec:
  template:
    spec:
      serviceAccountName: validatus-backend
      containers:
      - name: backend
        image: gcr.io/your-project/validatus-backend
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project"
```

**Required: Bind the Kubernetes SA to the GCP SA**
```bash
# Required: Bind the Kubernetes SA to the GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  validatus-backend@your-project.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:your-project.svc.id.goog[default/validatus-backend]"
```

### Redis Connection Security

**❌ NEVER hardcode Redis IP addresses**

Use Terraform outputs to dynamically set Redis host:

```bash
# In your deployment script
REDIS_HOST=$(terraform output -raw redis_host)
export REDIS_HOST
```

### Environment Configuration

1. **Copy the template**:
   ```bash
   cp backend/env.production.template .env.production
   ```

2. **Update dynamic values**:
   ```bash
   # Set Redis host from Terraform (portable approach)
   REDIS_HOST=$(terraform output -raw redis_host)
   
   # Set project-specific values (portable sed)
   sed "s/validatus-platform/your-project-id/g" .env.production | \
   sed "s/\${REDIS_HOST}/$REDIS_HOST/g" > .env.production.tmp
   mv .env.production.tmp .env.production
   ```

3. **Remove sensitive defaults**:
   - Never commit `.env.production` to version control
   - Use Secret Manager for sensitive values
   - Validate all configuration before deployment

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Environment variable explicitly set (not default)
- [ ] No hardcoded IP addresses
- [ ] Service account configured with Workload Identity
- [ ] All secrets stored in Secret Manager
- [ ] CORS origins restricted to specific domains
- [ ] Deletion protection enabled for production

### Post-deployment
- [ ] Verify service account authentication
- [ ] Test Redis connection with dynamic host
- [ ] Validate all GCP service connections
- [ ] Check security monitoring and logging
- [ ] Verify no service account key files exist

## 🔧 Configuration Examples

### Secure Cloud Run Deployment
```bash
# Deploy with secure service account
gcloud run deploy validatus-backend \
  --image gcr.io/your-project/validatus-backend \
  --service-account validatus-backend@your-project.iam.gserviceaccount.com \
  --set-env-vars "GCP_PROJECT_ID=your-project,ENVIRONMENT=production" \
  --region us-central1 \
  --platform managed
```

### Secure GKE Deployment
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: validatus-config
data:
  GCP_PROJECT_ID: "your-project"
  ENVIRONMENT: "production"
  USE_IAM_AUTH: "true"
  LOCAL_DEVELOPMENT_MODE: "false"
```

## 🚨 Security Warnings

### Critical Issues to Avoid
1. **Service Account Key Files**: Never store `.json` key files in containers
2. **Hardcoded IPs**: Always use dynamic host resolution
3. **Wildcard CORS**: Restrict to specific trusted domains only
4. **Default Passwords**: Always use Secret Manager for credentials
5. **Production Defaults**: Explicitly set environment to prevent accidents

### Monitoring
- Enable Cloud Security Command Center
- Set up alerts for service account key usage
- Monitor for unusual authentication patterns
- Track configuration drift with Terraform

## 📞 Support

For security questions or incidents:
1. Check this documentation first
2. Review GCP security best practices
3. Contact the security team for critical issues
