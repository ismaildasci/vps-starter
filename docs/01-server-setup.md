# Server Setup

Initial VPS configuration for Ubuntu 22.04+.

## 1. Create Deploy User

```bash
# Create user
sudo adduser deploy

# Add to sudo group (passwordless)
echo "deploy ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/deploy

# Add to docker group (after Docker installation)
sudo usermod -aG docker deploy
```

## 2. SSH Key Authentication

```bash
# On your local machine, generate key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy to server
ssh-copy-id deploy@YOUR_SERVER_IP

# Or manually add to ~/.ssh/authorized_keys on server
```

## 3. Disable Root SSH Login

Edit `/etc/ssh/sshd_config`:

```bash
PermitRootLogin no
PasswordAuthentication no
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

> **Warning**: Test deploy user login before disabling root!

## 4. Configure Git

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

## 5. Create Directory Structure

```bash
mkdir -p ~/apps ~/traefik ~/shared ~/backups ~/logs
```

## Next Steps

→ [Docker Setup](02-docker-setup.md)
