function root = fromDirectory(dataLocation, rootStoragePath, directory)
%fromDirectory Snapshot a real directory tree into a listing root
%   Hidden entries are included; the config's excludePatterns decide what to skip.
    arguments
        dataLocation (1,1) string
        rootStoragePath (1,1) string
        directory (1,1) string
    end
    if ~isfolder(directory)
        error("dsm:listing:NotADirectory", "%s is not a directory", directory)
    end
    found = dir(fullfile(directory, "**", "*"));
    found = found(~ismember({found.name}, {'.', '..'}));
    entries = cell(1, numel(found));
    base = char(directory);
    for i = 1:numel(found)
        relativeFolder = strrep(found(i).folder(numel(base) + 1:end), filesep, "/");
        relativeFolder = regexprep(relativeFolder, "^/", "");
        if relativeFolder ~= ""
            relativeFolder = relativeFolder + "/";
        end
        entry = relativeFolder + string(found(i).name);
        if found(i).isdir
            entry = entry + "/";
        end
        entries{i} = char(entry);
    end
    root = dsm.Listing.makeRoot(dataLocation, rootStoragePath, entries);
end
