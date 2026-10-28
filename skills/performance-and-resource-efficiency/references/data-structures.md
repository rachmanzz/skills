# Data Structures

Choose a data structure from access patterns, cardinality, ordering, mutation,
memory layout, and concurrency requirements.

## Questions to answer

- Is lookup, insertion, deletion, ordering, or iteration dominant?
- Are duplicate values meaningful?
- Is key cardinality bounded?
- Does the structure need stable ordering or random access?
- Are values uniform or weighted by size?
- Is memory locality important?
- Is the structure shared between workers?

Do not replace a list with a map without checking ordering, duplicate handling,
serialization, memory overhead, and worst-case behavior. Do not select a cache
eviction policy solely because the backing collection is convenient.

## Validation

Benchmark realistic distributions, including empty, small, large, skewed, and
adversarial inputs. Measure both operation latency and memory overhead.
