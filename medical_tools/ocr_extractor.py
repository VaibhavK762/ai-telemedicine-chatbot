import pdfplumber
from pathlib import Path
from paddleocr import PaddleOCR


ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en"
)


def extract_pdf_text(file_path):
    """
    Extract selectable text PDFs.
    """

    text = ""


    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"


    return text.strip()



def extract_image_text(file_path):
    """
    Extract scanned reports/images.
    """

    result = ocr.ocr(
        file_path,
        cls=True
    )


    lines = []


    for page in result:

        for item in page:

            detected_text = item[1][0]

            lines.append(
                detected_text
            )


    return "\n".join(lines)



def extract_report_text(file_path):

    path = Path(file_path)

    extension = path.suffix.lower()


    if extension == ".pdf":

        text = extract_pdf_text(
            file_path
        )


        # digital PDF worked
        if len(text) > 50:

            return text


        # scanned PDF fallback later
        return ""


    elif extension in [
        ".jpg",
        ".jpeg",
        ".png"
    ]:

        return extract_image_text(
            file_path
        )


    else:

        raise ValueError(
            "Unsupported file type"
        )



if __name__ == "__main__":


    text = extract_report_text(
        "test_reports/blood_report.pdf"
        )


    print(text)