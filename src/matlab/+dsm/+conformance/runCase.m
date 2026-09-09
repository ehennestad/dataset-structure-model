function result = runCase(caseDirectory, registry)
%runCase Run one conformance case against this reader
%
%   result = dsm.conformance.runCase(caseDirectory) returns a struct with
%   Name, Status ("pass" | "fail" | "skip") and Diffs (string array).
%   Cases that require extractors the registry lacks are skipped.

    arguments
        caseDirectory (1,1) string
        registry (1,1) dsm.ExtractorRegistry = dsm.conformance.fixtureExtractors()
    end
    [~, name] = fileparts(caseDirectory);
    configDoc = dsm.internal.readJson(fullfile(caseDirectory, "config.json"));
    expected = dsm.internal.readJson(fullfile(caseDirectory, "expected.json"));

    if isfield(expected, "error")
        try
            dsm.validateConfig(configDoc);
            actual = struct("records", {{}}, "unmatched", {{}});
        catch exception
            if isa(exception, "dsm.ConfigError")
                actual = struct("error", struct("code", exception.Code));
            else
                rethrow(exception)
            end
        end
        result = makeResult(name, dsm.compareResults(expected, actual));
        return
    end

    required = string(fieldnames(dsm.internal.getField(expected, "requiresExtractors", struct())))';
    missing = required(~arrayfun(@(k) registry.has(k), required));
    if ~isempty(missing)
        result = struct("Name", string(name), "Status", "skip", "Diffs", "extractor not registered: " + missing);
        return
    end

    try
        dsm.validateConfig(configDoc);
    catch exception
        result = struct("Name", string(name), "Status", "fail", "Diffs", "config refused: " + string(exception.message));
        return
    end
    listing = dsm.Listing.fromFile(fullfile(caseDirectory, "listing.json"));
    config = dsm.Config(configDoc, fullfile(caseDirectory, "config.json"));
    walked = dsm.walk(config, listing, registry);
    result = makeResult(name, dsm.compareResults(expected, walked.toStruct("IncludeDetail", false)));
end

function result = makeResult(name, diffs)
    if isempty(diffs)
        status = "pass";
    else
        status = "fail";
    end
    result = struct("Name", string(name), "Status", status, "Diffs", diffs);
end
