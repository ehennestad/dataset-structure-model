function text = renderReport(config, result)
%renderReport Human-readable dry-run report for a walk
    arguments
        config (1,1) dsm.Config
        result (1,1) dsm.WalkResult
    end
    lines = string.empty(1, 0);
    source = config.Source;
    if source == ""
        source = "<memory>";
    end
    lines(end+1) = sprintf("Config: %s (valid)", source);
    lines(end+1) = "Environment: " + ternary(result.Environment ~= "", result.Environment, "-");
    for warning = result.Warnings
        lines(end+1) = "Warning: " + warning; %#ok<AGROW>
    end
    lines(end+1) = "Roots:";
    for root = result.Roots
        lines(end+1) = sprintf("  %s/%s: %d entries", root{1}.DataLocation, root{1}.RootStoragePath, root{1}.EntryCount); %#ok<AGROW>
    end
    lines(end+1) = "Entities:";
    for entityType = config.entityTypes()
        records = result.Records(cellfun(@(r) r.entityType == entityType, result.Records));
        inferred = sum(cellfun(@(r) isempty(r.locations), records));
        note = "";
        if inferred > 0
            note = sprintf(" (%d without a folder or files of their own)", inferred);
        end
        lines(end+1) = sprintf("  %s: %d%s", entityType, numel(records), note); %#ok<AGROW>
    end
    codes = string.empty(1, 0);
    for record = result.Records
        codes = [codes, cellfun(@(i) string(i.code), record{1}.issues)]; %#ok<AGROW>
    end
    if isempty(codes)
        lines(end+1) = "Issues: none";
    else
        [names, ~, index] = unique(codes);
        counts = accumarray(index(:), 1)';
        lines(end+1) = "Issues: " + strjoin(arrayfun(@(i) sprintf("%s: %d", names(i), counts(i)), 1:numel(names)), ", ");
        for record = result.Records
            for item = record{1}.issues
                identity = strjoin(arrayfun(@(k) k + "=" + string(record{1}.identity.(k)), string(fieldnames(record{1}.identity))'), ", ");
                lines(end+1) = sprintf("  %s(%s): %s - %s", record{1}.entityType, identity, item{1}.code, item{1}.message); %#ok<AGROW>
            end
        end
    end
    lines(end+1) = "Unresolved extractors: " + ternary(~isempty(result.UnresolvedExtractors), strjoin(result.UnresolvedExtractors, ", "), "none");
    lines(end+1) = sprintf("Unmatched: %d", numel(result.Unmatched));
    for item = result.Unmatched
        detail = "";
        if item{1}.detail ~= ""
            detail = sprintf("  (%s)", item{1}.detail);
        end
        lines(end+1) = sprintf("  %s/%s  %s  %s%s", item{1}.dataLocationIdentifier, item{1}.rootStoragePathIdentifier, item{1}.path, item{1}.reason, detail); %#ok<AGROW>
    end
    text = strjoin(lines, newline) + newline;
end

function out = ternary(condition, a, b)
    if condition
        out = a;
    else
        out = b;
    end
end
