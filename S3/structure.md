# Raw Data Structure Overview 

-     <agency>
      └── <docket id>
          ├── binary-<docket id>
          │   ├── comments_attachments
          │   │   ├── <comment id>_attachement_<counter>.<extension>
          │   │   └── ...
          │   ├── documents_attachments
          │   │   ├── <document id>_attachement_<counter>.<extension>
          │   │   └── ...
          └── text-<docket id>
              ├── comments
              │   ├── <comment id>.json
              │   └── ...
              ├── comments_extracted_text
              │   ├── <tool name>
              │   |   ├── <comment id>_attachment_<counter>_extracted.txt
              │   |   └── ...
              |   └─ ... <other tools>
              ├── docket
              │   ├── <docket id>.json
              |   └── ...
              ├── documents
              │   ├── <document id>.json
              │   ├── <document id>_content.htm
              │   └── ...
              └── documents_extracted_text
                  ├── <tool name>
                  |   ├── <document id>_content_extracted.txt
                  |   └── ...
                  └─ ... <other tools>



# Ideas: 

# Derived data folder Structure: 

-     <agency>
      └── <docket id>
          ├── comments_extracted_text
          │   ├── <tool name>
          │   │   ├── <comment id>_attachment_<counter>_extracted.txt
          │   │   └── ...
          │   └── ... <other tools>
          ├── entity_extracted
          │   ├── <tool name>
          │   │   ├── <comment id>_attachment_<counter>_extracted.txt
          │   │   └── ...
          │   └── ... <other tools>
          ├── ai_summary_extracted
          │   ├── <tool name>
          │   │   ├── <comment id>_attachment_<counter>_extracted.txt
          │   │   └── ...
          │   └── ... <other tools>
          ├── topic_identification_extracted
          │   ├── <tool name>
          │   │   ├── <comment id>_attachment_<counter>_extracted.txt
          │   │   └── ...
          │   └── ... <other tools>
          └── documents_extracted_text
              ├── <tool name>
              │   ├── <document id>_content_extracted.txt
              │   └── ...
              └── ... <other tools>
