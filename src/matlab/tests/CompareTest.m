classdef CompareTest < matlab.unittest.TestCase
%CompareTest The comparison rules: order- and message-insensitive, value-sensitive

    methods (Test)
        function compareIsOrderAndMessageInsensitive(testCase)
            expected = dsm.internal.readJson(fullfile(dsm.conformance.casesDirectory(), "folder-hierarchy-basic", "expected.json"));
            actual = expected;
            actual.records = flipud(actual.records(:));
            for i = 1:numel(actual.records)
                record = actual.records{i};
                locations = dsm.internal.asCellOfStructs(record.locations);
                for j = 1:numel(locations)
                    locations{j}.paths = flipud(dsm.internal.asCellstr(locations{j}.paths)');
                end
                record.locations = locations;
                if isfield(record, "issues")
                    issues = dsm.internal.asCellOfStructs(record.issues);
                    for j = 1:numel(issues)
                        issues{j}.message = 'different wording';
                    end
                    record.issues = issues;
                end
                actual.records{i} = record;
            end
            actual.unmatched = flipud(actual.unmatched(:));
            testCase.verifyEmpty(dsm.compareResults(expected, actual));
            actual.records{1}.metadata.subject_id = 'm999';
            testCase.verifyNotEmpty(dsm.compareResults(expected, actual));
        end

        function errorCasesCompareByCode(testCase)
            expected = struct("error", struct("code", "schema-validation"));
            testCase.verifyEmpty(dsm.compareResults(expected, struct("error", struct("code", "schema-validation", "message", "x"))));
            testCase.verifyNotEmpty(dsm.compareResults(expected, struct("records", {{}}, "unmatched", {{}})));
        end
    end
end
