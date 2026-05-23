# Passenger Volume API Reference

The `PassengerVolume` module interfaces with LTA DataMall's dynamic passenger volume endpoints. Instead of returning raw individual data lines directly via JSON, these endpoints generate a temporary Amazon S3 pre-signed download link to compressed `.zip` files containing bulk monthly CSV transit metrics.

## Automated API Documentation

The reference interface below is dynamically generated from your live codebase source signatures, annotations, and docstrings.

::: ltadatamall.passenger_volume.PassengerVolume
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## Technical Architecture Overview

### 1. Data Processing & Payload Shape

Unlike standard DataMall endpoints where information arrays are directly embedded under a `"value"` key, the passenger volume endpoints return a wrapping list structure containing an asset extraction link:

```json
{
  "value": [
    {
      "Link": "[https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202603.zip](https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202603.zip)"
    }
  ]
}
```

The underlying code automatically handles extracting this string payload, verifying structural integrity, and raising descriptive error frameworks if keys are absent or empty.

### 2. Dataset Records and Pagination Note

For standard structural endpoints across other modules (such as Bus Routes or Bus Services), the LTA DataMall restricts response sizes to 500 records per query. To navigate those large collections, downstream managers implement loop cycles that increment a `$skip` query offset parameter by groups of 500 records (e.g., `?$skip=500`, `?$skip=1000`) until all database pages are exhausted.

*(Note: The `PassengerVolume` endpoint bypasses this manual pagination looping because it serves the entire monthly dataset directly inside a single downloaded batch file).*

### 3. Code Usage Examples

#### Synchronous Asset Download Link Generation

```python
from ltadatamall.passenger_volume import PassengerVolume

# Initialize the manager
pv_client = PassengerVolume(api_key="YOUR_LTA_DATAMALL_KEY")

try:
    # Fetch data for a specific year and month (YYYYMM)
    download_url = pv_client.pv_bus_stop(date="202603")
    print(f"📦 Download your Bus Stop dataset here: {download_url}")
  
except ValueError as e:
    print(f"Extraction failed: {e}")
```

#### Asynchronous Multi-Endpoint Link Fetching

```python
import asyncio
from ltadatamall.passenger_volume import PassengerVolume

async def fetch_all_transport_metrics():
    pv_client = PassengerVolume(api_key="YOUR_LTA_DATAMALL_KEY")
  
    print("Requesting latest train network metrics links asynchronously...")
  
    # Fire requests concurrently using the async variants
    bus_task = pv_client.async_pv_od_bus_stop()
    train_task = pv_client.async_pv_od_train_destination()
  
    bus_link, train_link = await asyncio.gather(bus_task, train_task)
  
    print(f"Bus OD Link: {bus_link}")
    print(f"Train OD Link: {train_link}")

if __name__ == "__main__":
    asyncio.run(fetch_all_transport_metrics())

```
