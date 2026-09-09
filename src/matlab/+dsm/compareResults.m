function diffs = compareResults(expected, actual)
%compareResults Differences between an expectation and a reader's result by the conformance rules
%
%   diffs = dsm.compareResults(expected, actual) accepts either decoded
%   expected.json documents or WalkResult.toStruct() output on either side
%   and returns a string array of differences, empty when the reader passes.
%   Records match by (entityType, identity, parents); paths and files are
%   compared as sorted sets; metadata exactly; issues by code as a set.

    arguments
        expected (1,1) struct
        actual (1,1) struct
    end
    diffs = string.empty(1, 0);
    if isfield(expected, "error") || isfield(actual, "error")
        expectedCode = errorCode(expected);
        actualCode = errorCode(actual);
        if expectedCode ~= actualCode
            diffs(end+1) = sprintf("error code: expected '%s', got '%s'", expectedCode, actualCode);
        end
        return
    end

    expectedRecords = indexRecords(dsm.internal.getField(expected, "records", {}));
    actualRecords = indexRecords(dsm.internal.getField(actual, "records", {}));
    for key = setdiff(string(keys(expectedRecords)), string(keys(actualRecords)))
        diffs(end+1) = "missing record " + key; %#ok<AGROW>
    end
    for key = setdiff(string(keys(actualRecords)), string(keys(expectedRecords)))
        diffs(end+1) = "unexpected record " + key; %#ok<AGROW>
    end
    for key = intersect(string(keys(expectedRecords)), string(keys(actualRecords)))
        recordDiffs = compareRecord(expectedRecords(char(key)), actualRecords(char(key)));
        diffs = [diffs, key + ": " + recordDiffs]; %#ok<AGROW>
    end

    expectedUnmatched = unmatchedKeys(dsm.internal.getField(expected, "unmatched", {}));
    actualUnmatched = unmatchedKeys(dsm.internal.getField(actual, "unmatched", {}));
    for item = setdiff(expectedUnmatched, actualUnmatched)
        diffs(end+1) = "missing unmatched " + item; %#ok<AGROW>
    end
    for item = setdiff(actualUnmatched, expectedUnmatched)
        diffs(end+1) = "unexpected unmatched " + item; %#ok<AGROW>
    end
end

function code = errorCode(doc)
    code = "";
    if isfield(doc, "error")
        code = string(dsm.internal.getField(doc.error, "code", ""));
    end
end

function index = indexRecords(records)
    index = containers.Map("KeyType", "char", "ValueType", "any");
    for record = dsm.internal.asCellOfStructs(records)
        index(char(recordKey(record{1}))) = record{1};
    end
end

function key = recordKey(record)
    key = string(record.entityType) + "(" + identityKey(record.identity) + ")";
    parents = dsm.internal.asCellOfStructs(dsm.internal.getField(record, "parents", {}));
    if ~isempty(parents)
        chain = cellfun(@(p) string(p.entityType) + "(" + identityKey(p.identity) + ")", parents);
        key = key + " under " + strjoin(chain, " < ");
    end
end

function key = identityKey(identity)
    names = sort(string(fieldnames(identity)))';
    key = strjoin(arrayfun(@(n) n + "=" + valueText(identity.(n)), names), ", ");
end

function text = valueText(value)
    if isnumeric(value) || islogical(value)
        text = string(mat2str(value));
    else
        text = string(value);
    end
end

function keys = unmatchedKeys(items)
    keys = string.empty(1, 0);
    for item = dsm.internal.asCellOfStructs(items)
        keys(end+1) = sprintf("%s/%s %s (%s)", item{1}.dataLocationIdentifier, ...
            item{1}.rootStoragePathIdentifier, item{1}.path, item{1}.reason); %#ok<AGROW>
    end
    keys = unique(keys);
end

function diffs = compareRecord(expected, actual)
    diffs = string.empty(1, 0);
    expectedLocations = indexLocations(dsm.internal.getField(expected, "locations", {}));
    actualLocations = indexLocations(dsm.internal.getField(actual, "locations", {}));
    for key = setdiff(string(keys(expectedLocations)), string(keys(actualLocations)))
        diffs(end+1) = "missing location " + key; %#ok<AGROW>
    end
    for key = setdiff(string(keys(actualLocations)), string(keys(expectedLocations)))
        diffs(end+1) = "unexpected location " + key; %#ok<AGROW>
    end
    for key = intersect(string(keys(expectedLocations)), string(keys(actualLocations)))
        e = expectedLocations(char(key));
        a = actualLocations(char(key));
        expectedType = string(dsm.internal.getField(e, "fileSystemType", "folder"));
        actualType = string(dsm.internal.getField(a, "fileSystemType", "folder"));
        if expectedType ~= actualType
            diffs(end+1) = sprintf("%s: fileSystemType expected %s, got %s", key, expectedType, actualType); %#ok<AGROW>
        end
        expectedPaths = sort(string(dsm.internal.asCellstr(e.paths)));
        actualPaths = sort(string(dsm.internal.asCellstr(a.paths)));
        if ~isequal(expectedPaths, actualPaths)
            diffs(end+1) = sprintf("%s: paths expected [%s], got [%s]", key, strjoin(expectedPaths, ", "), strjoin(actualPaths, ", ")); %#ok<AGROW>
        end
        if isfield(e, "files") ~= isfield(a, "files")
            diffs(end+1) = sprintf("%s: files %s", key, ternary(isfield(e, "files"), "expected", "not expected")); %#ok<AGROW>
        elseif isfield(e, "files")
            expectedFiles = asMap(e.files);
            actualFiles = asMap(a.files);
            for name = union(string(keys(expectedFiles)), string(keys(actualFiles)))
                ef = sort(string(dsm.internal.asCellstr(lookup(expectedFiles, name))));
                af = sort(string(dsm.internal.asCellstr(lookup(actualFiles, name))));
                if ~isequal(ef, af)
                    diffs(end+1) = sprintf("%s: files[%s] expected [%s], got [%s]", key, name, strjoin(ef, ", "), strjoin(af, ", ")); %#ok<AGROW>
                end
            end
        end
        if ~isequal(dsm.internal.getField(e, "isComplete", []), dsm.internal.getField(a, "isComplete", []))
            diffs(end+1) = sprintf("%s: isComplete differs", key); %#ok<AGROW>
        end
    end

    expectedMetadata = dsm.internal.getField(expected, "metadata", struct());
    actualMetadata = dsm.internal.getField(actual, "metadata", struct());
    for field = union(string(fieldnames(expectedMetadata)), string(fieldnames(actualMetadata)))'
        if ~isfield(actualMetadata, field)
            diffs(end+1) = sprintf("metadata[%s] missing (expected %s)", field, valueText(expectedMetadata.(field))); %#ok<AGROW>
        elseif ~isfield(expectedMetadata, field)
            diffs(end+1) = sprintf("metadata[%s] unexpected (%s)", field, valueText(actualMetadata.(field))); %#ok<AGROW>
        elseif ~valuesEqual(expectedMetadata.(field), actualMetadata.(field))
            diffs(end+1) = sprintf("metadata[%s] expected %s, got %s", field, valueText(expectedMetadata.(field)), valueText(actualMetadata.(field))); %#ok<AGROW>
        end
    end

    expectedCodes = issueCodes(dsm.internal.getField(expected, "issues", {}));
    actualCodes = issueCodes(dsm.internal.getField(actual, "issues", {}));
    if ~isequal(expectedCodes, actualCodes)
        diffs(end+1) = sprintf("issues expected [%s], got [%s]", strjoin(expectedCodes, ", "), strjoin(actualCodes, ", "));
    end
end

function index = indexLocations(locations)
    index = containers.Map("KeyType", "char", "ValueType", "any");
    for location = dsm.internal.asCellOfStructs(locations)
        index(char(string(location{1}.dataLocationIdentifier) + "/" + string(location{1}.rootStoragePathIdentifier))) = location{1};
    end
end

function map = asMap(files)
    if isa(files, "containers.Map")
        map = files;
    else
        map = containers.Map("KeyType", "char", "ValueType", "any");
        for name = string(fieldnames(files))'
            map(char(name)) = files.(name);
        end
    end
end

function value = lookup(map, name)
    if isKey(map, char(name))
        value = map(char(name));
    else
        value = {};
    end
end

function codes = issueCodes(issues)
    codes = string.empty(1, 0);
    for item = dsm.internal.asCellOfStructs(issues)
        codes(end+1) = string(item{1}.code); %#ok<AGROW>
    end
    codes = unique(codes);
end

function tf = valuesEqual(a, b)
    if (ischar(a) || isstring(a)) && (ischar(b) || isstring(b))
        tf = string(a) == string(b);
    elseif (ischar(a) || isstring(a)) || (ischar(b) || isstring(b))
        tf = false;
    else
        tf = isequal(a, b);
    end
end

function out = ternary(condition, a, b)
    if condition
        out = a;
    else
        out = b;
    end
end
