# Gemini CLI Configuration for Hovel

This directory contains the configuration for the [Google Gemini CLI](https://github.com/google-gemini/gemini-cli) integration with the Hovel project.

## 📁 File Structure

```
.gemini/
├── settings.json     # Main configuration file
└── README.md       # This documentation file
```

## 🔧 Configuration

### API Key Setup

1. **Get your API key** from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Replace the placeholder** in `settings.json`:
   ```json
   "api_key": "YOUR_ACTUAL_API_KEY_HERE"
   ```

### Model Settings

- **Default Model**: `gemini-1.5-flash` (fast, cost-effective)
- **Alternative**: `gemini-1.5-pro` (more capable, higher cost)
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Max Tokens**: 2048 (suitable for most tasks)

## 🚀 Usage

### Basic Commands

```bash
# Initialize Gemini CLI with this config
gemini init --config .gemini/settings.json

# Use project-specific templates
gemini template branch_creation --branch_name "feature-new-ui" --description "New UI components"

# Code review assistance
gemini template code_review --code "$(cat server.py)"

# Generate API documentation
gemini template api_documentation --endpoint "/api/branch"
```

### Integration Features

#### Git Integration
- **Auto-commit**: Disabled by default (set `"auto_commit": true` to enable)
- **Commit templates**: Uses conventional commit format
- **Branch operations**: Integrated with Hovel's branch management

#### Docker Integration
- **Auto-build**: Disabled by default
- **Container management**: Works with Hovel's Docker orchestration

#### Postman Integration
- **Collection path**: Points to `./Hovel_API_Collection.json`
- **API testing**: Integrated with Hovel's API endpoints

## 📋 Templates

### Branch Creation Template
```bash
gemini template branch_creation \
  --branch_name "feature-name" \
  --description "Description of the feature"
```

### Code Review Template
```bash
gemini template code_review \
  --code "$(cat filename.py)"
```

### API Documentation Template
```bash
gemini template api_documentation \
  --endpoint "/api/branch"
```

## 🔒 Security

- **API Key Encryption**: Enabled by default
- **Rate Limiting**: 60 requests/minute, 1000 requests/hour
- **Allowed Models**: Restricted to Gemini 1.5 models
- **Environment Variables**: Consider using `GEMINI_API_KEY` environment variable

## 🛠️ Development Workflow

1. **Setup**: Configure your API key in `settings.json`
2. **Branch Creation**: Use templates for consistent branch creation
3. **Code Review**: Get AI assistance for code reviews
4. **Documentation**: Generate API documentation automatically
5. **Integration**: Leverage Git, Docker, and Postman integrations

## 📚 References

- [Gemini CLI Documentation](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md)
- [Google AI Studio](https://makersuite.google.com/app/apikey)
- [Gemini API Documentation](https://ai.google.dev/docs)

## 🔄 Updates

This configuration is designed to work with the Hovel project's development workflow. Update the templates and settings as the project evolves. 