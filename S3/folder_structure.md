# S3 Folder Structure

## Current Data Structure Overview 

This is the current s3 layout

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
              ├── docket
              │   ├── <docket id>.json
              |   └── ...
              ├── documents
              │   ├── <document id>.json
              │   ├── <document id>_content.htm
              │   └── ...


## Candidate Folder Structures
Derived data folder Structure: 

### Candidate 1 Folder Structure

-     <agency>
      └── <docket id>
            ├── extracted_data
            │   ├── comments_extracted_text
            │   │   ├── <tool name>
            │   │   │   ├── <comment id>_attachment_<counter>_extracted.txt
            │   │   │   └── ...
            │   │   └── ... <other tools>
            │   └── documents_extracted_text
            │       ├── <tool name>
            │       │   ├── <document id>_content_extracted.txt
            │       │   └── ...
            │       └── ... <other tools>
            └── summarized_data
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
                └── topic_identification_extracted
                │   ├── <tool name>
                │   │   ├── <comment id>_attachment_<counter>_extracted.txt
                │   │   └── ...
                │   └── ... <other tools>
        


### Candidate 2 Folder Structure

-     <agency>
      └── <docket id>
          ├── Raw Data
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
                  ├── docket
                  │   ├── <docket id>.json
                  |   └── ...
                  ├── documents
                  │   ├── <document id>.json
                  │   ├── <document id>_content.htm
                  │   └── ...
          ├── Derived Data
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


### Candidate 3 Folder Structure

-     <agency>
      └── <docket id>
          ├── raw_data
              ├── binary
              │   ├── comments_attachments
              │   │   ├── <comment id>_attachement_<counter>.<extension>
              │   │   └── ...
              │   ├── documents_attachments
              │   │   ├── <document id>_attachement_<counter>.<extension>
              │   │   └── ...
              └── text
                  ├── comments
                  │   ├── <comment id>.json
                  │   └── ...
                  ├── docket
                  │   ├── <docket id>.json
                  |   └── ...
                  ├── documents
                  │   ├── <document id>.json
                  │   ├── <document id>_content.htm
                  │   └── ...
          ├── derived_data
              ├── mirrulations
              │   ├── comment_extraction
              │   │   ├── <comment id>_attachment_<counter>_extracted.txt
              │   │   └── ...
              │   ├── entity_extraction
              │   ├── <tool name>
              │   │   ├── <comment id>_attachment_<counter>_extracted.txt
              │   │   └── ...
              │   ├──  documents_extracted_text
              │   │   ├── <document id>_content_extracted.txt   
              │   ├── <tool name>
              │   │   ├── <comment id>_attachment_<counter>_extracted.txt
              │   │   └── ...
              │   └── ... <other tools>
              ├── propublica_chatgpt_sentiment
              ├── ├──  sentiment_summary_extraction
              ├── ├──  topic_extractions                    
              ├── careset_comment_identity
              │   ├── diff_graph
              │   │   └── ...  


