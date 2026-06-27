import argparse
import sys

import uvicorn

from app.ingest import ingest_pdf
from app.query import query_documents


def main():
    parser = argparse.ArgumentParser(
        prog="ragchat",
        description="Chat with your documents using RAG.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a PDF file")
    ingest_parser.add_argument("file", help="Path to the PDF file")

    # query command
    query_parser = subparsers.add_parser("query", help="Ask a question")
    query_parser.add_argument("question", help="Your question")

    # serve command
    subparsers.add_parser("serve", help="Start the API server")

    args = parser.parse_args()

    if args.command == "ingest":
        result = ingest_pdf(args.file)
        print(f"Ingested: {result['filename']}")
        print(f"  Pages: {result['pages']}")
        print(f"  Chunks: {result['chunks']}")

    elif args.command == "query":
        result = query_documents(args.question)
        print(f"\n{result['answer']}\n")
        if result["sources"]:
            print("Sources:")
            for src in result["sources"]:
                print(f"  - {src['filename']} (page {src['page']})")

    elif args.command == "serve":
        uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
