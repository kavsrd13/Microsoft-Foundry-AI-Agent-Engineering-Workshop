"""Optional upstream sample downloads. https://github.com/Azure-Samples/azure-search-sample-data/tree/main/health-plan"""
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

BASE = "https://raw.githubusercontent.com/Azure-Samples/azure-search-sample-data/main/health-plan/"
SAMPLES = {
    "Northwind_Standard_Benefits_Details.pdf": BASE + "Northwind_Standard_Benefits_Details.pdf",
    "Benefit_Options.pdf": BASE + "Benefit_Options.pdf",
    # The requested Invoice_1 binary is absent upstream; use the maintained invoice sample.
    "Invoice_1.pdf": "https://raw.githubusercontent.com/Azure-Samples/document-intelligence-code-samples/main/Data/invoice/invoice.pdf",
}


def main() -> None:
    destination = Path(__file__).parent / "datasets" / "benefits"
    destination.mkdir(parents=True, exist_ok=True)
    print("Optional Microsoft samples: review upstream licence/asset terms before use or redistribution.")
    print("This workshop uses these only for non-production training; this does not grant a new licence.")
    for filename, url in SAMPLES.items():
        try:
            with urlopen(url, timeout=20) as response:
                data = response.read()
            if not data.startswith(b"%PDF"):
                raise ValueError("The download was not a PDF")
            (destination / filename).write_bytes(data)
            print("Downloaded", filename)
        except (URLError, TimeoutError, ValueError) as error:
            print(f"Optional {filename} unavailable ({type(error).__name__}); use the bundled synthetic PDFs.")


if __name__ == "__main__":
    main()
