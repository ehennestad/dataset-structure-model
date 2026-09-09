function registry = fixtureExtractors()
%fixtureExtractors A registry with the extractors the conformance cases require
    registry = dsm.ExtractorRegistry();
    registry.register("session_number_from_folder_name", @sessionNumberFromFolderName);
end

function value = sessionNumberFromFolderName(fullPath, ~, ~)
%sessionNumberFromFolderName Contract from conformance/function-extractor: digits after 'ses-', else []
    component = dsm.internal.pathBase(fullPath);
    remainder = component;
    if startsWith(component, "ses-")
        remainder = extractAfter(component, strlength("ses-"));
    end
    digits = regexp(char(remainder), "^\d+", "match", "once");
    if isempty(digits)
        value = [];
    else
        value = str2double(digits);
    end
end
