# Bus Manager API Reference

The `BusManager` engine provides unified access to Singapore's Land Transport Authority (LTA) DataMall bus infrastructure data streams. It features automatic 500-record pagination handling using query offsets, input type normalization, and comprehensive coverage for real-time arrivals, service routes, and station positions.

## Automated API Documentation

The reference interface below is dynamically generated from the live source code implementation signatures and type annotations via the `mkdocstrings` compilation plugin loop.

::: ltadatamall.bus_manager.BusManager
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## Technical Architecture Overview

### 1. Transparent Pagination Management

The LTA DataMall server architecture restricts query payloads to a maximum of 500 records per individual network execution transaction. To bypass this baseline ceiling, methods prefixed with `get_all_*` automatically construct consecutive looping HTTP operations using tracking query offsets:

$$
\text{Next URL Request Query Parameter: } \$skip = \text{len}(\text{accumulated\_records})
$$

The internal cycle continues to request data increments until a response containing fewer than 500 entries is encountered, signaling that the network sequence has terminated cleanly.

### 2. Code Usage Paradigms

#### Synchronous Real-Time Arrivals Execution

```python
from ltadatamall.bus_manager import BusManager

# Initialize the manager with your confidential API Account Key
manager = BusManager(api_key="YOUR_LTA_DATAMALL_ACCOUNT_KEY")

# Fetch structured arrival predictions for a target bus stop
arrivals = manager.get_bus_arrival(bus_stop_code="65009", service_no="190")
for service in arrivals:
    print(f"Service: {service.service_no} -> Next Bus: {service.next_bus.estimated_arrival}")
```

#### Asynchronous Multi-Page Pagination Execution

```python
import asyncio
from ltadatamall.bus_manager import BusManager

async def main():
    manager = BusManager(api_key="YOUR_LTA_DATAMALL_ACCOUNT_KEY")
  
    print("Downloading complete Singapore bus stop network configurations...")
    # Pulls 5,000+ records asynchronously over multiple internal pages
    all_stops = await manager.async_get_all_stops()
    print(f"Successfully mapped {len(all_stops)} functional bus stop nodes.")

if __name__ == "__main__":
    asyncio.run(main())
```
