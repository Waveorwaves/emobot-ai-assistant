#!/bin/bash
echo "🔍 Verifying Emobot Demo Endpoints..."

BASE_URL="http://127.0.0.1:8000"

# 1. Check Health
echo -e "\n1️⃣  Checking Health..."
curl -s "$BASE_URL/api/health" | grep "ok" && echo "✅ Health Check Passed" || echo "❌ Health Check Failed"

# 2. Enable Demo Mode
echo -e "\n2️⃣  Enabling Demo Mode..."
curl -s -X POST "$BASE_URL/api/demo/toggle" -H "Content-Type: application/json" -d '{"enabled": true}' | grep "true" && echo "✅ Demo Mode Enabled" || echo "❌ Failed to Enable Demo Mode"

# 3. Check Emails (Demo Data)
echo -e "\n3️⃣  Checking Emails (Demo Data)..."
RESPONSE=$(curl -s "$BASE_URL/api/email/list")
echo $RESPONSE | grep "Prof. Chenhao Tan" && echo "✅ Found Prof. Tan email" || echo "❌ Prof. Tan email missing"
echo $RESPONSE | grep "Microsoft AI" && echo "✅ Found Microsoft email" || echo "❌ Microsoft email missing"

# 4. Check Calendar (Demo Data)
echo -e "\n4️⃣  Checking Calendar (Demo Data)..."
RESPONSE=$(curl -s "$BASE_URL/api/calendar/events")
echo $RESPONSE | grep "Data Science Class" && echo "✅ Found Data Science Class" || echo "❌ Data Science Class missing"

# 5. Check Todos (Demo Data)
echo -e "\n5️⃣  Checking Todos (Demo Data)..."
RESPONSE=$(curl -s "$BASE_URL/api/todo/list")
echo $RESPONSE | grep "Emobot draft" && echo "✅ Found Emobot draft task" || echo "❌ Emobot draft task missing"

# 6. Check Profile Analysis
echo -e "\n6️⃣  Checking Profile Analysis..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/memory/analyze")
echo $RESPONSE | grep "concise communication" && echo "✅ Profile analysis returned expected content" || echo "❌ Profile analysis unexpected"

# 7. Check Insights
echo -e "\n7️⃣  Checking Insights..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/insights/analyze")
echo $RESPONSE | grep "Microsoft interview confirmation" && echo "✅ Found Interview Insight" || echo "❌ Interview Insight missing"
echo $RESPONSE | grep "You have an upcoming interview but no prep time scheduled" && echo "✅ Found Prep Time Insight" || echo "❌ Prep Time Insight missing"

# 8. Check Reply Generation
echo -e "\n8️⃣  Checking Reply Generation..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/insights/generate-reply" -H "Content-Type: application/json" -d '{"recipient": "chenhao@uchicago.edu", "context": "test", "suggestion": "test"}')
echo $RESPONSE | grep "Brief update on Emobot draft" && echo "✅ Generated correct reply for Prof. Tan" || echo "❌ Reply generation failed"

echo -e "\n🏁 Verification Complete!"
