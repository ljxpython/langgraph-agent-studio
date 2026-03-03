# langgraph-agent-studio

## Run LangGraph dev server in background

Use the command below to start the dev server as a detached background process.
It will continue running after you close the terminal session.

```bash
setsid bash -lc 'cd /root/my_best/langgraph-agent-studio && exec nohup .venv/bin/langgraph dev --config graph_src_v2/langgraph.json --port 8123 --no-browser >/tmp/langgraph-8123.log 2>&1 < /dev/null' &
```

### Check process

```bash
pgrep -af "langgraph dev --config graph_src_v2/langgraph.json --port 8123"
```

### View logs

```bash
tail -f /tmp/langgraph-8123.log
```

### Stop service

```bash
pkill -f "langgraph dev --config graph_src_v2/langgraph.json --port 8123"
```
