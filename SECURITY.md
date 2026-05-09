# Security Guide

This document outlines security best practices for the Emobot project.

## 🔐 Sensitive Files

The following files contain sensitive information and are automatically ignored by Git:

### API Keys and Tokens
- `gmail_token.json` - Gmail OAuth tokens
- `gmail_credentials.json` - Gmail API credentials
- `.env` - Environment variables with API keys
- `*.key`, `*.pem`, `*.p12`, `*.pfx` - Certificate files

### Configuration Files
- `configs/gmail_config.yaml` - Gmail API configuration
- `configs/*_config.yaml` - Other API configurations

### Data Files
- `todo_list.json` - User todo data
- `todo_export_*.json` - Exported todo data
- `agent_memory/` - User memory and preferences

## 🛡️ Security Best Practices

### 1. Never Commit Sensitive Files
- Always check `.gitignore` before committing
- Use `git status --ignored` to verify sensitive files are ignored
- If you accidentally commit sensitive files, immediately rotate the credentials

### 2. Environment Variables
- Store API keys in `.env` files (never commit them)
- Use `.env-example` as a template
- Set appropriate file permissions: `chmod 600 .env`

### 3. API Key Management
- Use different API keys for development and production
- Regularly rotate API keys
- Use the minimum required permissions for each API
- Monitor API usage for unusual activity

### 4. Gmail API Security
- Use OAuth 2.0 for authentication
- Store tokens securely
- Implement token refresh logic
- Use appropriate scopes (readonly when possible)

### 5. Data Privacy
- User data is stored locally by default
- Implement data encryption for sensitive information
- Provide clear data retention policies
- Allow users to export/delete their data

## 🔧 Setup Instructions

### 1. Initial Setup
```bash
# Copy example configuration
cp configs/gmail_config.example.yaml configs/gmail_config.yaml

# Copy environment template
cp .env-example .env

# Edit configuration files with your credentials
nano configs/gmail_config.yaml
nano .env
```

### 2. File Permissions
```bash
# Set restrictive permissions on sensitive files
chmod 600 .env
chmod 600 configs/gmail_config.yaml
chmod 600 gmail_token.json
chmod 600 gmail_credentials.json
```

### 3. Verify Security
```bash
# Check that sensitive files are ignored
git status --ignored

# Verify no sensitive files are tracked
git ls-files | grep -E "(token|credential|\.env|\.key)"
```

## 🚨 Emergency Procedures

### If You Accidentally Commit Sensitive Data

1. **Immediate Actions**:
   ```bash
   # Remove from Git history
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push to remove from remote
   git push origin --force
   ```

2. **Rotate Credentials**:
   - Generate new API keys
   - Update all configuration files
   - Revoke old tokens

3. **Notify Team**:
   - Inform all developers
   - Check for any forks or clones
   - Monitor for unauthorized usage

## 📋 Security Checklist

Before deploying or sharing the project:

- [ ] All sensitive files are in `.gitignore`
- [ ] No API keys in committed files
- [ ] Environment variables are properly set
- [ ] File permissions are restrictive
- [ ] OAuth tokens are secure
- [ ] Data encryption is implemented
- [ ] Access logs are monitored
- [ ] Backup procedures are secure

## 🔍 Security Monitoring

### Regular Checks
- Monitor API usage and costs
- Review access logs
- Check for unusual activity
- Update dependencies regularly
- Audit file permissions

### Tools
- Use `git-secrets` to prevent committing secrets
- Implement pre-commit hooks
- Use security scanning tools
- Monitor for exposed credentials

## 📞 Security Contacts

If you discover a security vulnerability:

1. **DO NOT** create a public issue
2. **DO** contact the maintainers privately
3. **DO** provide detailed information about the vulnerability
4. **DO** allow time for assessment and fix

## 📚 Additional Resources

- [GitHub Security Best Practices](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure)
- [OAuth 2.0 Security](https://tools.ietf.org/html/rfc6819)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)
- [Environment Variable Security](https://12factor.net/config) 