#!/bin/bash

# Quick test to verify frontend can start

echo "🧪 Testing Frontend Startup..."
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found"
    exit 1
fi

echo "✅ node_modules exists"

# Check if vite is installed
if [ ! -f "node_modules/.bin/vite" ]; then
    echo "❌ vite binary not found"
    exit 1
fi

echo "✅ vite binary exists"

# Check vite version
VITE_VERSION=$(node_modules/.bin/vite --version 2>&1)
echo "✅ Vite version: $VITE_VERSION"

# Check if vite can be executed
echo ""
echo "🔍 Testing vite execution..."
timeout 5 npm run dev &
PID=$!

sleep 3

if kill -0 $PID 2>/dev/null; then
    echo "✅ Frontend started successfully!"
    kill $PID 2>/dev/null
    wait $PID 2>/dev/null
    echo ""
    echo "🎉 Frontend is ready to use!"
    exit 0
else
    echo "❌ Frontend failed to start"
    exit 1
fi
