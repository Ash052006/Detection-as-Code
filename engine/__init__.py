"""
Detection engine: load rules, load logs, match, run.
Simple: This file just says "when you type 'from engine import load_rules', you get the load_rules function."
So other code can do: from engine import load_rules, load_logs, run
instead of: from engine.load_rules import load_rules, from engine.load_logs import load_logs, etc.
"""

from engine.load_logs import load_logs
from engine.load_rules import load_rules
from engine.match import matches
from engine.run import run

# __all__ = "these names are the ones you get when you do 'from engine import *'"
__all__ = ["load_rules", "load_logs", "matches", "run"]
