# Code Review Checklist

Use this checklist to ensure code quality, security, and best practices before committing code.

## 🏗️ Architecture & Design Patterns

### Repository Pattern

- [ ] Data access is abstracted through repository classes
- [ ] Repository classes inherit from base repository
- [ ] No direct database access in service or API layers
- [ ] Proper separation between SQL and NoSQL repositories

### Service Layer

- [ ] Business logic is contained in service classes
- [ ] Services don't contain database queries
- [ ] Services orchestrate between repositories
- [ ] Proper error handling in service methods

### API Layer

- [ ] Endpoints only handle HTTP concerns
- [ ] Request/response validation with Pydantic
- [ ] Proper dependency injection usage
- [ ] Consistent error response format

### Dependency Injection

- [ ] Database sessions injected properly
- [ ] Services injected into endpoints
- [ ] Authentication dependencies used correctly
- [ ] No hardcoded dependencies

## 🔒 Security Checklist

### Authentication & Authorization

- [ ] JWT tokens validated properly
- [ ] Token expiration checked
- [ ] Proper role-based access control
- [ ] Password hashing with bcrypt
- [ ] No hardcoded secrets or credentials

### Input Validation

- [ ] All user inputs validated with Pydantic
- [ ] SQL injection prevention (using ORM)
- [ ] XSS protection in responses
- [ ] File upload validation (if applicable)
- [ ] Rate limiting implemented

### Data Protection

- [ ] Sensitive data not logged
- [ ] Proper CORS configuration
- [ ] HTTPS enforced in production
- [ ] Database credentials in environment variables
- [ ] No internal errors exposed to clients

## 📝 Code Quality Standards

### Type Hints

- [ ] All function parameters have type hints
- [ ] Return types specified for all functions
- [ ] Generic types used appropriately
- [ ] Optional types handled correctly
- [ ] Async functions properly typed

### Documentation

- [ ] Public methods have docstrings
- [ ] Docstrings follow Google/Sphinx format
- [ ] Complex logic is commented
- [ ] README updated for new features
- [ ] API documentation is accurate

### Code Style

- [ ] PEP 8 compliance
- [ ] Consistent naming conventions
- [ ] Functions under 50 lines
- [ ] Classes follow single responsibility
- [ ] No code duplication

### Error Handling

- [ ] Custom exception classes used
- [ ] Global exception handlers implemented
- [ ] Appropriate HTTP status codes
- [ ] Consistent error response format
- [ ] Errors logged appropriately

## 🗄️ Database Best Practices

### Async Operations

- [ ] All database operations are async
- [ ] Proper session management
- [ ] Connection pooling configured
- [ ] Transactions handled correctly
- [ ] Database connections closed properly

### Query Optimization

- [ ] No N+1 query problems
- [ ] Proper use of joins
- [ ] Database indexes on foreign keys
- [ ] Pagination implemented for lists
- [ ] Query performance monitored

### Migrations

- [ ] Alembic migrations for schema changes
- [ ] Migration files reviewed
- [ ] Rollback procedures tested
- [ ] Database versioning maintained

## 🧪 Testing Requirements

### Unit Tests

- [ ] Service methods have unit tests
- [ ] Repository methods tested
- [ ] Utility functions tested
- [ ] Edge cases covered
- [ ] Mock external dependencies

### Integration Tests

- [ ] API endpoints tested
- [ ] Database operations tested
- [ ] Authentication flow tested
- [ ] Error scenarios tested
- [ ] End-to-end workflows tested

### Test Quality

- [ ] Minimum 80% code coverage
- [ ] Tests are deterministic
- [ ] Proper test data setup
- [ ] Tests clean up after themselves
- [ ] Performance tests for critical paths

## ⚡ Performance Considerations

### Database Performance

- [ ] Efficient queries
- [ ] Proper indexing
- [ ] Connection pooling
- [ ] Query caching where appropriate
- [ ] Database monitoring

### Application Performance

- [ ] Async operations used
- [ ] Memory usage optimized
- [ ] Response times acceptable
- [ ] Caching implemented
- [ ] Resource cleanup

### Scalability

- [ ] Stateless design
- [ ] Horizontal scaling considerations
- [ ] Load balancing compatibility
- [ ] Resource limits configured

## 🔧 Configuration & Deployment

### Environment Configuration

- [ ] Environment variables used
- [ ] Configuration validation
- [ ] Different configs for environments
- [ ] Secrets management
- [ ] Feature flags implemented

### Docker & Deployment

- [ ] Dockerfile optimized
- [ ] Multi-stage builds used
- [ ] Security scanning passed
- [ ] Health checks implemented
- [ ] Logging configured

## 📊 Monitoring & Logging

### Logging

- [ ] Structured logging implemented
- [ ] Appropriate log levels used
- [ ] Sensitive data not logged
- [ ] Request correlation IDs
- [ ] Error tracking

### Monitoring

- [ ] Health check endpoints
- [ ] Metrics collection
- [ ] Performance monitoring
- [ ] Error rate tracking
- [ ] Alerting configured

## 🚀 Pre-Commit Checklist

Before committing, ensure:

- [ ] All tests pass
- [ ] Security scan passes (bandit)
- [ ] Documentation updated
- [ ] Breaking changes documented

## 🎯 Review Focus Areas

### Critical Issues (Must Fix)

- Security vulnerabilities
- Data loss risks
- Performance bottlenecks
- Breaking changes
- Missing error handling

### Important Issues (Should Fix)

- Code quality problems
- Missing tests
- Documentation gaps
- Performance optimizations
- Best practice violations

### Nice to Have (Could Fix)

- Code style improvements
- Additional tests
- Documentation enhancements
- Performance tweaks
- Refactoring opportunities

## 📋 Review Commands

Use these commands for specific reviews:

```bash
# Run tests and security checks
pytest --cov=app
bandit -r app/

# Security checks
safety check -r requirements.txt
pip-audit
```

## ✅ Final Approval

Before merging:

- [ ] All critical issues resolved
- [ ] Code review completed
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Security scan passed
- [ ] Performance acceptable
- [ ] Ready for production

---

**Remember**: Code review is about improving code quality, security, and maintainability while helping developers learn best practices.
