# Agent Interface Web

This project serves a small website to chat with a toy conversational agent and optionally upload a CSV file for analysis. The implementation relies only on Python's standard library.

## Running

Start the server with Python 3:

```bash
python3 app.py
```

The site will be available at [http://localhost:8888](http://localhost:8888).

### Features

- Chat mode: the agent simply echoes your message.
- Analyze mode: after uploading a CSV file, the agent reports how many lines are in the file.
- Uploaded files are saved to the `uploads/` directory.
