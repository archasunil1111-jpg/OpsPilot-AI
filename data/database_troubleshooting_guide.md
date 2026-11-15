
# Database Troubleshooting Guide

## 1. Database Connection Failure

A database connection failure occurs when an application cannot establish or maintain a connection with its database.

The error alone does not confirm the underlying cause.

## 2. Common Possible Causes

- Database server unavailable or not responding.
- Network connectivity problems between the application and database.
- Incorrect database connection configuration.
- Invalid database credentials or authentication failure.
- Database connection pool exhaustion.
- Database resource exhaustion.
- Firewall or access control restrictions.

These are possible causes, not confirmed diagnoses.

## 3. Evidence to Collect

- Exact database connection error message.
- Incident start time and duration.
- Application logs around the incident time.
- Database server status and health information.
- Database server logs.
- Network connectivity diagnostics between application and database.
- Database CPU, memory and connection usage.
- Recent application deployments or configuration changes.
- Database authentication and access error logs.

## 4. Recommended Investigation Steps

1. Confirm when the connection failure started and its scope.
2. Review application logs for database connection errors.
3. Verify database server availability and health.
4. Investigate network connectivity between the application and database.
5. Check database connection configuration and authentication errors.
6. Review database resource usage and active connections.
7. Examine recent deployment and configuration changes.

## 5. Troubleshooting Guidance

If the database server is unavailable, investigate its health and server logs.

If network connectivity is failing, investigate network routes, firewall rules and connectivity between the application and database.

If authentication errors occur, review credential validity and access permissions through approved procedures.

If the connection pool is exhausted, investigate active connections, connection limits and application usage patterns.

If resource usage is unusually high, identify the responsible workload.

Do not assume a root cause without supporting evidence.

## 6. Prevention Recommendations

- Monitor database availability and connection health.
- Maintain application and database logs.
- Monitor active database connections and resource usage.
- Review configuration and deployment changes.
- Establish database backup and recovery procedures.
- Document database incident investigation procedures.

## 7. Safety and Approval

Production database changes require qualified technician review and explicit approval.

Do not recommend deleting data, changing production configuration, restarting services or modifying database access controls without appropriate evidence and authorization.
