# Extrator provisório (não é o extrator oficial)

O benchmark final usa `pypdf.PdfReader` diretamente dentro do script de benchmark. O teste local do NovaMente usou a função `extrair_pdf` em `teste_pdf_completo.py`. Esta cópia independente preserva a lógica desse teste, com `documento_id` derivado do nome do PDF.

A equipe deverá substituir a implementação de ingestão/extração. O contrato esperado pelo pipeline é `pipeline.schemas.DocumentoExtraido` contendo `DocumentoEntrada` e `PaginaExtraida` com número de página e texto.

Limitação: `pypdf` não faz OCR; PDFs digitalizados podem não fornecer texto.
