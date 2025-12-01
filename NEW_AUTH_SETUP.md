# Backup Folder Updates

The backup folder has been updated with new Google OAuth credentials and fixed frontend dependencies.

## What Was Changed

### 1. Gmail Config Updated (`emobot/configs/gmail_config.yaml`)
   - New client_id: `47120659289-let84nh9a9nh3o98ijfkqmb55gare8b7.apps.googleusercontent.com`
   - New client_secret: `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`
   - User email: `waveorwaves777@gmail.com`

### 2. Old Tokens Removed
   - Deleted `gmail_token.json` (old authentication)
   - Deleted `gmail_credentials.json` (old authentication)

### 3. Frontend Dependencies Fixed
   - Reinstalled all node_modules (were corrupted)
   - Vite now works correctly
   - Frontend can start without errors

## How to Authenticate

Run one of these scripts to authenticate with the new credentials:

```bash
# Option 1: Use the reauth script (recommended)
cd emobot1-backup-before-memory-upgrade-20251113-015517
python3 reauth_gmail.py

# Option 2: Use the test script
python3 test_new_auth.py
```

Both scripts will:
- Open your browser for Google OAuth
- Request permissions for Gmail and Contacts (People API)
- Save the new token for future use

## What's Already Working

The backup folder already has:
- ✅ GmailAuthManager class (same as emobot1)
- ✅ Dynamic port selection for OAuth
- ✅ People API support for contacts
- ✅ Token refresh handling
- ✅ All necessary scopes configured

## Starting the System

Now you can start the integrated system normally:

```bash
./start-integrated.sh
```

This will start:
- Backend on http://localhost:8000
- Frontend on http://localhost:3000
- MCP Server on http://localhost:8080

## Notes

- Make sure People API is enabled in your Google Cloud Console
- The authentication will work with the same Google account as emobot1
- After authentication, all Gmail and contact features will work normally
- Frontend dependencies have been reinstalled and are working correctly
