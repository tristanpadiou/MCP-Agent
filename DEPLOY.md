# Deployment Guide for Hugging Face Spaces

This guide explains how to deploy your MCP Agent app to Hugging Face Spaces using Docker.

## Files Created

- `Dockerfile` - Container configuration for Python 3.13.2
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
├── requirements.txt
├── app.py
├── agent.py
└── README.md (optional)
```

### 3. Configuration

Your app will automatically:
- Use Python 3.13.2
- Install all dependencies from requirements.txt
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

## Notes

- The app expects users to provide their OpenAI API key through the interface
- MCP server URLs can be configured dynamically through the UI
- The container is optimized for size and security using Python 3.13.2-slim
- Git is included for any dependencies that might need it

## Troubleshooting

If the deployment fails:
1. Check the build logs in your Hugging Face Space
2. Ensure all required files are uploaded
3. Verify that your requirements.txt is properly formatted
4. Make sure agent.py doesn't have any missing dependencies 