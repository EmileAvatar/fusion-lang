import os

import pytest

# Compiling in the tests never writes a fusion.toml into the repo (Task 31)
os.environ["FUSION_NO_NEW_CONFIG"] = "1"


@pytest.fixture(autouse=True)
def _share_when_marked(request, monkeypatch):
    """@pytest.mark.share: a test of `[memory] assignment = "share"` - two names on one
    object, a struct copied with its Lists, objects in a circle - run with "share" as the
    default now that "move" is (Task 48.9, D.102)."""
    if request.node.get_closest_marker('share'):
        monkeypatch.setattr('src.semantic.semantic_analyzer.DEFAULT_ASSIGNMENT', 'share')
