function names = listCaseNames(directory)
%listCaseNames Names of the conformance cases (directories holding a config.json), sorted
    arguments
        directory (1,1) string = dsm.conformance.casesDirectory()
    end
    found = dir(directory);
    found = found([found.isdir] & ~ismember({found.name}, {'.', '..'}));
    names = string({found.name});
    names = sort(names(arrayfun(@(n) isfile(fullfile(directory, n, "config.json")), names)));
    names = reshape(names, 1, []);
end
