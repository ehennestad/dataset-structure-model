function results = runCases(directory, registry)
%runCases Run every conformance case against this reader
%
%   results = dsm.conformance.runCases() returns a struct array with Name,
%   Status and Diffs per case and prints a summary.

    arguments
        directory (1,1) string = dsm.conformance.casesDirectory()
        registry (1,1) dsm.ExtractorRegistry = dsm.conformance.fixtureExtractors()
    end
    names = dsm.conformance.listCaseNames(directory);
    results = struct("Name", {}, "Status", {}, "Diffs", {});
    for name = names
        results(end+1) = dsm.conformance.runCase(fullfile(directory, name), registry); %#ok<AGROW>
        fprintf("%-5s %s\n", upper(results(end).Status), name);
        if results(end).Status == "fail"
            fprintf("      %s\n", results(end).Diffs);
        end
    end
    fprintf("%d passed, %d failed, %d skipped\n", sum([results.Status] == "pass"), ...
        sum([results.Status] == "fail"), sum([results.Status] == "skip"));
end
