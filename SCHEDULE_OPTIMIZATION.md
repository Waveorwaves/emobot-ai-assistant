# Schedule Optimization Feature

## Overview

The Schedule Optimization feature provides AI-powered analysis of your emails, calendar, and tasks to generate actionable suggestions for improving productivity and time management.

## Features

### 1. **AI Actions Taken**
Displays automated analysis actions performed by the AI:
- Email categorization
- High-priority task identification
- Calendar conflict detection
- Pattern recognition

### 2. **Your Approval Needed**
Smart suggestions that require your approval before execution:
- **Time Blocking**: Schedule high-priority tasks in calendar gaps
- **Email Batch Processing**: Group similar emails for efficient processing
- **Task Reprioritization**: Upgrade tasks based on deadlines
- **Meeting Optimization**: Add buffers between back-to-back meetings

### 3. **Priority Tasks**
Quick view of your most important tasks that need attention.

## How It Works

### Backend Architecture

The optimization engine analyzes three data sources:

```python
# Fetches and analyzes:
1. Unread emails (up to 20)
2. Calendar events (upcoming)
3. Todo tasks (all active)
```

### Intelligence Algorithm

The system generates suggestions based on:

1. **Calendar Gap Detection**: Identifies free time for task scheduling
2. **Email Volume Analysis**: Recommends batch processing when ≥5 emails
3. **Task Deadline Proximity**: Suggests priority upgrades for medium tasks
4. **Meeting Density**: Adds buffers when ≥4 meetings detected

## API Endpoints

### POST `/api/schedule/optimize`
Generate schedule optimization suggestions

**Response:**
```json
{
  "success": true,
  "actions": [
    {
      "id": "action_1",
      "type": "email",
      "description": "Categorized 12 emails",
      "count": 12,
      "status": "completed"
    }
  ],
  "approvals": [
    {
      "id": "approval_1",
      "type": "schedule",
      "title": "Time Block for High-Priority Task",
      "description": "Schedule 'Project Report' tomorrow 2-4 PM",
      "impact": "⏱️ Saves 30 minutes of context switching"
    }
  ]
}
```

### GET `/api/schedule/actions`
Get list of AI actions taken

### GET `/api/schedule/approvals`
Get list of pending approval items

### POST `/api/schedule/approve`
Approve a suggested action

**Request:**
```json
{
  "approval_id": "approval_1"
}
```

### POST `/api/schedule/reject`
Reject a suggested action

**Request:**
```json
{
  "approval_id": "approval_1"
}
```

## Usage

### From Dashboard

1. Navigate to Dashboard page
2. Scroll to "AI-Generated Schedule Optimization" section
3. Click **"Optimize Schedule"** button
4. Review AI actions and approval requests
5. Click **"Approve"** or **"Skip"** for each suggestion

### Via API

```bash
# Run optimization
curl -X POST http://localhost:8000/api/schedule/optimize

# Get actions
curl http://localhost:8000/api/schedule/actions

# Get approvals
curl http://localhost:8000/api/schedule/approvals

# Approve an action
curl -X POST http://localhost:8000/api/schedule/approve \
  -H "Content-Type: application/json" \
  -d '{"approval_id": "approval_1"}'
```

### Using Test Script

```bash
# Run comprehensive test suite
python test_schedule_optimization.py
```

## Suggestion Types

### 1. Time Blocking
**Trigger**: High-priority tasks exist + calendar gaps available

**Action**: Schedule focus time for important tasks

**Impact**: Reduces context switching, increases deep work time

### 2. Email Batch Processing
**Trigger**: ≥5 unread emails

**Action**: Group emails by sender for batch processing

**Impact**: Reduces email processing time by 40%

### 3. Task Reprioritization
**Trigger**: ≥3 medium-priority tasks

**Action**: Upgrade 2 tasks to high priority based on deadlines

**Impact**: Better focus on what matters most

### 4. Meeting Buffer Addition
**Trigger**: ≥4 calendar events (back-to-back meetings)

**Action**: Reschedule to add 15-minute breaks

**Impact**: Reduces meeting fatigue by 35%

## UI Components

### Optimize Button
- **Location**: Top-right of Schedule Optimization section
- **States**:
  - Default: "Optimize Schedule"
  - Loading: "Optimizing..." with spinner
  - Disabled during optimization

### AI Actions Display
- Shows completed automated actions
- Displays count and status indicator
- Empty state when no actions taken

### Approval Cards
- Yellow border for pending items
- Shows title, description, and impact
- Two-button interface: Approve / Skip
- Badge showing count of pending approvals

### Empty States
- Informative messages when no data
- Clear call-to-action
- Helpful icons

## Data Flow

```
User clicks "Optimize Schedule"
         ↓
Frontend: POST /api/schedule/optimize
         ↓
Backend: Fetch emails, calendar, tasks
         ↓
Backend: Run optimization algorithm
         ↓
Backend: Generate actions & approvals
         ↓
Frontend: Display results
         ↓
User approves/rejects
         ↓
Frontend: POST /api/schedule/approve or /reject
         ↓
Backend: Execute approved action
         ↓
Backend: Update actions log
         ↓
Frontend: Refresh display
```

## Future Enhancements

### Phase 2
- [ ] Machine learning for pattern recognition
- [ ] User behavior tracking
- [ ] Personalized suggestion weighting
- [ ] Energy-based scheduling (morning vs afternoon)

### Phase 3
- [ ] Auto-execute safe optimizations
- [ ] Weekly optimization reports
- [ ] Success metrics tracking
- [ ] A/B testing different strategies

### Phase 4
- [ ] Integration with external calendars
- [ ] Team coordination suggestions
- [ ] Focus time protection
- [ ] Automated meeting declination

## Metrics & Analytics

Track optimization effectiveness:

- **Time Saved**: Calculate hours saved from suggestions
- **Completion Rate**: % of approved vs rejected suggestions
- **Popular Actions**: Which suggestions users approve most
- **Impact Score**: Measure productivity improvements

## Troubleshooting

### No suggestions appearing

**Possible causes:**
1. No data available (no emails/tasks/events)
2. Thresholds not met (need ≥5 emails, ≥3 tasks, etc.)
3. Recent optimization already performed

**Solution:**
- Check email, calendar, and todo list have data
- Wait for more tasks/emails to accumulate
- Lower thresholds in backend if needed

### Approval not working

**Possible causes:**
1. Network error
2. Backend not running
3. Invalid approval ID

**Solution:**
- Check browser console for errors
- Verify backend is running on port 8000
- Refresh page and try again

### Optimization takes too long

**Possible causes:**
1. Large dataset (100+ emails/events)
2. Slow API responses
3. Network latency

**Solution:**
- Reduce `max_results` in optimization code
- Add timeout handling
- Implement caching

## Performance

- **Optimization time**: ~2-5 seconds
- **API response**: <1 second for actions/approvals
- **Approval processing**: <500ms
- **Data refresh**: Automatic on page load

## Security

- All API endpoints require backend initialization
- No sensitive data exposed in responses
- Approval IDs are session-specific
- Actions logged with timestamps

## Testing

Run the test suite:

```bash
# Ensure backend is running
cd emobot && python web_app.py

# In another terminal, run tests
python test_schedule_optimization.py
```

Expected output:
- ✅ Health check passes
- ✅ Optimization generates suggestions
- ✅ Actions and approvals retrieved
- ✅ Approve/reject functionality works

## Code Locations

### Backend
- **Main API**: `/emobot/web_app.py` (lines 1177-1477)
- **Endpoints**:
  - `/api/schedule/optimize`
  - `/api/schedule/actions`
  - `/api/schedule/approvals`
  - `/api/schedule/approve`
  - `/api/schedule/reject`

### Frontend
- **Component**: `/frontend/src/components/dashboard/DashboardPage.tsx`
- **UI Section**: Lines 988-1106
- **State Management**: Lines 114-116, 167-214
- **Handlers**: Lines 735-784

### Tests
- **Test Script**: `/test_schedule_optimization.py`

## Contributing

To add new suggestion types:

1. Add logic in `optimize_schedule()` function
2. Define new `type` value
3. Update approval handler in frontend
4. Add execution logic in `approve_schedule_action()`
5. Update documentation

Example:
```python
# In web_app.py optimize_schedule()
if <condition>:
    approval_counter += 1
    approval_items.append({
        'id': f'approval_{approval_counter}',
        'type': 'new_type',
        'title': 'New Suggestion',
        'description': '...',
        'impact': '...',
        'action_data': {...}
    })
```
