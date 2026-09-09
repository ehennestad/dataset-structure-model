function root = fromLines(dataLocation, rootStoragePath, lines)
%fromLines Build a listing root from find-style output: one relative path per line
%   A path that ends with '/' or has entries below it is a directory; the rest are files.
    arguments
        dataLocation (1,1) string
        rootStoragePath (1,1) string
        lines (1,:) string
    end
    raw = string(dsm.internal.normalizeEntries(cellstr(lines)));
    directories = string.empty(1, 0);
    for entry = raw
        directories = [directories, dsm.internal.pathAncestors(entry)]; %#ok<AGROW>
    end
    entries = cell(1, numel(raw));
    for i = 1:numel(raw)
        entry = raw(i);
        if dsm.internal.isDirEntry(entry) || ismember(entry + "/", directories)
            entries{i} = char(regexprep(entry, "/$", "") + "/");
        else
            entries{i} = char(entry);
        end
    end
    root = dsm.Listing.makeRoot(dataLocation, rootStoragePath, entries);
end
