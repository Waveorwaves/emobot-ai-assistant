# Quick Start Guide - Email Functionality

## Prerequisites

1. Gmail API credentials configured
2. Python environment with dependencies installed
3. Node.js and npm installed (for frontend development)

## Step 1: Test Email Connection

Before starting the full application, verify email functionality works:

```bash
cd emobot1
python test_email_connection.py
```

**Expected Output:**
```
============================================================
Testing Email Tool Connection
============================================================

1. Initializing email tool...
✅ Email tool initialized successfully

2. Testing inbox read...
✅ Gmail service connected successfully

Result status: success
✅ Successfully fetched 5 emails

First email preview:
  From: sender@example.com
  Subject: Test Email
  ...
```

**If you see errors:**
- Check `emobot/configs/gmail_config.yaml` exists
- Check `emobot/gmail_token.json` exists
- Run OAuth flow if needed (script will prompt)

## Step 2: Start the Application

```bash
cd emobot1/emobot
python web_app.py
```

**Expected Output:**
```
============================================================
🚀 Starting Emobot Web Application
============================================================
📡 Starting MCP server...
✅ MCP server initialized with 4 tools
🚀 Starting MCP server at http://127.0.0.1:8080
🤖 Initializing agent with model: gemini-2.5-flash
✅ Agent initialized successfully

============================================================
✅ Emobot Web App is running!
🌐 Open your browser and go to:
   React Frontend:  http://127.0.0.1:8000
   Simple Test UI:  http://127.0.0.1:8000/simple
============================================================
```

## Step 3: Test Email in Browser

1. Open browser: http://localhost:8000
2. Navigate to **Email** page (sidebar)
3. Click the **refresh button** (🔄 icon in top right)
4. Open browser console (F12) to see logs:
   ```
   🔄 Refreshing emails...
   📧 Refresh response: {success: true, emails: [...]}
   ```
5. You should see:
   - Success alert: "✅ Emails refreshed successfully!"
   - Emails displayed in the list

## Step 4: Check for Errors

If emails don't load, check:

### Browser Console
Press F12 and look for:
- Red error messages
- API response logs
- Network errors

### Backend Terminal
Look for:
- `❌` error messages
- Stack traces
- MCP server errors

### Common Issues

**"Agent not initialized"**
- MCP server failed to start
- Check port 8080 is available
- Restart the application

**"Gmail 服务不可用"**
- Gmail authentication failed
- Run test script to verify
- Delete `gmail_token.json` and re-authenticate

**"Failed to connect"**
- Backend not running
- Check port 8000 is available
- Verify CORS is enabled

## Monitoring

### Check MCP Server Status
```bash
curl http://localhost:8080/tools
```

Should return JSON with available tools.

### Check Backend API
```bash
curl http://localhost:8000/api/email/list
```

Should return JSON with emails or error message.

### Check Frontend API Connection
Open browser console and run:
```javascript
fetch('http://localhost:8000/api/email/list')
  .then(r => r.json())
  .then(console.log)
```

## Debugging Tips

1. **Enable verbose logging**: Check terminal output for detailed logs
2. **Check all ports**: Ensure 8000 and 8080 are not in use
3. **Test in isolation**: Use test script to verify email tool works
4. **Check credentials**: Verify Gmail API credentials are valid
5. **Re-authenticate**: Delete token and restart if auth fails

## Success Indicators

✅ Test script shows "Successfully fetched X emails"
✅ MCP server starts on port 8080
✅ Backend starts on port 8000
✅ Browser shows emails in list
✅ Refresh button works and shows success alert
✅ Console shows successful API responses

## Need Help?

See `EMAIL_FIX_SUMMARY.md` for detailed troubleshooting guide.
