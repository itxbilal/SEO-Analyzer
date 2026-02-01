from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    data = None

    if request.method == "POST":
        url = request.form.get("url")

        try:
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")

            title = soup.title.text if soup.title else "Missing"
            description = soup.find("meta", attrs={"name": "description"})
            description = description["content"] if description else "Missing"

            h1 = len(soup.find_all("h1"))
            h2 = len(soup.find_all("h2"))

            images = soup.find_all("img")
            missing_alt = sum(1 for img in images if not img.get("alt"))

            links = soup.find_all("a")
            internal = 0
            external = 0
            domain = urlparse(url).netloc

            for link in links:
                href = link.get("href")
                if href:
                    if domain in href:
                        internal += 1
                    elif href.startswith("http"):
                        external += 1

            # SEO SCORE (Rule Based)
            score = 0
            if title != "Missing": score += 20
            if description != "Missing": score += 20
            if h1 > 0: score += 20
            if missing_alt == 0: score += 20
            if internal > 0: score += 20

            data = {
                "title": title,
                "description": description,
                "h1": h1,
                "h2": h2,
                "missing_alt": missing_alt,
                "internal": internal,
                "external": external,
                "score": score
            }

        except:
            data = {"error": "Invalid URL or website blocked"}

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
