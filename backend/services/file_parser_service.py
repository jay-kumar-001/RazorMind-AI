import os
import pandas as pd
from typing import Dict, Any

class FileParserService:
    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        """
        Parses TXT, PDF, CSV, or XLSX files and returns a structured dictionary containing
        extracted text, structural summaries, and metadata.
        """
        ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        result = {
            "file_name": file_name,
            "file_size": file_size,
            "content_type": ext,
            "text_content": "",
            "summary": ""
        }

        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                result["text_content"] = content
                result["summary"] = f"TXT file with {len(content)} characters. First 200 chars:\n\n{content[:200]}..."

        elif ext == ".csv":
            try:
                df = pd.read_csv(file_path)
                result["text_content"] = df.to_string(index=False, max_rows=50)
                summary_stats = df.describe(include='all').to_string()
                result["summary"] = (
                    f"CSV dataset containing {len(df)} rows and {len(df.columns)} columns.\n"
                    f"Columns: {', '.join(df.columns.tolist())}\n\n"
                    f"### Data Summary Statistics:\n\n```\n{summary_stats}\n```"
                )
            except Exception as e:
                result["summary"] = f"Failed to parse CSV file: {str(e)}"

        elif ext in [".xls", ".xlsx"]:
            try:
                xl = pd.ExcelFile(file_path)
                sheets_summary = []
                full_text = []
                for sheet_name in xl.sheet_names:
                    df = xl.parse(sheet_name)
                    sheets_summary.append(f"- Sheet '{sheet_name}' with {len(df)} rows and {len(df.columns)} columns.")
                    full_text.append(f"Sheet: {sheet_name}\n" + df.to_string(index=False, max_rows=30))
                
                result["text_content"] = "\n\n".join(full_text)
                result["summary"] = (
                    f"Excel workbook containing {len(xl.sheet_names)} sheets:\n"
                    + "\n".join(sheets_summary)
                )
            except Exception as e:
                result["summary"] = f"Failed to parse Excel file: {str(e)}"

        elif ext == ".pdf":
            try:
                # Lazy import pypdf
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(file_path)
                    text_pages = []
                    for i, page in enumerate(reader.pages):
                        t = page.extract_text()
                        if t:
                            text_pages.append(f"--- Page {i+1} ---\n{t}")
                    
                    full_text = "\n\n".join(text_pages)
                    result["text_content"] = full_text
                    result["summary"] = f"PDF Document with {len(reader.pages)} pages. First 300 chars:\n\n{full_text[:300]}..."
                except ImportError:
                    # Fallback if pypdf is missing
                    result["text_content"] = "[PDF text extraction requires pypdf package to be installed on server]"
                    result["summary"] = f"PDF Document uploaded: {file_name}. (Text extraction library 'pypdf' not installed on server)"
            except Exception as e:
                result["summary"] = f"Failed to parse PDF file: {str(e)}"
        
        else:
            result["summary"] = f"Unsupported file type: {ext}"

        return result

file_parser_service = FileParserService()
