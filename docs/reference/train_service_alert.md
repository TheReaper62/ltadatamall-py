# Train Service Alerts API Reference

The `TrainServiceAlertManager` tracks active MRT or LRT rail service disruptions across Singapore's transit network. When disruptions happen, the API provides details on affected track lines, impacted station arrays, available free public bridging buses, and MRT shuttle directions.

## Automated API Documentation

The classes below are auto-generated from your live codebase docstrings and type layouts.

### Alert Manager Interface

::: ltadatamall.train_service_alert.TrainServiceAlertManager
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

### Alert Data Object Model

::: ltadatamall.train_service_alert.TrainServiceAlert
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

---

## Technical Features & Data Cleanup

### 1. Automated Array Text Stripping

The raw LTA DataMall payload sends stations and bridging buses as unformatted, comma-separated strings (e.g., `"EW1 ,  EW2 , EW3 "`). The model's constructor automatically handles this via an internal cleanup filter:

* Leading and trailing whitespaces are automatically removed.
* Clean Python elements are stored into a list framework.
* If no disruptions are active, the fields cleanly fall back to `"Not Available"` or `"No Message"`.

### 2. Code Usage Examples

#### Synchronous Alert Pulling

```python
from ltadatamall.train_service_alert import TrainServiceAlertManager

# Initialize the alert system
alert_manager = TrainServiceAlertManager(api_key="YOUR_LTA_DATAMALL_KEY")

try:
    active_alerts = alert_manager.get_alerts()
  
    if not active_alerts:
        print("🟢 All rail transit lines are operating normally.")
    else:
        for alert in active_alerts:
            print(f"🚨 Disruption Detected on line: {alert.line}")
            print(f"Status Profile: {alert.status}")
            print(f"Impacted Stations: {', '.join(alert.stations)}")
            print(f"Free MRT Shuttle Buses Available: {alert.free_mrt_shuttle}")
            print(f"Live Message: {alert.message}")
        
except ValueError as e:
    print(f"Data configuration issue found: {e}")
```

#### Asynchronous Live Monitoring Loop

```python
import asyncio
from ltadatamall.train_service_alert import TrainServiceAlertManager

async def track_mrt_status():
    manager = TrainServiceAlertManager(api_key="YOUR_LTA_DATAMALL_KEY")
  
    print("Starting real-time Singapore rail network monitor...")
    # Fetches active alerts asynchronously
    alerts = await manager.async_get_alerts()
  
    print(f"Fetched transit alerts successfully. Active count: {len(alerts)}")

if __name__ == "__main__":
    asyncio.run(track_mrt_status())
```
