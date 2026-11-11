
# IT Incident Troubleshooting Guide

## Topic: HTTP 503 Service Unavailable

### 1. What is HTTP 503?

HTTP 503 Service Unavailable is an HTTP status code indicating that a server is temporarily unable to handle a request.

The service may be overloaded, undergoing maintenance, or unable to communicate with a required upstream service.

A 503 response does not, by itself, identify the root cause.

### 2. Common Possible Causes

- Application server overload or resource exhaustion.
- Application service stopped or unavailable.
- Upstream server or service unavailable.
- Reverse proxy or load balancer unable to reach the backend.
- Planned maintenance or temporary service shutdown.
- Database or another dependency unavailable, if the application depends on it.

These are possible causes, not confirmed diagnoses.

### 3. Recommended Investigation Steps

1. Confirm when the issue started and whether it affects all users.
2. Check whether the application service is running.
3. Review application logs around the incident start time.
4. Check CPU, memory, and server resource usage.
5. Verify whether the reverse proxy or load balancer can reach the upstream service.
6. Check the health and connectivity of dependent services, including databases where relevant.
7. Review recent deployments, configuration changes, and maintenance activity.

### 4. Evidence to Collect

- Exact error message and HTTP status code.
- Incident start time and duration.
- Application and server logs.
- Reverse proxy or load balancer logs.
- CPU and memory usage.
- Recent deployment or configuration changes.
- Whether the issue affects all users or only some users.

### 5. Troubleshooting Guidance

If the application service is stopped, investigate its logs and service status before restarting it.

If resource usage is unusually high, identify the process or workload responsible.

If an upstream service is unreachable, verify its health and network connectivity.

If a database connection failure is reported, inspect database availability and connection errors.

Do not assume any of these conditions without supporting evidence.

### 6. Prevention Recommendations

- Monitor application availability and response times.
- Configure appropriate resource and health monitoring.
- Review application and proxy logs regularly.
- Test deployments before production release.
- Maintain documented incident response procedures.
- Monitor critical dependencies.

### 7. Safety and Escalation

Do not perform production changes automatically based only on an AI-generated diagnosis.

A qualified technician must verify the evidence and approve corrective actions.

Escalate incidents when the root cause remains unclear or the service impact is significant.
