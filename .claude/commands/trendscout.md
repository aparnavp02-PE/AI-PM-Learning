Run the TrendScout market intelligence agent (PM-AG-002).

If $ARGUMENTS is provided, use those as keywords to scan. Otherwise, load keywords from watchlist.json.

Steps:
1. Run the agent: `python trendscout_agent.py $ARGUMENTS`
2. Show the output to the user.
3. Highlight any HIGH PRIORITY signals (impact_score >= 8) prominently.
4. If a `digest_<today>.md` file was created, confirm its location.
5. Remind the user they can edit `watchlist.json` to customize monitored keywords.

The agent will:
- Search the web for recent strategic news on each keyword
- Filter out noise (stock prices, hiring, marketing fluff)
- Score each signal 1-10 (Strategic Impact Score)
- Generate a Daily Market Pulse digest
- Alert on high-impact signals (score > 6) via Slack-style output
