# motion-blur
Extracts top percentage (default 5) clearest frame images with least motion blur from input video

## Usage
Example:
```
python main.py ./path/to/input.mov [options]
```

### Options
-  `-o`, `--outputDirectory`&emsp;&emsp;path for pictures, default=output
-  `-p`, `--percentage`&emsp;&emsp;percentage less of highest clarity found as minimum clarity, default=5
