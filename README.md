# Readme

This bot uses ZeroGPT to detect AI-generated posts in subreddits, and then comment the results in the post. This is intended to make people aware that they might not be even talking to a real person, and that a scam might be awaiting them on the other end.

## Start
To get started, use the `.env.example` as a template for your `.env` file. Once done, run the below commands to start and keep the bot running.

```bash
pip3 install -r requirements.txt
python3 main.py
```

## Configure
To modify the configuration for the bot, edit the `config.json` file before running the bot. The keynames are self-explanatory.

## Warning
Reddit hates this bot. Everytime you will run it, you account WILL be suspended. I've played around with delays and varying responses, but nothing throws them off the radar. For reasons unknown, this bot is always flagged and taken down. Use with caution.
