"""
Meme search module for MemeGen.

First checks known meme triggers and uses a matching local meme image when
the image is bundled in assets/. If no local match is available, it attempts
a lightweight DuckDuckGo HTML search and otherwise returns None for fallback
generation. This avoids requiring ddgs/lxml.
"""
import os
import re
import html
import urllib.parse
import urllib.request
from html.parser import HTMLParser


class ResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._text_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            href = attrs.get("href", "")
            classes = attrs.get("class", "")
            if href and ("result__a" in classes or "uddg=" in href):
                self._href = href
                self._text_parts = []

    def handle_data(self, data):
        if self._href is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            title = " ".join(" ".join(self._text_parts).split())
            href = self._href
            if "uddg=" in href:
                try:
                    parsed = urllib.parse.urlparse(href)
                    params = urllib.parse.parse_qs(parsed.query)
                    href = params.get("uddg", [href])[0]
                except Exception:
                    pass
            if title and href.startswith("http"):
                self.links.append({"title": title, "url": html.unescape(href)})
            self._href = None
            self._text_parts = []


class MemeSearch:
    def __init__(self, download_dir="meme_search_cache"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

        # Add more aliases here as we support more meme catchphrases.
        self.known_memes = [
            {
                "triggers": [
                    "wait a minute who are you",
                    "wait a minute, who are you",
                    "wait a minute who r u",
                    "who are you",
                ],
                "asset": "wait_a_minute_who_are_you.png",
                "title": "Wait a minute, who are you?",
                "source_url": "https://knowyourmeme.com/memes/wait-a-minute-who-are-you",
            }
        ]

    def _normalize(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return " ".join(text.split())

    def _find_known_meme(self, scenario):
        normalized = self._normalize(scenario)
        for meme in self.known_memes:
            for trigger in meme["triggers"]:
                if self._normalize(trigger) in normalized:
                    local_path = os.path.join(self.assets_dir, meme["asset"])
                    if os.path.isfile(local_path):
                        return {
                            "path": local_path,
                            "source_url": meme["source_url"],
                            "title": meme["title"],
                        }
        return None

    def search_and_download(self, scenario):
        # Prefer an exact known meme match before attempting a web search.
        known = self._find_known_meme(scenario)
        if known:
            return known

        query = f"{scenario} meme image"
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(query)
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                   "AppleWebKit/537.36 Chrome/125.0 Safari/537.36"}
        )
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                page = response.read().decode("utf-8", errors="ignore")
        except Exception:
            return None

        direct_images = re.findall(
            r'https?://[^"\'\s<>]+?\.(?:jpg|jpeg|png|webp)(?:\?[^"\'\s<>]*)?',
            html.unescape(page),
            flags=re.IGNORECASE
        )
        for image_url in direct_images:
            if any(host in image_url.lower() for host in ("duckduckgo.com", "bing.com")):
                continue
            try:
                data = self._download_image(image_url)
                if data:
                    ext = ".png" if "png" in image_url.lower() else ".jpg"
                    filename = os.path.join(self.download_dir, "online_meme" + ext)
                    with open(filename, "wb") as file:
                        file.write(data)
                    return {"path": filename, "source_url": image_url, "title": "Online image result"}
            except Exception:
                continue
        return None

    def _download_image(self, url):
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=8) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if not content_type.startswith("image/"):
                return None
            data = response.read(8 * 1024 * 1024 + 1)
            if len(data) > 8 * 1024 * 1024:
                return None
            return data
