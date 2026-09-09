function exportActual(outputDirectory, directory, registry)
%exportActual Write this reader's records for every case, for checking with `dsm compare`
%
%   dsm.conformance.exportActual(outputDirectory) writes <case>.actual.json
%   per valid case. The Python command `dsm compare conformance/<case>/expected.json
%   <case>.actual.json` then checks the MATLAB output with the reference
%   comparison, independently of dsm.compareResults.

    arguments
        outputDirectory (1,1) string
        directory (1,1) string = dsm.conformance.casesDirectory()
        registry (1,1) dsm.ExtractorRegistry = dsm.conformance.fixtureExtractors()
    end
    if ~isfolder(outputDirectory)
        mkdir(outputDirectory)
    end
    for name = dsm.conformance.listCaseNames(directory)
        caseDirectory = fullfile(directory, name);
        expected = dsm.internal.readJson(fullfile(caseDirectory, "expected.json"));
        if isfield(expected, "error")
            continue
        end
        config = dsm.loadConfig(fullfile(caseDirectory, "config.json"));
        listing = dsm.Listing.fromFile(fullfile(caseDirectory, "listing.json"));
        result = dsm.walk(config, listing, registry);
        result.write(fullfile(outputDirectory, name + ".actual.json"), "IncludeDetail", false);
    end
end
