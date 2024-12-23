import os
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from importlib import import_module
from scrapy.spiderloader import SpiderLoader

# Create data directory if not exists
data_dir = Path("../data")
data_dir.mkdir(exist_ok=True)

# Get Scrapy project settings
settings = get_project_settings()
settings["FEEDS"] = {}  # Will be set per spider

# Initialize spider loader
spider_loader = SpiderLoader.from_settings(settings)
spider_names = spider_loader.list()

# Create crawler process
process = CrawlerProcess(settings)

# For each spider
for spider_name in spider_names:
    # Generate output filename
    output_file = data_dir / f"{spider_name}.json"

    # Skip if file exists
    if output_file.exists():
        print(f"Skipping {spider_name} - output file already exists")
        continue

    print(f"Running spider: {spider_name}")

    # Configure output for this spider
    settings["FEEDS"][str(output_file)] = {
        "format": "json",
        "encoding": "utf8",
        "indent": 2,
    }

    # Add spider to crawler process
    process.crawl(spider_loader.load(spider_name))

# Run all spiders
if process.crawlers:
    process.start()
else:
    print("No new spiders to run - all output files exist")
