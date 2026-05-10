import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.embedding.table_metadata import embed_table_metadata
from app.embedding.batch_pipeline import run_products_embedding, run_reviews_embedding

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Run embedding pipeline")
    parser.add_argument("--all", action="store_true", help="Run all embedding steps")
    parser.add_argument("--table-metadata", action="store_true", help="Embed table metadata only")
    parser.add_argument("--products", action="store_true", help="Embed products only")
    parser.add_argument("--reviews", action="store_true", help="Embed reviews only")
    args = parser.parse_args()

    if not any([args.all, args.table_metadata, args.products, args.reviews]):
        args.all = True

    if args.all or args.table_metadata:
        embed_table_metadata()
    if args.all or args.products:
        run_products_embedding()
    if args.all or args.reviews:
        run_reviews_embedding()


if __name__ == "__main__":
    main()
