# Fairness and Scheduling

## Define fairness

Choose the relevant meaning instead of using “fair” as a general compliment:

- FIFO fairness;
- weighted fairness;
- per-key or per-tenant fairness;
- priority fairness;
- bounded waiting;
- no starvation;
- capacity fairness across resources.

Specify the unit being scheduled, the observation window, and the behavior under
overload. A system may be fair between tasks but unfair between tenants, or fair
when idle but starve work under retries.

## Review questions

- Can one key, tenant, priority, or retry class monopolize capacity?
- Can a high-priority stream permanently starve normal work?
- Can a large batch delay small work beyond its deadline?
- When cancelled work actually ends or resource accounting transfers, is its
  capacity released promptly and exactly once? Does work that continues after
  cancellation remain counted against capacity?
- Does a failed owner leave work visible to others?
- Does retry ordering preserve or bypass the fairness rule?
- Are scheduling guarantees documented and tested at the claimed scope?

## Evidence

Use queue age, service counts, wait-time distributions, admission decisions,
and starvation scenarios where available. Do not claim fairness from a FIFO data
structure alone; inspect admission, retries, batching, and worker allocation.
