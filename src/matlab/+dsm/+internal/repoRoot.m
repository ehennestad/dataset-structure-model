function root = repoRoot()
%repoRoot The repository root, resolved from this file's location (src/matlab/+dsm/+internal)
    thisDir = fileparts(mfilename("fullpath"));
    root = string(fileparts(fileparts(fileparts(fileparts(thisDir)))));
end
