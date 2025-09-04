# Configuration Files

This directory contains configuration files for the MCP emotion arc analyzer server.

## Files

- **`mcp_server_config.yaml`** - Main production configuration with all available options
- **`dev.yaml`** - Simplified development configuration for testing
- **`.env.example`** - Example environment variables file (to be created)

## Usage

### Development
```bash
python tools/emotion_arc_mcp_server.py --config config/dev.yaml
```

### Production  
```bash
python tools/emotion_arc_mcp_server.py --config config/mcp_server_config.yaml
```

### Default (no config file)
```bash
python tools/emotion_arc_mcp_server.py
```

## Configuration Options

### Server Settings
- `host`: Server host (default: localhost)
- `port`: Server port (default: 8000) 
- `debug`: Enable debug mode (default: false)

### Analysis Settings
- `default_window_size`: Rolling window size (default: 5)
- `max_text_length`: Maximum text length (default: 100000)
- `supported_formats`: Available output formats

### Logging
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `file`: Log file path
- `max_size_mb`: Maximum log file size

See the full configuration files for all available options.
