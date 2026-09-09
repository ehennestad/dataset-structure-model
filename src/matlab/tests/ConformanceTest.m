classdef ConformanceTest < matlab.unittest.TestCase
%ConformanceTest The MATLAB reader passes every conformance case

    properties (TestParameter)
        caseName = ConformanceTest.caseNames()
    end

    methods (Static)
        function names = caseNames()
            names = cellstr(dsm.conformance.listCaseNames());
        end
    end

    methods (Test)
        function readerPassesCase(testCase, caseName)
            result = dsm.conformance.runCase(fullfile(dsm.conformance.casesDirectory(), caseName));
            testCase.verifyEqual(result.Status, "pass", strjoin([caseName; result.Diffs(:)], newline));
        end

        function unregisteredExtractorSkipsCaseAndFlagsRecords(testCase)
            caseDirectory = fullfile(dsm.conformance.casesDirectory(), "function-extractor");
            testCase.verifyEqual(dsm.conformance.runCase(caseDirectory, dsm.ExtractorRegistry()).Status, "skip");
            config = dsm.loadConfig(fullfile(caseDirectory, "config.json"));
            listing = dsm.loadListing(fullfile(caseDirectory, "listing.json"));
            result = dsm.walk(config, listing);
            testCase.verifyEqual(result.UnresolvedExtractors, "session_number_from_folder_name");
            sessions = result.Records(cellfun(@(r) r.entityType == "session", result.Records));
            testCase.verifyNotEmpty(sessions);
            for record = sessions
                codes = cellfun(@(i) i.code, record{1}.issues);
                testCase.verifyTrue(ismember("unresolved-extractor", codes));
                testCase.verifyFalse(isfield(record{1}.metadata, "session_number"));
            end
        end
    end
end
