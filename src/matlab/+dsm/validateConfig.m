function validateConfig(doc, options)
%validateConfig Throw a dsm.ConfigError when a decoded config must be refused
%
%   dsm.validateConfig(doc) checks the schema, then the cross-reference
%   rules, then rejects DRAFT blocks (spreadsheet/database/api sources,
%   sidecar extraction). Pass RejectDraft=false to accept DRAFT blocks.

    arguments
        doc (1,1) struct
        options.RejectDraft (1,1) logical = true
    end
    errors = dsm.schemaErrors(doc);
    if ~isempty(errors)
        throw(dsm.ConfigError("schema-validation", errors))
    end
    problems = dsm.referenceProblems(doc);
    if ~isempty(problems)
        throw(dsm.ConfigError("reference-integrity", problems))
    end
    if options.RejectDraft
        drafts = dsm.internal.unsupportedDraftBlocks(doc);
        if ~isempty(drafts)
            throw(dsm.ConfigError("unsupported-draft", drafts))
        end
    end
end
