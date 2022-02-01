# catjam-leaderboard
the leaderboard for catjam
## Methods
- GET `/`: visual leaderboard (HTML)  
- GET `/leaderboard`: get JSON leaderboard in format `{ "status": "success", "data": [ { "initials": "AAA", "score": 12 }, ... ] }`  
- PUT `/report`: report a score for the current user in format `{ "initials": "AAA", "score": 12 }`  