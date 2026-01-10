import os
from pathlib import Path

class Config:
    """Application configuration management with .env file support"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.file_similarity_pro'
        self.config_dir.mkdir(exist_ok=True)
        self.env_file = self.config_dir / '.env'
        
        # Default configuration
        self.defaults = {
            # Scanning settings
            'MIN_FILE_SIZE': '0',  # KB
            'MAX_WORKERS': '4',
            'BATCH_SIZE': '10',
            'HASH_CHUNK_SIZE': '65536',  # 64KB
            'QUICK_HASH_SIZE': '8192',  # 8KB
            
            # Image processing
            'MAX_IMAGE_SIZE_MB': '100',
            'IMAGE_PREVIEW_SIZE': '400',
            'IMAGE_HASH_SIZE': '8',
            'PERCEPTUAL_HASH_THRESHOLD': '5',
            'MIN_IMAGE_SIMILARITY': '70',
            
            # Text processing
            'TEXT_PREVIEW_CHARS': '50000',
            'TEXT_FONT_SIZE': '10',
            'TEXT_TAB_SIZE': '4',
            
            # UI settings
            'DARK_MODE': 'false',
            'AUTO_SCROLL': 'true',
            'WINDOW_WIDTH': '1200',
            'WINDOW_HEIGHT': '750',
            'PREVIEW_WIDTH': '1400',
            'PREVIEW_HEIGHT': '900',
            
            # Filter defaults
            'DEFAULT_MIN_SIMILARITY': '70',
            'DEFAULT_FILE_TYPE': 'All Files',
            
            # Ignore patterns (JSON array as string)
            'IGNORE_PATTERNS': '["*.tmp", "*.temp", "*.cache", "*.log", ".git/*", ".svn/*", "__pycache__/*", "*.pyc", "node_modules/*", ".DS_Store", "Thumbs.db", "$RECYCLE.BIN/*"]',
            
            # Recent paths limit
            'MAX_RECENT_PATHS': '10',
            
            # Performance
            'ENABLE_IMAGE_SIMILARITY': 'true',
            'ENABLE_PARALLEL_PROCESSING': 'true',
        }
        
        self.config = {}
        self.load()
    
    def load(self):
        """Load configuration from .env file"""
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip()
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Apply defaults for missing values
        for key, value in self.defaults.items():
            if key not in self.config:
                self.config[key] = value
    
    def save(self):
        """Save configuration to .env file"""
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write("# File Similarity Pro Configuration\n")
                f.write("# Generated automatically - edit with care\n\n")
                
                for key, value in sorted(self.config.items()):
                    f.write(f"{key}={value}\n")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def get_int(self, key, default=0):
        """Get integer configuration value"""
        try:
            return int(self.config.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key, default=False):
        """Get boolean configuration value"""
        value = self.config.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def get_float(self, key, default=0.0):
        """Get float configuration value"""
        try:
            return float(self.config.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = str(value)
    
    def get_list(self, key, default=None):
        """Get list configuration value (JSON array)"""
        import json
        try:
            value = self.config.get(key)
            if value:
                return json.loads(value)
            return default or []
        except (json.JSONDecodeError, TypeError):
            return default or []
    
    def set_list(self, key, value):
        """Set list configuration value (as JSON array)"""
        import json
        self.config[key] = json.dumps(value)

# Global configuration instance
config = Config()