[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/c/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/haidildariell/news-image-20261124-v1/rank.svg)](https://make.fun/c/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/haidildariell/news-image-20261124-v1/reward.svg)](https://make.fun/c/news-image-20261124)

# The World in One Image — Tuesday 24 November 2026

Entry for the make.fun bounty [Sum up 24 November's world news in one image](https://make.fun/c/news-image-20261124).

`main.py` draws a 1024x1024 newspaper-style front page with the five
stories that defined Tuesday 24 November 2026, using only the Python
standard library: the image is rasterised from a small built-in 5x7
bitmap font and encoded as PNG by hand (zlib + struct), so it runs with
no network and no third-party packages, and two runs write identical
bytes.

Stories in the image (all reported 23–24 November 2026):

1. COP31 climate talks collapse with no deal — Reuters / CNN / BBC
2. NATO sends AWACS early-warning jets to Poland — Reuters
3. Ukraine says it sank a Russian warship off Libya — Reuters
4. Indonesia candy-factory fire kills 24 — Reuters
5. Russian aircraft prompts a brief evacuation alert in South Korea — Reuters

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, PNG)
```

## License

MIT — see LICENSE.
