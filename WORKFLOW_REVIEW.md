# GitHub Actions Workflow Review & Fixes

## Workflow Overview
**Name**: CI-CD -> EC2 Rolling update via ASG  
**Trigger**: Push to `main` branch  
**Purpose**: Build Docker image → Push to ECR → Update ASG Launch Template → Trigger instance refresh

---

## 3 Job Pipeline

### 1️⃣ **build_and_push**
- Builds Docker image tagged with 7-char commit SHA
- Pushes to ECR repository
- **NEW**: Retry logic for push failures (up to 3 attempts)

### 2️⃣ **update_launch_template** 
- Generates user-data script with environment variables
- Creates new launch template version with user-data
- **NEW**: Validates outputs before proceeding

### 3️⃣ **trigger_asg_refresh**
- Checks for in-progress refreshes (blocks concurrent updates)
- Triggers ASG instance refresh with new template
- **NEW**: Validates launch template version, better error messages

---

## 🐛 Critical Issues FIXED

### Issue 1: AWS CLI Version Conflict ✅
**Problem**: Installing both `awscli` v1 (apt) and AWS CLI v2 (manual)
- v1: `/usr/bin/aws` (deprecated)
- v2: `/usr/local/bin/aws` (current)
- Could cause PATH conflicts and failures

**Fix**: Removed `awscli` from apt install, using AWS CLI v2 only

### Issue 2: Missing Docker Pull Retries ✅
**Problem**: No retry logic for `docker pull` from ECR
- Transient network/ECR issues cause complete deployment failure
- No graceful degradation

**Fix**: Added 3-attempt retry loop with 5-second backoff

### Issue 3: Incomplete Error Handling ✅
**Problem**: Launch template version could be empty/None
- ASG refresh fails with cryptic errors
- No validation before using outputs

**Fix**: 
- Validate LT_VERSION is numeric before using
- Check files exist before encoding
- Verify base64 output is not empty
- Detect AWS CLI errors in response

### Issue 4: Silent Failures in User-Data ✅
**Problem**: User-data script fails but instance continues
- Docker not installed/running
- Container exits immediately
- No logs to diagnose

**Fix**:
- Added `set -e` to exit on first error
- Comprehensive logging to `/var/log/user-data.log`
- Container status verification (checks if running)
- Logs output after failures

### Issue 5: Docker Push Failures Unhandled ✅
**Problem**: ECR rate limiting or network issues cause immediate failure
- No retry for transient failures
- Entire workflow fails on temporary issue

**Fix**: Added 3-attempt retry with 10-second backoff

### Issue 6: Docker Group Permissions Unnecessary ✅
**Problem**: Script adds ubuntu user to docker group, but:
- Script runs as root anyway
- `newgrp docker` doesn't persist after script ends
- Adds unnecessary complexity

**Fix**: Removed docker group logic, running all commands as root in user-data

---

## ✨ Improvements Made

### Better Logging
```bash
# All scripts log to:
# - /var/log/user-data.log (EC2 instance)
# - GitHub Actions console output

# Log includes:
- Timestamp of each step
- Variable values
- Success/failure status
- Container status verification
```

### Validation Layer
```yaml
# Before each critical operation:
✓ Check variables are not empty
✓ Check files exist
✓ Validate command outputs
✓ Detect errors in responses
```

### Retry Logic
```bash
# For transient failures:
1. Docker pull: 3 attempts, 5s delay
2. Docker push: 3 attempts, 10s delay  
3. ASG refresh: 5 attempts, 30s delay
```

### Better Error Messages
```
Before: "Error: Process completed with exit code 1"
After:  "ERROR: Invalid launch template version: None
         LT_VERSION must be a numeric value"
```

---

## 🔍 How to Verify Deployment

### 1. Check GitHub Actions Console
```
✓ Build completed
✓ Image pushed to ECR
✓ Launch template version created
✓ ASG refresh triggered
```

### 2. SSH into EC2 Instance
```bash
# Check if user-data ran
sudo tail -100 /var/log/user-data.log

# Verify Docker is running
sudo systemctl status docker
docker ps

# Check Flask container
docker ps -a
docker logs flask-app

# Test connectivity
curl http://localhost:5000
```

### 3. AWS Console
```bash
# Monitor ASG refresh
aws autoscaling describe-instance-refreshes \
  --auto-scaling-group-name flask-app-asg \
  --region us-east-1

# Check launch template versions
aws ec2 describe-launch-template-versions \
  --launch-template-id lt-062d695e7b63ebec3 \
  --region us-east-1
```

---

## 🚨 Troubleshooting Guide

### Container Not Running
1. **SSH into instance**
   ```bash
   sudo tail -200 /var/log/user-data.log
   docker logs flask-app
   ```

2. **Check IAM Permissions**
   ```bash
   # EC2 instance needs:
   - ECR:GetDownloadUrlForLayer
   - ECR:BatchGetImage
   - ECR:PutImage
   - ECR:InitiateLayerUpload
   ```

3. **Verify Image in ECR**
   ```bash
   aws ecr describe-images \
     --repository-name flask-app \
     --region us-east-1
   ```

### ASG Refresh Fails
```bash
# Check if another refresh is in-progress
aws autoscaling describe-instance-refreshes \
  --auto-scaling-group-name flask-app-asg \
  --region us-east-1

# Check refresh details
aws autoscaling describe-instance-refreshes \
  --auto-scaling-group-name flask-app-asg \
  --query "InstanceRefreshes[0].[InstanceRefreshId,Status,FailureReason]" \
  --region us-east-1
```

### ECR Login Fails
- Verify EC2 IAM role has ECR permissions
- Check AWS credentials are valid
- Verify ECR repository exists in same region

---

## 📊 Workflow Execution Times

| Step | Typical Duration |
|------|------------------|
| Build Docker image | 2-5 min |
| Push to ECR | 1-3 min |
| Create Launch Template | 10-30 sec |
| Wait before refresh | 10 sec |
| ASG refresh (2 instances) | 5-10 min |
| **Total** | **~10-20 min** |

---

## 🎯 Next Steps

1. **Commit and push** the updated workflow
2. **Monitor first deployment** for any issues
3. **Check EC2 instance logs** if container doesn't start
4. **Verify IAM role** has required ECR permissions
5. **Test manual deployment** if needed

---

*Last Updated: 2026-06-10*
