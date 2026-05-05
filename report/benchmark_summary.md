# Benchmark Summary

This file is generated from the latest benchmark run.

## Run Configuration

- Benchmark profile: `large`
- Total benchmark rows: `32`
- Graph instances: `16`
- Algorithms compared: `Crescenzi, Takes-Kosters`

## Families Covered

- `barabasi_albert`: `5` graph instance(s)
- `erdos_renyi`: `5` graph instance(s)
- `real_world`: `1` graph instance(s)
- `watts_strogatz`: `5` graph instance(s)

## Validation

- No graphs were validated against the exact baseline in this run.

## Runtime Snapshot

- `Crescenzi`: mean runtime `33.398762` s, median BFS traversals `1932.0`
- `Takes-Kosters`: mean runtime `5.626111` s, median BFS traversals `354.0`

## Facebook Combined

- `Crescenzi` returned diameter `8` in `0.029051` s using `5` BFS traversals
- `Takes-Kosters` returned diameter `8` in `0.060778` s using `10` BFS traversals
