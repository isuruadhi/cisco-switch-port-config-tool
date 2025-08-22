# Cisco Switch Port Configuration Tool

A simple Python GUI tool to configure Cisco switch ports individually or via bulk CSV upload using **Netmiko**.

---

## Features

- Connect to a Cisco switch using IP, username, and password.
- View current interface configuration.
- Configure single interfaces:
  - Set port mode (Access/Trunk)
  - Set VLAN
  - Add description
  - Apply additional commands
  - Apply security or voice VLAN rules automatically for specific VLANs.
    
- Bulk configuration via CSV file:
  - Preview configuration for all switches before applying
  - Apply configurations to multiple switches at once
  - View detailed success/failure report

---

## CSV Format for Bulk Upload

| switch_ip | iface_type | port_num | port_mode | vlan_id | description | additional_cmds |
|-----------|-----------|---------|----------|--------|------------|----------------|
| 192.168.1.10 | GigabitEthernet | 1/0/1 | Access | 10 | User Port | no shutdown; spanning-tree portfast |
| 192.168.1.11 | GigabitEthernet | 1/0/2 | Trunk | 20 | Trunk to Server | switchport nonegotiate |

- `additional_cmds` should be semicolon-separated.

---

## Installation

1. Clone the repo:

```bash
git clone https://github.com/isuruadhi/cisco-switch-port-config-tool.git
cd cisco-switch-port-config-tool
```
---

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

1. Run the tool:

```bash
python switch_config_tool.py
```

2. Enter your switch credentials and target interface details.
3. Preview configuration before applying to avoid mistakes.
4. For bulk upload, use the "Bulk Upload CSV" button.

---

## Important Notes

- The tool uses Netmiko to connect to Cisco IOS devices.
- Be careful when applying configurations to live devices. Always preview before applying.
- Works with Cisco IOS only.

---

## Contribution

Feel free to fork and submit pull requests. Suggestions for improvements are welcome!


