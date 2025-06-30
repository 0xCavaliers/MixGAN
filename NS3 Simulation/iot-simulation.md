# NS3 IoT Network Traffic Simulation

This project implements a proof-of-concept framework for IoT network traffic simulation using NS3. It demonstrates how to transform real network traffic datasets into NS3 simulation events and collect traffic data for analysis.

## Overview

The framework consists of three main components:
1. Data preprocessing (traffic dataset → simulation events)
2. Network simulation (NS3 environment)
3. Traffic collection and analysis

### Data Flow
```
[IoT Traffic Dataset]
       ↓
[csv2ns3events.py] → Convert to simulation events
       ↓
[ns3_events.txt] → Traffic scheduling
       ↓
[NS3 Simulation] → Network simulation
       ↓
[Traffic Logs] → Analysis
```

## Framework Components

### 1. Data Preprocessing
- Input: IoT traffic dataset (`iot-test.csv`)
  * Contains protocol, service, packet size, duration, etc.
  * Includes both normal and attack traffic
- Conversion: `csv2ns3events.py`
  * Maps traffic records to simulation events
  * Assigns source/destination nodes
  * Configures protocol-specific parameters
- Output: `ns3_events.txt`
  * Structured event format for simulation

### 2. Network Simulation
The simulation creates a wireless network with:
- 1000 IoT/attack nodes (0-799: normal, 800-999: attack)
- 1 Access Point (node ID: 1000)
- Protocols: UDP, TCP, and ICMP
- WiFi 802.11b infrastructure mode

### 3. Traffic Collection
- Real-time packet logging at AP
- Captures:
  * Timestamps
  * Protocol information
  * Source/destination addresses
  * Packet sizes
  * Connection details

## Limitations & Future Work

This is a proof-of-concept implementation with several limitations:
1. Simplified traffic patterns
2. Basic attack modeling
3. Limited protocol support
4. Fixed network topology
5. No mobility support

Future improvements could include:
- More sophisticated attack patterns
- Dynamic network topology
- Mobile nodes
- Additional protocols
- Advanced traffic analysis

## Requirements

- NS3 version 3.43 or compatible
- C++ compiler with C++14 support
- Python 3.x for data preprocessing
- Python dependencies:
  ```bash
  pip install pandas numpy
  ```

## Usage

1. Prepare traffic dataset:
```bash
python csv2ns3events.py
```

2. Place simulation script in NS3:
```bash
cp flow.cc /path/to/ns3/scratch/
```

3. Set fixed random seed for reproducibility:
```bash
# Use fixed seed for reproducibility
export NS_GLOBAL_VALUE="RngSeed=42"
```

4. Run simulation:
```bash
./ns3 run flow
```

## Script Parameters

csv2ns3events.py accepts the following parameters:
- `--input`: Input CSV file (default: `iot-test.csv`)
- `--output`: Output NS3 events file (default: `ns3_events.txt`)
- `--attack_threshold`: Node ID above which traffic is treated as attack (default: 800)

## Quick Test Example

A minimal dataset (`sample_flow.csv`) is provided for verification:

```bash
python csv2ns3events.py --input iot-test.csv
./ns3 run flow
```

Expected output: `ap_rx_detail.csv` with ~20 packets demonstrating basic functionality.

## Data Anonymisation

This simulation does not include any personally identifiable information (PII).
All IP addresses and node identities are synthetically generated.
No raw PCAP data is exposed in the repository.
This project uses CICFlowMeter-compatible features; all flows are derived from anonymised CSV files.

## Output Files

The simulation generates:
- `ap_rx_detail.csv`: Detailed packet-level logging
- `flowmon.xml`: Flow monitoring statistics

### Log Format
```
Time,Protocol,Service,SrcNode,DstNode,SrcIP,DstIP,SrcPort,DstPort,Size,Class
```

## Implementation Notes

- Node assignment:
  * Normal nodes: 0-799
  * Attack nodes: 800-999
  * AP node: 1000
- Minimum UDP packet size: 12 bytes
- Grid-based node positioning
- Default port mappings for common services

## Citation

If you use this simulation setup, please cite our paper:

**[MixGAN: A Hybrid Semi-Supervised and Generative Approach for DDoS Detection in Cloud-Integrated IoT Networks]**, ECAI 2025 (under review).

## License

This project is provided as-is under standard NS3 licensing terms.