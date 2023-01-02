# Swagatha
Donate your cubes to other needy nerds.  

## Quick start
Clone this repository.  Pip install the dependencies
```python
pip install -r requirements.txt
```

It will take a little fine-tuning to get the screen locations correct. Put the screen locations into a config file like the ones found in `configs`.  Once you've found all your screen locations, close the Snap game client.  Swagatha will reopen it for you.

Finally unleash Swagatha with

```python
python make_me_credits.py <path to config yaml>
```

## Fun future stuff to do
Track stats.  There are tons of game log files at `~\AppData\LocalLow\Second Dinner\SNAP\Standalone\States\nvprod folder` (PC version).