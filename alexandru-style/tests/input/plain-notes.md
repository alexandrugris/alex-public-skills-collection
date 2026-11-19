# Plain notes (TC1 input)

Four things I learned running the home server this year.

Logs cost more than the machine. A 20-euro box writes about 2 GB of logs per day,
and 90 days of that fills any disk I have ever owned. Rotation weekly, raw flow kept
seven days, done.

Backups fail at restore time, not at backup time. My restores worked twice and
failed once because a path changed underneath. I now restore to a scratch directory
every month, not by policy but because the last surprise was expensive.

IPv6 was a one-hour fix and I had postponed it for two years. The router already
gave me a prefix; I only had to accept it.

Immutable updates changed everything: I re-flash the system partition from a known
image and copy `/etc` back from a git checkout. Nothing on the box is precious now.
