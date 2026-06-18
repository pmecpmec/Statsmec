from app.services.scrape_clients import parse_csstats, parse_esea

# Minimal fixture mirroring the server-rendered rank cards on a real csstats page.
CSSTATS_HTML = """
<div class="ranks">
  <div class="over">
    <div class="icon"><img src="https://static.csstats.gg/images/faceit.png" /></div>
    <div class="rank"><img class="rank" src="https://static.csstats.gg/images/ranks/faceit/level10.png" /></div>
  </div>
</div>
<div class="ranks">
  <div class="over">
    <div class="icon"><img src="https://static.csstats.gg/images/premier.png" alt="Premier - Season 4" title="Premier - Season 4" /></div>
    <div class="rank">
      <div class="cs2rating ancient sm " style="background-image: url(x)">
        <span class=""> 25<small>,562</small> </span>
      </div>
    </div>
    <div class="best">
      <div class="cs2rating ancient sm " style="background-image: url(x)">
        <span class=""> 27<small>,271</small> </span>
      </div>
    </div>
  </div>
</div>
"""


def test_parse_csstats_extracts_real_fields():
    stats = parse_csstats(CSSTATS_HTML)
    assert stats["faceit_level"] == 10
    assert stats["premier_season"] == "Season 4"
    assert stats["premier_rating"] == 25562
    assert stats["premier_tier"] == "ancient"
    assert stats["premier_best"] == 27271


def test_parse_csstats_empty_on_garbage():
    assert parse_csstats("<html>nothing here</html>") == {}


def test_parse_esea_empty_on_landing_page():
    # ESEA returns a generic landing stub behind Cloudflare; no stats parseable.
    assert parse_esea("<title>ESEA - Hate Cheaters?</title>") == {}
