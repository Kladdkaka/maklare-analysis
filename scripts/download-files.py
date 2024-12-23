import json
import asyncio
import aiohttp
from pathlib import Path
from asyncio import Semaphore
from typing import Dict
import hashlib


def hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


async def download_file(
    session: aiohttp.ClientSession, entry: Dict, data_dir: Path, semaphore: Semaphore
) -> None:
    document_name = entry["document_name"]
    document_url = entry["document_url"]

    safe_document_name = (
        "".join([c for c in document_name if c.isalpha() or c.isdigit() or c == " "])
        .rstrip()
        .replace(" ", "_")
    )

    file_name = hash_url(document_url) + "_" + safe_document_name

    file_name = file_name + ".pdf"
    file_path = data_dir / file_name

    if file_path.exists():
        print(f"Skipping {file_name} - file already exists")
        return

    async with semaphore:
        try:
            print(f"Downloading {file_name} from {document_url}")
            async with session.get(document_url) as response:
                content = await response.read()
                file_path.write_bytes(content)
                print(f"Downloaded {file_name}")
        except Exception as e:
            print(f"Error downloading {file_name}: {str(e)}")


async def main():
    # Create data directory if not exists
    data_dir = Path("../data/files")
    data_dir.mkdir(exist_ok=True)

    # Read all entries from JSON files
    entries = []
    for file in Path("../data").glob("*.json"):
        with open(file) as f:
            entries.extend(json.load(f))

    # Configure concurrent downloads
    max_concurrent = 50
    semaphore = Semaphore(max_concurrent)

    # Create session and download files concurrently
    async with aiohttp.ClientSession() as session:
        tasks = [
            download_file(session, entry, data_dir, semaphore) for entry in entries
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
