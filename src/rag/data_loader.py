from pathlib import Path
from typing import Any, List
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_core.documents import Document


def load_all_documents(data_dir: str) -> List[Any]:
    data_path = Path(data_dir).resolve()
    print(f"[DEBUG]: Data directory: {data_path}")
    documents = []

    pdf_files = list(data_path.glob("**/*.pdf"))
    print(f"[DEBUG]: PDF Files: {pdf_files} | PDF files found: {len(pdf_files)}")
    for pdf_file in pdf_files:
        print(f"[DEBUG] lOADING PDF {pdf_file}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            loaded = loader.load()
            has_text = any(
                len(str(d.page_content).strip()) > 0 for d in loaded if hasattr(d, "page_content")
            )
            if not has_text:
                print(f"[DEBUG] No text extracted via standard loader, falling back to OCR: {pdf_file}")
                from src.ocr_loader import ocr_pdf
                loaded = ocr_pdf(str(pdf_file))
            print(f"[DEBUG] Found {len(loaded)} PDF docs from {pdf_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR]: Failed to load PDF {pdf_file}: {e}")

    text_files = list(data_path.glob("**/*.txt"))
    print(f"[DEBUG] TXT files: {text_files} | TXT files found: {len(text_files)}")
    for txt_file in text_files:
        print(f"[DEBUG] LOADING TXT {txt_file} ")
        try:
            loader = TextLoader(str(txt_file))
            loaded = loader.load()
            print(f"[DEBUG] Found {len(text_files)} TXT files: {[str(f) for f in text_files]}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR]: Failed to load TXT {txt_file}: {e}")

    xlsx_files = list(data_path.glob("**/*.xlsx"))
    print(f"[DEBUG] XLSX files found: {len(xlsx_files)}: {[str(f) for f in xlsx_files]}")
    for xlsx_file in xlsx_files:
        print(f"[DEBUG] LOADING XLSX {xlsx_file}")
        try:
            df = pd.read_excel(xlsx_file, engine="openpyxl")
            df = df.dropna(how="all").reset_index(drop=True)
            for row_number, (_, row) in enumerate(df.iterrows(), start=2):
                row_text = " | ".join(
                    f"{col}: {val}" for col, val in row.items() if pd.notna(val)
                )
                doc = Document(
                    page_content=row_text,
                    metadata={
                        "source": str(xlsx_file),
                        "row": row_number,
                        "total_rows": len(df),
                    },
                )
                documents.append(doc)
            print(f"[DEBUG] Loaded {len(df)} rows from {xlsx_file}")
        except Exception as e:
            print(f"[ERROR]: Failed to load XLSX {xlsx_file}: {e}")

    csv_files = list(data_path.glob("**/*.csv"))
    print(f"[DEBUG] Found {len(csv_files)} CSV files: {[str(f) for f in csv_files]}")
    for csv_file in csv_files:
        print(f"[DEBUG] Loading CSV: {csv_file}")
        try:
            loader = CSVLoader(str(csv_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} CSV docs from {csv_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load CSV {csv_file}: {e}")

    docx_files = list(data_path.glob("**/*.docx"))
    print(f"[DEBUG] Found {len(docx_files)} Word files: {[str(f) for f in docx_files]}")
    for docx_file in docx_files:
        print(f"[DEBUG] Loading Word: {docx_file}")
        try:
            loader = Docx2txtLoader(str(docx_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} Word docs from {docx_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load Word {docx_file}: {e}")

    json_files = list(data_path.glob("**/*.json"))
    print(f"[DEBUG] Found {len(json_files)} JSON files: {[str(f) for f in json_files]}")
    for json_file in json_files:
        print(f"[DEBUG] Loading JSON: {json_file}")
        try:
            loader = JSONLoader(str(json_file), jq_schema=".")
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} JSON docs from {json_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load JSON {json_file}: {e}")

    ppt_files = [f for f in data_path.glob("**/*.ppt*") if not f.name.startswith(".~lock.")]
    print(f"[DEBUG] Found {len(ppt_files)} PowerPoint files: {[str(f) for f in ppt_files]}")
    for ppt_file in ppt_files:
        print(f"[DEBUG] Loading PowerPoint: {ppt_file}")
        try:
            loader = UnstructuredPowerPointLoader(str(ppt_file))
            loaded = loader.load()
            has_text = any(
                len(str(d.page_content).strip()) > 0 for d in loaded if hasattr(d, "page_content")
            )
            if not has_text:
                print(f"[DEBUG] No text extracted via standard loader, falling back to OCR: {ppt_file}")
                from src.ocr_loader import ocr_pptx
                loaded = ocr_pptx(str(ppt_file))
            print(f"[DEBUG] Loaded {len(loaded)} PPT docs from {ppt_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load PPT {ppt_file}: {e}")

    print(f"[DEBUG] Total loaded documents: {len(documents)}")
    return documents
