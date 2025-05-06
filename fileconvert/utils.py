import os
import subprocess
from pdf2docx import Converter
import pdfminer.high_level
import mammoth
import logging

logger = logging.getLogger(__name__)





def convert_pdf_to_word(input_path, output_path):
    """
    Convert a PDF file to Word (DOCX) using pdf2docx.
    """
    logger.info(f"Converting PDF to Word: {input_path} -> {output_path}")
    cv = Converter(input_path)
    try:
        cv.convert(
            output_path,
            start=0,
            end=None,
            layout_mode='loose',
            preserve_font_direction=True,
            preserve_image=True,
            preserve_table=True
        )
    except Exception as e:
        logger.error(f"PDF to Word conversion failed: {e}")
        raise
    finally:
        cv.close()




def convert_word_to_pdf(input_path, output_path):
    """
    Convert a Word (DOCX) file to PDF using LibreOffice via subprocess.
    """
    logger.info(f"Converting Word to PDF: {input_path} -> {output_path}")
    try:
        # Ensure LibreOffice is available
        result = subprocess.run(['libreoffice', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("LibreOffice is not installed or not accessible.")
        
        # Run LibreOffice in headless mode to convert DOCX to PDF
        command = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', os.path.dirname(output_path),
            input_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
        
        # LibreOffice saves the output as <input_filename>.pdf in outdir
        generated_pdf = os.path.join(
            os.path.dirname(output_path),
            f"{os.path.splitext(os.path.basename(input_path))[0]}.pdf"
        )
        if not os.path.exists(generated_pdf):
            raise RuntimeError("LibreOffice did not create the expected PDF file.")
        
        # Rename/move the generated PDF to the desired output_path
        os.rename(generated_pdf, output_path)
        
    except Exception as e:
        logger.error(f"Failed to convert Word to PDF: {str(e)}")
        raise



def convert_pdf_to_text(input_path, output_path):
    """
    Convert a PDF file to plain text using pdfminer.
    """
    logger.info(f"Converting PDF to Text: {input_path} -> {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        text = pdfminer.high_level.extract_text(input_path)
        f.write(text)

def convert_word_to_text(input_path, output_path):
    """
    Convert a Word (DOCX) file to plain text using mammoth.
    """
    logger.info(f"Converting Word to Text: {input_path} -> {output_path}")
    with open(input_path, "rb") as docx_file:
        result = mammoth.extract_raw_text(docx_file).value
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)