# Notes

```bash
uv init
uv add ruff
uv add nox
uv add ansible
uv add ansible-dev-tools

# antsibull-nox.toml: add
#[sessions.lint]
#code_files = ["plugins/modules/proxmox_role.py"]

uv run ruff format --config ./ruff.toml plugins/modules/proxmox_storage.py 
uv run nox -e lint -f ./noxfile.py
```
