function entries = normalizeEntries(entries)
%normalizeEntries Strip './' and leading '/', add missing ancestor directories, dedupe, sort
    cleaned = string.empty(1, 0);
    for raw = string(entries)
        entry = strrep(strtrim(raw), "\", "/");
        if entry == "" || startsWith(entry, "#")
            continue
        end
        while startsWith(entry, "./")
            entry = extractAfter(entry, 2);
        end
        entry = regexprep(entry, "^/+", "");
        if entry == "" || entry == "."
            continue
        end
        cleaned(end+1) = entry; %#ok<AGROW>
    end
    withAncestors = cleaned;
    for entry = cleaned
        withAncestors = [withAncestors, dsm.internal.pathAncestors(entry)]; %#ok<AGROW>
    end
    entries = cellstr(sort(unique(withAncestors)));
    entries = reshape(entries, 1, []);
end
