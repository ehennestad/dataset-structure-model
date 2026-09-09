function schema = loadSchema(name)
%loadSchema Decode one of the JSON schemas in the repository's schema folder
    arguments
        name (1,1) string
    end
    schemaPath = fullfile(dsm.internal.repoRoot(), "schema", name);
    if ~isfile(schemaPath)
        error("dsm:io:SchemaNotFound", "Schema not found: %s", schemaPath)
    end
    schema = jsondecode(fileread(schemaPath));
end
