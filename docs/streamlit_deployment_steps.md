# Streamlit Community Cloud deployment steps

**Status:** The app was tested locally through loopback. A hosted deployment and its access policy require separate owner authorization.

| Setting | Candidate value |
| --- | --- |
| Repository | `canada-us-trade-dependence`, on the owner-approved GitHub account |
| Branch | The reviewed default branch, normally `main` |
| Entrypoint | `dashboard/app.py` |
| Python | Select **3.14** explicitly in Advanced settings. Use a current patched 3.14 release when running locally. |
| Dependencies | Root `requirements.txt`, with exact pins including Streamlit 1.67.0. The dashboard requires no OS packages declared by the project. Paper-building and audit extras are separate. |
| App secrets | Leave empty. Login and source access are required to administer hosting through GitHub. The app itself uses no API keys or service credentials. |
| Inputs | 23 bundled, hash-verified files totaling 7,225,145 bytes. Paths are rooted in the checkout. |
| Resource test | Cold startup and one verified CSV were measured on macOS ARM64. The [release audit](phase7a_release_audit.md) records the observations and the Linux wheel resolution scope. |

Community Cloud documents support for actively security-supported released Python versions and a default that can differ from this project. It runs on Linux and discovers the root requirements file when no higher-precedence app-level environment file exists. The Python 3.14 x86-64 wheel dry-run resolved all pinned packages. It did not execute the application in the hosted Linux image. [Python support policy](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) · [Dependency resolution](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) · [File organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)

## Local verification

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m streamlit run dashboard/app.py --server.address 127.0.0.1
```

In a second terminal from the repository root, run `.venv/bin/python audit/dashboard_http_smoke.py http://127.0.0.1:8501`. This checks the production server endpoints and WebSocket registration and download of the exact national annual CSV. The local address is passed in the command. The committed configuration allows the host to supply its own bind address.

## After deployment authorization

1. Confirm that the approved repository revision is available to Community Cloud. Use the minimum repository permissions required. Review the additional GitHub permissions and app sharing rules if the approved source repository is private. [Community Cloud GitHub permissions](https://docs.streamlit.io/deploy/streamlit-community-cloud/status)
2. Open Community Cloud’s new-app form. Select the approved account, repository and branch, and enter `dashboard/app.py`. In **Advanced settings**, choose Python 3.14 and leave the app's secrets empty. Set the authorized access policy before sharing an app URL. [Deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) · [Sharing settings](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/app-settings)
3. Inspect the hosted build logs and startup, including Python and locked package versions, health, WebSockets over TLS and memory use under expected sessions. Verify English and French navigation, mobile layout and a filtered CSV over the hosted link. Confirm data vintage, source footers and the inconclusive model wording.
4. Record the hosted revision and tested access policy. Use the previously tested revision for rollback. Escalate any mismatch in package resolution, locked files, download headers or accessibility before sharing.

[Final approval checklist](final_approval_checklist.md)
