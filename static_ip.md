# Set Static IP on Jetson Nano Ethernet – Using nmcli Commands Only

## Prerequisites

- Bash shell (terminal access)
- nmcli utility (pre-installed on Jetson Nano)
- sudo privileges
- Ethernet connection

## Step 1: Get the required values (run these in Terminal via VNC/NoMachine or SSH)

1. Connection name (most important):

   ```bash
   nmcli connection show
   ```

   → Look under the "NAME" column for the Ethernet one.
   → Usually: "Wired connection 1" or "eth0"
   → Write it down exactly (case-sensitive)

2. Current IP and subnet mask:

   ```bash
   ip addr show eth0
   ```

   → Look for line like: inet 192.168.1.105/24
   → Current IP = 192.168.1.105
   → Subnet = /24

3. Gateway (router IP):
   ```bash
   ip route show | grep default
   ```
   → Look for: default via 192.168.1.1 ...
   → Gateway = 192.168.1.1

(You can keep DNS as Google: 8.8.8.8 8.8.4.4 – or use college DNS if known)

## Step 2: Run these commands (replace the placeholders)

```bash
sudo nmcli con mod "Replace with your connection name" \
  ipv4.method manual \
  ipv4.addresses Replace-with-your-static-IP/Replace-with-subnet \
  ipv4.gateway Replace-with-your-gateway \
  ipv4.dns "8.8.8.8 8.8.4.4"

sudo nmcli con up "Replace with your connection name"

sudo nmcli con mod "Replace with your connection name" connection.autoconnect yes
```

# Optional: reboot to make sure it applies after unplug/plug

```bash
sudo reboot
```

Example with made-up values:

```bash
sudo nmcli con mod "Wired connection 1" \
  ipv4.method manual \
  ipv4.addresses 192.168.1.150/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "8.8.8.8 8.8.4.4"

sudo nmcli con up "Wired connection 1"

sudo nmcli con mod "Wired connection 1" connection.autoconnect yes
```

## Step 3: Verify after reboot or cable re-plug

```bash
ip addr show eth0          # Should show your new static IP
ping 8.8.8.8               # Internet working?
ping google.com            # DNS working?
```

Done. Your Nano will now always use the same IP on Ethernet.
