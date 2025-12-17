# Unitasa Frontend Testing Suite

This directory contains automated end-to-end tests for the Unitasa dashboard agent functionality using Playwright.

## Setup

### Prerequisites
- Node.js 18+
- Backend server running on port 8001
- Frontend development server running on port 3002

### Installation
```bash
cd frontend
npm install
npx playwright install
```

## Test Structure

### Test Files
- `dashboard-agent.spec.ts` - Main test suite covering dashboard agent functionality

### Test Categories
1. **Landing Page Tests** - Verify Success Stories removal and core functionality
2. **Co-Creator Assessment Flow** - Test pricing display and assessment modal
3. **API Integration Tests** - Verify backend API responses
4. **Mobile Responsiveness** - Test mobile viewport compatibility
5. **Cross-browser Compatibility** - Test across different browsers
6. **Performance Tests** - Measure page load times
7. **Error Handling** - Test graceful failure scenarios

## Running Tests

### Run All Tests
```bash
npm run test:e2e
```

### Run Tests with UI
```bash
npm run test:e2e:ui
```

### Run Tests in Debug Mode
```bash
npm run test:e2e:debug
```

### Run Tests in Headed Mode (visible browser)
```bash
npm run test:e2e:headed
```

### View Test Reports
```bash
npm run test:e2e:report
```

### Run Specific Test File
```bash
npx playwright test dashboard-agent.spec.ts
```

### Run Tests for Specific Browser
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Configuration

### Playwright Config (`playwright.config.ts`)
- **Base URL**: `http://localhost:3002`
- **Browsers**: Chromium, Firefox, WebKit
- **Mobile**: iPhone 12, Pixel 5
- **Timeouts**: 30 seconds for actions, 10 seconds for expectations
- **Parallel Execution**: Enabled for faster test runs

### Environment Setup
The tests automatically start the development server before running tests. Ensure:
- Backend API is accessible at `http://localhost:8001`
- No port conflicts on 3002
- Database is properly configured

## Test Data

### Mock Data Used
- Twitter OAuth responses
- Analytics data (45 posts, 234 engagements)
- AI content generation responses
- User authentication states

### Test Accounts
- Co-creator user (full access)
- Free trial user (limited access)
- Pro user (standard access)

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run E2E Tests
  run: |
    cd frontend
    npm run test:e2e
  env:
    CI: true
```

### Docker Testing
```bash
# Build and test in container
docker build -t unitasa-test .
docker run --rm unitasa-test npm run test:e2e
```

## Debugging Tests

### Common Issues
1. **Port conflicts**: Ensure ports 3002 and 8001 are available
2. **API timeouts**: Check backend server is running
3. **Browser crashes**: Update Playwright browsers with `npx playwright install`

### Debug Commands
```bash
# Run with detailed logging
DEBUG=pw:api npm run test:e2e

# Run single test with pause on failure
npx playwright test --debug failing-test.spec.ts

# Generate code for new tests
npx playwright codegen http://localhost:3002
```

## Test Coverage

### Current Coverage
- ✅ Landing page functionality
- ✅ Co-creator pricing display
- ✅ API integration (health, OAuth, analytics)
- ✅ Mobile responsiveness
- ✅ Cross-browser compatibility
- ✅ Basic performance testing

### Future Enhancements
- [ ] Authentication flow testing
- [ ] Dashboard interaction testing
- [ ] Social media posting workflows
- [ ] Payment integration testing
- [ ] Accessibility compliance testing

## Contributing

### Adding New Tests
1. Create test file in `tests/` directory
2. Follow naming convention: `*.spec.ts`
3. Use descriptive test names with TC-* prefixes
4. Add appropriate test data and assertions

### Test Best Practices
- Use `data-testid` attributes for reliable element selection
- Avoid flaky waits; use proper Playwright locators
- Group related tests in `test.describe` blocks
- Use meaningful assertions with clear error messages
- Keep tests independent and isolated

## Troubleshooting

### Backend Connection Issues
```bash
# Check backend health
curl http://localhost:8001/api/v1/health

# Check API endpoints
curl http://localhost:8001/api/v1/social/analytics
```

### Frontend Issues
```bash
# Check if dev server is running
curl http://localhost:3002

# Restart dev server
npm start
```

### Browser Issues
```bash
# Reinstall browsers
npx playwright install --force

# Update Playwright
npm update @playwright/test
```

## Performance Benchmarks

### Expected Performance
- Page load: < 3 seconds
- API responses: < 1 second
- Test execution: < 2 minutes for full suite

### Monitoring
- Use Playwright's built-in tracing: `--trace on`
- Generate HTML reports for analysis
- Monitor CI/CD pipeline performance

## Support

For test-related issues:
1. Check this README first
2. Review Playwright documentation: https://playwright.dev/
3. Check existing test patterns in the codebase
4. Create an issue with test failure details