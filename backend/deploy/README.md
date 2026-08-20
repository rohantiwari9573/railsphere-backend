# Deploy setup

## Systemd services

- `railsphere.service` — the API (gunicorn + uvicorn workers)
- `railsphere-worker.service` — the arq background worker (scheduled analytics refresh)

Both expect the repo at `/home/ubuntu/railsphere-backend/backend` with a `.venv`
already created there. Copy to `/etc/systemd/system/`, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now railsphere
sudo systemctl enable --now railsphere-worker   # only once REDIS_URL is set
```

## CI/CD auto-deploy

`.github/workflows/ci.yml` has a `deploy` job that SSHes into EC2 and restarts
the services after every push to `main` that passes tests. It's automatically
skipped (not failed) until two repo secrets exist — nothing runs, and CI stays
green, until you set these up:

1. **Generate a dedicated deploy key** (don't reuse your personal SSH key) —
   run this on your own machine, not on the EC2 box:
   ```bash
   ssh-keygen -t ed25519 -f railsphere_deploy_key -N ""
   ```
   This creates two files: `railsphere_deploy_key` (private) and
   `railsphere_deploy_key.pub` (public).

2. **Authorize the public key on EC2** — append its contents to the server's
   `~/.ssh/authorized_keys` for the `ubuntu` user:
   ```bash
   cat railsphere_deploy_key.pub | ssh ubuntu@<your-ec2-ip> "cat >> ~/.ssh/authorized_keys"
   ```

3. **Add two repo secrets** on GitHub — go to
   `Settings → Secrets and variables → Actions → New repository secret` on
   `github.com/rohantiwari9573/railsphere-backend`:
   - `EC2_HOST` — the EC2 instance's public IP or hostname
   - `EC2_SSH_KEY` — the full contents of `railsphere_deploy_key` (the
     *private* key file), pasted in the GitHub web UI directly. Never paste
     this into a terminal, chat, or anywhere else it could get logged.

4. **Delete the local private key file** (`railsphere_deploy_key`) once it's
   in GitHub Secrets — you won't need it on your machine again, and GitHub
   Secrets are the only copy that should exist going forward.

5. **Verify sudo works passwordlessly for the `ubuntu` user** on
   `systemctl restart railsphere` — this should already be the case if
   you've been restarting it manually, but if the deploy step hangs on a sudo
   password prompt, add a sudoers rule scoped to just that command:
   ```bash
   echo "ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart railsphere, /bin/systemctl restart railsphere-worker" | sudo tee /etc/sudoers.d/railsphere-deploy
   ```

Once the two secrets exist, the very next push to `main` will deploy
automatically. Push a trivial change first (e.g. a comment or this file) to
confirm the `deploy` job runs and goes green before relying on it.
