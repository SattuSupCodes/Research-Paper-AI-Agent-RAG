from pathlib import Path
import requests


PAPERS_DIR = Path("data/papers")
PAPERS_DIR.mkdir(parents=True, exist_ok=True)


def download_pdf(pdf_url: str, arxiv_id: str) -> str:
    """
    Download an arXiv PDF and return the local file path.
    """

    safe_id = arxiv_id.replace("/", "_")
    output_path = PAPERS_DIR / f"{safe_id}.pdf"

    response = requests.get(
        pdf_url,
        timeout=30,
    )

    response.raise_for_status()

    output_path.write_bytes(response.content)

    return str(output_path)

#test block
# if __name__ == "__main__":
#     url = "https://arxiv.org/pdf/2510.14973v2"
#     arxiv_id = "2510.14973v2"

#     path = download_pdf(url, arxiv_id)

#     print(f"Downloaded to: {path}")