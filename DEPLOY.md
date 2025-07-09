# Deployment Guide for Hugging Face Spaces

This guide explains how to deploy your MCP Agent app to Hugging Face Spaces using Docker and uv.

## Files Created

- `Dockerfile` - Container configuration for Python 3.13.2 with uv package manager
- `.dockerignore` - Optimization file to exclude unnecessary files from build
- Updated `app.py` - Changed server binding from 127.0.0.1 to 0.0.0.0 for Docker compatibility

## Deployment Steps

### 1. Create a New Space on Hugging Face

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - **SDK**: Docker
   - **Hardware**: CPU basic (or upgrade as needed)
   - **Visibility**: Public or Private (your choice)

### 2. Upload Your Files

Upload these files to your Hugging Face Space repository:

```
├── Dockerfile
├── .dockerignore
├── pyproject.toml
├── uv.lock
├── src/
│   ├── mcp_agent/
│   │   └── agent.py
│   └── gradio_app/
│       └── app.py
└── README.md (optional)
```

### 3. Configuration

Your app will automatically:
- Use Python 3.13.2 with uv package manager
- Install all dependencies from pyproject.toml and uv.lock
- Run on port 7860 (standard for Gradio apps)
- Be accessible via the Hugging Face Spaces URL

### 4. Environment Variables (Optional)

If you need to set environment variables (like API keys), you can add them in the Space settings under the "Variables and secrets" section.

## Local Testing

To test the Docker container locally before deploying:

```bash
# Build the Docker image
docker build -t mcp-agent .

# Run the container
docker run -p 7860:7860 mcp-agent
```

Then visit `http://localhost:7860` to test your app.

## Development Workflow

If you need to update dependencies:

```bash
# Run your application
uv run python src/gradio_app/app.py

# Add new dependencies
uv add requests

# Add development dependencies  
uv add --dev pytest

# Run any Python script
uv run python your_script.py

# Sync dependencies
uv sync
```

After updating dependencies, make sure to commit both `pyproject.toml` and `uv.lock` files.

## Notes

- The app uses uv for fast and reliable dependency management
- Dependencies are locked in `uv.lock` for reproducible builds
- The container uses `uv sync --frozen --no-dev` for production deployment
- Users provide their OpenAI API key through the interface
- MCP server URLs can be configured dynamically through the UI
- The container is optimized for size and security using Python 3.13.2-slim

## Troubleshooting

If the deployment fails:
1. Check the build logs in your Hugging Face Space
2. Ensure all required files are uploaded (especially `pyproject.toml` and `uv.lock`)
3. Verify that your `pyproject.toml` has the correct dependencies
4. Make sure the `uv.lock` file is up to date with your dependencies
5. Check that the src/ directory structure is correct 