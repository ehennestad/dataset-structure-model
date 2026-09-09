function doc = readJson(path)
%readJson Decode a JSON file
    arguments
        path (1,1) string
    end
    if ~isfile(path)
        error("dsm:io:FileNotFound", "File not found: %s", path)
    end
    doc = jsondecode(fileread(path));
end
