function problems = unsupportedDraftBlocks(doc)
%unsupportedDraftBlocks DRAFT features this reader does not implement
    import dsm.internal.asCellOfStructs
    import dsm.internal.getField

    problems = string.empty(1, 0);
    for location = asCellOfStructs(getField(doc, "dataLocations", {}))
        sourceType = string(getField(location{1}, "sourceType", "filesystem"));
        if ismember(sourceType, ["spreadsheet", "database", "api"])
            problems(end+1) = sprintf("dataLocation '%s': sourceType '%s' is DRAFT and not supported", location{1}.identifier, sourceType); %#ok<AGROW>
        end
        for item = asCellOfStructs(getField(getField(location{1}, "filesystemSource", struct()), "metadataMapping", {}))
            if string(item{1}.extraction.method) == "sidecar"
                problems(end+1) = sprintf("dataLocation '%s': extraction method 'sidecar' for '%s' is DRAFT and not supported", location{1}.identifier, item{1}.metadataRef); %#ok<AGROW>
            end
        end
    end
end
