# Dashboard Agent Test Cases

## Overview
This document contains comprehensive test cases for agents-related events and functionality in the Unitasa dashboard. Since only Twitter is currently configured, all social media tests focus on Twitter integration.

## Test Environment Setup
- **User Account**: Test user with co-creator privileges
- **Browser**: Chrome/Firefox latest versions
- **Network**: Stable internet connection
- **API Endpoints**: All backend services running
- **Database**: Test data populated

## Test Case Categories

### 1. Business Dashboard - Quick Actions

#### TC-BD-QA-001: AI Content Generator Access
**Priority**: High
**Type**: Functional

**Preconditions**:
- User logged in with co-creator access
- Dashboard loaded successfully

**Test Steps**:
1. Navigate to Business Dashboard
2. Locate "Generate AI Content" card in Quick Actions
3. Click on the card

**Expected Results**:
- User redirected to `/generate-content` page
- Page loads without errors
- AI content generation interface displayed

**Test Data**:
- Content type: educational
- Platform: twitter

#### TC-BD-QA-002: Schedule Posts Access
**Priority**: High
**Type**: Functional

**Preconditions**:
- User logged in with pro/enterprise subscription

**Test Steps**:
1. Navigate to Business Dashboard
2. Locate "Schedule Posts" card in Quick Actions
3. Click on the card

**Expected Results**:
- User redirected to `/schedule-posts` page
- Post scheduling interface loads
- Calendar view displayed

#### TC-BD-QA-003: Smart Hashtags Access
**Priority**: Medium
**Type**: Functional

**Preconditions**:
- User logged in with paid subscription

**Test Steps**:
1. Navigate to Business Dashboard
2. Locate "Smart Hashtags" card in Quick Actions
3. Click on the card

**Expected Results**:
- User redirected to `/smart-hashtags` page
- Hashtag generation interface loads
- Input field for content/topic displayed

#### TC-BD-QA-004: Image Suggestions Access
**Priority**: Medium
**Type**: Functional

**Preconditions**:
- User logged in with paid subscription

**Test Steps**:
1. Navigate to Business Dashboard
2. Locate "Image Suggestions" card in Quick Actions
3. Click on the card

**Expected Results**:
- User redirected to `/image-suggestions` page
- Image search interface loads
- Search input field displayed

#### TC-BD-QA-005: Chat Assistant Access
**Priority**: Medium
**Type**: Functional

**Preconditions**:
- User logged in with paid subscription

**Test Steps**:
1. Navigate to Business Dashboard
2. Locate "AI Content Assistant" card in Quick Actions
3. Click on the card

**Expected Results**:
- User redirected to `/chat-assistant` page
- Chat interface loads
- Message input field displayed

#### TC-BD-QA-006: Feature Availability Based on Subscription
**Priority**: High
**Type**: Security/Functional

**Preconditions**:
- Multiple test users with different subscription levels

**Test Steps**:
1. Login as free user
2. Check Quick Actions availability
3. Login as pro user
4. Check Quick Actions availability
5. Login as co-creator
6. Check Quick Actions availability

**Expected Results**:
- Free users: Only "Generate AI Content" available
- Pro users: All features except team features available
- Co-creators: All features available

### 2. Business Dashboard - AI Content Hub

#### TC-BD-AI-001: AI Content Generation (Twitter)
**Priority**: Critical
**Type**: Integration

**Preconditions**:
- Twitter account connected
- User has co-creator access

**Test Steps**:
1. Navigate to Business Dashboard
2. Click "Try Now" on "AI Content Generator" card
3. Select Twitter platform
4. Enter content parameters
5. Click "Generate"

**Expected Results**:
- API call made to `/api/v1/social/content/generate`
- Loading state displayed
- Content generated successfully
- Success message: "Generated X content pieces for twitter"

**Test Data**:
```json
{
  "feature_key": "automated_social_posting",
  "platform": "twitter",
  "content_type": "educational"
}
```

#### TC-BD-AI-002: Content Generation Error Handling
**Priority**: High
**Type**: Error Handling

**Preconditions**:
- Backend service unavailable

**Test Steps**:
1. Navigate to AI Content Hub
2. Click "Try Now" on AI Content Generator
3. Attempt to generate content

**Expected Results**:
- Error message displayed: "Failed to generate content. Please try again."
- No crash or infinite loading
- User can retry operation

#### TC-BD-AI-003: Smart Hashtags Generation
**Priority**: Medium
**Type**: Integration

**Preconditions**:
- User has paid subscription

**Test Steps**:
1. Navigate to AI Content Hub
2. Click "Try Now" on Smart Hashtags
3. Enter topic/keywords
4. Click generate

**Expected Results**:
- Hashtags generated successfully
- Relevant hashtags displayed
- Copy functionality works

### 3. Social Media Dashboard - Account Management

#### TC-SM-AM-001: Twitter Account Connection
**Priority**: Critical
**Type**: Integration

**Preconditions**:
- Twitter OAuth configured
- User not connected to Twitter

**Test Steps**:
1. Navigate to Social Media Dashboard
2. Click "Accounts" tab
3. Locate Twitter card
4. Click "Connect Twitter"

**Expected Results**:
- OAuth flow initiated
- User redirected to Twitter authorization
- After authorization, redirected back to dashboard
- Twitter account appears in connected accounts list
- Account status shows "Connected"

**Test Data**:
- OAuth URL: `/api/v1/social/auth/twitter/url`
- Callback URL: `/api/v1/social/auth/twitter/callback`

#### TC-SM-AM-002: Account Connection Error Handling
**Priority**: High
**Type**: Error Handling

**Preconditions**:
- Invalid OAuth credentials

**Test Steps**:
1. Attempt to connect Twitter account
2. Simulate OAuth failure

**Expected Results**:
- Error message displayed: "Failed to connect account. Check console for details."
- User remains on accounts page
- No crash or data corruption

#### TC-SM-AM-003: Connected Account Display
**Priority**: Medium
**Type**: UI/UX

**Preconditions**:
- Twitter account connected

**Test Steps**:
1. Navigate to Accounts tab
2. View connected accounts section

**Expected Results**:
- Twitter account displayed with avatar
- Username and follower count shown
- Status indicator shows "Active"
- Settings button available

### 4. Social Media Dashboard - Content Creation

#### TC-SM-CC-001: Quick Post Creation
**Priority**: High
**Type**: Functional

**Preconditions**:
- Twitter account connected

**Test Steps**:
1. Navigate to Social Media Dashboard
2. Click "Quick Post" button
3. Select Twitter account
4. Enter post content
5. Click "Post"

**Expected Results**:
- Post modal opens
- Content posted successfully
- Success notification displayed
- Post appears in Twitter feed

#### TC-SM-CC-002: Post Creation with AI Content
**Priority**: High
**Type**: Integration

**Preconditions**:
- Twitter account connected
- AI content generated

**Test Steps**:
1. Generate AI content for Twitter
2. Use generated content in Quick Post
3. Post to Twitter

**Expected Results**:
- AI-generated content posts successfully
- Content appears on Twitter
- Engagement metrics tracked

### 5. Social Media Dashboard - Analytics

#### TC-SM-AN-001: Twitter Analytics Display
**Priority**: Medium
**Type**: UI/Functional

**Preconditions**:
- Twitter account connected
- Some posts made

**Test Steps**:
1. Navigate to Analytics tab
2. View platform breakdown

**Expected Results**:
- Twitter stats displayed
- Post count, engagements, engagement rate shown
- Data updates in real-time

#### TC-SM-AN-002: Analytics Data Accuracy
**Priority**: Medium
**Type**: Data Validation

**Preconditions**:
- Known post data in database

**Test Steps**:
1. Compare dashboard analytics with actual Twitter data
2. Verify engagement metrics

**Expected Results**:
- Analytics data matches actual Twitter metrics
- No data discrepancies

### 6. Cross-Module Integration

#### TC-CM-IN-001: Business to Social Module Switch
**Priority**: High
**Type**: Navigation

**Preconditions**:
- User has access to both modules

**Test Steps**:
1. Start in Business Dashboard
2. Click "Social Media" in sidebar
3. Navigate back to "Business"

**Expected Results**:
- Smooth transition between modules
- State preserved in each module
- No data loss or errors

#### TC-CM-IN-002: AI Content Hub to Social Posting
**Priority**: High
**Type**: Workflow

**Preconditions**:
- Twitter account connected

**Test Steps**:
1. Generate content in AI Content Hub
2. Navigate to Social Dashboard
3. Use generated content for posting

**Expected Results**:
- Seamless workflow between modules
- Generated content available for posting
- No duplicate API calls

### 7. Error Handling and Edge Cases

#### TC-EH-EC-001: Network Connectivity Issues
**Priority**: High
**Type**: Resilience

**Preconditions**:
- Simulate network issues

**Test Steps**:
1. Attempt AI content generation during network outage
2. Try account connection with poor connectivity

**Expected Results**:
- Graceful error handling
- User-friendly error messages
- Retry functionality available

#### TC-EH-EC-002: API Rate Limiting
**Priority**: Medium
**Type**: Performance

**Preconditions**:
- Twitter API rate limits simulated

**Test Steps**:
1. Make multiple rapid content generation requests

**Expected Results**:
- Rate limiting handled gracefully
- User informed of limits
- Queue system or retry mechanism

#### TC-EH-EC-003: Invalid Authentication
**Priority**: High
**Type**: Security

**Preconditions**:
- Twitter token expired

**Test Steps**:
1. Attempt to post content with expired token

**Expected Results**:
- Authentication error handled
- User prompted to re-authenticate
- No sensitive data exposed

### 8. Performance Testing

#### TC-PT-PF-001: Content Generation Response Time
**Priority**: Medium
**Type**: Performance

**Preconditions**:
- Stable network connection

**Test Steps**:
1. Time AI content generation requests
2. Measure response times for multiple requests

**Expected Results**:
- Average response time < 5 seconds
- No timeouts
- Loading states displayed appropriately

#### TC-PT-PF-002: Dashboard Load Performance
**Priority**: Medium
**Type**: Performance

**Preconditions**:
- Multiple connected accounts

**Test Steps**:
1. Time dashboard load with multiple accounts
2. Monitor memory usage

**Expected Results**:
- Dashboard loads within 3 seconds
- No memory leaks
- Smooth scrolling and interactions

### 9. Mobile Responsiveness

#### TC-MR-RS-001: Mobile Dashboard Navigation
**Priority**: Medium
**Type**: UI/UX

**Preconditions**:
- Mobile device or browser dev tools

**Test Steps**:
1. Access dashboard on mobile
2. Test sidebar navigation
3. Test Quick Actions on mobile

**Expected Results**:
- All features accessible on mobile
- Touch interactions work properly
- Content properly formatted for mobile

### 10. Accessibility Testing

#### TC-AT-AC-001: Keyboard Navigation
**Priority**: Low
**Type**: Accessibility

**Preconditions**:
- Keyboard-only navigation

**Test Steps**:
1. Navigate dashboard using Tab key
2. Access all interactive elements
3. Test form submissions

**Expected Results**:
- All features accessible via keyboard
- Proper focus indicators
- Logical tab order

## Test Execution Guidelines

### Pre-Test Setup
1. Ensure test user accounts are created with appropriate permissions
2. Populate test data for analytics and campaigns
3. Verify API endpoints are responding
4. Clear browser cache before testing

### Test Data Requirements
- Twitter test account with OAuth configured
- Sample content for AI generation
- Mock analytics data
- Various user subscription levels

### Reporting
- Document all test results with screenshots
- Log any bugs or issues found
- Note performance metrics
- Record environment details

## Success Criteria
- All high-priority tests pass
- No critical bugs found
- Performance meets requirements
- User experience is smooth
- Error handling works correctly

## Maintenance
- Update test cases when new features are added
- Review test cases quarterly
- Add regression tests for bug fixes